"""send_reminders va retry_notifications testlari (critique #18, #31)."""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.notifications.models import NotificationLog
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor

pytestmark = pytest.mark.django_db


@pytest.fixture
def make(db):
    cat = ServiceCategory.objects.create(title="T", slug="t")
    svc = Service.objects.create(category=cat, title="K", slug="k", duration_minutes=30)
    doc = Doctor.objects.create(full_name="D", specialization="x")

    def _make(hours_from_now, **kw):
        start = timezone.now() + timedelta(hours=hours_from_now)
        return Appointment.objects.create(
            doctor=doc,
            service=svc,
            patient_name="B",
            phone="+998901112233",
            starts_at=start,
            ends_at=start + timedelta(minutes=30),
            source="admin",
            **kw,
        )

    return _make


def test_past_appointment_is_flagged_not_sent(make, settings):
    """O'tgan qabulga eslatma YUBORILMAYDI, faqat belgilanadi (critique #18)."""
    settings.TELEGRAM_BOT_TOKEN = ""
    past = make(-5)  # 5 soat oldin
    assert past.reminder_2h_sent_at is None
    call_command("send_reminders")
    past.refresh_from_db()
    assert past.reminder_2h_sent_at is not None  # belgilandi
    # yuborilmadi — o'tgan qabul uchun NotificationLog yaratilmadi
    assert not NotificationLog.objects.filter(template_key="reminder_2h").exists()


def test_upcoming_2h_appointment_gets_reminder(make, settings):
    settings.TELEGRAM_BOT_TOKEN = ""
    appt = make(1)  # 1 soatdan keyin — 2h oynasida
    call_command("send_reminders")
    appt.refresh_from_db()
    assert appt.reminder_2h_sent_at is not None
    assert NotificationLog.objects.filter(template_key="reminder_2h").exists()


def test_reminder_is_idempotent(make, settings):
    settings.TELEGRAM_BOT_TOKEN = ""
    make(1)
    call_command("send_reminders")
    call_command("send_reminders")  # ikkinchi marta — qayta yubormaydi
    assert NotificationLog.objects.filter(template_key="reminder_2h").count() == 1


def test_retry_drains_failed(make, settings, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "x"
    settings.TELEGRAM_CHAT_ID = "-100"
    # failed log yaratamiz
    log = NotificationLog.objects.create(
        channel="telegram",
        template_key="new_appointment",
        status="failed",
        attempts=1,
        next_retry_at=timezone.now() - timedelta(minutes=1),
        payload={"text": "retry me"},
    )
    import requests

    class Ok:
        status_code = 200

        def json(self):
            return {"ok": True}

    monkeypatch.setattr(requests, "post", lambda *a, **k: Ok())
    call_command("retry_notifications")
    log.refresh_from_db()
    assert log.status == "sent"
