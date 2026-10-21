import importlib

PACKAGE = "copilot"


def test_golden_set_meets_launch_bar(cap, cap_data, copilot):
    evals = importlib.import_module("copilot.evals")
    metrics = cap.run_golden(copilot, evals.load_golden(cap_data / "golden.jsonl"))
    ok, misses = cap.launch_bar(metrics)
    assert ok, (misses, metrics["failures"])
    assert metrics["cases"] == 12 and metrics["false_answer_rate"] == 0.0


def test_launch_bar_reports_misses(cap):
    metrics = {"pass_rate": 0.8, "intent_accuracy": 1.0, "citation_precision": 0.9, "false_answer_rate": 0.1}
    ok, misses = cap.launch_bar(metrics)
    assert not ok and len(misses) == 3 and any("false_answer_rate" in m for m in misses)


def test_exec_readout_uses_measured_numbers(cap, cap_data, copilot):
    evals = importlib.import_module("copilot.evals")
    readout = importlib.import_module("copilot.readout")
    metrics = evals.run_golden(copilot, evals.load_golden(cap_data / "golden.jsonl"))
    impact = readout.business_impact(11, 8, 40_000, 45, 0.6, 1_500)
    assert impact == {"hours_saved_per_month": 1200, "net_savings_per_month": 52_500}
    md = readout.render_exec_readout(metrics, impact)
    for heading in ("## Executive summary", "## Results", "## Business impact", "## Risks", "## Next steps"):
        assert heading in md
    assert f"{metrics['pass_rate']:.0%}" in md and "1,200" in md and "proceed" in md


def test_eval_reports_refusal_recall_and_slices(cap, cap_data, copilot):
    evals = importlib.import_module("copilot.evals")
    golden = evals.load_golden(cap_data / "golden.jsonl")
    metrics = evals.run_golden(copilot, golden)
    assert metrics["over_refusal_rate"] == 0.0 and metrics["retrieval_recall"] == 1.0
    assert set(metrics["slices"]) == {"policy_question", "claim_status", "speak_to_human", "unanswerable"}
    assert metrics["successes"] == 12 and metrics["total_cost_usd"] > 0
    copilot.min_coverage = 1.01                       # a copilot that refuses everything is safe but useless
    timid = evals.run_golden(copilot, golden)
    assert timid["false_answer_rate"] == 0.0 and timid["over_refusal_rate"] == 1.0
    assert timid["retrieval_recall"] == 1.0           # retrieval still found the documents: the refusal is the bug
