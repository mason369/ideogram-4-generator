from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / "venv310"


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def create_venv() -> None:
    if venv_python().exists():
        return
    run([sys.executable, "-m", "venv", str(VENV)])


def install_python_deps(include_local_runtime: bool, cuda_index_url: str) -> None:
    python = str(venv_python())
    run([python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run([python, "-m", "pip", "install", "-r", "requirements.txt"])
    if include_local_runtime:
        run([python, "-m", "pip", "install", "torch", "--index-url", cuda_index_url])
        run([python, "-m", "pip", "install", "git+https://github.com/ideogram-oss/ideogram4.git"])


def install_frontend() -> None:
    run(["npm", "install"])
    run(["npm", "run", "build"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-run", action="store_true")
    parser.add_argument("--skip-local-runtime", action="store_true")
    parser.add_argument("--cuda-index-url", default="https://download.pytorch.org/whl/cu128")
    args = parser.parse_args()

    create_venv()
    install_python_deps(not args.skip_local_runtime, args.cuda_index_url)
    install_frontend()
    if not args.no_run:
        run([str(venv_python()), "run.py"])


if __name__ == "__main__":
    main()
