from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_requires_hf_token_for_weighted_package() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "HF_TOKEN" in workflow
    assert "max-parallel: 1" in workflow
    assert "Verify model download token is configured" in workflow
    assert "download_ideogram_weights.py" in workflow
    assert "sanitize_hf_cache.py" in workflow
    assert "Verify bundled model cache exists" in workflow
    assert "IDEOGRAM_STRICT_BUNDLE" in workflow
    assert "Create portable package" in workflow
    assert "Smoke test portable package" in workflow
    assert "Compress portable package" in workflow
    assert "upload_asset_with_retry" in workflow
    assert "Create release if missing" in workflow
    assert "Upload assets to release" in workflow
    assert "Free Linux runner disk space" in workflow
    assert "Clear package caches before model bundling" in workflow
    assert "HF_HUB_DISABLE_XET" in workflow
    assert "7z a" in workflow
    assert "-v1900m" in workflow
    assert 'split -b 1900M - "${PKG}.tar.gz.part"' in workflow
    assert "Ideogram4Generator-Windows-GPU-CUDA-NF4-Portable" in workflow
    assert "Ideogram4Generator-Linux-GPU-CUDA-NF4-Portable" in workflow
    assert "AI 模型已内置，无需额外下载" in workflow
    assert "官方接口只用于 Magic Prompt 提示词优化；图片由本地 CUDA 生成" in workflow
    assert "split_release_asset.py" not in workflow
    downloader = (ROOT / "tools" / "download_ideogram_weights.py").read_text(encoding="utf-8")
    assert "max_workers=2" in downloader
    assert "--retries" in downloader
    assert "429" in downloader


def test_build_workflow_runs_tests_and_frontend_build() -> None:
    workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow
    assert "ubuntu-22.04" in workflow
    assert "npm run build" in workflow
    assert "pytest -q" in workflow
