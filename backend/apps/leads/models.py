"""Murojaatlar: qoʻngʻiroq buyurtmasi, aloqa formasi, narx soʻrovi."""

from django.db import models

from apps.core.models import TimeStampedModel


class Lead(TimeStampedModel):
    class Kind(models.TextChoices):
        CALLBACK = "callback", "Qoʻngʻiroq buyurtmasi"
        CONTACT = "contact", "Aloqa formasi"
        PRICE_REQUEST = "price_request", "Narx soʻrovi"
        DEMO_INQUIRY = "demo_inquiry", "Demo soʻrovi"

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        IN_PROGRESS = "in_progress", "Ishlanmoqda"
        WON = "won", "Yutildi"
        LOST = "lost", "Yoʻqotildi"
        SPAM = "spam", "Spam"

    kind = models.CharField("turi", max_length=20, choices=Kind.choices, default=Kind.CALLBACK)
    name = models.CharField("ism", max_length=150)
    phone = models.CharField("telefon", max_length=20, db_index=True)  # E.164
    email = models.EmailField("email", blank=True)
    message = models.TextField("xabar", blank=True)
    service = models.ForeignKey(
        "services.Service",
        verbose_name="xizmat",
        on_delete=models.SET_NULL,
        related_name="leads",
        null=True,
        blank=True,
    )
    preferred_time = models.CharField("qulay vaqt", max_length=120, blank=True)

    locale = models.CharField("til", max_length=5, default="uz")
    source_page = models.CharField("sahifa", max_length=255, blank=True)
    utm_source = models.CharField("utm_source", max_length=100, blank=True)
    utm_medium = models.CharField("utm_medium", max_length=100, blank=True)
    utm_campaign = models.CharField("utm_campaign", max_length=100, blank=True)

    status = models.CharField(
        "status", max_length=16, choices=Status.choices, default=Status.NEW, db_index=True
    )
    notified = models.BooleanField("xabar yuborilgan", default=False)
    consent_given_at = models.DateTimeField("rozilik vaqti", null=True, blank=True)
    ip_hash = models.CharField("IP hash", max_length=64, blank=True)

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self):
        return f"{self.get_kind_display()} — {self.name} ({self.phone})"
