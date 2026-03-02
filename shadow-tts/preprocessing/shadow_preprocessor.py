from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class PauseConfig:
    pause_short: int = 700
    pause_inversion: int = 1500
    pause_analytical: int = 400


INVERSION_PATTERNS = [
    r"\bnot\b.+\bbut\b",
    r"\byou think\b",
    r"\bthe truth is\b",
    r"\bbut\b",
    r"\byet\b",
    r"\bhowever\b",
]

IDENTITY_PATTERNS = [
    r"\byou are\b",
    r"\byour identity\b",
    r"\bwho you are\b",
]

ANALYTICAL_PATTERNS = [
    r"\btherefore\b",
    r"\bin other words\b",
    r"\bthis means\b",
    r"\bobserve\b",
]


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def classify_line(line: str) -> str:
    lower = line.lower()
    if any(re.search(p, lower) for p in INVERSION_PATTERNS):
        return "inversion"
    if any(re.search(p, lower) for p in IDENTITY_PATTERNS):
        return "identity"
    if any(re.search(p, lower) for p in ANALYTICAL_PATTERNS):
        return "analytical"
    if len(line.split()) <= 7:
        return "short_impact"
    return "neutral"


def inject_pause_tokens(text: str, config: PauseConfig) -> str:
    chunks: list[str] = []
    for line in split_sentences(text):
        label = classify_line(line)
        if label in {"inversion", "identity"}:
            pause = config.pause_inversion
        elif label in {"analytical", "neutral"}:
            pause = config.pause_analytical
        else:
            pause = config.pause_short
        chunks.append(f"{line} <break time=\"{pause}ms\"/>")
    return " ".join(chunks)
