from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceProfile:
    name: str = "clinical_shadow"
    speech_rate: float = 0.9
    sentence_pause_ms: int = 380
    emphasis_pre_pause_ms: int = 240
    breath_level: float = 0.08
    pitch_floor_hz: int = 85
    pitch_ceiling_hz: int = 140
    compression_ratio: float = 2.2
    emphasis_dampening: float = 0.7
    silence_intensity: float = 1.0
    neutrality_intensity: float = 0.85


@dataclass(slots=True)
class ShadowModePreset:
    speech_rate: float = 0.82
    sentence_pause_ms: int = 520
    emphasis_pre_pause_ms: int = 420
    breath_level: float = 0.12
    pitch_floor_hz: int = 82
    pitch_ceiling_hz: int = 128
    compression_ratio: float = 2.4
    emphasis_dampening: float = 0.82
    silence_intensity: float = 1.35
    neutrality_intensity: float = 0.95


DEFAULT_PROFILE = VoiceProfile()
SHADOW_PROFILE = ShadowModePreset()
