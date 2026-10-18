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
