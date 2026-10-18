import math
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass
class LoadReport:
    count: int
    errors: int
    error_rate: float
    rps: float
    p50: float
    p95: float
    p99: float
    max: float


def _pct(vals, p):
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def _one(fn) -> tuple[float, bool]:
    t0 = time.perf_counter()
    try:
        fn()
        ok = True
    except Exception:
        ok = False
    return (time.perf_counter() - t0) * 1000, ok


def run_load(fn, total: int, concurrency: int) -> LoadReport:
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        results = list(ex.map(lambda _: _one(fn), range(total)))
    wall = time.perf_counter() - t0
    lat = sorted(r[0] for r in results)
    errors = sum(1 for r in results if not r[1])
    return LoadReport(
        count=total, errors=errors, error_rate=round(errors / total, 4), rps=round(total / wall, 1),
        p50=round(_pct(lat, 50), 1), p95=round(_pct(lat, 95), 1), p99=round(_pct(lat, 99), 1), max=round(lat[-1], 1),
    )


def littles_law_concurrency(target_rps: float, avg_latency_s: float) -> int:
    return math.ceil(round(target_rps * avg_latency_s, 9))


def max_rps(concurrency: int, avg_latency_s: float) -> float:
    return round(concurrency / avg_latency_s, 1)


def stage_breakdown(traces: list[dict]) -> list[tuple[str, float]]:
    totals = defaultdict(float)
    for t in traces:
        for stage, ms in t.items():
            totals[stage] += ms
    grand = sum(totals.values())
    return sorted(((s, round(v / grand, 3)) for s, v in totals.items()), key=lambda x: -x[1])
