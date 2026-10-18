# Forward Deployed Engineer: exercises & capstones

80 hands-on exercises and 5 capstone engagements for engineers preparing for Forward Deployed
Engineer (FDE) roles: building, integrating and running AI systems inside customers' environments, and owning the
customer outcome. Every exercise ships with a starter, tests and a reference solution, and runs **offline**: a
deterministic fake model stands in for the LLM, so no API key is needed.

## Quick start
```bash
pip install -r requirements.txt
python scripts/check.py --solutions          # all reference solutions: green
pytest exercises/m01-engagement-discovery/ex01-engagement-charter   # one exercise: starts red, make it green
```
Requirements: Python 3.11+, Node 23.6+ (for the TypeScript exercises; native type stripping, no npm install).

## How it works
- `exercises/<module>/<exercise>/`: `README.md` (scenario + task), `starter.*`, tests, `meta.json`.
- `solutions/` mirrors the tree with reference implementations. Peek only after you've tried.
- `pytest --solutions <path>` runs the same tests against the reference solution.
- `capstones/<cN>/`: multi-day engagements with `starter/` packages, deliverable templates, shared `data/` and tests.
- `fde_kit/`: the offline `FakeLLM`, an optional `AnthropicLLM` adapter (`FDE_LIVE=1`), and text utilities.

## Exercises

### M01 · Engagement & discovery
| # | Exercise |
|---|---|
| ex01 | [Engagement charter from discovery notes](exercises/m01-engagement-discovery/ex01-engagement-charter/README.md) |
| ex02 | [Discovery interview to user stories](exercises/m01-engagement-discovery/ex02-requirements-extractor/README.md) |
| ex03 | [ROI and payback model for an AI deployment](exercises/m01-engagement-discovery/ex03-roi-calculator/README.md) |
| ex04 | [Stakeholder map, RACI and comms plan](exercises/m01-engagement-discovery/ex04-stakeholder-map/README.md) |
| ex05 | [Weekly status report generator](exercises/m01-engagement-discovery/ex05-status-report/README.md) |
| ex06 | [Ambiguous request to clarifying questions and assumptions](exercises/m01-engagement-discovery/ex06-ambiguous-request/README.md) |
| ex07 | [RAID log: risks, assumptions, issues, decisions](exercises/m01-engagement-discovery/ex07-raid-log/README.md) |
| ex08 | [Scope negotiation with MoSCoW under a deadline](exercises/m01-engagement-discovery/ex08-scope-prioritization/README.md) |

### M02 · Production Python
| # | Exercise |
|---|---|
| ex09 | [Typed config and secrets loading](exercises/m02-production-python/ex09-typed-config/README.md) |
| ex10 | [Retries, backoff, jitter, idempotency](exercises/m02-production-python/ex10-retry-backoff/README.md) |
| ex11 | [Structured logging with correlation IDs](exercises/m02-production-python/ex11-structured-logging/README.md) |
| ex12 | [Async fan-out with rate limiting](exercises/m02-production-python/ex12-async-rate-limit/README.md) |
| ex13 | [Triage and fix a broken customer script](exercises/m02-production-python/ex13-debug-customer-script/README.md) |
| ex14 | [Circuit breaker and bulkhead](exercises/m02-production-python/ex14-circuit-breaker/README.md) |
| ex15 | [Idempotent job queue with dead-letter handling](exercises/m02-production-python/ex15-job-queue/README.md) |

### M03 · APIs & integration
| # | Exercise |
|---|---|
| ex16 | [Paginated REST client with rate-limit headers](exercises/m03-apis-integration/ex16-paginated-client/README.md) |
| ex17 | [Webhook receiver with HMAC and replay protection](exercises/m03-apis-integration/ex17-webhook-hmac/README.md) |
| ex18 | [OAuth2 client-credentials token cache](exercises/m03-apis-integration/ex18-oauth-token-cache/README.md) |
| ex19 | [CRM to canonical schema mapper](exercises/m03-apis-integration/ex19-schema-mapper/README.md) |
| ex20 | [Minimal HTTP service with auth and health](exercises/m03-apis-integration/ex20-http-service/README.md) |
| ex21 | [Proxy-, CA- and allowlist-aware client for customer networks](exercises/m03-apis-integration/ex21-proxy-aware-client/README.md) |

