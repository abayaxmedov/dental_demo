"""Booking/lead write API contract testlari (spec §8.3, critique fixes)."""

import time
from datetime import datetime, timedelta
from datetime import time as dtime
from zoneinfo import ZoneInfo

import pytest
from django.test import Client
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.core.antispam import make_form_token
from apps.core.models import ClinicSettings, WorkingHours
from apps.leads.models import Lead
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor, DoctorSchedule

TZ = ZoneInfo("Asia/Tashkent")
URL = "/api/v1/appointments/"
LEAD_URL = "/api/v1/leads/"


@pytest.fixture(autouse=True)
def _high_throttle(settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "booking": "1000/hour",
            "lead": "1000/hour",
            "token": "1000/hour",
        },
    }
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def setup(db):
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


def next_slot(days_ahead=1, hour=10):
    d = timezone.localdate() + timedelta(days=days_ahead)
    while d.weekday() == 6:  # Yakshanba — klinika yopiq
        d += timedelta(days=1)
    return datetime(d.year, d.month, d.day, hour, 0, tzinfo=TZ)


def payload(doc, svc, **over):
    base = {
        "doctor": doc.id,
        "service": svc.id,
        "starts_at": next_slot().isoformat(),
        "patient_name": "Bemor",
        "phone": "+998901112233",
        "locale": "uz",
        "consent": True,
        "consent_text_version": "v1",
        "form_token": make_form_token(issued_at=time.time() - 5),
    }
    base.update(over)
    return base


@pytest.fixture
def client():
    return Client()


def post(client, body, url=URL):
    return client.post(url, body, content_type="application/json")


# ── Anti-spam ──


def test_honeypot_returns_fake_201_and_persists_nothing(client, setup):
    doc, svc = setup
    r = post(client, payload(doc, svc, referral_note_2="i am a bot"))
    assert r.status_code == 201
    assert r.json()["notified"] is False
    assert Appointment.objects.count() == 0  # hech narsa saqlanmadi


def test_too_fast_is_rejected(client, setup):
    doc, svc = setup
    r = post(client, payload(doc, svc, form_token=make_form_token(issued_at=time.time() - 0.5)))
    assert r.status_code == 400 and r.json()["code"] == "too_fast"


def test_missing_consent_returns_consent_required(client, setup):
    doc, svc = setup
    r = post(client, payload(doc, svc, consent=False))
    assert r.status_code == 400 and r.json()["code"] == "consent_required"


def test_invalid_phone_returns_invalid_phone(client, setup):
    doc, svc = setup
    r = post(client, payload(doc, svc, phone="12345"))
    assert r.status_code == 400 and r.json()["code"] == "invalid_phone"


def test_missing_service_returns_400(client, setup):
    doc, svc = setup
    body = payload(doc, svc)
    del body["service"]
    r = post(client, body)
    assert r.status_code == 400  # service required


def test_naive_datetime_handled_gracefully(client, setup):
    """DRF naive datetime'ni Asia/Tashkent'da lokalizatsiya qiladi — crash EMAS, xushmuomala javob."""
    doc, svc = setup
    naive = next_slot().replace(tzinfo=None).isoformat()
    r = post(client, payload(doc, svc, starts_at=naive))
    assert r.status_code in (201, 400)  # 500 EMAS


# ── Data integrity: server client vaqtiga ishonmaydi ──


def test_tampered_sunday_time_rejected(client, setup):
    """Yakshanba 03:00 — DB constraint qabul qilardi, lekin is_slot_available rad etadi (critique #25)."""
    doc, svc = setup
    d = timezone.localdate() + timedelta(days=(6 - timezone.localdate().weekday()) % 7 or 7)
    sunday_3am = datetime(d.year, d.month, d.day, 3, 0, tzinfo=TZ)
    r = post(client, payload(doc, svc, starts_at=sunday_3am.isoformat()))
    assert r.status_code in (400, 403)
    assert r.json()["code"] in ("slot_unavailable", "lead_time_violation", "booking_disabled")
    assert Appointment.objects.count() == 0


def test_booking_disabled_returns_403(client, setup):
    doc, svc = setup
    cs = ClinicSettings.load()
    cs.booking_enabled = False
    cs.save()
    r = post(client, payload(doc, svc))
    assert r.status_code == 403 and r.json()["code"] == "booking_disabled"


def test_inactive_doctor_cannot_be_booked(client, setup):
    doc, svc = setup
    doc.is_bookable = False
    doc.save()
    r = post(client, payload(doc, svc))
    assert r.status_code >= 400
    assert Appointment.objects.count() == 0


# ── Muvaffaqiyat ──


def test_successful_booking_creates_pending_appointment(client, setup):
    doc, svc = setup
    r = post(client, payload(doc, svc))
    assert r.status_code == 201
    body = r.json()
    assert body["code"].startswith("A-")
    assert "cancel_token" in body
    appt = Appointment.objects.get(code=body["code"])
    assert appt.status == "pending" and appt.source == "web"
    assert appt.consent_given_at is not None
    assert appt.ip_hash  # tuzlangan hash saqlandi


def test_admin_session_cookie_does_not_403(client, setup, django_user_model):
    """Admin sessiyasi bilan ham booking POST 403 bermaydi (critique #4: auth classes bo'sh)."""
    doc, svc = setup
    user = django_user_model.objects.create_superuser("staff", "s@x.uz", "pw")
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(user)
    r = csrf_client.post(URL, payload(doc, svc), content_type="application/json")
    assert r.status_code == 201  # sessiya cookie CSRF 403 bermadi


