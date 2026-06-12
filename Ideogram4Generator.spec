# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import importlib.util
import os

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH)
STRICT_BUNDLE = os.environ.get("IDEOGRAM_STRICT_BUNDLE") == "1"


def collect_tree(source: Path, dest: str):
    items = []
    if not source.exists():
        return items
    for file in source.rglob("*"):
        if file.is_file() and "__pycache__" not in file.parts:
            items.append((str(file), str(Path(dest) / file.relative_to(source).parent)))
    return items


datas = [
    ("README.md", "."),
    ("LICENSE", "."),
]
datas += collect_tree(ROOT / "ideogram_tool" / "static", "ideogram_tool/static")
datas += collect_tree(ROOT / "public", "public")
datas += collect_tree(ROOT / "models" / "hf-cache", "models/hf-cache")

hiddenimports = [
    "uvicorn",
    "fastapi",
    "requests",
    "PIL",
]

def collect_optional(package: str):
    if importlib.util.find_spec(package) is None:
        if STRICT_BUNDLE:
            raise RuntimeError(f"required package is missing for strict bundle: {package}")
        return [], [], []
    try:
        package_datas, package_bins, package_hidden = collect_all(package)
    except Exception as exc:
        if STRICT_BUNDLE:
            raise RuntimeError(f"could not collect required package for strict bundle: {package}") from exc
        return [], [], []
    return package_datas, package_bins, package_hidden


binaries = []
for package in (
    "fastapi",
    "uvicorn",
    "pydantic",
    "requests",
    "PIL",
    "ideogram4",
    "torch",
    "transformers",
    "accelerate",
    "safetensors",
    "huggingface_hub",
    "bitsandbytes",
):
    package_datas, package_bins, package_hidden = collect_optional(package)
    datas += package_datas
    binaries += package_bins
    hiddenimports += package_hidden

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Ideogram4Generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Ideogram4Generator",
)
