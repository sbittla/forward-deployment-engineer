"""Golden-set evaluation and the launch bar agreed with the customer's AI governance board."""
import json
from pathlib import Path

LAUNCH_BAR = {"pass_rate": 0.9, "intent_accuracy": 0.9, "citation_precision": 0.95, "false_answer_rate": 0.0}


def load_golden(path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def _case_passes(case: dict, r) -> bool:
    if r.intent != case["intent"]:
        return False
    if case.get("should_abstain"):
        return r.abstained or r.escalated
    if case.get("must_contain"):
        if r.abstained or not all(s.lower() in r.text.lower() for s in case["must_contain"]):
            return False
    if case.get("expected_docs"):
        if not r.citations or not set(r.citations) <= set(case["expected_docs"]):
            return False
    return True


def run_golden(copilot, golden: list[dict]) -> dict:
    results = [(c, copilot.ask(c["question"])) for c in golden]
    n = len(results)
    cited = [(c, r) for c, r in results if r.citations]
    cited_docs = sum(len(r.citations) for _, r in cited)
    correct_docs = sum(len(set(r.citations) & set(c.get("expected_docs", []))) for c, r in cited)
    unanswerable = [r for c, r in results if c.get("should_abstain")]
    return {
        "cases": n,
        "pass_rate": round(sum(_case_passes(c, r) for c, r in results) / n, 4),
        "intent_accuracy": round(sum(r.intent == c["intent"] for c, r in results) / n, 4),
        "citation_precision": round(correct_docs / cited_docs, 4) if cited_docs else 0.0,
        "false_answer_rate": round(sum(not (r.abstained or r.escalated) for r in unanswerable) / len(unanswerable), 4)
        if unanswerable else 0.0,
        "avg_cost_usd": round(sum(r.cost_usd for _, r in results) / n, 6),
        "failures": [c["id"] for c, r in results if not _case_passes(c, r)],
    }


def launch_bar(metrics: dict) -> tuple[bool, list[str]]:
    misses = []
    for key, bar in LAUNCH_BAR.items():
        value = metrics[key]
        ok = value <= bar if key == "false_answer_rate" else value >= bar
        if not ok:
            misses.append(f"{key}={value} (bar {bar})")
    return not misses, misses
