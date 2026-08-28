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
    with pytest.raises(CommandError, match="DEBUG=False"):
        call_command("create_demo_admin", username="demo")
