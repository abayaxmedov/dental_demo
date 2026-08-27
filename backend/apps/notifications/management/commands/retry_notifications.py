"""
Muvaffaqiyatsiz xabarnomalarni qayta yuboradi (ADR-006, cron */5 daq).
Bitta VPS + flock qilingan cron — distributed queue mashinasi KERAK EMAS (critique #31).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import NotificationLog
from apps.notifications.services.notify import _deliver

BATCH = 50


class Command(BaseCommand):
    help = "Muvaffaqiyatsiz Telegram xabarnomalarini qayta yuboradi."

    def handle(self, *args, **opts):
        now = timezone.now()
        qs = NotificationLog.objects.filter(
            status=NotificationLog.Status.FAILED,
            next_retry_at__lte=now,
        ).order_by("created_at")[:BATCH]
        sent = failed = 0
        for log in qs:
            text = self._rebuild(log)
            if text is None:
                continue
            if _deliver(log, text):
                sent += 1
            else:
                failed += 1
        self.stdout.write(f"retry: {sent} yuborildi, {failed} qoldi")

    def _rebuild(self, log: NotificationLog):
        """Payload'dan matnni tiklaydi (obyekt oʻzgargan boʻlishi mumkin — payload haqiqat manbai)."""
        return (log.payload or {}).get("text")
