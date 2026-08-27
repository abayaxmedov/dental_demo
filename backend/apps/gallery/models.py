"""Klinika galereyasi."""

from django.db import models

from apps.core.models import TimeStampedModel


class GalleryImage(TimeStampedModel):
    class Category(models.TextChoices):
        CLINIC = "clinic", "Klinika"
        EQUIPMENT = "equipment", "Uskunalar"
        TEAM = "team", "Jamoa"
        WORK = "work", "Ishlarimiz"

    image = models.ImageField("rasm", upload_to="gallery/")
    alt = models.CharField("alt matn", max_length=200, blank=True)
    caption = models.CharField("izoh", max_length=250, blank=True)
    category = models.CharField(
        "kategoriya", max_length=16, choices=Category.choices, default=Category.CLINIC
    )
    instagram_url = models.URLField("Instagram havolasi", blank=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "Galereya rasmi"
        verbose_name_plural = "Galereya"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.alt or f"Rasm #{self.pk}"
