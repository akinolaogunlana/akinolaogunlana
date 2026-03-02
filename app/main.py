from __future__ import annotations

import json
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from app.config import DEFAULT_PROFILE, SHADOW_PROFILE
from app.pacing import build_pacing_segments
from app.schemas import BatchRenderRequest, RenderRequest, RenderResponse
from app.tts_backends import BACKENDS

OUTPUT_ROOT = Path("outputs")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def render(req: RenderRequest) -> RenderResponse:
    if not req.text.strip():
        raise ValueError("text is required")

    profile = SHADOW_PROFILE if req.shadow_mode else DEFAULT_PROFILE
    pause_intensity = _clamp(req.pause_intensity, 0.5, 2.0) * profile.silence_intensity

    if req.use_psychological_pacing:
        segments = build_pacing_segments(req.text, pause_intensity=pause_intensity)
    else:
        segments = build_pacing_segments(req.text, pause_intensity=0.7)
    backend = BACKENDS.get(req.provider)
    if backend is None:
        raise ValueError(f"Unknown provider: {req.provider}")

    warnings: list[str] = []
    try:
        output_path = backend.synthesize(segments, OUTPUT_ROOT, req.output_format)
    except RuntimeError as exc:
        warnings.append(str(exc))
        output_path = BACKENDS["local_coqui"].synthesize(segments, OUTPUT_ROOT, "wav")

    if req.output_format == "mp3":
        warnings.append("MP3 export fallback: generated WAV because no MP3 encoder is configured.")

    return RenderResponse(
        job_id=str(uuid.uuid4()),
        provider=backend.name,
        output_path=str(output_path),
        segments=segments,
        warnings=warnings,
    )


def render_batch(req: BatchRenderRequest) -> dict[str, Any]:
    jobs = []
    for script in req.scripts:
        result = render(RenderRequest(text=script, shadow_mode=req.shadow_mode))
        cursor = 0
        timestamps = []
        if req.export_timestamps:
            for seg in result.segments:
                duration_estimate = max(450, len(seg.text) * 55)
                timestamps.append(
                    {
                        "text": seg.text,
                        "start_ms": cursor,
                        "end_ms": cursor + duration_estimate,
                        "pause_after_ms": seg.pause_after_ms,
                        "category": seg.category,
                    }
                )
                cursor += duration_estimate + seg.pause_after_ms
        jobs.append({"render": result.to_dict(), "timestamps": timestamps})
    return {"jobs": jobs}


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._reply(200, {"status": "ok"})
            return
        self._reply(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._reply(400, {"error": "invalid json"})
            return

        try:
            if self.path == "/render":
                req = RenderRequest(**data)
                out = render(req)
                self._reply(200, out.to_dict())
                return
            if self.path == "/render/batch":
                req = BatchRenderRequest(**data)
                out = render_batch(req)
                self._reply(200, out)
                return
            self._reply(404, {"error": "not found"})
        except Exception as exc:  # runtime request guard
            self._reply(400, {"error": str(exc)})


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Psych TTS server listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
