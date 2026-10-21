import io
import json
import uuid


def lines(buf):
    return [json.loads(l) for l in buf.getvalue().splitlines() if l.strip()]


def test_json_line_and_correlation(impl):
    buf = io.StringIO()
    log = impl.get_logger(f"t-{uuid.uuid4()}", buf)
    with impl.correlation("req-42") as cid:
        assert cid == "req-42" and impl.current_correlation_id() == "req-42"
        log.info("answered %s", "q1", extra={"fields": {"latency_ms": 812, "model": "claude-opus-5-5"}})
    log.warning("outside")
    a, b = lines(buf)
    assert a["msg"] == "answered q1" and a["level"] == "INFO" and a["correlation_id"] == "req-42"
    assert a["latency_ms"] == 812 and a["model"] == "claude-opus-5-5"
    assert a["ts"].endswith("+00:00") or a["ts"].endswith("Z")
    assert b["correlation_id"] is None and b["level"] == "WARNING"


def test_generated_and_nested(impl):
    with impl.correlation() as outer:
        assert len(outer) == 32
        with impl.correlation("inner"):
            assert impl.current_correlation_id() == "inner"
        assert impl.current_correlation_id() == outer
    assert impl.current_correlation_id() is None


def test_redaction_nested(impl):
    buf = io.StringIO()
    log = impl.get_logger(f"t-{uuid.uuid4()}", buf)
    log.info("call", extra={"fields": {"headers": {"Authorization": "Bearer abc"}, "API_KEY": "sk",
                                         "items": [{"password": "p", "ok": 1}]}})
    rec = lines(buf)[0]
    assert rec["headers"]["Authorization"] == "[REDACTED]" and rec["API_KEY"] == "[REDACTED]"
    assert rec["items"][0] == {"password": "[REDACTED]", "ok": 1}
    assert "Bearer abc" not in buf.getvalue()


def test_exception_and_no_duplicate_handlers(impl):
    buf = io.StringIO()
    name = f"t-{uuid.uuid4()}"
    impl.get_logger(name, buf)
    log = impl.get_logger(name, buf)
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("boom")
    recs = lines(buf)
    assert len(recs) == 1
    assert recs[0]["exc_type"] == "ZeroDivisionError" and "Traceback" in recs[0]["exc"]


# Fault injection: every injected failure must be traceable to its request by correlation id

class FlakyDependency:
    """Fails the requests listed in `fail_on` with ConnectionError."""

    def __init__(self, fail_on):
        self.fail_on = set(fail_on)

    def __call__(self, request_no):
        if request_no in self.fail_on:
            raise ConnectionError(f"erp reset on request {request_no}")
        return "ok"


def test_fault_each_injected_failure_logged_with_correlation_id(impl):
    buf = io.StringIO()
    log = impl.get_logger(f"t-{uuid.uuid4()}", buf)
    dep = FlakyDependency(fail_on={2, 5, 7})
    for n in range(10):
        with impl.correlation(f"req-{n}"):
            try:
                dep(n)
                log.info("served", extra={"fields": {"request_no": n}})
            except ConnectionError:
                log.exception("dependency failed", extra={"fields": {"request_no": n, "dependency": "erp"}})
    recs = lines(buf)
    errors = [r for r in recs if r["level"] == "ERROR"]
    assert len(recs) == 10 and len(errors) == 3
    assert {r["correlation_id"] for r in errors} == {"req-2", "req-5", "req-7"}
    assert all(r["correlation_id"] == f"req-{r['request_no']}" for r in recs)
    assert all(r["exc_type"] == "ConnectionError" and r["dependency"] == "erp" for r in errors)


def test_fault_concurrent_failures_keep_their_own_correlation_id(impl):
    # 20 interleaved asyncio requests, every third one failing: no log line borrows another request's id
    import asyncio
    buf = io.StringIO()
    log = impl.get_logger(f"t-{uuid.uuid4()}", buf)

    async def handle(n):
        with impl.correlation(f"req-{n}"):
            await asyncio.sleep(0.001 * (n % 4))
            try:
                if n % 3 == 0:
                    raise TimeoutError("model call timed out")
                log.info("served", extra={"fields": {"request_no": n}})
            except TimeoutError:
                log.exception("failed", extra={"fields": {"request_no": n}})

    async def main():
        await asyncio.gather(*(handle(n) for n in range(20)))

    asyncio.run(main())
    recs = lines(buf)
    assert len(recs) == 20
    assert all(r["correlation_id"] == f"req-{r['request_no']}" for r in recs)
    assert sum(r["level"] == "ERROR" for r in recs) == 7


def test_fault_exception_inside_block_restores_outer_id(impl):
    with impl.correlation("outer"):
        try:
            with impl.correlation("inner"):
                raise ConnectionError("dependency failed mid-request")
        except ConnectionError:
            pass
        assert impl.current_correlation_id() == "outer"
    assert impl.current_correlation_id() is None
