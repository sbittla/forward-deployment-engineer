# ex49 · Golden-set eval harness

**Module:** m09 Evaluation · **Covers:** R13 Evaluation & quality measurement · **Time:** 60 min

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
