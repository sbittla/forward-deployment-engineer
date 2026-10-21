# ex52 · A/B experiment analysis with bootstrap CIs

**Chapter:** 12 · LLM Evaluation (`exercises/ch12-llm-evaluation/`) · **Covers:** R13 Evaluation, R30 Business value metrics

## Learning objectives
- Quantify an A/B lift with a bootstrap confidence interval.
- Run a two-proportion z-test and compute required sample sizes.
- Make a ship / inconclusive / harmful recommendation a sponsor can defend.

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

**Errors:** `lift`, `bootstrap_ci`, `z_test` and `decide` raise `ValueError` if either group is empty.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch12-llm-evaluation/ex52-ab-analysis`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch12-llm-evaluation/ex52-ab-analysis`: all 6 pass.
- **Tests:** `test_ab.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The analysis treats every ticket as independent and has no guard against peeking or novelty
  effects. A production analysis pre-registers the metric, rule and sample size, randomises and analyses by agent (or
  uses a clustered analysis) when tickets share an agent, and has a statistician review high-stakes decisions.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "A/B experiment analysis with
bootstrap CIs". Before I write code, teach me A/B testing for AI pilots: lift, bootstrap CIs, two-proportion
z-tests, statistical power and sample size. Use short Python examples that are not the exercise solution. Then ask
me three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch12-llm-evaluation/ex52-ab-analysis/starter.py so that test_ab.py passes. README.md in that folder
is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lift`, `bootstrap_ci`,
`z_test`, `sample_size`, `decide`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package
only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/ch12-llm-evaluation/ex52-ab-analysis` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "A/B experiment analysis with bootstrap CIs" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Is the bootstrap deterministic for a seed and are quantile indices
clamped? Does the z-test handle zero variance? Would you trust a 'ship' decision from a three-week pilot with
novelty effects? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
