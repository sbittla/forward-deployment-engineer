# Capstone 1 hints · Enterprise Support Copilot (insurance)

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Work in milestone order and keep one test file green before starting the next. Day 1 is `ingest.py` and
`retrieval.py` (`test_c1_ingest_retrieval.py`). Most of the code exists already in your solutions:

| Module | Reuse |
|---|---|
| `ingest.py` | ex37 heading chunks (keep the section path) |
| `retrieval.py` | ex38 BM25, ex39 vectors and RRF |
| `intent.py` | ex36 Naive Bayes |
| `pii.py` | ex53 token redaction and restore |
| `guard.py` | ex55 banned phrases and groundedness |
| `answer.py` | ex40 citations and abstention |
| `evals.py` | ex49 harness |
| `readout.py` | ex03 ROI |
| `app.py` | ex20 service |
| `web/answer_view.ts` | ex91 escaping rules |
| `ingest.sync_corpus` | ex23 incremental loads, ex24 blocking quality checks |
| `tenancy.py` | ex89 ACL filtering, ex56 tenant-scoped access |
| `tools.py` | ex43 tool validation, ex46 human approval, ex10 idempotency keys |
| `slo.py`, `loadmodel.py` | ex61 burn-rate alerts, ex62 load test percentiles, Capstone 4's canary |
| `golive.py` | Section 14.7's gates-first scorecard |

Write the discovery brief and the charter early too. They're what tell you the cost cap, the abstain rule, the PII
rule and the acceptance criteria every later stage is judged against. Stages 4 to 7 (`tenancy`, `tools`, `slo`,
`loadmodel`, `golive`) come after Chapters 13, 14 and 16; finish the Part III milestones first.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Build `Copilot.ask` as the exact pipeline in the README, with an early return at each gate:

