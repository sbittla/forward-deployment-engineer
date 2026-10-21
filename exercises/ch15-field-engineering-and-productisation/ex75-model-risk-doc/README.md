# ex75 · Model risk documentation for a regulated customer

**Chapter:** 15 · Field Engineering and Productisation (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R25 Regulated industries, R24 Technical writing, R14 Responsible AI

## Learning objectives
- Assign a model risk tier from deployment characteristics.
- Derive required controls and validate the risk document.
- Generate a model risk document that stays in sync with the system.

## Scenario
A bank's model risk management (MRM) team must approve any model that influences customer outcomes (in the US this
follows supervisory guidance such as SR 11-7). Your copilot needs a model card / risk document before the pilot can
touch real customers. Generate it from structured metadata so it stays in sync with the system.

## Your task
`meta` keys: `name, version, owner, purpose, users, out_of_scope (list), customer_facing (bool),
automated_decision (bool), regulated_domain (bool), data_sources (list), model_provider, evals (list of
{"name", "metric", "value", "threshold"}), limitations (list), monitoring (list), human_oversight (str)`.

1. `risk_tier(meta) -> int` — tier 1 (highest) if `automated_decision` and (`customer_facing` or
   `regulated_domain`); tier 2 if any of the three flags; else tier 3.
2. `required_controls(tier) -> list[str]` — tier 3: `["eval suite", "owner sign-off"]`; tier 2 adds
   `"monitoring dashboard", "human review of samples"`; tier 1 adds `"independent validation", "MRM approval",
   "kill switch"` (cumulative, in that order).
3. `validate(meta) -> list[str]` — `"missing:<key>"` for each absent/empty required key (all keys above except the
   three booleans, which must be present but may be False); `"eval_below_threshold:<name>"` for evals whose
   `value < threshold`; for tier 1, `"tier1_requires_human_oversight"` if `human_oversight` doesn't mention
   `review` or `approve`.
4. `render(meta) -> str` — markdown with headings, in order: `# Model risk document: <name> v<version>`,
   `## Summary` (owner, purpose, risk tier), `## Intended use`, `## Out of scope`, `## Data`, `## Evaluation`
   (table `| Eval | Metric | Value | Threshold | Status |` with `PASS`/`FAIL`), `## Limitations`,
   `## Monitoring`, `## Human oversight`, `## Required controls`, `## Approval` (a line
   `Status: BLOCKED (<n> issues)` if `validate` finds issues else `Status: READY FOR REVIEW`).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Model risk documentation for a
regulated customer". Before I write code, teach me model risk management for regulated customers (SR 11-7 style),
risk tiering, controls, and model cards. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch15-field-engineering-and-productisation/ex75-model-risk-doc/starter.py so that test_model_risk.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `risk_tier`,
`required_controls`, `validate`, `render`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch15-field-engineering-and-productisation/ex75-model-risk-doc` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Model risk documentation for a regulated customer" as a senior forward deployed engineer
would before it ships to a customer. Specifically: Are booleans required to be present even when False? Is the tier
logic correct for every flag combination? What would an MRM reviewer still ask for? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
