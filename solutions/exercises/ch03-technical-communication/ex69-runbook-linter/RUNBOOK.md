# Answer service runbook

## Overview
The answer service (`answer-svc`) serves grounded copilot answers to claims adjusters. It runs as a Kubernetes
Deployment (2–10 replicas) behind the `answer-svc` Service and calls the model API through the corporate proxy.
Business owner: Claims Operations. Technical owner: Claims Platform team.

## Prerequisites
- `kubectl` access to the cluster with the `claims-platform-deployer` role.
- NAMESPACE: the target namespace (`claims-prod` or `claims-staging`).
- IMAGE_TAG: the release tag from the CI pipeline (for example `1.0.3`).
- The `answer-svc` secret with key `api-key` exists in NAMESPACE.

## Deploy
```bash
kubectl -n <NAMESPACE> set image deploy/answer-svc app=registry.example.com/answer-svc:<IMAGE_TAG>
kubectl -n <NAMESPACE> rollout status deploy/answer-svc --timeout=5m
```
Verify: `/healthz` returns `{"status": "ok"}` and the eval gate dashboard shows no regression.

## Rollback
```bash
kubectl -n <NAMESPACE> rollout undo deploy/answer-svc
kubectl -n <NAMESPACE> rollout status deploy/answer-svc --timeout=5m
```
Roll back first, investigate second, whenever the error-budget page fires within an hour of a deploy.

## Monitoring
- SLO: 99.5% of requests succeed within 3 s (30-day window).
- Alerts: page on 14.4x burn (1 h and 5 min), ticket on 6x burn (6 h and 30 min).
- Dashboard: Grafana > Copilot > Answer SLO. Traces: search `service.name=answer-svc`.

## Escalation
1. On-call engineer: claims-platform-oncall@northwind.example, +1 415 555 0100.
2. Model API provider status page, then the provider's support channel for the account.
3. Business escalation: Claims Operations duty manager (via the on-call engineer).
