"""Statik huquqiy sahifalar: maxfiylik siyosati, oferta, shartlar."""

from django.db import models

from apps.core.models import SEOMixin, TimeStampedModel


class StaticPage(TimeStampedModel, SEOMixin):
    class Key(models.TextChoices):
        PRIVACY = "privacy", "Maxfiylik siyosati"
        OFFER = "offer", "Ommaviy oferta"
        TERMS = "terms", "Foydalanish shartlari"

    key = models.CharField("kalit", max_length=16, choices=Key.choices, unique=True)
    title = models.CharField("sarlavha", max_length=200)
    body = models.TextField("matn")
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "Statik sahifa"
        verbose_name_plural = "Statik sahifalar"

    def __str__(self):
        return self.title
