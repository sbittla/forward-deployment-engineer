import hashlib
import hmac
import json
import time


def _mac(secret: str, t: int, body: str) -> str:
    return hmac.new(secret.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()


def sign(body: str, secret: str, t: int) -> str:
    return f"t={t},v1={_mac(secret, t, body)}"


def _parse(header: str):
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    return int(parts["t"]), parts["v1"]


def apply_update(store: dict, record: dict) -> bool:
    """Store the record if it's newer than our copy; return True if it was applied."""
    current = store.get(record["id"])
    if current is not None and current["version"] >= record["version"]:
        return False
    store[record["id"]] = record
    return True


def reconcile(client, store: dict, since: str) -> int:
    """Catch anything the webhooks missed, through the same code path."""
    applied = 0
    for record in client.list_all("/cases", {"updated_since": since}):
        applied += apply_update(store, record)
    return applied


class WebhookReceiver:
    def __init__(self, secret: str, clock=time.time, tolerance: int = 300, dedupe_ttl: int = 3600,
                 store: dict | None = None):
        self.secret = secret
        self.clock = clock
        self.tolerance = tolerance
        self.dedupe_ttl = dedupe_ttl
        self.processed: list[dict] = []
        self.store = store
        self._seen: dict[str, float] = {}

    def handle(self, headers: dict, body: str) -> tuple[int, str]:
        now = self.clock()
        self._seen = {k: ts for k, ts in self._seen.items() if now - ts <= self.dedupe_ttl}

        header = next((v for k, v in headers.items() if k.lower() == "x-signature"), None)
        if not header:
            return 401, "missing signature"
        try:
            t, sig = _parse(header)
        except (KeyError, ValueError):
            return 401, "malformed signature"
        if not hmac.compare_digest(sig, _mac(self.secret, t, body)):
            return 401, "bad signature"
        if abs(now - t) > self.tolerance:
            return 400, "stale"
        try:
            event = json.loads(body)
            event_id = event["id"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return 400, "body must be JSON with an id"
        if event_id in self._seen:
            return 200, "duplicate"
        self._seen[event_id] = now
        self.processed.append(event)
        if self.store is not None and isinstance(event.get("data"), dict):
            apply_update(self.store, event["data"])
        return 202, "accepted"
