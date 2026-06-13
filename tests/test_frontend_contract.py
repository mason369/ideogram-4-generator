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
    assert "activeCanvasPresets" in source
    assert "creditCost" not in source
    assert "creditsBadge" not in source
    assert "official_canvas_presets" not in source
    api_source = (ROOT / "src" / "api.ts").read_text(encoding="utf-8")
    assert "/api/magic-prompt" in api_source
    assert "prompt: form.prompt.trim()" in api_source
    assert "竖版手机截图风格，原创角色星野铃，咖啡厅，galgame对话框" not in api_source
    assert "enable_copyright_detection" not in api_source


def test_language_packs_include_required_selector_text() -> None:
    source = (ROOT / "src" / "i18n" / "messages.ts").read_text(encoding="utf-8")
    for expected in ("Ideogram 4 图像生成器", "Ideogram 4 Generator", "官方提示词优化", "Official Magic Prompt"):
        assert expected in source
    assert "积分估算" not in source
    assert "credit estimate" not in source
    assert "完整原始请求" in source
