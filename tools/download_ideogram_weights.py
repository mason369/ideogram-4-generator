from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from huggingface_hub import snapshot_download


def _http_status_code(exc: BaseException) -> int | None:
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        response = getattr(current, "response", None)
        status_code = getattr(response, "status_code", None)
        if isinstance(status_code, int):
            return status_code
        current = current.__cause__ or current.__context__
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="ideogram-ai/ideogram-4-nf4")
    parser.add_argument("--cache-dir", default="models/hf-cache")
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--retry-delay", type=int, default=60)
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is required because Ideogram 4 weights are gated. "
            "Accept the Hugging Face model license, create a token, and rerun."
    )
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    retryable_statuses = {429, 500, 502, 503, 504}
    path = None
    for attempt in range(1, args.retries + 1):
        try:
            path = snapshot_download(
                repo_id=args.repo_id,
                cache_dir=str(cache_dir / "hub"),
                token=token,
                local_files_only=False,
                max_workers=2,
            )
            break
        except Exception as exc:
            status_code = _http_status_code(exc)
            is_retryable = status_code in retryable_statuses
            if not is_retryable or attempt >= args.retries:
                raise
            delay = args.retry_delay * attempt
            print(
                f"Model download failed with HTTP {status_code}; "
                f"retrying in {delay}s ({attempt}/{args.retries})."
            )
            time.sleep(delay)
    if path is None:
        raise SystemExit("Model download did not produce a snapshot path.")
    print(f"Downloaded {args.repo_id} into Hugging Face cache snapshot: {path}")


if __name__ == "__main__":
    main()
