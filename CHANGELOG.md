# Changelog

This project follows [semantic versioning](https://semver.org/) for its exercise interfaces: a breaking change to
a README spec or test contract bumps the minor version while the course is pre-1.0. Errata fixes are patch releases.

## [0.9.0] - 2026-10-18
First public pre-release, for technical reviewers and beta readers.

### Added
- 100 exercises across 15 modules and 6 capstone engagements, each with a README spec, a starter, tests and a
  reference solution, all running offline against a deterministic fake model.
- Module 15, prompt engineering: prompt linter (ex95), dynamic few-shot selection (ex96), prompt hill-climbing with a
  held-out test set and McNemar test (ex97), and a system prompt compiled from a policy spec with traceability (ex98).
- Evaluation: agent trajectory evals with pass@k and pass^k (ex99); online monitoring and drift detection (ex100).
- Learning objectives and a prompt kit in every exercise README (tutor, coding-agent build spec, review, and
  production prompts for LLM-facing exercises).
- `scripts/spec_lint.py` (tests may only use names the README documents) and `scripts/export_learner.py` (a
  workspace without solutions).
- `LICENSE` (MIT, code), `LICENSE-CONTENT` (CC BY-NC 4.0, written content), `NOTICE.md`, `VERSIONS.md`, and issue
  templates for errata.

### Changed
- MCP material (ex44, ex45, capstone 2) now targets spec **2026-07-28**: per-request `_meta` protocol version,
  mandatory `server/discover`, `-32022` UnsupportedProtocolVersionError, `resultType`/`ttlMs`. Servers stay
  dual-era for legacy `initialize` clients; the client probes and falls back.
- README index ordered by the book's parts, with prerequisite notes on capstones 1 and 3.

### Fixed
- `gather_limited(concurrency=0)` deadlocked instead of raising (ex12), along with 17 other missing error paths, now
  specified and tested (ex36, ex52, ex62, ex66, ex71, ex78, ex82, ex93 and others).
- Undocumented test dependencies in ex53 (`luhn_ok`) and ex91 (`initialState`).

[0.9.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v0.9.0
