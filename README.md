# Psychological Masterclass Voice TTS Engine

Working local implementation for psychologically controlled long-form narration workflows.

## Architecture (text diagram)

```text
[Web UI]
  -> POST /render
[Python HTTP API]
  -> [Psychological Pacing Engine]
     - contradiction/inversion/reveal/reframe/identity detection
     - pause map generation + speed/pitch dampening
  -> [Provider Adapter]
     - local_coqui (dependency-free waveform renderer)
     - elevenlabs (stub for API key integration)
     - local_gpu (stub for XTTS/Tortoise integration)
  -> [Exporter]
     - WAV output + timestamp map for editing
```

## What now works out-of-the-box

- No external package dependency required.
- `/render` creates a real WAV file (non-silent preview speech surrogate).
- `/render/batch` returns timestamps for scene/video edits.
- Shadow Mode profile enforces slower, flatter delivery.
- Frontend exports directly to the local API.

## Core controls

- Speech rate control via segment speed multipliers.
- Psychological pause scaling (`pause_intensity`).
- Pattern-aware slowdown + lower pitch emphasis.
- Pitch range + neutrality controls in profile objects.
- Optional provider switching with fallback to local renderer.

## API options (recommendations)

1. **Option A (local Python)**: Replace `LocalCoquiBackend` render loop with Coqui XTTS inference.
2. **Option B (API)**: Implement ElevenLabs in `ElevenLabsBackend` with stability ~0.8-0.9, style low.
3. **Option C (local GPU)**: Integrate XTTS-v2/Tortoise + quantization + batched chunks.

## Scalability + latency

- Segment scripts into 20-40 sentence chunks.
- Queue chunk renders (Redis/Celery/RQ) and stitch output.
- Cache repeated paragraphs and pause maps.
- Async post-processing workers for compression/de-ess/EQ stage.

## Run

```bash
python -m app.main
```

Then open `web/index.html` and render.
