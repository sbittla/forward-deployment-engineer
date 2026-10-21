# Capstone 4 hints · Pilot to production in a constrained customer environment

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start where an FDE on site would: read `data/pilot_incident.log` and `data/legacy_pilot.py`, and write down what
broke. Then work out from the incident. Almost every module here is a production version of something you've built:

| Module | Reuse |
|---|---|
| `config.py` | ex09 typed config, ex21 egress allowlist |
| `resilience.py` | ex10 retries, ex14 circuit breaker, ex34 fallback |
| `observability.py` | ex11 logging, plus Prometheus text format |
| `service.py` | ex20 service |
| `slo.py` | ex61 burn rates; the canary listing in Chapter 14 (Section 14.8) |
| `preflight.py` | ex63 checks, ex21 proxy/CA |
| `incident.py` | ex66 log forensics |
| `loadtest.py` | ex62 load and Little's Law |
| `policy.py` | ex57–ex59 linters |

`test_c4_config_resilience.py` is the best first target.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **ResilientLLM:**
  1. Check the breaker; if it's open, raise `CircuitOpen` straight away.
  2. Retry retryable statuses with jittered backoff, honouring `retry_after`.
  3. If the primary is still overloaded after the retries, try the fallback model.
  4. A non-retryable error (400) propagates immediately.
- **The service maps failures to honest status codes:** an upstream error is 502 (and trips the breaker); an open
  circuit is 503 with `Retry-After: 30`; `/readyz` turns 503 while the circuit is open, so the load balancer stops
  sending traffic.
- **Metrics:** counters and histograms keyed by sorted label tuples. A histogram bucket counts observations `<=` its
  bound, cumulatively, and always ends with `+Inf`.
- **Deploy artifacts:** run your own `policy.py` against `starter/deploy/*` and fix them until they're clean.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `required_replicas`: in-flight requests = rps × p95 latency × (1 + headroom), divided by the concurrency per
  replica, rounded **up**, and never fewer than 2 for availability. With the default 30% headroom, 20 rps at 4 s with
  16 slots per replica needs 7. Round before the ceiling to avoid float noise, as in ex62.
- Never log request payloads. Log route, status, latency and request id. The test checks the customer's text is
  absent from the log.
- Prometheus labels are sorted by name inside the braces, so `le` comes before `route`. Bucket bounds print without a
  trailing `.0` (`le="1"`).
- The incident findings must quote the **counts** from the log (4 overloads, 3 slow requests, backlog of 128) and pair
  each finding with its fix.
- Preflight returns WARN, not FAIL, for a missing CA bundle setting, but FAIL when the configured bundle path doesn't
  exist.
- The readiness review needs an explicit **Assumptions** section, because nobody could give you a traffic forecast.
- `canary_decision` checks the request count first: below the minimum, the answer is `wait` whatever the numbers say.
  A canary with the same errors and latency but a judge pass rate four points lower is a `rollback`.
- In the readiness review, put the gates (each PASS or FAIL) above the scorecard: the gates decide, the score coaches.
  In the performance plan, a number you didn't observe in a test is assumed, estimated or projected, never measured.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_settings` | Tokens not wrapped as secrets; redacted view shows tokens instead of a count |
| `test_settings_errors_aggregated` | Raising on the first error; endpoint host not checked against the allowlist |
| `test_retry_then_fallback` | Fallback tried before retries are exhausted; the breaker counts the overloads that the fallback rescued |
| `test_retry_after_and_non_retryable` | `retry_after` ignored; 400 retried or sent to the fallback |
| `test_breaker_opens_and_recovers` | Primary still called while open; no half-open trial after the timeout |
| `test_probes` | `/readyz` doesn't report the circuit state |
| `test_summarize_and_errors` | Size limit checked after parsing; payload text written to the log |
| `test_degrades_gracefully` | Open circuit returns 500 instead of 503 with `Retry-After`; readiness stays green |
| `test_metrics_exposition` | Wrong content type; labels unsorted; histogram missing `+Inf` or `_count` |
| `test_metrics_unit` | Buckets not cumulative; bound formatting (`1.0` instead of `1`) |
| `test_incident_diagnosis` | Counts missing from the finding text; a finding without a fix |
| `test_preflight_pass_warn_fail` | Checks out of order; missing CA treated as FAIL; empty env doesn't fail |
| `test_slo_alerts` | Only one window checked (see ex61) |
| `test_load_and_capacity` | Headroom or the two-replica minimum missing |
| `test_canary_decision` | Request minimum checked last; quality or refusal rate not compared; thresholds applied as ratios instead of points |
| `test_policy_catches_the_legacy_setup` | A rule missing from one of the three linters |
| `test_your_deploy_artifacts_pass` | Your `Dockerfile`, `k8s.yaml` or `ci.yml` still breaks a rule, or there's no HPA |
| `test_deliverables` | A required heading missing, a placeholder left in, or fewer than eight `[x]` checklist items |
| `test_readiness_review_gates_before_score` | Scorecard above the gates; a gate without PASS or FAIL; dimensions without weights; no weighted score |
| `test_performance_plan_labels_numbers` | The report doesn't say which numbers were measured, assumed or estimated |
