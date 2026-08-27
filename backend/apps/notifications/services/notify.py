"""
Xabarnoma yuborish: NotificationLog yozadi, keyin yuboradi.
Log AVVAL yaratiladi — send o'rtasida crash bo'lsa ham iz qoladi (spec §3).
Yuborish TRANZAKSIYADAN TASHQARIDA chaqiriladi (view on_commit qiladi) — critique #3.
"""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.notifications.models import NotificationLog

from . import messages as tpl
from .telegram import send_message

# Exponential backoff jadvali (daqiqa) — urinish 1..6 (spec §5.3)
BACKOFF_MINUTES = [5, 15, 30, 60, 180, 360]
MAX_ATTEMPTS = 6


def _log_for(obj, template_key: str, target: str) -> NotificationLog:
    ct = ContentType.objects.get_for_model(obj.__class__)
    return NotificationLog.objects.create(
        channel=NotificationLog.Channel.TELEGRAM,
        template_key=template_key,
        target=target,
        content_type=ct,
        object_id=obj.pk,
        status=NotificationLog.Status.PENDING,
    )


def _deliver(log: NotificationLog, text: str) -> bool:
    """Bitta urinish. NotificationLog'ni yangilaydi. True = yuborildi."""

    log.attempts += 1
    log.payload = {"text": text}
    res = send_message(text)
    if res.ok:
        log.status = NotificationLog.Status.SENT
        log.sent_at = timezone.now()
        log.last_error = ""
        log.next_retry_at = None
        log.save(
            update_fields=[
                "attempts",
                "payload",
                "status",
                "sent_at",
                "last_error",
                "next_retry_at",
            ]
        )
        return True

    log.last_error = res.error
    if res.permanent or log.attempts >= MAX_ATTEMPTS:
        log.status = NotificationLog.Status.ABANDONED
        log.next_retry_at = None
    else:
        log.status = NotificationLog.Status.FAILED
        idx = min(log.attempts - 1, len(BACKOFF_MINUTES) - 1)
        delay = res.retry_after or BACKOFF_MINUTES[idx] * 60
        from datetime import timedelta

        log.next_retry_at = timezone.now() + timedelta(seconds=delay)
    log.save(update_fields=["attempts", "payload", "status", "last_error", "next_retry_at"])
    return False


def notify_new_appointment(appt) -> bool:
    log = _log_for(appt, "new_appointment", appt.code)
    return _deliver(log, tpl.new_appointment(appt))


def notify_new_lead(lead) -> bool:
    log = _log_for(lead, "new_lead", lead.phone)
    return _deliver(log, tpl.new_lead(lead))


def notify_cancelled(appt, *, late=False, reason="") -> bool:
    log = _log_for(appt, "appointment_cancelled", appt.code)
    return _deliver(log, tpl.appointment_cancelled(appt, late=late, reason=reason))


def notify_rescheduled(appt, *, old_start, doctor_changed=False) -> bool:
    log = _log_for(appt, "appointment_rescheduled", appt.code)
    return _deliver(
        log, tpl.appointment_rescheduled(appt, old_start=old_start, doctor_changed=doctor_changed)
    )
