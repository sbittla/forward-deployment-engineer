import math
import time
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


def run_load(fn, total: int, concurrency: int) -> LoadReport:
    raise NotImplementedError


def littles_law_concurrency(target_rps: float, avg_latency_s: float) -> int:
    raise NotImplementedError


def max_rps(concurrency: int, avg_latency_s: float) -> float:
    raise NotImplementedError


def stage_breakdown(traces: list[dict]) -> list[tuple[str, float]]:
    raise NotImplementedError
