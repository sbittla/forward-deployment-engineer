# ex51 · Prompt regression gate for CI

**Chapter:** 12 · LLM Evaluation (`exercises/ch12-llm-evaluation/`) · **Covers:** R13 Evaluation, R07 CI/CD

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch12-llm-evaluation/ex51-prompt-regression`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch12-llm-evaluation/ex51-prompt-regression`: all 6
  pass.
- **Tests:** `test_gate.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The gate trusts the tags and pass/fail values in two JSON files and treats every non-
  critical case as equally noisy. A production gate reads results from a tagged, reproducible eval run, protects the
  critical-tag list and the golden set's version from change in the same pull request, and keeps a human approval
  step for any override.

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
Implement exercises/ch12-llm-evaluation/ex51-prompt-regression/starter.py so that test_gate.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Gate`, `compare`,
`render`, `main`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch12-llm-evaluation/ex51-prompt-regression` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Prompt regression gate for CI" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Is the pass rate computed over the intersection of case ids only? Does a missing case fail
the gate? Is the markdown report readable in a pull-request comment? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
