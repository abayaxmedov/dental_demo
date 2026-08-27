"""Booking write API (Faza 2). Slots GET, appointment/lead POST, cancel/reschedule."""

from __future__ import annotations

from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.appointments.models import (
    ACTIVE_STATUSES,
    Appointment,
    AppointmentStatus,
)
from apps.appointments.serializers import (
    AppointmentCreateSerializer,
    AppointmentPublicSerializer,
    DaySlotsSerializer,
    LeadCreateSerializer,
)
from apps.appointments.services import booking as bk
from apps.appointments.services.slots import available_slots, is_slot_available
from apps.core.antispam import (
    HONEYPOT_FIELD,
    FormTiming,
    check_form_timing,
    client_ip,
    hash_ip,
)
from apps.core.errors import problem
from apps.core.utils.phone import InvalidPhoneError, normalize_uz_phone
from apps.leads.models import Lead


def _antispam(data, request) -> Response | None:
    """Honeypot (fake 201) + timing. Xato bo'lsa Response qaytaradi, aks holda None."""
    # Honeypot: bot to'ldirsa — soxta muvaffaqiyat, hech narsa saqlanmaydi (critique #17)
    if data.get(HONEYPOT_FIELD):
        from apps.notifications.models import NotificationLog

        NotificationLog.objects.create(
            channel=NotificationLog.Channel.TELEGRAM,
            template_key="honeypot_tripped",
            status=NotificationLog.Status.ABANDONED,
            target="bot",
        )
        return Response({"ok": True, "notified": False}, status=201)
    # Timing (faqat form_token bo'lsa — reschedule/cancel'da yo'q)
    timing = check_form_timing(data.get("form_token") or None)
    if timing == FormTiming.TOO_FAST:
        return problem("too_fast", status=400)
    if timing == FormTiming.STALE and data.get("form_token"):
        return problem("stale_form", status=400)
    return None


