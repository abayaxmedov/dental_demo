"""Production settings (UZ VPS — ADR-014)."""

from .base import *  # noqa: F401,F403

DEBUG = False

# SITE_HTTPS — domen + TLS boʻlsa `true`. IP-only HTTP demo uchun `false` (aks holda
# SECURE_SSL_REDIRECT https'ga cheksiz redirect qiladi va sayt ochilmaydi). Domen olgach
# `true` qiling va qayta deploy qiling (frontend CSP ham shu bayroqni oʻqiydi).
SITE_HTTPS = env.bool("SITE_HTTPS", default=False)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# DIQQAT: http→https redirect'ni EDGE (reverse proxy — host nginx + certbot) bajaradi, Django EMAS.
# Nega default False: Django SECURE_SSL_REDIRECT=True boʻlsa u ICHKI SSR fetch'ni ham
# (frontend → http://backend:8000, X-Forwarded-Proto YOʻQ) https'ga 301 qiladi → backend'da TLS
# yoʻq → "fetch failed" → barcha SSR sahifa BOʻSH chiqadi (T-DEPLOY-03 bug). Tashqi trafik
# host nginx'da allaqachon https'ga yoʻnaltiriladi, shuning uchun bu ortiqcha va zararli.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = SITE_HTTPS
CSRF_COOKIE_SECURE = SITE_HTTPS
SECURE_HSTS_SECONDS = 31536000 if SITE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SITE_HTTPS
SECURE_HSTS_PRELOAD = SITE_HTTPS

# Admin login POST (Django 4+) Origin sarlavhasini shu roʻyxatga solishtiradi — schema BILAN.
# Boʻsh boʻlsa bare-IP admin'da CSRF 403 chiqadi. .env: CSRF_TRUSTED_ORIGINS=http://3.227.184.179
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# WhiteNoise — static'ni gunicorn oʻzi serve qiladi (nginx faqat /media'ni proxy qiladi).
# SecurityMiddleware'dan keyin, boshqa hammadan oldin (WhiteNoise talabi).
MIDDLEWARE = [
    *MIDDLEWARE[:1],  # corsheaders (eng yuqorida qolishi kerak)
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[2:],  # SecurityMiddleware'dan keyingi hammasi
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # WhiteNoise: siqilgan + manifest (far-future cache) — ManifestStaticFilesStorage o'rniga.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
