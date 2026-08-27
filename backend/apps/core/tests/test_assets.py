"""seed_assets litsenziya gate testi (T-P3-06). "Litsenziya qatori yoʻq — merge yoʻq"."""
import pytest
from django.core.management import CommandError, call_command


def test_all_assets_are_licensed():
    """check_asset_licenses xatosiz oʻtishi kerak (har fayl manifest + ASSETS_LICENSES.md da)."""
    call_command("check_asset_licenses")  # xato bo'lsa CommandError -> test yiqiladi


def test_gate_catches_unlicensed(tmp_path, monkeypatch):
    """Manifestda yoʻq fayl gate'ni yiqitishini tasdiqlaymiz."""
    from apps.core.management.commands import check_asset_licenses as mod

    fake = tmp_path / "seed_assets"
    (fake / "services").mkdir(parents=True)
    (fake / "services" / "orphan.jpg").write_bytes(b"\xff\xd8\xff")  # litsenziyasiz
    (fake / "manifest.json").write_text("{}")
    monkeypatch.setattr(mod, "ASSETS", fake)
    monkeypatch.setattr(mod, "MANIFEST", fake / "manifest.json")
    monkeypatch.setattr(mod, "LICENSES_MD", tmp_path / "ASSETS_LICENSES.md")
    (tmp_path / "ASSETS_LICENSES.md").write_text("# bo'sh")
    with pytest.raises(CommandError):
        call_command("check_asset_licenses")
