from __future__ import annotations

import os
from typing import Any

import requests

from .schemas import IdeogramRequest, MagicPromptResult
from .validators import aspect_ratio_for_size

API_BASE = "https://api.ideogram.ai"
MAGIC_PROMPT_URL = f"{API_BASE}/v1/ideogram-v4/magic-prompt"


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
            "billing_note": "Magic Prompt is the only official Ideogram API call in this project; image generation runs locally.",
        },
        message="official Magic Prompt optimization completed",
    )
