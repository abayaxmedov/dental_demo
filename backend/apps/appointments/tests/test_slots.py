"""
Slot engine edge-case matritsasi (dizayn spec §6). Har test bitta tekshiriladigan daʼvo.
`now` har doim inject qilinadi — testlar joriy vaqtga bogʻliq boʻlmasligi uchun.
"""

from datetime import timedelta

import pytest

from apps.appointments.models import Appointment, AppointmentStatus
from apps.appointments.services.slots import ClosedReason, available_slots, is_slot_available
from apps.team.models import Doctor, TimeOff

from .conftest import at, give_schedule, next_weekday

pytestmark = pytest.mark.django_db


def labels(res, day):
    d = next(x for x in res.days if x.day == day)
    return [s.label for s in d.slots]


def day_of(res, day):
    return next(x for x in res.days if x.day == day)


# now'ni har doim erta ertalabga qoʻyamiz — lead time bugungi slotlarni kesmasin.
def early(day):
    return at(day, 6, 0)


# ── Pool / konfiguratsiya ──


def test_e01_not_bookable_doctor_explicit(clinic, service, doctor):
    import django.utils.timezone as tzmod

    doctor.is_bookable = False
    doctor.save()
    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday())
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    assert res.reason == ClosedReason.DOCTOR_UNAVAILABLE


def test_e02_inactive_doctor(clinic, service, doctor):
    doctor.is_active = False
    doctor.save()
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday())
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    assert res.reason == ClosedReason.DOCTOR_UNAVAILABLE


def test_e03_inactive_service(clinic, service, doctor):
    service.is_active = False
    service.save()
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday())
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    assert res.reason == ClosedReason.SERVICE_UNAVAILABLE


def test_e04_booking_disabled(clinic, service, doctor):
    clinic.booking_enabled = False
    clinic.save()
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday())
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    assert res.reason == ClosedReason.BOOKING_DISABLED
    assert res.days == ()
    assert is_slot_available(doctor=doctor, service=service, starts_at=at(mon, 10)) is False


def test_e06_service_with_no_doctors_falls_back_to_all(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday())
    # service.doctors bo'sh → hamma bookable doctor
    res = available_slots(date_from=mon, date_to=mon, service=service, now=early(mon))
    assert len(labels(res, mon)) > 0


def test_e07_zero_bookable_doctors(clinic, service):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    res = available_slots(date_from=mon, date_to=mon, service=service, now=early(mon))
    assert res.reason == ClosedReason.NO_DOCTOR_SCHEDULE


# ── Klinika chegaralari ──


def test_e09_clinic_closed_weekday(clinic, service, doctor):
    import django.utils.timezone as tzmod

    sun = next_weekday(tzmod.localdate() + timedelta(days=1), 6)
    give_schedule(doctor, 6)  # doctor ishlaydi, lekin klinika yopiq
    res = available_slots(
        date_from=sun, date_to=sun, doctor=doctor, service=service, now=early(sun)
    )
    assert day_of(res, sun).closed_reason == ClosedReason.CLINIC_CLOSED


def test_e12_doctor_wider_than_clinic_is_clamped(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), start=(7, 0), end=(22, 0), slot=60)
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    ls = labels(res, mon)
    assert ls[0] == "09:00"  # klinika 09:00 dan oldin emas
    assert "08:00" not in ls
    assert all(lab <= "18:30" for lab in ls)  # 18:30+30=19:00 oxirgi


# ── Tanaffus ──


def test_e23_duration_ending_exactly_at_break_allowed(clinic, implant, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(
        doctor, mon.weekday(), start=(9, 0), end=(13, 0), slot=30, brk=((11, 0), (11, 30))
    )
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=implant, now=early(mon)
    )
    ls = labels(res, mon)
    assert "09:30" in ls  # 09:30+90=11:00 == break_start, [) yarim-ochiq → ruxsat
    assert "10:00" not in ls  # 10:00+90=11:30 tanaffusni kesadi


def test_e25_grid_reanchors_after_break(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(
        doctor, mon.weekday(), start=(9, 15), end=(16, 0), slot=30, brk=((13, 0), (14, 0))
    )
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
    )
    ls = labels(res, mon)
    assert "14:00" in ls  # tanaffusdan keyin qayta anchor (14:15 emas)
    assert "14:15" not in ls


# ── Davomiylik ──


def test_worked_example_90_on_30_grid(clinic, implant, doctor):
    """Spec §3 aniq misol: 09:00–13:00, tanaffus 11:00–11:30, 90 daq → 09:00, 09:30, 11:30."""
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(
        doctor, mon.weekday(), start=(9, 0), end=(13, 0), slot=30, brk=((11, 0), (11, 30))
    )
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=implant, now=early(mon)
    )
    assert labels(res, mon) == ["09:00", "09:30", "11:30"]


