import threading
import time


class TokenProvider:
    def __init__(self, token_url, client_id, client_secret, transport, clock=time.time, skew=60):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.transport = transport
        self.clock = clock
        self.skew = skew
        self._token: str | None = None
        self._expires_at = 0.0
        self._lock = threading.Lock()

    def _valid(self) -> bool:
        return self._token is not None and self.clock() < self._expires_at

    def get_token(self) -> str:
        if self._valid():
            return self._token
        with self._lock:  # single-flight: late arrivals see the fresh token
            if not self._valid():
                issued = self.clock()
                data = self.transport(self.token_url, {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                })
                self._token = data["access_token"]
                self._expires_at = issued + float(data["expires_in"]) - self.skew
            return self._token

    def invalidate(self) -> None:
        with self._lock:
            self._token, self._expires_at = None, 0.0

    def call_with_auth(self, fn):
        try:
            return fn(self.get_token())
        except Exception as exc:
            if getattr(exc, "status", None) != 401:
                raise
        self.invalidate()
        return fn(self.get_token())
