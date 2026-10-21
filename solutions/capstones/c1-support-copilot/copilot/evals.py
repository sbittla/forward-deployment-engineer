"""Golden-set evaluation and the launch bar agreed with the customer's AI governance board."""
import json
from pathlib import Path

from . import pii

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


def _slice(case: dict) -> str:
    return "unanswerable" if case.get("should_abstain") else case["intent"]


def _retrieved_expected(copilot, case: dict, principal) -> bool:
    query = pii.strip_tokens(pii.redact(case["question"])[0])
    return any(h.chunk.doc_id in case["expected_docs"] for h in copilot.search(query, principal))


def run_golden(copilot, golden: list[dict], principal=None) -> dict:
    """Run every case as `principal` (None for a copilot whose retriever isn't permission-aware)."""
    results = [(c, copilot.ask(c["question"], principal=principal)) for c in golden]
    n = len(results)
    cited = [(c, r) for c, r in results if r.citations]
    cited_docs = sum(len(r.citations) for _, r in cited)
    correct_docs = sum(len(set(r.citations) & set(c.get("expected_docs", []))) for c, r in cited)
    unanswerable = [r for c, r in results if c.get("should_abstain")]
    answerable = [(c, r) for c, r in results if c.get("expected_docs")]
    slices: dict[str, list[bool]] = {}
    for c, r in results:
        slices.setdefault(_slice(c), []).append(_case_passes(c, r))
    return {
        "cases": n,
        "pass_rate": round(sum(_case_passes(c, r) for c, r in results) / n, 4),
        "intent_accuracy": round(sum(r.intent == c["intent"] for c, r in results) / n, 4),
        "citation_precision": round(correct_docs / cited_docs, 4) if cited_docs else 0.0,
        "false_answer_rate": round(sum(not (r.abstained or r.escalated) for r in unanswerable) / len(unanswerable), 4)
        if unanswerable else 0.0,
        "over_refusal_rate": round(sum(r.abstained or r.escalated for _, r in answerable) / len(answerable), 4)
        if answerable else 0.0,
        "retrieval_recall": round(sum(_retrieved_expected(copilot, c, principal) for c, _ in answerable)
                                  / len(answerable), 4) if answerable else 0.0,
        "slices": {k: round(sum(v) / len(v), 4) for k, v in sorted(slices.items())},
        "avg_cost_usd": round(sum(r.cost_usd for _, r in results) / n, 6),
        "total_cost_usd": round(sum(r.cost_usd for _, r in results), 6),
        "successes": sum(_case_passes(c, r) for c, r in results),
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


def run_security(copilot, probes: list[dict], principals: dict) -> dict:
    """Ask each probe as its principal; a leak is a forbidden document in the retrieved context or the citations."""
    leaked = []
    for p in probes:
        who = principals.get(p["principal"])
        query = pii.strip_tokens(pii.redact(p["question"])[0])
        seen = {h.chunk.doc_id for h in copilot.search(query, who)}
        seen |= set(copilot.ask(p["question"], principal=who).citations)
        if seen & set(p["forbidden_docs"]):
            leaked.append(p["id"])
    return {"probes": len(probes), "leaks": len(leaked), "leaked": leaked}
