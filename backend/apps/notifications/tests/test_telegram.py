"""Telegram klient va xabarnoma testlari (ADR-006/010)."""

from datetime import timedelta

import pytest
import requests
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.notifications.models import NotificationLog
from apps.notifications.services import messages as tpl
from apps.notifications.services.notify import (
    notify_new_appointment,
)
from apps.notifications.services.telegram import escape_html, send_message
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor

pytestmark = pytest.mark.django_db


@pytest.fixture
def appt(db):
    cat = ServiceCategory.objects.create(title="T", slug="t")
    svc = Service.objects.create(category=cat, title="Implant", slug="implant", duration_minutes=90)
    doc = Doctor.objects.create(full_name="Dilshod Raximov", specialization="implantolog")
    start = timezone.now() + timedelta(days=1)
    return Appointment.objects.create(
        doctor=doc,
        service=svc,
        patient_name="Aziza Karimova",
        phone="+998901112233",
        starts_at=start,
        ends_at=start + timedelta(minutes=90),
        source="admin",
        locale="ru",
    )


def test_escape_html():
    assert escape_html("A & B < C > D") == "A &amp; B &lt; C &gt; D"


def test_empty_token_degrades_not_crashes(settings, appt):
    settings.TELEGRAM_BOT_TOKEN = ""
    res = send_message("test")
    assert res.ok is False and res.error == "not_configured" and res.permanent is True


def test_notify_writes_log_even_when_unconfigured(settings, appt):
    settings.TELEGRAM_BOT_TOKEN = ""
    ok = notify_new_appointment(appt)
    assert ok is False
    log = NotificationLog.objects.latest("created_at")
    assert log.template_key == "new_appointment"
    assert log.status == NotificationLog.Status.ABANDONED  # not_configured = permanent


def test_message_contains_key_fields(appt):
    text = tpl.new_appointment(appt)
    assert "Aziza Karimova" in text
    assert "+998901112233" in text
    assert appt.code in text
    assert "Til: rus" in text  # bemor tili staff uchun ko'rsatiladi (finding #29)


def test_transient_error_schedules_retry(settings, appt, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "x"
    settings.TELEGRAM_CHAT_ID = "-100"

    class FakeResp:
        status_code = 503
        text = "server error"

        def json(self):
            return {}

    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp())
    ok = notify_new_appointment(appt)
    assert ok is False
    log = NotificationLog.objects.latest("created_at")
    assert log.status == NotificationLog.Status.FAILED
    assert log.next_retry_at is not None  # qayta urinish rejalashtirildi


def test_permanent_error_abandons(settings, appt, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "x"
    settings.TELEGRAM_CHAT_ID = "-100"

    class FakeResp:
        status_code = 403
        text = "bot was kicked"

        def json(self):
            return {"description": "Forbidden"}

    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp())
    notify_new_appointment(appt)
    log = NotificationLog.objects.latest("created_at")
    assert log.status == NotificationLog.Status.ABANDONED


def test_successful_send(settings, appt, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "x"
    settings.TELEGRAM_CHAT_ID = "-100"

    class FakeResp:
        status_code = 200

        def json(self):
            return {"ok": True, "result": {}}

    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp())
    assert notify_new_appointment(appt) is True
    log = NotificationLog.objects.latest("created_at")
    assert log.status == NotificationLog.Status.SENT and log.sent_at is not None


def test_timeout_is_caught(settings, appt, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "x"
    settings.TELEGRAM_CHAT_ID = "-100"

    def _raise(*a, **k):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "post", _raise)
    # exception bemorga yetib bormasligi kerak
    assert notify_new_appointment(appt) is False
