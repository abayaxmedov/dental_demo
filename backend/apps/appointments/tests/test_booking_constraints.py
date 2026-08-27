"""
ADR-007 kafolatlari (R-02 "sotuvni yoʻqotadigan" risk).
Bu testlar Faza 2 uchun merge blocker.
"""

from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus, InvalidTransition
from apps.team.models import Doctor


@pytest.fixture
def doctor(db):
    return Doctor.objects.create(full_name="Dilshod Raximov", specialization="implantolog")


@pytest.fixture
def slot():
    start = timezone.now() + timedelta(days=1)
    return start, start + timedelta(minutes=30)


def _make(doctor, start, end, **kw):
    # source="admin" — web-only constraint (doctor+service majburiy) bu birlik
    # testlarga taalluqli emas; ular exclusion constraint va state machine'ni sinaydi.
    kw.setdefault("source", "admin")
    return Appointment.objects.create(
        doctor=doctor,
        patient_name=kw.pop("name", "Bemor"),
        phone=kw.pop("phone", "+998901234567"),
        starts_at=start,
        ends_at=end,
        **kw,
    )


def test_overlapping_appointment_rejected_by_db(doctor, slot):
    """Bir shifokorda kesishuvchi faol qabul DB tomonidan rad etiladi."""
    start, end = slot
    _make(doctor, start, end)

    with pytest.raises(IntegrityError), transaction.atomic():
        _make(doctor, start + timedelta(minutes=10), end + timedelta(minutes=10), name="B")


def test_adjacent_appointment_allowed(doctor, slot):
    """Ketma-ket (chegara tegib turgan) qabullar ruxsat etiladi — '[)' oraliq."""
    start, end = slot
    _make(doctor, start, end)
    later = _make(doctor, end, end + timedelta(minutes=30), name="B")
    assert later.pk


def test_cancelled_appointment_frees_the_slot(doctor, slot):
    """Bekor qilingan qabul slotni darhol boʻshatadi (Faza 2 DoD)."""
    start, end = slot
    first = _make(doctor, start, end)
    first.cancel_by_patient()

    assert _make(doctor, start, end, name="C").pk


def test_appointments_without_doctor_do_not_collide(db, slot):
    """doctor=None ('istalgan boʻsh') exclusion constraint'ga tushmaydi.
    Eslatma: doctor=None faqat admin/telefon uchun (web-requires-doctor constraint) —
    va slot engine bunday qabullarni HAMMA shifokorni bloklovchi deb hisoblaydi (critique #21)."""
    start, end = slot
    Appointment.objects.create(
        patient_name="A", phone="+998901111111", starts_at=start, ends_at=end, source="phone"
    )
    Appointment.objects.create(
        patient_name="B", phone="+998902222222", starts_at=start, ends_at=end, source="phone"
    )


def test_end_must_be_after_start(doctor, slot):
    start, end = slot
    with pytest.raises(IntegrityError), transaction.atomic():
        _make(doctor, end, start)


@pytest.mark.parametrize(
    "start_status,target",
    [
        (AppointmentStatus.COMPLETED, AppointmentStatus.CONFIRMED),
        (AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CONFIRMED),
        (AppointmentStatus.NO_SHOW, AppointmentStatus.PENDING),
    ],
)
def test_terminal_statuses_are_terminal(doctor, slot, start_status, target):
    start, end = slot
    appt = _make(doctor, start, end, status=start_status)
    with pytest.raises(InvalidTransition):
        appt.transition_to(target)


def test_pending_to_confirmed_to_completed(doctor, slot):
    start, end = slot
    appt = _make(doctor, start, end)
    appt.confirm()
    assert appt.status == AppointmentStatus.CONFIRMED
    appt.transition_to(AppointmentStatus.COMPLETED)
    assert appt.status == AppointmentStatus.COMPLETED


def test_code_and_cancel_token_are_unique(doctor, slot):
    start, end = slot
    a = _make(doctor, start, end)
    b = _make(doctor, end, end + timedelta(minutes=30), name="B")
    assert a.code != b.code
    assert a.cancel_token != b.cancel_token
