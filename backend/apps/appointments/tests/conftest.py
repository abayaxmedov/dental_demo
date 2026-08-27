"""Slot engine testlari uchun umumiy fixtures va yordamchilar."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from apps.core.models import ClinicSettings, WorkingHours
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor, DoctorSchedule

TZ = ZoneInfo("Asia/Tashkent")


def at(d: date, h: int, m: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, h, m, tzinfo=TZ)


@pytest.fixture
def clinic(db):
    cs = ClinicSettings.load()
    cs.booking_enabled = True
    cs.save()
    # Du–Sha ochiq 09:00–19:00, Yakshanba yopiq
    for wd in range(6):
        WorkingHours.objects.update_or_create(
            weekday=wd, defaults={"opens": time(9, 0), "closes": time(19, 0), "is_closed": False}
        )
    WorkingHours.objects.update_or_create(weekday=6, defaults={"is_closed": True})
    return cs


@pytest.fixture
def category(db):
    return ServiceCategory.objects.create(title="Terapiya", slug="terapiya")


@pytest.fixture
def service(category):
    return Service.objects.create(
        category=category, title="Karies", slug="karies", duration_minutes=30
    )


@pytest.fixture
def implant(category):
    return Service.objects.create(
        category=category, title="Implant", slug="implant", duration_minutes=90
    )


@pytest.fixture
def doctor(db):
    return Doctor.objects.create(full_name="Dilshod", specialization="terapevt", order=1)


def give_schedule(doc, weekday, start=(9, 0), end=(19, 0), slot=30, brk=None, vf=None, vt=None):
    return DoctorSchedule.objects.create(
        doctor=doc,
        weekday=weekday,
        start_time=time(*start),
        end_time=time(*end),
        slot_minutes=slot,
        break_start=time(*brk[0]) if brk else None,
        break_end=time(*brk[1]) if brk else None,
        valid_from=vf,
        valid_to=vt,
    )


def next_weekday(from_date: date, weekday: int) -> date:
    """from_date dan keyingi (yoki teng) berilgan weekday sanasi."""
    days = (weekday - from_date.weekday()) % 7
    return from_date + timedelta(days=days)
