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

Write the discovery brief early too. It's what tells you the cost cap, the abstain rule and the PII rule.
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
