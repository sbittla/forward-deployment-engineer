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


def test_boundary_persistent_401_costs_two_token_calls(impl):
    tr = Transport()
    p = impl.TokenProvider("u", "c", "s", tr)

    def always401(token):
        raise Unauthorized()

    with pytest.raises(Unauthorized):
        p.call_with_auth(always401)
    assert len(tr.calls) == 2  # the first token and one refresh: never a loop


# Negative tests: invalid credentials, an unreachable identity provider, a rate-limited token endpoint, rotation

class TokenError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(status)
        self.status = status
        if retry_after is not None:
            self.retry_after = retry_after


class FailingTransport:
    def __init__(self, errors):
        self.errors, self.calls = list(errors), []

    def __call__(self, url, form):
        self.calls.append(dict(form))
        if self.errors:
            raise self.errors.pop(0)
        return {"access_token": f"tok{len(self.calls)}", "expires_in": 3600, "token_type": "Bearer"}


def test_invalid_client_fails_closed(impl):
    # Wrong client secret: the token endpoint answers 401 invalid_client. No token is cached or handed to the API.
    tr = FailingTransport([TokenError(401), TokenError(401)])
    p = impl.TokenProvider("u", "c", "wrong", tr, clock=Clock())
    api_calls = []
    with pytest.raises(TokenError):
        p.call_with_auth(lambda token: api_calls.append(token))
    assert api_calls == [] and len(tr.calls) == 1
    with pytest.raises(TokenError):
        p.get_token()  # nothing was cached: the next call asks again
    assert len(tr.calls) == 2


def test_idp_unreachable_fails_closed(impl):
    # Offline, or air-gapped with a public token URL: the transport can't connect. The caller gets the error and
    # the API is never called without a token.
    tr = FailingTransport([ConnectionError("no route to host")])
    p = impl.TokenProvider("https://idp.example/token", "c", "s", tr, clock=Clock())
    api_calls = []
    with pytest.raises(ConnectionError):
        p.call_with_auth(lambda token: api_calls.append(token))
    assert api_calls == []


def test_token_endpoint_429_is_honored(impl):
    # The token endpoint rate-limits us with Retry-After: 30. Sixteen threads make one token call between them,
    # and no further call is made until 30 seconds have passed.
    clk = Clock()
    tr = FailingTransport([TokenError(429, retry_after=30)])
    p = impl.TokenProvider("u", "c", "s", tr, clock=clk)
    errors = []

    def worker():
        try:
            p.get_token()
        except TokenError as exc:
            errors.append(exc.status)
        except Exception as exc:  # e.g. NotImplementedError from an unfinished starter
            errors.append(type(exc).__name__)

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == [429] * 16 and len(tr.calls) == 1
    clk.t = 29.9
    with pytest.raises(TokenError):
        p.get_token()
    assert len(tr.calls) == 1
    clk.t = 30
    assert p.get_token() == "tok2" and len(tr.calls) == 2


def test_rotated_secret_is_read_at_each_refresh(impl):
    # client_secret may be a callable that reads the secret store, so a rotation needs no restart.
    clk, tr = Clock(), Transport()
    store = {"secret": "old"}
    p = impl.TokenProvider("u", "c", lambda: store["secret"], tr, clock=clk)
    p.get_token()
    store["secret"] = "new"
    clk.t = 3540
    p.get_token()
    assert [form["client_secret"] for _, form in tr.calls] == ["old", "new"]
