# Performance test plan

| | |
|---|---|
| **Owner** | FDE with the SRE team |
| **When** | Before the pilot ends; re-run on model, prompt or load changes |
| **Inputs** | Pilot logs (token counts, journeys), expected users and arrival pattern, provider quotas |
| **Done when** | Targets agreed with the sponsor and SRE team; every test in the matrix has a pass condition |
| **Book** | Chapter 14, Section 14.5 · ex60, ex62 |

## 1. Workload model
| Journey | Share | Input tokens p50 / p95 | Output tokens p50 / p95 | Tool calls | Streamed or full |
|---|---|---|---|---|---|

Arrival model (open): peak ______ req/s; bursts ______; session length ______
Provider quota: ______ requests/min, ______ input tokens/min, ______ output tokens/min

## 2. Targets
| Measure | Target |
|---|---|
| Time to first token p95 (streamed) | |
| Full response p95 / p99 (streamed) | |
| Full response p95 (non-streamed) | |
| Output tokens per second p50 | |
| Sustained throughput | |
| Error rate / timeout rate | |
| Cost per successful task | |
| Quality under load | |

## 3. Latency budget (p95)
| Stage | Budget |
|---|---|
| Queueing | |
| Network (including the proxy) | |
| Auth, validation, routing | |
| Retrieval and reranking | |
| Tool calls | |
| Model time to first token | |
| Generation | |
| Output checks | |

## 4. Test matrix
Baseline · peak · stress (step until a target breaks) · spike · soak · cold cache · prompt growth · model change ·
rate limits · degraded dependency · retry amplification. For each: load, duration, pass condition, fake or real model,
spending limit.

## 5. Quality under load
Golden-set cases mixed into the load: ______; live answers judged: ______; pass condition: ______
