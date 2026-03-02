from __future__ import annotations

from pathlib import Path
import subprocess


def postprocess_wav(input_wav: Path, output_wav: Path) -> None:
    """Open-source ffmpeg chain: compression, normalization, low-mid shaping."""
    filters = (
        "acompressor=threshold=-18dB:ratio=2.0:attack=10:release=120,"
        "loudnorm=I=-19:TP=-2:LRA=6,"
        "equalizer=f=220:width_type=h:width=180:g=1.6,"
        "equalizer=f=4200:width_type=h:width=1300:g=-1"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_wav),
        "-af",
        filters,
        str(output_wav),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def wav_to_mp3(input_wav: Path, output_mp3: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(input_wav), str(output_mp3)], check=True, capture_output=True)
