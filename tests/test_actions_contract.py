from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_requires_hf_token_for_weighted_package() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "HF_TOKEN" in workflow
    assert "download_ideogram_weights.py" in workflow
    assert "Ideogram4Generator-Linux-GPU-Portable" in workflow


def test_build_workflow_runs_tests_and_frontend_build() -> None:
    workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    assert "npm run build" in workflow
    assert "pytest -q" in workflow
