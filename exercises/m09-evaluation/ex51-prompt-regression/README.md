# ex51 · Prompt regression gate for CI

**Module:** m09 · **Covers:** R13 Evaluation, R07 CI/CD · **Time:** 45 min

## Learning objectives
- Compare eval runs case by case instead of by average.
- Block merges on critical regressions or missing cases.
- Wire an eval gate into CI with clear exit codes.

## Scenario
A teammate "improved" the system prompt; overall pass rate went up 1%, but three safety-critical cases now fail.
Averages hide regressions. Build a CI gate that compares eval runs case by case.

## Your task
Eval run files are JSON: `{"run_id": str, "results": {case_id: {"passed": bool, "tags": [...]}}}`.

1. `compare(base, cand, max_drop=0.02, critical_tags=("safety",)) -> Gate`
   - `base_rate`, `cand_rate` over the **intersection** of case ids (4 dp), `delta = cand - base`
   - `regressions`: ids passing in base and failing in candidate (sorted); `fixes`: the reverse (sorted)
   - `missing`: ids in base but not in candidate (sorted) — any missing id fails the gate
   - `critical_regressions`: regressions whose candidate tags intersect `critical_tags`
   - `passed` is False if `delta < -max_drop`, or any critical regression, or anything missing
2. `render(gate) -> str` — markdown with a first line `## Eval gate: PASS` or `## Eval gate: FAIL`, a line
   `Pass rate: 0.9000 -> 0.8800 (-0.0200)`, and sections `### Regressions`, `### Fixes`, `### Missing` listing ids
   (`- none` when empty). Critical regressions are suffixed with ` (critical)`.
3. `main(argv) -> int` — `main(["base.json", "cand.json", "--max-drop", "0.05"])` prints the report and returns
   exit code 0 (pass) or 1 (fail). Use `argparse`.

A sample GitHub Actions step lives in `ci-example.yml` (read it; no need to change it).

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Prompt regression gate for CI".
Before I write code, teach me regression testing for prompts and models, why averages hide regressions, critical
tags, and CI gating. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m09-evaluation/ex51-prompt-regression/starter.py so that test_gate.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Gate`, `compare`,
`render`, `main`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m09-evaluation/ex51-prompt-regression` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Prompt regression gate for CI" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Is the pass rate computed over the intersection of case ids only? Does a missing case fail
the gate? Is the markdown report readable in a pull-request comment? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
