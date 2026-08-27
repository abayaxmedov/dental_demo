"""Shifokorlar, ularning ish jadvali va dam olish vaqtlari."""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import SEOMixin, TimeStampedModel
from apps.core.utils.slugify_uz import slugify_uz


class Doctor(TimeStampedModel, SEOMixin):
    full_name = models.CharField("F.I.O.", max_length=150)
    slug = models.SlugField("slug", max_length=180, unique=True, blank=True)
    specialization = models.CharField("mutaxassislik", max_length=150)
    bio = models.TextField("tarjimai hol", blank=True)
    photo = models.ImageField("rasm", upload_to="doctors/", blank=True, null=True)
    photo_alt = models.CharField("rasm alt", max_length=200, blank=True)
    experience_years = models.PositiveSmallIntegerField("tajriba (yil)", default=0)
    education = models.TextField("taʼlim", blank=True)
    certificates = models.TextField("sertifikatlar", blank=True)
    languages_spoken = models.CharField("tillar", max_length=64, blank=True)  # "uz,ru,en"
    is_bookable = models.BooleanField("qabulga yozish mumkin", default=True)
    is_active = models.BooleanField("faol", default=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    telegram_username = models.CharField("Telegram", max_length=64, blank=True)

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
        ordering = ["order", "full_name"]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uz(self.full_name)
        super().save(*args, **kwargs)


class DoctorSchedule(models.Model):
    """Shifokorning hafta kuni boʻyicha ish jadvali. Slot engine shundan hisoblaydi."""

    doctor = models.ForeignKey(
        Doctor,
        verbose_name="shifokor",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    weekday = models.PositiveSmallIntegerField("hafta kuni")  # 0=Dushanba
    start_time = models.TimeField("boshlanish")
    end_time = models.TimeField("tugash")
    slot_minutes = models.PositiveSmallIntegerField(
        "slot (daq)", default=30, validators=[MinValueValidator(5)]
    )
    break_start = models.TimeField("tanaffus boshi", null=True, blank=True)
    break_end = models.TimeField("tanaffus oxiri", null=True, blank=True)
    valid_from = models.DateField("amal qiladi (dan)", null=True, blank=True)
    valid_to = models.DateField("amal qiladi (gacha)", null=True, blank=True)

    class Meta:
        verbose_name = "Shifokor jadvali"
        verbose_name_plural = "Shifokor jadvallari"
        ordering = ["doctor", "weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="schedule_end_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(slot_minutes__gte=5),
                name="schedule_slot_minutes_min",
            ),
            models.CheckConstraint(
                condition=models.Q(weekday__lt=7),
                name="schedule_weekday_valid",
            ),
        ]

    def __str__(self):
        return f"{self.doctor} — {self.weekday} {self.start_time}–{self.end_time}"

    def clean(self):
        if bool(self.break_start) != bool(self.break_end):
            raise ValidationError("Tanaffus boshi va oxiri birga koʻrsatilishi kerak.")
        if self.break_start and self.break_end and self.break_end <= self.break_start:
            raise ValidationError({"break_end": "Tanaffus oxiri boshidan keyin boʻlishi kerak."})
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError({"valid_to": "Amal qilish oxiri boshidan keyin boʻlishi kerak."})


class TimeOff(models.Model):
    """Dam olish / taʼtil. doctor=None boʻlsa — butun klinika bayrami."""

    doctor = models.ForeignKey(
        Doctor,
        verbose_name="shifokor",
        on_delete=models.CASCADE,
        related_name="time_off",
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField("boshlanish")
    ends_at = models.DateTimeField("tugash")
    reason = models.CharField("sabab", max_length=200, blank=True)

    class Meta:
        verbose_name = "Dam olish"
        verbose_name_plural = "Dam olish vaqtlari"
        ordering = ["-starts_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="timeoff_end_after_start",
            ),
        ]

    def __str__(self):
        who = self.doctor or "Butun klinika"
        return f"{who}: {self.starts_at:%Y-%m-%d} → {self.ends_at:%Y-%m-%d}"
