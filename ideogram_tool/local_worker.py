from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

QUANTIZATION_REPOS = {
    "nf4": "ideogram-ai/ideogram-4-nf4",
    "fp8": "ideogram-ai/ideogram-4-fp8",
}


def _compute_dtype(torch: Any, device: str) -> Any:
    if str(device).startswith("cuda"):
        return torch.bfloat16
    return torch.bfloat16


def run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        import torch
        from ideogram4 import PRESETS, Ideogram4Pipeline, Ideogram4PipelineConfig
    except Exception as exc:
        raise RuntimeError(
            "open-weight ideogram4 runtime is unavailable. Install with "
            "`pip install git+https://github.com/ideogram-oss/ideogram4.git`."
        ) from exc

    device = str(payload.get("device") or "cuda")
    quantization = str(payload.get("quantization") or "nf4")
    if quantization not in QUANTIZATION_REPOS:
        raise RuntimeError(f"unsupported quantization: {quantization}")
    if quantization == "nf4" and not torch.cuda.is_available():
        raise RuntimeError("Ideogram 4 nf4 local mode requires CUDA; set IDEOGRAM_QUANTIZATION=fp8 for non-CUDA diagnostics")
    preset_name = str(payload["sampler_preset"])
    preset = PRESETS.get(preset_name)
    if preset is None:
        raise RuntimeError(f"unsupported sampler preset: {preset_name}")

    output_dir = Path(payload["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    pipe = Ideogram4Pipeline.from_pretrained(
        config=Ideogram4PipelineConfig(weights_repo=QUANTIZATION_REPOS[quantization]),
        device=device,
        dtype=_compute_dtype(torch, device),
    )
    files: list[str] = []
    seed = int(payload["seed"])
    candidate_count = int(payload["candidate_count"])
    for index in range(candidate_count):
        images = pipe(
            str(payload["prompt"]),
            height=int(payload["height"]),
            width=int(payload["width"]),
            num_steps=preset.num_steps,
            guidance_schedule=preset.guidance_schedule,
            mu=preset.mu,
            std=preset.std,
            seed=seed + index,
            raise_on_caption_issues=bool(payload.get("is_structured")),
        )
        if not images:
            raise RuntimeError("Ideogram 4 produced no image")
        output_path = output_dir / f"local-candidate-{index + 1:02d}-seed-{seed + index}.png"
        images[0].save(output_path)
        files.append(str(output_path))
    return {"files": files}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m ideogram_tool.local_worker <payload-json>", file=sys.stderr)
        return 2
    try:
        result = run_payload(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
