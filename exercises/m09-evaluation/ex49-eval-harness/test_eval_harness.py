import json

import pytest

CASES = [
    {"id": "c1", "input": "capital of France?", "expected": "Paris", "grader": "exact", "tags": ["geo"]},
    {"id": "c2", "input": "deductible?", "expected": ["$500", "per claim"], "grader": "contains", "tags": ["policy"]},
    {"id": "c3", "input": "claim id?", "expected": r"CL-\d{4}", "grader": "regex", "tags": ["policy"]},
    {"id": "c4", "input": "premium?", "expected": {"value": 1250, "tol": 1}, "grader": "numeric", "tags": ["policy", "math"]},
    {"id": "c5", "input": "extract", "expected": {"path": "claimant.name", "value": "Ana"}, "grader": "json_field"},
    {"id": "c6", "input": "explode", "expected": "x", "grader": "exact", "tags": ["geo"]},
]
ANSWERS = {
    "capital of France?": "  paris ",
    "deductible?": "Your deductible is $500 PER CLAIM.",
    "claim id?": "It is CL-12.",
    "premium?": "The premium is 1,250.40 dollars, or 104 monthly.",
    "extract": '{"claimant": {"name": "Ana"}}',
}


def system(q):
    if q == "explode":
        raise TimeoutError("model timed out")
    return ANSWERS[q]


@pytest.fixture
def cases(impl, tmp_path):
    p = tmp_path / "golden.jsonl"
    p.write_text("\n".join(json.dumps(c) for c in CASES) + "\n\n")
    return impl.load_cases(p)


def test_load(cases):
    assert len(cases) == 6 and cases[4].tags == [] and cases[3].expected == {"value": 1250, "tol": 1}


@pytest.mark.parametrize("name,out,exp,ok", [
    ("exact", "Hello   World", "hello world", True),
    ("contains", "a b c", ["A", "c"], True),
    ("contains", "a b", ["a", "z"], False),
    ("regex", "id CL-1234", r"CL-\d{4}", True),
    ("numeric", "about 3.14159", {"value": 3.14, "tol": 0.01}, True),
    ("numeric", "no numbers", {"value": 1, "tol": 1}, False),
    ("json_field", "not json", {"path": "a", "value": 1}, False),
    ("json_field", '{"a": {"b": 2}}', {"path": "a.b", "value": 2}, True),
])
def test_graders(impl, name, out, exp, ok):
    assert impl.GRADERS[name](out, exp) is ok


def test_run_and_report(impl, cases):
    rep = impl.run_eval(cases, system)
    status = {r.case.id: r.passed for r in rep.results}
    assert status == {"c1": True, "c2": True, "c3": False, "c4": True, "c5": True, "c6": False}
    assert rep.pass_rate == round(4 / 6, 4)
    assert rep.by_tag() == {"geo": 0.5, "math": 1.0, "policy": round(2 / 3, 4)}
    err = next(r for r in rep.results if r.case.id == "c6")
    assert err.error == "TimeoutError: model timed out" and err.output == ""
    md = rep.to_markdown()
    assert md.splitlines()[0] == "# Eval: 4/6 passed (66.7%)"
    assert "| geo | 0.5 |" in md or "| geo | 0.5000 |" in md
    assert "- c6: TimeoutError: model timed out" in md and "- c3: It is CL-12." in md


def test_unknown_grader(impl):
    calls = []
    with pytest.raises(ValueError):
        impl.run_eval([impl.Case("x", "i", "e", "vibes")], lambda q: calls.append(q) or "")
    assert calls == []


@pytest.mark.parametrize("passed,n,low,high", [
    (186, 200, 88.6, 95.8),   # coverage questions, candidate B (Chapter 12 worked decision)
    (31, 40, 62.5, 87.7),     # exclusions (critical)
    (40, 40, 91.2, 100.0),    # unanswerable
    (20, 20, 83.9, 100.0),    # fraud hand-off (critical)
    (85, 100, 76.7, 90.7),    # other
    (362, 400, 87.2, 93.0),   # overall
])
def test_wilson_interval_matches_worked_decision(impl, passed, n, low, high):
    lo, hi = impl.wilson_interval(passed, n)
    assert (round(lo * 100, 1), round(hi * 100, 1)) == (low, high)


def test_wilson_interval_edges(impl):
    lo, hi = impl.wilson_interval(0, 10)
    assert lo == 0.0 and 0.27 < hi < 0.28
    assert impl.wilson_interval(10, 10)[1] == 1.0
    narrow, wide = impl.wilson_interval(31, 40, z=1.0), impl.wilson_interval(31, 40)
    assert wide[0] < narrow[0] and narrow[1] < wide[1]
    for bad in [(1, 0), (5, 4), (-1, 4)]:
        with pytest.raises(ValueError):
            impl.wilson_interval(*bad)


def _results(impl, tag, passed, n):
    return [impl.CaseResult(impl.Case(f"{tag}-{i}", f"q {i}", "x", "exact", [tag]), i < passed, "")
            for i in range(n)]


def test_by_slice(impl):
    rep = impl.EvalReport(_results(impl, "exclusions", 31, 40) + _results(impl, "fraud", 20, 20))
    s = rep.by_slice()
    assert list(s) == ["exclusions", "fraud"]
    assert s["exclusions"] == {"n": 40, "passed": 31, "pass_rate": 0.775, "low": 0.625, "high": 0.8768}
    assert s["fraud"] == {"n": 20, "passed": 20, "pass_rate": 1.0, "low": 0.8389, "high": 1.0}


def test_failure_taxonomy(impl, cases):
    rep = impl.run_eval(cases, system)  # c3 and c6 fail
    assert rep.failure_taxonomy({"c3": "format or citation error"}) == [
        ("format or citation error", 1), ("unlabelled", 1)]
    rep = impl.EvalReport(_results(impl, "cov", 0, 5))
    labels = {"cov-0": "not retrieved", "cov-1": "not retrieved", "cov-2": "refused", "cov-3": "not retrieved"}
    assert rep.failure_taxonomy(labels) == [("not retrieved", 3), ("refused", 1), ("unlabelled", 1)]


def test_cost_per_success(impl):
    assert round(impl.cost_per_success(0.0195, 0.88), 4) == 0.0222  # candidate A
    assert round(impl.cost_per_success(0.0210, 0.90), 4) == 0.0233  # candidate C
    with pytest.raises(ValueError):
        impl.cost_per_success(0.02, 0.0)


def test_find_leakage(impl, cases):
    examples = [
        "Q: Capital of   FRANCE ?\nA: Paris",       # c1 leaks: same words, different case and punctuation
        "User asked about the premium: is it monthly?",  # c4 ("premium?") appears as a whole word
        "extraction rules for claims",                # "extract" is only part of a word: no leak
    ]
    assert impl.find_leakage(cases, examples) == ["c1", "c4"]
    assert impl.find_leakage(cases, []) == []
