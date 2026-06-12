from __future__ import annotations

import json
import secrets
from math import gcd
from typing import Any

from .schemas import IdeogramRequest

IDEOGRAM_DIMENSION_MIN = 256
IDEOGRAM_DIMENSION_MAX = 2048
IDEOGRAM_DIMENSION_STEP = 16
IDEOGRAM_MAX_ASPECT_RATIO = 6
MAX_IDEOGRAM_SEED = 2147483647

SAMPLER_PRESETS = ["V4_QUALITY_48", "V4_DEFAULT_20", "V4_TURBO_12"]
CANDIDATE_COUNTS = [1, 2, 3, 4]

CANVAS_PRESETS = [
    {"key": "square2k", "width": 2048, "height": 2048},
    {"key": "portrait9x16", "width": 1152, "height": 2048},
    {"key": "landscape16x9", "width": 2048, "height": 1152},
    {"key": "poster2x3", "width": 1360, "height": 2048},
    {"key": "wide4x1", "width": 2048, "height": 512},
    {"key": "tall1x4", "width": 512, "height": 2048},
]

OFFICIAL_CANVAS_PRESETS = [
    {"key": "square2k", "width": 2048, "height": 2048},
    {"key": "portrait9x16", "width": 1440, "height": 2560},
    {"key": "landscape16x9", "width": 2560, "height": 1440},
    {"key": "poster2x3", "width": 1600, "height": 2560},
    {"key": "wide4x1", "width": 2880, "height": 1440},
    {"key": "tall1x4", "width": 1440, "height": 2880},
]

OFFICIAL_V4_RESOLUTIONS = [
    "2048x2048",
    "1440x2880",
    "2880x1440",
    "1664x2496",
    "2496x1664",
    "1792x2240",
    "2240x1792",
    "1440x2560",
    "2560x1440",
    "1600x2560",
    "2560x1600",
    "1728x2304",
    "2304x1728",
    "1296x3168",
    "3168x1296",
    "1152x2944",
    "2944x1152",
    "1248x3328",
    "3328x1248",
    "1280x3072",
    "3072x1280",
    "1024x3072",
    "3072x1024",
]

OFFICIAL_MAGIC_ASPECTS = {
    "1x4",
    "1x3",
    "1x2",
    "9x16",
    "10x16",
    "2x3",
    "3x4",
    "4x5",
    "1x1",
    "5x4",
    "4x3",
    "3x2",
    "16x10",
    "16x9",
    "2x1",
    "3x1",
    "4x1",
}

SAMPLER_TO_RENDERING_SPEED = {
    "V4_QUALITY_48": "QUALITY",
    "V4_DEFAULT_20": "DEFAULT",
    "V4_TURBO_12": "TURBO",
}


def validate_dimensions(width: int, height: int) -> None:
    for label, value in (("width", width), ("height", height)):
        if value < IDEOGRAM_DIMENSION_MIN or value > IDEOGRAM_DIMENSION_MAX:
            raise ValueError(
                f"{label} must be between {IDEOGRAM_DIMENSION_MIN} and {IDEOGRAM_DIMENSION_MAX}"
            )
        if value % IDEOGRAM_DIMENSION_STEP != 0:
            raise ValueError(f"{label} must be a multiple of {IDEOGRAM_DIMENSION_STEP}")
    ratio = max(width / height, height / width)
    if ratio > IDEOGRAM_MAX_ASPECT_RATIO:
        raise ValueError(
            f"width and height aspect ratio must be between 1:{IDEOGRAM_MAX_ASPECT_RATIO} "
            f"and {IDEOGRAM_MAX_ASPECT_RATIO}:1"
        )


def normalize_seed(seed: int, candidate_count: int) -> int:
    if seed < 0 or seed > MAX_IDEOGRAM_SEED:
        raise ValueError(f"seed must be between 0 and {MAX_IDEOGRAM_SEED}")
    if seed == 0:
        return secrets.randbelow(MAX_IDEOGRAM_SEED - candidate_count + 1) + 1
    if seed + candidate_count - 1 > MAX_IDEOGRAM_SEED:
        raise ValueError(f"seed range exceeds {MAX_IDEOGRAM_SEED} for the selected candidate count")
    return seed


def resolution_for_request(params: IdeogramRequest) -> str:
    return f"{params.width}x{params.height}"


def require_official_resolution(params: IdeogramRequest) -> str:
    resolution = resolution_for_request(params)
    if resolution not in OFFICIAL_V4_RESOLUTIONS:
        raise ValueError(
            "official Ideogram API v4 accepts a fixed resolution list; "
            f"{resolution} is not supported. Supported values: {', '.join(OFFICIAL_V4_RESOLUTIONS)}"
        )
    return resolution


def aspect_ratio_for_size(width: int, height: int) -> str:
    divisor = gcd(max(1, width), max(1, height))
    ratio = f"{width // divisor}x{height // divisor}"
    if ratio not in OFFICIAL_MAGIC_ASPECTS:
        raise ValueError(
            "official Magic Prompt v4 requires a supported aspect ratio bucket; "
            f"{ratio} is not supported. Supported values: {', '.join(sorted(OFFICIAL_MAGIC_ASPECTS))}"
        )
    return ratio


def parse_json_prompt(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"local_json mode requires valid JSON prompt: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("local_json mode requires a JSON object")
    if "high_level_description" not in parsed or "compositional_deconstruction" not in parsed:
        raise ValueError(
            "local_json mode requires Ideogram 4 fields: high_level_description and compositional_deconstruction"
        )
    return parsed
