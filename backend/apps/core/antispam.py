"""
Anti-spam (ADR-009): honeypot, imzolangan form-token bilan vaqt tuzogʻi, tuzlangan IP hash.
SMS OTP yoʻq. Bu qatlamlar tashqi bogʻliqliksiz spamning aksariyatini toʻxtatadi.
"""

from __future__ import annotations

import hashlib
import time

from django.conf import settings
from django.core import signing

FORM_TOKEN_SALT = "dental.form_token"
# Honeypot maydoni — brauzer autofill tanimaydigan nom (critique #17).
HONEYPOT_FIELD = "referral_note_2"
MIN_FILL_SECONDS = 2
MAX_FORM_AGE_SECONDS = 2 * 60 * 60  # 2 soat


def make_form_token(*, issued_at: float | None = None) -> str:
    """Forma render qilinganda beriladigan imzolangan token.
    Yaratilgan vaqt payload ICHIDA — Django token formatini parse qilmaymiz."""
    return signing.dumps(
        {"t": issued_at if issued_at is not None else time.time()}, salt=FORM_TOKEN_SALT
    )


class FormTiming:
    OK = "ok"
    TOO_FAST = "too_fast"
    STALE = "stale_form"


def check_form_timing(token: str | None, *, now: float | None = None) -> str:
    """Token yoshini tekshiradi: < 2s = bot, 2s..2soat = OK, buzuq/eski = eskirgan."""
    if not token:
        return FormTiming.STALE
    try:
        data = signing.loads(token, salt=FORM_TOKEN_SALT, max_age=MAX_FORM_AGE_SECONDS)
    except (signing.SignatureExpired, signing.BadSignature):
        return FormTiming.STALE
    issued = data.get("t")
    if not isinstance(issued, (int, float)):
        return FormTiming.STALE
    age = (now if now is not None else time.time()) - issued
    if age < MIN_FILL_SECONDS:
        return FormTiming.TOO_FAST
    return FormTiming.OK


def hash_ip(ip: str | None) -> str:
    """Tuzlangan IP hash (critique #26): tuzsiz sha256 IPv4 fazosida qaytariladigan boʻlardi."""
    if not ip:
        return ""
    key = settings.SECRET_KEY.encode()[:64]
    return hashlib.blake2b(ip.encode(), key=key, digest_size=32).hexdigest()


def client_ip(request) -> str | None:
    """NUM_PROXIES=1 bilan mos: X-Forwarded-For'ning ishonchli proksidan oldingi qismi.
    Eng oʻngdagi qiymat — nginx qoʻygan, spoof qilinmaydi."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.META.get("REMOTE_ADDR")
