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
    concurrency: int = 0
    think_time_s: float = 0.0


def _pct(vals, p):
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def _one(fn, think_time_s: float = 0.0) -> tuple[float, bool]:
    t0 = time.perf_counter()
    try:
        fn()
        ok = True
    except Exception:
        ok = False
    elapsed = (time.perf_counter() - t0) * 1000
    if think_time_s:
        time.sleep(think_time_s)          # the simulated user pauses before the worker's next request
    return elapsed, ok


def run_load(fn, total: int, concurrency: int, think_time_s: float = 0.0) -> LoadReport:
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        results = list(ex.map(lambda _: _one(fn, think_time_s), range(total)))
    wall = time.perf_counter() - t0
    lat = sorted(r[0] for r in results)
    errors = sum(1 for r in results if not r[1])
    return LoadReport(
        count=total, errors=errors, error_rate=round(errors / total, 4), rps=round(total / wall, 1),
        p50=round(_pct(lat, 50), 1), p95=round(_pct(lat, 95), 1), p99=round(_pct(lat, 99), 1), max=round(lat[-1], 1),
        concurrency=concurrency, think_time_s=think_time_s,
    )


def littles_law_concurrency(target_rps: float, avg_latency_s: float) -> int:
    if target_rps < 0 or avg_latency_s < 0:
        raise ValueError("inputs must be non-negative")
    return math.ceil(round(target_rps * avg_latency_s, 9))


def max_rps(concurrency: int, avg_latency_s: float) -> float:
    if avg_latency_s <= 0 or concurrency < 1:
        raise ValueError("need avg_latency_s > 0 and concurrency >= 1")
    return round(concurrency / avg_latency_s, 1)


def stage_breakdown(traces: list[dict]) -> list[tuple[str, float]]:
    totals = defaultdict(float)
    for t in traces:
        for stage, ms in t.items():
            totals[stage] += ms
    grand = sum(totals.values())
    return sorted(((s, round(v / grand, 3)) for s, v in totals.items()), key=lambda x: -x[1])


LABELS = ("measured", "simulated")


def report_line(rep: LoadReport, label: str, arrival_rps: float | None = None) -> str:
    if label not in LABELS:
        raise ValueError(f"label must be one of {LABELS}")
    model = "closed loop" if arrival_rps is None else f"open arrivals {arrival_rps} req/s"
    return (f"p50 {rep.p50} ms, p95 {rep.p95} ms, p99 {rep.p99} ms, max {rep.max} ms "
            f"(n={rep.count}, error rate {rep.error_rate}) | load model: {model}, "
            f"concurrency {rep.concurrency}, think time {rep.think_time_s} s | {label}")
