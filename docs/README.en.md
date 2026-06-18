# Ideogram 4 Local CUDA Image Generator

<p align="center">
  <a href="../README.md">中文</a> | English
</p>

Want to try `Ideogram 4` without turning the whole image-generation step into an official API call? This project is the open-source local version of the TelkNet Ideogram 4 tool. It keeps the familiar UI, runs `ideogram-ai/ideogram-4-nf4` locally with CUDA, and ships Windows / Linux portable releases with the model cache already bundled.

The tool keeps the common Ideogram 4 parameters: `prompt / width / height / sampler_preset / seed / candidate_count`, and makes the two execution paths explicit:

- **Local CUDA open-weight generation**: the default path. It does not call the official Magic Prompt service; the full natural-language prompt is wrapped into local Ideogram 4 JSON and rendered locally.
- **Official Magic Prompt optimization**: with an Ideogram API key, the app calls only `/v1/ideogram-v4/magic-prompt`; the returned `json_prompt` is still rendered by the local CUDA runtime, not by the official image-generation endpoint.

Online demo: the TelkNet Ideogram 4 page with the official prompt-optimization flow is available at [https://telknet.cc/tools/ideogram-v4](https://telknet.cc/tools/ideogram-v4). This repository is the open-source local version; after launch, open `http://127.0.0.1:7860`.

Search keywords: `Ideogram 4 local install`, `Ideogram 4 CUDA`, `Ideogram 4 Magic Prompt`, `open-weight text-to-image`, `local AI image generator`, `Windows Linux portable AI image generation`.

## Screenshots

| Windows | Linux |
|---------|-------|
| ![Windows UI](Windows界面.png) | ![Linux UI](Linux界面.png) |

## Features

- **TelkNet-style workspace UI**: prompt input, model notes, canvas presets, sampler presets, candidate count, and generation actions are all on the first screen.
- **Chinese first, English ready**: the app defaults to Chinese and can switch to English from the top-right corner; both README versions are maintained.
- **Seed control with a dice button**: use `0` for runtime randomness, or enter a fixed seed when you want reproducible outputs.
- **Local open-weight rendering**: runs `ideogram-ai/ideogram-4-nf4` or `fp8` through the official `ideogram-oss/ideogram4` runtime and writes PNG outputs to `runtime/outputs/`.
- **Official Magic Prompt only optimizes prompts**: it expands natural language into Ideogram 4 structured JSON Prompt; actual image generation remains local CUDA.
- **Prompt-only optimization**: inspect the Magic Prompt JSON without starting a local generation job.
- **Strict parameter validation**: 256-2048 px canvas, 16 px steps, max 6:1 aspect ratio, 1-4 candidates, and the documented seed range.
- **No silent fallback**: missing API keys, missing model access, unsupported aspect buckets, CUDA problems, and missing weights fail visibly.
- **Portable releases with the model included**: GitHub Actions builds Windows and Linux GPU CUDA NF4 packages with the Ideogram 4 NF4 cache and runtime compatibility report inside.

## Source Checkout And Run

### 1. Clone the repository

```bash
git clone https://github.com/mason369/ideogram-4-generator.git
cd ideogram-4-generator
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv venv310
venv310\Scripts\python -m pip install --upgrade pip wheel "setuptools<81"
venv310\Scripts\python -m pip install -r requirements.txt
```

Linux / WSL:

```bash
python3 -m venv venv310
source venv310/bin/activate
python -m pip install --upgrade pip wheel "setuptools<81"
python -m pip install -r requirements.txt
```

If Ubuntu / WSL reports that the `venv` module is missing, install it first:

```bash
sudo apt-get update
sudo apt-get install -y python3.10-venv
```

### 3. Build the frontend

```bash
npm install
npm run build
```

### 4. Run prompt-only Magic Prompt mode

Windows:

```powershell
venv310\Scripts\python run.py
```

Linux / WSL:

```bash
source venv310/bin/activate
python run.py
```

Open `http://127.0.0.1:7860`, choose **Official Magic Prompt**, enter an Ideogram API key in the UI or set `IDEOGRAM_API_KEY`, then click **Optimize Prompt Only**.

This action calls Magic Prompt only and does not generate an image. Clicking **Generate Image** always uses local CUDA, so prepare the local model as described in the next section.

### 5. Run local CUDA generation from source

Source-based local CUDA generation requires a CUDA environment and a Hugging Face token with accepted `ideogram-ai/ideogram-4-nf4` license access. This is a gated model repository: anonymous access is limited to public model-card files, while weight and configuration downloads require authenticated license access.

Windows PowerShell:

```powershell
$env:HF_TOKEN="your Hugging Face token"
venv310\Scripts\python install.py --no-run
venv310\Scripts\python tools\download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
venv310\Scripts\python run.py
```

Linux / WSL:

```bash
export HF_TOKEN="your Hugging Face token"
source venv310/bin/activate
python install.py --no-run
python tools/download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
python run.py
```

This manual model-download step applies only to source-based development. Release artifacts are built with an embedded model cache; no model-download step is required on the target machine.

Hardware notes:

- System RAM should be at least `64 GiB`. The runtime checks `IDEOGRAM_MIN_SYSTEM_MEMORY_GB` before loading the local model and fails explicitly when the machine is below the threshold, instead of letting WSL or Windows run into OOM. Default WSL memory around `16 GiB` is insufficient; raise `memory` in `.wslconfig` and restart WSL.
- VRAM of `24 GB+` is recommended for long Magic Prompt JSON, 9:16 or higher resolutions, and `V4_QUALITY_48`. `16 GB` VRAM is only suitable for low-resolution, short-prompt, fast-preset experiments and is not the recommended configuration.

### 6. Development checks

```bash
npm run typecheck
npm run build

python -m pip install -r requirements-dev.txt
pytest -q
python run.py --self-test
```

## Modes

| Mode | UI label | Official Magic Prompt | Input | Output |
|------|----------|-----------------------|-------|--------|
| `local_plain` | Local plain prompt | No | Complete natural-language prompt, wrapped into local Ideogram 4 JSON | Local PNG |
| `local_json` | Local structured JSON | No | Ideogram 4 JSON caption | Local PNG |
| `official_magic` | Official Magic Prompt | Yes | Natural language + API key | Local PNG with official prompt optimization |

All generation modes use the local 256-2048 px canvas. Local plain mode preserves the complete prompt and wraps it into local JSON. The official path optimizes the prompt only; it does not request official Ideogram image generation.

Official mode has two actions:

- `Optimize Prompt Only`: calls `/v1/ideogram-v4/magic-prompt` and returns the structured JSON Prompt without generating an image.
- `Generate Image`: calls Magic Prompt, then passes the returned JSON Prompt to the local CUDA runtime. This project does not call `/v1/ideogram-v4/generate`; Magic Prompt still requires an active API key.

## Why Ideogram 4

Ideogram 4 is Ideogram's first open-weight text-to-image foundation model, with **9.3B parameters** and a workflow built around structured JSON prompting. Its strengths are practical design tasks: readable text in images, multilingual typography, layout control, color palettes, and up to 2K local generation.

This project keeps that workflow visible instead of hiding it behind a black box. Plain prompts are wrapped into local Ideogram 4 JSON, official Magic Prompt responses are kept as structured `json_prompt`, and every image is rendered locally through CUDA.

## References

- [Ideogram 4 GitHub](https://github.com/ideogram-oss/ideogram4)
- [Ideogram 4 NF4 Model Card](https://huggingface.co/ideogram-ai/ideogram-4-nf4)
- [Ideogram 4 Technical Blog](https://ideogram.ai/blog/ideogram-4.0/)
- [Magic Prompt v4 API](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

## Citation

```bibtex
@misc{ideogram-4-2026,
  author={Ideogram AI},
  title={{Ideogram 4}},
  year={2026},
  howpublished={\url{https://ideogram.ai/blog/ideogram-4.0/}},
}
```

## Release Builds

`.github/workflows/release.yml` builds:

- `Ideogram4Generator-Windows-GPU-CUDA-NF4-Portable.7z.001` / `.7z.002` ...
- `Ideogram4Generator-Linux-GPU-CUDA-NF4-Portable.tar.partaa` / `.tar.partab` ...

The workflow requires repository secret `HF_TOKEN`; the token must have accepted the `ideogram-ai/ideogram-4-nf4` model license because model weights and configuration files cannot be downloaded anonymously. The token is injected only into the model-download and cache-scan steps, and is not written to the repository, README, release notes, or release assets. Actions downloads the model into `models/hf-cache`, sanitizes token files, verifies that the cache is non-empty, and packages it into the portable builds. The Release workflow pins the `torch==2.11.0` `cu128` wheel so GPU compatibility does not drift with future PyTorch releases. Each portable package includes `RUNTIME-CUDA-COMPATIBILITY.txt`, which records the packaged PyTorch version, CUDA runtime version, PyTorch `sm_` architecture list, bitsandbytes CUDA libraries, and collected CUDA dynamic libraries. GPU compatibility depends on the bundled PyTorch CUDA wheel, bitsandbytes, and the target machine's NVIDIA driver; the portable package does not include the NVIDIA kernel driver, so the target driver must be compatible with CUDA 12.8. Release packaging writes split archives and `.sha256` checksum files directly, then uploads them to GitHub Release from the build job without an Actions-artifact transfer. All parts for the target platform are required; Windows extracts from `.7z.001`, and Linux combines `.tar.part*` files before extracting the tar archive. If the token is missing, the license is not accepted, CUDA dependencies cannot be collected, or the cache is empty, the workflow fails explicitly and no incomplete GPU package is uploaded.

## License

Project code is MIT licensed. Ideogram 4 weights, runtime code, and model license terms remain governed by their upstream licenses.