### M04 · Data & SQL
| # | Exercise |
|---|---|
| ex22 | [SQL analytics on a support-ticket DB](exercises/m04-data-sql/ex22-sql-analytics/README.md) |
| ex23 | [Incremental ETL with watermarks and upserts](exercises/m04-data-sql/ex23-incremental-etl/README.md) |
| ex24 | [Data-quality checks framework](exercises/m04-data-sql/ex24-data-quality/README.md) |
| ex25 | [Schema drift detection](exercises/m04-data-sql/ex25-schema-drift/README.md) |
| ex26 | [Bronze/silver/gold mini lakehouse](exercises/m04-data-sql/ex26-medallion-pipeline/README.md) |

### M05 · Full-stack & TypeScript
| # | Exercise |
|---|---|
| ex27 | [TypeScript: runtime-validated API client](exercises/m05-fullstack-typescript/ex27-ts-typed-client/README.md) |
| ex28 | [TypeScript: SSE token-stream parser](exercises/m05-fullstack-typescript/ex28-ts-sse-parser/README.md) |
| ex29 | [TypeScript: chat UI state reducer](exercises/m05-fullstack-typescript/ex29-ts-chat-reducer/README.md) |
| ex30 | [Demo chat UI served from Python](exercises/m05-fullstack-typescript/ex30-demo-web-ui/README.md) |

### M06 · LLM applications
| # | Exercise |
|---|---|
| ex31 | [Versioned prompt templates](exercises/m06-llm-apps/ex31-prompt-templates/README.md) |
| ex32 | [Structured output with validation and repair](exercises/m06-llm-apps/ex32-structured-output/README.md) |
| ex33 | [Token budgeting and context packing](exercises/m06-llm-apps/ex33-context-packing/README.md) |
| ex34 | [Cost/latency-aware model router with fallback](exercises/m06-llm-apps/ex34-model-router/README.md) |
| ex35 | [Response cache and cost accounting](exercises/m06-llm-apps/ex35-llm-cache-costs/README.md) |
| ex36 | [Classical ML baseline vs LLM classifier](exercises/m06-llm-apps/ex36-ml-baseline/README.md) |

### M07 · Retrieval & RAG
| # | Exercise |
|---|---|
| ex37 | [Chunking strategies](exercises/m07-retrieval-rag/ex37-chunking/README.md) |
| ex38 | [BM25 from scratch](exercises/m07-retrieval-rag/ex38-bm25/README.md) |
| ex39 | [Vector + keyword hybrid search with RRF](exercises/m07-retrieval-rag/ex39-hybrid-search/README.md) |
| ex40 | [RAG answers with citations and abstention](exercises/m07-retrieval-rag/ex40-rag-citations/README.md) |
| ex41 | [Retrieval metrics: recall@k, MRR, nDCG](exercises/m07-retrieval-rag/ex41-retrieval-eval/README.md) |

### M08 · Agents, tools & MCP
| # | Exercise |
|---|---|
| ex42 | [Tool-calling agent loop](exercises/m08-agents-mcp/ex42-tool-agent-loop/README.md) |
| ex43 | [Tool input validation and error recovery](exercises/m08-agents-mcp/ex43-tool-validation/README.md) |
| ex44 | [Build an MCP server](exercises/m08-agents-mcp/ex44-mcp-server/README.md) |
| ex45 | [MCP client and DB connector](exercises/m08-agents-mcp/ex45-mcp-client-connector/README.md) |
| ex46 | [Planner/worker agents with human approval](exercises/m08-agents-mcp/ex46-multi-agent-hitl/README.md) |
| ex47 | [Conversation memory and summarisation](exercises/m08-agents-mcp/ex47-agent-memory/README.md) |
| ex48 | [Voice agent transcripts: turns, barge-in, latency](exercises/m08-agents-mcp/ex48-voice-transcripts/README.md) |

### M09 · Evaluation
| # | Exercise |
|---|---|
| ex49 | [Golden-set eval harness](exercises/m09-evaluation/ex49-eval-harness/README.md) |
| ex50 | [LLM-as-judge with calibration](exercises/m09-evaluation/ex50-llm-judge/README.md) |
| ex51 | [Prompt regression gate for CI](exercises/m09-evaluation/ex51-prompt-regression/README.md) |
| ex52 | [A/B experiment analysis with bootstrap CIs](exercises/m09-evaluation/ex52-ab-analysis/README.md) |

### M10 · Safety, security & compliance
| # | Exercise |
|---|---|
| ex53 | [PII detection and redaction](exercises/m10-safety-security/ex53-pii-redaction/README.md) |
| ex54 | [Prompt-injection defences for agents](exercises/m10-safety-security/ex54-prompt-injection/README.md) |
| ex55 | [Output guardrails and groundedness](exercises/m10-safety-security/ex55-output-guardrails/README.md) |
| ex56 | [RBAC and audit log for multi-tenant AI](exercises/m10-safety-security/ex56-rbac-audit/README.md) |

