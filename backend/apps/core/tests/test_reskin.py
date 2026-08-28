"""`manage.py reskin` (ADR-012) testlari."""

import pytest
from django.core.management import CommandError, call_command

from apps.core.models import ClinicSettings


def _write(tmp_path, body):
    p = tmp_path / "prospect.yml"
    p.write_text(body, encoding="utf-8")
    return str(p)


@pytest.mark.django_db
def test_reskin_applies_name_and_colors(tmp_path):
    cfg = _write(
        tmp_path,
        'name: "Smile Line"\ntheme:\n  brand: "#7C3AED"\n  accent: "#F59E0B"\n',
    )
    call_command("reskin", config=cfg)
    s = ClinicSettings.load()
    assert s.name == "Smile Line"
    assert s.brand_color == "#7C3AED"
    assert s.accent_color == "#F59E0B"


@pytest.mark.django_db
def test_reskin_dry_run_writes_nothing(tmp_path):
    cfg = _write(tmp_path, 'name: "Changed"\ntheme:\n  brand: "#123456"\n')
    call_command("reskin", config=cfg, dry_run=True)
    assert ClinicSettings.load().name == "Oq Marvarid Dental"  # default — o'zgarmadi


@pytest.mark.django_db
def test_reskin_partial_update_keeps_other_fields(tmp_path):
    s = ClinicSettings.load()
    s.tagline = "Original tagline"
    s.save()
    cfg = _write(tmp_path, 'theme:\n  brand: "#0A0A0A"\n')  # faqat rang
    call_command("reskin", config=cfg)
    s.refresh_from_db()
    assert s.brand_color == "#0A0A0A"
    assert s.tagline == "Original tagline"  # tegilmadi


# ── Tarjima qilinadigan maydonlar (AUDIT-2026-08-29 / T-FIX-01) ──
# Regressiya: oddiy `setattr` faqat FAOL til ustunini yozardi, shuning uchun rebrand
# qilingan saytda ru/en da OLDINGI klinikaning matni qolib ketardi.


@pytest.mark.django_db
def test_reskin_plain_string_writes_all_three_languages(tmp_path):
    s = ClinicSettings.load()
    for lang in ("uz", "ru", "en"):
        setattr(s, f"name_{lang}", f"Eski klinika {lang}")
        setattr(s, f"address_{lang}", f"Eski manzil {lang}")
    s.save()

    cfg = _write(tmp_path, 'name: "Smile Line"\nlocation:\n  address: "Yangi koʻcha 1"\n')
    call_command("reskin", config=cfg)

    s.refresh_from_db()
    for lang in ("uz", "ru", "en"):
        assert getattr(s, f"name_{lang}") == "Smile Line", f"{lang} tilida eski nom qoldi"
        assert getattr(s, f"address_{lang}") == "Yangi koʻcha 1"


@pytest.mark.django_db
def test_reskin_per_language_map(tmp_path):
    cfg = _write(
        tmp_path,
        'tagline:\n  uz: "Ogʻriqsiz davolash"\n  ru: "Лечение без боли"\n  en: "Painless care"\n',
    )
    call_command("reskin", config=cfg)
    s = ClinicSettings.load()
    assert s.tagline_uz == "Ogʻriqsiz davolash"
    assert s.tagline_ru == "Лечение без боли"
    assert s.tagline_en == "Painless care"


@pytest.mark.django_db
def test_reskin_partial_language_map_warns_and_keeps_others(tmp_path, capsys):
    s = ClinicSettings.load()
    s.tagline_en = "Old english tagline"
    s.save()

    cfg = _write(tmp_path, 'tagline:\n  uz: "Faqat uz"\n  ru: "Только ru"\n')
    call_command("reskin", config=cfg)

    s.refresh_from_db()
    assert s.tagline_uz == "Faqat uz"
    assert s.tagline_ru == "Только ru"
    assert s.tagline_en == "Old english tagline"  # tegilmadi
    assert "en tili berilmadi" in capsys.readouterr().out


@pytest.mark.django_db
def test_reskin_rejects_unknown_language_key(tmp_path):
    cfg = _write(tmp_path, 'tagline:\n  uz: "a"\n  de: "b"\n')
    with pytest.raises(CommandError, match="nomaʼlum til kaliti"):
        call_command("reskin", config=cfg)


@pytest.mark.django_db
def test_reskin_rejects_non_text_translated_value(tmp_path):
    cfg = _write(tmp_path, "name: 12345\n")
    with pytest.raises(CommandError, match="matn yoki"):
        call_command("reskin", config=cfg)


@pytest.mark.django_db
def test_reskin_rejects_bad_hex(tmp_path):
    cfg = _write(tmp_path, 'theme:\n  brand: "purple"\n')
    with pytest.raises(CommandError, match="hex"):
        call_command("reskin", config=cfg)


@pytest.mark.django_db
def test_reskin_rejects_unknown_font_pair(tmp_path):
    cfg = _write(tmp_path, 'theme:\n  font_pair: "comic-sans"\n')
    with pytest.raises(CommandError, match="font_pair"):
        call_command("reskin", config=cfg)


@pytest.mark.django_db
def test_reskin_missing_asset_file_errors(tmp_path):
    cfg = _write(tmp_path, 'assets:\n  logo: "does-not-exist.png"\n')
    with pytest.raises(CommandError, match="topilmadi"):
        call_command("reskin", config=cfg)


def test_reskin_missing_config_errors():
    with pytest.raises(CommandError, match="topilmadi"):
        call_command("reskin", config="/nonexistent/prospect.yml")
