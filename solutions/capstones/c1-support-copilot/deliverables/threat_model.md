# Threat model: Northwind Insurance support copilot

Template: `playbook/design/threat-model.md`. Reviewed with Priya Shah (IT Security) in week 6 (illustrative).

## Assets
Policyholder personal data in questions; special investigations (SIU) referral guidance; unpublished draft
bulletins; other tenants' documents on the shared platform index; the ability to pause a claim's payment.

## Threats
| # | Threat | Boundary | Control | Negative test | Gate |
|---|---|---|---|---|---|
| T1 | Prompt injection makes the model propose a tool call | B3, B4 | The model chooses arguments only; identity, approval and budget come from the session | `test_execution_budget_stops_runaway_tool_calls` | Tool authorization |
| T2 | Documents shown to an adjuster without permission (SIU, drafts) | B2 | Group ACLs filtered before ranking; no ACL means no access | `test_restricted_groups_and_missing_acl_fail_closed` | `permission_leaks` = 0 |
| T3 | One tenant's documents reaching another | B2 | Tenant match required; one index per permission set | `test_cross_tenant_chunks_never_retrieved` | `permission_leaks` = 0 |
| T4 | Personal data leaving the network | B3 | Redaction before retrieval and prompting | `test_pii_never_reaches_model` | Capstone PII gate |
| T5 | A claim review opened without authority, twice, or in a loop | B4 | Assigned adjuster or supervisor; another supervisor's approval; idempotency key; execution budget | `test_tool_requires_authorization`, `test_tool_requires_valid_approval`, `test_tool_is_idempotent` | Tool approval |
| T6 | Secrets or internals in errors | B1 | Generic 500 body with a request id | `test_http_api` | G3 |
| T7 | A confident wrong answer acted on | B3 | Abstain on weak coverage; citations validated; promises blocked | `test_abstains_without_calling_model`, `test_guardrail_blocks_promises` | `false_answer_rate` = 0 |

## Security findings
**SF-1 (high), found in week 6 by the security probes, fixed in week 7.** The v0 build indexed every document on
the shared platform into one index without ACLs. All five probes leaked (measured: `test_v0_fails_the_gates`): an
adjuster retrieved SIU referral guidance and another tenant's marine endorsement, a Harbor Mutual adjuster retrieved
Northwind's claims guide, and v0 answered an unanswerable question from an unpublished draft bulletin. Root cause:
ACLs weren't copied at ingestion, and the retriever had no notion of a caller. Fix: `tenancy.py` filters by tenant
and group *before* ranking, re-checks every hit, and treats a missing ACL or a missing principal as no access.
Retest: 0 of 5 probes leak (measured: `test_remediated_build_passes_every_gate`).

**SF-2 (medium), found in design review in week 5.** The first tool design returned "claim not found" for unknown
claims and "forbidden" for another tenant's claims, which confirms that a claim number exists. Fix: both return
`forbidden` (`test_tool_requires_authorization`).

## Negative tests
`test_cross_tenant_chunks_never_retrieved`, `test_restricted_groups_and_missing_acl_fail_closed`,
`test_copilot_without_principal_fails_closed`, `test_pii_never_reaches_model`, `test_tool_requires_authorization`,
`test_tool_requires_valid_approval`, `test_tool_is_idempotent`, `test_execution_budget_stops_runaway_tool_calls`,
`test_http_api`, `test_guardrail_blocks_promises`, and the security probes in `data/security_probes.jsonl`.
