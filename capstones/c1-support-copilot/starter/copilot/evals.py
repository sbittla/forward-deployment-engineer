"""Golden-set evaluation and the launch bar agreed with the customer's AI governance board."""
import json
from pathlib import Path

from . import pii

LAUNCH_BAR = {"pass_rate": 0.9, "intent_accuracy": 0.9, "citation_precision": 0.95, "false_answer_rate": 0.0}


def load_golden(path) -> list[dict]:
    raise NotImplementedError


def _case_passes(case: dict, r) -> bool:
    raise NotImplementedError


def _slice(case: dict) -> str:
    raise NotImplementedError


def _retrieved_expected(copilot, case: dict, principal) -> bool:
    raise NotImplementedError


def run_golden(copilot, golden: list[dict], principal=None) -> dict:
    """Run every case as `principal` (None for a copilot whose retriever isn't permission-aware)."""
    raise NotImplementedError


def launch_bar(metrics: dict) -> tuple[bool, list[str]]:
    raise NotImplementedError


def run_security(copilot, probes: list[dict], principals: dict) -> dict:
    """Ask each probe as its principal; a leak is a forbidden document in the retrieved context or the citations."""
    raise NotImplementedError
