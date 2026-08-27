"""
RFC-9457 (application/problem+json) xato javoblari, uch tilda lokalizatsiya qilingan.
DRF exception_handler'ni oʻraydi; Retry-After header'ini saqlaydi (critique #19).
"""

from __future__ import annotations

from django.utils.translation import get_language
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

TYPE_BASE = "https://oqmarvarid.uz/errors/"

# code -> {locale -> (title, detail)}
MESSAGES = {
    "slot_taken": {
        "uz": (
            "Bu vaqt band boʻldi",
            "Bu vaqtni siz yozilishdan bir lahza oldin boshqa bemor band qildi. Quyidagi boʻsh vaqtlardan birini tanlang.",
        ),
        "ru": (
            "Это время уже занято",
            "Это время заняли за мгновение до вас. Пожалуйста, выберите другое из свободных ниже.",
        ),
        "en": (
            "That time was just taken",
            "Someone booked this time moments before you. Please pick another slot from the list below.",
        ),
    },
    "no_doctor_available": {
        "uz": (
            "Boʻsh shifokor qolmadi",
            "Afsuski, bu vaqtga boʻsh shifokor qolmadi. Boshqa vaqtni tanlang.",
        ),
        "ru": (
            "Нет свободных врачей",
            "К сожалению, на это время нет свободных врачей. Выберите другое время.",
        ),
        "en": ("No doctor available", "No doctor is free at that time. Please pick another slot."),
    },
    "duplicate_booking": {
        "uz": (
            "Sizda allaqachon yozuv bor",
            "Bu raqamda yaqinda yaratilgan qabul mavjud. Agar oʻzgartirmoqchi boʻlsangiz, biz bilan bogʻlaning.",
        ),
        "ru": (
            "У вас уже есть запись",
            "На этот номер недавно создана запись. Чтобы изменить её, свяжитесь с нами.",
        ),
        "en": (
            "You already have a booking",
            "There is a recent booking for this number. Contact us to change it.",
        ),
    },
    "slot_unavailable": {
        "uz": (
            "Vaqt endi mavjud emas",
            "Tanlangan vaqt endi boʻsh emas. Iltimos, boshqasini tanlang.",
        ),
        "ru": (
            "Время недоступно",
            "Выбранное время больше не свободно. Пожалуйста, выберите другое.",
        ),
        "en": (
            "Time no longer available",
            "The selected time is no longer free. Please choose another.",
        ),
    },
    "lead_time_violation": {
        "uz": (
            "Vaqt juda yaqin",
            "Onlayn yozilish kamida 2 soat oldin ochiq. Keyingi vaqtni tanlang.",
        ),
        "ru": (
            "Слишком близко",
            "Онлайн-запись возможна минимум за 2 часа. Выберите более позднее время.",
        ),
        "en": ("Too soon", "Online booking needs at least 2 hours' notice. Pick a later time."),
    },
    "booking_disabled": {
        "uz": ("Onlayn yozilish vaqtincha yopiq", "Iltimos, telefon orqali bogʻlaning."),
        "ru": ("Онлайн-запись временно недоступна", "Пожалуйста, позвоните нам."),
        "en": ("Online booking is off", "Please call us to book."),
    },
    "invalid_phone": {
        "uz": ("Telefon raqami notoʻgʻri", "+998 bilan boshlanuvchi toʻgʻri raqam kiriting."),
        "ru": ("Неверный номер", "Введите корректный номер, начинающийся с +998."),
        "en": ("Invalid phone", "Enter a valid +998 phone number."),
    },
    "consent_required": {
        "uz": ("Rozilik kerak", "Davom etish uchun maxfiylik siyosatiga rozilik bering."),
        "ru": ("Требуется согласие", "Для продолжения примите политику конфиденциальности."),
        "en": ("Consent required", "Please accept the privacy policy to continue."),
    },
    "too_fast": {
        "uz": ("Soʻrov rad etildi", "Iltimos, qayta urinib koʻring."),
        "ru": ("Запрос отклонён", "Пожалуйста, попробуйте снова."),
        "en": ("Request rejected", "Please try again."),
    },
    "stale_form": {
        "uz": ("Forma eskirdi", "Sahifani yangilab, qayta urinib koʻring."),
        "ru": ("Форма устарела", "Обновите страницу и попробуйте снова."),
        "en": ("Form expired", "Refresh the page and try again."),
    },
    "service_required": {
        "uz": ("Xizmatni tanlang", "Iltimos, xizmat turini tanlang."),
        "ru": ("Выберите услугу", "Пожалуйста, выберите услугу."),
        "en": ("Select a service", "Please choose a service."),
    },
    "rate_limited": {
        "uz": ("Juda koʻp urinish", "Biroz kuting yoki bizga qoʻngʻiroq qiling."),
        "ru": ("Слишком много попыток", "Подождите немного или позвоните нам."),
        "en": ("Too many attempts", "Please wait a moment or call us."),
    },
    "not_found": {
        "uz": ("Topilmadi", "Bunday qabul topilmadi."),
        "ru": ("Не найдено", "Запись не найдена."),
        "en": ("Not found", "No such appointment."),
    },
    "already_cancelled": {
        "uz": ("Allaqachon bekor qilingan", "Bu qabul allaqachon bekor qilingan."),
        "ru": ("Уже отменено", "Эта запись уже отменена."),
        "en": ("Already cancelled", "This appointment is already cancelled."),
    },
    "not_cancellable": {
        "uz": ("Bekor qilib boʻlmaydi", "Bu qabulni bekor qilib boʻlmaydi."),
        "ru": ("Нельзя отменить", "Эту запись нельзя отменить."),
        "en": ("Cannot cancel", "This appointment cannot be cancelled."),
    },
    "not_reschedulable": {
        "uz": ("Koʻchirib boʻlmaydi", "Bu qabulni koʻchirib boʻlmaydi."),
        "ru": ("Нельзя перенести", "Эту запись нельзя перенести."),
        "en": ("Cannot reschedule", "This appointment cannot be moved."),
    },
    "appointment_past": {
        "uz": ("Vaqt oʻtib ketdi", "Bu qabul vaqti oʻtib ketgan. Bizga qoʻngʻiroq qiling."),
        "ru": ("Время прошло", "Время этой записи прошло. Позвоните нам."),
        "en": ("Time has passed", "This appointment time has passed. Please call us."),
    },
    "reschedule_limit": {
        "uz": ("Koʻchirish chegarasi", "Juda koʻp marta koʻchirildi. Bizga qoʻngʻiroq qiling."),
        "ru": ("Лимit переносов", "Слишком много переносов. Позвоните нам."),
        "en": ("Reschedule limit", "Too many reschedules. Please call us."),
    },
    "validation_error": {
        "uz": ("Maʼlumotni tekshiring", "Baʼzi maydonlar toʻgʻri toʻldirilmagan."),
        "ru": ("Проверьте данные", "Некоторые поля заполнены неверно."),
        "en": ("Check your details", "Some fields are not filled in correctly."),
    },
    "server_error": {
        "uz": ("Texnik nosozlik", "Kutilmagan xatolik. Keyinroq urinib koʻring."),
        "ru": ("Техническая ошибка", "Непредвиденная ошибка. Попробуйте позже."),
        "en": ("Server error", "An unexpected error occurred. Please try again later."),
    },
}


