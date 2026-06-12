from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_split_release_asset_writes_parts_and_checksum(tmp_path: Path) -> None:
    asset = tmp_path / "bundle.zip"
    asset.write_bytes(b"abcdefghi")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "split_release_asset.py"),
            str(asset),
            "--max-size-bytes",
            "4",
        ],
        check=True,
        cwd=ROOT,
    )

    assert not asset.exists()
    parts = sorted(part for part in tmp_path.glob("bundle.zip.part*") if part.suffix != ".txt")
    assert [part.name for part in parts] == ["bundle.zip.part001", "bundle.zip.part002", "bundle.zip.part003"]
    assert b"".join(part.read_bytes() for part in parts) == b"abcdefghi"
    assert (tmp_path / "bundle.zip.sha256").exists()
    assert (tmp_path / "bundle.zip.parts.txt").exists()


def test_split_release_asset_keeps_small_asset_and_writes_checksum(tmp_path: Path) -> None:
    asset = tmp_path / "bundle.tar.gz"
    asset.write_bytes(b"abc")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "split_release_asset.py"),
            str(asset),
            "--max-size-bytes",
            "4",
        ],
        check=True,
        cwd=ROOT,
    )

    assert asset.exists()
    assert asset.read_bytes() == b"abc"
    assert (tmp_path / "bundle.tar.gz.sha256").exists()
    assert not (tmp_path / "bundle.tar.gz.parts.txt").exists()
