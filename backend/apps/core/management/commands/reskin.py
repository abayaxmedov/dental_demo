"""`manage.py reskin --config prospect.yml` — bitta prospekt uchun 30 daqiqada qayta brendlash.

ADR-012: reskin BIRINCHI DARAJALI xususiyat — mahsulotning butun qiymat taklifi (bir marta
quriladi, har klinika uchun qayta brendlanadi). YAML config `ClinicSettings` singleton'iga
yoziladi; brand rang frontend'ga CSS custom property sifatida uzatiladi (ADR-004), shuning
uchun bitta hex butun `color-mix` shkalasini surади.

    manage.py reskin --config prospect.yml [--assets-dir DIR] [--dry-run]

Config faqat oʻzgartirmoqchi boʻlgan kalitlarni oʻz ichiga oladi (qisman yangilash) — masalan
faqat ranglarni yoki faqat nomni. Namuna: `deploy/reskin/prospect.example.yml`.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import ClinicSettings, FontPair

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# YAML seksiyasi → model maydoni. Nested config'ni tekis model maydoniga bogʻlaydi.
FIELD_MAP: dict[str, dict[str, str]] = {
    "_root": {"name": "name", "tagline": "tagline", "about_short": "about_short"},
    "theme": {
        "brand": "brand_color",
        "accent": "accent_color",
        "ink": "ink_color",
        "surface": "surface_color",
        "font_pair": "font_pair",
    },
    "contact": {
        "phone_primary": "phone_primary",
        "phone_secondary": "phone_secondary",
        "email": "email",
        "telegram_username": "telegram_username",
        "telegram_channel_url": "telegram_channel_url",
        "instagram_url": "instagram_url",
        "facebook_url": "facebook_url",
        "youtube_url": "youtube_url",
    },
    "location": {
        "address": "address",
        "map_lat": "map_lat",
        "map_lng": "map_lng",
        "map_zoom": "map_zoom",
        "yandex_maps_url": "yandex_maps_url",
        "two_gis_url": "two_gis_url",
    },
    "legal": {"license_text": "license_text", "legal_entity_name": "legal_entity_name"},
    "analytics": {
        "metrika_id": "metrika_id",
        "ga4_id": "ga4_id",
        "yandex_verification": "yandex_verification",
        "google_verification": "google_verification",
    },
    "flags": {"prices_visible": "prices_visible", "booking_enabled": "booking_enabled"},
    "meta": {
        "default_meta_title": "default_meta_title",
        "default_meta_description": "default_meta_description",
    },
}
COLOR_FIELDS = {"brand_color", "accent_color", "ink_color", "surface_color"}
ASSET_FIELDS = ("logo", "logo_dark", "favicon", "hero_image", "og_image")


class Command(BaseCommand):
    help = "Prospekt config'i (YAML) bilan ClinicSettings'ni qayta brendlaydi (ADR-012)."

    def add_arguments(self, parser):
        parser.add_argument("--config", required=True, help="prospect.yml yoʻli")
        parser.add_argument(
            "--assets-dir",
            default=None,
            help="assets: dagi nisbiy yoʻllar uchun asosiy katalog (default: config yonida)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Faqat oʻzgarishlarni koʻrsatadi, yozmaydi.",
        )

    def handle(self, *args, **opts):
        cfg_path = Path(opts["config"])
        if not cfg_path.is_file():
            raise CommandError(f"Config topilmadi: {cfg_path}")
        try:
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:  # noqa: BLE001
            raise CommandError(f"YAML xatosi: {exc}") from exc
        if not isinstance(cfg, dict):
            raise CommandError("Config yuqori darajada map (dict) boʻlishi kerak.")

        assets_dir = Path(opts["assets_dir"]) if opts["assets_dir"] else cfg_path.parent
        dry = opts["dry_run"]

        # 1) Oddiy (rasm boʻlmagan) maydonlarni yigʻamiz + validatsiya
        updates: dict[str, object] = {}
        for section, mapping in FIELD_MAP.items():
            src = cfg if section == "_root" else cfg.get(section) or {}
            if not isinstance(src, dict):
                raise CommandError(f"`{section}` seksiyasi map boʻlishi kerak.")
            for key, field in mapping.items():
                if key not in src:
                    continue
                value = src[key]
                if field in COLOR_FIELDS and not HEX_RE.match(str(value)):
                    raise CommandError(f"`{section}.{key}` yaroqli hex rang emas: {value!r}")
                if field == "font_pair" and value not in FontPair.values:
                    raise CommandError(
                        f"`theme.font_pair` nomaʼlum: {value!r} (ruxsat: {FontPair.values})"
                    )
                updates[field] = value

        # 2) Rasm assetlarini tekshiramiz (mavjudligini oldindan)
        asset_paths: dict[str, Path] = {}
        assets_cfg = cfg.get("assets") or {}
        if not isinstance(assets_cfg, dict):
            raise CommandError("`assets` seksiyasi map boʻlishi kerak.")
        for field in ASSET_FIELDS:
            rel = assets_cfg.get(field)
            if not rel:
                continue
            p = Path(rel)
            if not p.is_absolute():
                p = assets_dir / p
            if not p.is_file():
                raise CommandError(f"`assets.{field}` fayli topilmadi: {p}")
            asset_paths[field] = p

        if not updates and not asset_paths:
            self.stdout.write(self.style.WARNING("Config boʻsh — oʻzgartiriladigan narsa yoʻq."))
            return

        settings = ClinicSettings.load()

        # 3) Farqni chiqaramiz (before → after)
        self.stdout.write(self.style.MIGRATE_HEADING("Reskin — oʻzgarishlar:"))
        for field, new in updates.items():
            old = getattr(settings, field)
            mark = "=" if str(old) == str(new) else "→"
            self.stdout.write(f"  {field}: {old!r} {mark} {new!r}")
        for field, p in asset_paths.items():
            self.stdout.write(f"  {field}: <rasm> → {p.name}")

        if dry:
            self.stdout.write(self.style.WARNING("\n--dry-run: hech narsa yozilmadi."))
            return

        # 4) Transaksiyada qoʻllaymiz
        with transaction.atomic():
            for field, value in updates.items():
                setattr(settings, field, value)
            for field, p in asset_paths.items():
                with p.open("rb") as fh:
                    getattr(settings, field).save(p.name, File(fh), save=False)
            settings.full_clean(exclude=list(ASSET_FIELDS))  # rasm cleanni oʻtkazamiz
            settings.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Reskin qoʻllandi — {settings.name}. "
                f"{len(updates)} maydon, {len(asset_paths)} rasm."
            )
        )
        self.stdout.write(
            "Frontend keshi: `make warm` yoki ISR revalidate (300s) kutib turing."
        )