def _locale() -> str:
    lang = (get_language() or "uz")[:2]
    return lang if lang in ("uz", "ru", "en") else "uz"


def problem(
    code: str,
    *,
    status: int,
    errors: dict | None = None,
    instance: str = "",
    headers: dict | None = None,
    **extra,
) -> Response:
    loc = _locale()
    title, detail = MESSAGES.get(code, MESSAGES["server_error"]).get(loc, (code, ""))
    body = {
        "type": TYPE_BASE + code.replace("_", "-"),
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
    }
    if instance:
        body["instance"] = instance
    if errors:
        body["errors"] = errors
    body.update(extra)
    resp = Response(body, status=status, content_type="application/problem+json")
    resp["Cache-Control"] = "no-store"
    for k, v in (headers or {}).items():
        resp[k] = v
    return resp


def exception_handler(exc, context):
    """DRF standart handler'ni RFC-9457 shakliga oʻraydi."""
    response = drf_default_handler(exc, context)
    if response is None:
        return None  # 500 — Django default (Sentry uchun re-raise)

    from rest_framework.exceptions import Throttled, ValidationError

    headers = {}
    if isinstance(exc, Throttled) and exc.wait:
        headers["Retry-After"] = str(int(exc.wait))
        return problem("rate_limited", status=response.status_code, headers=headers)

    if isinstance(exc, ValidationError):
        errors = response.data if isinstance(response.data, dict) else {"detail": response.data}
        return problem("validation_error", status=response.status_code, errors=errors)

    # 404, 405, permission, va boshqalar
    code = "not_found" if response.status_code == 404 else "server_error"
    return problem(code, status=response.status_code)
