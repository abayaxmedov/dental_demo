"""Oʻzbekiston telefon raqamlarini E.164 (+998XXXXXXXXX) ga normallashtirish (T-P1-13)."""

import re

UZ_CODE = "998"
NATIONAL_LEN = 9  # operator kodi (2) + raqam (7)


class InvalidPhoneError(ValueError):
    """Raqam Oʻzbekiston formatiga mos emas."""


def normalize_uz_phone(raw: str) -> str:
    """
    '90 123 45 67', '8 90 1234567', '998901234567', '+998 90 123-45-67'
    → '+998901234567'. Notoʻgʻri boʻlsa InvalidPhoneError.
    """
    if not raw or not raw.strip():
        raise InvalidPhoneError("Telefon raqami boʻsh.")

    digits = re.sub(r"\D", "", raw)

    if digits.startswith(UZ_CODE):
        national = digits[len(UZ_CODE) :]
    elif len(digits) == NATIONAL_LEN + 1 and digits.startswith("8"):
        # eski '8 90 …' formati
        national = digits[1:]
    elif len(digits) == NATIONAL_LEN:
        national = digits
    else:
        raise InvalidPhoneError(f"Notoʻgʻri raqam: {raw!r}")

    if len(national) != NATIONAL_LEN or not national.isdigit():
        raise InvalidPhoneError(f"Notoʻgʻri raqam: {raw!r}")

    return f"+{UZ_CODE}{national}"
