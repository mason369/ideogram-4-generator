from __future__ import annotations

from fastapi.testclient import TestClient

from ideogram_tool.schemas import ExecutionMode, GeneratedImage, IdeogramResult, MagicPromptResult
from ideogram_tool.server import create_app


def test_config_defaults_are_chinese_ui_compatible() -> None:
    client = TestClient(create_app())
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["defaults"]["execution_mode"] == "local_plain"
    assert data["defaults"]["seed"] == 0
    assert {"key": "portrait9x16", "width": 1152, "height": 2048} in data["canvas_presets"]
    assert "official_resolutions" not in data
    assert "official_canvas_presets" not in data


def test_official_mode_optimizes_prompt_then_runs_local_cuda(monkeypatch) -> None:
    optimized_prompt = {
        "high_level_description": "portrait test",
        "compositional_deconstruction": [],
    }

    def fake_optimize(params):
        assert params.width == 1152
        assert params.height == 2048
        return MagicPromptResult(
            aspect_ratio="9x16",
            optimized_prompt=optimized_prompt,
            request={"prompt_flow": "official_magic_prompt_only"},
            message="ok",
        )

    def fake_generate(params, output_dir, *, optimized_prompt=None, prompt_flow=None):
        assert optimized_prompt == {
            "high_level_description": "portrait test",
            "compositional_deconstruction": [],
        }
        assert prompt_flow == "official_magic_prompt_then_local_cuda"
        return IdeogramResult(
            mode=ExecutionMode.official_magic,
            images=[
                GeneratedImage(
                    url="/outputs/test.png",
                    filename="test.png",
                    seed=None,
                    prompt=params.prompt,
                    resolution=f"{params.width}x{params.height}",
                )
            ],
            request={"prompt_flow": prompt_flow, "resolution": f"{params.width}x{params.height}"},
            optimized_prompt=optimized_prompt,
            message="ok",
        )

    monkeypatch.setattr("ideogram_tool.server.optimize_prompt_with_official_magic", fake_optimize)
    monkeypatch.setattr("ideogram_tool.server.generate_with_local_cuda", fake_generate)
    client = TestClient(create_app())
    response = client.post(
        "/api/generate",
        json={
            "prompt": "portrait test",
            "width": 1152,
            "height": 2048,
            "execution_mode": "official_magic",
            "api_key": "test-key",
        },
    )
    assert response.status_code == 200
    assert response.json()["request"]["prompt_flow"] == "official_magic_prompt_then_local_cuda"
    assert response.json()["request"]["resolution"] == "1152x2048"


def test_magic_prompt_endpoint_only_optimizes(monkeypatch) -> None:
    def fake_optimize(params):
        return {
            "aspect_ratio": "9x16",
            "optimized_prompt": {
                "high_level_description": params.prompt,
                "compositional_deconstruction": {},
            },
            "request": {"prompt_flow": "official_magic_prompt_only"},
            "message": "ok",
        }

    monkeypatch.setattr("ideogram_tool.server.optimize_prompt_with_official_magic", fake_optimize)
    client = TestClient(create_app())
    response = client.post(
        "/api/magic-prompt",
        json={
            "prompt": "portrait test",
            "width": 1152,
            "height": 2048,
            "execution_mode": "official_magic",
            "api_key": "test-key",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["aspect_ratio"] == "9x16"
    assert data["request"]["prompt_flow"] == "official_magic_prompt_only"
