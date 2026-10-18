# Production readiness review: shipment-exception summarizer

## Summary
The pilot worked in demos but failed its first real afternoon of traffic: overloads surfaced as errors, requests
hung for 30 seconds, and Kubernetes restarted the container for lack of a health endpoint. Version 2.0 fixes every
finding below. We recommend go-live behind the HPA at 3 replicas, with the sign-offs listed.

## Assumptions
The customer could not provide exact traffic forecasts, so these are written assumptions to revisit after two weeks:
- Peak load is 20 requests/second (3x the pilot's busiest hour), with p95 model latency of 4 seconds.
- The corporate proxy and CA bundle stay as configured in the preflight output from 2026-10-15.
- The LLM gateway's org-level rate limit is at least 4,000 requests/minute.

## Incident findings
| Finding (from `pilot_incident.log`) | Fix in 2.0 |
|---|---|
| 4 upstream 529 overloads were not retried; 4 surfaced as HTTP 500 | Retries with backoff plus a fallback model |
| 3 requests took 30 s or longer (no client timeout) | Timeout and circuit breaker; 503 with Retry-After when open |
| Request backlog reached 128 on a single-threaded server | Threaded server, HPA, capacity plan |
| Liveness probe failed: no `/healthz` | `/healthz` liveness and `/readyz` readiness tied to the circuit |

## Checklist
- [x] Secrets come from Kubernetes secrets; none are in code or images
- [x] All configuration validated at start-up with aggregated errors
- [x] Authentication on every business endpoint; constant-time token comparison
- [x] Input size limits (413) and JSON validation (400)
- [x] Retries, fallback model and circuit breaker around the model client
- [x] Liveness and readiness probes; readiness reflects degraded mode
- [x] Prometheus metrics for request rate, status and latency, plus model-call outcomes
- [x] Structured JSON logs with request IDs; no customer payloads logged
- [x] Image passes platform policy: pinned base, non-root, health check, exec form
- [x] Manifests pass policy: replicas ≥ 2, resources, probes, no literal secrets
- [x] CI: least-privilege token, pinned actions, timeouts, tests gate the image build
- [x] Preflight passes in the customer's staging namespace
- [x] SLO defined (99.5%, 5 s) with multi-window burn-rate alerts

## Capacity
Little's law: 20 req/s × 4 s p95 × 1.3 headroom = 104 requests in flight. At 16 concurrent requests per replica
that is 7 replicas at peak. The HPA runs 3 to 12 replicas, and the load test confirmed linear scaling up to 5
concurrent clients per replica with no errors.

## Open risks
- The fallback model gives shorter summaries. Operations managers were told and accepted this for degraded mode.
- Gateway rate limits are shared with another team. Usage is monitored and the gateway owner is on the escalation path.

## Sign-off
| Role | Name | Status |
|---|---|---|
| Platform engineering | M. Okoro | Approved |
| Security | P. Shah | Approved |
| Operations sponsor | D. Ruiz | Approved |
