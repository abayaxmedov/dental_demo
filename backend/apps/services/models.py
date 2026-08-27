"""Xizmatlar katalogi: kategoriya, xizmat, narx qatori, FAQ."""

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import SEOMixin, TimeStampedModel
from apps.core.utils.slugify_uz import slugify_uz


class ServiceCategory(TimeStampedModel):
    title = models.CharField("nomi", max_length=150)
    slug = models.SlugField("slug", max_length=180, unique=True, blank=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    icon = models.CharField("icon", max_length=48, blank=True)

    class Meta:
        verbose_name = "Xizmat kategoriyasi"
        verbose_name_plural = "Xizmat kategoriyalari"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uz(self.title)
        super().save(*args, **kwargs)


class Service(TimeStampedModel, SEOMixin):
    category = models.ForeignKey(
        ServiceCategory,
        verbose_name="kategoriya",
        on_delete=models.PROTECT,
        related_name="services",
    )
    title = models.CharField("nomi", max_length=180)
    slug = models.SlugField("slug", max_length=200, unique=True, blank=True)
    excerpt = models.CharField("qisqa tavsif", max_length=300, blank=True)
    body = models.TextField("toʻliq tavsif", blank=True)
    icon = models.CharField("icon", max_length=48, blank=True)
    cover = models.ImageField("rasm", upload_to="services/", blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField(
        "davomiyligi (daq)", default=30, validators=[MinValueValidator(5)]
    )
    is_featured = models.BooleanField("bosh sahifada", default=False)
    is_active = models.BooleanField("faol", default=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    doctors = models.ManyToManyField(
        "team.Doctor",
        verbose_name="shifokorlar",
        related_name="services",
        blank=True,
    )

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ["order", "title"]
        indexes = [models.Index(fields=["is_featured", "is_active"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gte=5),
                name="service_duration_min",
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uz(self.title)
        super().save(*args, **kwargs)


class PriceItem(TimeStampedModel):
    """Narx qatori. UZS, 'dan boshlab' qualifier bilan."""

    service = models.ForeignKey(
        Service,
        verbose_name="xizmat",
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        ServiceCategory,
        verbose_name="kategoriya",
        on_delete=models.PROTECT,
        related_name="prices",
    )
    title = models.CharField("nomi", max_length=200)
    price_from = models.DecimalField("narx (dan)", max_digits=12, decimal_places=2)
    price_to = models.DecimalField(
        "narx (gacha)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField("valyuta", max_length=8, default="UZS")
    unit = models.CharField("birlik", max_length=60, blank=True)  # "1 tish", "1 seans"
    # Tarjima qilinadigan maydon — hardcode oʻzbekcha default BERILMAYDI,
    # aks holda modeltranslation uni avto-toʻldirilgan deb hisoblab fallback qiladi.
    qualifier = models.CharField("izoh", max_length=60, blank=True)
    is_promo = models.BooleanField("aksiya", default=False)
    promo_note = models.CharField("aksiya izohi", max_length=120, blank=True)
    order = models.PositiveSmallIntegerField("tartib", default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "Narx"
        verbose_name_plural = "Narxlar"
        ordering = ["category__order", "order", "title"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price_to__isnull=True)
                | models.Q(price_to__gte=models.F("price_from")),
                name="price_to_gte_price_from",
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.price_from:,.0f} {self.currency}"


class Faq(TimeStampedModel):
    question = models.CharField("savol", max_length=300)
    answer = models.TextField("javob")
    service = models.ForeignKey(
        Service,
        verbose_name="xizmat",
        on_delete=models.CASCADE,
        related_name="faqs",
        null=True,
        blank=True,
    )
    order = models.PositiveSmallIntegerField("tartib", default=0)
    is_active = models.BooleanField("faol", default=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["order"]

    def __str__(self):
        return self.question
