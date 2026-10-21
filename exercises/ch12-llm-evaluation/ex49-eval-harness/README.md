# ex49 · Golden-set eval harness

**Chapter:** 12 · LLM Evaluation (`exercises/ch12-llm-evaluation/`) · **Covers:** R13 Evaluation & quality measurement

## Learning objectives
- Build a golden-set eval harness with pluggable graders.
- Report pass rates by tag and surface failures for review.
- Fail fast on misconfigured evals before spending tokens.
- Turn a run into a decision: per-slice Wilson intervals, a failure taxonomy, cost per successful answer and a
  leakage check.

## Scenario
"It looks good in the demo" is not a launch criterion. The customer's AI governance board wants a pass rate on a
fixed golden set, broken down by category, re-run on every change. You'll build the harness.

## Your task
- `load_cases(path)` — JSONL, one case per line: `{"id", "input", "expected", "grader", "tags": [...]}` (`tags`
  optional). Blank lines ignored.
- Graders (`GRADERS[name](output: str, expected) -> bool`):
  | name | passes when |
  |---|---|
  | `exact` | output equals expected after lower-casing and collapsing whitespace |
  | `contains` | `expected` is a list; every item appears in output (case-insensitive) |
  | `regex` | `re.search(expected, output)` |
  | `numeric` | `expected = {"value": x, "tol": t}`; the **first** number in output (commas allowed) is within `t` |
  | `json_field` | `expected = {"path": "a.b", "value": v}`; output parses as JSON and the dotted path equals `v` |
- `run_eval(cases, system) -> EvalReport` — `system(input) -> str`. An exception counts as a failure with
  `error="<Type>: <msg>"` and `output=""`. Unknown grader → `ValueError` before running anything.
- `EvalReport.pass_rate` (4 dp), `EvalReport.by_tag()` → `{tag: pass_rate}` (4 dp, sorted keys),
  `EvalReport.failures()` → failing `CaseResult`s, `to_markdown()` → first line `# Eval: P/N passed (xx.x%)`, then a
  `| Tag | Pass rate |` table, then a `## Failures` list with `- <id>: <error or output[:80]>`.

### Evaluation as a decision
- `wilson_interval(successes, n, z=1.96) -> (low, high)` — the Wilson score interval for a pass rate, as floats
  (unrounded) clamped to `[0, 1]`. With `p = successes / n`: centre `(p + z²/2n) / (1 + z²/n)`, half-width
  `z·√(p(1−p)/n + z²/4n²) / (1 + z²/n)`. Raise `ValueError` unless `n > 0` and `0 <= successes <= n`.
- `EvalReport.by_slice(z=1.96)` → `{tag: {"n", "passed", "pass_rate", "low", "high"}}` over the same tag groups as
  `by_tag`, sorted keys; `pass_rate`, `low` and `high` rounded to 4 dp. A slice of 40 can't tell 85% from 95%; the
  interval says so.
- `EvalReport.failure_taxonomy(labels)` — `labels` maps case id → cause. Count the **failing** cases by cause (a
  failure with no label counts as `"unlabelled"`; labels on passing cases are ignored) and return
  `[(cause, count)]` sorted by count descending, then cause.
- `cost_per_success(cost_per_request, pass_rate)` — `cost_per_request / pass_rate` (unrounded); `ValueError` if
  `pass_rate <= 0`. A cheap wrong answer has to be paid for again by a person.
- `find_leakage(cases, examples)` — ids (in case order) of cases whose input appears in any few-shot or training
  example after normalising both: lower-case, replace every run of characters other than `a-z` and `0-9` with one
  space, collapse and strip spaces. The normalised input must appear as whole words (`"extract"` doesn't leak into
  `"extraction rules"`). An input that normalises to `""` never leaks.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch12-llm-evaluation/ex49-eval-harness`.
- **Expected output:** all 22 tests fail against the starter; when you're done, all 22 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch12-llm-evaluation/ex49-eval-harness`: all 22
  pass.
- **Tests:** `test_eval_harness.py` (22 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The harness runs cases sequentially against an in-process function and graders that match
  strings and numbers. A production harness pins and records the golden set's version, runs cases in parallel with
  timeouts and retries, stores every output for audit, and pairs string graders with a calibrated judge where a
  phrase match can pass a wrong answer.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Golden-set eval harness". Before I
write code, teach me golden sets, deterministic graders (exact, contains, regex, numeric tolerance, JSON field), and
eval reporting for a governance board. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch12-llm-evaluation/ex49-eval-harness/starter.py so that test_eval_harness.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Case`,
`CaseResult`, `EvalReport`, `load_cases`, `run_eval`, `wilson_interval`, `cost_per_success`, `find_leakage`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/ch12-llm-evaluation/ex49-eval-harness` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Golden-set eval harness" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Does an unknown grader fail before any case runs? Is the numeric grader robust to commas and
negative numbers? Which cases would you add so the eval cannot be gamed by verbose answers? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
