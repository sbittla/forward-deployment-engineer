import json
from collections import defaultdict
from datetime import datetime


def parse(lines: list[str]) -> tuple[list[dict], int]:
    recs, bad = [], 0
    for line in lines:
        try:
            r = json.loads(line)
            datetime.fromisoformat(r["ts"])
            r["service"], r["level"]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            bad += 1
            continue
        recs.append(r)
    return sorted(recs, key=lambda r: r["ts"]), bad


def error_rate_by_minute(records: list[dict]) -> dict:
    counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in records:
        minute = r["ts"][11:16]
        cell = counts[r["service"]][minute]
        cell[1] += 1
        cell[0] += r["level"] == "ERROR"
    return {svc: {m: round(e / n, 3) for m, (e, n) in sorted(mins.items())} for svc, mins in counts.items()}


def first_errors(records: list[dict]) -> dict:
    out = {}
    for r in records:
        if r["level"] == "ERROR" and r["service"] not in out:
            out[r["service"]] = r["ts"]
    return out


def _downstream(service: str, deps: dict, seen=None) -> set[str]:
    seen = seen if seen is not None else set()
    for d in deps.get(service, []):
        if d not in seen:
            seen.add(d)
            _downstream(d, deps, seen)
    return seen


def root_cause(records: list[dict], deps: dict[str, list[str]]) -> str:
    fe = first_errors(records)
    candidates = [s for s, ts in fe.items()
                  if not any(d in fe and fe[d] < ts for d in _downstream(s, deps))]
    return min(candidates, key=lambda s: fe[s])


def timeline(records: list[dict], request_id: str) -> list[str]:
    return [f"{r['ts']} {r['service']} {r['level']} {r['msg']}" for r in records if r.get("request_id") == request_id]


def incident_summary(lines: list[str], deps: dict[str, list[str]]) -> str:
    recs, bad = parse(lines)
    fe = first_errors(recs)
    blast = sorted(fe, key=lambda s: fe[s])
    return "\n".join([
        "# Incident summary", "",
        f"Root cause: {root_cause(recs, deps)}",
        f"Blast radius: {', '.join(blast)}",
        f"Malformed lines: {bad}",
    ]) + "\n"
