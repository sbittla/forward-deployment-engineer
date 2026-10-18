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


class WebhookReceiver:
    def __init__(self, secret: str, clock=time.time, tolerance: int = 300, dedupe_ttl: int = 3600):
        self.secret = secret
        self.clock = clock
        self.tolerance = tolerance
        self.dedupe_ttl = dedupe_ttl
        self.processed: list[dict] = []
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
        return 202, "accepted"
