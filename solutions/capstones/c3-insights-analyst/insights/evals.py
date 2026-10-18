"""Execution-accuracy evals: compare the analyst's result set with the gold query's result set."""
import json
from pathlib import Path

from fde_kit import FakeLLM

from .analyst import Analyst


def _normalise(rows, ordered: bool):
    norm = [tuple(round(v, 2) if isinstance(v, float) else v for v in r) for r in rows]
    return norm if ordered else sorted(norm, key=repr)


def run_questions(conn, questions_path) -> dict:
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    results = []
    for q in questions:
        analyst = Analyst(FakeLLM(list(q["model_attempts"])), conn)
        ans = analyst.ask(q["question"])
        if q.get("expect_refusal"):
            ok = ans.refused and not ans.rows
        else:
            gold = conn.execute(q["gold_sql"]).fetchall()
            ordered = "order by" in q["gold_sql"].lower()
            ok = not ans.refused and _normalise(ans.rows, ordered) == _normalise(gold, ordered)
        results.append({"id": q["id"], "passed": ok, "attempts": ans.attempts, "refused": ans.refused,
                        "unsafe_blocked": sum("UnsafeSQL" in e for e in ans.errors)})
    n = len(results)
    answerable = [r for r, q in zip(results, questions) if not q.get("expect_refusal")]
    return {
        "questions": n,
        "execution_accuracy": round(sum(r["passed"] for r in answerable) / len(answerable), 4),
        "refusal_accuracy": round(sum(r["passed"] for r, q in zip(results, questions) if q.get("expect_refusal"))
                                  / max(1, n - len(answerable)), 4),
        "unsafe_blocked": sum(r["unsafe_blocked"] for r in results),
        "avg_attempts": round(sum(r["attempts"] for r in results) / n, 2),
        "failures": [r["id"] for r in results if not r["passed"]],
    }
