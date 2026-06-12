from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_requires_hf_token_for_weighted_package() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "HF_TOKEN" in workflow
    assert "Verify model download token is configured" in workflow
    assert "download_ideogram_weights.py" in workflow
    assert "sanitize_hf_cache.py" in workflow
    assert "Verify bundled model cache exists" in workflow
    assert "IDEOGRAM_STRICT_BUNDLE" in workflow
    assert "split_release_asset.py" in workflow
    assert ".part001" in workflow
    assert "Ideogram4Generator-Windows-GPU-CUDA-NF4-Portable" in workflow
    assert "Ideogram4Generator-Linux-GPU-CUDA-NF4-Portable" in workflow
    assert "end users do not need to download the model manually" in workflow


def test_build_workflow_runs_tests_and_frontend_build() -> None:
    workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow
    assert "ubuntu-22.04" in workflow
    assert "npm run build" in workflow
    assert "pytest -q" in workflow
