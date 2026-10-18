# Order-ops agent runbook

## Overview
The agent handles refund and order-status requests from the support inbox. It moves money only through the
`issue_refund` tool, under the refund policy, and refunds above $100 wait in the approval queue. Owner: Support
Engineering.

## Deploy
```bash
kubectl -n support-prod set image deploy/ops-agent app=registry.retail.example/ops-agent:<IMAGE_TAG>
kubectl -n support-prod rollout status deploy/ops-agent --timeout=5m
```
IMAGE_TAG is the CI release tag. CI blocks the release unless the scenario evals report zero policy violations.

## Rollback
```bash
kubectl -n support-prod rollout undo deploy/ops-agent
```
Kill switch: set `OPS_AGENT_REFUNDS_ENABLED=false` to keep answering status questions while refunds go to humans.

## Approval queue
- Supervisors review pending refunds in the support console. The target is approval within 4 business hours.
- Alert if the oldest pending approval is older than 8 hours or the queue holds more than 50 items.

## Monitoring
- Refunds per hour and total refund value per day (alert above 3x the 7-day average).
- Blocked-injection rate (spikes usually mean a targeted campaign; notify Security).
- Audit chain verification runs hourly; any failure is a security incident.

## Escalation
1. Support Engineering on-call: support-eng-oncall@retail.example, +1 206 555 0142.
2. Security (suspected fraud or injection campaign): security@retail.example.
3. Finance (refund anomalies): finance-ops@retail.example.
