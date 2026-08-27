"""Read API testlari (ADR E-qism) — uch tilli hal qilish va content filtrlari."""

import pytest
from rest_framework.test import APIClient

from apps.cases.models import CasePair
from apps.core.management.commands.seed_demo import set_i18n
from apps.core.models import ClinicSettings, StatCounter, WorkingHours
from apps.services.models import Service, ServiceCategory
from apps.team.models import Doctor


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def catalogue(db):
    cat = ServiceCategory(title="Jarrohlik")
    set_i18n(cat, "title", {"uz": "Jarrohlik", "ru": "Хирургия", "en": "Surgery"})
    for lang in ("uz", "ru", "en"):
        setattr(cat, f"slug_{lang}", "jarrohlik")
    cat.slug = "jarrohlik"
    cat.save()

    svc = Service(category=cat, duration_minutes=90, is_featured=True)
    set_i18n(svc, "title", {"uz": "Implantatsiya", "ru": "Имплантация", "en": "Dental implants"})
    set_i18n(
        svc, "excerpt", {"uz": "Bitta tishdan", "ru": "От одного зуба", "en": "From one tooth"}
    )
    for lang, slug in (("uz", "implantatsiya"), ("ru", "implantatsiya"), ("en", "dental-implants")):
        setattr(svc, f"slug_{lang}", slug)
    svc.slug = "implantatsiya"
    svc.save()

    hidden = Service(category=cat, title="Yashirin", slug="yashirin", is_active=False)
    hidden.save()
    return {"category": cat, "service": svc, "hidden": hidden}


def test_site_settings_returns_theme_and_hours(api, db):
    ClinicSettings.load()
    WorkingHours.objects.create(weekday=6, is_closed=True)
    StatCounter.objects.create(label="mutaxassis", value=14)

    res = api.get("/api/v1/site-settings/")
    assert res.status_code == 200

    body = res.json()
    assert set(body["theme"]) == {"brand", "accent", "ink", "surface", "fontPair"}
    assert any(h["is_closed"] for h in body["working_hours"])
    assert body["counters"][0]["value"] == 14
    assert res["Cache-Control"] == "public, max-age=300"


@pytest.mark.parametrize(
    "lang,expected",
    [("uz", "Implantatsiya"), ("ru", "Имплантация"), ("en", "Dental implants")],
)
def test_services_resolve_accept_language(api, catalogue, lang, expected):
    res = api.get("/api/v1/services/", HTTP_ACCEPT_LANGUAGE=lang)
    assert res.status_code == 200
    assert res.json()["results"][0]["title"] == expected


@pytest.mark.parametrize("lang,expected", [("ru", "Имплантация"), ("en", "Dental implants")])
def test_lang_query_param_overrides_header(api, catalogue, lang, expected):
    """`?lang=` Accept-Language'dan ustun turadi."""
    res = api.get(f"/api/v1/services/?lang={lang}", HTTP_ACCEPT_LANGUAGE="uz")
    assert res.json()["results"][0]["title"] == expected


def test_inactive_services_are_hidden(api, catalogue):
    slugs = [s["slug"] for s in api.get("/api/v1/services/").json()["results"]]
    assert "yashirin" not in slugs


def test_featured_filter(api, catalogue):
    res = api.get("/api/v1/services/?featured=1")
    assert all(s["is_featured"] for s in res.json()["results"])


def test_service_detail_includes_prices_and_doctors(api, catalogue):
    res = api.get("/api/v1/services/implantatsiya/")
    assert res.status_code == 200
    body = res.json()
    assert "prices" in body and "doctors" in body and "faqs" in body


def test_prices_hidden_when_disabled(api, catalogue):
    """`prices_visible=False` boʻlsa narxlar butunlay yashiriladi (ADR-004)."""
    settings_obj = ClinicSettings.load()
    settings_obj.prices_visible = False
    settings_obj.save()

    assert api.get("/api/v1/services/prices/").json() == []


def test_unpublished_case_is_not_exposed(api, db):
    """Bemor roziligisiz / chop etilmagan ish API'da koʻrinmaydi (ADR-014)."""
    CasePair.objects.create(
        title="Rozilik yoʻq",
        slug="rozilik-yoq",
        image_before="cases/a.jpg",
        image_after="cases/b.jpg",
        consent_on_file=False,
        is_published=False,
    )
    assert api.get("/api/v1/cases/").json()["count"] == 0


def test_image_field_returns_object_not_bare_url(api, db):
    """Rasm {src,width,height} shaklida — CLS=0 uchun (ADR E-qism)."""
    doc = Doctor.objects.create(full_name="Test", specialization="terapevt")
    res = api.get("/api/v1/doctors/")
    payload = res.json()["results"][0]
    assert payload["photo"] is None  # rasm yoʻq — null, boʻsh satr emas
    assert payload["languages"] == []
    assert doc.slug == "test"


def test_reviews_summary(api, db):
    from apps.reviews.models import Review

    Review.objects.create(author_name="A", rating=5, text="Zoʻr")
    Review.objects.create(author_name="B", rating=4, text="Yaxshi")

    body = api.get("/api/v1/reviews/summary/").json()
    assert body["total"] == 2
    assert body["average"] == 4.5


def test_healthz(api, db):
    res = api.get("/healthz/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_openapi_schema_is_reachable(api, db):
    assert api.get("/api/v1/schema/").status_code == 200
