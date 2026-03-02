from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import DEFAULT_PROFILE, SHADOW_PROFILE
from app.pacing import build_pacing_segments
from app.schemas import BatchRenderRequest, RenderRequest, RenderResponse
from app.tts_backends import BACKENDS

app = FastAPI(title="Psychological Masterclass TTS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_ROOT = Path("outputs")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/render", response_model=RenderResponse)
def render(req: RenderRequest) -> RenderResponse:
    profile = SHADOW_PROFILE if req.shadow_mode else DEFAULT_PROFILE

    segments = build_pacing_segments(
        req.text,
        pause_intensity=req.pause_intensity * profile.silence_intensity,
    )

    backend = BACKENDS.get(req.provider)
    if not backend:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    warnings: list[str] = []
    try:
        output_path = backend.synthesize(segments, OUTPUT_ROOT)
    except RuntimeError as exc:
        warnings.append(str(exc))
        fallback = BACKENDS["local_coqui"]
        output_path = fallback.synthesize(segments, OUTPUT_ROOT)

    return RenderResponse(
        job_id=str(uuid.uuid4()),
        provider=backend.name,
        output_path=str(output_path),
        segments=segments,
        warnings=warnings,
    )


@app.post("/render/batch")
def render_batch(req: BatchRenderRequest) -> dict:
    job_results = []
    for script in req.scripts:
        render_req = RenderRequest(text=script, shadow_mode=req.shadow_mode)
        result = render(render_req)
        timestamps = []
        if req.export_timestamps:
            cursor = 0
            for seg in result.segments:
                duration_estimate = max(450, len(seg.text) * 55)
                timestamps.append({
                    "text": seg.text,
                    "start_ms": cursor,
                    "end_ms": cursor + duration_estimate,
                    "pause_after_ms": seg.pause_after_ms,
                    "category": seg.category,
                })
                cursor += duration_estimate + seg.pause_after_ms
        job_results.append({"render": result.model_dump(), "timestamps": timestamps})
    return {"jobs": job_results}
