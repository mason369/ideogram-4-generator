from __future__ import annotations

import os
import json
from pathlib import Path

import pytest

from ideogram_tool.local_cuda import LocalRuntimeError, generate_with_local_cuda
from ideogram_tool.schemas import ExecutionMode, IdeogramRequest


def _request() -> IdeogramRequest:
    return IdeogramRequest(
        prompt="local cache test",
        width=512,
        height=512,
        sampler_preset="V4_TURBO_12",
        seed=123,
        candidate_count=1,
        execution_mode=ExecutionMode.local_plain,
    )


def test_local_cuda_sets_offline_hf_cache_before_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cache = tmp_path / "hf-cache"
    (cache / "hub").mkdir(parents=True)
    output_dir = tmp_path / "outputs"
    captured_env: dict[str, str | None] = {}
    captured_payload: dict[str, object] = {}

    monkeypatch.setenv("IDEOGRAM_HF_CACHE", str(cache))
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.delenv("TRANSFORMERS_OFFLINE", raising=False)

    def fake_run_payload(payload):
        captured_payload.update(payload)
        for key in ("HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
            captured_env[key] = os.environ.get(key)
        output_path = Path(payload["output_dir"]) / "local-candidate-01-seed-123.png"
        output_path.write_bytes(b"not-empty")
        return {"files": [str(output_path)]}

    monkeypatch.setattr("ideogram_tool.local_worker.run_payload", fake_run_payload)

    result = generate_with_local_cuda(_request(), output_dir)

    assert result.request["prompt_flow"] == "plain_prompt_wrapped_as_local_json_without_official_magic_prompt"
    assert captured_payload["is_structured"] is True
    runtime_prompt = json.loads(str(captured_payload["prompt"]))
    assert runtime_prompt["high_level_description"] == "local cache test"
    assert "art_style" in runtime_prompt["style_description"]
    assert isinstance(runtime_prompt["style_description"]["color_palette"], list)
    assert isinstance(runtime_prompt["compositional_deconstruction"]["background"], str)
    assert runtime_prompt["compositional_deconstruction"]["elements"][0]["type"] == "obj"
    assert runtime_prompt["compositional_deconstruction"]["elements"][0]["desc"] == "local cache test"
    assert captured_env == {
        "HF_HOME": str(cache),
        "HF_HUB_CACHE": str(cache / "hub"),
        "HUGGINGFACE_HUB_CACHE": str(cache / "hub"),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    }
    assert os.environ["HF_HUB_OFFLINE"] == "0"
    assert os.environ.get("TRANSFORMERS_OFFLINE") is None


def test_local_cuda_fails_when_model_cache_is_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("IDEOGRAM_HF_CACHE", str(tmp_path / "missing-cache"))

    with pytest.raises(LocalRuntimeError, match="model cache not found"):
        generate_with_local_cuda(_request(), tmp_path / "outputs")
