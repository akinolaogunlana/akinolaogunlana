from __future__ import annotations

from pathlib import Path


def build_ffmpeg_chain(include_room_tone: bool) -> list[str]:
    filters = [
        "acompressor=threshold=-17dB:ratio=2.2:attack=15:release=120",
        "deesser=i=0.45:m=0.5:f=0.5:s=o",
        "equalizer=f=220:width_type=h:width=200:g=2",
        "equalizer=f=4200:width_type=h:width=1200:g=-1.2",
        "loudnorm=I=-19:TP=-2:LRA=6",
    ]
    if include_room_tone:
        filters.append("amix=inputs=2:duration=first:weights='1 0.025'")
    return filters


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
