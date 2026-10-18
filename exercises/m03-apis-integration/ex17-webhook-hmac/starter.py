import time


def sign(body: str, secret: str, t: int) -> str:
    raise NotImplementedError


class WebhookReceiver:
    def __init__(self, secret: str, clock=time.time, tolerance: int = 300, dedupe_ttl: int = 3600):
        self.secret = secret
        self.clock = clock
        self.tolerance = tolerance
        self.dedupe_ttl = dedupe_ttl
        self.processed: list[dict] = []

    def handle(self, headers: dict, body: str) -> tuple[int, str]:
        raise NotImplementedError
