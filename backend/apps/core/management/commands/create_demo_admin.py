"""`manage.py create_demo_admin` — prospektga koʻrsatish uchun demo admin akkaunt.

Sotuv demosida prospekt `/admin/` ni oʻzi koʻrishi uchun. Idempotent (mavjud boʻlsa parolni
tiklaydi). XAVFSIZLIK: bu zaif, maʼlum parolli superuser — shuning uchun default'da faqat
`DEBUG=True` da ishlaydi; production'da ataylab `--force` kerak va LOUD ogohlantirish chiqadi.
HANDOVER.md: ishga tushirishdan OLDIN oʻchiring yoki parolini oʻzgartiring.
"""

from __future__ import annotations

import os

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
        # `settings.DEBUG` YETARLI EMAS: manage.py `DJANGO_SETTINGS_MODULE` ni
        # `config.settings.dev` ga default qiladi, dev.py esa `DEBUG = True` ni qotirib
        # yozgan. Yaʼni prod serverda `python manage.py create_demo_admin` desa gate
        # aylanib oʻtilardi (AUDIT-2026-08-29 / T-FIX-16). Shuning uchun `.env` dagi
        # XOM qiymatni ham tekshiramiz — u serverning haqiqiy niyatini koʻrsatadi
        # (django-environ `read_env` uni os.environ ga yozadi).
        raw_debug = os.environ.get("DEBUG", "")
        raw_says_prod = raw_debug.strip().lower() in {"false", "0", "no", "off", ""}
        if (not dj_settings.DEBUG or raw_says_prod) and not opts["force"]:
            raise CommandError(
                "Demo admin ishlab chiqarishda yaratilmaydi "
                f"(settings.DEBUG={dj_settings.DEBUG}, .env DEBUG={raw_debug!r}). "
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
