# ex90 · Architecture decision records and partner design-review gate

**Chapter:** 16 · Delivery Leadership (`exercises/ch16-delivery-leadership/`) · **Covers:** R40 Technical leadership & design review, R24 Writing, R28 Architecture

## Learning objectives
- Write and lint ADRs that capture why, alternatives and downsides.
- Review partner designs against a severity-ranked checklist.
- Gate partner deliverables on evidence, not assurances.

## Scenario
Anthropic's Staff FDE "leads engagements delivered with partners, setting the architecture and the quality bar for
work you don't build yourself" and "reviews designs and unblocks other FDEs". Deloitte's Lead FDE runs pods. Senior
FDEs scale through review, not typing. You'll formalise the two tools they use: ADRs that capture *why*, and a
review gate that decides whether a partner's design or deliverable can ship.

## Your task
1. `parse_adr(markdown) -> ADR(number, title, status, sections: dict)`: the first line is
   `# ADR-<n>: <title>`; a `Status:` line gives one of `proposed|accepted|superseded|rejected` (case-insensitive);
   `## <Heading>` blocks become sections (heading lower-cased → body stripped). Missing title or status → `ValueError`.
2. `lint_adr(adr) -> list[str]`: require sections `context`, `decision`, `consequences`, `alternatives considered`
   (`missing:<section>`); `alternatives considered` must list at least 2 bullets (`alternatives:fewer-than-2`);
   `consequences` must mention at least one downside, i.e. a word from `{"cost", "risk", "trade-off", "tradeoff",
   "downside", "slower", "lock-in", "complexity"}` (`consequences:no-downside`); an `accepted` ADR must include
   `decided-by:` in its decision section (`decision:no-owner`).
3. `review_design(design: dict) -> list[Finding(severity, area, message)]` against `CHECKLIST`. The design dict has
   keys such as `auth`, `data_flow`, `pii_handling`, `evals`, `rollback`, `observability`, `cost_estimate`,
   `slo`, `threat_model`. Missing/empty `blocker` items → severity `"blocker"`; missing `major` → `"major"`; missing
   `minor` → `"minor"`. Additionally, if `pii_handling` mentions "sent to model" without "redact" → a blocker in area
   `pii_handling`. Order: blockers, majors, minors; then by area.
4. `gate(findings, evidence) -> (decision, reasons)` for a partner deliverable. `evidence` has `tests_passed`,
   `tests_total`, `eval_pass_rate`, `open_criticals`. Decision `"reject"` if any blocker or `open_criticals > 0`;
   `"conditional"` if majors exist, test pass rate < 100%, or `eval_pass_rate < 0.9`; else `"accept"`. Reasons list
   every triggered condition in that order.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch16-delivery-leadership/ex90-adr-design-review`.
- **Expected output:** all 4 tests fail against the starter; when you're done, all 4 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch16-delivery-leadership/ex90-adr-design-review`:
  all 4 pass.
- **Tests:** `test_review_gate.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** the gate checks that each design field is present and non-empty, and takes the evidence
  numbers as reported; it can't tell a real rollback plan or threat model from a placeholder sentence. In production,
  link each item to the artefact itself (the CI run, the evaluation report, the signed security review), have a named
  reviewer read it, and keep the gate decision and its reasons in the RAID log.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Architecture decision records and
partner design-review gate". Before I write code, teach me architecture decision records, design review checklists,
severity levels, and quality gates for partner work. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch16-delivery-leadership/ex90-adr-design-review/starter.py so that test_review_gate.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ADR`, `Finding`, `parse_adr`, `lint_adr`, `review_design`, `gate`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/ch16-delivery-leadership/ex90-adr-design-review` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Architecture decision records and partner design-review gate" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does the ADR linter accept a consequences section with
no downside? Are findings ordered by severity then area? What evidence would you demand before approving a partner's
production release? Rank findings by customer impact, quote the line for each, and say which ones a test should
catch.
```
