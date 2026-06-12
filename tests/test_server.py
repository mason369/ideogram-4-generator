from __future__ import annotations

from fastapi.testclient import TestClient

from ideogram_tool.schemas import ExecutionMode, GeneratedImage, IdeogramResult
from ideogram_tool.server import create_app


def test_config_defaults_are_chinese_ui_compatible() -> None:
    client = TestClient(create_app())
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["defaults"]["execution_mode"] == "local_plain"
    assert data["defaults"]["seed"] == 0
    assert "2048x2048" in data["official_resolutions"]
    assert {"key": "portrait9x16", "width": 1152, "height": 2048} in data["canvas_presets"]
    assert {"key": "portrait9x16", "width": 1440, "height": 2560} in data["official_canvas_presets"]


def test_official_mode_accepts_v4_portrait_resolution(monkeypatch) -> None:
    def fake_generate(params, output_dir):
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
            request={"resolution": f"{params.width}x{params.height}"},
            optimized_prompt={"high_level_description": params.prompt},
            message="ok",
        )

    monkeypatch.setattr("ideogram_tool.server.generate_with_official_magic", fake_generate)
    client = TestClient(create_app())
    response = client.post(
        "/api/generate",
        json={
            "prompt": "portrait test",
            "width": 1440,
            "height": 2560,
            "execution_mode": "official_magic",
            "api_key": "test-key",
        },
    )
    assert response.status_code == 200
    assert response.json()["request"]["resolution"] == "1440x2560"


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
            "width": 1440,
            "height": 2560,
            "execution_mode": "official_magic",
            "api_key": "test-key",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["aspect_ratio"] == "9x16"
    assert data["request"]["prompt_flow"] == "official_magic_prompt_only"
