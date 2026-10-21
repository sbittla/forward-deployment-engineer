"""Greedy prompt optimisation against a train split, judged once on a held-out test split."""
import hashlib
import json
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


def prompt_version(prompt: str) -> str:
    """First 12 hex characters of the SHA-256 of the prompt text: the version a record and a log line cite."""
    raise NotImplementedError


def dataset_hash(cases: list[dict]) -> str:
    """Freeze an evaluation set by content: any edited, added, removed or reordered case changes the hash."""
    raise NotImplementedError


def repeat_evaluate(prompt: str, cases: list[dict], model: Model, grader: Grader, runs: int = 3) -> dict:
    """Score the same prompt `runs` times. A sampled model gives different scores; the spread is the noise floor."""
    raise NotImplementedError


def wilson_interval(passes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a pass rate; honest at small n and at 0% or 100%."""
    raise NotImplementedError


def regression_gate(base: list[bool], cand: list[bool], protected: frozenset[int] = frozenset(),
                    max_drop: float = 0.0) -> dict:
    """Block a candidate whose pass rate falls more than `max_drop` below the baseline, or that breaks any
    protected (for example safety-tagged) case the baseline passed."""
    raise NotImplementedError


def experiment_record(name: str, base_prompt: str, cand_prompt: str, cases: list[dict], model: Model,
                      grader: Grader, seed: int = 0, test_frac: float = 0.3,
                      protected: frozenset[int] = frozenset()) -> dict:
    """Score baseline and candidate once each on the held-out split and return the fields a reviewer needs.
    `protected` holds indices into the test split."""
    raise NotImplementedError
