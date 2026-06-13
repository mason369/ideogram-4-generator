from __future__ import annotations

import json
import secrets
from math import gcd
from typing import Any

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
    {"key": "poster2x3", "width": 1344, "height": 2016},
    {"key": "wide4x1", "width": 2048, "height": 512},
    {"key": "tall1x4", "width": 512, "height": 2048},
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
    return normalize_json_prompt_order(parsed)


def _ordered_dict(source: dict[str, Any], preferred_order: list[str]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for key in preferred_order:
        if key in source:
            ordered[key] = source[key]
    for key, value in source.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _normalize_style_description(style_description: Any) -> Any:
    if not isinstance(style_description, dict):
        return style_description
    if "photo" in style_description:
        return _ordered_dict(style_description, ["aesthetics", "lighting", "photo", "medium", "color_palette"])
    return _ordered_dict(style_description, ["aesthetics", "lighting", "medium", "art_style", "color_palette"])


def _normalize_element(element: Any) -> Any:
    if not isinstance(element, dict):
        return element
    if element.get("type") == "text":
        return _ordered_dict(element, ["type", "bbox", "text", "desc", "color_palette"])
    return _ordered_dict(element, ["type", "bbox", "desc", "color_palette"])


def _normalize_compositional_deconstruction(compositional_deconstruction: Any) -> Any:
    if not isinstance(compositional_deconstruction, dict):
        return compositional_deconstruction
    normalized = dict(compositional_deconstruction)
    elements = normalized.get("elements")
    if isinstance(elements, list):
        normalized["elements"] = [_normalize_element(element) for element in elements]
    return _ordered_dict(normalized, ["background", "elements"])


def normalize_json_prompt_order(prompt: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(prompt)
    if "style_description" in normalized:
        normalized["style_description"] = _normalize_style_description(normalized["style_description"])
    if "compositional_deconstruction" in normalized:
        normalized["compositional_deconstruction"] = _normalize_compositional_deconstruction(
            normalized["compositional_deconstruction"]
        )
    return _ordered_dict(normalized, ["high_level_description", "style_description", "compositional_deconstruction"])
