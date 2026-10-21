import time


def sign(body: str, secret: str, t: int) -> str:
    raise NotImplementedError


def apply_update(store: dict, record: dict) -> bool:
    raise NotImplementedError


def reconcile(client, store: dict, since: str) -> int:
    raise NotImplementedError


class WebhookReceiver:
    def __init__(self, secret: str | list[str], clock=time.time, tolerance: int = 300, dedupe_ttl: int = 3600,
                 store: dict | None = None):
        self.secret = secret
        self.clock = clock
        self.tolerance = tolerance
        self.dedupe_ttl = dedupe_ttl
        self.processed: list[dict] = []
        self.store = store

    def handle(self, headers: dict, body: str) -> tuple[int, str]:
        raise NotImplementedError
