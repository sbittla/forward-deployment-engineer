"""Evaluate how an agent got its answer: tool choice, order, arguments, efficiency and reliability across runs."""
import math
from dataclasses import dataclass, field


@dataclass
class TrajectoryScore:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    efficiency: float = 1.0
    steps: int = 0


def tool_calls(trajectory: list[dict]) -> list[dict]:
    raise NotImplementedError


def final_text(trajectory: list[dict]) -> str | None:
    raise NotImplementedError


def _is_subsequence(needle: list[str], haystack: list[str]) -> bool:
    raise NotImplementedError


def score_trajectory(trajectory: list[dict], spec: dict) -> TrajectoryScore:
    raise NotImplementedError


def tool_call_f1(trajectory: list[dict], expected_calls: list[dict]) -> dict:
    """Precision/recall over (name, arguments) pairs, as multisets."""
    raise NotImplementedError


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimate that at least one of k sampled runs passes, given c passes in n runs."""
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Estimate that all k sampled runs pass (pass^k): the reliability a customer actually experiences."""
    raise NotImplementedError


def run_suite(agent, cases: list[dict], trials: int = 1, k: int = 1) -> dict:
    """agent(task, trial) -> trajectory. Reports per-case pass counts, pass@k, pass^k and the most common failures."""
    raise NotImplementedError
