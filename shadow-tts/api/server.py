from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app import render_shadow_tts


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self._send(204, {})

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/render":
            self._send(404, {"error": "not found"})
            return
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        try:
            payload = json.loads(raw.decode() or "{}")
            out = render_shadow_tts(
                text=payload.get("text", ""),
                shadow_mode=bool(payload.get("shadow_mode", True)),
                pause_intensity=float(payload.get("pause_intensity", 1.0)),
            )
            self._send(200, out)
        except Exception as exc:
            self._send(400, {"error": str(exc)})


def run() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    print("API listening on :8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
