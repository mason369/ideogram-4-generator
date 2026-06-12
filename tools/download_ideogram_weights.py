from __future__ import annotations

import argparse
import os
from pathlib import Path

from huggingface_hub import snapshot_download


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="ideogram-ai/ideogram-4-nf4")
    parser.add_argument("--cache-dir", default="models/hf-cache")
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is required because Ideogram 4 weights are gated. "
            "Accept the Hugging Face model license, create a token, and rerun."
        )
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(
        repo_id=args.repo_id,
        cache_dir=str(cache_dir / "hub"),
        token=token,
        local_files_only=False,
    )
    print(f"Downloaded {args.repo_id} into Hugging Face cache snapshot: {path}")


if __name__ == "__main__":
    main()
