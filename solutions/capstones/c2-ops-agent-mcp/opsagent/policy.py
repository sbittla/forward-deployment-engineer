"""Refund policy: deterministic code, never left to the model's judgement."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Decision:
    allowed: bool
    needs_approval: bool
    reason: str


@dataclass
class RefundPolicy:
    window_days: int = 30
    auto_limit: float = 100.0

    def evaluate(self, order: dict, amount: float, already_refunded: float, today: date) -> Decision:
        if order["status"] != "delivered" or not order.get("delivered_on"):
            return Decision(False, False, "order has not been delivered yet")
        age = (today - date.fromisoformat(order["delivered_on"])).days
        if age > self.window_days:
            return Decision(False, False, f"outside the {self.window_days}-day refund window ({age} days)")
        remaining = round(order["total"] - already_refunded, 2)
        if amount <= 0:
            return Decision(False, False, "amount must be positive")
        if amount > remaining:
            return Decision(False, False, f"amount exceeds the refundable balance of ${remaining:.2f}")
        if amount > self.auto_limit:
            return Decision(True, True, f"refunds over ${self.auto_limit:.2f} need supervisor approval")
        return Decision(True, False, "within policy")
