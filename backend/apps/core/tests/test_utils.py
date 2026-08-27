"""slugify_uz va normalize_uz_phone testlari (T-P1-12, T-P1-13)."""

import pytest

from apps.core.utils.phone import InvalidPhoneError, normalize_uz_phone
from apps.core.utils.slugify_uz import slugify_uz


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Oʻzbek maxsus harflari — unidecode buzadigan holatlar
        ("Ogʻiz boʻshligʻi gigiyenasi", "ogiz-boshligi-gigiyenasi"),
        ("Oʻzbekiston", "ozbekiston"),
        ("Aqli tish olib tashlash", "aqli-tish-olib-tashlash"),
        ("Implantatsiya", "implantatsiya"),
        ("Estetik plombalash", "estetik-plombalash"),
        ("Bolalar stomatologiyasi", "bolalar-stomatologiyasi"),
        ("Ildiz kanali davolash", "ildiz-kanali-davolash"),
        ("Breketlar oʻrnatish", "breketlar-ornatish"),
        # Apostrof variantlari
        ("O'zbek tili", "ozbek-tili"),
        ("G‘isht", "gisht"),
        # Rus (kirill) sarlavhalari
        ("Имплантация зубов", "implantatsiya-zubov"),
        ("Профессиональная гигиена", "professionalnaya-gigiena"),
        ("Отбеливание зубов", "otbelivanie-zubov"),
        # Shifokor ismlari
        ("Dilshod Raximov", "dilshod-raximov"),
        ("Nigora Yusupova", "nigora-yusupova"),
        ("Shohruh Gʻaniyev", "shohruh-ganiyev"),
        # Chegara holatlari
        ("  Koʻp   boʻshliq  ", "kop-boshliq"),
        ("Narx: 1 000 000 soʻm!", "narx-1-000-000-som"),
        ("---", ""),
        ("", ""),
    ],
)
def test_slugify_uz(raw, expected):
    assert slugify_uz(raw) == expected


def test_slugify_respects_max_length():
    assert len(slugify_uz("a" * 300, max_length=50)) <= 50


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+998901234567", "+998901234567"),
        ("998901234567", "+998901234567"),
        ("901234567", "+998901234567"),
        ("90 123 45 67", "+998901234567"),
        ("+998 90 123-45-67", "+998901234567"),
        ("8901234567", "+998901234567"),
        ("(90) 123 45 67", "+998901234567"),
        ("+998 (71) 200-40-40", "+998712004040"),
    ],
)
def test_normalize_uz_phone_valid(raw, expected):
    assert normalize_uz_phone(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "abc", "123", "12345", "+1 555 123 4567", "9012345678901", "+99890123456"],
)
def test_normalize_uz_phone_invalid(raw):
    with pytest.raises(InvalidPhoneError):
        normalize_uz_phone(raw)
