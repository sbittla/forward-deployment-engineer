import threading
import time


class TokenProvider:
    def __init__(self, token_url, client_id, client_secret, transport, clock=time.time, skew=60):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret  # a string, or a zero-arg callable read at each refresh (rotation)
        self.transport = transport
        self.clock = clock
        self.skew = skew
        self._token: str | None = None
        self._expires_at = 0.0
        self._blocked_until = 0.0  # set by a 429 from the token endpoint
        self._throttle: Exception | None = None
        self._lock = threading.Lock()

    def _valid(self) -> bool:
        return self._token is not None and self.clock() < self._expires_at

    def _secret(self) -> str:
        return self.client_secret() if callable(self.client_secret) else self.client_secret

    def get_token(self) -> str:
        if self._valid():
            return self._token
        with self._lock:  # single-flight: late arrivals see the fresh token, or the throttle
            if self._valid():
                return self._token
            if self._throttle is not None and self.clock() < self._blocked_until:
                raise self._throttle  # the token endpoint asked us to wait: don't call it again yet
            issued = self.clock()
            try:
                data = self.transport(self.token_url, {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self._secret(),
                })
            except Exception as exc:
                if getattr(exc, "status", None) == 429:
                    ra = getattr(exc, "retry_after", None)
                    self._throttle = exc
                    self._blocked_until = issued + (ra if isinstance(ra, (int, float)) else 1)
                raise  # fail closed: nothing cached, no token handed out
            self._throttle = None
            self._token = data["access_token"]
            self._expires_at = issued + float(data["expires_in"]) - self.skew
            return self._token

    def invalidate(self) -> None:
        with self._lock:
            self._token, self._expires_at = None, 0.0

    def call_with_auth(self, fn):
        token = self.get_token()  # a token-endpoint error propagates: it isn't the API's 401
        try:
            return fn(token)
        except Exception as exc:
            if getattr(exc, "status", None) != 401:
                raise
        self.invalidate()
        return fn(self.get_token())
