from __future__ import annotations

import math
import random
import uuid
import wave
from pathlib import Path

from app.audio_processing import ensure_output_dir
from app.schemas import Segment

SAMPLE_RATE = 24000


class TTSBackend:
    name = "base"

    def synthesize(self, segments: list[Segment], output_dir: Path, output_format: str = "wav") -> Path:
        raise NotImplementedError


class LocalCoquiBackend(TTSBackend):
    """Dependency-free speech surrogate that creates intelligible pacing previews.

    This is not a neural model; it is a deterministic waveform renderer so the app
    works out-of-the-box in restricted environments.
    """

    name = "local_coqui"

    def synthesize(self, segments: list[Segment], output_dir: Path, output_format: str = "wav") -> Path:
        ensure_output_dir(output_dir)
        out = output_dir / f"{uuid.uuid4()}.wav"
        pcm = bytearray()

        for seg in segments:
            base_freq = 110 * (2 ** (seg.pitch_shift_semitones / 12))
            seg_rate = max(0.78, min(1.06, seg.speed_multiplier))
            chars = max(1, len(seg.text))
            seg_ms = int(chars * (52 / seg_rate))
            samples = int((seg_ms / 1000) * SAMPLE_RATE)

            for i in range(samples):
                t = i / SAMPLE_RATE
                carrier = math.sin(2 * math.pi * base_freq * t)
                harmonic = 0.35 * math.sin(2 * math.pi * base_freq * 2.1 * t)
                noise = random.uniform(-0.06, 0.06)
                amp = 0.17 * (0.6 + 0.4 * math.sin(2 * math.pi * 3.1 * t) ** 2)
                val = int(max(-1.0, min(1.0, (carrier + harmonic + noise) * amp)) * 32767)
                pcm += int(val).to_bytes(2, "little", signed=True)

            pause_samples = int((seg.pause_after_ms / 1000) * SAMPLE_RATE)
            pcm += b"\x00\x00" * pause_samples

        with wave.open(str(out), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SAMPLE_RATE)
            f.writeframes(pcm)

        return out


class ElevenLabsBackend(TTSBackend):
    name = "elevenlabs"

    def synthesize(self, segments: list[Segment], output_dir: Path, output_format: str = "wav") -> Path:
        raise RuntimeError("ElevenLabs provider requires API integration and credentials.")


class LocalGPUBackend(TTSBackend):
    name = "local_gpu"

    def synthesize(self, segments: list[Segment], output_dir: Path, output_format: str = "wav") -> Path:
        raise RuntimeError("Local GPU backend requires XTTS/Tortoise model installation.")


BACKENDS = {
    LocalCoquiBackend.name: LocalCoquiBackend(),
    ElevenLabsBackend.name: ElevenLabsBackend(),
    LocalGPUBackend.name: LocalGPUBackend(),
}