class AppointmentCreateView(APIView):
    throttle_scope = "booking"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(request=AppointmentCreateSerializer, responses=OpenApiTypes.OBJECT, tags=["booking"])
    def post(self, request):
        blocked = _antispam(request.data, request)
        if blocked:
            return blocked

        ser = AppointmentCreateSerializer(data=request.data)
        if not ser.is_valid():
            return self._validation_problem(ser)
        v = ser.validated_data

        try:
            phone = normalize_uz_phone(v["phone"])
        except InvalidPhoneError:
            return problem("invalid_phone", status=400, errors={"phone": ["invalid_phone"]})

        # Slot mavjudligini oldindan tekshirish — aniq xabar uchun (spec §1.2 step 11)
        doctor = v.get("doctor")
        service = v["service"]
        starts_at = v["starts_at"]

        # Idempotency replay — slot pre-check'dan OLDIN (aks holda band slot 400 beradi)
        if key := v.get("idempotency_key"):
            existing = Appointment.objects.filter(idempotency_key=key).first()
            if existing:
                return self._success_body(existing, is_replay=True)

        why = self._why_unavailable(doctor, service, starts_at)
        if why:
            return problem(
                why,
                status=403 if why == "booking_disabled" else 400,
                errors={"starts_at": [why]},
                **self._available_for(doctor, service, starts_at),
            )

        req = bk.BookingRequest(
            service=service,
            starts_at=starts_at,
            patient_name=v["patient_name"],
            phone=phone,
            locale=v["locale"],
            doctor=doctor,
            email=v["email"],
            comment=v["comment"],
            consent_text_version=v.get("consent_text_version") or "",
            ip_hash=hash_ip(client_ip(request)),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            idempotency_key=v.get("idempotency_key"),
        )
        try:
            # OUTER atomic YOʻQ — _insert har urinishda o'z tranzaksiyasini boshqaradi
            # (deadlock butun tranzaksiyani abort qiladi, savepoint yordam bermaydi).
            appt, is_replay = bk.create_appointment(req)
        except bk.BookingError as exc:
            extra = (
                self._available_for(exc.extra.get("doctor", doctor), service, starts_at)
                if exc.code in ("slot_taken", "no_doctor_available")
                else {}
            )
            return problem(exc.code, status=exc.http, **extra)

        return self._success_body(appt, is_replay=is_replay, send=True)

    def _success_body(self, appt, *, is_replay, send=False):
        # Telegram TRANZAKSIYADAN TASHQARIDA (critique #3) — bu yerda transaction yopilgan.
        notified = False
        if send:
            from apps.notifications.services.notify import notify_new_appointment

            notified = notify_new_appointment(appt)
        elif appt.status in ("pending", "confirmed"):
            # replay: haqiqiy yuborilgan-yuborilmaganini logdan bilmaymiz, ehtiyot uchun False
            notified = False
        body = {
            "ok": True,
            "code": appt.code,
            "cancel_token": str(appt.cancel_token),
            "starts_at": appt.starts_at.isoformat(),
            "ends_at": appt.ends_at.isoformat(),
            "doctor": appt.doctor_id,
            "service": appt.service_id,
            "status": appt.status,
            "notified": notified,
        }
        headers = {"Location": f"/api/v1/appointments/{appt.cancel_token}/"}
        if is_replay:
            headers["Idempotency-Replayed"] = "true"
            return Response(body, status=200, headers=headers)
        return Response(body, status=201, headers=headers)

    def _validation_problem(self, ser):
        errors = {}
        code = "validation_error"
        for field, errs in ser.errors.items():
            msgs = [str(e) for e in errs]
            errors[field] = msgs
            # maxsus kodlarni ko'taramiz
            if "consent_required" in msgs:
                code = "consent_required"
            elif "naive_datetime" in msgs and field == "starts_at":
                code = "validation_error"
            elif "service_required" in msgs:
                code = "service_required"
        status = 400
        return problem(code, status=status, errors=errors)

    def _why_unavailable(self, doctor, service, starts_at):
        from apps.core.models import ClinicSettings

        if not ClinicSettings.load().booking_enabled:
            return "booking_disabled"
        if is_slot_available(doctor=doctor, service=service, starts_at=starts_at):
            return None
        # nega mavjud emas — sababni aniqlaymiz
        now = timezone.now()
        min_lead = timedelta(
            minutes=__import__(
                "django.conf", fromlist=["settings"]
            ).settings.BOOKING_MIN_LEAD_MINUTES
        )
        if starts_at < now + min_lead:
            return "lead_time_violation"
        return "slot_unavailable"

    def _available_for(self, doctor, service, starts_at):
        """409/400 javobiga yangilangan slotlarni qo'shadi (spec §4). Xato bo'lsa — o'tkazib yuboradi."""
        try:
            d = starts_at.astimezone(
                __import__("zoneinfo").ZoneInfo(
                    __import__("django.conf", fromlist=["settings"]).settings.TIME_ZONE
                )
            ).date()
            res = available_slots(
                date_from=d,
                date_to=d + timedelta(days=2),
                doctor=doctor if doctor else None,
                service=service,
            )
            days = [DaySlotsSerializer(dy).data for dy in res.days if dy.slots][:2]
            return {"available": {"days": days}}
        except Exception:  # noqa: BLE001 — 409/400 ni hech qachon 500 ga aylantirmaymiz (critique #11)
            return {}


