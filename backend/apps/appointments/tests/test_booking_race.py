"""
ADR-007 (R-02, sotuvni yoʻqotadigan risk): ikki parallel booking'dan AYNAN bittasi
201, ikkinchisi 409 chiqishi kerak. Bu test Faza 2 uchun MERGE BLOCKER.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import time as dtime
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.db import connection, connections
from django.test import Client
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment
from apps.core.antispam import make_form_token
from apps.core.models import ClinicSettings, WorkingHours
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor, DoctorSchedule

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="ADR-007 Postgres talab qiladi (btree_gist)"
)

URL = "/api/v1/appointments/"


def _setup():
    """Test ichida (transaction=True) yaratamiz — truncation singletonni ham oʻchiradi."""
    cs = ClinicSettings.load()
    cs.booking_enabled = True
    cs.save()
    for wd in range(6):
        WorkingHours.objects.update_or_create(
            weekday=wd, defaults={"opens": dtime(9, 0), "closes": dtime(19, 0), "is_closed": False}
        )
    WorkingHours.objects.update_or_create(weekday=6, defaults={"is_closed": True})
    cat = ServiceCategory.objects.create(title="T", slug="t")
    svc = Service.objects.create(category=cat, title="Karies", slug="karies", duration_minutes=30)
    doc = Doctor.objects.create(full_name="Dilshod", specialization="terapevt", order=1)
    for wd in range(6):
        DoctorSchedule.objects.create(
            doctor=doc, weekday=wd, start_time=dtime(9, 0), end_time=dtime(19, 0), slot_minutes=30
        )
    return doc, svc


def _next_working_slot(now):
    """Ertaga (yoki keyingi ish kuni) 10:00 lokal."""
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Tashkent")
    d = now.astimezone(tz).date() + timedelta(days=1)
    while d.weekday() == 6:
        d += timedelta(days=1)
    from datetime import datetime

    return datetime(d.year, d.month, d.day, 10, 0, tzinfo=tz)


def _payload(doc_id, svc_id, starts_at, phone):
    return {
        "doctor": doc_id,
        "service": svc_id,
        "starts_at": starts_at.isoformat(),
        "patient_name": "Bemor",
        "phone": phone,
        "locale": "uz",
        "consent": True,
        "consent_text_version": "v1",
        "form_token": make_form_token(issued_at=time.time() - 5),  # 5s eski — timing'dan oʻtadi
    }


def _post(barrier, payload):
    client = Client()
    try:
        barrier.wait(timeout=10)
        r = client.post(URL, payload, content_type="application/json")
        return r.status_code, (r.json() if r.content else {})
    finally:
        connections.close_all()  # MAJBURIY — thread connection hygiene


@pytest.mark.django_db(transaction=True)
def test_concurrent_booking_yields_one_201_and_one_409(settings, monkeypatch):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "booking": "1000/hour",
            "lead": "1000/hour",
            "token": "1000/hour",
        },
    }
    # Tarmoqqa chiqmaslik kafolati
    monkeypatch.setattr(
        "apps.notifications.services.telegram.requests.post",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("testda tarmoq yoʻq")),
    )
    doc, svc = _setup()
    base = _next_working_slot(timezone.now())

    for i in range(12):
        cache.clear()
        slot = base + timedelta(minutes=30 * i)
        barrier = threading.Barrier(2)
        payloads = [
            _payload(doc.id, svc.id, slot, f"+9989011{i:05d}"),
            _payload(doc.id, svc.id, slot, f"+9989022{i:05d}"),
        ]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futs = [pool.submit(_post, barrier, p) for p in payloads]
            results = [f.result(timeout=15) for f in futs]

        statuses = sorted(s for s, _ in results)
        assert statuses[0] == 201, f"iter {i}: {statuses} — {results}"
        # Yutqazgan 409 (konkurent) yoki 400 slot_unavailable (pre-check tutdi) boʻlishi mumkin.
        loser_status, loser_body = next((s, b) for s, b in results if s != 201)
        assert loser_status in (409, 400), f"iter {i}: yutqazgan {loser_status}"
        assert loser_body.get("code") in ("slot_taken", "slot_unavailable"), loser_body

        # ASOSIY INVARIANT: bitta slotda aynan bitta faol qabul
        assert (
            Appointment.objects.filter(
                doctor=doc, starts_at=slot, status__in=ACTIVE_STATUSES
            ).count()
            == 1
        ), f"iter {i}: double-booking!"


@pytest.mark.django_db
def test_exclusion_violation_maps_to_409_slot_taken(settings, monkeypatch):
    """Deterministik: mavjud qabul ustiga bosdirilsa 409 slot_taken (konkurentsiz)."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "booking": "1000/hour",
            "lead": "1000/hour",
            "token": "1000/hour",
        },
    }
    # is_slot_available'ni HAR bog'langan joyda patch qilamiz (api.py va booking.py
    # uni import paytida bog'lab oladi) — shunda constraint yo'liga yetamiz.
    always = lambda **k: True  # noqa: E731
    monkeypatch.setattr("apps.appointments.api.is_slot_available", always)
    monkeypatch.setattr("apps.appointments.services.booking.is_slot_available", always)
    doc, svc = _setup()
    slot = _next_working_slot(timezone.now())
    Appointment.objects.create(
        doctor=doc,
        service=svc,
        patient_name="X",
        phone="+998901234500",
        starts_at=slot,
        ends_at=slot + timedelta(minutes=30),
        source="admin",
    )
    client = Client()
    r = client.post(
        URL, _payload(doc.id, svc.id, slot, "+998909998877"), content_type="application/json"
    )
    assert r.status_code == 409
    assert r.json()["code"] == "slot_taken"
    assert r["Content-Type"].startswith("application/problem+json")
