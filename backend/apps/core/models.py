"""
Core modellar: abstract base'lar + sayt sozlamalari (ClinicSettings singleton, ADR-004),
ish vaqti, statistik counter, redirect va SEO bloklari.
Tarjima qilinadigan maydonlar translation.py da roʻyxatdan oʻtadi (modeltranslation).
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("yaratilgan vaqti", auto_now_add=True)
    updated_at = models.DateTimeField("yangilangan vaqti", auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = "created_at"


class SEOMixin(models.Model):
    """Ommaviy sahifalar uchun SEO (tarjima qilinadi). Frontend metadata API ishlatadi (ADR-016)."""

    meta_title = models.CharField("meta title", max_length=180, blank=True)
    meta_description = models.CharField("meta description", max_length=320, blank=True)
    og_image = models.ImageField("OG rasm", upload_to="og/", blank=True, null=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """pk=1 majburlangan singleton. load() bilan olinadi (ADR-004)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # singleton oʻchirilmaydi
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FontPair(models.TextChoices):
    INTER_MANROPE = "inter_manrope", "Inter + Manrope"
    PLAYFAIR_INTER = "playfair_inter", "Playfair + Inter"


# Rang maydonlari `<html style="--brand:…">` ga XOM injeksiya qilinadi (layout.tsx, ADR-004).
# Validator boʻlmasa admin `teal` yoki `0E7C86` (# siz) yozsa butun `bg-brand` CTA'lari
# koʻrinmas boʻlib qolardi, xatolik xabarisiz (AUDIT-2026-08-29 / T-FIX-05).
HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$",
    message="Hex rang boʻlishi kerak: #RGB, #RGBA, #RRGGBB yoki #RRGGBBAA (masalan #0E7C86).",
)


