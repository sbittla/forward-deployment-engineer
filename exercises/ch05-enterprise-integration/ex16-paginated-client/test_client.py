import pytest


class FakeAPI:
    def __init__(self, impl, script):
        self.impl, self.script, self.calls = impl, list(script), []

    def __call__(self, method, url, headers, params):
        self.calls.append(dict(method=method, url=url, headers=headers, params=dict(params or {})))
        return self.script.pop(0)


def R(impl, status=200, body=None, **headers):
    return impl.Response(status, {k.replace("_", "-"): v for k, v in headers.items()}, body)


def test_auth_headers_and_pagination(impl):
    api = FakeAPI(impl, [
        R(impl, body={"data": [1, 2], "next_cursor": "c2"}),
        R(impl, body={"data": [3], "next_cursor": "c3"}),
        R(impl, body={"data": [4], "next_cursor": None}),
    ])
    c = impl.ApiClient("https://helpdesk.example.com/api/", "tok", api, sleep=lambda s: None)
    assert list(c.list_all("/tickets", {"status": "closed"})) == [1, 2, 3, 4]
    assert api.calls[0]["url"] == "https://helpdesk.example.com/api/tickets"
    assert api.calls[0]["headers"]["Authorization"] == "Bearer tok"
    assert api.calls[1]["params"] == {"status": "closed", "cursor": "c2"}
    assert "cursor" not in api.calls[0]["params"]


def test_retry_after(impl):
    sleeps = []
    api = FakeAPI(impl, [R(impl, 429, Retry_After="3"), R(impl, 429), R(impl, body={"ok": True})])
    c = impl.ApiClient("https://x", "t", api, sleep=sleeps.append)
    assert c.get("/a") == {"ok": True}
    assert sleeps == [3, 1]


def test_429_exhausted(impl):
    api = FakeAPI(impl, [R(impl, 429)] * 4)
    c = impl.ApiClient("https://x", "t", api, sleep=lambda s: None, max_retries=3)
    with pytest.raises(impl.ApiError) as e:
        c.get("/a")
    assert e.value.status == 429 and len(api.calls) == 4


def test_client_error(impl):
    api = FakeAPI(impl, [R(impl, 404, {"error": "nope"})])
    c = impl.ApiClient("https://x", "t", api, sleep=lambda s: None)
    with pytest.raises(impl.ApiError) as e:
        c.get("/a")
    assert e.value.status == 404 and e.value.body == {"error": "nope"}


def test_proactive_rate_limit_wait(impl):
    sleeps = []
    api = FakeAPI(impl, [
        R(impl, body={"data": [1], "next_cursor": "n"}, **{"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1010"}),
        R(impl, body={"data": [2], "next_cursor": None}),
    ])
    c = impl.ApiClient("https://x", "t", api, sleep=sleeps.append, clock=lambda: 1000.0)
    assert list(c.list_all("/t")) == [1, 2]
    assert sleeps == [10.0]


def test_cursor_loop_guard(impl):
    api = FakeAPI(impl, [R(impl, body={"data": [], "next_cursor": "same"})] * 5)
    c = impl.ApiClient("https://x", "t", api, sleep=lambda s: None)
    with pytest.raises(impl.ApiError):
        list(c.list_all("/t", max_pages=3))


# Negative tests: invalid or expired credentials are never retried

@pytest.mark.parametrize("status", [401, 403])
def test_invalid_or_expired_token_is_not_retried(impl, status):
    sleeps = []
    api = FakeAPI(impl, [R(impl, status, {"error": "invalid_token"}), R(impl, body={"ok": True})])
    c = impl.ApiClient("https://x", "expired", api, sleep=sleeps.append)
    with pytest.raises(impl.ApiError) as e:
        c.get("/a")
    assert e.value.status == status and len(api.calls) == 1 and sleeps == []
