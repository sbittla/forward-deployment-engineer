"""Harden and deploy stages: failure injection, the load model, SLO burn-rate alerts, the canary and the rollout."""
import importlib

from fde_kit import FakeLLM

PACKAGE = "copilot"
Q = "Is water damage from a burst pipe covered?"


def _copilot(cap, cap_data, llm, retriever=None):
    retriever = retriever or cap.HybridRetriever(cap.load_corpus(cap_data / "policies"))
    return cap.Copilot(llm, retriever, cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl"))


def test_model_timeout_retries_once_then_degrades(cap, cap_data, llm):
    faults = importlib.import_module("copilot.faults")
    once = faults.FaultyLLM(llm, fail_on={1})                    # first attempt times out, the retry succeeds
    r = _copilot(cap, cap_data, once).ask(Q)
    assert once.attempts == 2 and not r.degraded and r.citations == ["homeowners"] and "burst pipe" in r.text
    down = faults.FaultyLLM(FakeLLM(["unused"]))                 # every attempt times out
    r = _copilot(cap, cap_data, down).ask(Q)
    assert down.attempts == 2                                    # bounded: one try plus max_retries=1
    assert r.degraded and not r.abstained and r.cost_usd == 0
    assert r.text.startswith(cap.answer.MODEL_DOWN_TEXT) and "homeowners#water-damage" in r.chunk_ids
    assert "Homeowners Policy HO-3 > Coverage > Water damage" in r.text   # retrieval-only: sections, no answer


def test_retrieval_outage_escalates_without_model_call(cap, cap_data, llm):
    faults = importlib.import_module("copilot.faults")
    broken = faults.FaultyRetriever(cap.HybridRetriever(cap.load_corpus(cap_data / "policies")))
    r = _copilot(cap, cap_data, llm, broken).ask("My email is ana@example.com - is jewelry theft covered?")
    assert r.escalated and r.degraded and r.text == cap.answer.SEARCH_DOWN_TEXT
    assert llm.calls == [] and "ana@example.com" not in r.text   # no ungrounded call, and no exception surfaces


def test_load_model_reports_latency_and_cost_per_success(cap, cap_data, copilot):
    evals = importlib.import_module("copilot.evals")
    loadmodel = importlib.import_module("copilot.loadmodel")
    golden = evals.load_golden(cap_data / "golden.jsonl")
    a = loadmodel.run_load(copilot, golden, repeats=5)
    assert a == loadmodel.run_load(copilot, golden, repeats=5)   # deterministic: same inputs, same report
    assert a["requests"] == 60 and a["successes"] == 60
    assert a["p50_ms"] <= a["p95_ms"] <= 4000                    # the latency SLO's threshold
    assert 0 < a["cost_per_success_usd"] <= 0.025                # the cost-per-successful-answer gate
    assert loadmodel.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95) == 10
    assert loadmodel.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50) == 5
    slow = loadmodel.LatencyModel(first_token_ms=5000)
    assert loadmodel.run_load(copilot, golden, repeats=1, latency=slow)["p95_ms"] > 4000


def test_burn_rate_alerts(cap):
    slo = importlib.import_module("copilot.slo")
    s = slo.SLO()
    now = 10 * slo.HOUR
    healthy = [(now - i, True, 1500) for i in range(3600)]
    assert s.alerts(healthy, now) == []
    fast = [(now - i, i % 10 != 0, 1500) for i in range(3600)]          # 10% bad for an hour: burn 20x
    assert s.burn_rate(fast, now, slo.HOUR) == 20.0 and s.alerts(fast, now) == ["page"]
    slow_burn = [(now - i * 6, i % 25 != 0, 1500) for i in range(3600)]  # 4% bad for six hours: burn 8x
    assert s.alerts(slow_burn, now) == ["ticket"]
    too_slow = [(now - i, True, 4500) for i in range(600)]              # successes that miss the latency bar count
    assert s.burn_rate(too_slow, now, 300) == 200.0


def test_canary_rolls_back_on_quality_or_leak(cap):
    slo = importlib.import_module("copilot.slo")
    base = {"requests": 5000, "error_rate": 0.002, "p95_ms": 3000, "pass_rate": 0.95, "false_answer_rate": 0.0,
            "leaks": 0, "cost_per_success_usd": 0.004}
    assert slo.canary_decision(base, {**base, "requests": 499}) == ("wait", ["499 requests (need 500)"])
    assert slo.canary_decision(base, {**base, "requests": 800}) == ("promote", [])
    decision, reasons = slo.canary_decision(base, {**base, "requests": 800, "false_answer_rate": 0.01})
    assert decision == "rollback" and reasons[0].startswith("false_answer_rate")   # errors and latency look fine
    decision, reasons = slo.canary_decision(base, {**base, "requests": 800, "leaks": 1})
    assert decision == "rollback" and reasons == ["permission leaks 1"]
    decision, reasons = slo.canary_decision(base, {**base, "requests": 800, "cost_per_success_usd": 0.006})
    assert decision == "rollback" and reasons[0].startswith("cost_per_success_usd")


def test_staged_rollout_rolls_back_automatically(cap):
    slo = importlib.import_module("copilot.slo")
    base = {"requests": 5000, "error_rate": 0.002, "p95_ms": 3000, "pass_rate": 0.95, "false_answer_rate": 0.0,
            "leaks": 0, "cost_per_success_usd": 0.004}
    good = lambda pct: {**base, "requests": 1000}
    assert slo.run_rollout(base, good)["decision"] == "promoted"
    regress_at_50 = lambda pct: {**base, "requests": 1000, "pass_rate": 0.90 if pct >= 50 else 0.95}
    r = slo.run_rollout(base, regress_at_50)
    assert r["decision"] == "rolled_back" and r["stage"] == 50 and r["traffic_percent"] == 0
    assert r["history"] == [(10, "promote"), (50, "rollback")]
