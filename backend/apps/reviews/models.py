"""Bemor sharhlari (manba havolasi bilan — Prodent'dagi lorem iqtiboslar oʻrnida)."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Review(TimeStampedModel):
    class Source(models.TextChoices):
        MANUAL = "manual", "Qoʻlda"
        GOOGLE = "google", "Google"
        TWO_GIS = "2gis", "2GIS"
        YANDEX = "yandex", "Yandex"
        INSTAGRAM = "instagram", "Instagram"

    author_name = models.CharField("muallif", max_length=150)
    author_photo = models.ImageField("rasm", upload_to="reviews/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        "reyting",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
    )
    text = models.TextField("sharh")
    source = models.CharField("manba", max_length=16, choices=Source.choices, default=Source.MANUAL)
    source_url = models.URLField("manba havolasi", blank=True)
    reviewed_at = models.DateField("sana", null=True, blank=True)
    is_featured = models.BooleanField("bosh sahifada", default=False)
    is_active = models.BooleanField("faol", default=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["order", "-reviewed_at"]

    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"
