import json

DEPS = {"gateway": ["api"], "api": ["retriever", "authsvc"], "retriever": ["vectordb"], "vectordb": [], "authsvc": []}


def L(ts, service, level, msg, rid=None):
    d = {"ts": f"2026-10-17T02:{ts}", "service": service, "level": level, "msg": msg}
    if rid:
        d["request_id"] = rid
    return json.dumps(d)


LINES = [
    L("13:58", "gateway", "INFO", "GET /answer", "r1"),
    L("14:02", "api", "ERROR", "upstream retriever timeout", "r2"),
    L("13:59", "api", "INFO", "answer ok", "r1"),
    L("14:01", "vectordb", "ERROR", "disk full: compaction failed"),
    L("14:00", "vectordb", "WARN", "disk 97%"),
    "this is not json",
    L("14:02", "retriever", "ERROR", "vectordb query timeout", "r2"),
    L("14:03", "gateway", "ERROR", "502 bad gateway", "r2"),
    L("14:00", "gateway", "INFO", "GET /answer", "r2"),
    L("14:04", "authsvc", "ERROR", "token cache miss storm"),
    L("14:10", "gateway", "INFO", "GET /answer", "r3"),
    '{"ts": "bad"',
]


def test_parse(impl):
    recs, bad = impl.parse(LINES)
    assert bad == 2 and len(recs) == 10
    assert [r["ts"] for r in recs] == sorted(r["ts"] for r in recs)


def test_first_errors_and_root(impl):
    recs, _ = impl.parse(LINES)
    fe = impl.first_errors(recs)
    assert fe["vectordb"] == "2026-10-17T02:14:01" and "gateway" in fe
    # authsvc errors too, but only after api's first error -> not the root; vectordb has no deps
    assert impl.root_cause(recs, DEPS) == "vectordb"


def test_error_rate(impl):
    recs, _ = impl.parse(LINES)
    rates = impl.error_rate_by_minute(recs)
    assert rates["gateway"]["02:14"] == round(1 / 3, 3)  # 14:00 INFO, 14:03 ERROR, 14:10 INFO
    assert rates["gateway"]["02:13"] == 0.0
    assert rates["vectordb"]["02:14"] == 0.5


def test_timeline(impl):
    recs, _ = impl.parse(LINES)
    assert impl.timeline(recs, "r2") == [
        "2026-10-17T02:14:00 gateway INFO GET /answer",
        "2026-10-17T02:14:02 api ERROR upstream retriever timeout",
        "2026-10-17T02:14:02 retriever ERROR vectordb query timeout",
        "2026-10-17T02:14:03 gateway ERROR 502 bad gateway",
    ]


def test_summary(impl):
    md = impl.incident_summary(LINES, DEPS)
    assert md.splitlines()[0] == "# Incident summary"
    assert "Root cause: vectordb" in md
    assert "Blast radius: vectordb, api, retriever, gateway, authsvc" in md
    assert "Malformed lines: 2" in md