class LeadCreateView(APIView):
    throttle_scope = "lead"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(request=LeadCreateSerializer, responses=OpenApiTypes.OBJECT, tags=["booking"])
    def post(self, request):
        blocked = _antispam(request.data, request)
        if blocked:
            return blocked

        ser = LeadCreateSerializer(data=request.data)
        if not ser.is_valid():
            code = "consent_required" if "consent" in ser.errors else "validation_error"
            return problem(
                code, status=400, errors={k: [str(e) for e in v] for k, v in ser.errors.items()}
            )
        v = ser.validated_data

        try:
            phone = normalize_uz_phone(v["phone"])
        except InvalidPhoneError:
            return problem("invalid_phone", status=400, errors={"phone": ["invalid_phone"]})

        # Dedupe: bir xil telefon + kind, oxirgi 10 daqiqa → soxta success (spec §8)
        window_ago = timezone.now() - timedelta(minutes=10)
        if Lead.objects.filter(phone=phone, kind=v["kind"], created_at__gte=window_ago).exists():
            return Response({"ok": True, "deduplicated": True}, status=201)

        lead = Lead.objects.create(
            kind=v["kind"],
            name=v["name"],
            phone=phone,
            email=v["email"],
            message=v["message"],
            service=v.get("service"),
            preferred_time=v["preferred_time"],
            locale=v["locale"],
            source_page=v["source_page"],
            utm_source=v["utm_source"],
            utm_medium=v["utm_medium"],
            utm_campaign=v["utm_campaign"],
            consent_given_at=timezone.now(),
            ip_hash=hash_ip(client_ip(request)),
        )

        from apps.notifications.services.notify import notify_new_lead

        notified = notify_new_lead(lead)
        if notified:
            Lead.objects.filter(pk=lead.pk).update(notified=True)

        return Response({"ok": True, "notified": notified}, status=201)


class SlotsView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["booking"])
    def get(self, request):
        p = request.query_params
        today = timezone.localdate()
        try:
            date_from = date.fromisoformat(p["date_from"]) if p.get("date_from") else today
            date_to = (
                date.fromisoformat(p["date_to"]) if p.get("date_to") else today + timedelta(days=14)
            )
        except ValueError:
            return problem("validation_error", status=400, errors={"date": ["invalid date"]})

        exclude_id = None
        if token := p.get("exclude"):
            appt = Appointment.objects.filter(cancel_token=token).first()
            exclude_id = appt.pk if appt else None

        res = available_slots(
            date_from=date_from,
            date_to=date_to,
            doctor=p.get("doctor") or None,
            service=p.get("service") or None,
            exclude_appointment_id=exclude_id,
        )
        body = {
            "timezone": res.timezone,
            "duration_minutes": res.duration_minutes,
            "booking_enabled": res.booking_enabled,
            "reason": res.reason,
            "window": {"from": res.window_start.isoformat(), "to": res.window_end.isoformat()},
            "days": DaySlotsSerializer(res.days, many=True).data,
        }
        resp = Response(body)
        resp["Cache-Control"] = "private, no-cache"
        return resp


class FormTokenView(APIView):
    """Forma render qilinganda imzolangan token beradi (anti-spam timing tuzogʻi uchun)."""

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["booking"])
    def get(self, request):
        from apps.core.antispam import make_form_token

        return Response({"form_token": make_form_token()})


class AppointmentTokenView(APIView):
    throttle_scope = "token"
    throttle_classes = [ScopedRateThrottle]

    def _get(self, token):
        return (
            Appointment.objects.select_related("doctor", "service")
            .filter(cancel_token=token)
            .first()
        )

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["booking"])
    def get(self, request, cancel_token):
        appt = self._get(cancel_token)
        if not appt:
            return problem("not_found", status=404)
        resp = Response(AppointmentPublicSerializer(appt).data)
        resp["Cache-Control"] = "no-store"
        resp["X-Robots-Tag"] = "noindex, nofollow"
        return resp


class AppointmentCancelView(AppointmentTokenView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT, tags=["booking"])
    def post(self, request, cancel_token):
        appt = self._get(cancel_token)
        if not appt:
            return problem("not_found", status=404)
        if appt.status in (
            AppointmentStatus.CANCELLED_BY_PATIENT,
            AppointmentStatus.CANCELLED_BY_CLINIC,
        ):
            return problem("already_cancelled", status=409)
        if appt.status in (AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW):
            return problem("not_cancellable", status=409)
        if appt.starts_at <= timezone.now():
            return problem("appointment_past", status=409)

        # Shartli update — poyga g'olibi aniq (spec §6.2)
        late = appt.starts_at - timezone.now() < timedelta(hours=2)
        updated = Appointment.objects.filter(
            pk=appt.pk,
            status__in=ACTIVE_STATUSES,
        ).update(status=AppointmentStatus.CANCELLED_BY_PATIENT, updated_at=timezone.now())
        if not updated:
            return problem("already_cancelled", status=409)

        appt.refresh_from_db()
        reason = str(request.data.get("reason", ""))[:500]
        from apps.notifications.services.notify import notify_cancelled

        notify_cancelled(appt, late=late, reason=reason)
        return Response({"ok": True, "status": appt.status})


