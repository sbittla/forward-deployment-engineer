# Partner review memo: Atlas SI deliverables, week 3

## Summary
D-data-1 (ingestion) is accepted. D-fe-1 (agent-desktop UI) is rejected: two blockers, one open critical defect,
and evidence below the agreed bar. The frontend is not on the critical path, but go-live cannot happen until it
passes.

## Findings
| Deliverable | Severity | Area | Finding |
|---|---|---|---|
| D-fe-1 | blocker | rollback | No rollback plan for the UI release |
| D-fe-1 | blocker | pii_handling | Customer names are sent to the model without redaction |
| D-fe-1 | major | evals | No UI-level evals or acceptance tests for answer rendering |
| D-fe-1 | major | threat_model | No threat model (XSS in rendered answers is the obvious one) |
| D-fe-1 | evidence | tests | 40 of 46 tests pass; 1 open critical defect; eval pass rate 0.88 |

## Conditions for acceptance
1. Redact customer names before any model call, or justify and document the exception with the bank's DPO.
2. Document and rehearse a rollback (previous build behind a feature flag).
3. Close the critical defect; all tests green; eval pass rate of 0.90 or higher.
4. Threat model covering rendering of model output and SSO session handling.

## Re-review date
2026-11-25, with evidence submitted by 2026-11-23.
