import pytest

GOOD_SYSTEM = ("You are a claims assistant for Acme Insurance adjusters. Answer from the policy excerpts only, "
               "because adjusters act on your answers. Respond with JSON: {\"answer\": str, \"citations\": [str]}.")
GOOD_TEMPLATE = "<policy_document>\n{policy_document}\n</policy_document>\n\nQuestion: {question}"


def rules(findings):
    return [f.rule for f in findings]


def test_clean_prompt(impl):
    f = impl.lint(GOOD_SYSTEM, GOOD_TEMPLATE, {"policy_document", "question"})
    assert f == [] and impl.score(f) == 10


def test_placeholders_ignore_escaped_braces(impl):
    assert impl.placeholders("{a} {{literal}} {b} {a}") == ["a", "b"]


def test_empty_system_and_undelimited_untrusted(impl):
    f = impl.lint("", "Summarise this email: {email_body}. Output JSON.", {"email_body"})
    assert rules(f) == ["P001", "P002"]
    assert all(x.severity == "error" for x in f) and impl.score(f) == 4
    assert "{email_body}" in f[1].message


def test_mismatched_tag_is_not_delimited(impl):
    f = impl.lint(GOOD_SYSTEM, "<doc>{ticket_text}</ticket>", {"ticket_text"})
    assert rules(f) == ["P002"]


def test_format_and_shouting(impl):
    f = impl.lint("You are a helper. You MUST be polite. NEVER guess. ALWAYS cite.", "Q: {question}", {"question"})
    assert rules(f) == ["P003", "P004"] and "3 all-caps" in f[1].message


def test_variable_mismatch(impl):
    f = impl.lint(GOOD_SYSTEM, "Question: {question} for {customer}", {"question", "tenant"})
    assert rules(f) == ["P005", "P006"]
    assert f[0].severity == "error" and "customer" in f[0].message and "tenant" in f[1].message


def test_tool_descriptions(impl):
    tools = [{"name": "search", "description": "Search", "input_schema": {"properties": {"q": {"type": "string"}}}},
             {"name": "get_claim", "description": "Fetch one claim by id, including status and payout history.",
              "input_schema": {"properties": {"claim_id": {"type": "string", "description": "Claim id like C-123"}}}}]
    f = impl.lint(GOOD_SYSTEM, "Q: {question}", {"question"}, tools)
    assert rules(f) == ["P007", "P007"] and all("search" in x.message for x in f)


def test_dynamic_system_and_contradiction(impl):
    f = impl.lint("Today is 2026-10-18. Be concise but give a comprehensive, detailed answer in JSON.", "Q: {question}",
                  {"question"})
    assert rules(f) == ["P008", "P009"]
    f2 = impl.lint("You help {customer_name}. Output JSON.", "Q: {question}", {"question"})
    assert rules(f2) == ["P008"]


def test_errors_sort_before_warnings(impl):
    f = impl.lint("", "{email}", set())
    assert [x.severity for x in f] == sorted([x.severity for x in f], key={"error": 0, "warning": 1}.get)
    assert rules(f) == ["P001", "P002", "P005", "P003"] and impl.score(f) == 0


def test_render(impl):
    assert impl.render("Hi {name}, {{x}}", {"name": "Ana"}) == "Hi Ana, {{x}}"
    with pytest.raises(KeyError):
        impl.render("{a} {b}", {"a": 1})
