# Versions and dated facts (as of 2026-10)

AI platforms change monthly. This page lists every version-sensitive fact the exercises depend on, so you know what
to re-check when something stops matching the real world. If you find one that's out of date, please open an
[errata issue](.github/ISSUE_TEMPLATE/errata.yml).

## Runtimes
| Item | Version used | Where |
|---|---|---|
| Python | 3.11, 3.12, 3.13 (CI matrix) | all Python exercises |
| Node.js | 22.18+ (native TypeScript type stripping, on by default from 22.18 and 23.6); use a supported LTS line: 24 recommended, and CI uses 24. Node 23 is end-of-life | ex27–ex29, ex91, capstone 1 web view |
| pytest / PyYAML | see `requirements.txt` | test runner, YAML exercises |

## Protocols and specifications
| Item | Version | Where | Notes |
|---|---|---|---|
| Model Context Protocol | **2026-07-28** (modern), plus legacy 2025-11-25 and earlier via `initialize` | ex44, ex45, capstone 2 | 2026-07-28 removed the handshake: per-request `_meta` protocol version, mandatory `server/discover`, `-32022` UnsupportedProtocolVersionError |
| JSON Schema | 2020-12 (MCP default dialect); exercises validate a subset | ex32, ex43, ex44 | |
| JSON-RPC | 2.0 | ex44, ex45, capstone 2 | |
| OAuth 2.0 client credentials | RFC 6749 §4.4 | ex18 | |
| OAuth 2.0 Token Exchange | RFC 8693 | ex89 | on-behalf-of flows |
| OpenID Connect ID tokens | OIDC Core 1.0 (HS256 in the exercise; IdPs use RS256 with JWKS) | ex89 | |
| Server-Sent Events | WHATWG HTML living standard | ex28 | |
| Agent Skills format | `SKILL.md` with `name`/`description` frontmatter | ex85 | |
| Claude Code subagents | `.claude/agents/<name>.md` with `name`, `description`, `tools`, `model` | ex85 | |

## Model identifiers
Exercises run offline against `fde_kit.FakeLLM`; these ids appear as **labels and test data**, plus the default for
the optional live adapter (`FDE_LIVE=1`).

| Id | Used in |
|---|---|
| `claude-opus-5-5` | `fde_kit/llm.py` default for `AnthropicLLM`; ex34 routing table; capstone configs |
| `claude-sonnet-5-5` | ex11, ex34, ex35, ex60, ex85, capstones 1–4 |
| `claude-haiku-5-5` | ex34, ex35, ex60, capstones |
| `server-side-fallback-2026-07-01` beta | `fde_kit/llm.py` (live adapter only) |

## Prices
Every price in this repository is **exercise data**, chosen to make the arithmetic interesting: ex03, ex34, ex35,
ex60, capstone 4. Don't quote them to a customer; check the provider's current price list.

## Third-party request/response formats
| Format | Where | Re-check when |
|---|---|---|
| Anthropic Messages API (tool_use / tool_result blocks, streaming events) | fde_kit, ex28, ex42, ex86 | the API adds new block types |
| OpenAI Chat Completions function calling | ex86 | |
| Google Gemini `generateContent` function calling | ex86 | |
| AWS ECS task definitions, GCP Cloud Run (Knative) services, Azure Container Apps | ex76 | |
| Bedrock / Vertex AI / Azure AI Foundry endpoint hostnames | ex76 | |
| GitHub Actions workflow syntax | ex59, `.github/workflows/ci.yml` | |
| Kubernetes `apps/v1`, `autoscaling/v2` | ex58, capstone 4 | |
