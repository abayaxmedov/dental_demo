"""
Base settings — dental_demo (headless DRF, ADR-016).
Shared by dev / prod / test. Environment via django-environ.
"""

from pathlib import Path

import environ

# backend/ katalogi (config/settings/base.py dan 3 daraja yuqori)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# backend/.env (agar bor boʻlsa) oʻqiladi
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---- Applications ----
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.core",
    "apps.services",
    "apps.team",
    "apps.appointments",
    "apps.leads",
    "apps.cases",
    "apps.gallery",
    "apps.reviews",
    "apps.blog",
    "apps.pages",
    "apps.notifications",
]

# modeltranslation admin integratsiyasi uchun django.contrib.admin dan OLDIN;
# unfold esa django.contrib.admin dan OLDIN turishi kerak (admin skin).
INSTALLED_APPS = (
    ["modeltranslation", "unfold", "unfold.contrib.filters", "unfold.contrib.forms"]
    + DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Accept-Language ni oʻqiydi (headless API uchun; URL prefiks Next.js'da — ADR-016)
    "django.middleware.locale.LocaleMiddleware",
    "apps.core.middleware.QueryParamLocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.core.middleware.AdminLocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Headless: faqat admin va DRF template'lari. Frontend Next.js'da (ADR-016).
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---- Database ----
# DATABASE_URL boʻlmasa dev uchun sqlite (faqat lokal `check`/tez ishga tushirish).
# Haqiqiy maqsad — PostgreSQL 17 (docker-compose), btree_gist/pg_trgm bilan.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---- i18n / l10n (ADR-002/014) ----
# URL prefiks endi Next.js'da (next-intl). Bu yerda faqat content tarjimasi (modeltranslation)
# va admin/API uchun Accept-Language hal qilinadi.
LANGUAGE_CODE = "uz"
LANGUAGES = [
    ("uz", "Oʻzbekcha"),
    ("ru", "Русский"),
    ("en", "English"),
]
MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"
MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uz", "ru", "en")
LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ---- Static / media ----
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1

# ---- DRF (ADR-016: barcha read/write shu API orqali) ----
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.core.errors.exception_handler",
    # Ommaviy read/write API — sessiya auth YOʻQ (admin cookie CSRF 403 bermasin, critique #4).
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_THROTTLE_RATES": {
        "booking": env("BOOKING_THROTTLE_RATE", default="5/hour"),
        "lead": env("LEAD_THROTTLE_RATE", default="10/hour"),
        "token": env("TOKEN_THROTTLE_RATE", default="30/hour"),
    },
    # X-Forwarded-For'da ishonchli proksilar soni (critique #5: spoofing oldini oladi).
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "dental_demo API",
    "DESCRIPTION": "Headless DRF backend — Oq Marvarid Dental demo (ADR-016).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
}

# ---- CORS (frontend origin — ADR-016) ----
from corsheaders.defaults import default_headers  # noqa: E402

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
# Booking POST idempotency-key header'ini yuboradi — preflight'da ruxsat (critique #1).
CORS_ALLOW_HEADERS = (*default_headers, "idempotency-key")
# Frontend Retry-After/Idempotency-Replayed header'larini o'qishi uchun (critique #1).
CORS_EXPOSE_HEADERS = ("Retry-After", "Idempotency-Replayed", "ETag")

# ---- Telegram (ADR-010) — kalitlar .env da ----
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")
# Webhook secret_token — setWebhook'da beriladi, callback so'rovlari shu bilan tekshiriladi.
TELEGRAM_WEBHOOK_SECRET = env("TELEGRAM_WEBHOOK_SECRET", default="")
# Callback tugmalari uchun sayt bazaviy URL'i (webhook yo'q bo'lsa tugmalar ko'rsatilmaydi).
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", default="")

# ---- Booking (Faza 2) ----
BOOKING_MIN_LEAD_MINUTES = env.int("BOOKING_MIN_LEAD_MINUTES", default=120)  # 2 soat
BOOKING_WINDOW_DAYS = env.int("BOOKING_WINDOW_DAYS", default=30)
CONSENT_TEXT_VERSION = env("CONSENT_TEXT_VERSION", default="v1")


# ---- Unfold admin (registratura xodimi uchun, R-14) ----
UNFOLD = {
    "SITE_TITLE": "Oq Marvarid Dental",
    "SITE_HEADER": "Oq Marvarid Dental",
    "SITE_SUBHEADER": "Boshqaruv paneli",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "COLORS": {
        "primary": {
            "50": "236 253 253",
            "100": "207 250 250",
            "200": "165 243 243",
            "300": "103 232 233",
            "400": "34 211 214",
            "500": "14 124 134",
            "600": "13 110 120",
            "700": "15 90 99",
            "800": "20 73 80",
            "900": "22 61 68",
            "950": "8 40 46",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
