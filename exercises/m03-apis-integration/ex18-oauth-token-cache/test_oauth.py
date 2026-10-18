import threading
import time

import pytest


class Transport:
    def __init__(self, delay=0.0):
        self.calls, self.delay = [], delay

    def __call__(self, url, form):
        self.calls.append((url, dict(form)))
        time.sleep(self.delay)
        return {"access_token": f"tok{len(self.calls)}", "expires_in": 3600, "token_type": "Bearer"}


class Clock:
    t = 0.0

    def __call__(self):
        return self.t


class Unauthorized(Exception):
    status = 401


def test_caches_until_skew(impl):
    tr, clk = Transport(), Clock()
    p = impl.TokenProvider("https://idp/token", "cid", "sec", tr, clock=clk, skew=60)
    assert p.get_token() == "tok1"
    assert tr.calls[0] == ("https://idp/token", {"grant_type": "client_credentials", "client_id": "cid",
                                                 "client_secret": "sec"})
    clk.t = 3539
    assert p.get_token() == "tok1"
    clk.t = 3540
    assert p.get_token() == "tok2"


def test_single_flight(impl):
    tr = Transport(delay=0.05)
    p = impl.TokenProvider("u", "c", "s", tr)
    out = []
    threads = [threading.Thread(target=lambda: out.append(p.get_token())) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(tr.calls) == 1 and set(out) == {"tok1"}


def test_retry_once_on_401(impl):
    tr = Transport()
    p = impl.TokenProvider("u", "c", "s", tr)
    seen = []

    def api(token):
        seen.append(token)
        if token == "tok1":
            raise Unauthorized()
        return "data"

    assert p.call_with_auth(api) == "data"
    assert seen == ["tok1", "tok2"]


def test_401_twice_propagates_and_other_errors(impl):
    p = impl.TokenProvider("u", "c", "s", Transport())

    def always401(token):
        raise Unauthorized()

    with pytest.raises(Unauthorized):
        p.call_with_auth(always401)

    def boom(token):
        raise ValueError("x")

    with pytest.raises(ValueError):
        p.call_with_auth(boom)


def test_invalidate(impl):
    tr = Transport()
    p = impl.TokenProvider("u", "c", "s", tr)
    p.get_token()
    p.invalidate()
    assert p.get_token() == "tok2"
