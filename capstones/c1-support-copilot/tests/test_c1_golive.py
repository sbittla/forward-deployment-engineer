"""Prove-value stage: v0 fails the gates, the remediated build passes, and go/no-go compares with the baseline."""
import importlib

PACKAGE = "copilot"


def _modules():
    return importlib.import_module("copilot.build"), importlib.import_module("copilot.golive")


def test_v0_fails_the_gates(cap, cap_data, llm):
    build, golive = _modules()
    v0 = build.build_copilot(llm, cap_data, naive=True)
    evidence = golive.collect_evidence(v0, cap_data)
    assert evidence["pass_rate"] >= 0.9          # v0 clears the headline pass rate, which is why it looked ready
    result = golive.go_no_go(evidence, golive.load_value(cap_data / "pilot_handle_time.json"))
    assert result["decision"] == "no-go"
    failed = {g["gate"] for g in result["gates"] if not g["passed"]}
    assert {"false_answer_rate", "permission_leaks", "citation_precision"} <= failed
    assert evidence["permission_leaks"] == 5 and "g09" in evidence["failures"]


def test_remediated_build_passes_every_gate(cap, cap_data, llm):
    build, golive = _modules()
    evidence = golive.collect_evidence(build.build_copilot(llm, cap_data), cap_data)
    gates = golive.check_gates(evidence)
    assert [g["gate"] for g in gates if not g["passed"]] == []
    assert len(gates) == len(golive.GATES) == 9
    assert evidence["permission_leaks"] == 0 and evidence["false_answer_rate"] == 0.0
    assert evidence["slices"]["unanswerable"] == 1.0 and evidence["retrieval_recall"] >= 0.9
    # gates fail closed: a missing measurement is a failed gate, not a pass
    missing = golive.check_gates({k: v for k, v in evidence.items() if k != "p95_ms"})
    assert [g["gate"] for g in missing if not g["passed"]] == ["p95_ms"]


def test_go_no_go_compares_value_with_baseline(cap, cap_data, llm):
    build, golive = _modules()
    evidence = golive.collect_evidence(build.build_copilot(llm, cap_data), cap_data)
    value = golive.load_value(cap_data / "pilot_handle_time.json")      # 11 -> 7 target; pilot 7.5, control 10.4
    result = golive.go_no_go(evidence, value)
    assert result["decision"] == "go with conditions" and result["blockers"] == []
    assert result["value"]["effect_vs_control_min"] == 2.9 and not result["value"]["target_met"]
    assert "7.0 min target" in result["conditions"][0]
    assert golive.go_no_go(evidence, {**value, "pilot_min": 6.8})["decision"] == "go"
    assert golive.go_no_go(evidence, {**value, "pilot_min": 10.6})["decision"] == "no-go"
    md = golive.render_decision(result)
    for heading in ("## Decision", "## Gates", "## Value against the baseline"):
        assert heading in md
    assert "**go with conditions**" in md and "| permission_leaks | <= 0 | 0 | pass |" in md
