"""A constrained agent tool: `open_claim_review`, the copilot's only consequential action.

Opening a review pauses payment on a claim, so the tool enforces, in this order:
1. an execution budget per request (every attempt counts, so a looping model stops);
2. authorization: same tenant, the `claims` group, and either the assigned adjuster or a supervisor. An unknown
   claim gets the same `forbidden` as another tenant's claim, so the tool never confirms that a claim exists;
3. idempotency: a repeated idempotency key returns the first result instead of opening a second review, and the same
   key with different arguments is a conflict;
4. approval: without one the call returns `pending_approval` and changes nothing. A valid approval comes from a
   supervisor in the same tenant, for the same claim, who isn't the requester.
Every outcome is written to the audit log.
"""
import json
from dataclasses import dataclass
from pathlib import Path

TOOL_NAME = "open_claim_review"


class ToolError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


@dataclass(frozen=True)
class Approval:
    approver: object      # a tenancy.Principal
    claim_id: str


class ExecutionBudget:
    """At most `max_calls` tool calls in one request."""

    def __init__(self, max_calls: int = 3):
        self.max_calls, self.used = max_calls, 0

    def spend(self):
        raise NotImplementedError


def load_claims(path) -> dict:
    raise NotImplementedError


class ClaimReviewTool:
    def __init__(self, claims: dict):
        self.claims = claims
        self.reviews: dict[str, dict] = {}      # review_id -> review
        self._by_key: dict[str, tuple] = {}     # idempotency key -> (arguments, result)
        self.audit: list[dict] = []

    def _authorized(self, principal, claim_id: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def _approval_ok(principal, claim_id: str, approval) -> bool:
        raise NotImplementedError

    def _log(self, principal, claim_id, outcome, **extra):
        raise NotImplementedError

    def open_claim_review(self, principal, claim_id: str, reason: str, *, idempotency_key: str,
                          budget: ExecutionBudget, approval: Approval | None = None) -> dict:
        raise NotImplementedError


def execute_tool_calls(calls, tool: ClaimReviewTool, principal, request_id: str, budget: ExecutionBudget,
                       approvals: dict | None = None) -> list[dict]:
    """Run the model's proposed tool calls under the caller's identity. Never raises; errors become results.

    The model chooses arguments, never identity or approval: `principal` and `approvals` (claim_id -> Approval)
    come from the authenticated session, and the idempotency key is derived from the request id.
    """
    raise NotImplementedError
