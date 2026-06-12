# Ideogram 4 Generator

<p align="center">
  <a href="../README.md">中文</a> | English
</p>

An open-source standalone version of the TelkNet `Ideogram 4` image-generation tool. It keeps the original parameter surface: `prompt / width / height / sampler_preset / seed / candidate_count`, and exposes two explicit execution paths:

- **Local CUDA open-weight path**: default mode. No official Magic Prompt is used; the natural-language prompt is sent verbatim to the local Ideogram 4 runtime.
- **Official prompt optimization path**: enter an Ideogram API key, call `/v1/ideogram-v4/magic-prompt`, then pass the returned `json_prompt` to `/v1/ideogram-v4/generate`.

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
- Strict parameter validation: 256-2048 px, 16 px step, max 6:1 aspect ratio, 1-4 candidates.
- No silent fallback: missing keys, missing weights, unsupported official resolutions, and CUDA/runtime problems fail explicitly.
- GitHub Actions for Windows and Linux GPU portable releases.

## Quick Start

```bash
git clone https://github.com/mason369/ideogram-4-generator.git
cd ideogram-4-generator
python -m venv venv310
venv310\Scripts\python -m pip install -r requirements.txt
npm install
npm run build
venv310\Scripts\python run.py
```

Open `http://127.0.0.1:7860`.

For local CUDA mode, accept the gated Hugging Face model license and set `HF_TOKEN`:

```bash
python install.py --no-run
python tools/download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
python run.py
```

## Modes

| Mode | UI label | Official Magic Prompt | Input | Output |
|------|----------|-----------------------|-------|--------|
| `local_plain` | Local plain prompt | No | Natural language | Local PNG |
| `local_json` | Local structured JSON | No | Ideogram 4 JSON caption | Local PNG |
| `official_magic` | Official Magic Prompt | Yes | Natural language + API key | Downloaded official PNG |

The local model supports arbitrary 256-2048 px multiples of 16 up to 6:1. The official v4 API currently accepts a fixed `resolution` enum, so official mode validates this strictly and never silently changes the requested size.

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

- `Ideogram4Generator-Windows-GPU-Portable.zip`
- `Ideogram4Generator-Linux-GPU-Portable.tar.gz`

The workflow requires repository secret `HF_TOKEN`; if the token is missing or the model license has not been accepted, the workflow fails explicitly.

## License

Project code is MIT licensed. Ideogram 4 weights, runtime code, and model license terms remain governed by their upstream licenses.
