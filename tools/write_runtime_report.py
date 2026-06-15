from __future__ import annotations

import argparse
import importlib.metadata
import platform
from pathlib import Path


CUDA_FILE_PATTERNS = (
    "torch_cuda.dll",
    "cudart64*.dll",
    "cublas64*.dll",
    "cublasLt64*.dll",
    "nvrtc64*.dll",
    "libtorch_cuda.so*",
    "libcudart.so*",
    "libcublas.so*",
    "libcublasLt.so*",
    "libnvrtc.so*",
)

BITSANDBYTES_FILE_PATTERNS = (
    "libbitsandbytes_cuda*.dll",
    "libbitsandbytes_cuda*.so",
    "libbitsandbytes_cpu.dll",
    "libbitsandbytes_cpu.so",
)


def _files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    if not root.exists():
        return []
    found: dict[str, Path] = {}
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file():
                found[str(path.resolve())] = path
    return sorted(found.values(), key=lambda path: path.name.lower())


def _size_mib(path: Path) -> str:
    return f"{path.stat().st_size / (1024 * 1024):.1f} MiB"


def build_report(package_dir: Path) -> str:
    import torch

    try:
        bitsandbytes_version = importlib.metadata.version("bitsandbytes")
    except importlib.metadata.PackageNotFoundError:
        bitsandbytes_version = "not installed"

    arch_list = torch.cuda.get_arch_list()
    cuda_files = _files(package_dir, CUDA_FILE_PATTERNS)
    bnb_files = _files(package_dir, BITSANDBYTES_FILE_PATTERNS)

    lines = [
        "Ideogram 4 Generator CUDA Compatibility Report",
        "",
        "Build/runtime versions",
        f"- Python platform: {platform.platform()}",
        f"- PyTorch: {torch.__version__}",
        f"- PyTorch CUDA runtime: {torch.version.cuda}",
        f"- PyTorch CUDA arch list: {', '.join(arch_list) if arch_list else 'not reported'}",
        f"- bitsandbytes: {bitsandbytes_version}",
        "",
        "Compatibility notes",
        "- The portable package includes user-mode PyTorch CUDA and bitsandbytes runtime libraries.",
        "- The target machine still needs a compatible NVIDIA driver; the package does not include the NVIDIA kernel driver.",
        "- Supported GPU models are determined by the bundled PyTorch CUDA wheel and bitsandbytes library.",
        "- If a GPU compute capability is not supported by those bundled libraries, startup or local generation will fail explicitly.",
        "- Recommended hardware for the NF4 local path: 24GB+ VRAM and 64GB+ system RAM.",
        "",
        "Packaged CUDA files",
    ]
    if cuda_files:
        lines.extend(f"- {path.name} ({_size_mib(path)})" for path in cuda_files)
    else:
        lines.append("- none found")

    lines.append("")
    lines.append("Packaged bitsandbytes files")
    if bnb_files:
        lines.extend(f"- {path.name} ({_size_mib(path)})" for path in bnb_files)
    else:
        lines.append("- none found")

    lines.append("")
    return "\n".join(lines)


def validate_runtime_files(package_dir: Path, *, require_cuda: bool, require_bitsandbytes_cuda: bool) -> None:
    cuda_files = _files(package_dir, CUDA_FILE_PATTERNS)
    bnb_files = _files(package_dir, BITSANDBYTES_FILE_PATTERNS)
    bnb_cuda_files = [path for path in bnb_files if "cuda" in path.name.lower()]

    if require_cuda and not cuda_files:
        raise SystemExit(f"no packaged PyTorch CUDA runtime files found in {package_dir}")
    if require_bitsandbytes_cuda and not bnb_cuda_files:
        raise SystemExit(f"no packaged bitsandbytes CUDA runtime files found in {package_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", default="dist/Ideogram4Generator")
    parser.add_argument("--output", default="")
    parser.add_argument("--require-cuda", action="store_true")
    parser.add_argument("--require-bitsandbytes-cuda", action="store_true")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    validate_runtime_files(
        package_dir,
        require_cuda=args.require_cuda,
        require_bitsandbytes_cuda=args.require_bitsandbytes_cuda,
    )
    output = Path(args.output) if args.output else package_dir / "RUNTIME-CUDA-COMPATIBILITY.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(package_dir), encoding="utf-8")
    print(f"wrote runtime compatibility report: {output}")


if __name__ == "__main__":
    main()
