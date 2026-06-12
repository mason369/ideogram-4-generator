from __future__ import annotations

import argparse
import os
from pathlib import Path


TOKEN_FILE_NAMES = {
    "token",
    "stored_tokens",
    "hf_token",
    ".hf_token",
}


def remove_auth_files(cache_dir: Path) -> list[Path]:
    removed: list[Path] = []
    if not cache_dir.exists():
        return removed
    for path in cache_dir.rglob("*"):
        if path.is_file() and path.name.lower() in TOKEN_FILE_NAMES:
            path.unlink()
            removed.append(path)
    return removed


def verify_token_absent(cache_dir: Path, token: str, max_scan_bytes: int) -> None:
    if not token or not cache_dir.exists():
        return
    token_bytes = token.encode()
    for path in cache_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.stat().st_size > max_scan_bytes:
            continue
        data = path.read_bytes()
        if token_bytes in data:
            raise SystemExit(f"secret token material found in cache file: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default="models/hf-cache")
    parser.add_argument("--max-scan-mib", type=int, default=10)
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir)
    token = os.environ.get("HF_TOKEN", "")
    removed = remove_auth_files(cache_dir)
    verify_token_absent(cache_dir, token, args.max_scan_mib * 1024 * 1024)
    print(f"sanitized Hugging Face cache: {cache_dir}")
    if removed:
        print(f"removed auth files: {len(removed)}")


if __name__ == "__main__":
    main()
