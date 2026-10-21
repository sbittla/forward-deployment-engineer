# ex100 hints · Online quality monitoring and drift detection

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the three small pieces before anything else: `quantile_edges` (one list comprehension with the README's index
formula), `p95` (nearest rank) and `drift_level` (two thresholds). Then write one shared helper that sums
`(a - e) * ln(a / e)` over two equal-length lists of shares. Both PSI functions use it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Numeric PSI:** compute the edges from the **baseline** only. A value's bucket is the number of edges `<= x`, which
  gives `bins` buckets. Turn the counts into shares for each window, floor each share at `EPS`, and apply the helper.
- **Category PSI:** use the sorted union of categories, with shares of 0 (then floored) for categories missing on one
  side.
- **check_window:** return the "samples" record immediately when there are too few records. Otherwise evaluate each
  metric in the README's order and append an alert only when it triggers.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The flooring at `EPS` is what makes a brand-new intent (missing from the baseline) produce a large but finite PSI
  instead of `log(0)`.
- The judge alert needs at least `min_samples` **judged** records. Ignore `judge_pass is None` when counting and when
  computing the rate.
- Round each rate to 4 dp *before* comparing it with its threshold. The tests' expected values are the rounded ones.
- For sampling, hash the id with SHA-256 and take the first 8 hex digits as an integer over `0xFFFFFFFF`. It's
  deterministic across machines and reruns, unlike `random`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_quantile_edges_and_p95` | Edge index formula changed; p95 interpolates instead of using nearest rank |
| `test_psi_numeric` | Edges recomputed from the current window; bucket counts edges `< x` instead of `<= x`; no flooring |
| `test_category_psi_and_levels` | New categories dropped instead of floored; thresholds use `>` instead of `>=` |
| `test_healthy_window_is_quiet` | An alert fires on equality, or rates compared unrounded |
| `test_too_few_samples` | Further alerts computed despite too few records; message wording differs |
| `test_degraded_window` | Alerts out of order; p95 or refusal rate computed wrongly |
| `test_intent_shift_cost_and_unjudged` | Unjudged records counted as failures; judge alert fires with fewer than `min_samples` judged |
| `test_sampling_is_deterministic` | Python's `hash()` or `random` used (not stable across runs); rate not validated |
