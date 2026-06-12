from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_exposes_seed_input_and_random_button() -> None:
    source = (ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "randomSeed()" in source
    assert "Dices" in source
    assert 'update("seed", randomSeed())' in source
    assert "2147483647" in source
    assert 'placeholder="123456789"' in source
    assert 'aria-label={t("randomSeed")}' in source
    assert "optimizeOnly" in source
    assert "official_canvas_presets" in source
    assert "activeCanvasPresets" in source
    assert "/api/magic-prompt" in (ROOT / "src" / "api.ts").read_text(encoding="utf-8")


def test_language_packs_include_required_selector_text() -> None:
    source = (ROOT / "src" / "i18n" / "messages.ts").read_text(encoding="utf-8")
    for expected in ("Ideogram 4 图像生成器", "Ideogram 4 Generator", "官方提示词优化", "Official Magic Prompt"):
        assert expected in source
