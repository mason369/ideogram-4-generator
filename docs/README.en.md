# Ideogram 4 Generator

<p align="center">
  <a href="../README.md">中文</a> | English
</p>

An open-source standalone version of the TelkNet `Ideogram 4` image-generation tool. It keeps the original parameter surface: `prompt / width / height / sampler_preset / seed / candidate_count`, and exposes two explicit execution paths:

- **Local CUDA open-weight path**: default mode. No official Magic Prompt is used; the natural-language prompt is sent verbatim to the local Ideogram 4 runtime.
- **Official prompt optimization path**: enter an Ideogram API key and call only `/v1/ideogram-v4/magic-prompt`; the returned `json_prompt` is rendered by the local CUDA Ideogram 4 runtime.

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
- Official Magic Prompt flow that sends the natural-language prompt to the official optimizer only, then renders PNG outputs locally.
- Prompt-only Magic Prompt action that returns JSON Prompt without local generation.
- Strict parameter validation: all generation modes use 256-2048 px, 16 px step, max 6:1 aspect ratio, supported Magic Prompt aspect buckets, 1-4 candidates, and the documented seed range.
- No silent fallback: missing keys, missing weights, unsupported Magic Prompt aspect buckets, and CUDA/runtime problems fail explicitly.
- GitHub Actions for Windows and Linux GPU CUDA NF4 portable releases. Release artifacts include the model cache; no additional model download is required on the target machine.

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
python3 -m venv venv310
source venv310/bin/activate
python -m pip install --upgrade pip setuptools wheel
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

- System RAM should be at least `24 GiB`. The runtime checks `IDEOGRAM_MIN_SYSTEM_MEMORY_GB` before loading the local model and fails explicitly when the machine is below the threshold, instead of letting WSL get killed by the OOM killer. Default WSL memory around `16 GiB` is insufficient; raise `memory` in `.wslconfig` and restart WSL.
- VRAM of `24 GB+` is recommended for long Magic Prompt JSON, 9:16 or higher resolutions, and `V4_QUALITY_48`. `16 GB` VRAM can be used for exploratory tests with lower resolutions, shorter prompts, and faster sampler presets, but is not the recommended configuration.

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
| `official_magic` | Official Magic Prompt | Yes | Natural language + API key | Local PNG with official prompt optimization |

All generation modes use the local 256-2048 px canvas. The official path optimizes the prompt only; it does not request official Ideogram image generation.

Official mode has two actions:

- `Optimize Prompt Only`: calls `/v1/ideogram-v4/magic-prompt` and returns the structured JSON Prompt without generating an image.
- `Generate Image`: calls Magic Prompt, then passes the returned JSON Prompt to the local CUDA runtime. This project does not call `/v1/ideogram-v4/generate`; Magic Prompt still requires an active API key.

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

The workflow requires repository secret `HF_TOKEN`; the token must have accepted the `ideogram-ai/ideogram-4-nf4` model license because model weights and configuration files cannot be downloaded anonymously. The token is injected only into the model-download and cache-scan steps, and is not written to the repository, README, release notes, or release assets. Actions downloads the model into `models/hf-cache`, sanitizes token files, verifies that the cache is non-empty, and packages it into the portable builds. Release packaging writes split archives and `.sha256` checksum files directly, then uploads them to GitHub Release from the build job without an Actions-artifact transfer. All parts for the target platform are required; Windows extracts from `.7z.001`, and Linux combines `.tar.part*` files before extracting the tar archive. If the token is missing, the license is not accepted, CUDA dependencies cannot be collected, or the cache is empty, the workflow fails explicitly and no incomplete GPU package is uploaded.

## License

Project code is MIT licensed. Ideogram 4 weights, runtime code, and model license terms remain governed by their upstream licenses.
