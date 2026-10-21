# Support copilot runbook

## Overview
The copilot answers adjusters' coverage questions from indexed policy documents, with citations. It routes
claim-status questions to the claims system and escalates "talk to a person" requests. Owner: Claims Platform team.

## Deploy
```bash
kubectl -n claims-prod set image deploy/copilot app=registry.northwind.example/copilot:<IMAGE_TAG>
kubectl -n claims-prod rollout status deploy/copilot --timeout=5m
```
IMAGE_TAG is the release tag produced by CI after the eval gate passes.

## Rollback
```bash
kubectl -n claims-prod rollout undo deploy/copilot
```
Roll back first whenever the golden-set pass rate drops below 90% or the abstention check fails after a release.
During a canary the rollback is automatic (`slo.run_rollout`); run the command above only when it didn't happen.

## Monitoring
- Golden-set eval runs nightly. Alert if the pass rate is below 90% or the false-answer rate is above 0%.
- Track average cost per question (budget $0.02) and the share of abstentions. A sudden jump in abstentions
  usually means the policy index is stale.
- SLO: 99.5% of requests succeed and answer within 4 seconds (`slo.SLO`). Page on a 14.4x burn over 1 hour and 5
  minutes; ticket on a 6x burn over 6 hours and 30 minutes.
- Blocked documents from `sync_corpus` (its report's `blocked` list) alert the policy platform team.

## Re-indexing policy documents
```bash
python -m copilot.ingest --source /mnt/policies --out /var/lib/copilot/index
```
Run after every policy form change, then run the golden-set eval before switching traffic to the new index.

## Escalation
1. Claims Platform on-call: claims-platform-oncall@northwind.example, +1 415 555 0100.
2. Compliance (for any answer that cited the wrong policy): compliance-ai@northwind.example.

## Dashboards
One dashboard, four rows, each panel with its alert threshold drawn on it:
1. **Reliability:** request rate, SLO burn rate (1 h and 6 h), error rate, p50 and p95 latency.
2. **Quality:** nightly golden-set pass rate, false-answer rate, over-refusal rate, abstention share, degraded share.
3. **Safety:** permission-probe leaks (must be 0), PII-scan hits on outbound prompts, claim reviews opened, refused
   tool calls by error code (`forbidden`, `approval_invalid`, `budget_exceeded`).
4. **Cost:** model cost per successful answer and per team per day, against the $0.025 gate.

## Canary rollout
1. Deploy the candidate to 10% of adjusters. Compare it with the base over the same window (`canary_decision`).
2. After at least 500 canary requests: promote to 50%, then 100%, with the same comparison at each stage.
3. Any permission leak, any answer to an unanswerable question, a pass-rate drop over 3 points, an error rate over
   1.5x the base's, a p95 over 1.2x, or cost per success over 1.2x rolls traffic back to 0% automatically.
4. Record each stage's decision and reasons in the release ticket.

## Incident procedure
1. **Declare** in #claims-copilot-incidents; the on-call engineer is incident commander until handed off.
2. **Contain first.** Kill switches, fastest first: turn off claim reviews (`open_claim_review` disabled), switch to
   retrieval-only mode, turn the copilot off. A suspected permission leak is a SEV-1: turn the copilot off, then
   tell IT Security (Priya Shah) within 30 minutes.
3. **Diagnose** with the request id from the user's report: the trace, the retrieved chunk ids, the tool audit log.
4. **Recover:** roll back, or re-index from the last good sync state.
5. **Review** within five working days: a blameless postmortem, a new golden case or probe for the failure, and an
   owner and date for every action.

## Ownership transfer
| Item | From | To | Done when |
|---|---|---|---|
| Service, deploys, on call | FDE team | Claims platform team | Two of their engineers have deployed and rolled back unaided |
| Ingestion and ACL metadata | FDE team | Policy platform team | They've run a sync and resolved a blocked document |
| Golden set and probes | FDE team | Compliance with the claims quality lead | They've added cases from pilot traffic and rerun the gates |
| Dashboards and alerts | FDE team | Claims platform team | A test page reached their rotation |
| FDE access | FDE team | Northwind IT | Revoked at sign-off |
