from __future__ import annotations

import pytest

from ideogram_tool.validators import (
    CANVAS_PRESETS,
    aspect_ratio_for_size,
    normalize_json_prompt_order,
    normalize_seed,
    validate_dimensions,
)


def test_dimensions_follow_telknet_rules() -> None:
    validate_dimensions(2048, 512)
    with pytest.raises(ValueError, match="multiple of 16"):
        validate_dimensions(1025, 1024)
    with pytest.raises(ValueError, match="between 1:6"):
        validate_dimensions(2048, 256)


def test_zero_seed_is_randomized_and_candidate_range_is_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr("ideogram_tool.validators.secrets.randbelow", lambda upper: calls.append(upper) or 41)
    assert normalize_seed(0, 4) == 42
    assert calls == [2147483644]
    with pytest.raises(ValueError, match="seed range exceeds"):
        normalize_seed(2147483647, 2)


def test_canvas_presets_are_local_cuda_and_magic_prompt_compatible() -> None:
    assert {"key": "portrait9x16", "width": 1152, "height": 2048} in CANVAS_PRESETS
    assert {"key": "poster2x3", "width": 1344, "height": 2016} in CANVAS_PRESETS
    for preset in CANVAS_PRESETS:
        validate_dimensions(preset["width"], preset["height"])
        assert aspect_ratio_for_size(preset["width"], preset["height"])


def test_magic_aspect_bucket_is_strict() -> None:
    assert aspect_ratio_for_size(2048, 2048) == "1x1"
    assert aspect_ratio_for_size(1152, 2048) == "9x16"
    with pytest.raises(ValueError, match="supported aspect ratio"):
        aspect_ratio_for_size(1360, 2048)


def test_json_prompt_order_is_normalized_for_ideogram4_verifier() -> None:
    prompt = {
        "compositional_deconstruction": {
            "elements": [
                {"desc": "hero", "type": "obj"},
                {"desc": "caption", "text": "你好", "type": "text"},
            ],
            "background": "room",
        },
        "style_description": {
            "color_palette": ["#FFFFFF"],
            "medium": "photo",
            "photo": "portrait",
            "lighting": "soft",
            "aesthetics": "warm",
        },
        "high_level_description": "test",
    }

    normalized = normalize_json_prompt_order(prompt)

    assert list(normalized) == ["high_level_description", "style_description", "compositional_deconstruction"]
    assert list(normalized["style_description"]) == ["aesthetics", "lighting", "photo", "medium", "color_palette"]
    assert list(normalized["compositional_deconstruction"]) == ["background", "elements"]
    assert list(normalized["compositional_deconstruction"]["elements"][0]) == ["type", "desc"]
    assert list(normalized["compositional_deconstruction"]["elements"][1]) == ["type", "text", "desc"]
