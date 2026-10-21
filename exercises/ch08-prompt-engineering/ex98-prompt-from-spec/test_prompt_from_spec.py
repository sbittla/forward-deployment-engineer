import pytest

from fde_kit.llm import FakeLLM

ROWS = [
    {"id": "POL-2", "kind": "must_not", "rule": "quote internal claim reserve amounts", "why": "reserves are confidential"},
    {"id": "POL-1", "kind": "must", "rule": "cite the policy section for every coverage statement",
     "tests": [{"input": "Is flood covered?", "expect_contains": ["section"]}]},
    {"id": "POL-3", "kind": "escalate", "rule": "the customer mentions a lawyer or lawsuit",
     "tests": [{"input": "My lawyer says you owe me", "expect_contains": ["human"], "expect_absent": ["denied"]},
               {"input": "I'm suing", "expect_contains": ["human"]}]},
]
ROLE = "You assist claims adjusters at Acme Insurance."
FORMAT = "Plain text, max 120 words."

EXPECTED = """<role>
You assist claims adjusters at Acme Insurance.
</role>

<policies>
<policy id="POL-1">Always cite the policy section for every coverage statement.</policy>
<policy id="POL-2">Never quote internal claim reserve amounts. Why: reserves are confidential.</policy>
<policy id="POL-3">Hand off to a human when the customer mentions a lawyer or lawsuit.</policy>
</policies>

When policies conflict, escalation wins over never, and never wins over always. Cite the ids of the policies you \
applied in a final line: Policies: <ids>.

<output_format>
Plain text, max 120 words.
</output_format>"""


def test_load_validates(impl):
    ps = impl.load_policies(ROWS)
    assert [p.id for p in ps] == ["POL-2", "POL-1", "POL-3"] and ps[1].tests[0]["input"] == "Is flood covered?"
    for bad in ([{"id": "pol1", "kind": "must", "rule": "x"}],
                [{"id": "P-1", "kind": "should", "rule": "x"}],
                [{"id": "P-1", "kind": "must", "rule": "  "}],
                [{"id": "P-1", "kind": "must", "rule": "x"}, {"id": "P-1", "kind": "must", "rule": "y"}]):
        with pytest.raises(ValueError):
            impl.load_policies(bad)


def test_build_prompt_exact(impl):
    assert impl.build_system_prompt(ROLE, impl.load_policies(ROWS), FORMAT) == EXPECTED


def test_rules_are_escaped(impl):
    ps = impl.load_policies([{"id": "X-1", "kind": "must", "rule": "treat <script> & tags as text"}])
    assert '<policy id="X-1">Always treat &lt;script&gt; &amp; tags as text.</policy>' in impl.build_system_prompt("r", ps, "f")


def test_trace_and_coverage(impl):
    ps = impl.load_policies(ROWS)
    prompt = impl.build_system_prompt(ROLE, ps, FORMAT)
    assert impl.trace(prompt, ps) == {"POL-2": True, "POL-1": True, "POL-3": True}
    assert impl.trace(prompt.replace('<policy id="POL-2">', "<policy>"), ps)["POL-2"] is False
    assert impl.coverage(ps) == 0.6667 and impl.coverage([]) == 0.0


def test_generate_cases(impl):
    cases = impl.generate_cases(impl.load_policies(ROWS))
    assert [c["case"] for c in cases] == ["POL-1#1", "POL-3#1", "POL-3#2"]
    assert cases[1]["policy_id"] == "POL-3" and cases[1]["expect_absent"] == ["denied"]


def test_run_conformance(impl):
    ps = impl.load_policies(ROWS)
    prompt = impl.build_system_prompt(ROLE, ps, FORMAT)

    def reply(messages, system, tools):
        text = messages[-1]["content"]
        if "flood" in text:
            return "Flood is excluded under Section 4.2. Policies: POL-1"
        if "lawyer" in text:
            return "Claim denied. A human adjuster will contact you."
        return "Let me connect you with a HUMAN colleague. Policies: POL-3"

    llm = FakeLLM(reply)
    report = impl.run_conformance(llm, prompt, ps)
    assert all(c["system"] == prompt for c in llm.calls) and len(llm.calls) == 3
    assert [r["passed"] for r in report["results"]] == [True, False, True]
    assert report["results"][1]["leaked"] == ["denied"] and report["results"][1]["missing"] == []
    assert report["by_policy"] == {"POL-1": True, "POL-3": False}
    assert report["untested"] == ["POL-2"] and report["pass_rate"] == 0.6667 and report["traced"] is True


def test_diff_policies(impl):
    old = impl.load_policies(ROWS)
    new_rows = [dict(ROWS[0], rule="quote reserve or settlement amounts"), ROWS[1],
                {"id": "POL-4", "kind": "must", "rule": "answer in the adjuster's language"}]
    assert impl.diff_policies(old, impl.load_policies(new_rows)) == {
        "added": ["POL-4"], "removed": ["POL-3"], "changed": ["POL-2"]}
    reworded_why = [dict(ROWS[0], why="different reason"), ROWS[1], ROWS[2]]
    assert impl.diff_policies(old, impl.load_policies(reworded_why))["changed"] == []
