# Summarizer runbook

## Overview
`summarizer` turns shipment-exception reports into 5-bullet summaries for operations managers. It runs in
namespace `logistics-ai` (3 to 12 replicas) and calls the internal LLM gateway through the corporate proxy.
Owner: Logistics Platform team.

## Deploy
```bash
kubectl -n logistics-ai set image deploy/summarizer app=registry.logistics.example/summarizer:<IMAGE_TAG>
kubectl -n logistics-ai rollout status deploy/summarizer --timeout=5m
```
IMAGE_TAG is the git SHA tag built by CI after tests pass.

## Rollback
```bash
kubectl -n logistics-ai rollout undo deploy/summarizer
```

## Alerts
- **Page:** error-budget burn ≥ 14.4x over both 1 h and 5 min. Check `/metrics` for `pilot_llm_calls_total`
  outcomes, then the gateway status page.
- **Ticket:** burn ≥ 6x over 6 h and 30 min.
- **Readiness flapping:** pods are leaving the load balancer because the LLM circuit is open. Treat this as an
  upstream incident.

## Degraded mode
When the primary model is overloaded, requests fall back to the smaller model automatically. If the circuit opens,
clients get `503` with `Retry-After: 30` and readiness turns red until a trial request succeeds. No action is needed
unless this lasts more than 15 minutes.

## Customer environment
- Egress goes only to `llm-gateway.logistics.example` via `http://proxy.logistics.example:3128`.
- TLS inspection uses the corporate root CA at `/etc/ssl/certs/corp-root.pem` (`REQUESTS_CA_BUNDLE`).
- Run `python -m pilot.preflight` in a debug pod after any proxy, DNS or certificate change.

## Escalation
1. Logistics Platform on-call: platform-oncall@logistics.example, +1 312 555 0188.
2. LLM gateway owners: ai-gateway@logistics.example.
3. Network/proxy team (egress or TLS failures): netops@logistics.example.
