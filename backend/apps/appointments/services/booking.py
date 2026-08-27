"""
Booking write path (ADR-007). Kafolat: ExclusionConstraint + candidate loop.
select_for_update YOʻQ (bo'sh kunda hech narsa qulflamaydi — ADR-007 mexanizm tuzatildi).
Telegram yuborish bu yerda EMAS — view transaction.on_commit qiladi (critique #3).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Q
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment, generate_code
from apps.core.db_errors import (
    EXCLUSION_VIOLATION,
    UNIQUE_VIOLATION,
    constraint_of,
)
from apps.team.models import Doctor

from .slots import is_slot_available

DUPLICATE_WINDOW_MINUTES = 10  # critique #10: kalendar kun emas, qisqa oyna


class BookingError(Exception):
    def __init__(self, code: str, http: int = 400, **extra):
        self.code = code
        self.http = http
        self.extra = extra
        super().__init__(code)


class SlotTaken(BookingError):
    def __init__(self, **extra):
        super().__init__("slot_taken", http=409, **extra)


class NoDoctorAvailable(BookingError):
    def __init__(self, **extra):
        super().__init__("no_doctor_available", http=409, **extra)


class DuplicateBooking(BookingError):
    def __init__(self, **extra):
        super().__init__("duplicate_booking", http=409, **extra)


@dataclass
class BookingRequest:
    service: object
    starts_at: object  # aware datetime
    patient_name: str
    phone: str  # E.164
    locale: str = "uz"
    doctor: object | None = None  # None = "istalgan bo'sh"
    email: str = ""
    comment: str = ""
    consent_text_version: str = ""
    ip_hash: str = ""
    user_agent: str = ""
    idempotency_key: uuid.UUID | None = None


def _load_that_day(doctor_id, starts_at) -> int:
    day_start = starts_at.replace(hour=0, minute=0, second=0, microsecond=0)
    return Appointment.objects.filter(
        doctor_id=doctor_id,
        status__in=ACTIVE_STATUSES,
        starts_at__gte=day_start,
        starts_at__lt=day_start + timedelta(days=1),
    ).count()


def resolve_candidates(req: BookingRequest) -> list[Doctor]:
    """ "Istalgan bo'sh" uchun nomzod shifokorlar, eng kam yuklangandan (spec §5)."""
    if req.doctor is not None:
        return [req.doctor]
    qs = Doctor.objects.filter(is_active=True, is_bookable=True)
    if req.service.doctors.exists():
        qs = qs.filter(services=req.service)
    free = [
        d for d in qs if is_slot_available(doctor=d, service=req.service, starts_at=req.starts_at)
    ]
    free.sort(key=lambda d: (_load_that_day(d.id, req.starts_at), d.order, d.pk))
    return free


def _check_duplicate(req: BookingRequest) -> None:
    """Bir xil telefon + bir xil slot, faol qabul → duplicate (critique #10: kalendar kun emas)."""
    window_ago = timezone.now() - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)
    exists = (
        Appointment.objects.filter(phone=req.phone, status__in=ACTIVE_STATUSES)
        .filter(Q(starts_at=req.starts_at) | Q(created_at__gte=window_ago))
        .exists()
    )
    if exists:
        raise DuplicateBooking()


DEADLOCK = "40P01"


def _is_deadlock(exc: Exception) -> bool:
    return getattr(getattr(exc, "__cause__", None), "sqlstate", None) == DEADLOCK


def _insert(**fields) -> Appointment:
    """
    Insert. Har urinish OʻZ top-level tranzaksiyasi (savepoint EMAS) — chunki deadlock
    butun tranzaksiyani abort qiladi, savepoint yordam bermaydi. Chaqiruvchi outer
    atomic ochmaydi. code-collision va deadlock qayta urinadi; 23P01 ni chaqiruvchi tutadi.
    """
    last = None
    for _ in range(6):
        try:
            with transaction.atomic():
                return Appointment.objects.create(**fields)
        except IntegrityError as exc:
            sqlstate, name = constraint_of(exc)
            if sqlstate == UNIQUE_VIOLATION and name.endswith("_code_key"):
                fields["code"] = generate_code()
                last = exc
                continue
            raise  # 23P01 (exclusion) va idempotency — chaqiruvchi hal qiladi
        except OperationalError as exc:
            if _is_deadlock(exc):
                # Deadlock: Postgres bizni oʻldirdi, raqib davom etdi. Qayta urinamiz —
                # endi raqib qatori commit boʻlgan boʻlishi mumkin → 23P01 keladi.
                last = exc
                continue
            raise
    raise last


def create_appointment(req: BookingRequest) -> tuple[Appointment, bool]:
    """
    Qabul yaratadi. (appointment, is_replay) qaytaradi.
    SlotTaken/NoDoctorAvailable/DuplicateBooking ko'taradi.
    Telegram YUBORMAYDI — view on_commit qiladi.
    """
    # Idempotency replay
    if req.idempotency_key:
        existing = Appointment.objects.filter(idempotency_key=req.idempotency_key).first()
        if existing:
            return existing, True

    _check_duplicate(req)

    candidates = resolve_candidates(req)
    if not candidates:
        raise NoDoctorAvailable()

    ends_at = req.starts_at + timedelta(minutes=req.service.duration_minutes)
    base_fields = {
        "service": req.service,
        "patient_name": req.patient_name,
        "phone": req.phone,
        "email": req.email,
        "comment": req.comment,
        "starts_at": req.starts_at,
        "ends_at": ends_at,
        "locale": req.locale,
        "source": Appointment.Source.WEB,
        "consent_given_at": timezone.now(),
        "consent_text_version": req.consent_text_version,
        "ip_hash": req.ip_hash,
        "user_agent": req.user_agent[:300],
        "idempotency_key": req.idempotency_key,
    }

    for doctor in candidates:
        # Har nomzod uchun qayta validatsiya (staleness: jadval o'zgargan bo'lishi mumkin)
        if not is_slot_available(doctor=doctor, service=req.service, starts_at=req.starts_at):
            continue
        try:
            appt = _insert(doctor=doctor, **base_fields)
            return appt, False
        except IntegrityError as exc:
            sqlstate, name = constraint_of(exc)
            if sqlstate == UNIQUE_VIOLATION and name.endswith("_idempotency_key_key"):
                # parallel double-submit — g'olib qatorini o'qiymiz
                existing = Appointment.objects.filter(idempotency_key=req.idempotency_key).first()
                if existing:
                    return existing, True
                raise SlotTaken() from exc
            if sqlstate == EXCLUSION_VIOLATION:
                continue  # bu nomzod poygada yutqazdi — keyingisi
            raise
        except OperationalError as exc:
            if _is_deadlock(exc):
                continue  # deadlock: raqib yutdi — keyingi nomzodni sinaymiz
            raise
    # Hamma nomzod band
    if req.doctor is not None:
        raise SlotTaken()
    raise NoDoctorAvailable()
