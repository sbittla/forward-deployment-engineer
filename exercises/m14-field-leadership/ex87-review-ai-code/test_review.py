import csv
import re
import sqlite3

import pytest


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE tickets(id INTEGER, customer TEXT, subject TEXT, status TEXT)")
    c.executemany("INSERT INTO tickets VALUES (?,?,?,?)", [(1, "acme", "Login, broken", "open"), (2, "globex", "x", "closed")])
    return c


def test_sql_injection(impl, conn):
    assert impl.find_tickets(conn, "acme") == [(1, "Login, broken", "open")]
    assert impl.find_tickets(conn, "x' OR '1'='1") == []


def test_export_safe_and_quoted(impl, tmp_path):
    rows = [(1, 'Login, "broken"', "open")]
    p = impl.export_csv(rows, "acme.csv", str(tmp_path))
    with open(p, newline="") as f:
        assert list(csv.reader(f))[1] == ["1", 'Login, "broken"', "open"]
    for bad in ("../escape.csv", "/etc/passwd", "..\\escape.csv"):
        with pytest.raises(ValueError):
            impl.export_csv(rows, bad, str(tmp_path))


def test_pagination(impl):
    class C:
        def get_page(self, n):
            return [n]
    assert impl.fetch_all(C(), 3) == [1, 2, 3]


def test_token_not_logged(impl):
    class C:
        def export(self, token):
            return "ok"
    log = []
    assert impl.call_api(C(), "sk-secret-123", log) == "ok"
    assert all("sk-secret-123" not in line for line in log)


def test_load_errors(impl, tmp_path):
    with pytest.raises(FileNotFoundError):
        impl.load_tickets(str(tmp_path / "missing.json"))
    bad = tmp_path / "bad.json"
    bad.write_text("{oops")
    with pytest.raises(ValueError) as e:
        impl.load_tickets(str(bad))
    assert "bad.json" in str(e.value)


def test_no_shared_state(impl):
    assert impl.tag_counts([{"tags": ["a"]}]) == {"a": 1}
    assert impl.tag_counts([{"tags": ["a"]}]) == {"a": 1}


def test_review_md(exercise_dir):
    text = (exercise_dir / "REVIEW.md").read_text(encoding="utf-8")
    findings = re.findall(r"^- \[(security|correctness|reliability)\] \S+:\w+: .+ → .+$", text, re.M)
    assert len(findings) >= 6 and findings.count("security") >= 2
    low = text.lower()
    assert "sql injection" in low and "path traversal" in low and "token" in low


def test_agent_instructions(exercise_dir):
    text = (exercise_dir / "AGENT_INSTRUCTIONS.md").read_text(encoding="utf-8")
    heads = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for s in ("project overview", "commands", "conventions", "never do", "before you finish"):
        assert any(s in h for h in heads), s
    assert re.search(r"`[^`]*pytest[^`]*`", text)
    never = text.lower().split("never do", 1)[1]
    assert "secret" in never or "token" in never
    assert "sql" in never and "path" in never
