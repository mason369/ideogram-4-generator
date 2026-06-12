from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ideogram_tool.official_api import GENERATE_URL, generate_with_official_magic
from ideogram_tool.schemas import IdeogramRequest
from ideogram_tool.validators import SAMPLER_TO_RENDERING_SPEED


def test_sampler_presets_map_to_official_rendering_speed() -> None:
    assert SAMPLER_TO_RENDERING_SPEED == {
        "V4_QUALITY_48": "QUALITY",
        "V4_DEFAULT_20": "DEFAULT",
        "V4_TURBO_12": "TURBO",
    }


def test_official_generate_uses_multipart_form(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[dict[str, Any]] = []

    class Response:
        status_code = 200
        content = b"png"
        text = ""

        def __init__(self, payload: dict[str, Any] | None = None) -> None:
            self._payload = payload or {}

        def json(self) -> dict[str, Any]:
            return self._payload

    def fake_post(url: str, **kwargs: Any) -> Response:
        calls.append({"url": url, **kwargs})
        if "magic-prompt" in url:
            return Response({"json_prompt": {"high_level_description": "x", "compositional_deconstruction": []}})
        return Response({"data": [{"is_image_safe": True, "url": "https://example.test/result.png"}]})

    monkeypatch.setattr("ideogram_tool.official_api.requests.post", fake_post)
    monkeypatch.setattr("ideogram_tool.official_api.requests.get", lambda *args, **kwargs: Response())

    generate_with_official_magic(
        IdeogramRequest(
            prompt="x",
            width=1440,
            height=2560,
            sampler_preset="V4_TURBO_12",
            execution_mode="official_magic",
            api_key="test-key",
        ),
        tmp_path,
    )

    generate_call = next(call for call in calls if call["url"] == GENERATE_URL)
    assert "files" in generate_call
    assert "data" not in generate_call
    assert generate_call["files"]["resolution"] == (None, "1440x2560")
