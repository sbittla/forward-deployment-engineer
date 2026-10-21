# Capstone 1 · Enterprise Support Copilot (insurance)

**The book's signature capstone.** It follows Northwind Insurance, the book's running customer, through a whole
engagement: discover, build, extend, evaluate, harden, deploy and prove value. Appendix E tells the same engagement at
full scale; this folder is the part you build and test.

**Covers:** R01 Python · R02 TypeScript · R08 LLM apps · R09 Prompt/context · R10 RAG · R13 Evals · R14 Guardrails ·
R16 ML baseline · R18 Discovery · R19 Exec communication · R22 Production · R24 Writing · R25 Regulated domain ·
R27 Cost · R30 Value metrics
**Builds on:** ex01, ex03, ex20, ex23, ex24, ex31–ex41, ex43, ex46, ex49, ex53, ex55, ex56, ex61, ex62, ex69, ex89, ex90
**Take after:** Start after Part III (stages 1 to 4: ex31–ex41, ex49 and ex53–ex55, plus ex01, ex03 and ex69 from
Part I and ex20 from Part II). Finish stages 5 to 7 after Chapter 14 (Part IV) and Chapter 16 (Part V).

## The engagement
Northwind Insurance's 400 claims adjusters spend about 11 minutes per coverage question digging through policy
PDFs. The VP of Claims has funded a pilot of a copilot that answers adjusters' questions **from the policy text,
with citations**. Compliance has two non-negotiables: every answer cites its source, and when the documents don't
contain the answer the copilot must say so. IT Security requires that no policyholder PII leaves the VPC unredacted,
and that nobody sees a document they couldn't open in the policy archive. Finance caps model spend at $0.02 per
question.

Data in `data/`:

| Path | What it is |
|---|---|
| `policies/` | Northwind's three published policy documents |
| `platform/` | Other documents on the shared platform index: SIU referral guidance (`siu` group only), another tenant's (Harbor Mutual) marine endorsement, and an unpublished draft bulletin with **no ACL** |
| `acl.json` | Tenant and groups per document, as exported by the policy archive |
| `principals.json` | Users: `adjuster`, `adjuster_2`, `supervisor`, `investigator`, `harbor_adjuster`, `harbor_supervisor` |
| `claims.json` | Claims with their tenant and assigned adjuster, for the claim-review tool |
| `golden.jsonl` | 12 cases agreed with Compliance |
| `security_probes.jsonl` | 5 probes: a principal, a question and the `forbidden_docs` that principal must never see |
| `intents.jsonl` | Labeled intent examples |
| `pilot_handle_time.json` | Exercise data: baseline 11.0, target 7.0, pilot 7.5 and control 10.4 minutes |

## The seven stages
Requirements and acceptance criteria are set once, in the charter, and carried unchanged through every stage.

| Stage | Book | What you build | Tests | Gate it feeds |
|---|---|---|---|---|
| 1 · Discover | Ch 2, 3 | Discovery brief, engagement charter with baselines and acceptance criteria | `test_deliverables` | All of them |
| 2 · Build | Ch 6, 10, 13 | Chunking, hybrid retrieval, incremental sync, permission-aware retrieval | `test_c1_ingest_retrieval.py`, `test_c1_tenancy_ingest.py` | `retrieval_recall`, `permission_leaks` |
| 3 · Answer | Ch 9, 10, 13 | The request path: routing, redaction, abstention, citations, guardrails, budget | `test_c1_copilot.py` | `false_answer_rate`, `citation_precision` |
| 4 · Extend | Ch 11 | `open_claim_review`: authorization, approval, idempotency, execution budget | `test_c1_agent_tools.py` | Tool approval |
| 5 · Evaluate | Ch 12 | Golden-set metrics, refusal both ways, slices, security probes | `test_c1_evals_readout.py` | Quality gates |
| 6 · Harden and deploy | Ch 13, 14 | Failure injection, load model, SLO alerts, canary and staged rollout, runbook | `test_c1_resilience.py` | `p95_ms`, `cost_per_success_usd` |
| 7 · Prove value | Ch 3, 16 | Go/no-go from the gates and the baseline; final readout | `test_c1_golive.py` | The decision |

