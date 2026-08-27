"""Demo tayyorligini tekshirish: klinika guruhiga sinov xabari yuboradi."""

from django.core.management.base import BaseCommand

from apps.notifications.services.telegram import send_message


class Command(BaseCommand):
    help = "Telegram sozlamalarini tekshiradi (demo'dan oldin)."

    def handle(self, *args, **opts):
        res = send_message("✅ <b>Oq Marvarid Dental</b>\nTelegram ulanishi ishlayapti.")
        if res.ok:
            self.stdout.write(self.style.SUCCESS("✓ Telegram xabari yuborildi"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Yuborilmadi: {res.error}"))
