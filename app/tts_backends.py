from __future__ import annotations

import uuid
import wave
from pathlib import Path

from app.audio_processing import ensure_output_dir
from app.schemas import Segment


class TTSBackend:
    name = "base"

    def synthesize(self, segments: list[Segment], output_dir: Path) -> Path:
        raise NotImplementedError


class LocalCoquiBackend(TTSBackend):
    name = "local_coqui"

    def synthesize(self, segments: list[Segment], output_dir: Path) -> Path:
        ensure_output_dir(output_dir)
        out = output_dir / f"{uuid.uuid4()}.wav"

        # Placeholder signal. Replace with Coqui model inference in production.
        total_ms = sum(max(450, len(s.text) * 55) + s.pause_after_ms for s in segments)
        total_samples = int(total_ms * 24)
        silence = b"\x00\x00" * total_samples

        with wave.open(str(out), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(24000)
            f.writeframes(silence)

        return out


class ElevenLabsBackend(TTSBackend):
    name = "elevenlabs"

    def synthesize(self, segments: list[Segment], output_dir: Path) -> Path:
        raise RuntimeError(
            "ElevenLabs integration stub. Wire API key + voice settings: stability high, similarity medium, style low."
        )


class LocalGPUBackend(TTSBackend):
    name = "local_gpu"

    def synthesize(self, segments: list[Segment], output_dir: Path) -> Path:
        raise RuntimeError(
            "Local GPU backend stub. Integrate XTTS-v2/Tortoise with quantized inference and batching."
        )


BACKENDS = {
    LocalCoquiBackend.name: LocalCoquiBackend(),
    ElevenLabsBackend.name: ElevenLabsBackend(),
    LocalGPUBackend.name: LocalGPUBackend(),
}
