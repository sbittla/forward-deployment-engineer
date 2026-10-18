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
    """Re-plan the remaining work from `as_of_day` using reported progress."""
    raise NotImplementedError


def workstream_rag(eng: dict) -> dict:
    """Earned-value style variance per workstream: (actual - planned progress), weighted by effort."""
    raise NotImplementedError