def test_e35_short_appointment_destroys_long_capacity(clinic, implant, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(
        doctor, mon.weekday(), start=(9, 0), end=(13, 0), slot=30, brk=((11, 0), (11, 30))
    )
    # 11:30–12:00 tozalash → 11:30 implant sig'maydi
    Appointment.objects.create(
        doctor=doctor,
        service=service,
        patient_name="X",
        phone="+998901234567",
        starts_at=at(mon, 11, 30),
        ends_at=at(mon, 12, 0),
    )
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=implant, now=early(mon)
    )
    assert labels(res, mon) == ["09:00", "09:30"]


def test_e57_duration_equals_block(clinic, doctor, category):
    import django.utils.timezone as tzmod

    from apps.services.models import Service

    svc = Service.objects.create(
        category=category, title="Katta", slug="katta", duration_minutes=240
    )
    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), start=(9, 0), end=(13, 0), slot=30)
    res = available_slots(date_from=mon, date_to=mon, doctor=doctor, service=svc, now=early(mon))
    assert labels(res, mon) == ["09:00"]


# ── Qabullar ──


def test_e29_abutting_appointment_not_overlap(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    Appointment.objects.create(
        doctor=doctor,
        service=service,
        patient_name="X",
        phone="+998901234567",
        starts_at=at(mon, 10, 0),
        ends_at=at(mon, 10, 30),
    )
    ls = labels(
        _res := available_slots(
            date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
        ),
        mon,
    )
    assert "10:00" not in ls
    assert "09:30" in ls and "10:30" in ls  # tegib turish overlap emas


def test_e30_cancelled_appointment_frees_slot(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    Appointment.objects.create(
        doctor=doctor,
        service=service,
        patient_name="X",
        phone="+998901234567",
        starts_at=at(mon, 10, 0),
        ends_at=at(mon, 10, 30),
        status=AppointmentStatus.CANCELLED_BY_PATIENT,
    )
    assert "10:00" in labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)),
        mon,
    )


def test_e38_null_doctor_appointment_blocks_all(clinic, service, doctor):
    """doctor=NULL faol qabul HAMMA shifokorni bloklaydi (critique #21)."""
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    Appointment.objects.create(
        doctor=None,
        service=service,
        patient_name="Phone",
        phone="+998901234567",
        starts_at=at(mon, 10, 0),
        ends_at=at(mon, 10, 30),
        source="phone",
    )
    assert "10:00" not in labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)),
        mon,
    )


# ── TimeOff ──


def test_e39_doctor_timeoff_partial_day(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    TimeOff.objects.create(
        doctor=doctor, starts_at=at(mon, 12, 0), ends_at=at(mon, 19, 0), reason="dam"
    )
    ls = labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)),
        mon,
    )
    assert "11:00" in ls
    assert all(lab < "12:00" for lab in ls)


def test_e40_clinic_wide_timeoff_full_day(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    TimeOff.objects.create(
        doctor=None, starts_at=at(mon, 0, 0), ends_at=at(mon, 23, 59), reason="bayram"
    )
    assert (
        day_of(
            available_slots(
                date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)
            ),
            mon,
        ).closed_reason
        == ClosedReason.CLINIC_HOLIDAY
    )


def test_e42_multiday_timeoff_clips_per_day(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=2), 0)
    for wd in range(6):
        give_schedule(doctor, wd, slot=30)
    tue = mon + timedelta(days=1)
    wed = mon + timedelta(days=2)
    # Mon 14:00 → Wed 10:00
    TimeOff.objects.create(
        doctor=doctor, starts_at=at(mon, 14, 0), ends_at=at(wed, 10, 0), reason="tatil"
    )
    res = available_slots(
        date_from=mon, date_to=wed, doctor=doctor, service=service, now=at(mon, 6)
    )
    assert all(lab < "14:00" for lab in labels(res, mon))  # Mon ertalab bor
    assert labels(res, tue) == []  # Tue to'liq band
    assert any(lab >= "10:00" for lab in labels(res, wed))  # Wed 10:00 dan bor


def test_e24_timeoff_boundary_half_open(clinic, service, doctor):
    """TimeOff 14:00 da tugasa 14:00 slot bo'shaydi; 14:00 da boshlansa o'chadi (critique #24)."""
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    TimeOff.objects.create(
        doctor=doctor, starts_at=at(mon, 9, 0), ends_at=at(mon, 14, 0), reason="x"
    )
    ls = labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=early(mon)),
        mon,
    )
    assert "14:00" in ls  # tugash chegarasi ochiq
    assert "13:30" not in ls  # 13:30+30=14:00 blok ichida


# ── Lead time / oyna ──


