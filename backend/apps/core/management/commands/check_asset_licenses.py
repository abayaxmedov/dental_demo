"""
Har bir seed_assets/ fayli manifest.json va ASSETS_LICENSES.md da qatorga ega ekanini
tekshiradi (T-P3-06). "Litsenziya qatori yoʻq — merge yoʻq" (R-06) shu bilan MEXANIK boʻladi.
CI/make be-test'da ishlaydi; xato bo'lsa non-zero exit.
"""
from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

ASSETS = Path(settings.BASE_DIR) / "apps" / "core" / "seed_assets"
MANIFEST = ASSETS / "manifest.json"
LICENSES_MD = Path(settings.BASE_DIR).parent / "ASSETS_LICENSES.md"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"}
REQUIRED = ("source_url", "author", "license")


class Command(BaseCommand):
    help = "seed_assets/ fayllarining litsenziya qatorlarini tekshiradi."

    def handle(self, *args, **opts):
        if not ASSETS.exists():
            self.stdout.write("seed_assets/ yo'q — o'tkazildi")
            return
        manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
        md_text = LICENSES_MD.read_text() if LICENSES_MD.exists() else ""

        files = sorted(
            p.relative_to(ASSETS).as_posix()
            for p in ASSETS.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS
        )
        problems: list[str] = []
        for rel in files:
            row = manifest.get(rel)
            if not row:
                problems.append(f"{rel}: manifest.json da qator yo'q")
                continue
            for key in REQUIRED:
                if not row.get(key):
                    problems.append(f"{rel}: manifest'da '{key}' bo'sh")
            # ASSETS_LICENSES.md da fayl nomi eslatilganmi
            if rel not in md_text:
                problems.append(f"{rel}: ASSETS_LICENSES.md da yo'q")

        if problems:
            for p in problems:
                self.stderr.write(f"  ✗ {p}")
            raise CommandError(f"{len(problems)} ta litsenziya muammosi ({len(files)} fayldan)")
        self.stdout.write(self.style.SUCCESS(f"✓ {len(files)} fayl — hammasi litsenziyalangan"))
