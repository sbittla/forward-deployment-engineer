# Changelog

This project follows [semantic versioning](https://semver.org/) for its exercise interfaces. From 1.0.0, a breaking
change to a README spec or test contract bumps the major version, new exercises or templates bump the minor version,
and errata fixes are patch releases. Exercise ids never change within an edition of the book; directory names change
only in a major release.

## [1.1.1] - 2026-10-21
Errata release, verified against *The Forward Deployed Engineer*, First Edition, version 1.1.1. Fixes every defect a
chapter-by-chapter technical review found, and adds the reviewer's recommendations on token validation, research
reproducibility and release currency. 1,002 tests (973 Python, 29 TypeScript) in 106 suites, up from 955. No exercise ids or folders changed.

### Fixed (security)
- **ex54 ToolGate egress bypass.** Destinations were matched only as lower-case `http(s)://` URLs, so
  `HTTPS://attacker.net`, `//attacker.net` and a bare `attacker.net/collect` passed. The gate now finds URLs in any
  case and scheme, scheme-relative URLs, e-mail addresses, IP literals and bare host names, and denies by default
  (`test_boundary_egress_bypasses_blocked`); the remaining limit, obfuscated hosts, is pinned and documented.
- **C3 SQL guard.** Quoted, bracketed and backticked identifiers (`"salaries"`, `[salaries]`, `"sqlite_master"`)
  bypassed the allow-list; the guard now refuses them (eight new cases in `test_blocks`).
- **ex17 webhooks.** A non-ASCII signature header raised an unhandled exception (a 500 for an unauthenticated
  sender); the comparison now runs on bytes, and the raw body bytes are signed.
- **ex35 response cache.** The key now includes the tenant and entitlements explicitly.
- **ex89 tokens.** ID-token checks add `nonce` and `azp`; ID tokens are rejected where an access token is required,
  and a new `verify_access_token` requires `typ: at+jwt` and the scope.

### Fixed (behavior; existing tests updated)
- **ex21** prefers lower-case proxy variables, as `requests` and curl do.
- **ex28** follows the SSE standard: a bare CR ends a line, and an unterminated event is discarded at end of stream.
- **ex30** numbers its events and resumes a stream after `Last-Event-ID` from a per-request replay buffer.
- **ex37** chunk keys include the chunk's ordinal; `plan_reindex` returns updates for moved chunks.
- **ex77** checks a batch's completeness against the trailing median, not an absolute row floor.
- **C6** `render_steering` follows the book's six-item steering order, with changes since last week, risks and asks
  with owners and dates, and the next milestone.
- **ex13** tests are named in the customer's words.

### Added
- Tests behind book figures: ex03 `full_case` (Table 2.3 and the stop/go line) and the measured-saving re-run; ex41
  query rewriting for follow-ups and `rag_scorecard`; ex61's worked alert times; ex10's per-attempt timeout; ex16's
  HTTP-date `Retry-After`; ex90's check for negated downsides and ex92's log of refused actions.
- `research/`: the job-posting analysis behind Chapters 1 and 17, with a per-posting index (no posting text), the
  classification rules and a script that recomputes every published figure; its tests run in `check.py
  --solutions`. Tightened rules changed the sample to 157 roles at 44 companies and corrected several percentages.
- `scripts/currency_check.py`, run by `verify_release.py`: every section of `VERSIONS.md` carries a "Last checked"
  date, and a release fails if one is older than 120 days or the code uses an unlisted model id.
- Reader validation now records setup success, time to first passing test, hint use, unclear instructions and
  caveat comprehension, per reader background.

### Changed
- Exercise and capstone documentation uses American English, like the book. Directory names keep their original
  spelling (`ch15-field-engineering-and-productisation`): they're fixed identifiers.
- `interview/questions-and-answers.md` is generated from the book, so it matches Appendix J.

## [1.1.0] - 2026-10-21
Verified against *The Forward Deployed Engineer*, First Edition, version 1.1. Closes an external review's
recommendations: reproducibility, production safety, one signature capstone, measurable claims and usability.
955 tests (927 Python, 28 TypeScript) in 106 suites, up from 805. No exercise ids or folders changed.

**Upgrading from 1.0.0.** About 45 exercises and Capstone 1 gained tests and required functions, so a solution that
passed 1.0.0 may fail some new tests. Each new requirement is in the exercise README's spec and has a HINTS row. Two
behavior changes alter what existing callers see: ex24's `pseudonymise` rejects keys under 16 bytes, and ex32's
`complete_structured` raises on a `refusal` or `max_tokens` stop reason instead of spending repairs.

### Added
- **Signature capstone.** Capstone 1 (Northwind's support copilot) now runs discovery to go/no-go: incremental,
  permission-aware ingestion and retrieval (`tenancy`), a constrained claim-review tool with authorization, approval,
  idempotency and an execution budget (`tools`), failure injection (`faults`), a load model reporting p50/p95 and cost
  per successful answer (`loadmodel`), SLOs, burn-rate alerts and a canary with automatic rollback (`slo`), and a
  go/no-go decision from nine objective gates against the baseline (`golive`). A deliberately failing v0 build
  (`build_copilot(..., naive=True)`) fails its gates; the README documents the remediation. Six new deliverable
  templates (charter, architecture, threat model, evaluation report, test report, final readout) with completed
  Northwind examples in `solutions/`. 42 tests, up from 17.
- **Fault injection** (ex10–ex12, ex14, ex15): partial failures, retry storms, deadlines, cancellation, lost
  responses and crashed workers, with bounded retries and no duplicate side effects (`test_fault_*`).
- **Security negative tests** across chapters: expired, misdirected, tampered and algorithm-confused tokens and key
  rotation by `kid` (ex89); invalid credentials, replayed and rewritten webhooks, secret rotation and fail-closed
  token refresh (ex16–ex18, ex20); cross-tenant isolation that fails closed at retrieval (ex39, ex41, C1);
  least-privilege tools, approval that fails closed and an audit entry per call (ex43, ex46); prompt injection through
  templates, retrieved text and replies (ex31, ex40, ex70, ex96); privileged containers, long-lived CI keys and
  replayed old bundles (ex58, ex59, ex64).
- **Measurable evidence:** an evaluation dossier (provenance, labeler agreement, exact McNemar) in ex49–ex50; a
  reproducible prompt experiment with prompt and dataset hashes, repeated runs, Wilson intervals and a regression gate
  (ex97); provider-failure rehearsal with cost per successful task and p50/p95 (ex34); a fixed retrieval benchmark
  with citation precision, stale and foreign chunks and abstention (ex41); load reports that state the load model
  (ex62); a 100,000-row backfill (ex23).
- **Operations and delivery:** canary rollback on error-budget burn and exact page thresholds (ex61), postmortem
  required fields (ex94), PoC exit gates with a Wilson lower bound (ex70), fail-closed model-risk documents (ex75),
  risk-acceptance records (ex90, ex93), measurable SOW acceptance criteria (ex81), and a streaming client with auth,
  cancellation and resumable reconnects plus accessible failure states (ex28–ex30, ex91).
- `TRACEABILITY.md` (`scripts/traceability.py`): every exercise and capstone with its chapter, path, command and
  expected result; regenerated by `run_all.py` and checked by `check.py --solutions`.
- `SECURITY-MATRIX.md` (`scripts/security_matrix.py`): assets, trust boundaries, identities, failure modes and the
  negative tests for 66 exercises and capstones; a renamed or missing test fails the check.
- `scripts/verify_release.py --offline`: builds a wheelhouse and installs it in a container with no network; every
  report is also written as JSON.
- `reader-validation/` and a reader-validation issue form: the protocol for testing the exercises with three to five
  target readers.

### Changed
- `playbook/design/adr.md` uses "Alternatives considered", which ex90's linter requires;
  `playbook/design/threat-model.md` adds tool poisoning, token passthrough, forged tokens and residual-risk acceptance;
  `playbook/design/evaluation-plan.md` adds provenance.
- ex34 fails over on 500, 502, 504 and timeouts as well as 429, 503 and 529, and enforces a hard budget before each
  call. ex30's `make_app` takes an optional `api_token`.

## [1.0.0] - 2026-10-21
The first public release, verified against *The Forward Deployed Engineer*, First Edition, version 1.0, from an
anonymous clean checkout of this tag (the verification report is attached to the GitHub release). Earlier version
numbers were internal pre-releases; their tags (v1.4.0, v2.0.0) were withdrawn and the history below is kept for
reference. 805 tests (787 Python, 18 TypeScript) in 106 suites.

### Added
- **Run and verify, in every README.** Each exercise and capstone README ends with the same reproducibility
  contract: prerequisites, the command, expected output against the starter and when done, how to check the
  reference solution, the tests, common failures, how to tell whether a failure is your environment, your code or a
  defect in the published solution, cleanup, and production caveats. `scripts/contract_lint.py` enforces it and runs
  in `check.py --solutions`, `run_all.py` and CI; `--write` regenerates the counts from the latest `output/` report.
- **Boundary tests** that pin what a teaching implementation does *not* protect against, each cited by a
  production-readiness panel in the book: ex10 (`Retry-After` not capped by a deadline), ex12 (cancellation
  propagates), ex17 (replay outside the window; dedupe is per process), ex18 (a persistent 401 costs two token calls),
  ex23 (late-arriving rows; replay after a watermark reset), ex29 (connection lost mid-stream), ex32 (schema-valid
  isn't correct; a refusal spends the repairs), ex40 (a valid citation isn't checked for support), ex44 (arguments
  aren't validated against `inputSchema`), ex46 (approval follows the plan's flag), ex50 (a consistent judge bias
  passes order-swapping), ex53 (names aren't redacted), ex54 (a paraphrased injection evades the signals but the gate
  blocks it), ex55 (a poisoned source counts as grounded), ex56 (a rebuilt audit chain still verifies), ex64 (a shared
  HMAC key can re-sign a bundle), ex72 (other people's names aren't scrubbed), ex95 (`render` inserts values
  verbatim). Where a boundary wasn't yet in the spec, the README states it (ex12, ex23, ex44, ex53, ex56, ex72, ex95).
- `scripts/verify_release.py`: clones the public repository anonymously, installs from scratch and runs every
  documented check, optionally in Docker, writing a report with the commit, OS and tool versions.
- `interview/questions-and-answers.md`: the book's 127 end-of-chapter interview questions with model answers,
  strong signals and red flags (Appendix J).

### Fixed (test contracts changed)
- **Capstone 3 SQL guard:** a table listed after a comma (`FROM accounts, salaries`) bypassed the allow-list, which
  only checked names after `FROM` and `JOIN`. Now every item of a `FROM` list is checked; two cases added to
  `test_blocks`.
- **ex44:** `structuredContent` was sent for list results, but MCP requires a JSON object there. Lists are now
  returned as JSON text only; new `test_list_result_has_no_structured_content`.
- **ex45:** `%` and `_` in a search query acted as `LIKE` wildcards, so `%` matched every ticket. They're now
  escaped; new `test_search_wildcards_are_literal`.

### Changed
- One folder per book chapter for exercises, solutions and outputs (`exercises/ch02-discovery-and-scoping/` to
  `exercises/ch16-delivery-leadership/`, mirrored under `solutions/exercises/` and `output/exercises/`); `meta.json`
  has `"chapter"` instead of `"module"`. Exercise ids are unchanged.
- Playbook templates, the capstone rubric and hints cite the book's version 1.0 section numbers.

### Verified
- See the verification report attached to the v1.0.0 GitHub release: anonymous clone of the tag; `check.py
  --solutions` (every solution plus the spec, hints and contract linters); `starters_red.py`; and `run_all.py
  --docker` (106 of 106 suites as expected, every declared test ran, every starter fails at least one test).

## Pre-release history

Internal releases made before the first public release. The v1.4.0 and v2.0.0 tags were withdrawn on 2026-10-21;
their content is part of 1.0.0.

### 2.0.0 (pre-release, tag withdrawn) - 2026-10-20
The release verified against *The Forward Deployed Engineer*, First Edition, revision 2.0. The repository is now
organised the way the book is, so a chapter number is enough to find its exercises, solutions and test reports.

#### Changed (breaking): one folder per book chapter
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

#### Changed: book cross-references
- Playbook templates, `capstones/RUBRIC.md` and Capstone 4's hints cite the book's revision 2.0 section numbers (the
  book now has 6 or 7 numbered sections per chapter).

#### Verified
- In Docker (Ubuntu 24.04, Python 3.12, Node.js 24, `--gpus all`): 106 of 106 suites as expected, 780 tests passed
  (763 Python, 17 TypeScript), every declared test ran, every starter fails at least one test; spec and hints linters
  report 0 problems, and `starters_red.py` reports 0 problems.

### 1.4.0 (pre-release, tag withdrawn) - 2026-10-20
The release verified against *The Forward Deployed Engineer*, First Edition, revision 1.3. The book and the
repository were checked against each other chapter by chapter, and new exercise parts now practise what the chapters
teach. Exercise ids and directories are unchanged; existing functions keep their signatures, and new parts add
functions or optional arguments. Three test contracts changed (ex05, Capstone 4 and Capstone 6, below). 780 tests
(763 Python, 17 TypeScript), up from 734.

#### Added: new exercise parts
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

#### Changed
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

### 1.0.0-rc (pre-release, untagged) - 2026-10-18
The release verified against *The Forward Deployed Engineer*, First Edition, revision 1.2. Exercise ids,
directories and test contracts are unchanged from 0.9.0.

#### Added
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

#### Changed
- Node.js requirement is now 22.18 or later (type stripping is on by default from 22.18), with Node 24 LTS
  recommended; Node 23 is end-of-life. `package.json`, the README, `VERSIONS.md`, `check.py` and the TypeScript
  exercise READMEs agree. The TypeScript solutions were verified on Node 22.18.0 and 23.11.1; CI uses 24.

#### Fixed
- ex91 README now specifies the message-id counter the reference solution uses (one per `makeUseChat` call).
- Capstone 6 starter documents the forecast method and the RAG thresholds that `test_rag` checks.

### [0.9.0] - 2026-10-18
First public pre-release, for technical reviewers and beta readers.

#### Added
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

#### Changed
- MCP material (ex44, ex45, capstone 2) now targets spec **2026-07-28**: per-request `_meta` protocol version,
  mandatory `server/discover`, `-32022` UnsupportedProtocolVersionError, `resultType`/`ttlMs`. Servers stay
  dual-era for legacy `initialize` clients; the client probes and falls back.
- README index ordered by the book's parts, with prerequisite notes on capstones 1 and 3.

#### Fixed
- `gather_limited(concurrency=0)` deadlocked instead of raising (ex12), along with 17 other missing error paths, now
  specified and tested (ex36, ex52, ex62, ex66, ex71, ex78, ex82, ex93 and others).
- Undocumented test dependencies in ex53 (`luhn_ok`) and ex91 (`initialState`).

[1.1.1]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v1.1.1
[1.1.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v1.1.0
[1.0.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v1.0.0
[0.9.0]: https://github.com/sbittla/forward-deployment-engineer/releases/tag/v0.9.0