class ClinicSettings(SingletonModel):
    """Sayt sozlamalari — brending data (kod emas). reskin (ADR-012) shu yerni yozadi."""

    # Identifikatsiya (tarjima: name/tagline/about_short/address)
    name = models.CharField("klinika nomi", max_length=120, default="Oq Marvarid Dental")
    tagline = models.CharField("shior", max_length=200, blank=True)
    about_short = models.TextField("qisqa taʼrif", blank=True)

    logo = models.ImageField("logo", upload_to="brand/", blank=True, null=True)
    logo_dark = models.ImageField("logo (dark)", upload_to="brand/", blank=True, null=True)
    favicon = models.ImageField("favicon", upload_to="brand/", blank=True, null=True)
    # Hero — LCP elementi va klinikaga xos, shuning uchun sozlamada (public/ ga qotirilmaydi).
    hero_image = models.ImageField("hero rasmi", upload_to="brand/", blank=True, null=True)
    og_image = models.ImageField("OG rasm (default)", upload_to="og/", blank=True, null=True)

    # Ranglar (ADR-004: CSS custom property sifatida frontend'ga uzatiladi)
    brand_color = models.CharField("brand rang", max_length=9, default="#0E7C86", validators=[HEX_COLOR_VALIDATOR])
    accent_color = models.CharField("accent rang", max_length=9, default="#F2A65A", validators=[HEX_COLOR_VALIDATOR])
    ink_color = models.CharField("matn rangi", max_length=9, default="#0F172A", validators=[HEX_COLOR_VALIDATOR])
    surface_color = models.CharField("fon rangi", max_length=9, default="#FFFFFF", validators=[HEX_COLOR_VALIDATOR])
    font_pair = models.CharField(
        "shrift juftligi",
        max_length=32,
        choices=FontPair.choices,
        default=FontPair.INTER_MANROPE,
    )

    # Aloqa
    phone_primary = models.CharField("asosiy telefon", max_length=32, default="+998712004040")
    phone_secondary = models.CharField("qoʻshimcha telefon", max_length=32, blank=True)
    telegram_username = models.CharField("Telegram username", max_length=64, blank=True)
    telegram_channel_url = models.URLField("Telegram kanal", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
    email = models.EmailField("email", blank=True)

    # Manzil / xarita
    address = models.CharField("manzil", max_length=255, blank=True)
    map_lat = models.DecimalField("kenglik", max_digits=9, decimal_places=6, null=True, blank=True)
    map_lng = models.DecimalField("uzunlik", max_digits=9, decimal_places=6, null=True, blank=True)
    map_zoom = models.PositiveSmallIntegerField("zoom", default=16)
    yandex_maps_url = models.URLField("Yandex Maps", blank=True)
    two_gis_url = models.URLField("2GIS", blank=True)

    # Huquqiy / analytics / bayroqlar
    license_text = models.CharField("litsenziya matni", max_length=255, blank=True)
    legal_entity_name = models.CharField("yuridik shaxs", max_length=200, blank=True)
    metrika_id = models.CharField("Yandex Metrika ID", max_length=32, blank=True)
    ga4_id = models.CharField("GA4 ID", max_length=32, blank=True)
    yandex_verification = models.CharField("Yandex Webmaster", max_length=128, blank=True)
    google_verification = models.CharField("Google verification", max_length=128, blank=True)
    prices_visible = models.BooleanField("narxlar koʻrinsin", default=True)
    booking_enabled = models.BooleanField("onlayn qabul yoqilgan", default=True)

    default_meta_title = models.CharField("default meta title", max_length=180, blank=True)
    default_meta_description = models.CharField(
        "default meta description", max_length=320, blank=True
    )

    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return self.name


class WorkingHours(models.Model):
    """Hafta kuni boʻyicha ish vaqti. Topbar, footer, JSON-LD va slot generatsiyasini boshqaradi."""

    class Weekday(models.IntegerChoices):
        MON = 0, "Dushanba"
        TUE = 1, "Seshanba"
        WED = 2, "Chorshanba"
        THU = 3, "Payshanba"
        FRI = 4, "Juma"
        SAT = 5, "Shanba"
        SUN = 6, "Yakshanba"

    weekday = models.PositiveSmallIntegerField("hafta kuni", choices=Weekday.choices, unique=True)
    opens = models.TimeField("ochilish", null=True, blank=True)
    closes = models.TimeField("yopilish", null=True, blank=True)
    is_closed = models.BooleanField("dam olish kuni", default=False)
    note = models.CharField("izoh", max_length=120, blank=True)

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqti"
        ordering = ["weekday"]

    def __str__(self):
        return f"{self.get_weekday_display()}: {'dam' if self.is_closed else f'{self.opens}–{self.closes}'}"


class StatCounter(models.Model):
    """Bosh sahifadagi animatsion counterlar (Prodent'ning hardcode raqamlari oʻrnida)."""

    label = models.CharField("nom", max_length=120)
    value = models.PositiveIntegerField("qiymat")
    suffix = models.CharField("qoʻshimcha", max_length=8, blank=True)  # + / K / %
    icon = models.CharField("icon", max_length=48, blank=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "Statistik counter"
        verbose_name_plural = "Statistik counterlar"
        ordering = ["order"]

    def __str__(self):
        return f"{self.value}{self.suffix} — {self.label}"


class Redirect(models.Model):
    class Status(models.IntegerChoices):
        MOVED = 301, "301 Moved Permanently"
        FOUND = 302, "302 Found"
        GONE = 410, "410 Gone"

    old_path = models.CharField("eski yoʻl", max_length=255, db_index=True)
    new_path = models.CharField("yangi yoʻl", max_length=255, blank=True)
    status = models.PositiveSmallIntegerField(
        "status", choices=Status.choices, default=Status.MOVED
    )
    locale = models.CharField("til", max_length=5, blank=True)
    hits = models.PositiveIntegerField("bosishlar", default=0)
    last_hit_at = models.DateTimeField("oxirgi bosish", null=True, blank=True)

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirectlar"

    def __str__(self):
        return f"{self.old_path} → {self.new_path} ({self.status})"

    def clean(self):
        if self.status != self.Status.GONE and not self.new_path:
            raise ValidationError({"new_path": "301/302 uchun yangi yoʻl majburiy."})
