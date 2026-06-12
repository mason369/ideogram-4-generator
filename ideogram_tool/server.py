from __future__ import annotations

import argparse
import os
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .local_cuda import LocalRuntimeError, generate_with_local_cuda
from .official_api import IdeogramApiError, generate_with_official_magic
from .schemas import AppConfig, ExecutionMode, IdeogramRequest, IdeogramResult
from .validators import (
    CANVAS_PRESETS,
    CANDIDATE_COUNTS,
    OFFICIAL_V4_RESOLUTIONS,
    SAMPLER_PRESETS,
    validate_dimensions,
)


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def output_dir() -> Path:
    configured = os.environ.get("IDEOGRAM_OUTPUT_DIR")
    return (project_root() / configured).resolve() if configured else project_root() / "runtime" / "outputs"


def create_app() -> FastAPI:
    app = FastAPI(title="Ideogram 4 Generator", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/outputs", StaticFiles(directory=out_dir), name="outputs")

    @app.get("/api/config", response_model=AppConfig)
    def get_config() -> AppConfig:
        return AppConfig(
            defaults={
                "prompt": "",
                "width": 2048,
                "height": 2048,
                "sampler_preset": "V4_QUALITY_48",
                "seed": 0,
                "candidate_count": 1,
                "execution_mode": "local_plain",
            },
            canvas_presets=CANVAS_PRESETS,
            sampler_presets=SAMPLER_PRESETS,
            candidate_counts=CANDIDATE_COUNTS,
            official_resolutions=OFFICIAL_V4_RESOLUTIONS,
        )

    @app.post("/api/generate", response_model=IdeogramResult)
    def generate(params: IdeogramRequest) -> IdeogramResult:
        try:
            validate_dimensions(params.width, params.height)
            if params.execution_mode == ExecutionMode.official_magic:
                return generate_with_official_magic(params, out_dir)
            return generate_with_local_cuda(params, out_dir)
        except (ValueError, IdeogramApiError, LocalRuntimeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    static_dir = project_root() / "ideogram_tool" / "static"
    index = static_dir / "index.html"
    if static_dir.exists() and index.exists():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{path:path}")
        def spa(path: str) -> FileResponse:
            requested = static_dir / path
            if path and requested.exists() and requested.is_file():
                return FileResponse(requested)
            return FileResponse(index)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        app = create_app()
        if not app:
            raise RuntimeError("FastAPI app failed to initialize")
        print("Ideogram 4 Generator self-test passed")
        return
    if not args.no_browser:
        webbrowser.open(f"http://{args.host}:{args.port}")
    uvicorn.run(create_app(), host=args.host, port=args.port)
