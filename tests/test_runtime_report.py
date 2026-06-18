from __future__ import annotations

import importlib.metadata
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from tools.write_runtime_report import build_report


def test_runtime_report_lists_cuda_arches_and_packaged_libraries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "torch_cuda.dll").write_bytes(b"x")
    (tmp_path / "libbitsandbytes_cuda128.dll").write_bytes(b"x")
    fake_torch = SimpleNamespace(
        __version__="2.11.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=SimpleNamespace(get_arch_list=lambda: ["sm_80", "sm_90"]),
    )

    def fake_package_version(name: str) -> str:
        if name == "bitsandbytes":
            return "0.49.2"
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setattr(importlib.metadata, "version", fake_package_version)

    report = build_report(tmp_path)

    assert "PyTorch CUDA runtime: 12.8" in report
    assert "PyTorch CUDA arch list: sm_80, sm_90" in report
    assert "bitsandbytes: 0.49.2" in report
    assert "torch_cuda.dll" in report
    assert "libbitsandbytes_cuda128.dll" in report
    assert "NVIDIA kernel driver" in report