## What you build (`starter/copilot/`)
| Module | Responsibility |
|---|---|
| `ingest.py` | Heading-aware chunking that keeps each section's path (`Policy > Coverage > Flood`); `sync_corpus(dir, previous)` returns `(state, report)`, re-chunking only documents whose SHA-256 changed. The report lists `added`, `changed`, `unchanged`, `removed` and `blocked`: a document that yields no chunks is blocked and its previous version keeps serving. `chunks_of(state)` flattens a state |
| `retrieval.py` | Hybrid BM25 + vector retrieval fused with RRF; each hit reports query-token `coverage` |
| `tenancy.py` | `Principal(user, tenant, groups)`, `Acl(tenant, groups)`, `load_acl`, `load_principals`; `can_read(principal, acl)` is false for a missing principal, a missing ACL, another tenant or no shared group. `PermissionAwareRetriever(chunks, acl)` filters **before** ranking; `search(query, principal, k)` returns `[]` with no principal |
| `intent.py` | Naive Bayes intent router (`policy_question`, `claim_status`, `speak_to_human`) + claim-id rule |
| `pii.py` | Tokenize emails/phones/policy numbers before any model call; restore afterward |
| `guard.py` | Block promises ("guaranteed"), drop unsupported sentences |
| `answer.py` | The request path: route → redact → retrieve → abstain or generate → validate citations → guard → restore; per-request cost budget. `ask(question, principal=None)`; `Copilot.search(query, principal)` fails closed for a permission-aware retriever. Faults: a search error returns `SEARCH_DOWN_TEXT`, escalated and `degraded`; the model is tried `1 + max_retries` times, then the response is retrieval-only (`MODEL_DOWN_TEXT` plus the numbered section paths, `degraded`, no cost) |
| `tools.py` | `ClaimReviewTool(claims).open_claim_review(principal, claim_id, reason, *, idempotency_key, budget, approval=None)`. Order: `ExecutionBudget.spend()` (every attempt counts) → authorization (same tenant, `claims` group, assigned adjuster or `supervisors`; unknown claims also get `forbidden`) → idempotency (same key returns the first result with `replayed: True`; same key, different arguments is `idempotency_conflict`) → approval (none: `pending_approval`, nothing changes; an `Approval(approver, claim_id)` must come from another supervisor in the same tenant for the same claim, else `approval_invalid`) → open `RV-0001`. Errors raise `ToolError` with a `code`; every outcome goes to `audit`. `execute_tool_calls(calls, tool, principal, request_id, budget, approvals)` runs a model's `ToolCall`s with key `"<request_id>:<claim_id>"`, never raises, and refuses unknown tools (`unknown_tool`). `load_claims` reads `claims.json` |
| `faults.py` | Given: `FaultyLLM(llm, error, fail_on)` (counts `attempts`) and `FaultyRetriever(retriever)` inject a timeout or an index outage |
| `evals.py` | Golden-set runner and the launch bar (pass rate ≥ 90%, intent accuracy ≥ 90%, citation precision ≥ 95%, zero answers to unanswerable questions). `run_golden(copilot, golden, principal=None)` also reports `over_refusal_rate`, `retrieval_recall` (an expected document in the top k), `slices` (by intent, plus `unanswerable`), `successes` and `total_cost_usd`. `run_security(copilot, probes, principals)` counts a leak when a forbidden document is retrieved or cited: `{"probes", "leaks", "leaked"}` |
| `loadmodel.py` | `run_load(copilot, cases, principal=None, repeats=5, latency=LatencyModel())`: deterministic replay with simulated latency (routing, retrieval, time to first token, per-token time) and computed cost; reports `requests`, `p50_ms`, `p95_ms`, `max_ms`, `successes`, `cost_per_success_usd`. `percentile` is nearest-rank |
| `slo.py` | `SLO(target=0.995, latency_threshold_ms=4000)` with `burn_rate` and `alerts` (page at 14.4x over `HOUR` and 5 minutes; ticket at 6x over 6 hours and 30 minutes). `canary_decision(base, canary)` returns `("wait" \| "rollback" \| "promote", reasons)`; `run_rollout(base, observe)` walks `ROLLOUT_STAGES` (10, 50, 100) and rolls back to 0% automatically |
| `golive.py` | `GATES`, `check_gates(evidence)` (a missing value fails), `collect_evidence(copilot, data_dir)`, `load_value`, `go_no_go(evidence, value)` and `render_decision(result)` |
| `build.py` | `build_copilot(llm, data_dir, naive=False)`: the remediated build, or the v0 thin slice with `naive=True` |
| `readout.py` | Executive readout generated from measured metrics and an ROI model |
| `app.py` | Authenticated JSON API with health check |
| `web/answer_view.ts` | Escaped HTML rendering of answers with footnote citations for the agent desktop |

