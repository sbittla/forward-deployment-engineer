# ex51 hints · Prompt regression gate for CI

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Everything in `compare` is set arithmetic on case ids. Compute the sorted intersection of the two runs' ids first. Pass
rates, regressions and fixes are all measured on that intersection, and `missing` is `base - candidate`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Regressions:** passed in base, failed in the candidate. **Fixes:** the reverse.
- **Critical regressions:** regressions whose candidate tags share anything with `critical_tags`.
- `passed = delta >= -max_drop and not critical and not missing`.
- **render:** one helper that builds a section heading plus `- id` lines, or `- none` when the list is empty. Format
  rates with `:.4f` and the delta with `:+.4f`.
- **main:** `argparse` with two positional paths and `--max-drop` (`type=float`). Print the report and return 0 or 1;
  don't call `sys.exit` inside `main`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A critical regression fails the gate even when the overall rate went **up**. Safety cases aren't averaged away.
- A missing case also fails the gate. A candidate run that quietly drops failing cases would otherwise look better.
- Round the delta to 4 dp before comparing it with `-max_drop`, so floating-point noise doesn't flip a borderline
  result.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_pass_with_fix` | Rates computed over all ids instead of the intersection |
| `test_critical_regression_fails_even_if_rate_up` | Critical check uses base tags, or is skipped when the rate didn't drop |
| `test_rate_drop` | Delta sign reversed, or compared with `>` instead of `>=` |
| `test_missing` | Missing cases not detected, or don't fail the gate |
| `test_render` | Delta not signed; `(critical)` suffix missing; `- none` printed for non-empty sections |
| `test_main` | `main` calls `sys.exit`, or `--max-drop` not parsed as a float |
