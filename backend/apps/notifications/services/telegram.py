"""
Telegram Bot API klienti (ADR-010, ADR-006).
Kafolatlar:
  - Token boʻsh boʻlsa → "yozildi, yuborilmadi" (NotificationLog), crash/blok YOʻQ.
  - Hech qanday exception request'ga (bemorga) yetib bormaydi.
  - Har urinish NotificationLog yozadi.
Inline tugma/webhook subsistemasi v1'da YOʻQ (critique #30) — guruh xabari + manage link yetarli.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger("dental.telegram")

API = "https://api.telegram.org/bot{token}/sendMessage"
TIMEOUT = 3  # soniya (ADR-006)

# Telegram HTML parse_mode — faqat & < > escape qilinadi (MarkdownV2 ~18 belgi talab qiladi).
# Klinika/bemor nomlarida &<> uchrashi mumkin, shuning uchun HTML tanlandi (critique/spec).


def escape_html(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SendResult:
    def __init__(
        self, ok: bool, *, error: str = "", permanent: bool = False, retry_after: int | None = None
    ):
        self.ok = ok
        self.error = error
        self.permanent = permanent  # qayta urinish foydasiz (bad token, chat not found)
        self.retry_after = retry_after


def send_message(text: str, *, chat_id: str | None = None) -> SendResult:
    """Bitta xabar yuboradi. Hech qachon exception ko'tarmaydi."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat = chat_id or settings.TELEGRAM_CHAT_ID

    if not token or not chat:
        # Dev/yangi deploy: sozlanmagan — bu XATO EMAS, degradatsiya.
        logger.info("Telegram sozlanmagan (token/chat boʻsh) — xabar yuborilmadi")
        return SendResult(False, error="not_configured", permanent=True)

    try:
        resp = requests.post(
            API.format(token=token),
            json={
                "chat_id": chat,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=TIMEOUT,
        )
    except requests.Timeout:
        return SendResult(False, error="timeout")
    except requests.ConnectionError as e:
        return SendResult(False, error=f"connection: {e}")
    except requests.RequestException as e:  # boshqa har qanday requests xatosi
        return SendResult(False, error=f"request: {e}")

    if resp.status_code == 200 and resp.json().get("ok"):
        return SendResult(True)

    # Xatoni tahlil qilamiz: doimiy vs vaqtinchalik
    try:
        body = resp.json()
    except ValueError:
        body = {}
    desc = body.get("description", resp.text[:200])

    if resp.status_code == 429:
        retry_after = int(body.get("parameters", {}).get("retry_after", 1))
        return SendResult(False, error=f"rate_limited: {desc}", retry_after=retry_after)
    if resp.status_code in (400, 401, 403, 404):
        # bad token, chat not found, bot kicked — qayta urinish foydasiz
        return SendResult(False, error=f"permanent {resp.status_code}: {desc}", permanent=True)
    # 5xx va boshqalar — vaqtinchalik
    return SendResult(False, error=f"transient {resp.status_code}: {desc}")
