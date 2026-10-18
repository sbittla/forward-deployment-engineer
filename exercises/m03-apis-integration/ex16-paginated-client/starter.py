import time
from dataclasses import dataclass, field


@dataclass
class Response:
    status: int
    headers: dict = field(default_factory=dict)
    body: dict | list | None = None


class ApiError(Exception):
    def __init__(self, status, body=None):
        super().__init__(f"HTTP {status}: {body}")
        self.status, self.body = status, body


class ApiClient:
    def __init__(self, base_url, token, transport, sleep=time.sleep, clock=time.time, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.transport = transport
        self.sleep = sleep
        self.clock = clock
        self.max_retries = max_retries

    def get(self, path, params=None):
        raise NotImplementedError

    def list_all(self, path, params=None, max_pages=1000):
        raise NotImplementedError
