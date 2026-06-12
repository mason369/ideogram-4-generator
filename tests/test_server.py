from __future__ import annotations

from fastapi.testclient import TestClient

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
