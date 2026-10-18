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
        raise NotImplementedError
