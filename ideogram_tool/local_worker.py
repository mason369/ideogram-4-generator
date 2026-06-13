from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

QUANTIZATION_REPOS = {
    "nf4": "ideogram-ai/ideogram-4-nf4",
    "fp8": "ideogram-ai/ideogram-4-fp8",
}


def _system_memory_gib() -> float | None:
    if sys.platform == "win32":
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return status.ullTotalPhys / (1024**3)
    if hasattr(os, "sysconf"):
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
        except (OSError, ValueError):
            return None
        return float(pages * page_size) / (1024**3)
    return None


def _assert_minimum_system_memory() -> None:
    required = float(os.environ.get("IDEOGRAM_MIN_SYSTEM_MEMORY_GB", "24"))
    total = _system_memory_gib()
    if total is not None and total < required:
        raise RuntimeError(
            "Ideogram 4 local generation needs at least "
            f"{required:g} GiB system RAM for the bundled NF4 runtime; detected {total:.1f} GiB. "
            "Increase WSL memory or run on Windows/Linux with more RAM."
        )


def _sync_hf_runtime_constants() -> None:
    try:
        from huggingface_hub import constants
    except Exception:
        return
    if "HF_HOME" in os.environ:
        constants.HF_HOME = os.environ["HF_HOME"]
    if "HF_HUB_CACHE" in os.environ:
        constants.HF_HUB_CACHE = os.environ["HF_HUB_CACHE"]
        constants.HUGGINGFACE_HUB_CACHE = os.environ["HF_HUB_CACHE"]
    constants.HF_HUB_OFFLINE = os.environ.get("HF_HUB_OFFLINE") == "1"


def _patch_offline_qwen_loader(pipeline_module: Any) -> None:
    if getattr(pipeline_module, "_telknet_offline_qwen_loader", False):
        return

    def load_qwen3_vl(
        repo_id: str,
        device: Any,
        dtype: Any,
        *,
        tokenizer_subfolder: str | None = None,
        text_encoder_subfolder: str | None = None,
    ):
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        from ideogram4.quantized_loading import FP8_TEXT_ENCODER_CONFIG_FLAG

        tokenizer_kwargs = {"subfolder": tokenizer_subfolder} if tokenizer_subfolder else {}
        model_kwargs = {"subfolder": text_encoder_subfolder} if text_encoder_subfolder else {}
        config_kwargs = {
            "subfolder": text_encoder_subfolder,
            "trust_remote_code": True,
            "local_files_only": True,
        }
        config = AutoConfig.from_pretrained(repo_id, **{key: value for key, value in config_kwargs.items() if value})
        tokenizer = AutoTokenizer.from_pretrained(
            repo_id,
            config=config,
            local_files_only=True,
            **tokenizer_kwargs,
        )

        cfg_path = pipeline_module.hf_hub_download(
            repo_id=repo_id,
            filename=f"{text_encoder_subfolder}/config.json" if text_encoder_subfolder else "config.json",
            local_files_only=True,
        )
        with open(cfg_path, encoding="utf-8") as handle:
            cfg_data = json.load(handle)
        is_quantized = "quantization_config" in cfg_data
        is_fp8 = bool(cfg_data.get(FP8_TEXT_ENCODER_CONFIG_FLAG, False))

        if is_fp8:
            model = pipeline_module._load_fp8_text_encoder(
                repo_id,
                device,
                dtype,
                text_encoder_subfolder=text_encoder_subfolder or "",
            )
        elif is_quantized:
            model = AutoModel.from_pretrained(
                repo_id,
                torch_dtype=dtype,
                trust_remote_code=True,
                device_map={"": device},
                local_files_only=True,
                **model_kwargs,
            )
            model.eval()
        else:
            model = AutoModel.from_pretrained(
                repo_id,
                torch_dtype=dtype,
                trust_remote_code=True,
                local_files_only=True,
                **model_kwargs,
            )
            model.to(device)
            model.eval()
        return tokenizer, model

    pipeline_module._load_qwen3_vl = load_qwen3_vl
    pipeline_module._telknet_offline_qwen_loader = True


def _compute_dtype(torch: Any, device: str) -> Any:
    if str(device).startswith("cuda"):
        return torch.bfloat16
    return torch.bfloat16


def run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _assert_minimum_system_memory()
    _sync_hf_runtime_constants()
    try:
        import torch
        from ideogram4 import PRESETS, Ideogram4Pipeline, Ideogram4PipelineConfig
        import ideogram4.pipeline_ideogram4 as pipeline_module
    except Exception as exc:
        raise RuntimeError(
            "open-weight ideogram4 runtime is unavailable. Install with "
            "`pip install git+https://github.com/ideogram-oss/ideogram4.git`."
        ) from exc
    _patch_offline_qwen_loader(pipeline_module)

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
