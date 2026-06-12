from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .schemas import GeneratedImage, IdeogramRequest, IdeogramResult
from .validators import normalize_seed, parse_json_prompt


class LocalRuntimeError(RuntimeError):
    pass


def _hf_cache_env() -> dict[str, str]:
    env = os.environ.copy()
    configured = os.environ.get("IDEOGRAM_HF_CACHE")
    bundled = Path(__file__).resolve().parent.parent / "models" / "hf-cache"
    cache_dir = Path(configured).expanduser() if configured else bundled
    if cache_dir.exists():
        env["HF_HOME"] = str(cache_dir)
        env["HF_HUB_CACHE"] = str(cache_dir / "hub")
    return env


def generate_with_local_cuda(
    params: IdeogramRequest,
    output_dir: Path,
    *,
    optimized_prompt: dict[str, Any] | None = None,
    prompt_flow: str | None = None,
) -> IdeogramResult:
    from .local_worker import run_payload

    base_seed = normalize_seed(params.seed, params.candidate_count)
    prompt_for_runtime = params.prompt
    is_structured = params.execution_mode.value == "local_json" or optimized_prompt is not None
    active_prompt_flow = prompt_flow
    if is_structured:
        if optimized_prompt is None:
            optimized_prompt = parse_json_prompt(params.prompt)
            active_prompt_flow = "user_supplied_structured_json_prompt"
        prompt_for_runtime = json.dumps(optimized_prompt, ensure_ascii=False, separators=(",", ":"))
    if active_prompt_flow is None:
        active_prompt_flow = "plain_prompt_without_official_magic_prompt"

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ideogram4-local-") as tmp:
        payload_path = Path(tmp) / "payload.json"
        payload = {
            "prompt": prompt_for_runtime,
            "width": params.width,
            "height": params.height,
            "sampler_preset": params.sampler_preset,
            "seed": base_seed,
            "candidate_count": params.candidate_count,
            "output_dir": str(output_dir),
            "device": os.environ.get("IDEOGRAM_DEVICE", "cuda"),
            "quantization": os.environ.get("IDEOGRAM_QUANTIZATION", "nf4"),
            "is_structured": is_structured,
        }
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        previous_env = {key: os.environ.get(key) for key in ("HF_HOME", "HF_HUB_CACHE")}
        os.environ.update({key: value for key, value in _hf_cache_env().items() if key in {"HF_HOME", "HF_HUB_CACHE"}})
        try:
            runtime_output = run_payload(json.loads(payload_path.read_text(encoding="utf-8")))
        except Exception as exc:
            raise LocalRuntimeError(f"local Ideogram 4 runtime failed: {exc}") from exc
        finally:
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    files = runtime_output.get("files")
    if not isinstance(files, list) or len(files) != params.candidate_count:
        raise LocalRuntimeError(f"local Ideogram 4 produced {len(files) if isinstance(files, list) else 0} files")
    images = []
    for index, file in enumerate(files):
        path = Path(file)
        if not path.exists() or path.stat().st_size == 0:
            raise LocalRuntimeError(f"local Ideogram 4 output is missing or empty: {path}")
        images.append(
            GeneratedImage(
                url=f"/outputs/{path.name}",
                filename=path.name,
                seed=base_seed + index,
                prompt=prompt_for_runtime,
                resolution=f"{params.width}x{params.height}",
            )
        )
    return IdeogramResult(
        mode=params.execution_mode,
        images=images,
        optimized_prompt=optimized_prompt,
        request={
            "runtime": "ideogram-oss/ideogram4",
            "prompt_flow": active_prompt_flow,
            "width": params.width,
            "height": params.height,
            "sampler_preset": params.sampler_preset,
            "seed": base_seed,
            "candidate_count": params.candidate_count,
            "device": os.environ.get("IDEOGRAM_DEVICE", "cuda"),
            "quantization": os.environ.get("IDEOGRAM_QUANTIZATION", "nf4"),
        },
        message="local Ideogram 4 generation completed",
    )
