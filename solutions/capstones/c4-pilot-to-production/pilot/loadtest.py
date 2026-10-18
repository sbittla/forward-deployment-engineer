"""Small HTTP load generator and a Little's-law capacity estimate."""
import json
import math
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass
class LoadReport:
    count: int
    errors: int
    rps: float
    p50_ms: float
    p95_ms: float


def _pct(vals, p):
    vals = sorted(vals)
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def run_load(url: str, token: str, payload: dict, total: int, concurrency: int) -> LoadReport:
    data = json.dumps(payload).encode()

    def one(_):
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                ok = r.status == 200
                r.read()
        except (urllib.error.URLError, OSError):
            ok = False
        return (time.perf_counter() - t0) * 1000, ok

    t0 = time.perf_counter()
    with ThreadPoolExecutor(concurrency) as ex:
        results = list(ex.map(one, range(total)))
    wall = time.perf_counter() - t0
    lat = [r[0] for r in results]
    return LoadReport(total, sum(not r[1] for r in results), round(total / wall, 1),
                      round(_pct(lat, 50), 1), round(_pct(lat, 95), 1))


def required_replicas(target_rps: float, p95_latency_s: float, concurrency_per_replica: int,
                      headroom: float = 0.3) -> int:
    """Little's law: in-flight = rps x latency; add headroom; at least 2 replicas for availability."""
    in_flight = target_rps * p95_latency_s * (1 + headroom)
    return max(2, math.ceil(round(in_flight / concurrency_per_replica, 9)))