class AppointmentRescheduleView(AppointmentTokenView):
    class _In(serializers.Serializer):
        starts_at = serializers.DateTimeField()
        doctor = serializers.IntegerField(required=False, allow_null=True)

    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT, tags=["booking"])
    def post(self, request, cancel_token):
        appt = self._get(cancel_token)
        if not appt:
            return problem("not_found", status=404)
        if appt.status not in ACTIVE_STATUSES:
            return problem("not_reschedulable", status=409)
        if appt.starts_at <= timezone.now():
            return problem("appointment_past", status=409)
        if appt.reschedule_count >= 3:
            return problem("reschedule_limit", status=409)

        ser = self._In(data=request.data)
        if not ser.is_valid():
            return problem("validation_error", status=400, errors=ser.errors)
        new_start = ser.validated_data["starts_at"]
        if new_start.tzinfo is None:
            return problem("validation_error", status=400, errors={"starts_at": ["naive_datetime"]})

        from apps.team.models import Doctor

        new_doctor = appt.doctor
        if did := ser.validated_data.get("doctor"):
            new_doctor = (
                Doctor.objects.filter(pk=did, is_active=True, is_bookable=True).first()
                or appt.doctor
            )

        # O'z qatorini istisno qilib mavjudlikni tekshiramiz (critique #16)
        if not is_slot_available(
            doctor=new_doctor,
            service=appt.service,
            starts_at=new_start,
            exclude_appointment_id=appt.pk,
        ):
            return problem(
                "slot_unavailable", status=400, errors={"starts_at": ["slot_unavailable"]}
            )

        new_end = new_start + timedelta(
            minutes=appt.service.duration_minutes if appt.service else 30
        )
        old_start = appt.starts_at
        doctor_changed = new_doctor != appt.doctor

        from django.db import IntegrityError
        from django.db.models import F

        from apps.core.db_errors import EXCLUSION_VIOLATION, constraint_of

        try:
            with transaction.atomic():
                n = Appointment.objects.filter(pk=appt.pk, status__in=ACTIVE_STATUSES).update(
                    doctor=new_doctor,
                    starts_at=new_start,
                    ends_at=new_end,
                    reschedule_count=F("reschedule_count") + 1,
                    reminder_24h_sent_at=None,
                    reminder_2h_sent_at=None,  # KRITIK (spec §6.3)
                    updated_at=timezone.now(),
                )
        except IntegrityError as exc:
            sqlstate, _ = constraint_of(exc)
            if sqlstate == EXCLUSION_VIOLATION:
                d = new_start.astimezone(
                    __import__("zoneinfo").ZoneInfo(
                        __import__("django.conf", fromlist=["settings"]).settings.TIME_ZONE
                    )
                ).date()
                res = available_slots(
                    date_from=d,
                    date_to=d + timedelta(days=2),
                    doctor=new_doctor,
                    service=appt.service,
                    exclude_appointment_id=appt.pk,
                )
                days = [DaySlotsSerializer(dy).data for dy in res.days if dy.slots][:2]
                return problem("slot_taken", status=409, available={"days": days})
            raise
        if n == 0:
            return problem("not_reschedulable", status=409)

        appt.refresh_from_db()
        from apps.notifications.services.notify import notify_rescheduled

        notify_rescheduled(appt, old_start=old_start, doctor_changed=doctor_changed)
        return Response(AppointmentPublicSerializer(appt).data)
