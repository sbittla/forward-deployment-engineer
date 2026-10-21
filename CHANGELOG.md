# Changelog

This project follows [semantic versioning](https://semver.org/) for its exercise interfaces. From 1.0.0, a breaking
change to a README spec or test contract bumps the major version, new exercises or templates bump the minor version,
and errata fixes are patch releases. Exercise ids never change within an edition of the book; directory names change
only in a major release.

## [Unreleased]
### Added
- `interview/questions-and-answers.md`: the book's 127 end-of-chapter interview questions with their model answers,
  strong signals and red flags (Appendix J), grouped by chapter.

## [2.0.0] - 2026-10-20
The release verified against *The Forward Deployed Engineer*, First Edition, revision 2.0. The repository is now
organised the way the book is, so a chapter number is enough to find its exercises, solutions and test reports.

### Changed (breaking): one folder per book chapter
- Exercises moved from the 15 topic modules (`exercises/m01-...` to `exercises/m15-...`) to one folder per book
  chapter, named after the chapter: `exercises/ch02-discovery-and-scoping/` to `exercises/ch16-delivery-leadership/`
  (for example `exercises/ch10-rag/ex37-chunking/`). Chapters 1 and 17 have no exercises.
- `solutions/exercises/` and `output/exercises/` mirror the same chapter folders.
- Exercise ids (ex01 to ex100), file names, specs and test contracts are unchanged; only the parent folder moved.
  Update any bookmarks or scripts that used a module path. `git log --follow` keeps each file's history.
- `meta.json` replaces `"module"` with `"chapter"` (the chapter folder name), and each exercise README's header names
  its chapter and folder instead of the module. The leftover per-exercise time estimates are removed.
- `scripts/check.py --chapter N` now looks only in that chapter's folder, and a full `scripts/run_all.py` run fails if
  any exercise folder would be skipped.
- README: the exercise index is grouped by chapter folder, and the part names follow the book.

### Changed: book cross-references
- Playbook templates, `capstones/RUBRIC.md` and Capstone 4's hints cite the book's revision 2.0 section numbers (the
  book now has 6 or 7 numbered sections per chapter).

### Verified
- In Docker (Ubuntu 24.04, Python 3.12, Node.js 24, `--gpus all`): 106 of 106 suites as expected, 780 tests passed
  (763 Python, 17 TypeScript), every declared test ran, every starter fails at least one test; spec and hints linters
  report 0 problems, and `starters_red.py` reports 0 problems.

## [1.4.0] - 2026-10-20
The release verified against *The Forward Deployed Engineer*, First Edition, revision 1.3. The book and the
repository were checked against each other chapter by chapter, and new exercise parts now practise what the chapters
teach. Exercise ids and directories are unchanged; existing functions keep their signatures, and new parts add
functions or optional arguments. Three test contracts changed (ex05, Capstone 4 and Capstone 6, below). 780 tests
(763 Python, 17 TypeScript), up from 734.

### Added: new exercise parts
Each part adds a spec section, tests that start red, hints and a reference solution.
- **ex03:** `sensitivity()` also takes a tuple of parameters scaled together, which reproduces Chapter 2's
  token-price column.
- **ex15:** `extend(job_id, worker, lease_s)`, lease extension for long jobs (Chapter 4).
- **ex17:** Part B, `apply_update` and `reconcile`: version-ordered updates that converge whatever order events arrive
  in, and however often (Chapter 5).
- **ex24:** Part B, `pseudonymise(value, key)` (keyed HMAC-SHA256) and `checks_from_contract`, data-quality checks
  built from a data contract (Chapter 6).
- **ex30:** a streaming relay: `sse()`, `relay()` and `POST /api/chat/stream`, with keep-alives and upstream
  cancellation when the client disconnects (Chapter 7).
- **ex35:** `cost_per_request` with prompt-cache read pricing and `monthly_cost`, reproducing Chapter 9's worked cost
  model.
- **ex37:** `chunk_key`, `plan_reindex` (incremental re-indexing) and `filter_effective` (effective-date filtering)
  (Chapter 10).
- **ex42:** `RunBudget` (steps, tokens, dollars, seconds), per-tool caps, repeated-call detection and "outcome
  unknown" for tool timeouts, all as optional arguments to `run_agent` (Chapter 11).
- **ex49:** `wilson_interval`, per-slice reports, a failure taxonomy, `cost_per_success` and `find_leakage`
  (Chapter 12).
- **ex77:** the Part B job must check its input (row count and freshness) before it overwrites the table (Chapter 6).
- **ex93:** `scan_tools` (poisoned MCP tool descriptions), `check_audience` and `upstream_headers` (token audience
  checks and no token passthrough) (Chapter 13).
- **Capstone 4:** a `performance_test_plan.md` deliverable, `canary_decision` in `pilot/slo.py`, and a readiness
  review with gates before the scorecard (Chapter 14).
- **Capstone 6:** the statement of work needs support boundaries and exit criteria, as the rubric says.
- `playbook/handover/integration-register.md`, the first page of the handover pack (Chapter 5); 26 templates.
- `scripts/run_all.py`: runs every exercise and capstone solution one suite at a time and checks the results. A suite
  passes only if every test it declares ran and passed, and its starter fails at least one of them. `--docker` builds
  `docker/runner.Dockerfile` (CUDA base, Python 3.12, Node 24) and runs inside it with `--gpus all`.
- `output/`: the latest run's report, laid out like `exercises/` and `capstones/`: a `result.json` and test log per
  suite, plus `summary.md`, `summary.json` and `environment.txt` at the top.

### Changed
- **ex05:** the status note puts `## Asks` straight after the Overall line, as Chapter 3 and the exercise's own
  field notes say ("lead with the ask"). The old order fails the new test.
- **Capstone 4:** `test_c4_deploy_docs.py` requires a Gates section before a Scorecard section in the readiness
  review, and the new performance test plan.
- **Capstone 6:** the steering update leads with the decisions needed, as Chapter 16 describes;
  `test_steering_update` checks the new section order.
- Prompt kits for ex95 to ex100 end with "If the README and the tests disagree, stop and tell me instead of
  guessing", like the other exercises.
- Time estimates are gone. The README, the capstone READMEs and the book's exercise tables no longer say how long an
  exercise or capstone takes.
- Capstone 1's README lists the intent-accuracy bar (90%) that `evals.py` already enforces. Capstone 5's "Take after"
  includes ex53.
- `export_learner.py` leaves out `run_all.py`, which needs the solutions.

## [1.0.0] - 2026-10-18
The release verified against *The Forward Deployed Engineer*, First Edition, revision 1.2. Exercise ids,
directories and test contracts are unchanged from 0.9.0.

### Added
- `capstones/RUBRIC.md`: one assessment for all six capstones. Gates first (tests, critical correctness, security and
  privacy, honest reporting, plus each capstone's own gates), then nine weighted dimensions, with per-capstone
  acceptance criteria and a strong and a borderline sample submission. Every capstone README links to it.
- `playbook/`: 25 engagement templates in five packs (discovery, solution design, delivery, production readiness,
  handover), each stating its owner, when to use it, its inputs and when it's done. Included in learner exports.
- `scripts/starters_red.py` and a `starters` CI job: every exercise and capstone suite must fail against its starter.
- `python scripts/check.py --chapter N` runs the exercises for one chapter of the book.
- `HINTS.md` for all 100 exercises and 6 capstones: three progressive hints (where to start, the approach, the
  tricky part) and a table mapping each test to its most likely cause of failure. Every README links to it.
- `scripts/hints_lint.py`, run by `check.py --solutions`: every hints file has three levels, names only tests that
  exist, and contains no code block longer than four lines.

### Changed
- Node.js requirement is now 22.18 or later (type stripping is on by default from 22.18), with Node 24 LTS
  recommended; Node 23 is end-of-life. `package.json`, the README, `VERSIONS.md`, `check.py` and the TypeScript
  exercise READMEs agree. The TypeScript solutions were verified on Node 22.18.0 and 23.11.1; CI uses 24.

### Fixed
- ex91 README now specifies the message-id counter the reference solution uses (one per `makeUseChat` call).
- Capstone 6 starter documents the forecast method and the RAG thresholds that `test_rag` checks.

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

[2.0.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v2.0.0
[1.4.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v1.4.0
[0.9.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v0.9.0
