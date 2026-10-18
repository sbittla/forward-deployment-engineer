# ex49 · Golden-set eval harness

**Module:** m09 Evaluation · **Covers:** R13 Evaluation & quality measurement · **Time:** 60 min

## Learning objectives
- Build a golden-set eval harness with pluggable graders.
- Report pass rates by tag and surface failures for review.
- Fail fast on misconfigured evals before spending tokens.

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
Implement exercises/m09-evaluation/ex49-eval-harness/starter.py so that test_eval_harness.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Case`,
`CaseResult`, `EvalReport`, `load_cases`, `run_eval`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/m09-evaluation/ex49-eval-harness` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Golden-set eval harness" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Does an unknown grader fail before any case runs? Is the numeric grader robust to commas and
negative numbers? Which cases would you add so the eval cannot be gamed by verbose answers? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
