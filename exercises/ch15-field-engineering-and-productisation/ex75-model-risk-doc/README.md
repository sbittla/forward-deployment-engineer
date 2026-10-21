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
   three booleans, which must be present but may be False); `"eval_incomplete:<name>"` for an eval whose `value` or
   `threshold` is missing or not a number (it fails closed: never a pass); `"eval_below_threshold:<name>"` for
   complete evals whose `value < threshold`; for tier 1, `"tier1_requires_human_oversight"` if `human_oversight` doesn't mention
   `review` or `approve`.
4. `render(meta) -> str` — markdown with headings, in order: `# Model risk document: <name> v<version>`,
   `## Summary` (owner, purpose, risk tier), `## Intended use`, `## Out of scope`, `## Data`, `## Evaluation`
   (table `| Eval | Metric | Value | Threshold | Status |` with `PASS`/`FAIL`; a missing value or threshold prints as
   `None` and the row is `FAIL`), `## Limitations`,
   `## Monitoring`, `## Human oversight`, `## Required controls`, `## Approval` (a line
   `Status: BLOCKED (<n> issues)` if `validate` finds issues else `Status: READY FOR REVIEW`).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Compliance evidence map

Chapter 15's Table 15.1 points here. A reviewer asks "show me"; answer with an artifact that a rerun reproduces, not a
statement. Run each test from the repository root with `--solutions` to regenerate the evidence.

| Control | Artifact that proves it | Exercise |
|---|---|---|
| Direct identifiers removed; dates, ages and ZIP codes generalized | `test_deidentify`, `test_elderly_and_restricted_zip` | ex72 |
| The limit of free-text scrubbing is known and written down | `test_boundary_other_names_not_scrubbed`; the Production readiness panel in Section 15.3 | ex72 |
| Retention purges old records; legal holds win | `test_retention` | ex72 |
| Access is logged by purpose and identity, never contents; anonymous access fails | `test_access_log`, `test_access_log_fails_closed` | ex72 |
| The model risk document is generated, tiered and blocks on a failed or incomplete evaluation | `render` output with its `Status:` line; `test_validate`, `test_validate_fails_closed` | ex75 |
| Model output can't override or add fields, even from an injected document | `test_llm_fills_only_missing`, `test_injected_reply_cannot_add_or_override` | ex70 |
| An accuracy claim carries its sample size and a decision rule | `exit_decision` output; `test_exit_gate` | ex70 |
| Fine-tuning data has contact details redacted and no train/validation leakage | `test_to_example_merge_redact_trailing`, `test_split_stratified_no_overlap` | ex71 |
| Agent-written code has no string-built SQL, path escape or logged token | `REVIEW.md`; `test_sql_injection`, `test_export_safe_and_quoted`, `test_token_not_logged` | ex87 |
| One customer's names and contacts never reach another's output | `test_no_customer_names_in_library_code`, `test_other_customer` | ex67 |

Tests prove the code does what it says; they don't prove the rule is the right one. Privacy, legal and MRM sign-off
stay with the customer's people.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch15-field-engineering-and-productisation/ex75-model-risk-doc`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch15-field-engineering-and-productisation/ex75-model-risk-doc`: all 5 pass.
- **Tests:** `test_model_risk.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The tiering rules, controls and thresholds are illustrative, and `validate` checks that
  fields are present and evaluations pass, not that the metadata is true. A real model risk document follows the
  customer's MRM policy and templates, cites versioned evaluation evidence, and is approved by the people that policy
  names.

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
