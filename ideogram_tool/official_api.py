from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from .schemas import GeneratedImage, IdeogramRequest, IdeogramResult, MagicPromptResult
from .validators import (
    SAMPLER_TO_RENDERING_SPEED,
    aspect_ratio_for_size,
    require_official_resolution,
)

API_BASE = "https://api.ideogram.ai"
MAGIC_PROMPT_URL = f"{API_BASE}/v1/ideogram-v4/magic-prompt"
GENERATE_URL = f"{API_BASE}/v1/ideogram-v4/generate"


class IdeogramApiError(RuntimeError):
    pass


def _api_key_from_request(api_key: str | None) -> str:
    resolved = (api_key or os.environ.get("IDEOGRAM_API_KEY") or "").strip()
    if not resolved:
        raise IdeogramApiError("official_magic mode requires an Ideogram API key")
    return resolved


def _raise_for_bad_response(response: requests.Response, label: str) -> None:
    if 200 <= response.status_code < 300:
        return
    body = response.text.strip()
    if len(body) > 2000:
        body = body[:2000] + "...[truncated]"
    raise IdeogramApiError(f"{label} failed with HTTP {response.status_code}: {body}")


def _safe_name(value: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-")
    return name or "image.png"


def _download_image(url: str, output_dir: Path, filename: str, api_key: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=180, headers={"Api-Key": api_key})
    if response.status_code == 401:
        response = requests.get(url, timeout=180)
    _raise_for_bad_response(response, "image download")
    path = output_dir / filename
    path.write_bytes(response.content)
    if path.stat().st_size == 0:
        raise IdeogramApiError(f"downloaded image is empty: {filename}")
    return path


def _magic_prompt(api_key: str, params: IdeogramRequest) -> dict[str, Any]:
    aspect_ratio = aspect_ratio_for_size(params.width, params.height)
    response = requests.post(
        MAGIC_PROMPT_URL,
        headers={"Api-Key": api_key, "Content-Type": "application/json"},
        json={"text_prompt": params.prompt, "aspect_ratio": aspect_ratio},
        timeout=180,
    )
    _raise_for_bad_response(response, "official Magic Prompt")
    data = response.json()
    json_prompt = data.get("json_prompt")
    if not isinstance(json_prompt, dict):
        raise IdeogramApiError(f"official Magic Prompt returned no json_prompt: {data}")
    return data


def optimize_prompt_with_official_magic(params: IdeogramRequest) -> MagicPromptResult:
    api_key = _api_key_from_request(params.api_key)
    magic = _magic_prompt(api_key, params)
    return MagicPromptResult(
        aspect_ratio=str(magic["aspect_ratio"]),
        optimized_prompt=magic["json_prompt"],
        request={
            "endpoint": MAGIC_PROMPT_URL,
            "prompt_flow": "official_magic_prompt_only",
            "aspect_ratio": magic["aspect_ratio"],
            "billing_note": "Magic Prompt is separate from image generation; it still requires an active API key.",
        },
        message="official Magic Prompt optimization completed",
    )


def generate_with_official_magic(params: IdeogramRequest, output_dir: Path) -> IdeogramResult:
    api_key = _api_key_from_request(params.api_key)
    resolution = require_official_resolution(params)
    magic = _magic_prompt(api_key, params)
    json_prompt = magic["json_prompt"]
    rendering_speed = SAMPLER_TO_RENDERING_SPEED[params.sampler_preset]

    images: list[GeneratedImage] = []
    for index in range(params.candidate_count):
        form: dict[str, str] = {
            "json_prompt": json.dumps(json_prompt, ensure_ascii=False, separators=(",", ":")),
            "resolution": resolution,
            "rendering_speed": rendering_speed,
        }
        if params.enable_copyright_detection is not None:
            form["enable_copyright_detection"] = "true" if params.enable_copyright_detection else "false"
        multipart = {key: (None, value) for key, value in form.items()}
        response = requests.post(
            GENERATE_URL,
            headers={"Api-Key": api_key},
            files=multipart,
            timeout=600,
        )
        _raise_for_bad_response(response, "official Ideogram 4 generation")
        payload = response.json()
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise IdeogramApiError(f"official Ideogram 4 returned no data: {payload}")
        image = data[0]
        if not image.get("is_image_safe", False):
            raise IdeogramApiError("official Ideogram 4 marked the generated image as unsafe")
        url = image.get("url")
        if not isinstance(url, str) or not url:
            raise IdeogramApiError(f"official Ideogram 4 returned no usable image URL: {image}")
        url_name = Path(urlparse(url).path).name
        filename = _safe_name(f"official-{index + 1:02d}-{url_name or 'image.png'}")
        saved = _download_image(url, output_dir, filename, api_key)
        images.append(
            GeneratedImage(
                url=f"/outputs/{saved.name}",
                filename=saved.name,
                seed=image.get("seed"),
                prompt=image.get("prompt"),
                resolution=image.get("resolution"),
            )
        )

    return IdeogramResult(
        mode=params.execution_mode,
        images=images,
        optimized_prompt=json_prompt,
        request={
            "endpoint": GENERATE_URL,
            "prompt_flow": "official_magic_prompt_then_json_prompt",
            "resolution": resolution,
            "rendering_speed": rendering_speed,
            "candidate_count": params.candidate_count,
            "seed_note": "Official Ideogram v4 API docs do not expose request seed; returned seeds are recorded per image.",
        },
        message="official Ideogram 4 API generation completed",
    )
