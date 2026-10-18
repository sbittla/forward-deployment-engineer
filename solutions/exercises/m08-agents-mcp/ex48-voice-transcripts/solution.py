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
    open_: dict[str, tuple[float, list[str]]] = {}
    out = []
    for e in events:
        sp = e["speaker"]
        if e["type"] == "start":
            open_[sp] = (e["t"], [])
        elif e["type"] == "text" and sp in open_:
            open_[sp][1].append(e["text"])
        elif e["type"] == "end" and sp in open_:
            start, texts = open_.pop(sp)
            out.append(Segment(sp, start, e["t"], " ".join(texts)))
    last_t = events[-1]["t"] if events else 0
    for sp, (start, texts) in open_.items():
        out.append(Segment(sp, start, last_t, " ".join(texts)))
    return sorted(out, key=lambda s: (s.start, s.speaker))


def turns(segs: list[Segment]) -> list[Segment]:
    out: list[Segment] = []
    for s in segs:
        if out and out[-1].speaker == s.speaker:
            prev = out[-1]
            out[-1] = Segment(s.speaker, prev.start, max(prev.end, s.end), " ".join(x for x in (prev.text, s.text) if x))
        else:
            out.append(Segment(s.speaker, s.start, s.end, s.text))
    return out


def response_latencies(segs: list[Segment]) -> list[float]:
    out = []
    for prev, cur in zip(segs, segs[1:]):
        if cur.speaker == "agent" and prev.speaker == "caller" and cur.start >= prev.end:
            out.append(round(cur.start - prev.end, 3))
    return out


def barge_ins(segs: list[Segment]) -> list[float]:
    agents = [s for s in segs if s.speaker == "agent"]
    return [c.start for c in segs if c.speaker == "caller" and any(a.start < c.start < a.end for a in agents)]


def _pct(values: list[float], p: float):
    if not values:
        return None
    vals = sorted(values)
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def call_metrics(events: list[dict], silence_threshold: float = 3.0) -> dict:
    segs = segments(events)
    lat = response_latencies(segs)
    agent = sum(s.end - s.start for s in segs if s.speaker == "agent")
    total = sum(s.end - s.start for s in segs)
    by_time = sorted(segs, key=lambda s: s.start)
    silences, latest_end = 0, None
    for s in by_time:
        if latest_end is not None and s.start - latest_end > silence_threshold:
            silences += 1
        latest_end = s.end if latest_end is None else max(latest_end, s.end)
    return {
        "latency_p50": _pct(lat, 50),
        "latency_p95": _pct(lat, 95),
        "barge_in_count": len(barge_ins(segs)),
        "agent_talk_ratio": round(agent / total, 3) if total else 0.0,
        "long_silences": silences,
    }


def to_transcript(turn_list: list[Segment]) -> str:
    return "\n".join(f"{t.speaker.capitalize()}: {t.text}" for t in turn_list)
