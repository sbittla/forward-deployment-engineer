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


def _h(headers: dict, name: str):
    name = name.lower()
    for k, v in (headers or {}).items():
        if k.lower() == name:
            return v
    return None


class ApiClient:
    def __init__(self, base_url, token, transport, sleep=time.sleep, clock=time.time, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.transport = transport
        self.sleep = sleep
        self.clock = clock
        self.max_retries = max_retries
        self._wait_until = 0.0

    def _respect_limit(self):
        delay = self._wait_until - self.clock()
        if delay > 0:
            self.sleep(delay)
        self._wait_until = 0.0

    def _note_limit(self, resp):
        if _h(resp.headers, "X-RateLimit-Remaining") == "0":
            reset = _h(resp.headers, "X-RateLimit-Reset")
            if reset is not None:
                self._wait_until = float(reset)

    def get(self, path, params=None):
        url = self.base_url + "/" + path.lstrip("/")
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        for attempt in range(self.max_retries + 1):
            self._respect_limit()
            resp = self.transport("GET", url, headers, dict(params or {}))
            self._note_limit(resp)
            if resp.status == 429:
                if attempt == self.max_retries:
                    raise ApiError(429, resp.body)
                self.sleep(float(_h(resp.headers, "Retry-After") or 1))
                continue
            if resp.status >= 400:
                raise ApiError(resp.status, resp.body)
            return resp.body
        raise AssertionError("unreachable")

    def list_all(self, path, params=None, max_pages=1000):
        params = dict(params or {})
        for _ in range(max_pages):
            body = self.get(path, params)
            yield from body.get("data", [])
            cursor = body.get("next_cursor")
            if not cursor:
                return
            params["cursor"] = cursor
        raise ApiError(0, f"exceeded max_pages={max_pages}; possible cursor loop")
