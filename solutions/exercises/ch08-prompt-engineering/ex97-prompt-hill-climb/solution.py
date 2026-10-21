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
        return round(self.train - self.test, 4)


def split(cases: list[dict], test_frac: float = 0.3, seed: int = 0) -> tuple[list[dict], list[dict]]:
    if not 0 < test_frac < 1:
        raise ValueError("test_frac must be between 0 and 1")
    shuffled = list(cases)
    random.Random(seed).shuffle(shuffled)
    n_test = max(1, round(len(shuffled) * test_frac))
    return shuffled[n_test:], shuffled[:n_test]


def run(prompt: str, cases: list[dict], model: Model, grader: Grader) -> list[bool]:
    return [grader(model(prompt, c["input"]), c["expected"]) for c in cases]


def evaluate(prompt: str, cases: list[dict], model: Model, grader: Grader) -> float:
    results = run(prompt, cases, model, grader)
    return round(sum(results) / len(results), 4) if results else 0.0


def hill_climb(base_prompt: str, edits: dict[str, Callable[[str], str]], train: list[dict], test: list[dict],
               model: Model, grader: Grader, max_rounds: int = 5, min_gain: float = 0.0) -> ClimbResult:
    """Each round, try every unused edit on the current prompt; keep the best if it beats the current train score
    by more than `min_gain`. The test split is scored once, at the end."""
    prompt, score = base_prompt, evaluate(base_prompt, train, model, grader)
    history = [{"round": 0, "edit": None, "train": score}]
    unused = dict(edits)
    for rnd in range(1, max_rounds + 1):
        trials = [(evaluate(fn(prompt), train, model, grader), name) for name, fn in unused.items()]
        if not trials:
            break
        best_score, best_name = max(trials, key=lambda t: (t[0], -list(edits).index(t[1])))
        if best_score <= score + min_gain:
            break
        prompt, score = unused.pop(best_name)(prompt), best_score
        history.append({"round": rnd, "edit": best_name, "train": score})
    return ClimbResult(prompt, score, evaluate(prompt, test, model, grader), history)


def mcnemar_p(base: list[bool], cand: list[bool]) -> float:
    """Exact two-sided McNemar test on paired outcomes: are the discordant cases balanced?"""
    if len(base) != len(cand):
        raise ValueError("paired results must have equal length")
    b = sum(1 for x, y in zip(base, cand) if x and not y)
    c = sum(1 for x, y in zip(base, cand) if y and not x)
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n
    return min(1.0, round(2 * tail, 6))
