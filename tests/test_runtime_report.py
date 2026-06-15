from __future__ import annotations

from pathlib import Path

from tools.write_runtime_report import build_report


def test_runtime_report_lists_cuda_arches_and_packaged_libraries(tmp_path: Path) -> None:
    (tmp_path / "torch_cuda.dll").write_bytes(b"x")
    (tmp_path / "libbitsandbytes_cuda128.dll").write_bytes(b"x")

    report = build_report(tmp_path)

    assert "PyTorch CUDA runtime:" in report
    assert "PyTorch CUDA arch list:" in report
    assert "bitsandbytes:" in report
    assert "torch_cuda.dll" in report
    assert "libbitsandbytes_cuda128.dll" in report
    assert "NVIDIA kernel driver" in report
