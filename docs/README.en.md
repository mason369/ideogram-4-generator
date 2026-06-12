# Ideogram 4 Generator

<p align="center">
  <a href="../README.md">中文</a> | English
</p>

An open-source standalone version of the TelkNet `Ideogram 4` image-generation tool. It keeps the original parameter surface: `prompt / width / height / sampler_preset / seed / candidate_count`, and exposes two explicit execution paths:

- **Local CUDA open-weight path**: default mode. No official Magic Prompt is used; the natural-language prompt is sent verbatim to the local Ideogram 4 runtime.
- **Official prompt optimization path**: enter an Ideogram API key, call `/v1/ideogram-v4/magic-prompt`, then pass the returned `json_prompt` to `/v1/ideogram-v4/generate`.

Online demo: the TelkNet Ideogram 4 page with the official prompt-optimization flow is available at [https://telknet.cc/tools/ideogram-v4](https://telknet.cc/tools/ideogram-v4). This repository is the open-source local version; after launch, open `http://127.0.0.1:7860`.

## Screenshots

| Windows | Linux |
|---------|-------|
| ![Windows UI](Windows界面.png) | ![Linux UI](Linux界面.png) |

## Features

- TelkNet-style Ideogram workspace UI.
- Chinese by default with an English switch.
- Seed field with a dice randomizer button.
- Local open-weight generation via `ideogram-oss/ideogram4`.
- Official API generation with Magic Prompt and downloaded PNG outputs.
- Prompt-only Magic Prompt action that returns JSON Prompt without calling the paid image-generation endpoint.
- Strict parameter validation: local mode uses 256-2048 px, 16 px step, and max 6:1 aspect ratio; official mode uses the Ideogram v4 fixed `resolution` enum, including values such as `1440x2560`.
- No silent fallback: missing keys, missing weights, unsupported official resolutions, and CUDA/runtime problems fail explicitly.
- GitHub Actions for Windows and Linux GPU CUDA NF4 portable releases. Release assets bundle the model cache so end users do not need to download the model manually.

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
venv310\Scripts\python -m pip install -r requirements.txt
```

Linux / WSL:

```bash
python -m venv venv310
source venv310/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 3. Build the frontend

```bash
npm install
npm run build
```

### 4. Run official API mode

Windows:

```powershell
venv310\Scripts\python run.py
```

Linux / WSL:

```bash
source venv310/bin/activate
python run.py
```

Open `http://127.0.0.1:7860`, choose **Official Magic Prompt**, and enter an Ideogram API key in the UI or set `IDEOGRAM_API_KEY`.

### 5. Run local CUDA mode from source

Source runs require a CUDA-capable local machine and a Hugging Face token that has accepted the `ideogram-ai/ideogram-4-nf4` license:

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

The manual model download above is only for source-based development. GitHub Release bundles download and package the model cache in Actions, so release users do not need this step.

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
| `local_plain` | Local plain prompt | No | Natural language | Local PNG |
| `local_json` | Local structured JSON | No | Ideogram 4 JSON caption | Local PNG |
| `official_magic` | Official Magic Prompt | Yes | Natural language + API key | Downloaded official PNG |

The local model supports arbitrary 256-2048 px multiples of 16 up to 6:1. The official v4 API currently accepts a fixed `resolution` enum, so official mode validates this strictly and never silently changes the requested size.

Official mode has two actions:

- `Optimize Prompt Only`: calls `/v1/ideogram-v4/magic-prompt` and returns the structured JSON Prompt without generating an image.
- `Generate Image`: calls Magic Prompt, then `/v1/ideogram-v4/generate`, downloads the PNG, and is billed by image output. Magic Prompt is not listed as a separate line item on Ideogram's public API pricing page, but it still requires an active API key.

## References

- [Ideogram 4 GitHub](https://github.com/ideogram-oss/ideogram4)
- [Ideogram 4 NF4 Model Card](https://huggingface.co/ideogram-ai/ideogram-4-nf4)
- [Ideogram 4 Technical Blog](https://ideogram.ai/blog/ideogram-4.0/)
- [Generate with Ideogram 4.0 API](https://developer.ideogram.ai/api-reference/api-reference/generate-v4)
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

- `Ideogram4Generator-Windows-GPU-CUDA-NF4-Portable.zip`
- `Ideogram4Generator-Linux-GPU-CUDA-NF4-Portable.tar.gz`

The workflow requires repository secret `HF_TOKEN`; the token must have accepted the `ideogram-ai/ideogram-4-nf4` model license. The token is only injected into the model-download and cache-scan steps, and is not written to the repository, README, release notes, or release assets. Actions downloads the model into `models/hf-cache`, sanitizes token files, verifies that the cache is non-empty, and packages it into the portable builds. If the complete archive is too large for a single GitHub Release asset, the workflow emits `.part001` / `.part002` split files plus a `.sha256` checksum. If the token is missing, the license is not accepted, CUDA dependencies cannot be collected, or the cache is empty, the workflow fails explicitly and no incomplete GPU package is uploaded.

## License

Project code is MIT licensed. Ideogram 4 weights, runtime code, and model license terms remain governed by their upstream licenses.
