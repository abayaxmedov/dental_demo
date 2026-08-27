"""Anti-spam testlari (ADR-009)."""

import time

from apps.core.antispam import (
    FormTiming,
    check_form_timing,
    hash_ip,
    make_form_token,
)


def test_too_fast():
    now = time.time()
    assert check_form_timing(make_form_token(issued_at=now - 0.5), now=now) == FormTiming.TOO_FAST


def test_normal_speed_ok():
    now = time.time()
    assert check_form_timing(make_form_token(issued_at=now - 5), now=now) == FormTiming.OK


def test_missing_token_stale():
    assert check_form_timing(None) == FormTiming.STALE


def test_tampered_token_stale():
    assert check_form_timing("garbage.token.value") == FormTiming.STALE


def test_hash_ip_is_salted(settings):
    """Bir xil IP ikki xil SECRET_KEY ostida boshqacha hash beradi (critique #26)."""
    settings.SECRET_KEY = "key-one-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    h1 = hash_ip("1.2.3.4")
    settings.SECRET_KEY = "key-two-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    h2 = hash_ip("1.2.3.4")
    assert h1 != h2
    assert "1.2.3.4" not in h1  # xom IP saqlanmaydi


def test_hash_ip_empty():
    assert hash_ip(None) == "" and hash_ip("") == ""


def test_hash_ip_fits_field():
    assert len(hash_ip("192.168.1.1")) == 64  # CharField(max_length=64)
