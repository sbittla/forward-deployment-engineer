# ex51 · Prompt regression gate for CI

**Module:** m09 · **Covers:** R13 Evaluation, R07 CI/CD · **Time:** 45 min

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
