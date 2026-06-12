from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sanitize_hf_cache_removes_auth_files(tmp_path: Path) -> None:
    cache = tmp_path / "hf-cache"
    cache.mkdir()
    (cache / "token").write_text("secret", encoding="utf-8")
    (cache / "model.bin").write_bytes(b"not-a-secret")

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "sanitize_hf_cache.py"), "--cache-dir", str(cache)],
        check=True,
        cwd=ROOT,
    )

    assert not (cache / "token").exists()
    assert (cache / "model.bin").exists()


def test_sanitize_hf_cache_fails_if_token_material_is_present(tmp_path: Path) -> None:
    cache = tmp_path / "hf-cache"
    cache.mkdir()
    (cache / "metadata.json").write_text('{"token": "hf_secret_value"}', encoding="utf-8")
    env = os.environ.copy()
    env["HF_TOKEN"] = "hf_secret_value"

    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "sanitize_hf_cache.py"), "--cache-dir", str(cache)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "hf_secret_value" not in result.stdout
    assert "hf_secret_value" not in result.stderr