## Objective gates
`golive.check_gates` applies these to the evidence from `collect_evidence` (the golden set and the probes asked as
`adjuster`, the load model over the golden set). Any failure is a blocker.

| Gate | Threshold | Measures |
|---|---|---|
| `pass_rate` | ≥ 0.90 | Task success |
| `intent_accuracy` | ≥ 0.90 | Routing |
| `citation_precision` | ≥ 0.95 | Citation accuracy |
| `retrieval_recall` | ≥ 0.90 | Retrieval quality |
| `false_answer_rate` | ≤ 0 | Refusal: never answer the unanswerable |
| `over_refusal_rate` | ≤ 0.10 | Refusal: still answer the answerable |
| `permission_leaks` | ≤ 0 | Cross-tenant and group isolation |
| `p95_ms` | ≤ 4000 | Latency (simulated) |
| `cost_per_success_usd` | ≤ 0.025 | Cost per successful answer (computed) |

`go_no_go(evidence, value)`: any failed gate is **no-go**. With every gate passing, the pilot at or under the target
is **go**; a positive effect against control (`control_min - pilot_min`) that misses the target is **go with
conditions**, with a condition naming the miss; no effect is **no-go**. The result carries `decision`, `gates`,
`blockers`, `conditions` and `value` (with `effect_vs_control_min` and `target_met`). `render_decision` writes
`## Decision`, `## Gates` and `## Value against the baseline`.

## v0 and its remediation
The first build that worked in a demo is kept as `build_copilot(llm, data_dir, naive=True)`: every document in one
index without ACLs, and no abstention threshold. It passes 11 of 12 golden cases (92%), the one number the demo
showed. The gates stop it (`test_v0_fails_the_gates`):

| Defect | Caught by | Remediation |
|---|---|---|
| Answers the unanswerable cryptocurrency question from the unpublished draft bulletin | `false_answer_rate` = 1.0 | Coverage threshold 0.4; documents without an ACL are invisible |
| All 5 security probes leak: SIU guidance, the other tenant's documents both ways, the draft | `permission_leaks` = 5 | `PermissionAwareRetriever`: filter before ranking, fail closed |
| Cites the draft where no document was expected | `citation_precision` = 0.90 | Same ACL fix |

The remediated build passes every gate and, with the pilot's exercise data, `go_no_go` returns **go with
conditions** (`test_go_no_go_compares_value_with_baseline`).

## Engagement events
The engagement includes the five events every real one has. Record each in the deliverables named.

| Event | What happened | Where it's recorded |
|---|---|---|
| Failed experiment | v0 passed the demo and failed three gates | `evaluation_report.md` ("v0 against v1") |
| Changed requirement | Week 5: adjusters asked to open a claim review (it pauses payment) from the copilot. A consequential action, so it needs approval | `engagement_charter.md` change log; `tools.py` |
| Security finding | Week 6: the probes found SIU and other-tenant documents retrievable (SF-1) | `threat_model.md` |
| Budget constraint | $0.02 worst-case per question (`_fit_budget` trims sources); 3 tool calls per request; $0.025 per successful answer at go-live | `engagement_charter.md` |
| Go/no-go | Computed, not argued: `go_no_go` | `final_readout.md` |

