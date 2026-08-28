"""`manage.py create_demo_admin` testlari."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command


@pytest.mark.django_db
def test_creates_superuser_with_force():
    call_command("create_demo_admin", "--force", username="demo", password="pw-123")
    User = get_user_model()
    u = User.objects.get(username="demo")
    assert u.is_superuser and u.is_staff
    assert u.check_password("pw-123")


@pytest.mark.django_db
def test_idempotent_resets_password(settings):
    settings.DEBUG = True  # force'siz ishlashi uchun
    call_command("create_demo_admin", username="demo", password="first")
    call_command("create_demo_admin", username="demo", password="second")
    User = get_user_model()
    assert User.objects.filter(username="demo").count() == 1
    assert User.objects.get(username="demo").check_password("second")


@pytest.mark.django_db
def test_refuses_in_production_without_force(settings):
    settings.DEBUG = False
    with pytest.raises(CommandError, match="ishlab chiqarishda yaratilmaydi"):
        call_command("create_demo_admin", username="demo")


@pytest.mark.django_db
def test_refuses_when_env_says_prod_even_under_dev_settings(settings, monkeypatch):
    """T-FIX-16: manage.py dev settings'ga default qiladi (DEBUG=True qotirilgan),
    shuning uchun `.env` dagi XOM DEBUG=False ham gate'ni yopishi shart."""
    settings.DEBUG = True
    monkeypatch.setenv("DEBUG", "False")
    with pytest.raises(CommandError, match="ishlab chiqarishda yaratilmaydi"):
        call_command("create_demo_admin", username="demo")


@pytest.mark.django_db
def test_force_still_works_on_a_production_box(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setenv("DEBUG", "False")
    call_command("create_demo_admin", "--force", username="demo", password="pw-forced")
    from django.contrib.auth import get_user_model

    assert get_user_model().objects.get(username="demo").check_password("pw-forced")
