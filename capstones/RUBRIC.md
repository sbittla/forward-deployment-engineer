# Capstone assessment rubric

Every capstone is assessed the same way, so a reviewer, an instructor or you can tell whether a submission meets the
bar. There are two parts, and the order matters: **gates first, then a weighted score.** A failed gate can't be
offset by a high score anywhere else. This is the same structure as the production-readiness scorecard in Chapter 14
of the book (Section 14.9).

## 1. Gates (all must pass)

Every capstone has these four gates, plus its own gates listed in section 4.

- **G1 · Tests.** `pytest capstones/<capstone>` is green from a clean checkout, with no tests skipped or deleted.
- **G2 · Critical correctness.** The capstone's critical behaviours (section 4) hold, shown by tests or eval results.
- **G3 · Security and privacy.** No secrets in code or logs; the capstone's security gates (section 4) pass, shown by
  a negative test (one that tries to make the system misbehave and confirms it can't).
- **G4 · Honest reporting.** Every number in the deliverables traces to a test, an eval run or a stated assumption,
  and is labelled as measured, assumed, estimated or projected.

## 2. Weighted dimensions

Score each dimension from 0 to 4: **0** missing · **1** present but ad hoc · **2** documented · **3** tested or
measured, with evidence · **4** evidence a customer's team could take over unchanged.

| Dimension | Weight | Evidence to require | A 3 looks like |
|---|---|---|---|
| Problem and acceptance criteria | 10% | Problem statement, stakeholders, measurable outcomes, explicit non-goals | Clear, testable and agreed: every outcome has a baseline, a target and a measurement |
| Functional behaviour | 15% | Automated tests, edge cases, error handling, deterministic reproduction | Correct and robust: error paths tested, not only the happy path |
| AI quality | 15% | Evaluation dataset, slice-level results, failure analysis, regression evidence | Meets the stated quality bar on every slice, with failures classified |
| Security and privacy | 15% | Threat model, authorisation tests, tenant isolation, secrets and retention controls | All mandatory gates pass, each with a negative test |
| Performance and reliability | 10% | Workload model, latency and throughput results, failure and recovery tests | Meets defined targets; degraded modes tested |
| Economics | 10% | Cost model, assumptions, cost per successful task, sensitivity analysis | Transparent and plausible; the dominant assumption is identified |
| Production operations | 10% | Monitoring, alerts, runbook, rollback, ownership, incident process | Operable by another team: someone else could run the rollback from the runbook |
| Customer adoption | 5% | Workflow fit, onboarding, feedback loop, usage and outcome measures | The adoption plan is measurable and has an owner |
| Handover and communication | 10% | Architecture summary, known limitations, decision log, demo, handover checklist | Another team can maintain it; the readout leads with a decision |

**Bar:** all gates pass, a weighted score of at least **3.0**, and no dimension below **2**. Below the bar, the
scorecard says exactly what to improve: the lowest-scoring dimension, and the evidence that would raise it.

The weights suit a general-purpose review. A capstone that's mostly delivery (C6) or mostly safety (C2) may shift
weight towards its focus; write the change down before scoring, not after.

## 3. Scorecard to submit

Copy this into `starter/deliverables/scorecard.md` and fill it in.

```markdown
# Capstone <n> scorecard
## Gates
- [ ] G1 Tests green from a clean checkout (command and date)
- [ ] G2 Critical correctness (evidence)
- [ ] G3 Security and privacy (negative tests)
- [ ] G4 Honest reporting (every number labelled)
- [ ] Capstone gates (list each, with evidence)
## Dimensions
| Dimension | Weight | Score | Evidence |
|---|---|---|---|
## Weighted total and decision
## What I'd improve next
```

## 4. Per-capstone criteria

### C1 · Enterprise support copilot
- **Required artefacts:** the `copilot/` modules, `discovery_brief.md`, `runbook.md`, a generated readout.
- **Acceptance criteria:** golden-set pass rate ≥ 90%; citation precision ≥ 95%; zero answers to unanswerable
  questions; per-question model spend within $0.02.
- **Capstone gates:** no PII in any prompt sent to the model (negative test with PII in the question); the copilot
  abstains rather than answers when retrieval is weak; API errors never leak internals.
- **Test evidence:** `test_c1_ingest_retrieval.py`, `test_c1_copilot.py`; the eval report.

### C2 · Agentic order operations over MCP
- **Required artefacts:** the `opsagent/` modules, `design_doc.md`, `runbook.md`, `product_feedback.md`.
- **Acceptance criteria:** every scenario reaches its expected outcome; the independent policy re-check finds no
  refund outside policy.
- **Capstone gates:** tools can only touch the authenticated customer's orders; refunds over $100 never execute
  without approval; an injected instruction can't cause a refund; the audit chain verifies; MCP clients of both eras
  are served.
- **Test evidence:** the scenario eval run and the policy re-check.

### C3 · Lakehouse analyst
- **Required artefacts:** the `insights/` modules, `analyst_guide.md`, `exec_readout.md`.
- **Acceptance criteria:** execution accuracy against the gold queries as stated in your readout; every bad row
  quarantined with a reason; no data lost silently between bronze and gold.
- **Capstone gates:** the SQL guard blocks every write, multi-statement, system-table and non-allow-listed query
  (negative tests with the malicious attempts); the assistant refuses rather than invents a number.
- **Test evidence:** the ETL load report, the eval run with refusal accuracy and the unsafe-blocked count.

### C4 · Pilot to production
- **Required artefacts:** the `pilot/` modules, fixed deploy artefacts, `production_readiness_review.md`,
  `performance_test_plan.md`, `runbook.md`.
- **Acceptance criteria:** the platform policy accepts the Dockerfile, manifests and CI; every incident finding is
  paired with a fix; capacity is explained with Little's Law and written assumptions.
- **Capstone gates:** secrets never logged; readiness reports not ready while the circuit is open; burn-rate alerts
  fire as specified; a canary that regresses on quality is rolled back even when its errors and latency match; the
  readiness review applies gates before any score.
- **Test evidence:** the policy check output, the load test, the SLO and canary tests, and the performance test
  plan's report.

### C5 · Embedded field engagement
- **Required artefacts:** the `engagement/` modules, `stakeholder_update.md`, `handoff_runbook.md`,
  `product_feedback.md`, the generated board readout.
- **Acceptance criteria:** urgent-case recall of 100% (every emergency caught as an emergency); field accuracy as
  stated in the readout; assumptions for every open discovery question.
- **Capstone gates:** no PHI in any outbound prompt (the PHI guard blocks a deliberately leaky prompt); triage can
  only escalate, never downgrade, the model's urgency.
- **Test evidence:** the eval run, including the under-triaged chest-pain call.

### C6 · Deployment lead
- **Required artefacts:** the `deliverylead/` modules, `sow.md`, `partner_review_memo.md`, `enablement_plan.md`, the
  generated steering update.
- **Acceptance criteria:** the forecast, variance and go-live decision match the agreed rules; every blocker and
  condition is listed with its reason; the SOW has acceptance criteria per milestone, support boundaries and exit
  criteria.
- **Capstone gates:** questions on physical security and model risk always go to humans; a rejected partner
  deliverable always blocks go-live.
- **Test evidence:** the capstone tests and the generated steering update.

## 5. Two sample submissions (C1)

**Strong (weighted 3.4, all gates pass).** Tests green from a clean checkout. The eval report shows 11 of 12 golden
cases passing (92%), the unanswerable case (g09) abstained, citation precision 100%, broken down by slice, with the one
failure classified ("exclusion in a different chunk") and a proposed fix. A negative test puts an email address and
a policy number in the question and asserts neither reaches the fake model. The readout opens with "Recommend a
two-team pilot with a control group", labels the 4-minute saving as assumed, and shows a sensitivity table in which
adoption dominates. The runbook's rollback was run by someone else, and the scorecard says so. Weakest dimension:
adoption (2), because the plan has no per-team targets, and the scorecard says that's next.

**Borderline (weighted 2.9; fails G4).** Tests green and the launch bar met, so it looks finished. But the readout
says "the copilot will save $864,000 a year" with no status labels and no sensitivity table, and quotes a 95% pass
rate that doesn't match the eval report's 92%. The runbook's rollback section says "redeploy the previous version".
There's no negative test for PII; the submission relies on the module working as designed. The fix is small but
essential: label and reconcile every number, add the PII negative test, and write the rollback command. Then G4
passes and the score clears 3.0.
