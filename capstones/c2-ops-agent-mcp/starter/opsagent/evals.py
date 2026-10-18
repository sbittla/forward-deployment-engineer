"""Scenario evals: replay scripted model behaviour against the real tools, policy and approval flow.

Scripts deliberately include bad model behaviour (over-refunds, wrong customer, injected instructions)
so the evals measure whether the *harness* keeps the business safe, not whether the model is polite.
"""
import json
from datetime import date
from pathlib import Path

from fde_kit import FakeLLM, LLMResponse, ToolCall

from .agent import OpsAgent
from .store import OrderStore


def script_llm(script: list[dict]) -> FakeLLM:
    raise NotImplementedError


def policy_violations(store: OrderStore, window_days: int = 30, auto_limit: float = 100.0) -> list[str]:
    """Independent re-check of every refund in the store against the written policy."""
    raise NotImplementedError


def run_scenarios(orders_path, scenarios_path) -> dict:
    raise NotImplementedError
