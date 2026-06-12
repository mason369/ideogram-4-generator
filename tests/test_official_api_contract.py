from __future__ import annotations

from typing import Any

import pytest

from ideogram_tool.official_api import MAGIC_PROMPT_URL, optimize_prompt_with_official_magic
from ideogram_tool.schemas import IdeogramRequest


def test_official_magic_prompt_posts_json_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    class Response:
        status_code = 200
        text = ""

        def json(self) -> dict[str, Any]:
            return {
                "aspect_ratio": "9x16",
                "json_prompt": {
                    "high_level_description": "x",
                    "compositional_deconstruction": [],
                },
            }

    def fake_post(url: str, **kwargs: Any) -> Response:
        calls.append({"url": url, **kwargs})
        return Response()

    monkeypatch.setattr("ideogram_tool.official_api.requests.post", fake_post)

    result = optimize_prompt_with_official_magic(
        IdeogramRequest(
            prompt="x",
            width=1152,
            height=2048,
            sampler_preset="V4_TURBO_12",
            execution_mode="official_magic",
            api_key="test-key",
        )
    )

    assert len(calls) == 1
    assert calls[0]["url"] == MAGIC_PROMPT_URL
    assert calls[0]["json"] == {"text_prompt": "x", "aspect_ratio": "9x16"}
    assert "files" not in calls[0]
    assert result.request["prompt_flow"] == "official_magic_prompt_only"
