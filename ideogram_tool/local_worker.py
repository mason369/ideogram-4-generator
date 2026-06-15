from __future__ import annotations

import json
import os
import sys
import gc
from pathlib import Path
from typing import Any

QUANTIZATION_REPOS = {
    "nf4": "ideogram-ai/ideogram-4-nf4",
    "fp8": "ideogram-ai/ideogram-4-fp8",
}

_PIPELINE_CACHE: dict[tuple[str, str, str], Any] = {}


def _log(message: str) -> None:
    print(f"[ideogram-local] {message}", file=sys.stderr, flush=True)


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
    required = float(os.environ.get("IDEOGRAM_MIN_SYSTEM_MEMORY_GB", "64"))
    total = _system_memory_gib()
    if total is not None and total < required:
        raise RuntimeError(
            "Ideogram 4 local generation needs at least "
            f"{required:g} GiB system RAM for the bundled NF4 runtime; detected {total:.1f} GiB. "
            "Increase system RAM or raise WSL memory before running local generation."
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

        _log("loading qwen tokenizer/config from local cache")
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
            _log("loading qwen fp8 text encoder")
            model = pipeline_module._load_fp8_text_encoder(
                repo_id,
                device,
                dtype,
                text_encoder_subfolder=text_encoder_subfolder or "",
            )
        elif is_quantized:
            _log("loading qwen quantized text encoder")
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
            _log("loading qwen text encoder")
            model = AutoModel.from_pretrained(
                repo_id,
                torch_dtype=dtype,
                trust_remote_code=True,
                local_files_only=True,
                **model_kwargs,
            )
            model.to(device)
            model.eval()
        _log("qwen text encoder loaded")
        return tokenizer, model

    pipeline_module._load_qwen3_vl = load_qwen3_vl
    pipeline_module._telknet_offline_qwen_loader = True


def _patch_offline_weight_loader(pipeline_module: Any) -> None:
    if getattr(pipeline_module, "_telknet_offline_weight_loader", False):
        return

    original_hf_hub_download = pipeline_module.hf_hub_download
    original_load_indexed = pipeline_module._load_indexed_or_single_state_dict
    original_build_transformer = pipeline_module._build_transformer
    original_load_autoencoder = pipeline_module._load_autoencoder

    def hf_hub_download_local(*args: Any, **kwargs: Any) -> str:
        filename = kwargs.get("filename")
        if filename is None and len(args) >= 2:
            filename = args[1]
        kwargs["local_files_only"] = True
        _log(f"resolving weight from local cache: {filename or '<unknown>'}")
        return original_hf_hub_download(*args, **kwargs)

    def load_indexed_or_single_state_dict(repo_id: str, index_filename: str) -> dict[str, Any]:
        _log(f"loading state dict: {index_filename}")
        state_dict = original_load_indexed(repo_id, index_filename)
        _log(f"state dict loaded: {index_filename} tensors={len(state_dict)}")
        return state_dict

    def build_transformer(transformer_config: Any, state_dict: dict[str, Any], device: Any, dtype: Any) -> Any:
        _log(f"building transformer tensors={len(state_dict)} device={device} dtype={dtype}")
        model = original_build_transformer(transformer_config, state_dict, device, dtype)
        _log("transformer built")
        return model

    def load_autoencoder(weights_path: str, device: Any, dtype: Any) -> Any:
        _log("loading autoencoder")
        model = original_load_autoencoder(weights_path, device, dtype)
        _log("autoencoder loaded")
        return model

    pipeline_module.hf_hub_download = hf_hub_download_local
    pipeline_module._load_indexed_or_single_state_dict = load_indexed_or_single_state_dict
    pipeline_module._build_transformer = build_transformer
    pipeline_module._load_autoencoder = load_autoencoder
    pipeline_module._telknet_offline_weight_loader = True


def _compute_dtype(torch: Any, device: str) -> Any:
    if str(device).startswith("cuda"):
        return torch.bfloat16
    return torch.bfloat16


def _load_pipeline_sequential(pipeline_module: Any, torch: Any, config: Any, device: str, dtype: Any) -> Any:
    device_obj = torch.device(device)
    transformer_config = pipeline_module.Ideogram4Config()

    _log("loading conditional transformer")
    conditional_state_dict = pipeline_module._load_indexed_or_single_state_dict(
        config.weights_repo,
        config.conditional_index_filename,
    )
    conditional_transformer = pipeline_module._build_transformer(
        transformer_config,
        conditional_state_dict,
        device_obj,
        dtype,
    )
    del conditional_state_dict
    gc.collect()
    _log("conditional transformer ready")

    _log("loading unconditional transformer")
    unconditional_state_dict = pipeline_module._load_indexed_or_single_state_dict(
        config.weights_repo,
        config.unconditional_index_filename,
    )
    unconditional_transformer = pipeline_module._build_transformer(
        transformer_config,
        unconditional_state_dict,
        device_obj,
        dtype,
    )
    del unconditional_state_dict
    gc.collect()
    _log("unconditional transformer ready")

    autoencoder_weights = pipeline_module.hf_hub_download(
        repo_id=config.weights_repo,
        filename=config.autoencoder_filename,
    )
    text_tokenizer, text_encoder = pipeline_module._load_qwen3_vl(
        config.weights_repo,
        device_obj,
        dtype,
        tokenizer_subfolder=config.tokenizer_subfolder,
        text_encoder_subfolder=config.text_encoder_subfolder,
    )
    autoencoder = pipeline_module._load_autoencoder(autoencoder_weights, device_obj, dtype)

    return pipeline_module.Ideogram4Pipeline(
        conditional_transformer=conditional_transformer,
        unconditional_transformer=unconditional_transformer,
        text_encoder=text_encoder,
        text_tokenizer=text_tokenizer,
        autoencoder=autoencoder,
        config=config,
        device=device_obj,
        dtype=dtype,
    )


def _get_pipeline(torch: Any, device: str, quantization: str) -> Any:
    from ideogram4 import Ideogram4PipelineConfig
    import ideogram4.pipeline_ideogram4 as pipeline_module

    dtype = _compute_dtype(torch, device)
    cache_key = (device, quantization, str(dtype))
    if cache_key not in _PIPELINE_CACHE:
        _log(f"loading pipeline device={device} quantization={quantization} dtype={dtype}")
        _PIPELINE_CACHE[cache_key] = _load_pipeline_sequential(
            pipeline_module,
            torch,
            Ideogram4PipelineConfig(weights_repo=QUANTIZATION_REPOS[quantization]),
            device,
            dtype,
        )
        _log("pipeline loaded")
    else:
        _log("reusing cached pipeline")
    return _PIPELINE_CACHE[cache_key]


def run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _log(
        "request "
        f"size={payload.get('width')}x{payload.get('height')} "
        f"preset={payload.get('sampler_preset')} "
        f"candidates={payload.get('candidate_count')} "
        f"structured={bool(payload.get('is_structured'))}"
    )
    _assert_minimum_system_memory()
    _sync_hf_runtime_constants()
    try:
        _log("importing runtime dependencies")
        import torch
        from ideogram4 import PRESETS
        import ideogram4.pipeline_ideogram4 as pipeline_module
    except Exception as exc:
        raise RuntimeError(
            "open-weight ideogram4 runtime is unavailable. Install with "
            "`pip install git+https://github.com/ideogram-oss/ideogram4.git`."
        ) from exc
    _log(f"torch imported cuda_available={torch.cuda.is_available()}")
    _patch_offline_weight_loader(pipeline_module)
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
    pipe = _get_pipeline(torch, device, quantization)
    files: list[str] = []
    seed = int(payload["seed"])
    candidate_count = int(payload["candidate_count"])
    for index in range(candidate_count):
        _log(f"generating candidate={index + 1}/{candidate_count} seed={seed + index}")
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
        _log(f"saved {output_path}")
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