def test_e46_lead_time_boundary_inclusive(clinic, service, doctor):
    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    now = at(mon, 9, 0)  # 2h lead → 11:00 birinchi
    ls = labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=now), mon
    )
    assert "11:00" in ls
    assert "10:30" not in ls


def test_e47_today_all_within_lead_shows_lead_time_reason(clinic, service, doctor):
    import django.utils.timezone as tzmod

    today = tzmod.localdate()
    if today.weekday() == 6:
        pytest.skip("yakshanba")
    give_schedule(doctor, today.weekday(), slot=30)
    now = at(today, 18, 30)  # klinika 19:00 yopiladi, 2h lead → hech narsa
    res = available_slots(date_from=today, date_to=today, doctor=doctor, service=service, now=now)
    assert day_of(res, today).closed_reason == ClosedReason.LEAD_TIME


def test_e48_window_clamped_to_30_days(clinic, service, doctor):
    import django.utils.timezone as tzmod

    today = tzmod.localdate()
    for wd in range(6):
        give_schedule(doctor, wd, slot=30)
    res = available_slots(
        date_from=today,
        date_to=today + timedelta(days=60),
        doctor=doctor,
        service=service,
        now=at(today, 6),
    )
    assert res.window_end == today + timedelta(days=30)


# ── Timezone ──


def test_e60_no_active_tz_leakage(clinic, service, doctor):
    import django.utils.timezone as tzmod
    from django.utils import timezone as djtz

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    now = at(mon, 6)
    a = labels(
        available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=now), mon
    )
    djtz.activate("UTC")
    try:
        b = labels(
            available_slots(date_from=mon, date_to=mon, doctor=doctor, service=service, now=now),
            mon,
        )
    finally:
        djtz.deactivate()
    assert a == b


def test_e61_all_slots_aware(clinic, service, doctor):
    import django.utils.timezone as tzmod
    from django.utils import timezone as djtz

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    res = available_slots(
        date_from=mon, date_to=mon, doctor=doctor, service=service, now=at(mon, 6)
    )
    assert all(djtz.is_aware(s.start) and djtz.is_aware(s.end) for d in res.days for s in d.slots)


def test_e62_naive_now_raises(clinic, service, doctor):
    from datetime import datetime

    import django.utils.timezone as tzmod

    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    with pytest.raises(ValueError):
        available_slots(
            date_from=mon, date_to=mon, doctor=doctor, service=service, now=datetime(2026, 9, 1, 10)
        )


# ── Any-doctor merge ──


def test_e63_two_doctors_merge_to_one_slot(clinic, service, doctor):
    import django.utils.timezone as tzmod

    d2 = Doctor.objects.create(full_name="Nigora", specialization="ortodont", order=2)
    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    give_schedule(d2, mon.weekday(), slot=30)
    res = available_slots(date_from=mon, date_to=mon, service=service, now=at(mon, 6))
    d = day_of(res, mon)
    s = next(s for s in d.slots if s.label == "10:00")
    assert s.doctor_ids == tuple(sorted([doctor.id, d2.id]))


def test_e64_one_doctor_busy_slot_shows_other(clinic, service, doctor):
    import django.utils.timezone as tzmod

    d2 = Doctor.objects.create(full_name="Nigora", specialization="ortodont", order=2)
    mon = next_weekday(tzmod.localdate() + timedelta(days=1), 0)
    give_schedule(doctor, mon.weekday(), slot=30)
    give_schedule(d2, mon.weekday(), slot=30)
    Appointment.objects.create(
        doctor=doctor,
        service=service,
        patient_name="X",
        phone="+998901234567",
        starts_at=at(mon, 10, 0),
        ends_at=at(mon, 10, 30),
    )
    res = available_slots(date_from=mon, date_to=mon, service=service, now=at(mon, 6))
    s = next(s for s in day_of(res, mon).slots if s.label == "10:00")
    assert s.doctor_ids == (d2.id,)


# ── Performance ──


def test_query_count_is_constant(clinic, service, doctor, django_assert_max_num_queries):
    """Query soni oyna uzunligidan mustaqil (Phase B fetch, Phase C compute)."""
    import django.utils.timezone as tzmod

    d2 = Doctor.objects.create(full_name="D2", specialization="x", order=2)
    d3 = Doctor.objects.create(full_name="D3", specialization="y", order=3)
    today = tzmod.localdate()
    for doc in (doctor, d2, d3):
        for wd in range(6):
            give_schedule(doc, wd, slot=30)
    # 30 kun × 3 shifokor — 8 tadan ko'p bo'lmasligi kerak (critique #31: 6 emas <=8)
    with django_assert_max_num_queries(8):
        available_slots(
            date_from=today, date_to=today + timedelta(days=30), service=service, now=at(today, 6)
        )
