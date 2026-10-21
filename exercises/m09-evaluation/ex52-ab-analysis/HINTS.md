# ex52 hints · A/B experiment analysis with bootstrap CIs

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write a `_mean(xs)` helper that raises `ValueError` on an empty list. Use it everywhere, and the empty-group error path
for all four functions comes for free. Then write `lift` and `z_test`, which are closed-form; the bootstrap is a loop
around `lift`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **z-test:**
  - pooled proportion = all successes / all trials;
  - variance = `pooled * (1 - pooled) * (1/n1 + 1/n2)`;
  - `z = (p2 - p1) / sqrt(variance)`;
  - p-value = `math.erfc(abs(z) / math.sqrt(2))`.
- **Bootstrap:** one `random.Random(seed)`. For each of `n` rounds, resample each group with
  `rng.choices(group, k=len(group))` and record the lift. Sort the lifts and pick the values at index
  `int(q * n)` (clamped to `n - 1`) for both tails.
- **Sample size:** type the formula in exactly as written, and use the hard-coded z values for the defaults.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- If the pooled variance is 0 (every outcome the same), return 1.0 rather than dividing by zero.
- The bootstrap is only reproducible if the draws happen in the same order every time. Resample variant then control
  (or the other way round) consistently, from the same RNG.
- `decide` needs **both** conditions for "ship": a CI lower bound above 0 *and* p < 0.05. "harmful" only needs the
  upper bound below 0.
- Pass `decide`'s keyword arguments (`n`, `seed`) through to `bootstrap_ci`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_lift` | Control minus variant (sign reversed) |
| `test_z_test_known_value` | Unpooled variance, or a one-sided p-value |
| `test_bootstrap_deterministic_and_covers` | New unseeded RNG per call; percentile index off |
| `test_sample_size` | Square misplaced: the whole numerator is squared before dividing by `mde**2` |
| `test_decide` | Keyword arguments not passed through; "ship" checks only one condition |
| `test_empty_groups` | Empty groups give `ZeroDivisionError` instead of `ValueError`; zero variance not handled |
