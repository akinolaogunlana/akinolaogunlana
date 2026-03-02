# Psychological Masterclass Voice TTS Engine

A production-oriented blueprint + reference implementation for long-form (45-60 minute) psychological narration with controlled tension and neutral authority.

## 1) Architecture Diagram (text)

```text
[Web UI]
  -> POST /render
[FastAPI Orchestrator]
  -> [Psychological Pacing Engine]
      - contradiction/inversion/reveal detection
      - strategic silence map
      - pitch/speed dampening
  -> [TTS Provider Adapter]
      - Option A: Local Coqui
      - Option B: API provider (ElevenLabs-like)
      - Option C: Local GPU inference
  -> [Post-Processing Chain]
      - compression
      - de-essing
      - EQ low-mid warmth
      - optional room-tone bed
  -> [Exporter]
      - WAV master
      - MP3 delivery
      - timestamp JSON for video editing
```

## 2) Code Structure

- `app/main.py` FastAPI routes (`/render`, `/render/batch`) and orchestration.
- `app/pacing.py` sentence splitting, pattern recognition, silence rules.
- `app/tts_backends.py` provider abstraction for local/API/GPU backends.
- `app/audio_processing.py` FFmpeg filter chain definitions.
- `app/config.py` baseline and Shadow Mode presets.
- `web/index.html` minimal UI with pacing/neutrality controls.

## 3) Voice Controls Implemented

- Speech rate via profile defaults and per-segment speed multipliers.
- Micro-pause control after sentence-level classifications.
- Emphasis pre-pause profile fields.
- Breath realism parameter (`breath_level`) for backend integration.
- Pitch limiter via floor/ceiling profile bounds.
- Dynamic compression and de-essing defined in FFmpeg chain.
- Emphasis dampening and strategic silence controls.
- Shadow Mode preset for low-variance, slower delivery.

## 4) Psychological Pacing Rules

Current defaults (configurable):

- Short destabilizing line: ~700 ms pause.
- Contradiction/reframe/reveal: ~950-1200 ms pause.
- Inversion/identity-level line: ~1300-1400 ms pause.
- `pause_intensity` scales all values globally.

## 5) Model/API Recommendations

### Option A - Python + Coqui (local)
Pros:
- Full control over style constraints.
- Lowest marginal cost at scale.
- Data privacy for sensitive scripts.

Cons:
- Heavier MLOps burden (model quality + infra).
- Voice quality depends on selected checkpoints.

### Option B - API-based (ElevenLabs-style)
Pros:
- Fastest to production.
- Strong voice cloning and stability controls.
- Reduced infra maintenance.

Cons:
- Ongoing per-character cost.
- Vendor lock-in + policy dependence.

### Option C - Local GPU inference
Pros:
- Best quality/control trade-off if tuned.
- No per-character API fees.

Cons:
- GPU memory/latency engineering complexity.
- Requires batching + quantization work.

## 6) Scalability + Latency Strategy

- Chunk scripts into 20-40 sentence segments.
- Parallel inference workers with queue-based scheduling.
- Cache recurring script sections and reusable room-tone mixes.
- Stream partial renders for long-form jobs.
- Keep post-processing async and batch FFmpeg calls.

## 7) Hosting Recommendations

- API Layer: Fly.io / Render / ECS Fargate (FastAPI).
- GPU Layer: Modal / RunPod / self-managed A10/L40 nodes.
- Storage: S3 + CloudFront for WAV/MP3 artifacts.
- Queue: Redis + RQ/Celery for long-form batch jobs.

## 8) Cost Snapshot (rough)

- API-first: moderate fixed cost + variable character fees; best for low volume.
- Local GPU: higher fixed infra, near-zero marginal TTS cost; best for high volume.
- Hybrid: API for premium voices, local for drafts/batch renders.

## 9) Run

```bash
uvicorn app.main:app --reload
```

Open `web/index.html` directly (or serve statically), then render via API.
