import re

import pytest

from fde_kit import FakeLLM

PACKAGE = "insights"


@pytest.fixture
def conn(cap, cap_data):
    return cap.load_warehouse(cap_data)[0]


def test_repair_loop(cap, conn):
    llm = FakeLLM(["SELECT SUM(amount) FROM transactions",
                   "```sql\nSELECT ROUND(SUM(amount_usd), 2) AS total FROM transactions\n```"])
    ans = cap.Analyst(llm, conn).ask("What is total spend?")
    assert not ans.refused and ans.attempts == 2 and ans.columns == ["total"]
    total = conn.execute("SELECT ROUND(SUM(amount_usd), 2) FROM transactions").fetchone()[0]
    assert ans.rows == [(total,)] and ans.narrative == f"total: {total}"
    feedback = llm.calls[1]["messages"][-1]["content"]
    assert "no such column" in feedback


def test_system_prompt_has_schema_and_rules(cap, conn):
    llm = FakeLLM(["CANNOT_ANSWER"])
    ans = cap.Analyst(llm, conn).ask("What's the weather?")
    assert ans.refused and ans.attempts == 1 and ans.rows == []
    system = llm.calls[0]["system"]
    assert "monthly_spend(" in system and "CANNOT_ANSWER" in system and "SELECT" in system


def test_refuses_after_unsafe_attempts(cap, conn):
    llm = FakeLLM(["DELETE FROM transactions", "DROP TABLE accounts", "UPDATE accounts SET segment = 'x'"])
    ans = cap.Analyst(llm, conn).ask("wipe it")
    assert ans.refused and len(ans.errors) == 3 and all("UnsafeSQL" in e for e in ans.errors)
    assert conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 18


def test_narrative_multi_row(cap, conn):
    llm = FakeLLM(["SELECT category, COUNT(*) AS n FROM transactions GROUP BY category ORDER BY n DESC, category"])
    ans = cap.Analyst(llm, conn).ask("count by category")
    assert re.match(r"^\d+ rows\. First row: category=fuel, n=\d+\.$", ans.narrative)


def test_question_suite(cap, cap_data, conn):
    m = cap.run_questions(conn, cap_data / "questions.json")
    assert m["failures"] == [] and m["execution_accuracy"] == 1.0 and m["refusal_accuracy"] == 1.0
    assert m["unsafe_blocked"] >= 5 and m["questions"] == 7
