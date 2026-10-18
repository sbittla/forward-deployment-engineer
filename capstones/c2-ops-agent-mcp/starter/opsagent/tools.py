"""Customer-scoped tools with schema validation, policy enforcement and an approval queue."""
import json
from dataclasses import dataclass, field

from .policy import RefundPolicy


class ToolError(Exception):
    """An expected, user-safe failure whose message the model may read."""


TYPES = {"string": str, "number": (int, float), "integer": int, "object": dict}


def validate(schema: dict, args) -> list[str]:
    raise NotImplementedError


@dataclass
class Tool:
    name: str
    description: str
    schema: dict
    fn: object
    side_effect: bool = False


class ApprovalQueue:
    def __init__(self, store, audit):
        self.store, self.audit = store, audit
        self.pending: list[dict] = []
        self.resolved: list[dict] = []

    def request(self, order_id: str, amount: float, reason: str, requested_for: str) -> str:
        raise NotImplementedError

    def resolve(self, approval_id: str, approved: bool, approver: str) -> dict:
        raise NotImplementedError


class Registry:
    def __init__(self, tools: list[Tool], audit):
        self.tools = {t.name: t for t in tools}
        self.audit = audit

    def specs(self) -> list[dict]:
        raise NotImplementedError

    def call(self, name: str, args) -> tuple[str, bool]:
        raise NotImplementedError


def build_tools(store, policy: RefundPolicy, customer_email: str, approvals: ApprovalQueue, audit) -> Registry:
    """Tools are bound to one authenticated customer: they cannot see or touch anyone else's orders."""

    raise NotImplementedError
