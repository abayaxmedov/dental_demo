"""
Yarim-ochiq [a, b) aware datetime intervallari ustida ishlaydigan sof funksiyalar.
Slot engine shulardan foydalanadi (slots.py). Bu yerda I/O yoʻq, faqat matematika.
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

CLINIC_TZ = ZoneInfo(settings.TIME_ZONE)

Interval = tuple[datetime, datetime]  # (start, end), aware, [start, end)


def clinic_tz() -> ZoneInfo:
    # settings.TIME_ZONE oʻzgarishi mumkin (reskin) — har chaqiruvda oʻqiladi.
    return ZoneInfo(settings.TIME_ZONE)


def L(d: date, t: time) -> datetime:
    """Naive lokal devor-soatini klinika mintaqasidagi aware datetime'ga aylantiradi.
    Bu modulda naive→aware koʻtarishning YAGONA joyi (ADR: timezone toʻgʻriligi)."""
    return datetime.combine(d, t, tzinfo=clinic_tz())


def _assert_aware(dt: datetime) -> None:
    if settings.DEBUG and not timezone.is_aware(dt):
        raise ValueError(f"aware datetime kutilgan edi, naive keldi: {dt!r}")


def intersect(a: Interval, b: Interval) -> Interval | None:
    """Ikki intervalning kesishmasi yoki None."""
    lo = max(a[0], b[0])
    hi = min(a[1], b[1])
    return (lo, hi) if lo < hi else None


def clip(intervals: list[Interval], lo: datetime, hi: datetime) -> list[Interval]:
    """Har intervalni [lo, hi) ga qirqadi, boʻshlarni tashlaydi.
    Koʻp kunli TimeOff'ni kunlik qismlarga toʻgʻri ajratadi."""
    out: list[Interval] = []
    for iv in intervals:
        c = intersect(iv, (lo, hi))
        if c:
            out.append(c)
    return out


def subtract(interval: Interval, blockers: list[Interval]) -> list[Interval]:
    """interval'dan blockers'ni ayiradi. Saralangan, disjoint, maksimal boʻsh oraliqlar."""
    start, end = interval
    _assert_aware(start)
    cursor = start
    free: list[Interval] = []
    for b0, b1 in sorted(blockers):
        if b1 <= cursor or b0 >= end:
            continue  # bu bloker interval bilan kesishmaydi
        if b0 > cursor:
            free.append((cursor, min(b0, end)))
        cursor = max(cursor, b1)
        if cursor >= end:
            break
    if cursor < end:
        free.append((cursor, end))
    return free


def fits_in_one(a: datetime, b: datetime, free: list[Interval]) -> bool:
    """[a, b) butunligicha BITTA boʻsh oraliq ichiga sigʻadimi?
    Ikki oraliq orasini bosib oʻtsa — sigʻmaydi."""
    return any(f0 <= a and b <= f1 for f0, f1 in free)


def covers(blockers: list[Interval], interval: Interval) -> bool:
    """blockers birlashib butun interval'ni qoplaydimi (boʻsh joy qolmaydimi)?"""
    return not subtract(interval, blockers)


def split_on_break(
    block: Interval, break_start: time | None, break_end: time | None, day: date
) -> list[Interval]:
    """Ish blokini tanaffusga koʻra 1 yoki 2 ta sub-blokka boʻladi.
    Tanaffus blok chegarasi (blocker emas) — grid tanaffusdan keyin qayta anchor boʻladi."""
    if break_start is None or break_end is None:
        return [block]
    bs, be = L(day, break_start), L(day, break_end)
    # tanaffus blok bilan kesishmasa — boʻlinmaydi
    if be <= block[0] or bs >= block[1]:
        return [block]
    subs: list[Interval] = []
    if block[0] < bs:
        subs.append((block[0], min(bs, block[1])))
    if be < block[1]:
        subs.append((max(be, block[0]), block[1]))
    return subs
