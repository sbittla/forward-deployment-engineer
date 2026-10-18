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
    raise NotImplementedError


def run_load(url: str, token: str, payload: dict, total: int, concurrency: int) -> LoadReport:
    raise NotImplementedError


def required_replicas(target_rps: float, p95_latency_s: float, concurrency_per_replica: int,
                      headroom: float = 0.3) -> int:
    """Little's law: in-flight = rps x latency; add headroom; at least 2 replicas for availability."""
    raise NotImplementedError
