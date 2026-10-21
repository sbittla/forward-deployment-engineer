"""Baseline plan (PERT + critical path), forecast from actual progress, and workstream RAG status."""
import json
import math
from pathlib import Path

Z90 = 1.2816


def load_json(path) -> dict:
    raise NotImplementedError


def expected(t: dict) -> float:
    raise NotImplementedError


def _order(tasks):
    raise NotImplementedError


def schedule(tasks: list[dict], durations: dict | None = None, offset: float = 0.0) -> dict:
    """CPM: {id: {"es", "ef", "slack"}}. `durations` overrides expected durations (used for forecasting)."""
    raise NotImplementedError


def critical_path(tasks: list[dict]) -> list[str]:
    raise NotImplementedError


def estimate(tasks: list[dict]) -> tuple[float, float]:
    raise NotImplementedError


def forecast(eng: dict) -> dict:
    """Re-plan the remaining work from `as_of_day` using reported progress.

    Remaining duration = expected * (1 - progress); re-run `schedule` with those durations and `offset=as_of_day`.
    Returns {"baseline_finish_day", "forecast_finish_day", "slip_days"} (latest finish of each schedule, 1 dp).
    """
    raise NotImplementedError


def workstream_rag(eng: dict) -> dict:
    """Earned-value style variance per workstream: (actual - planned progress), weighted by effort.

    Planned progress of a task at `as_of_day` = (as_of_day - es) / (ef - es) on the baseline, clamped to [0, 1].
    variance = sum(expected * (actual - planned)) / sum(expected) over the workstream's tasks, rounded to 3 dp.
    RAG: green if variance >= -0.1, amber if >= -0.25, else red; a green workstream with a critical-path task more
    than 0.1 behind plan is amber. Returns {workstream: {"variance", "rag"}}.
    """
    raise NotImplementedError


def next_milestone(eng: dict) -> dict | None:
    """The first unfinished milestone (progress < 1.0) by baseline finish: {"milestone", "task", "acceptance",
    "baseline_day", "forecast_day"}, days rounded to 1 dp; None when every milestone is done."""
    raise NotImplementedError
