from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_asset(path: Path, max_size: int) -> list[Path]:
    if not path.exists():
        raise SystemExit(f"release asset does not exist: {path}")
    if path.stat().st_size <= max_size:
        return [path]
    parts: list[Path] = []
    with path.open("rb") as source:
        index = 1
        while True:
            first_chunk = source.read(min(max_size, 8 * 1024 * 1024))
            if not first_chunk:
                break
            part = path.with_name(f"{path.name}.part{index:03d}")
            written = 0
            with part.open("wb") as target:
                target.write(first_chunk)
                written += len(first_chunk)
                while written < max_size:
                    chunk = source.read(min(max_size - written, 8 * 1024 * 1024))
                    if not chunk:
                        break
                    target.write(chunk)
                    written += len(chunk)
            parts.append(part)
            index += 1
    path.unlink()
    return parts


def write_metadata(original_path: Path, original_sha: str, parts: list[Path]) -> None:
    sha_lines = [f"{original_sha}  {original_path.name}"]
    sha_lines.extend(f"{file_sha256(part)}  {part.name}" for part in parts if part != original_path)
    original_path.with_name(f"{original_path.name}.sha256").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    if len(parts) > 1:
        original_path.with_name(f"{original_path.name}.parts.txt").write_text(
            "\n".join(
                [
                    f"Original file: {original_path.name}",
                    f"Original sha256: {original_sha}",
                    "Download every part file in order, then concatenate them.",
                    f"Linux/macOS: cat {original_path.name}.part* > {original_path.name}",
                    f"Windows cmd: copy /b {original_path.name}.part* {original_path.name}",
                    "Make sure every part file is present before concatenating.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset")
    parser.add_argument("--max-size-mib", type=int, default=1900)
    parser.add_argument("--max-size-bytes", type=int, default=0)
    args = parser.parse_args()

    path = Path(args.asset)
    max_size = args.max_size_bytes or args.max_size_mib * 1024 * 1024
    original_sha = file_sha256(path)
    parts = split_asset(path, max_size)
    write_metadata(path, original_sha, parts)
    print("release asset files:")
    for part in parts:
        print(part)


if __name__ == "__main__":
    main()