# ── Idempotency ──


def test_idempotency_key_replays_same_appointment(client, setup):
    import uuid

    doc, svc = setup
    key = str(uuid.uuid4())
    r1 = post(client, payload(doc, svc, idempotency_key=key))
    r2 = post(client, payload(doc, svc, idempotency_key=key))
    assert r1.status_code == 201 and r2.status_code == 200
    assert r1.json()["cancel_token"] == r2.json()["cancel_token"]
    assert Appointment.objects.count() == 1


# ── Cancel ──


def test_cancel_frees_slot_and_notifies(client, setup):
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    r = client.post(
        f"/api/v1/appointments/{ct}/cancel/", {"reason": "x"}, content_type="application/json"
    )
    assert r.status_code == 200 and r.json()["status"] == "cancelled_by_patient"
    # slot bo'shadi
    r2 = post(client, payload(doc, svc, phone="+998907776655"))
    assert r2.status_code == 201


def test_cancel_unknown_token_404(client, setup):
    import uuid

    r = client.post(
        f"/api/v1/appointments/{uuid.uuid4()}/cancel/", {}, content_type="application/json"
    )
    assert r.status_code == 404 and r.json()["code"] == "not_found"


def test_double_cancel_returns_already_cancelled(client, setup):
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    client.post(f"/api/v1/appointments/{ct}/cancel/", {}, content_type="application/json")
    r = client.post(f"/api/v1/appointments/{ct}/cancel/", {}, content_type="application/json")
    assert r.status_code == 409 and r.json()["code"] == "already_cancelled"


# ── Public retrieve (bemor token orqali ko'radi) ──


def test_public_retrieve_exposes_reschedule_contract(client, setup):
    """Reschedule UI shu maydonlarga tayanadi: service_id, doctor_id, can_reschedule."""
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    r = client.get(f"/api/v1/appointments/{ct}/")
    assert r.status_code == 200
    data = r.json()
    assert data["service_id"] == svc.id
    assert data["doctor_id"] == doc.id
    assert data["can_reschedule"] is True
    # Ichki maydonlar OSHKOR ETILMAYDI (token — bemorники, staff emas)
    assert "cancel_token" not in data
    assert "phone" not in data


def test_public_retrieve_null_doctor(client, setup):
    """Shifokorsiz qabulda (admin/telefon — DB constraint faqat web'da majbur qiladi)
    doctor_id null bo'ladi va serializer 500 bermaydi."""
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    appt = Appointment.objects.get(cancel_token=ct)
    appt.source = Appointment.Source.ADMIN  # web bo'lmagan manba doctor=NULL'ga ruxsat beradi
    appt.doctor = None
    appt.save(update_fields=["source", "doctor"])
    r = client.get(f"/api/v1/appointments/{ct}/")
    assert r.status_code == 200
    assert r.json()["doctor_id"] is None
    assert r.json()["service_id"] == svc.id


# ── Reschedule ──


def test_reschedule_moves_and_clears_reminders(client, setup):
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    appt = Appointment.objects.get(cancel_token=ct)
    appt.reminder_24h_sent_at = timezone.now()
    appt.save()
    new = next_slot(days_ahead=3, hour=11)  # boshqa ish kuni (Yakshanba o'tkaziladi)
    r = client.post(
        f"/api/v1/appointments/{ct}/reschedule/",
        {"starts_at": new.isoformat()},
        content_type="application/json",
    )
    assert r.status_code == 200
    appt.refresh_from_db()
    assert appt.reschedule_count == 1
    assert appt.reminder_24h_sent_at is None  # KRITIK (spec §6.3)


def test_reschedule_within_own_footprint(client, setup):
    """O'z qatorini istisno qilib mavjudlik tekshiriladi (critique #16)."""
    doc, svc = setup
    ct = post(client, payload(doc, svc)).json()["cancel_token"]
    appt = Appointment.objects.get(cancel_token=ct)
    new = appt.starts_at + timedelta(minutes=30)  # 30 daq siljish — o'z izi bilan yaqin
    r = client.post(
        f"/api/v1/appointments/{ct}/reschedule/",
        {"starts_at": new.isoformat()},
        content_type="application/json",
    )
    assert r.status_code == 200


# ── Lead ──


def test_lead_creates_and_dedupes(client, setup):
    body = {
        "kind": "callback",
        "name": "Ali",
        "phone": "+998905556677",
        "consent": True,
        "form_token": make_form_token(issued_at=time.time() - 5),
        "locale": "uz",
    }
    r1 = post(client, body, url=LEAD_URL)
    r2 = post(
        client, dict(body, form_token=make_form_token(issued_at=time.time() - 5)), url=LEAD_URL
    )
    assert r1.status_code == 201 and r1.json()["ok"] is True
    assert r2.status_code == 201 and r2.json().get("deduplicated") is True
    assert Lead.objects.count() == 1  # dedupe ishladi


def test_lead_honeypot(client, setup):
    body = {
        "kind": "callback",
        "name": "Bot",
        "phone": "+998905556677",
        "consent": True,
        "form_token": make_form_token(issued_at=time.time() - 5),
        "referral_note_2": "x",
    }
    r = post(client, body, url=LEAD_URL)
    assert r.status_code == 201
    assert Lead.objects.count() == 0
