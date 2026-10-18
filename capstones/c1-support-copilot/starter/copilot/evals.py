"""Golden-set evaluation and the launch bar agreed with the customer's AI governance board."""
import json
from pathlib import Path

LAUNCH_BAR = {"pass_rate": 0.9, "intent_accuracy": 0.9, "citation_precision": 0.95, "false_answer_rate": 0.0}


def load_golden(path) -> list[dict]:
    raise NotImplementedError


def _case_passes(case: dict, r) -> bool:
    raise NotImplementedError


def run_golden(copilot, golden: list[dict]) -> dict:
    raise NotImplementedError


def launch_bar(metrics: dict) -> tuple[bool, list[str]]:
    raise NotImplementedError
