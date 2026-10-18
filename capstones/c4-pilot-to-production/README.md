# Capstone 4 · Pilot to production in a constrained customer environment

**Covers:** R01 Python · R06 Cloud · R07 Containers/K8s/CI · R15 Observability · R20 Ambiguity · R22 Production ·
R24 Writing · R26 On-site embedding · R27 Cost & latency · R28 Architecture · R29 Debugging
**Suggested time:** 3 days · **Builds on:** ex09–ex14, ex20, ex21, ex57–ex66

## The engagement
A logistics company's shipment-exception summarizer (`data/legacy_pilot.py`) impressed executives in a demo. In
its first real afternoon it fell over. `data/pilot_incident.log` is all the evidence you have. The customer wants it
in production in three weeks, on their on-prem Kubernetes cluster:
- egress only through an authenticated corporate proxy, TLS inspected with a corporate root CA
- outbound traffic allowed only to the internal LLM gateway
- a platform admission policy for images, manifests and CI pipelines
- an SLO the SRE team will page on

Nobody can give you real traffic forecasts. Make reasonable assumptions, **write them down**, and design so they're
cheap to revisit.

## What you build (`starter/pilot/`)
| Module | Responsibility |
|---|---|
| `config.py` | Typed settings from env, aggregated errors, secret masking, egress allowlist check |
| `resilience.py` | `ResilientLLM`: retries with jittered backoff (honour `retry_after`), fallback model on overload, circuit breaker |
| `observability.py` | Prometheus text-format counters and histograms; JSON logger |
| `service.py` | `/healthz`, `/readyz` (red when the circuit is open), `/metrics`, authenticated `/v1/summarize` with limits; 503 + `Retry-After` in degraded mode; never log payloads |
| `slo.py` | Burn-rate alerts (page 14.4x over 1 h and 5 m; ticket 6x over 6 h and 30 m) |
| `preflight.py` | Run on site: config, DNS, egress via proxy, allowlist, CA bundle → PASS/WARN/FAIL (+ CLI) |
| `incident.py` | Turn the pilot's incident log into findings, each paired with its fix |
| `loadtest.py` | HTTP load generator and a Little's-law replica estimate |
| `policy.py` | The platform team's admission rules for Dockerfile, Kubernetes manifests and CI |
| `main.py` | Container entry point |

Fix the deploy artifacts in `starter/deploy/` (`Dockerfile`, `k8s.yaml`, `ci.yml`) until `policy.py` is happy.

## Deliverables (`starter/deliverables/`)
- `production_readiness_review.md`: summary, **assumptions**, incident findings → fixes, a checklist (≥ 8 items done),
  capacity math, open risks, sign-off.
- `runbook.md`: deploy, rollback, alerts, degraded mode, customer-environment specifics, escalation.

## Run
```bash
pytest capstones/c4-pilot-to-production
pytest --solutions capstones/c4-pilot-to-production
```
