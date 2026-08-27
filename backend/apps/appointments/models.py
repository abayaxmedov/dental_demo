"""
Qabullar (ADR-007): booking toʻgʻriligi Python'da emas, Postgres'da majburlanadi.
`ExclusionConstraint` bir shifokorda vaqt oraligʻi ustma-ust tushishini imkonsiz qiladi.
"""

import secrets
import uuid

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.db import models
from django.utils import timezone

# Faol statuslar — faqat shular ustma-ust tusha olmaydi.
ACTIVE_STATUSES = ("pending", "confirmed")

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # chalkashadigan 0/O/1/I yoʻq


def generate_code() -> str:
    return "A-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(5))


class TsTzRange(models.Func):
    """
    (starts_at, ends_at, '[)') → tstzrange, ExclusionConstraint uchun.
    Chegara turi RangeBoundary() bilan uchinchi argument sifatida beriladi —
    bu yerda qoʻshimcha argument qoʻshilmaydi.
    """

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    CONFIRMED = "confirmed", "Tasdiqlangan"
    CANCELLED_BY_PATIENT = "cancelled_by_patient", "Bemor bekor qildi"
    CANCELLED_BY_CLINIC = "cancelled_by_clinic", "Klinika bekor qildi"
    COMPLETED = "completed", "Yakunlandi"
    NO_SHOW = "no_show", "Kelmadi"


# Ruxsat etilgan status oʻtishlari. Terminal statuslardan chiqish yoʻq.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    AppointmentStatus.PENDING: {
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED_BY_PATIENT,
        AppointmentStatus.CANCELLED_BY_CLINIC,
    },
    AppointmentStatus.CONFIRMED: {
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW,
        AppointmentStatus.CANCELLED_BY_PATIENT,
        AppointmentStatus.CANCELLED_BY_CLINIC,
    },
    AppointmentStatus.CANCELLED_BY_PATIENT: set(),
    AppointmentStatus.CANCELLED_BY_CLINIC: set(),
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.NO_SHOW: set(),
}


class InvalidTransition(ValueError):
    """Ruxsat etilmagan status oʻtishi."""


class Appointment(models.Model):
    class Source(models.TextChoices):
        WEB = "web", "Sayt"
        PHONE = "phone", "Telefon"
        TELEGRAM = "telegram", "Telegram"
        ADMIN = "admin", "Admin"

    code = models.CharField(
        "kod", max_length=12, unique=True, default=generate_code, editable=False
    )
    cancel_token = models.UUIDField(
        "bekor qilish tokeni",
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    doctor = models.ForeignKey(
        "team.Doctor",
        verbose_name="shifokor",
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        "services.Service",
        verbose_name="xizmat",
        on_delete=models.SET_NULL,
        related_name="appointments",
        null=True,
        blank=True,
    )

    patient_name = models.CharField("bemor ismi", max_length=150)
    phone = models.CharField("telefon", max_length=20, db_index=True)  # E.164
    email = models.EmailField("email", blank=True)
    comment = models.TextField("izoh", blank=True)

    starts_at = models.DateTimeField("boshlanish")
    ends_at = models.DateTimeField("tugash")

    status = models.CharField(
        "status",
        max_length=32,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        db_index=True,
    )
    source = models.CharField("manba", max_length=16, choices=Source.choices, default=Source.WEB)
    locale = models.CharField("til", max_length=5, default="uz")

    # Rozilik / audit (ADR-014)
    consent_given_at = models.DateTimeField("rozilik vaqti", null=True, blank=True)
    consent_text_version = models.CharField("rozilik matni versiyasi", max_length=32, blank=True)
    ip_hash = models.CharField("IP hash", max_length=64, blank=True)
    user_agent = models.CharField("User-Agent", max_length=300, blank=True)

    reminder_24h_sent_at = models.DateTimeField("24s eslatma", null=True, blank=True)
    reminder_2h_sent_at = models.DateTimeField("2s eslatma", null=True, blank=True)

    # Idempotency (ADR: double-submit himoyasi) va reschedule cheklovi
    idempotency_key = models.UUIDField(
        "idempotency key", null=True, blank=True, unique=True, editable=False
    )
    reschedule_count = models.PositiveSmallIntegerField("koʻchirishlar soni", default=0)

    created_at = models.DateTimeField("yaratilgan", auto_now_add=True)
    updated_at = models.DateTimeField("yangilangan", auto_now=True)

    class Meta:
        verbose_name = "Qabul"
        verbose_name_plural = "Qabullar"
        ordering = ["-starts_at"]
        indexes = [
            models.Index(fields=["starts_at", "status"]),
            models.Index(fields=["doctor", "starts_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="appointment_end_after_start",
            ),
            # Web orqali yaratilgan qabul doctor VA service'ga ega boʻlishi shart
            # (doctor=NULL "istalgan boʻsh" faqat admin/telefon uchun — booking.py hal qiladi).
            models.CheckConstraint(
                condition=~models.Q(source="web")
                | (models.Q(doctor__isnull=False) & models.Q(service__isnull=False)),
                name="appointment_web_requires_doctor_and_service",
            ),
            # ADR-007: bitta shifokorda faol qabullar vaqt boʻyicha kesisha olmaydi.
            ExclusionConstraint(
                name="appointment_no_overlap_per_doctor",
                expressions=[
                    ("doctor", RangeOperators.EQUAL),
                    (TsTzRange("starts_at", "ends_at", RangeBoundary()), RangeOperators.OVERLAPS),
                ],
                condition=models.Q(status__in=ACTIVE_STATUSES, doctor__isnull=False),
            ),
        ]

    def __str__(self):
        return f"{self.code} — {self.patient_name} ({self.starts_at:%Y-%m-%d %H:%M})"

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    def transition_to(self, new_status: str, *, save: bool = True) -> None:
        """
        Statusni ruxsat etilgan oʻtish boʻyicha oʻzgartiradi.
        View'lar status'ni toʻgʻridan-toʻgʻri yozmaydi — faqat shu metod orqali.
        """
        allowed = ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidTransition(
                f"'{self.status}' → '{new_status}' oʻtishi mumkin emas. "
                f"Ruxsat etilgan: {sorted(allowed) or 'yoʻq (terminal status)'}"
            )
        self.status = new_status
        if save:
            self.save(update_fields=["status", "updated_at"])

    def cancel_by_patient(self):
        self.transition_to(AppointmentStatus.CANCELLED_BY_PATIENT)

    def confirm(self):
        self.transition_to(AppointmentStatus.CONFIRMED)

    @property
    def is_past(self) -> bool:
        return self.ends_at < timezone.now()
