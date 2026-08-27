"""
Klinika Telegram guruhiga xabar matnlari.
Finding #29: klinika xabarlari BITTA staff tilida (uz) — auditoriya registratura xodimi.
Bemorning tili alohida "Til:" qatori sifatida beriladi (xodim qaysi tilda qoʻngʻiroq
qilishni bilishi uchun). 27 shablon oʻrniga bir nechta funksiya.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

from django.conf import settings

from .telegram import escape_html as e

LOCALE_NAME = {"uz": "oʻzbek", "ru": "rus", "en": "ingliz"}


def _local(dt):
    return dt.astimezone(ZoneInfo(settings.TIME_ZONE))


def _dt(dt) -> str:
    return _local(dt).strftime("%d.%m.%Y  %H:%M")


def _manage_link(appt) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    if not base:
        return ""
    return f"{base}/uz/qabul/{appt.cancel_token}"


def new_appointment(appt) -> str:
    doctor = appt.doctor.full_name if appt.doctor else "—"
    service = appt.service.title if appt.service else "—"
    lines = [
        "🦷 <b>Yangi onlayn qabul</b>",
        "",
        f"👤 <b>{e(appt.patient_name)}</b>",
        f'📞 <a href="tel:{e(appt.phone)}">{e(appt.phone)}</a>',
        f"🕒 {e(_dt(appt.starts_at))}",
        f"🩺 {e(service)}",
        f"👨‍⚕️ {e(doctor)}",
        f"🌐 Til: {LOCALE_NAME.get(appt.locale, appt.locale)}",
        f"🔖 <code>{e(appt.code)}</code>",
    ]
    if appt.comment:
        lines.append(f"💬 {e(appt.comment)}")
    link = _manage_link(appt)
    if link:
        lines += ["", f"🔗 {e(link)}"]
    return "\n".join(lines)


def new_lead(lead) -> str:
    kind = lead.get_kind_display()
    lines = [
        f"📩 <b>Yangi murojaat — {e(kind)}</b>",
        "",
        f"👤 <b>{e(lead.name)}</b>",
        f'📞 <a href="tel:{e(lead.phone)}">{e(lead.phone)}</a>',
        f"🌐 Til: {LOCALE_NAME.get(lead.locale, lead.locale)}",
    ]
    if lead.service_id:
        lines.append(f"🩺 {e(lead.service.title)}")
    if lead.preferred_time:
        lines.append(f"🕒 Qulay vaqt: {e(lead.preferred_time)}")
    if lead.message:
        lines.append(f"💬 {e(lead.message)}")
    if lead.source_page:
        lines.append(f"📄 {e(lead.source_page)}")
    return "\n".join(lines)


def appointment_cancelled(appt, *, late: bool = False, reason: str = "") -> str:
    doctor = appt.doctor.full_name if appt.doctor else "—"
    head = "⚠️ <b>KECH BEKOR QILISH</b>" if late else "❌ <b>Qabul bekor qilindi</b>"
    lines = [
        head,
        "",
        f"👤 <b>{e(appt.patient_name)}</b>",
        f'📞 <a href="tel:{e(appt.phone)}">{e(appt.phone)}</a>',
        f"🕒 {e(_dt(appt.starts_at))}",
        f"👨‍⚕️ {e(doctor)}",
        f"🔖 <code>{e(appt.code)}</code>",
    ]
    if reason:
        lines.append(f"💬 Sabab: {e(reason)}")
    if late:
        lines.append("")
        lines.append("Slotni toʻldirishga urinib koʻring.")
    return "\n".join(lines)


def appointment_rescheduled(appt, *, old_start, doctor_changed: bool = False) -> str:
    doctor = appt.doctor.full_name if appt.doctor else "—"
    lines = [
        "🔄 <b>Qabul koʻchirildi</b>",
        "",
        f"👤 <b>{e(appt.patient_name)}</b>",
        f'📞 <a href="tel:{e(appt.phone)}">{e(appt.phone)}</a>',
        f"🕒 {e(_dt(old_start))} → <b>{e(_dt(appt.starts_at))}</b>",
        f"👨‍⚕️ {e(doctor)}",
        f"🔖 <code>{e(appt.code)}</code>",
    ]
    if doctor_changed:
        lines.append("❗ Shifokor oʻzgardi")
    return "\n".join(lines)
