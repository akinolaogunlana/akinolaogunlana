from __future__ import annotations

import subprocess
import wave
from pathlib import Path


class PiperEngine:
    def __init__(self, model_path: Path, config_path: Path, piper_bin: str = "piper") -> None:
        self.model_path = model_path
        self.config_path = config_path
        self.piper_bin = piper_bin

    def synthesize(self, text: str, out_wav: Path) -> None:
        cmd = [
            self.piper_bin,
            "--model",
            str(self.model_path),
            "--config",
            str(self.config_path),
            "--output_file",
            str(out_wav),
        ]
        subprocess.run(cmd, input=text.encode("utf-8"), check=True, capture_output=True)


class FallbackToneEngine:
    """Runs when Piper isn't available; keeps workflow deterministic for CI tests."""

    def synthesize(self, text: str, out_wav: Path) -> None:
        frame_rate = 22050
        duration_s = max(1.0, len(text) / 40.0)
        samples = int(frame_rate * duration_s)
        with wave.open(str(out_wav), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(frame_rate)
            f.writeframes(b"\x00\x00" * samples)
