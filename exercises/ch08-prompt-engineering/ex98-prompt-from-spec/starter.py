"""Compile a customer's policy spec into a system prompt, trace every policy, and test conformance."""
import re
from dataclasses import dataclass
from html import escape

POLICY_ID = re.compile(r"^[A-Z]+-\d+$")
KINDS = ("must", "must_not", "escalate")
KIND_PREFIX = {"must": "Always", "must_not": "Never", "escalate": "Hand off to a human when"}


@dataclass(frozen=True)
class Policy:
    id: str
    kind: str
    rule: str
    why: str = ""
    tests: tuple = ()          # ({"input": str, "expect_contains": [...], "expect_absent": [...]}, ...)


def load_policies(rows: list[dict]) -> list[Policy]:
    raise NotImplementedError


def build_system_prompt(role: str, policies: list[Policy], output_format: str) -> str:
    raise NotImplementedError


def trace(prompt: str, policies: list[Policy]) -> dict[str, bool]:
    raise NotImplementedError


def coverage(policies: list[Policy]) -> float:
    raise NotImplementedError


def generate_cases(policies: list[Policy]) -> list[dict]:
    raise NotImplementedError


def run_conformance(llm, prompt: str, policies: list[Policy]) -> dict:
    raise NotImplementedError


def diff_policies(old: list[Policy], new: list[Policy]) -> dict[str, list[str]]:
    raise NotImplementedError
