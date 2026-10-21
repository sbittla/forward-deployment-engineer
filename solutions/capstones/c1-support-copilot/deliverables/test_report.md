# Test report: Northwind Insurance support copilot

Command: `python scripts/check.py --solutions capstones/c1-support-copilot` from the repository root. Every test
uses the deterministic fake model; no network or credentials. Numbers are *measured* by that run unless labeled.

## Summary
All tests pass against the reference solution and fail against the starter. The suites, by stage: build
(`test_c1_ingest_retrieval.py`, `test_c1_tenancy_ingest.py`), request path (`test_c1_copilot.py`), extend
(`test_c1_agent_tools.py`), evaluate (`test_c1_evals_readout.py`), harden and deploy (`test_c1_resilience.py`),
prove value (`test_c1_golive.py`), and the API, widget and deliverables (`test_c1_app_widget_docs.py`).

## Gates
| Gate | Threshold | v1 measured | Test |
|---|---|---|---|
| `pass_rate` | ≥ 0.90 | 1.0 | `test_remediated_build_passes_every_gate` |
| `intent_accuracy` | ≥ 0.90 | 1.0 | same |
| `citation_precision` | ≥ 0.95 | 1.0 | same |
| `retrieval_recall` | ≥ 0.90 | 1.0 | same |
| `false_answer_rate` | ≤ 0 | 0.0 | same |
| `over_refusal_rate` | ≤ 0.10 | 0.0 | same |
| `permission_leaks` | ≤ 0 | 0 | same |
| `p95_ms` | ≤ 4,000 | 1,474.5 (simulated) | same |
| `cost_per_success_usd` | ≤ 0.025 | 0.000626 (computed) | same |
| Tool: no review without approval | 0 | 0 | `test_tool_requires_valid_approval` |
| No PII in prompts | 0 | 0 | `test_pii_never_reaches_model` |

A missing measurement fails its gate (`check_gates` fails closed), and v0 fails three gates
(`test_v0_fails_the_gates`).

## Failure injection
| Fault injected | Expected | Result |
|---|---|---|
| Model times out once (`FaultyLLM(fail_on={1})`) | Retry succeeds; normal cited answer | Pass |
| Model always times out | 2 attempts, then retrieval-only, no cost | Pass |
| Index unreachable (`FaultyRetriever`) | Escalate; model never called; no PII echoed | Pass |
| Empty document export | Refresh blocked; previous version serves | Pass |
| Model proposes 4 tool calls and an unknown tool | Budget stops at 2; unknown tool refused | Pass |

## Load model
`run_load` replays the golden set 5 times (60 requests). p50 1,473 ms, p95 1,475 ms (simulated), max 1,475 ms;
identical on every run (`test_load_model_reports_latency_and_cost_per_success`). Raising time to first token to
5 s pushes p95 past the 4 s gate, so the gate can fail. SLO alerting, the canary and the staged rollout are tested
on synthetic event streams: `test_burn_rate_alerts`, `test_canary_rolls_back_on_quality_or_leak`,
`test_staged_rollout_rolls_back_automatically`.

## Known gaps
- The load model simulates latency; it doesn't measure concurrency, queueing or provider rate limits. Run Section
  14.3's performance test plan (Capstone 4, ex62) against the deployed service before go-live.
- 12 golden cases and 5 probes prove the gates work, not production quality. Grow both from pilot traffic.
- Redaction is regex-based; names pass through. Measure NER redaction recall before production (Table E.6).
- ACLs come from a JSON file; production copies them from the policy archive and the identity provider at ingestion.
