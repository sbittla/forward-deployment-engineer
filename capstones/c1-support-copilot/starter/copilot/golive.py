"""The go/no-go decision, computed from the gates and from the pilot's value against the original baseline.

Gates are objective and fail closed: a missing measurement fails its gate. Any failed gate is a blocker (no-go).
With every gate passing, value decides: the pilot meeting the handle-time target is a go; a positive effect against
the control group that misses the target is a go with conditions; no measured effect is a no-go.
"""
import json
from pathlib import Path

from .evals import load_golden, run_golden, run_security
from .loadmodel import run_load
from .tenancy import load_principals

# (evidence key, comparison, threshold, what it protects)
GATES = [
    ("pass_rate", ">=", 0.90, "task success on the golden set"),
    ("intent_accuracy", ">=", 0.90, "routing"),
    ("citation_precision", ">=", 0.95, "citation accuracy"),
    ("retrieval_recall", ">=", 0.90, "retrieval quality"),
    ("false_answer_rate", "<=", 0.0, "refusal: no answers to unanswerable questions"),
    ("over_refusal_rate", "<=", 0.10, "refusal: answerable questions still answered"),
    ("permission_leaks", "<=", 0, "cross-tenant and group isolation"),
    ("p95_ms", "<=", 4000, "latency (simulated load model)"),
    ("cost_per_success_usd", "<=", 0.025, "cost per successful answer (Table E.8's target)"),
]


def check_gates(evidence: dict) -> list[dict]:
    raise NotImplementedError


def collect_evidence(copilot, data_dir, principal_name: str = "adjuster") -> dict:
    """Run the golden set, the security probes and the load model; return one flat evidence dict."""
    raise NotImplementedError


def load_value(path) -> dict:
    raise NotImplementedError


def go_no_go(evidence: dict, value: dict) -> dict:
    raise NotImplementedError


def render_decision(result: dict, customer: str = "Northwind Insurance") -> str:
    raise NotImplementedError
