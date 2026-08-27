"""
Qabul eslatmalari (T-24s va T-2s). Soatlik cron.
Critique #18: oʻtgan qabullar uchun "2 soatdan keyin" yubormaslik — ikkala oyna
PASTDAN ham chegaralanadi; oʻtgan bayroqsizlar YUBORILMASDAN belgilanadi.

Eslatma (ADR-010): xabarlar hozircha klinika GURUHIGA boradi (bemorda chat_id yoʻq).
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.appointments.models import ACTIVE_STATUSES, Appointment
from apps.notifications.services import messages as tpl
from apps.notifications.services.notify import _deliver, _log_for


class Command(BaseCommand):
    help = "T-24s va T-2s qabul eslatmalarini yuboradi."

    def handle(self, *args, **opts):
        now = timezone.now()
        self._flag_past(now)
        c24 = self._window(now, hours=24, field="reminder_24h_sent_at")
        c2 = self._window(now, hours=2, field="reminder_2h_sent_at")
        self.stdout.write(f"reminders: 24h={c24}, 2h={c2}")

    def _flag_past(self, now):
        """Oʻtgan, bayroqsiz faol qabullarni YUBORMASDAN belgilaydi (critique #18)."""
        Appointment.objects.filter(
            status__in=ACTIVE_STATUSES,
            starts_at__lt=now,
        ).filter(reminder_24h_sent_at__isnull=True).update(reminder_24h_sent_at=now)
        Appointment.objects.filter(
            status__in=ACTIVE_STATUSES,
            starts_at__lt=now,
        ).filter(reminder_2h_sent_at__isnull=True).update(reminder_2h_sent_at=now)

    def _window(self, now, *, hours, field):
        lo = now  # PASTDAN chegara — o'tganlar tushmaydi
        hi = now + timedelta(hours=hours)
        qs = Appointment.objects.filter(
            status__in=ACTIVE_STATUSES,
            starts_at__gte=lo,
            starts_at__lte=hi,
            **{f"{field}__isnull": True},
        )
        count = 0
        for appt in qs:
            log = _log_for(appt, f"reminder_{hours}h", appt.code)
            text = tpl.new_appointment(appt)  # oddiy eslatma — batafsil ma'lumot
            _deliver(log, "⏰ Eslatma:\n" + text)
            setattr(appt, field, now)
            appt.save(update_fields=[field])
            count += 1
        return count
