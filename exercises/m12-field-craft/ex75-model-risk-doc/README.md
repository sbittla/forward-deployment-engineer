# ex75 · Model risk documentation for a regulated customer

**Module:** m12 · **Covers:** R25 Regulated industries, R24 Technical writing, R14 Responsible AI · **Time:** 50 min

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
