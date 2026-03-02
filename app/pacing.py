from __future__ import annotations

import re

from app.schemas import Segment

SHORT_LINE_WORD_LIMIT = 7

PATTERN_RULES: list[tuple[str, str, int, float, float]] = [
    (r"\bbut\b|\byet\b|\bhowever\b", "contradiction", 950, 0.92, -0.4),
    (r"\bnot\s+.*\bbut\b", "inversion", 1300, 0.88, -0.5),
    (r"\bthe\s+truth\s+is\b|\breality\s+is\b", "structural_reveal", 1200, 0.9, -0.35),
    (r"\byou\s+are\b|\byour\s+identity\b", "identity_level", 1400, 0.86, -0.6),
    (r"\bin\s+other\s+words\b|\bwhat\s+this\s+means\b", "reframe", 1050, 0.9, -0.3),
]


def split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def classify_sentence(sentence: str) -> tuple[str, int, float, float]:
    lower = sentence.lower()
    for pattern, label, pause_ms, speed, pitch in PATTERN_RULES:
        if re.search(pattern, lower):
            return label, pause_ms, speed, pitch

    word_count = len(sentence.split())
    if word_count <= SHORT_LINE_WORD_LIMIT:
        return "destabilizing_short", 700, 0.94, -0.2

    return "neutral", 380, 1.0, 0.0


def build_pacing_segments(text: str, pause_intensity: float = 1.0) -> list[Segment]:
    segments: list[Segment] = []
    for sentence in split_sentences(text):
        category, base_pause_ms, speed, pitch = classify_sentence(sentence)
        pause_after_ms = int(base_pause_ms * pause_intensity)
        segments.append(
            Segment(
                text=sentence,
                category=category,
                pause_after_ms=pause_after_ms,
                speed_multiplier=speed,
                pitch_shift_semitones=pitch,
            )
        )
    return segments
