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
