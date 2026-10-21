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
    concurrency: int = 0
    think_time_s: float = 0.0


def run_load(fn, total: int, concurrency: int, think_time_s: float = 0.0) -> LoadReport:
    raise NotImplementedError


def littles_law_concurrency(target_rps: float, avg_latency_s: float) -> int:
    raise NotImplementedError


def max_rps(concurrency: int, avg_latency_s: float) -> float:
    raise NotImplementedError


def stage_breakdown(traces: list[dict]) -> list[tuple[str, float]]:
    raise NotImplementedError


def report_line(rep: LoadReport, label: str, arrival_rps: float | None = None) -> str:
    raise NotImplementedError
