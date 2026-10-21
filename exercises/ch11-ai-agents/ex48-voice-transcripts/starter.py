from dataclasses import dataclass


@dataclass
class Segment:
    speaker: str
    start: float
    end: float
    text: str = ""


def segments(events: list[dict]) -> list[Segment]:
    raise NotImplementedError


def turns(segs: list[Segment]) -> list[Segment]:
    raise NotImplementedError


def response_latencies(segs: list[Segment]) -> list[float]:
    raise NotImplementedError


def barge_ins(segs: list[Segment]) -> list[float]:
    raise NotImplementedError


def call_metrics(events: list[dict], silence_threshold: float = 3.0) -> dict:
    raise NotImplementedError


def to_transcript(turn_list: list[Segment]) -> str:
    raise NotImplementedError
