"""
CC0/CC rasmlarni Openverse API'dan yuklab, seed_assets/ ga tayyorlaydi (T-P3-04/05).

Openverse (WordPress) — kalitsiz CC qidiruv API'si; har natija uchun to'g'ridan-to'g'ri URL,
muallif va litsenziya beradi → attribution AVTOMATIK va rost bo'ladi ("litsenziya qatori yo'q,
merge yo'q" mexanik bo'ladi, T-P3-06).

Ishlash: har subyekt uchun aniq query → birinchi mos CC0 (yetарli o'lchamli) natija →
yuklab olish → cover-crop + JPEG q82 → seed_assets/ ga yozish → manifest.json ga qator.
Idempotent: mavjud fayl (mos o'lchamli) qayta yuklanmaydi.

`seed_assets/` COMMIT qilinadi (media/ .gitignore da). Bu — reproduksiya manbai.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

OPENVERSE = "https://api.openverse.org/v1/images/"
UA = "dental-demo-seed/1.0 (educational demo; contact ahmedovabay@gmail.com)"
ASSETS = Path(settings.BASE_DIR) / "apps" / "core" / "seed_assets"
MANIFEST = ASSETS / "manifest.json"

# Har subyekt: (rel_path, query, (w,h), model_release, subject)
# Shifokorlar — NIQOBLI/ish ustida (yuz berkitilgan; huquqiy jihatdan xavfsiz, R-1).
SUBJECTS: list[tuple[str, str, tuple[int, int], str, str]] = [
    # Hero (LCP) — keng, yorqin operatorxona
    ("hero/hero.jpg", "dentist chair clinic", (1600, 900), "n/a", "clinic operatory wide"),
    # 14 xizmat cover
    ("services/implantatsiya.jpg", "tooth implant", (1400, 933), "n/a", "implant model"),
    ("services/estetik-plombalash.jpg", "dentist composite filling", (1400, 933), "n/a", "filling"),
    ("services/professional-gigiyena.jpg", "teeth cleaning", (1400, 933), "n/a", "hygiene"),
    ("services/breketlar.jpg", "orthodontics braces", (1400, 933), "n/a", "braces"),
    ("services/ildiz-kanali-davolash.jpg", "dental treatment", (1400, 933), "n/a", "endodontics"),
    ("services/aqli-tish-olib-tashlash.jpg", "dental surgery instruments", (1400, 933), "n/a", "surgery tray"),
    ("services/karies-davolash.jpg", "dentist drill teeth", (1400, 933), "n/a", "caries"),
    ("services/tishlarni-oqartirish.jpg", "teeth whitening", (1400, 933), "n/a", "whitening"),
    ("services/suyak-toqimasi-tiklash.jpg", "dental xray", (1400, 933), "n/a", "cbct"),
    ("services/elayner.jpg", "clear dental aligner", (1400, 933), "n/a", "aligner"),
    ("services/bolalar-stomatologiyasi.jpg", "child teeth brushing", (1400, 933), "n/a", "pediatric"),
    ("services/vinirlar.jpg", "dental veneers", (1400, 933), "n/a", "veneers"),
    ("services/protezlash.jpg", "dental prosthesis crown", (1400, 933), "n/a", "prosthetics"),
    ("services/milk-kasalliklari-davolash.jpg", "dental examination", (1400, 933), "n/a", "gums"),
    # 5 shifokor — niqobli
    ("doctors/dilshod-raximov.jpg", "dentist patient chair", (1200, 1500), "none — demo only", "masked dentist"),
    ("doctors/nigora-yusupova.jpg", "dentist mask gloves", (1200, 1500), "none — demo only", "masked dentist"),
    ("doctors/kamola-ergasheva.jpg", "dentist face mask clinic", (1200, 1500), "none — demo only", "masked dentist"),
    ("doctors/sardor-toshmatov.jpg", "dentist working", (1200, 1500), "none — demo only", "masked dentist"),
    ("doctors/malika-qodirova.jpg", "dentist mask patient", (1200, 1500), "none — demo only", "masked dentist"),
    # 12 case (6 juft: before/after) — CC0 tabassum/tish
    ("cases/case1-before.jpg", "teeth closeup", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case1-after.jpg", "white smile teeth", (1200, 900), "none — demo only", "smile after"),
    ("cases/case2-before.jpg", "crooked teeth", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case2-after.jpg", "straight teeth smile", (1200, 900), "none — demo only", "smile after"),
    ("cases/case3-before.jpg", "dental patient mouth", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case3-after.jpg", "beautiful smile woman", (1200, 900), "none — demo only", "smile after"),
    ("cases/case4-before.jpg", "yellow teeth", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case4-after.jpg", "bright smile man", (1200, 900), "none — demo only", "smile after"),
    ("cases/case5-before.jpg", "dental checkup teeth", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case5-after.jpg", "healthy smile", (1200, 900), "none — demo only", "smile after"),
    ("cases/case6-before.jpg", "missing tooth", (1200, 900), "none — demo only", "teeth before"),
    ("cases/case6-after.jpg", "perfect smile teeth", (1200, 900), "none — demo only", "smile after"),
    # 12 galereya — 4 clinic, 4 equipment, 2 team, 2 work
    ("gallery/clinic-1.jpg", "clinic reception", (1400, 1050), "n/a", "reception"),
    ("gallery/clinic-2.jpg", "dental office interior", (1400, 1050), "n/a", "interior"),
    ("gallery/clinic-3.jpg", "dental waiting room", (1400, 1050), "n/a", "waiting"),
    ("gallery/clinic-4.jpg", "dental treatment room", (1400, 1050), "n/a", "operatory"),
    ("gallery/equipment-1.jpg", "dental chair equipment", (1400, 1050), "n/a", "chair"),
    ("gallery/equipment-2.jpg", "dental x-ray machine", (1400, 1050), "n/a", "x-ray"),
    ("gallery/equipment-3.jpg", "dental sterilizer tools", (1400, 1050), "n/a", "sterilizer"),
    ("gallery/equipment-4.jpg", "microscope", (1400, 1050), "n/a", "microscope"),
    ("gallery/team-1.jpg", "dental team clinic", (1400, 1050), "none — demo only", "team"),
    ("gallery/team-2.jpg", "dentist hands gloves work", (1400, 1050), "n/a", "hands at work"),
    ("gallery/work-1.jpg", "dental instruments closeup", (1400, 1050), "n/a", "instruments"),
    ("gallery/work-2.jpg", "dental impression mold", (1400, 1050), "n/a", "detail"),
    # 6 blog cover
    ("blog/implant-care.jpg", "dental implant care", (1400, 788), "n/a", "implant"),
    ("blog/kids-caries.jpg", "child brushing teeth", (1400, 788), "n/a", "kids"),
    ("blog/braces-aligners.jpg", "dental braces", (1400, 788), "n/a", "orthodontics"),
    ("blog/toothache.jpg", "tooth pain", (1400, 788), "n/a", "toothache"),
    ("blog/hygiene.jpg", "toothbrush dental hygiene", (1400, 788), "n/a", "hygiene"),
    ("blog/crowns.jpg", "dental crown", (1400, 788), "n/a", "crowns"),
]


class Command(BaseCommand):
    help = "CC0 rasmlarni Openverse'dan yuklab seed_assets/ ga tayyorlaydi."

    def add_arguments(self, parser):
        parser.add_argument("--only", help="faqat shu prefiks (masalan 'doctors/')", default="")
        parser.add_argument("--force", action="store_true", help="mavjud fayllarni ham qayta yuklash")

    def handle(self, *args, **opts):
        only = opts["only"]
        force = opts["force"]
        manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
        done = skipped = failed = 0

        for rel_path, query, target, model_release, subject in SUBJECTS:
            if only and not rel_path.startswith(only):
                continue
            dest = ASSETS / rel_path
            if dest.exists() and not force:
                skipped += 1
                continue
            try:
                meta = self._fetch_one(query, target, dest)
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"  ✗ {rel_path}: {exc}")
                failed += 1
                continue
            manifest[rel_path] = {
                "path": rel_path,
                "query": query,
                "subject": subject,
                "source_url": meta["foreign_landing_url"] or meta["url"],
                "direct_url": meta["url"],
                "author": meta.get("creator") or "unknown",
                "author_url": meta.get("creator_url") or "",
                "license": f"{meta.get('license', '')} {meta.get('license_version', '')}".strip(),
                "license_url": meta.get("license_url") or "",
                "source": meta.get("source") or "",
                "model_release": model_release,
                "target": list(target),
                "bytes": dest.stat().st_size,
            }
            done += 1
            self.stdout.write(f"  ✓ {rel_path}  ({meta.get('license')}, {meta.get('creator')})")
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
            time.sleep(0.4)  # Openverse'ga xushmuomala

        self.stdout.write(
            self.style.SUCCESS(f"tugadi: {done} yuklandi, {skipped} o'tkazildi, {failed} xato")
        )

    def _fetch_one(self, query: str, target: tuple[int, int], dest: Path) -> dict:
        """Openverse'dan eng katta mos natijani (CC0 yoki CC-BY) yuklab, cover-crop qiladi.
        CC-BY ham qabul qilinadi — attribution manifest'da avtomatik saqlanadi (rost)."""
        from io import BytesIO

        params = {"q": query, "license": "cc0,by", "page_size": 12, "mature": "false"}
        r = requests.get(OPENVERSE, params=params, headers={"User-Agent": UA}, timeout=25)
        r.raise_for_status()
        results = r.json().get("results", [])
        # Eng katta enlilardan boshlab urinamiz (sifat uchun).
        results.sort(key=lambda it: (it.get("width") or 0), reverse=True)
        tw, th = target
        for item in results:
            url = item.get("url")
            if not url:
                continue
            try:
                img_resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
                img_resp.raise_for_status()
                img = Image.open(BytesIO(img_resp.content))
                if img.width < 500 or img.height < 400:
                    continue  # juda kichik — sifat past
                img = ImageOps.exif_transpose(img).convert("RGB")
                img = ImageOps.fit(img, (tw, th), Image.LANCZOS)  # cover-crop (kerak bo'lsa upscale)
                dest.parent.mkdir(parents=True, exist_ok=True)
                img.save(dest, "JPEG", quality=82, optimize=True)
                return item
            except Exception:  # noqa: BLE001, S112
                continue
        raise RuntimeError(f"mos natija topilmadi: {query!r}")
