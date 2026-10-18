# ex52 · A/B experiment analysis with bootstrap CIs

**Module:** m09 · **Covers:** R13 Evaluation, R30 Business value metrics · **Time:** 50 min

## Scenario
The pilot ran the copilot for half of the agents for three weeks. Resolution rate went from 71.2% to 74.0%. The
sponsor asks: is that real, and should we roll out? You will answer with an interval, not a vibe.

## Your task
Outcomes are lists of 0/1 (1 = ticket resolved on first contact).

1. `lift(control, variant) -> float` — `mean(variant) - mean(control)`.
2. `bootstrap_ci(control, variant, n=2000, alpha=0.05, seed=0) -> (lo, hi)` — resample each group with replacement
   (`random.Random(seed)`, `choices`), compute the lift each time, return the `alpha/2` and `1-alpha/2` empirical
   quantiles (sort, index `int(q * n)` clamped to `n-1`), rounded to 4 dp.
3. `z_test(control, variant) -> p_value` — two-sided, two-proportion z-test with pooled variance; use
   `math.erfc(abs(z) / sqrt(2))`. Return 1.0 if the pooled variance is 0. Round to 4 dp.
4. `sample_size(p_base, mde, alpha=0.05, power=0.8) -> int` — per-group n for a two-sided test:
   `ceil((z_a * sqrt(2 p̄ (1-p̄)) + z_b * sqrt(p1(1-p1) + p2(1-p2)))**2 / mde**2)` with `p1 = p_base`,
   `p2 = p_base + mde`, `p̄ = (p1+p2)/2`, `z_a = 1.959964` (alpha=.05), `z_b = 0.841621` (power=.8). Use
   `statistics.NormalDist().inv_cdf` for other alpha/power values.
5. `decide(control, variant, **kw) -> str` — `"ship"` if CI lower bound > 0 and p < 0.05; `"harmful"` if CI upper
   bound < 0; else `"inconclusive"`.
