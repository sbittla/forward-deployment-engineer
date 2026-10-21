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
        if self.used >= self.max_calls:
            raise ToolError("budget_exceeded", f"tool budget of {self.max_calls} calls per request used up")
        self.used += 1


def load_claims(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class ClaimReviewTool:
    def __init__(self, claims: dict):
        self.claims = claims
        self.reviews: dict[str, dict] = {}      # review_id -> review
        self._by_key: dict[str, tuple] = {}     # idempotency key -> (arguments, result)
        self.audit: list[dict] = []

    def _authorized(self, principal, claim_id: str) -> bool:
        claim = self.claims.get(claim_id)
        if principal is None or claim is None or claim["tenant"] != principal.tenant:
            return False
        if "claims" not in principal.groups:
            return False
        return claim["adjuster"] == principal.user or "supervisors" in principal.groups

    @staticmethod
    def _approval_ok(principal, claim_id: str, approval) -> bool:
        a = approval.approver
        return (approval.claim_id == claim_id and a is not None and a.tenant == principal.tenant
                and "supervisors" in a.groups and a.user != principal.user)

    def _log(self, principal, claim_id, outcome, **extra):
        self.audit.append({"tool": TOOL_NAME, "user": getattr(principal, "user", None), "claim_id": claim_id,
                           "outcome": outcome, **extra})

    def open_claim_review(self, principal, claim_id: str, reason: str, *, idempotency_key: str,
                          budget: ExecutionBudget, approval: Approval | None = None) -> dict:
        try:
            budget.spend()
        except ToolError:
            self._log(principal, claim_id, "budget_exceeded")
            raise
        if not self._authorized(principal, claim_id):
            self._log(principal, claim_id, "forbidden")
            raise ToolError("forbidden", "not allowed to open a review on this claim")
        args = (principal.user, claim_id, reason)
        if idempotency_key in self._by_key:
            first_args, result = self._by_key[idempotency_key]
            if first_args != args:
                self._log(principal, claim_id, "idempotency_conflict")
                raise ToolError("idempotency_conflict", "idempotency key reused with different arguments")
            self._log(principal, claim_id, "replayed", review_id=result["review_id"])
            return {**result, "replayed": True}
        if approval is None:
            self._log(principal, claim_id, "pending_approval")
            return {"status": "pending_approval", "claim_id": claim_id}
        if not self._approval_ok(principal, claim_id, approval):
            self._log(principal, claim_id, "approval_invalid")
            raise ToolError("approval_invalid", "approval must come from another supervisor for this claim")
        review_id = f"RV-{len(self.reviews) + 1:04d}"
        self.reviews[review_id] = {"claim_id": claim_id, "reason": reason, "requested_by": principal.user,
                                   "approved_by": approval.approver.user}
        result = {"status": "opened", "review_id": review_id, "claim_id": claim_id, "replayed": False}
        self._by_key[idempotency_key] = (args, result)
        self._log(principal, claim_id, "opened", review_id=review_id, approved_by=approval.approver.user)
        return result


def execute_tool_calls(calls, tool: ClaimReviewTool, principal, request_id: str, budget: ExecutionBudget,
                       approvals: dict | None = None) -> list[dict]:
    """Run the model's proposed tool calls under the caller's identity. Never raises; errors become results.

    The model chooses arguments, never identity or approval: `principal` and `approvals` (claim_id -> Approval)
    come from the authenticated session, and the idempotency key is derived from the request id.
    """
    approvals = approvals or {}
    out = []
    for call in calls:
        if call.name != TOOL_NAME:
            out.append({"status": "error", "error": "unknown_tool", "tool": call.name})
            continue
        claim_id = str(call.arguments.get("claim_id", ""))
        try:
            out.append(tool.open_claim_review(
                principal, claim_id, str(call.arguments.get("reason", "")),
                idempotency_key=f"{request_id}:{claim_id}", budget=budget, approval=approvals.get(claim_id)))
        except ToolError as e:
            out.append({"status": "error", "error": e.code, "claim_id": claim_id})
    return out
