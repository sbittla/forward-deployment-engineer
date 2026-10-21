# Performance test plan: shipment-exception summarizer

Agreed with the Logistics Platform SRE team and the operations sponsor before go-live. Re-run it whenever the model,
the prompt, the gateway or the load changes. Every number is labeled measured, assumed, estimated or projected.

## Workload model
| Journey | Share | Input | Output | Delivery |
|---|---|---|---|---|
| Summarize one shipment-exception report | 100% | Up to 20,000 characters (the configured limit) | Up to 1,024 tokens, 5 bullets | Full JSON response, not streamed |

- **Arrivals:** an open process; requests arrive whether or not earlier ones have finished. Peak of 20 requests a
  second, three times the pilot's busiest hour (assumed: nobody could give us a forecast).
- **Model latency:** p95 of 4 seconds through the LLM gateway (assumed, from the gateway owner; to be measured).
- **In flight at peak:** 20 × 4 s × 1.3 headroom = 104 requests; at 16 per replica, 7 replicas (estimated, by
  Little's Law from the assumed figures).
- **Gateway quota:** 20 requests a second is 1,200 a minute; with two retries on every call, at most 3,600 a minute,
  under the assumed 4,000-a-minute limit (estimated). The limit is shared with another team.

## Targets
| Measure | Target at the assumed peak |
|---|---|
| Full response (p95 / p99) | 5 s / 10 s (the SLO's latency threshold is 5 s) |
| Errors and timeouts (5xx, or slower than 5 s) | at most 0.5%, the SLO's error budget |
| Sustained throughput within the targets above | 20 requests a second |
| Retries | at most 10% of model calls |
| Degraded mode | an open circuit returns 503 with `Retry-After: 30` within 100 ms, never a hang |

The summary is parsed whole by the operations dashboard, so full-response time is the target; there is no
time-to-first-token target.

## Latency budget
| Stage | Budget (p95) |
|---|---|
| Queueing: admission and waiting for a worker thread | 100 ms |
| Authentication, size limit and JSON validation | 20 ms |
| Network: service to the gateway through the corporate proxy | 150 ms |
| Model call through the gateway | 4,000 ms |
| Metrics and logging | 10 ms |
| **Full response** | **4,280 ms**, inside the 5 s target |

The model takes over 90% of the budget, so the service's own stages are not where a regression will come from;
the proxy hop is measured separately because TLS inspection adds a handshake the pilot never saw.

## Tests
| Test | Load | What it answers |
|---|---|---|
| Baseline | One client, 50 sequential requests | Latency with no contention |
| Peak | Open arrivals at 20 a second for 30 minutes | Do we meet the targets at the assumed peak? |
| Stress | Add 4 requests a second every 5 minutes until a target breaks | Where's the knee, and what breaks first? |
| Spike | From 5 to 20 a second in 10 seconds | Does the HPA scale before the queue backs up? |
| Soak | 20 a second for 2 hours | Thread, memory and connection growth |
| Gateway overload | Gateway returns 529 for 10% of calls | Retries stay within budget; fallback model takes over |
| Circuit open | Gateway unreachable | 503 with `Retry-After`, readiness red, recovery after a trial request |

Peak, stress and spike run in the customer's staging namespace against the real gateway, through the proxy. The
rest run against the fake model, so they cost nothing and repeat exactly. `pilot.loadtest` is a closed-model
generator (fixed workers), right for capacity; user-facing percentiles come from a scheduled-arrival run.

## Quality under load
A fast summary can still be a worse one: under overload the fallback model gives shorter summaries. During the peak
and stress runs, 50 known reports are mixed in at fixed times. Each response must still have five bullets and
mention the shipment id, and an operations manager reviews the summaries the fallback model produced.

## Report
**Verdict: not yet shown at peak.** Only the local runs below are measured. The peak, stress and spike runs need the
customer's staging namespace and the real gateway; until they run, go-live at 20 requests a second rests on the
assumed and estimated figures, and the readiness review records that as an open risk.

| Result | Value | Status |
|---|---|---|
| Pilot latency, the three requests that completed normally | 2.2 to 2.5 s | Measured (pilot log, n = 3: too few for a percentile) |
| Service path against the fake model | 30 requests at concurrency 5, 0 errors | Measured (`pilot.loadtest`, local) |
| Peak load | 20 requests a second | Assumed |
| Model p95 through the gateway | 4 s | Assumed |
| Requests in flight at peak / replicas needed | 104 / 7 | Estimated |
| Gateway calls at peak, worst case with retries | 1,200 / 3,600 a minute | Estimated |
| Staging peak run: full response p95 / p99, errors and timeouts | Not run yet: needs staging and the real gateway | Planned |
| Stress knee | Not run yet | Planned |
| Capacity at the HPA maximum of 12 replicas | about 36 requests a second | Projected (Little's Law; not tested, and above the knee) |

The likeliest first limit is the gateway, not the service: its quota is shared with another team, so the real
ceiling may sit below the assumed 4,000 calls a minute. That is listed in the readiness review's open risks, and the
gateway owners are on the escalation path; the stress run will show which limit breaks first.
