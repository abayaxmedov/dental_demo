"""
Slot engine (ADR-007 read tomoni) — boʻsh vaqtlar OʻQISHDA hisoblanadi, materializatsiya yoʻq.
Batafsil spec: dizayn workflow. Asosiy invariant: Phase B fetch qiladi, Phase C hisoblaydi
(day loop ichida hech qanday I/O yoʻq — 6 ta query, oyna uzunligidan mustaqil).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment
from apps.core.models import ClinicSettings, WorkingHours
from apps.services.models import Service
from apps.team.models import Doctor, DoctorSchedule, TimeOff

from .intervals import Interval, L, clip, covers, fits_in_one, split_on_break, subtract

ONE_DAY = timedelta(days=1)


class ClosedReason(models.TextChoices):
    OPEN = "open", "Ochiq"
    BOOKING_DISABLED = "booking_disabled", "Onlayn qabul oʻchirilgan"
    SERVICE_UNAVAILABLE = "service_unavailable", "Xizmat mavjud emas"
    DOCTOR_UNAVAILABLE = "doctor_unavailable", "Shifokor mavjud emas"
    CLINIC_CLOSED = "clinic_closed", "Klinika yopiq"
    CLINIC_HOLIDAY = "clinic_holiday", "Bayram"
    NO_DOCTOR_SCHEDULE = "no_doctor_schedule", "Jadval yoʻq"
    DOCTOR_TIME_OFF = "doctor_time_off", "Dam olish"
    FULLY_BOOKED = "fully_booked", "Toʻliq band"
    LEAD_TIME = "lead_time", "Vaqt oʻtib ketgan"


@dataclass(frozen=True, slots=True)
class Slot:
    start: datetime
    end: datetime
    duration_minutes: int
    doctor_ids: tuple[int, ...]

    @property
    def label(self) -> str:
        return self.start.strftime("%H:%M")


@dataclass(frozen=True, slots=True)
class DaySlots:
    day: date
    weekday: int
    slots: tuple[Slot, ...]
    closed_reason: str = ClosedReason.OPEN


@dataclass(frozen=True, slots=True)
class SlotResult:
    days: tuple[DaySlots, ...]
    duration_minutes: int | None
    doctor_ids: tuple[int, ...]
    timezone: str
    generated_at: datetime
    booking_enabled: bool
    window_start: date
    window_end: date
    reason: str = ClosedReason.OPEN


def _resolve(obj, model):
    if obj is None or isinstance(obj, model):
        return obj
    return model.objects.filter(pk=obj).first()


def available_slots(
    *,
    date_from: date,
    date_to: date,
    doctor: Doctor | int | None = None,
    service: Service | int | None = None,
    now: datetime | None = None,
    include_empty_days: bool = True,
    exclude_appointment_id: int | None = None,
) -> SlotResult:
    """Boʻsh slotlarni kun boʻyicha guruhlab qaytaradi. Barcha vaqtlar aware, CLINIC_TZ."""
    tz = __import__("zoneinfo").ZoneInfo(settings.TIME_ZONE)
    if now is None:
        now = timezone.now()
    elif not timezone.is_aware(now):
        raise ValueError("now aware boʻlishi kerak")

    local_now = now.astimezone(tz)
    today = local_now.date()
    min_lead = timedelta(minutes=settings.BOOKING_MIN_LEAD_MINUTES)
    earliest = now + min_lead

    def empty(reason: str) -> SlotResult:
        return SlotResult(
            days=(),
            duration_minutes=None,
            doctor_ids=(),
            timezone=settings.TIME_ZONE,
            generated_at=now,
            booking_enabled=cs.booking_enabled,
            window_start=today,
            window_end=today,
            reason=reason,
        )

    # ── Phase A: guards ──
    cs = ClinicSettings.load()
    if not cs.booking_enabled:
        return empty(ClosedReason.BOOKING_DISABLED)

    service = _resolve(service, Service)
    if service is not None and not service.is_active:
        return empty(ClosedReason.SERVICE_UNAVAILABLE)
    duration_minutes = service.duration_minutes if service else None

    pool_qs = Doctor.objects.filter(is_active=True, is_bookable=True)
    if service is not None and service.doctors.exists():
        pool_qs = pool_qs.filter(services=service)
    doctor = _resolve(doctor, Doctor)
    if doctor is not None:
        pool_qs = pool_qs.filter(pk=doctor.pk)
    pool = list(pool_qs.only("id", "order", "full_name").order_by("order", "id"))
    if not pool:
        return empty(ClosedReason.DOCTOR_UNAVAILABLE if doctor else ClosedReason.NO_DOCTOR_SCHEDULE)
    pool_ids = [d.id for d in pool]

    window_start = max(date_from, today)
    window_end = min(date_to, today + timedelta(days=settings.BOOKING_WINDOW_DAYS))
    if window_start > window_end:
        return empty(ClosedReason.OPEN)

    # ── Phase B: bulk fetch (fixed query count) ──
    win_lo = L(window_start, time.min)
    win_hi = L(window_end + ONE_DAY, time.min)

    work_hours = {wh.weekday: wh for wh in WorkingHours.objects.all()}

    schedules: dict[tuple[int, int], list[DoctorSchedule]] = defaultdict(list)
    sched_qs = (
        DoctorSchedule.objects.filter(
            doctor_id__in=pool_ids,
            slot_minutes__gte=5,
        )
        .filter(models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=window_end))
        .filter(models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=window_start))
        .order_by("doctor_id", "weekday", "start_time")
    )
    for sch in sched_qs:
        schedules[(sch.doctor_id, sch.weekday)].append(sch)

    timeoff_doc: dict[int, list[Interval]] = defaultdict(list)
    timeoff_clinic: list[Interval] = []
    for t in TimeOff.objects.filter(starts_at__lt=win_hi, ends_at__gt=win_lo).filter(
        models.Q(doctor_id__isnull=True) | models.Q(doctor_id__in=pool_ids)
    ):
        iv = (t.starts_at.astimezone(tz), t.ends_at.astimezone(tz))
        (timeoff_clinic if t.doctor_id is None else timeoff_doc[t.doctor_id]).append(iv)

    # Band vaqtlar. doctor=NULL faol qabul HAMMA shifokorni bloklaydi (critique #21).
    busy: dict[int, list[Interval]] = defaultdict(list)
    busy_all: list[Interval] = []
    appt_qs = Appointment.objects.filter(
        status__in=ACTIVE_STATUSES, starts_at__lt=win_hi, ends_at__gt=win_lo
    ).filter(models.Q(doctor_id__isnull=True) | models.Q(doctor_id__in=pool_ids))
    if exclude_appointment_id is not None:
        appt_qs = appt_qs.exclude(pk=exclude_appointment_id)
    for did, st, en in appt_qs.values_list("doctor_id", "starts_at", "ends_at"):
        iv = (st.astimezone(tz), en.astimezone(tz))
        if did is None:
            busy_all.append(iv)
        else:
            busy[did].append(iv)

    # ── Phase C: day loop (pure Python) ──
    days: list[DaySlots] = []
    day = window_start
    while day <= window_end:
        wd = day.weekday()
        wh = work_hours.get(wd)
        if wh is None or wh.is_closed or wh.opens is None or wh.closes is None:
            if include_empty_days:
                days.append(DaySlots(day, wd, (), ClosedReason.CLINIC_CLOSED))
            day += ONE_DAY
            continue

        # closes==00:00 → kun oxiri (critique #23)
        closes = wh.closes
        if closes == time(0, 0):
            closes = time(23, 59, 59, 999999)
        if closes <= wh.opens:
            if include_empty_days:
                days.append(DaySlots(day, wd, (), ClosedReason.CLINIC_CLOSED))
            day += ONE_DAY
            continue

        day_lo, day_hi = L(day, time.min), L(day + ONE_DAY, time.min)
        clinic = (L(day, wh.opens), L(day, closes))
        holiday = clip(timeoff_clinic, day_lo, day_hi)
        if covers(holiday, clinic):
            if include_empty_days:
                days.append(DaySlots(day, wd, (), ClosedReason.CLINIC_HOLIDAY))
            day += ONE_DAY
            continue

        clinic_busy_all = clip(busy_all, day_lo, day_hi)  # doctor=NULL qabullar
        by_instant: dict[datetime, list[int]] = {}
        durations: dict[datetime, int] = {}
        saw_any_block = False
        saw_lead_cut = False

        for doc in pool:
            rows = [
                s
                for s in schedules[(doc.id, wd)]
                if (s.valid_from is None or s.valid_from <= day)
                and (s.valid_to is None or s.valid_to >= day)
            ]
            if not rows:
                continue
            blocked = (
                holiday
                + clinic_busy_all
                + clip(timeoff_doc[doc.id], day_lo, day_hi)
                + clip(busy[doc.id], day_lo, day_hi)
            )
            for sch in rows:
                dur_min = duration_minutes or sch.slot_minutes
                dur = timedelta(minutes=dur_min)
                step = timedelta(minutes=sch.slot_minutes)
                raw = (L(day, sch.start_time), L(day, sch.end_time))
                subs = split_on_break(raw, sch.break_start, sch.break_end, day)
                subs = [i for i in (intersect_clinic(s, clinic) for s in subs) if i]
                if subs:
                    saw_any_block = True
                for sub in subs:
                    free = subtract(sub, blocked)
                    if not free:
                        continue
                    c = sub[0]
                    while c + dur <= sub[1]:
                        end_c = c + dur
                        if fits_in_one(c, end_c, free):
                            if c >= earliest:
                                by_instant.setdefault(c, []).append(doc.id)
                                durations[c] = dur_min
                            else:
                                saw_lead_cut = True
                        c += step

        slots = tuple(
            Slot(t, t + timedelta(minutes=durations[t]), durations[t], tuple(sorted(set(ids))))
            for t, ids in sorted(by_instant.items())
        )
        if slots:
            reason = ClosedReason.OPEN
        elif saw_lead_cut and day == today:
            reason = ClosedReason.LEAD_TIME
        elif saw_any_block:
            reason = ClosedReason.FULLY_BOOKED
        else:
            reason = ClosedReason.NO_DOCTOR_SCHEDULE
        if slots or include_empty_days:
            days.append(DaySlots(day, wd, slots, reason))
        day += ONE_DAY

    return SlotResult(
        days=tuple(days),
        duration_minutes=duration_minutes,
        doctor_ids=tuple(pool_ids),
        timezone=settings.TIME_ZONE,
        generated_at=now,
        booking_enabled=True,
        window_start=window_start,
        window_end=window_end,
        reason=ClosedReason.OPEN,
    )


def intersect_clinic(sub: Interval, clinic: Interval) -> Interval | None:
    lo = max(sub[0], clinic[0])
    hi = min(sub[1], clinic[1])
    return (lo, hi) if lo < hi else None


def is_slot_available(
    *,
    doctor,
    service,
    starts_at: datetime,
    now: datetime | None = None,
    exclude_appointment_id: int | None = None,
) -> bool:
    """Write path guard: berilgan aniq vaqt engine chiqishida bormi?
    Arifmetika EMAS — engine chiqishida aʼzolik (critique #25). Grid tanaffusdan keyin
    qayta anchor boʻlgani uchun modulo tekshiruv notoʻgʻri boʻlardi."""
    tz = __import__("zoneinfo").ZoneInfo(settings.TIME_ZONE)
    d = starts_at.astimezone(tz).date()
    res = available_slots(
        date_from=d,
        date_to=d,
        doctor=doctor,
        service=service,
        now=now,
        exclude_appointment_id=exclude_appointment_id,
    )
    return any(s.start == starts_at for day in res.days for s in day.slots)