## Deliverables (`starter/deliverables/`)
- `discovery_brief.md`: problem, users, quantified success metrics, data, constraints, out of scope, stakeholders.
- `engagement_charter.md`: sponsor, problem and baseline, acceptance criteria, scope, stakeholders, budget, change log.
- `architecture.md`: a diagram (Mermaid or ASCII), components, trust boundaries, degraded modes.
- `threat_model.md`: assets, threats with controls and negative tests, security findings.
- `evaluation_report.md`: test sets, results, slices, failure analysis, latency and cost, v0 against v1.
- `test_report.md`: summary, gates, failure injection, load model, known gaps.
- `runbook.md`: deploy, rollback, monitoring, re-indexing, escalation, dashboards, canary rollout, incident
  procedure and ownership transfer for the Claims Platform team.
- `final_readout.md`: decision, value against the baseline, gates, risks, conditions, ownership transfer.

The evaluation report, test report and final readout must say which numbers are measured; label the rest computed,
simulated, exercise data or illustrative. Templates for each are in `playbook/`.

## Milestones
1. **Day 1:** discovery brief and charter signed off; ingest + retrieval passing `test_c1_ingest_retrieval.py`.
2. **Day 2:** the request path with routing, PII handling, citations and guardrails (`test_c1_copilot.py`).
3. **Day 3:** golden set over the launch bar, readout generated, API + widget + runbook done. End of Part III.
4. **Day 4:** permission-aware retrieval and incremental sync (`test_c1_tenancy_ingest.py`); the claim-review tool
   (`test_c1_agent_tools.py`); threat model.
5. **Day 5:** failure injection, load model, SLO and rollout (`test_c1_resilience.py`); evaluation and test reports.
6. **Day 6:** v0 against v1 and the go/no-go (`test_c1_golive.py`); architecture and final readout.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run
```bash
pytest capstones/c1-support-copilot              # your work (starts red)
pytest --solutions capstones/c1-support-copilot  # reference solution
```
The tests use a deterministic fake model. To try a real model, construct `Copilot(AnthropicLLM(), ...)` with
`FDE_LIVE=1` and your credentials. Expect wording to differ, which is exactly why the eval harness exists.

## Grading rubric (self-assessment)
| Area | Excellent |
|---|---|
| Correctness | All tests green; every gate met with margin |
| Safety | No PII in prompts; no document outside the caller's permissions; abstains rather than guesses; no consequential action without approval |
| Engineering | Clear module boundaries; cost and tool budgets enforced; faults degrade safely; API errors never leak internals |
| Communication | Readout leads with the decision; every number traces back to a test or eval and carries its label |

## Assessment
Assessed with the shared [capstone rubric](../RUBRIC.md): gates first (tests, critical correctness, security and
privacy, honest reporting, plus this capstone's own gates), then a weighted score across nine dimensions. The bar is
every gate passing, a weighted score of at least 3.0 and no dimension below 2. Section 4 of the rubric lists C1's
acceptance criteria and gates. Submit your scorecard as `starter/deliverables/scorecard.md`.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest capstones/c1-support-copilot`.
- **Expected output:** all 42 tests fail against the starter; when you're done, all 42 pass.
- **Check the reference solution:** `pytest --solutions capstones/c1-support-copilot`: all 42 pass.
- **Tests:** `tests/test_c1_agent_tools.py`, `tests/test_c1_app_widget_docs.py`, `tests/test_c1_copilot.py`,
  `tests/test_c1_evals_readout.py`, `tests/test_c1_golive.py`, `tests/test_c1_ingest_retrieval.py`,
  `tests/test_c1_resilience.py`, `tests/test_c1_tenancy_ingest.py` (42 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** PII handling is regex-based (names pass through), the API trusts static bearer tokens, ACLs
  come from a JSON file rather than the policy archive and identity provider, latency comes from a simulated load
  model, and the guard trusts every indexed document. Production adds NER-based redaction with measured recall, OIDC
  sign-in with token validation (ex89), a real load test (ex62, Capstone 4) and the security release gates of Section
  13.6 run against the shipped configuration.

