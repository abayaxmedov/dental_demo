"""
Xabarnoma jurnali (ADR-006): Celery yoʻq — sinxron yuborish + NotificationLog + cron retry.
Admin'da "Qayta yuborish" action'i shu jadval ustida ishlaydi.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class NotificationLog(models.Model):
    class Channel(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    class Status(models.TextChoices):
        PENDING = "pending", "Navbatda"
        SENT = "sent", "Yuborildi"
        FAILED = "failed", "Xato"
        ABANDONED = "abandoned", "Tashlab yuborildi"

    channel = models.CharField(
        "kanal", max_length=16, choices=Channel.choices, default=Channel.TELEGRAM
    )
    template_key = models.CharField("shablon", max_length=64)
    target = models.CharField("qabul qiluvchi", max_length=128, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    status = models.CharField(
        "status", max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    attempts = models.PositiveSmallIntegerField("urinishlar", default=0)
    last_error = models.TextField("oxirgi xato", blank=True)
    payload = models.JSONField("payload", default=dict, blank=True)
    sent_at = models.DateTimeField("yuborilgan", null=True, blank=True)
    next_retry_at = models.DateTimeField("keyingi urinish", null=True, blank=True)
    created_at = models.DateTimeField("yaratilgan", auto_now_add=True)

    class Meta:
        verbose_name = "Xabarnoma"
        verbose_name_plural = "Xabarnomalar"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "next_retry_at"])]

    def __str__(self):
        return f"{self.get_channel_display()} · {self.template_key} · {self.get_status_display()}"
