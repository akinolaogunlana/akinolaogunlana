from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class RenderRequest:
    text: str
    use_psychological_pacing: bool = True
    pause_intensity: float = 1.0
    neutrality_intensity: float = 0.85
    shadow_mode: bool = False
    provider: str = "local_coqui"
    output_format: str = "wav"
    include_room_tone: bool = False


@dataclass(slots=True)
class Segment:
    text: str
    category: str
    pause_after_ms: int
    speed_multiplier: float
    pitch_shift_semitones: float


@dataclass(slots=True)
class RenderResponse:
    job_id: str
    provider: str
    output_path: str
    segments: list[Segment]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["segments"] = [asdict(seg) for seg in self.segments]
        return data


@dataclass(slots=True)
class BatchRenderRequest:
    scripts: list[str]
    shadow_mode: bool = True
    export_timestamps: bool = True
