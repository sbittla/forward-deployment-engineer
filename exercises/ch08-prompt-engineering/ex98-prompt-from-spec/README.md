# ex98 · System prompt from a policy spec, with traceability

**Chapter:** 8 · Prompt Engineering (`exercises/ch08-prompt-engineering/`) · **Covers:** R09 Prompt & context engineering, R14 Guardrails, R43 Regulatory & compliance

## Learning objectives
- Write system prompts the way regulated customers need them: generated from a reviewed spec, not hand-edited.
- Give each rule an id, a reason and a test, so compliance can trace "where is rule X enforced?" in one step.
- Detect policy drift between spec versions and re-test only what changed.

## Scenario
An insurer's compliance team owns a 30-rule policy document for the claims assistant. Today an engineer copies
rules into the prompt by hand, and nobody can say which version of the policy is live. The auditor's question is
simple: "Show me where rule POL-17 is in the prompt, and the test proving the assistant follows it." You'll compile
the spec into the prompt, trace every rule, and run a conformance suite generated from the same spec.

## Your task
- `Policy(id, kind, rule, why="", tests=())`, a frozen dataclass. `kind` is one of `KINDS = ("must", "must_not",
  "escalate")`. Each test is `{"input", "expect_contains": [...], "expect_absent": [...]}` (both lists optional).
- `load_policies(rows) -> list[Policy]` keeps input order and strips `rule`/`why`. Raise `ValueError` for an id not
  matching `^[A-Z]+-\d+$`, a duplicate id, an unknown kind, or an empty rule.
- `build_system_prompt(role, policies, output_format) -> str` produces exactly this layout (see the test for a full
  example):
  - a `<role>` block, then a blank line, then `<policies>` with one line per policy, grouped by kind in `KINDS`
    order (input order within a kind):
    `<policy id="ID">{Always|Never|Hand off to a human when} {rule}.{ Why: {why}.}</policy>` (no doubled period;
    HTML-escape rule and why);
  - `</policies>`, a blank line, the conflict-resolution sentence from the test, a blank line, and an
    `<output_format>` block.
- `trace(prompt, policies) -> {id: bool}`: true when `<policy id="ID">` appears in the prompt.
- `coverage(policies) -> float`: share of policies with at least one test (4 dp; `0.0` when empty).
- `generate_cases(policies) -> list[dict]`: each test plus `policy_id` and `case` = `"ID#n"` (1-based per policy).
- `run_conformance(llm, prompt, policies) -> dict`: for each case, call `llm.complete([user input], system=prompt)`.
  A case passes when every `expect_contains` string appears and no `expect_absent` string appears
  (case-insensitive). Return `results` (`case`, `policy_id`, `passed`, `missing`, `leaked`), `by_policy` (all of
  that policy's cases passed), `untested` ids, `pass_rate` (4 dp) and `traced` (every policy traced).
- `diff_policies(old, new) -> {"added", "removed", "changed"}`: sorted ids. A policy has changed when its `kind` or
  `rule` differs; changes to `why` alone don't count.

## Field notes
Explaining *why* in the prompt ("reserves are confidential") makes models generalise a rule to cases the rule's
wording didn't anticipate. Version the spec, not the prompt: the prompt is a build artifact.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch08-prompt-engineering/ex98-prompt-from-spec`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch08-prompt-engineering/ex98-prompt-from-spec`: all
  7 pass.
- **Tests:** `test_prompt_from_spec.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Conformance uses substring checks against a fake model, which catch blatant failures only.
  In production, add rubric-graded cases with a calibrated judge (ex50), version and review the policy specification
  as the source of truth, and enforce hard constraints such as never revealing a reserve in code as well as in the
  prompt (Chapter 13).

## Prompt kit
**Learn (tutor prompt)**
```text
I'm deploying an LLM assistant for a regulated customer (insurance). Explain how to structure a system prompt so
each business rule is traceable to a policy id, testable, and robust: XML sections, stating the reason behind
rules, conflict resolution between rules, and escalation rules. Show a 5-rule example and the 5 tests you would
write for it. Point out which rules a prompt alone cannot enforce and need code instead.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch08-prompt-engineering/ex98-prompt-from-spec/starter.py so test_prompt_from_spec.py passes.
The prompt layout must match the EXPECTED string in the test byte for byte. Use html.escape(quote=False) for rules
and reasons. Use fde_kit.llm.FakeLLM only through its complete() method. Don't edit tests; show pytest output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review this policy-to-prompt compiler with a compliance officer's eyes: Can a rule silently disappear from the
prompt? Are "must_not" rules phrased in a way the model can actually follow? Which policies in a typical claims
spec should be enforced in code (output filters, tool permissions) instead of in the prompt, and why?
```
**Production prompt (generated by this exercise)**
```text
<role>
You assist claims adjusters at Acme Insurance.
</role>

<policies>
<policy id="POL-1">Always cite the policy section for every coverage statement.</policy>
<policy id="POL-2">Never quote internal claim reserve amounts. Why: reserves are confidential.</policy>
<policy id="POL-3">Hand off to a human when the customer mentions a lawyer or lawsuit.</policy>
</policies>

When policies conflict, escalation wins over never, and never wins over always. Cite the ids of the policies you
applied in a final line: Policies: <ids>.

<output_format>
Plain text, max 120 words.
</output_format>
```
