"""Append-only, hash-chained audit trail of everything the agent saw and did."""
import hashlib
import json

GENESIS = "0" * 64


class AuditLog:
    def __init__(self):
        self.entries: list[dict] = []

    def append(self, event: str, **data) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        body = {"seq": len(self.entries) + 1, "event": event, "data": data, "prev_hash": prev}
        body["hash"] = hashlib.sha256((prev + json.dumps(body, sort_keys=True, default=str)).encode()).hexdigest()
        self.entries.append(body)
        return body

    def verify(self) -> bool:
        prev = GENESIS
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            digest = hashlib.sha256((prev + json.dumps(body, sort_keys=True, default=str)).encode()).hexdigest()
            if e["prev_hash"] != prev or e["hash"] != digest:
                return False
            prev = e["hash"]
        return True

    def events(self) -> list[str]:
        return [e["event"] for e in self.entries]
