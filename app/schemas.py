from __future__ import annotations

from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    text: str = Field(min_length=1)
    use_psychological_pacing: bool = True
    pause_intensity: float = Field(default=1.0, ge=0.5, le=2.0)
    neutrality_intensity: float = Field(default=0.85, ge=0.5, le=1.0)
    shadow_mode: bool = False
    provider: str = Field(default="local_coqui")
    output_format: str = Field(default="wav", pattern="^(wav|mp3)$")
    include_room_tone: bool = False


class Segment(BaseModel):
    text: str
    category: str
    pause_after_ms: int
    speed_multiplier: float
    pitch_shift_semitones: float


class RenderResponse(BaseModel):
    job_id: str
    provider: str
    output_path: str
    segments: list[Segment]
    warnings: list[str] = []


class BatchRenderRequest(BaseModel):
    scripts: list[str] = Field(min_length=1)
    shadow_mode: bool = True
    export_timestamps: bool = True
