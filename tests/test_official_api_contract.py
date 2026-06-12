from __future__ import annotations

from ideogram_tool.validators import SAMPLER_TO_RENDERING_SPEED


def test_sampler_presets_map_to_official_rendering_speed() -> None:
    assert SAMPLER_TO_RENDERING_SPEED == {
        "V4_QUALITY_48": "QUALITY",
        "V4_DEFAULT_20": "DEFAULT",
        "V4_TURBO_12": "TURBO",
    }
