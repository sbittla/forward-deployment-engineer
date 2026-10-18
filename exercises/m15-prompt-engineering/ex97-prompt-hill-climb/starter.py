"""Greedy prompt optimisation against a train split, judged once on a held-out test split."""
import math
import random
from dataclasses import dataclass, field
from typing import Callable

Model = Callable[[str, str], str]          # (prompt, input) -> output
Grader = Callable[[str, str], bool]        # (output, expected) -> passed


@dataclass
class ClimbResult:
    prompt: str
    train: float
    test: float
    history: list[dict] = field(default_factory=list)

    @property
    def overfit_gap(self) -> float:
        raise NotImplementedError


def split(cases: list[dict], test_frac: float = 0.3, seed: int = 0) -> tuple[list[dict], list[dict]]:
    raise NotImplementedError


def run(prompt: str, cases: list[dict], model: Model, grader: Grader) -> list[bool]:
    raise NotImplementedError


def evaluate(prompt: str, cases: list[dict], model: Model, grader: Grader) -> float:
    raise NotImplementedError


def hill_climb(base_prompt: str, edits: dict[str, Callable[[str], str]], train: list[dict], test: list[dict],
               model: Model, grader: Grader, max_rounds: int = 5, min_gain: float = 0.0) -> ClimbResult:
    """Each round, try every unused edit on the current prompt; keep the best if it beats the current train score
    by more than `min_gain`. The test split is scored once, at the end."""
    raise NotImplementedError


def mcnemar_p(base: list[bool], cand: list[bool]) -> float:
    """Exact two-sided McNemar test on paired outcomes: are the discordant cases balanced?"""
    raise NotImplementedError
