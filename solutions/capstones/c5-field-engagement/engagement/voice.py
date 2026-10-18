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
    events = sorted(events, key=lambda e: e["t"])
    open_, out = {}, []
    for e in events:
        sp = e["speaker"]
        if e["type"] == "start":
            open_[sp] = (e["t"], [])
        elif e["type"] == "text" and sp in open_:
            open_[sp][1].append(e["text"])
        elif e["type"] == "end" and sp in open_:
            start, texts = open_.pop(sp)
            out.append(Segment(sp, start, e["t"], " ".join(texts)))
    last = events[-1]["t"] if events else 0
    out += [Segment(sp, s, last, " ".join(t)) for sp, (s, t) in open_.items()]
    return sorted(out, key=lambda s: (s.start, s.speaker))


def caller_transcript(events: list[dict]) -> str:
    return "\n".join(f"{s.speaker.capitalize()}: {s.text}" for s in segments(events))


def call_metrics(events: list[dict]) -> dict:
    segs = segments(events)
    lat = [round(c.start - p.end, 3) for p, c in zip(segs, segs[1:])
           if c.speaker == "agent" and p.speaker == "caller" and c.start >= p.end]
    agents = [s for s in segs if s.speaker == "agent"]
    barge = [c.start for c in segs if c.speaker == "caller" and any(a.start < c.start < a.end for a in agents)]
    return {"max_latency_s": max(lat) if lat else None,
            "avg_latency_s": round(sum(lat) / len(lat), 3) if lat else None,
            "barge_ins": len(barge),
            "duration_s": round(max(s.end for s in segs) - min(s.start for s in segs), 1) if segs else 0.0}


def p95(values: list[float]) -> float | None:
    vals = sorted(v for v in values if v is not None)
    return vals[max(0, math.ceil(0.95 * len(vals)) - 1)] if vals else None