1. **Route:** "speak to human" escalates and claim-status answers by rule. Neither calls the model.
2. **Redact:** replace PII with tokens before anything leaves the process.
3. **Retrieve** with the redacted question (strip the tokens so `[EMAIL_1]` doesn't affect the search).
4. **Abstain** if the best hit's coverage is low. The model is never called.
5. **Trim** the sources to the budget.
6. **Generate.**
7. **Validate citations:** drop invalid numbers, and escalate if none are left.
8. **Guard.**
9. **Restore** the PII in the final text only.

**Coverage** is the share of the query's content tokens that appear in the chunk. It's your cheap, model-free "do we
even have this?" signal.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Headings with no body text of their own (`Coverage`) produce no chunk, but they still belong in their children's
  paths. The test expects exactly 14 chunks.
- The budget is a **worst-case** estimate made before the call: input tokens from the prompt length plus the maximum
  output tokens, priced per million. Drop the lowest-ranked source until it fits. If even one source doesn't fit,
  abstain rather than calling the model with no context.
- "No valid citation" must escalate, not pass. A citation-free answer is ungrounded by definition.
- `citations` lists doc ids (deduplicated, in order); `chunk_ids` lists the chunks that were actually cited.
- The readout must quote the **measured** pass rate formatted as a percentage, and lead with the recommendation
  ("proceed").
- The widget escapes text *first*, then turns `[n]` into footnote links, so model output can never inject HTML.
- Permissions: filter the chunks a principal may read *before* building the index you rank over. Dropping forbidden
  hits after ranking still lets them crowd out allowed ones. `None` for a principal or an ACL means no access.
- The tool's check order matters: budget, then authorization, then idempotency, then approval. A pending request
  stores nothing, so the approved retry with the same key still opens the review.
- In `execute_tool_calls` the model supplies only `claim_id` and `reason`. The principal and approvals come from the
  caller, which is what makes an injected tool call harmless.
- v0 is meant to fail. If `test_v0_fails_the_gates` fails because v0 *passes*, your evals or probes are too lenient.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_chunks_keep_section_paths` | Body-less headings emitted as chunks; path trail not popped for sibling headings |
| `test_retrieval_ranks_the_right_section` | Section path not included in the indexed text; RRF uses raw scores |
| `test_coverage_definition` | Coverage counted over all tokens instead of the query's content tokens |
| `test_grounded_answer_with_citation` | Cost not recorded; doc ids and chunk ids mixed up |
| `test_abstains_without_calling_model` | Coverage threshold checked after the model call |
| `test_routing` | Claim-status or escalation paths call the model |
| `test_pii_never_reaches_model` | Redaction applied after building the prompt; PII not restored in the final text |
| `test_guardrail_blocks_promises` | Guard result ignored, or the blocked text still returned |
| `test_invalid_citations_removed_and_uncited_escalates` | `[9]` left in the text; uncited answers returned instead of escalated |
| `test_budget_trims_sources` | Budget checked after the call; no abstention when nothing fits |
| `test_golden_set_meets_launch_bar` | One of the earlier gates is wrong; read `metrics["failures"]` for the failing cases |
| `test_launch_bar_reports_misses` | Misses not listed one per failed criterion |
| `test_exec_readout_uses_measured_numbers` | Hard-coded numbers; `business_impact` arithmetic wrong |
| `test_http_api` | Auth or validation order wrong; `request_id` missing from the body |
| `test_answer_view_widget` | See the three widget tests below |
| `citations become footnote links and sources are listed` | Footnote markup differs from `<sup><a href="#src-n">n</a></sup>` |
| `model and customer text is escaped` | Escaping applied after inserting the footnote HTML, or not at all |
| `abstained and escalated states` | State class missing on the wrapper element |
| `test_deliverables` | A required heading missing, a placeholder left in, or the success metrics not quantified |
| `test_eval_reports_refusal_recall_and_slices` | Over-refusal counted over all cases instead of answerable ones; recall run without the redacted, token-stripped query |
| `test_cross_tenant_chunks_never_retrieved` | Tenant not compared, or forbidden hits filtered after ranking |
| `test_restricted_groups_and_missing_acl_fail_closed` | A missing ACL treated as public; an empty group set treated as "any group" |
| `test_copilot_without_principal_fails_closed` | `ask` falls back to an unfiltered search when `principal` is `None` |
| `test_incremental_sync_reindexes_only_changes` | Hash not compared, so every document is re-chunked; removed files not reported |
| `test_sync_blocks_empty_document_and_keeps_previous` | An empty export replaces the good version instead of being blocked |
| `test_tool_requires_authorization` | Unknown claims answered differently from other tenants' claims; audit entries missing |
| `test_tool_requires_valid_approval` | Self-approval allowed; approval's claim or tenant not checked; side effect before approval |
| `test_tool_is_idempotent` | Key stored before approval, or replay not compared against the first call's arguments |
| `test_execution_budget_stops_runaway_tool_calls` | Refused attempts not charged to the budget; `execute_tool_calls` lets a `ToolError` escape |
| `test_model_timeout_retries_once_then_degrades` | Retries unbounded, or the degraded response has a cost or no section paths |
| `test_retrieval_outage_escalates_without_model_call` | Search exception not caught; the model called with no sources |
| `test_load_model_reports_latency_and_cost_per_success` | Wall-clock time used instead of the latency model; cost divided by requests instead of successes |
| `test_burn_rate_alerts` | Slow successes counted as good; one window checked instead of two |
| `test_canary_rolls_back_on_quality_or_leak` | Only errors and latency compared; leaks or false answers not checked |
| `test_staged_rollout_rolls_back_automatically` | Rollout continues after a rollback, or traffic isn't returned to 0% |
| `test_v0_fails_the_gates` | `naive=True` still uses ACLs or the abstention threshold |
| `test_remediated_build_passes_every_gate` | A gate passes on a missing value; probes run without their own principal |
| `test_go_no_go_compares_value_with_baseline` | Effect computed against the baseline instead of the control group; a missed target treated as no-go |
