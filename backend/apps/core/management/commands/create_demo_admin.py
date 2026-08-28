"""`manage.py create_demo_admin` — prospektga koʻrsatish uchun demo admin akkaunt.

Sotuv demosida prospekt `/admin/` ni oʻzi koʻrishi uchun. Idempotent (mavjud boʻlsa parolni
tiklaydi). XAVFSIZLIK: bu zaif, maʼlum parolli superuser — shuning uchun default'da faqat
`DEBUG=True` da ishlaydi; production'da ataylab `--force` kerak va LOUD ogohlantirish chiqadi.
HANDOVER.md: ishga tushirishdan OLDIN oʻchiring yoki parolini oʻzgartiring.
"""

from __future__ import annotations

from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

DEFAULT_USERNAME = "demo"
DEFAULT_PASSWORD = "demo-2026"  # ataylab maʼlum — faqat demo uchun
DEFAULT_EMAIL = "demo@example.com"


class Command(BaseCommand):
    help = "Demo uchun admin akkaunt yaratadi/tiklaydi (faqat DEBUG, aks holda --force)."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=DEFAULT_USERNAME)
        parser.add_argument("--password", default=DEFAULT_PASSWORD)
        parser.add_argument("--email", default=DEFAULT_EMAIL)
        parser.add_argument(
            "--force",
            action="store_true",
            help="Production'da (DEBUG=False) ham yaratishga ruxsat (XAVFLI).",
        )

    def handle(self, *args, **opts):
        if not dj_settings.DEBUG and not opts["force"]:
            raise CommandError(
                "DEBUG=False — demo admin ishlab chiqarishda yaratilmaydi. "
                "Rostdan xohlasangiz --force qoʻshing (tavsiya etilmaydi)."
            )

        User = get_user_model()
        username = opts["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": opts["email"], "is_staff": True, "is_superuser": True},
        )
        user.email = opts["email"]
        user.is_staff = True
        user.is_superuser = True
        user.set_password(opts["password"])
        user.save()

        verb = "yaratildi" if created else "tiklandi"
        self.stdout.write(
            self.style.SUCCESS(f"✓ Demo admin {verb}: {username} / {opts['password']}")
        )
        if not dj_settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(
                    "⚠ PRODUCTION'da zaif parolli superuser yaratildi — demo tugagach OʻCHIRING."
                )
            )
        self.stdout.write("Kirish: /admin/  (HANDOVER.md — ishga tushirishdan oldin oʻchiring).")
