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


# --- Experiment record: versions, repeated runs, an interval and a regression gate -------------------------------

def _sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def prompt_version(prompt: str) -> str:
    """First 12 hex characters of the SHA-256 of the prompt text: the version a record and a log line cite."""
    return _sha12(prompt)


def dataset_hash(cases: list[dict]) -> str:
    """Freeze an evaluation set by content: any edited, added, removed or reordered case changes the hash."""
    return _sha12(json.dumps(cases, sort_keys=True, ensure_ascii=False))


def repeat_evaluate(prompt: str, cases: list[dict], model: Model, grader: Grader, runs: int = 3) -> dict:
    """Score the same prompt `runs` times. A sampled model gives different scores; the spread is the noise floor."""
    if runs < 1:
        raise ValueError("runs must be at least 1")
    scores = [evaluate(prompt, cases, model, grader) for _ in range(runs)]
    return {"runs": runs, "scores": scores, "mean": round(sum(scores) / runs, 4),
            "spread": round(max(scores) - min(scores), 4)}


def wilson_interval(passes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a pass rate; honest at small n and at 0% or 100%."""
    if n < 1 or not 0 <= passes <= n:
        raise ValueError("need 0 <= passes <= n and n >= 1")
    p = passes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)


def regression_gate(base: list[bool], cand: list[bool], protected: frozenset[int] = frozenset(),
                    max_drop: float = 0.0) -> dict:
    """Block a candidate whose pass rate falls more than `max_drop` below the baseline, or that breaks any
    protected (for example safety-tagged) case the baseline passed."""
    if len(base) != len(cand):
        raise ValueError("paired results must have equal length")
    broken = [i for i, (x, y) in enumerate(zip(base, cand)) if x and not y]
    reasons = []
    if base:
        b_rate, c_rate = sum(base) / len(base), sum(cand) / len(cand)
        if c_rate < b_rate - max_drop - 1e-12:
            reasons.append(f"pass rate {c_rate:.4f} is below baseline {b_rate:.4f} - {max_drop}")
    reasons += [f"protected case {i} regressed" for i in broken if i in protected]
    return {"passed": not reasons, "broken": broken, "reasons": reasons}


def experiment_record(name: str, base_prompt: str, cand_prompt: str, cases: list[dict], model: Model,
                      grader: Grader, seed: int = 0, test_frac: float = 0.3,
                      protected: frozenset[int] = frozenset()) -> dict:
    """Score baseline and candidate once each on the held-out split and return the fields a reviewer needs.
    `protected` holds indices into the test split."""
    _, test = split(cases, test_frac, seed)
    base, cand = run(base_prompt, test, model, grader), run(cand_prompt, test, model, grader)
    n = len(test)
    return {
        "experiment": name, "dataset": dataset_hash(cases), "seed": seed, "n_test": n,
        "baseline": {"prompt": prompt_version(base_prompt), "passes": sum(base),
                     "rate": round(sum(base) / n, 4), "ci95": wilson_interval(sum(base), n)},
        "candidate": {"prompt": prompt_version(cand_prompt), "passes": sum(cand),
                      "rate": round(sum(cand) / n, 4), "ci95": wilson_interval(sum(cand), n)},
        "mcnemar_p": mcnemar_p(base, cand),
        "gate": regression_gate(base, cand, protected),
    }
