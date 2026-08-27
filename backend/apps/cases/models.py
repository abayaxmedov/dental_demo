"""Before/After ishlar — Prodent'ni ortda qoldiruvchi asosiy farq."""

from django.db import models

from apps.core.models import SEOMixin, TimeStampedModel
from apps.core.utils.slugify_uz import slugify_uz


class CasePair(TimeStampedModel, SEOMixin):
    title = models.CharField("nomi", max_length=200)
    slug = models.SlugField("slug", max_length=220, unique=True, blank=True)
    service = models.ForeignKey(
        "services.Service",
        verbose_name="xizmat",
        on_delete=models.SET_NULL,
        related_name="cases",
        null=True,
        blank=True,
    )
    doctor = models.ForeignKey(
        "team.Doctor",
        verbose_name="shifokor",
        on_delete=models.SET_NULL,
        related_name="cases",
        null=True,
        blank=True,
    )
    image_before = models.ImageField("oldin", upload_to="cases/")
    image_after = models.ImageField("keyin", upload_to="cases/")
    caption = models.CharField("izoh", max_length=300, blank=True)
    treatment_summary = models.TextField("davolash tavsifi", blank=True)
    duration_note = models.CharField("davomiyligi", max_length=120, blank=True)

    # Bemor roziligi boʻlmasa publish qilinmaydi (ADR-014)
    consent_on_file = models.BooleanField("bemor roziligi bor", default=False)
    is_published = models.BooleanField("chop etilgan", default=False)
    is_featured = models.BooleanField("bosh sahifada", default=False)
    order = models.PositiveSmallIntegerField("tartib", default=0)

    class Meta:
        verbose_name = "Ish (before/after)"
        verbose_name_plural = "Ishlarimiz"
        ordering = ["order", "-created_at"]
        constraints = [
            # Roziliksiz chop etib boʻlmaydi — DB darajasida.
            models.CheckConstraint(
                condition=models.Q(is_published=False) | models.Q(consent_on_file=True),
                name="case_published_requires_consent",
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uz(self.title)
        super().save(*args, **kwargs)
