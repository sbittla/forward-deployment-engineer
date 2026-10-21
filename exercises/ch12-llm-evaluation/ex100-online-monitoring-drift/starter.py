"""Online quality monitoring for a deployed LLM feature: input drift, live judge scores, and review sampling."""
import hashlib
import math
from dataclasses import dataclass

EPS = 1e-4


def _psi_terms(expected: list[float], actual: list[float]) -> float:
    raise NotImplementedError


def quantile_edges(values: list[float], bins: int) -> list[float]:
    raise NotImplementedError


def _bucket(x: float, edges: list[float]) -> int:
    raise NotImplementedError


def psi(baseline: list[float], current: list[float], bins: int = 10) -> float:
    """Population stability index of a numeric feature, binned at the baseline's quantiles."""
    raise NotImplementedError


def category_psi(baseline: dict[str, int], current: dict[str, int]) -> float:
    raise NotImplementedError


def drift_level(value: float) -> str:
    raise NotImplementedError


def p95(values: list[float]) -> float:
    raise NotImplementedError


@dataclass
class Thresholds:
    min_samples: int = 50
    judge_drop: float = 0.05          # absolute drop in judge pass rate vs baseline
    refusal_rate: float = 0.05
    p95_latency_ms: float = 4000
    cost_per_conv: float = 0.10


def check_window(baseline: dict, window: list[dict], t: Thresholds = Thresholds()) -> list[dict]:
    """baseline: {"input_len": [...], "intents": {...}, "judge_pass": float}.
    window records: {"input_len", "intent", "judge_pass": bool | None, "refused", "latency_ms", "cost"}."""
    raise NotImplementedError


def sample_for_review(records: list[dict], rate: float, always=lambda r: False) -> list[str]:
    """Deterministic hash sampling (stable across reruns and machines) plus everything `always` flags."""
    raise NotImplementedError
