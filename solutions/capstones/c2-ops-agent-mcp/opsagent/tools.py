"""Customer-scoped tools with schema validation, policy enforcement and an approval queue."""
import json
from dataclasses import dataclass, field

from .policy import RefundPolicy


class ToolError(Exception):
    """An expected, user-safe failure whose message the model may read."""


TYPES = {"string": str, "number": (int, float), "integer": int, "object": dict}


def validate(schema: dict, args) -> list[str]:
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    problems = [f"{k} is required" for k in schema.get("required", []) if k not in args]
    props = schema.get("properties", {})
    for k, v in args.items():
        if k not in props:
            problems.append(f"{k} is not an allowed argument")
            continue
        t = props[k].get("type")
        if t and (not isinstance(v, TYPES[t]) or isinstance(v, bool)):
            problems.append(f"{k} must be a {t}")
        elif "minimum" in props[k] and v < props[k]["minimum"]:
            problems.append(f"{k} must be >= {props[k]['minimum']}")
    return problems


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
        req = {"approval_id": f"AP-{len(self.pending) + len(self.resolved) + 1}", "order_id": order_id,
               "amount": amount, "reason": reason, "customer": requested_for}
        self.pending.append(req)
        self.audit.append("approval_requested", **req)
        return req["approval_id"]

    def resolve(self, approval_id: str, approved: bool, approver: str) -> dict:
        req = next(r for r in self.pending if r["approval_id"] == approval_id)
        self.pending.remove(req)
        req = {**req, "approved": approved, "approver": approver}
        if approved:
            req["refund_id"] = self.store.add_refund(req["order_id"], req["amount"], req["reason"], approver)
        self.resolved.append(req)
        self.audit.append("approval_resolved", **req)
        return req


class Registry:
    def __init__(self, tools: list[Tool], audit):
        self.tools = {t.name: t for t in tools}
        self.audit = audit

    def specs(self) -> list[dict]:
        return [{"name": t.name, "description": t.description, "inputSchema": t.schema} for t in self.tools.values()]

    def call(self, name: str, args) -> tuple[str, bool]:
        tool = self.tools.get(name)
        if tool is None:
            return f"Unknown tool '{name}'. Available: {', '.join(sorted(self.tools))}", True
        problems = validate(tool.schema, args)
        if problems:
            self.audit.append("tool_rejected", tool=name, problems=problems)
            return f"Invalid arguments for {name}:\n" + "\n".join(f"- {p}" for p in problems), True
        try:
            result = tool.fn(**args)
        except ToolError as e:
            self.audit.append("tool_error", tool=name, args=args, error=str(e))
            return str(e), True
        except Exception as e:  # unexpected failures never leak details to the model
            self.audit.append("tool_crash", tool=name, error=type(e).__name__)
            return f"Tool {name} failed: {type(e).__name__}", True
        self.audit.append("tool_ok", tool=name, args=args)
        return json.dumps(result), False


def build_tools(store, policy: RefundPolicy, customer_email: str, approvals: ApprovalQueue, audit) -> Registry:
    """Tools are bound to one authenticated customer: they cannot see or touch anyone else's orders."""

    def owned(order_id: str) -> dict:
        order = store.get_order(order_id)
        if order is None or order["customer_email"] != customer_email:
            raise ToolError(f"Order {order_id} was not found on this customer's account.")
        return order

    def get_order(order_id: str):
        o = owned(order_id)
        return {**o, "refunded": store.refunded_total(order_id)}

    def list_orders():
        return [{"order_id": o["order_id"], "status": o["status"], "items": o["items"], "total": o["total"]}
                for o in store.orders_for(customer_email)]

    def issue_refund(order_id: str, amount: float, reason: str):
        order = owned(order_id)
        decision = policy.evaluate(order, float(amount), store.refunded_total(order_id), store.today)
        if not decision.allowed:
            raise ToolError(f"Refund not allowed: {decision.reason}.")
        if decision.needs_approval:
            approval_id = approvals.request(order_id, float(amount), reason, customer_email)
            return {"status": "pending_approval", "approval_id": approval_id, "reason": decision.reason}
        refund_id = store.add_refund(order_id, float(amount), reason, "auto-policy")
        return {"status": "refunded", "refund_id": refund_id, "amount": float(amount)}

    order_schema = {"type": "object", "required": ["order_id"], "properties": {"order_id": {"type": "string"}}}
    refund_schema = {"type": "object", "required": ["order_id", "amount", "reason"], "properties": {
        "order_id": {"type": "string"}, "amount": {"type": "number", "minimum": 0.01}, "reason": {"type": "string"}}}
    return Registry([
        Tool("get_order", "Look up one of the customer's orders, including how much has been refunded.", order_schema,
             get_order),
        Tool("list_orders", "List the customer's orders with status.", {"type": "object", "properties": {}},
             list_orders),
        Tool("issue_refund", "Refund part or all of a delivered order. Large refunds go to a supervisor.",
             refund_schema, issue_refund, side_effect=True),
    ], audit)
