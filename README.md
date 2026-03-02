# GitHub-Hosted Open-Source Shadow Psychology TTS Engine

This repository implements a **fully open-source** Shadow-style TTS pipeline designed to be controlled from GitHub.

## What this solves
- Runs with GitHub-first workflows (no paid/proprietary speech APIs).
- Supports CI-triggered generation via GitHub Actions.
- Includes Codespaces-ready container setup.
- Supports optional API hosting on open platforms (Render/Fly.io/HuggingFace Spaces).
- Uses open-source stack only (`piper`, `ffmpeg`, `pydub`, `librosa`, `torchaudio`, `gradio`).

## Repository structure

```text
/shadow-tts
  /models
  /preprocessing
  /audio
  /workflows
  /api
  /ui
  app.py
  Dockerfile
  requirements.txt
README.md
.github/workflows/shadow-tts-generate.yml
.devcontainer/devcontainer.json
```

## Deployment architecture

### Option A — GitHub Actions inference
1. Trigger workflow manually (`workflow_dispatch`) or push `shadow-tts/input/*.txt`.
2. Action installs ffmpeg + Python deps.
3. Action downloads open-source Piper binary + voice model.
4. Action runs synthesis and preprocessing.
5. Outputs uploaded as GitHub artifacts (`shadow.wav`, optional `shadow.mp3`, prepared text).

Workflow file: `.github/workflows/shadow-tts-generate.yml`.

### Option B — GitHub Codespaces
- One-click launch with `.devcontainer/devcontainer.json`.
- Container builds from `shadow-tts/Dockerfile`.
- Run `python app.py` to launch Gradio UI.

### Option C — External open hosting (GitHub-controlled)
- Build/deploy same Docker image to Render/Fly.io/HuggingFace Spaces.
- Keep GitHub as source of truth and trigger deploys via CI/CD.
- Optional API mode: `python api/server.py` (`/health`, `/render`).

## Shadow preprocessor module
File: `shadow-tts/preprocessing/shadow_preprocessor.py`

- Detects short impact lines, inversion/reversal phrases, identity destabilizers, analytical transitions.
- Injects SSML-like tokens: `<break time="Nms"/>`.
- Configurable pause profile:
  - `pause_short: 700ms`
  - `pause_inversion: 1500ms`
  - `pause_analytical: 400ms`

## Audio processing stack (open-source)
File: `shadow-tts/audio/postprocess.py`

- ffmpeg compression
- loudness normalization
- subtle low-mid EQ shaping
- WAV -> MP3 export
- Works with pydub/librosa/torchaudio ecosystem in requirements for extension workflows.

## Runtime modes
- **Gradio UI** (HuggingFace Spaces friendly): `python app.py`
- **API endpoint**: `python api/server.py`

## Model recommendation
Default workflow downloads:
- Piper binary v1.2.0
- `en_US-lessac-medium` ONNX model (lightweight, CPU-friendly)

This fits GitHub-hosted runner constraints better than larger CUDA-dependent models.

## Scalability and limits
- GitHub-hosted runners are bounded by wall-clock and RAM (~7GB typical practical envelope).
- Use sentence segmentation and chunk synthesis for long scripts.
- Upload chunked outputs as artifacts and merge downstream.

## Cost analysis (API vs local open infra)
- Proprietary API TTS: zero infra setup, recurring per-character fees (not used here).
- Open self-hosted GitHub workflow: no proprietary fees, compute bounded by Actions quotas.
- External open hosting: predictable infra cost + no vendor speech lock-in.

## Quick start (local container parity with hosted)

```bash
cd shadow-tts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Notes
- Pipeline is intentionally open-source only.
- If Piper/model is unavailable, fallback renderer is used for deterministic CI behavior.
