# Capstone 4 · Pilot to production in a constrained customer environment

**Covers:** R01 Python · R06 Cloud · R07 Containers/K8s/CI · R15 Observability · R20 Ambiguity · R22 Production ·
R24 Writing · R26 On-site embedding · R27 Cost & latency · R28 Architecture · R29 Debugging
**Builds on:** ex09–ex14, ex20, ex21, ex57–ex66
**Take after:** End of Part IV: after ex57–ex66, plus ex09–ex14, ex20 and ex21 from Part II.

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
| `resilience.py` | `ResilientLLM`: retries with jittered backoff (honor `retry_after`), fallback model on overload, circuit breaker |
| `observability.py` | Prometheus text-format counters and histograms; JSON logger |
| `service.py` | `/healthz`, `/readyz` (red when the circuit is open), `/metrics`, authenticated `/v1/summarize` with limits; 503 + `Retry-After` in degraded mode; never log payloads |
| `slo.py` | Burn-rate alerts (page 14.4x over 1 h and 5 m; ticket 6x over 6 h and 30 m); `canary_decision(base, canary, min_requests=500)` → `wait`, `rollback` or `promote` |
| `preflight.py` | Run on site: config, DNS, egress via proxy, allowlist, CA bundle → PASS/WARN/FAIL (+ CLI) |
| `incident.py` | Turn the pilot's incident log into findings, each paired with its fix |
| `loadtest.py` | HTTP load generator and a Little's-law replica estimate |
| `policy.py` | The platform team's admission rules for Dockerfile, Kubernetes manifests and CI |
| `main.py` | Container entry point |

Fix the deploy artifacts in `starter/deploy/` (`Dockerfile`, `k8s.yaml`, `ci.yml`) until `policy.py` is happy.

## Deliverables (`starter/deliverables/`)
- `production_readiness_review.md`: summary, **assumptions**, incident findings → fixes, a checklist (≥ 8 items done),
  **gates** (each marked PASS or FAIL, with evidence) listed **before** a **scorecard** (each dimension's weight and
  score, and the weighted score), capacity math, open risks, sign-off. Any failed gate means not ready, whatever the
  score.
- `performance_test_plan.md`: workload model, targets, latency budget, tests, quality under load, and a report whose
  numbers are each labeled measured, assumed, estimated or projected.
- `runbook.md`: deploy, rollback, alerts, degraded mode, customer-environment specifics, escalation.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run
```bash
pytest capstones/c4-pilot-to-production
pytest --solutions capstones/c4-pilot-to-production
```

## Assessment
Assessed with the shared [capstone rubric](../RUBRIC.md): gates first (tests, critical correctness, security and
privacy, honest reporting, plus this capstone's own gates), then a weighted score across nine dimensions. The bar is
every gate passing, a weighted score of at least 3.0 and no dimension below 2. Section 4 of the rubric lists C4's
acceptance criteria and gates. Submit your scorecard as `starter/deliverables/scorecard.md`.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest capstones/c4-pilot-to-production`.
- **Expected output:** all 22 tests fail against the starter; when you're done, all 22 pass.
- **Check the reference solution:** `pytest --solutions capstones/c4-pilot-to-production`: all 22 pass.
- **Tests:** `tests/test_c4_config_resilience.py`, `tests/test_c4_deploy_docs.py`, `tests/test_c4_ops.py`,
  `tests/test_c4_service.py` (22 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The service, load test and canary decision run locally against a fake model, so their
  numbers are simulated, not measured. Before production, measure against the real model and quota in the customer's
  tenant, run the canary in a progressive-delivery controller with automated rollback, and have the customer's
  operations team rehearse rollback.

