"""Voice-call analytics from the voice agent's event stream (see ex48)."""
import math
from dataclasses import dataclass


@dataclass
class Segment:
    speaker: str
    start: float
    end: float
    text: str = ""


def segments(events: list[dict]) -> list[Segment]:
    raise NotImplementedError


def caller_transcript(events: list[dict]) -> str:
    raise NotImplementedError


def call_metrics(events: list[dict]) -> dict:
    raise NotImplementedError


def p95(values: list[float]) -> float | None:
    raise NotImplementedError
