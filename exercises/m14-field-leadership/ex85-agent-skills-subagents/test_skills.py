import pytest

from fde_kit import FakeLLM


def write_skill(root, folder, name, desc, body="Do the thing.", extra=None):
    d = root / folder
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\n{body}\n", encoding="utf-8")
    for rel, text in (extra or {}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


def test_frontmatter(impl):
    meta, body = impl.parse_frontmatter("---\nname: x\ndescription: does y: z\n---\nBody here\n")
    assert meta == {"name": "x", "description": "does y: z"} and body.strip() == "Body here"
    with pytest.raises(ValueError):
        impl.parse_frontmatter("no frontmatter")


def test_parse_skill_and_validation(impl, tmp_path):
    d = write_skill(tmp_path, "pdf", "invoice-reader", "Extract invoice fields. Use when the user shares an invoice.",
                    extra={"reference/fields.md": "fields", "scripts/parse.py": "print(1)"})
    s = impl.parse_skill(d)
    assert s.name == "invoice-reader" and s.resources == ["reference/fields.md", "scripts/parse.py"]
    for bad_name in ("Invoice_Reader", "claude-helper", "x" * 65):
        bd = write_skill(tmp_path, f"bad-{len(bad_name)}-{bad_name[:3]}", bad_name, "ok")
        with pytest.raises(ValueError):
            impl.parse_skill(bd)
    with pytest.raises(ValueError):
        impl.parse_skill(write_skill(tmp_path, "xml", "xml-skill", "Use <b>always</b>"))
    with pytest.raises(ValueError):
        impl.parse_skill(write_skill(tmp_path, "empty", "empty-skill", "desc", body=""))


def test_registry_progressive_disclosure(impl, tmp_path):
    write_skill(tmp_path, "a", "claims-triage", "Route new insurance claims to the right queue by severity.",
                body="Step 1...", extra={"reference/rules.md": "RULES"})
    write_skill(tmp_path, "b", "invoice-reader", "Extract fields from vendor invoices and receipts.")
    reg = impl.SkillRegistry(tmp_path)
    assert reg.metadata_prompt() == ("- claims-triage: Route new insurance claims to the right queue by severity.\n"
                                     "- invoice-reader: Extract fields from vendor invoices and receipts.")
    assert "Step 1" not in reg.metadata_prompt()
    assert reg.select("triage this water damage claim by severity") == ["claims-triage"]
    assert reg.select("weather forecast tomorrow") == []
    assert reg.load("claims-triage").strip() == "Step 1..."
    assert reg.read_resource("claims-triage", "reference/rules.md") == "RULES"
    with pytest.raises(ValueError):
        reg.read_resource("claims-triage", "../b/SKILL.md")


def test_duplicate_names(impl, tmp_path):
    write_skill(tmp_path, "a", "same", "one")
    write_skill(tmp_path, "b", "same", "two")
    with pytest.raises(ValueError):
        impl.SkillRegistry(tmp_path)


SUB = """---
name: policy-researcher
description: Finds the policy clauses relevant to a claim. Use for coverage questions.
tools: search_policies, read_policy
model: claude-sonnet-5-5
---
You research insurance policy wording. Return clause ids and quotes only.
"""
TOOLS = [{"name": n, "description": n, "input_schema": {"type": "object"}}
         for n in ("search_policies", "read_policy", "issue_refund")]


def test_subagent_delegation(impl):
    sub = impl.parse_subagent(SUB)
    assert sub.tools == ["search_policies", "read_policy"] and sub.model == "claude-sonnet-5-5"
    llm = FakeLLM(["Clause 9.1: flood excluded."])
    out = impl.delegate(sub, "Is flood covered for claim CL-1?", llm, TOOLS)
    assert out == "Clause 9.1: flood excluded."
    call = llm.calls[0]
    assert call["messages"] == [{"role": "user", "content": "Is flood covered for claim CL-1?"}]
    assert call["system"].startswith("You research insurance policy wording")
    assert [t["name"] for t in call["tools"]] == ["search_policies", "read_policy"]
    assert call["model"] == "claude-sonnet-5-5"


def test_subagent_inherits_and_unknown_tool(impl):
    sub = impl.parse_subagent(SUB.replace("tools: search_policies, read_policy\n", "").replace("model: claude-sonnet-5-5\n", ""))
    assert sub.tools is None and sub.model is None
    llm = FakeLLM(["ok"])
    impl.delegate(sub, "t", llm, TOOLS)
    assert len(llm.calls[0]["tools"]) == 3
    bad = impl.parse_subagent(SUB.replace("read_policy", "delete_everything"))
    with pytest.raises(ValueError):
        impl.delegate(bad, "t", FakeLLM(["x"]), TOOLS)


def test_your_skill_and_subagent(impl, exercise_dir):
    skill = impl.parse_skill(exercise_dir / "skills" / "claims-triage")
    assert skill.name == "claims-triage" and "reference/routing-rules.md" in skill.resources
    assert "use when" in skill.description.lower()
    sub = impl.parse_subagent((exercise_dir / "agents" / "policy-researcher.md").read_text(encoding="utf-8"))
    assert sub.name == "policy-researcher" and sub.tools == ["search_policies", "read_policy"]
    assert len(sub.system_prompt.split()) >= 20
