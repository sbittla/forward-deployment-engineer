# Reader validation

The book's claim that a reader can finish the exercises **without the author's help** is only true once target
readers have shown it. This folder is the protocol for that test. Until it has been run and its findings fixed, the
release notes list reader validation as *not yet done*.

## Who

Three to five people who match the book's audience and have **not** worked on the book:

- at least one software engineer with no customer-facing experience;
- at least one engineer who has built an LLM application but not deployed one for a customer;
- at least one person from a consulting, solutions or support-engineering role.

## What each reader does (about 6 hours, spread over a week)

| Session | Read | Then complete | Done when |
|---|---|---|---|
| 1. Setup | Introduction; Appendix A | Clone the repository at the release tag, create a virtual environment, run `python scripts/check.py --solutions` | All green, or the reader records where setup stopped |
| 2. Foundations | Section 4.2 | ex10 (retries, backoff, idempotency) | `python scripts/check.py exercises/ch04-production-grade-python/ex10-retry-backoff` passes |
| 3. Retrieval | Sections 10.1–10.3 | ex37 (chunking) and ex39 (hybrid search) | Both suites pass |
| 4. Agents and security | Sections 11.2, 11.6 and 13.2 | ex42 (agent loop) and ex54 (prompt-injection defenses) | Both suites pass |
| 5. Signature capstone, first stage | Appendix D; `capstones/c1-support-copilot/README.md` | C1 milestone 1 (ingestion and retrieval) | `test_c1_ingest_retrieval.py` passes |

**Rules for the observer:** no coaching. Answer only "read the README" or "read the hints file". If the reader is
stuck for 20 minutes, record it as a blocker, give the smallest hint that unblocks them, and write down exactly what
you said.

## What to record

Use the [reader feedback issue form](../.github/ISSUE_TEMPLATE/reader-validation.yml) once per session. The measures:

| Measure | How it's taken |
|---|---|
| Setup success | Session 1 reached "done when" without help (yes/no), and the step where it stopped if not |
| Time to first passing test | Minutes from opening the exercise README to the first test that passes against the reader's own code |
| Time to "done when" | Minutes for the whole session |
| Hint use | Which of the three hints in `HINTS.md` the reader opened, and whether the test-to-cause table was used |
| Observer interventions | Count, and the exact words of each hint the observer gave |
| Unclear instructions | Each place the reader re-read or misread: file and line, what they expected, what happened |
| Failed commands | The command, its output, and the reader's OS, Python and Node versions |
| Caveat comprehension | After each session, ask: "What does this exercise *not* protect against in production?" Score 1 if the answer names a point from the exercise's Production caveats or the book's Production readiness panel, else 0 |
| Change request | One sentence on what the reader would change |

## Readers and backgrounds

Record each reader's starting background (one of the three above, plus years of experience and whether they have
used Python, TypeScript and Docker before) without names. Report results per background as well as overall: an
exercise that only one background can finish is a finding.

## Pass bar and what happens next

- **Pass:** at least 80% of sessions reach "done when" without help, every reader completes setup, caveat
  comprehension is at least 80%, and no session is blocked by a defect in the book or the repository.
- Every recorded friction point gets a fix or a written reason not to fix it, linked from the issue.
- The release notes and Appendix G then record the date, the number of readers and their backgrounds, the pass rate,
  the median time to first passing test, hint use, and caveat comprehension.