### M11 · Deploy & operate
| # | Exercise |
|---|---|
| ex57 | [Production Dockerfile and compose](exercises/m11-deploy-operate/ex57-dockerize/README.md) |
| ex58 | [Kubernetes manifests with probes and HPA](exercises/m11-deploy-operate/ex58-k8s-manifests/README.md) |
| ex59 | [CI pipeline as code](exercises/m11-deploy-operate/ex59-ci-pipeline/README.md) |
| ex60 | [Tracing and metrics for LLM calls](exercises/m11-deploy-operate/ex60-llm-tracing/README.md) |
| ex61 | [SLOs and error-budget burn alerts](exercises/m11-deploy-operate/ex61-slo-burn-rate/README.md) |
| ex62 | [Load test and latency profiling](exercises/m11-deploy-operate/ex62-load-test/README.md) |
| ex63 | [Customer-environment preflight checker](exercises/m11-deploy-operate/ex63-env-preflight/README.md) |
| ex64 | [Air-gapped deployment bundle with manifest and checksums](exercises/m11-deploy-operate/ex64-airgap-bundle/README.md) |
| ex65 | [IaC config with least-privilege IAM validator](exercises/m11-deploy-operate/ex65-iac-least-privilege/README.md) |
| ex66 | [Log forensics: root-cause an incident](exercises/m11-deploy-operate/ex66-log-forensics/README.md) |

### M12 · Field craft
| # | Exercise |
|---|---|
| ex67 | [Productise a one-off field script](exercises/m12-field-craft/ex67-productize-field-code/README.md) |
| ex68 | [Field feedback triage to product brief](exercises/m12-field-craft/ex68-feedback-triage/README.md) |
| ex69 | [Runbook and handoff doc linter](exercises/m12-field-craft/ex69-runbook-linter/README.md) |
| ex70 | [Time-boxed POC: invoice extraction](exercises/m12-field-craft/ex70-rapid-poc/README.md) |
| ex71 | [Fine-tuning dataset preparation](exercises/m12-field-craft/ex71-finetune-dataprep/README.md) |
| ex72 | [Regulated data: de-identification and retention](exercises/m12-field-craft/ex72-phi-deidentify/README.md) |
| ex73 | [Generalise three customer variants into a config-driven connector](exercises/m12-field-craft/ex73-connector-framework/README.md) |
| ex74 | [API reference and quickstart generator](exercises/m12-field-craft/ex74-docs-generator/README.md) |
| ex75 | [Model risk documentation for a regulated customer](exercises/m12-field-craft/ex75-model-risk-doc/README.md) |

### M13 · Enterprise stack
| # | Exercise |
|---|---|
| ex76 | [One service spec rendered for AWS, GCP and Azure with data residency](exercises/m13-enterprise-stack/ex76-multi-cloud-deploy/README.md) |
| ex77 | [Spark fundamentals: partitions, shuffles, skew, and a PySpark/Delta job](exercises/m13-enterprise-stack/ex77-spark-fundamentals/README.md) |
| ex78 | [Port a customer's Java/Go/C++ request signer to Python](exercises/m13-enterprise-stack/ex78-polyglot-port/README.md) |
| ex79 | [LangGraph-style state graph with checkpoints and interrupts](exercises/m13-enterprise-stack/ex79-graph-orchestration/README.md) |
| ex80 | [SQLite to Postgres portability and pgvector](exercises/m13-enterprise-stack/ex80-postgres-pgvector/README.md) |

## Capstones
| # | Engagement |
|---|---|
| C1 | [Enterprise Support Copilot (insurance)](capstones/c1-support-copilot/README.md) |
| C2 | [Agentic Order-Ops with MCP connectors (retail)](capstones/c2-ops-agent-mcp/README.md) |
| C3 | [Lakehouse ETL + NL-to-SQL analyst (financial services)](capstones/c3-insights-analyst/README.md) |
| C4 | [Pilot to production hardening in a constrained customer environment](capstones/c4-pilot-to-production/README.md) |
| C5 | [Embedded field engagement: healthcare intake from call transcripts](capstones/c5-field-engagement/README.md) |

## Using a real model
Exercises accept any client with `complete(messages, system=..., tools=..., **kw)`. `fde_kit.AnthropicLLM` wraps the
official `anthropic` SDK (default model `claude-opus-5-5`, with server-side refusal fallbacks enabled). Install `anthropic`
and set credentials, then pass `AnthropicLLM()` where the tests pass a `FakeLLM`. Outputs will vary, which is
what the evaluation exercises are for.
