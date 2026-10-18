# Capstone 1 · Enterprise Support Copilot (insurance)

**Covers:** R01 Python · R02 TypeScript · R08 LLM apps · R09 Prompt/context · R10 RAG · R13 Evals · R14 Guardrails ·
R16 ML baseline · R18 Discovery · R19 Exec communication · R22 Production · R24 Writing · R25 Regulated domain ·
R27 Cost · R30 Value metrics
**Suggested time:** 2–3 days · **Builds on:** ex01, ex03, ex20, ex31–ex41, ex49, ex53, ex55, ex69
**Take after:** End of Part III: after ex31–ex41, ex49 and ex53–ex55, plus ex01, ex03 and ex69 from Part I and ex20 from Part II.

## The engagement
Northwind Insurance's 400 claims adjusters spend about 11 minutes per coverage question digging through policy
PDFs. The VP of Claims has funded a 6-week pilot of a copilot that answers adjusters' questions **from the policy
text, with citations**. Compliance has two non-negotiables: every answer cites its source, and when the documents
don't contain the answer the copilot must say so. IT Security requires that no policyholder PII leaves the VPC
unredacted. Finance caps model spend at $0.02 per question.

Data in `data/`: three policy documents, a 12-case golden set agreed with Compliance, and labelled intent examples.

## What you build (`starter/copilot/`)
| Module | Responsibility |
|---|---|
| `ingest.py` | Heading-aware chunking that keeps each section's path (`Policy > Coverage > Flood`) |
| `retrieval.py` | Hybrid BM25 + vector retrieval fused with RRF; each hit reports query-token `coverage` |
| `intent.py` | Naive Bayes intent router (`policy_question`, `claim_status`, `speak_to_human`) + claim-id rule |
| `pii.py` | Tokenise emails/phones/policy numbers before any model call; restore afterwards |
| `guard.py` | Block promises ("guaranteed"), drop unsupported sentences |
| `answer.py` | The request path: route → redact → retrieve → abstain or generate → validate citations → guard → restore; per-request cost budget |
| `evals.py` | Golden-set runner and the launch bar (pass rate ≥ 90%, citation precision ≥ 95%, zero answers to unanswerable questions) |
| `readout.py` | Executive readout generated from measured metrics and an ROI model |
| `app.py` | Authenticated JSON API with health check |
| `web/answer_view.ts` | Escaped HTML rendering of answers with footnote citations for the agent desktop |

## Deliverables (`starter/deliverables/`)
- `discovery_brief.md`: problem, users, quantified success metrics, data, constraints, out of scope, stakeholders.
- `runbook.md`: deploy, rollback, monitoring, re-indexing and escalation for the Claims Platform team.

## Milestones
1. **Day 1:** discovery brief signed off; ingest + retrieval passing `test_c1_ingest_retrieval.py`.
2. **Day 2:** the request path with routing, PII handling, citations and guardrails (`test_c1_copilot.py`).
3. **Day 3:** golden set over the launch bar, readout generated, API + widget + runbook done.

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
| Correctness | All tests green; launch bar met with margin |
| Safety | No PII in prompts; abstains rather than guesses; guardrails can't be bypassed by citation tricks |
| Engineering | Clear module boundaries; cost budget enforced; API errors never leak internals |
| Communication | Readout leads with the recommendation; every number traces back to an eval |
