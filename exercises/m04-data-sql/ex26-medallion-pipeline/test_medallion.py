import json

LINES = [
    json.dumps({"event_id": "e1", "ts": "2026-10-01T10:00:00", "type": "view", "product": "p1", "country": "usa"}),
    json.dumps({"event_id": "e2", "ts": "2026-10-01T10:05:00", "type": "purchase", "product": "p1",
                "country": "US", "amount": 20.0}),
    "{broken json",
    json.dumps({"event_id": "e3", "ts": "2026-10-01T11:00:00", "type": "purchase", "product": "p1",
                "country": "Germany", "amount": "abc"}),
    json.dumps({"event_id": "e2", "ts": "2026-10-01T10:06:00", "type": "purchase", "product": "p1",
                "country": "US", "amount": 25.0}),
    json.dumps({"event_id": "e4", "ts": "2026-10-02T09:00:00", "type": "view", "product": "p2", "country": "fr"}),
    json.dumps({"event_id": "e5", "ts": "2026-10-02T09:01:00", "type": "view", "product": "p1",
                "country": "Atlantis"}),
    json.dumps({"event_id": "e6", "ts": "2026-10-02T09:30:00", "type": "refund", "product": "p1", "country": "US"}),
    json.dumps({"event_id": "e7", "ts": "2026-10-02T12:00:00", "type": "view", "product": "p1", "country": "uk"}),
    json.dumps({"event_id": "e8", "ts": "2026-10-02T12:01:00", "type": "purchase", "product": "p1",
                "country": "United Kingdom", "amount": 10.555}),
    json.dumps({"ts": "2026-10-02T12:02:00", "type": "view", "product": "p1", "country": "US"}),
]


def test_bronze_keeps_everything(impl):
    b = impl.bronze(LINES, "s3://bucket/events", "2026-10-03T00:00:00")
    assert len(b) == len(LINES)
    assert b[2] == {"raw": "{broken json", "source": "s3://bucket/events",
                    "ingested_at": "2026-10-03T00:00:00", "line_no": 2}


def test_silver(impl):
    events, quarantine = impl.silver(impl.bronze(LINES, "s", "t"))
    ids = [e["event_id"] for e in events]
    assert ids == ["e1", "e2", "e4", "e7", "e8"]
    e2 = next(e for e in events if e["event_id"] == "e2")
    assert e2["amount"] == 25.0 and e2["ts"] == "2026-10-01T10:06:00"
    assert events[0]["country"] == "US" and events[0]["amount"] == 0.0
    assert next(e for e in events if e["event_id"] == "e4")["country"] == "FR"
    assert {q["line_no"] for q in quarantine} == {2, 3, 6, 7, 10}
    assert all(q["reason"] for q in quarantine)


def test_gold(impl):
    events, _ = impl.silver(impl.bronze(LINES, "s", "t"))
    g = impl.gold(events)
    assert g["revenue_by_day_country"] == {("2026-10-01", "US"): 25.0, ("2026-10-02", "GB"): 10.56}
    assert g["conversion_by_product"] == {"p1": 1.0, "p2": 0.0}
