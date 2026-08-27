"""
Tarjima regressiya testlari.

Tarix: `PriceItem.qualifier` da `default="dan boshlab"` boʻlgani uchun modeltranslation
uni avto-toʻldirilgan deb hisoblab, oʻzbek tilida rus qiymatini qaytargan edi.
Bu testlar shu xatoning qaytishini bloklaydi.
"""

import pytest
from django.utils import translation

from apps.core.management.commands.seed_demo import set_i18n
from apps.services.models import PriceItem, Service, ServiceCategory


@pytest.fixture
def category(db):
    cat = ServiceCategory(title="Terapiya")
    set_i18n(cat, "title", {"uz": "Terapiya", "ru": "Терапия", "en": "Therapy"})
    cat.save()
    return cat


def test_price_qualifier_resolves_per_language(category):
    """Har bir til oʻz qiymatini qaytaradi — boshqa tilnikini emas."""
    item = PriceItem(category=category, price_from=1000)
    set_i18n(item, "title", {"uz": "Konsultatsiya", "ru": "Консультация", "en": "Consultation"})
    set_i18n(item, "qualifier", {"uz": "dan boshlab", "ru": "от", "en": "from"})
    item.save()
    item.refresh_from_db()

    expected = {"uz": "dan boshlab", "ru": "от", "en": "from"}
    for lang, want in expected.items():
        with translation.override(lang):
            assert item.qualifier == want, f"{lang}: {item.qualifier!r} != {want!r}"


def test_translated_field_has_no_hardcoded_default():
    """
    Tarjima qilinadigan maydonda hardcode default boʻlmasligi kerak —
    modeltranslation uni avto-toʻldirilgan deb hisoblab fallback qiladi.
    """
    field = PriceItem._meta.get_field("qualifier")
    assert field.default is not None or True  # NOT_PROVIDED tekshiruvi quyida
    from django.db.models.fields import NOT_PROVIDED

    assert field.default is NOT_PROVIDED, "qualifier'ga default qaytarib qoʻyilgan"


def test_service_slug_is_translated_per_language(category):
    """Slug har til uchun alohida — /ru/ sahifada ruscha URL boʻlishi uchun (ADR-003)."""
    svc = Service(category=category, duration_minutes=30)
    set_i18n(svc, "title", {"uz": "Implantatsiya", "ru": "Имплантация", "en": "Dental implants"})
    for lang, slug in (("uz", "implantatsiya"), ("ru", "implantatsiya"), ("en", "dental-implants")):
        setattr(svc, f"slug_{lang}", slug)
    svc.slug = "implantatsiya"
    svc.save()

    with translation.override("en"):
        assert svc.slug == "dental-implants"
    with translation.override("uz"):
        assert svc.slug == "implantatsiya"


def test_set_i18n_writes_all_three_languages(category):
    item = PriceItem(category=category, price_from=500)
    set_i18n(item, "title", {"uz": "Koʻrik", "ru": "Осмотр", "en": "Check-up"})
    item.save()

    assert item.title_uz == "Koʻrik"
    assert item.title_ru == "Осмотр"
    assert item.title_en == "Check-up"
    assert item.title == "Koʻrik", "bazaviy ustun uz qiymatini saqlashi kerak"
