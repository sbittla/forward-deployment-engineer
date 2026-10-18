import pytest

PACKAGE = "insights"


@pytest.fixture
def wh(cap, cap_data):
    return cap.load_warehouse(cap_data)


def test_load_report(wh):
    conn, rep = wh
    assert rep.bronze_rows == 22 and rep.loaded == 18 and rep.duplicates == 1
    reasons = dict(rep.quarantined)
    assert set(reasons) == {"T012", "T013", "T021"}
    assert "amount" in reasons["T012"] and "account" in reasons["T013"] and "posted_at" in reasons["T021"]
    assert conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 18


def test_silver_rules(wh):
    conn, _ = wh
    row = lambda t: conn.execute("SELECT posted_at, amount_usd, original_amount, currency FROM transactions "
                                 "WHERE txn_id = ?", (t,)).fetchone()
    assert row("T005")[1] == 890.0                     # later update wins
    assert row("T004")[0] == "2026-01-22"              # MM/DD/YYYY normalised
    assert row("T002")[1] == 1250.0                    # thousands separator
    assert row("T006") == ("2026-01-15", 513.0, 5400.0, "SEK")


def test_gold_view(wh):
    conn, _ = wh
    rows = conn.execute("SELECT month, amount FROM monthly_spend WHERE account_id = 'A2' AND category = 'fuel' "
                        "ORDER BY month").fetchall()
    assert rows == [("2026-01", 6075.25), ("2026-02", 3260.0), ("2026-03", 3479.5)]


def test_schema_prompt_and_dictionary(cap, wh):
    conn, _ = wh
    prompt = cap.schema_prompt(conn)
    assert "transactions(" in prompt and "monthly_spend(" in prompt and "amount_usd REAL" in prompt
    assert all(name in prompt for name in cap.METRICS)
    dd = cap.data_dictionary(conn)
    assert dd.startswith("# Data dictionary") and "## accounts" in dd and "| segment | TEXT |" in dd
    assert "| refund_count |" in dd
