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

    def get_token(self) -> str:
        raise NotImplementedError

    def invalidate(self) -> None:
        raise NotImplementedError

    def call_with_auth(self, fn):
        raise NotImplementedError
