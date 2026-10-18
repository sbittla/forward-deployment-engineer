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

## Monitoring
- Golden-set eval runs nightly. Alert if the pass rate is below 90% or the false-answer rate is above 0%.
- Track average cost per question (budget $0.02) and the share of abstentions. A sudden jump in abstentions
  usually means the policy index is stale.
- Request latency SLO: 95% of answers in under 4 seconds.

## Re-indexing policy documents
```bash
python -m copilot.ingest --source /mnt/policies --out /var/lib/copilot/index
```
Run after every policy form change, then run the golden-set eval before switching traffic to the new index.

## Escalation
1. Claims Platform on-call: claims-platform-oncall@northwind.example, +1 415 555 0100.
2. Compliance (for any answer that cited the wrong policy): compliance-ai@northwind.example.
