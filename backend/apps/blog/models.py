"""Blog — flat (taksonomiyasiz, ADR §12: kategoriya/teg v1 da yoʻq)."""

import math
import re

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.operations import TrigramExtension  # noqa: F401 (migration'da)
from django.db import models

from apps.core.models import SEOMixin, TimeStampedModel
from apps.core.utils.slugify_uz import slugify_uz

WORDS_PER_MINUTE = 180


class Post(TimeStampedModel, SEOMixin):
    title = models.CharField("sarlavha", max_length=250)
    slug = models.SlugField("slug", max_length=280, unique=True, blank=True)
    excerpt = models.CharField("qisqa matn", max_length=350, blank=True)
    body = models.TextField("matn")
    cover = models.ImageField("muqova", upload_to="blog/", blank=True, null=True)
    author = models.ForeignKey(
        "team.Doctor",
        verbose_name="muallif",
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField("chop etilgan", null=True, blank=True)
    is_published = models.BooleanField("chop etilgan", default=False)
    reading_time = models.PositiveSmallIntegerField("oʻqish vaqti (daq)", default=1)

    class Meta:
        verbose_name = "Maqola"
        verbose_name_plural = "Blog"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "-published_at"]),
            GinIndex(
                name="post_title_excerpt_trgm",
                fields=["title", "excerpt"],
                opclasses=["gin_trgm_ops", "gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uz(self.title)
        words = len(re.findall(r"\w+", self.body or ""))
        self.reading_time = max(1, math.ceil(words / WORDS_PER_MINUTE))
        super().save(*args, **kwargs)
