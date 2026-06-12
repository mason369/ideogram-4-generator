from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    local_plain = "local_plain"
    local_json = "local_json"
    official_magic = "official_magic"


class IdeogramRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    width: int = 2048
    height: int = 2048
    sampler_preset: Literal["V4_QUALITY_48", "V4_DEFAULT_20", "V4_TURBO_12"] = "V4_QUALITY_48"
    seed: int = Field(default=0, ge=0, le=2147483647)
    candidate_count: int = Field(default=1, ge=1, le=4)
    execution_mode: ExecutionMode = ExecutionMode.local_plain
    api_key: str | None = None
    enable_copyright_detection: bool | None = None


class GeneratedImage(BaseModel):
    url: str
    filename: str
    seed: int | None = None
    prompt: str | None = None
    resolution: str | None = None


class IdeogramResult(BaseModel):
    mode: ExecutionMode
    images: list[GeneratedImage]
    request: dict[str, Any]
    optimized_prompt: dict[str, Any] | str | None = None
    message: str


class MagicPromptResult(BaseModel):
    aspect_ratio: str
    optimized_prompt: dict[str, Any]
    request: dict[str, Any]
    message: str


class AppConfig(BaseModel):
    defaults: dict[str, Any]
    canvas_presets: list[dict[str, Any]]
    official_canvas_presets: list[dict[str, Any]]
    sampler_presets: list[str]
    candidate_counts: list[int]
    official_resolutions: list[str]
