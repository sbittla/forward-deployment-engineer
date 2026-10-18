"""Append-only, hash-chained audit trail of everything the agent saw and did."""
import hashlib
import json

GENESIS = "0" * 64


class AuditLog:
    def __init__(self):
        self.entries: list[dict] = []

    def append(self, event: str, **data) -> dict:
        raise NotImplementedError

    def verify(self) -> bool:
        raise NotImplementedError

    def events(self) -> list[str]:
        raise NotImplementedError
