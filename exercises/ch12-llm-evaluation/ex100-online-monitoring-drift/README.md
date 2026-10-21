# ex100 · Online quality monitoring and drift detection

**Chapter:** 12 · LLM Evaluation (`exercises/ch12-llm-evaluation/`) · **Covers:** R13 Evaluation, R15 Observability & reliability

## Learning objectives
- Extend evaluation past launch: watch inputs, live judge scores, refusals, latency and cost in production windows.
- Detect input drift with the population stability index (PSI), for numeric and categorical features.
- Avoid alert noise with minimum sample sizes, and sample conversations for human review in a reproducible way.

## Scenario
Six weeks after go-live, the support copilot's offline evals are still green, but agents say it "got worse". In
fact a product launch shifted the ticket mix: a new `outage` intent, longer pasted logs, and more refusals. Nobody
noticed for nine days. You'll build the monitor that would have paged on day one, and the sampler that sends a fair,
reproducible slice of conversations to human reviewers.

## Your task
- `quantile_edges(values, bins) -> list[float]`: with `s = sorted(values)`, edge `i` for `i = 1..bins-1` is
  `s[min(n-1, int(n*i/bins))]`.
- `psi(baseline, current, bins=10) -> float`:
  - bin both windows with the baseline's quantile edges; the bucket index is the number of edges `<= x`;
  - floor each bucket's share at `EPS = 1e-4`;
  - return `Σ (a - e) · ln(a / e)` rounded to 4 dp;
  - raise `ValueError` if either window is empty.
- `category_psi(baseline_counts, current_counts) -> float`: the same formula over the union of categories (sorted),
  where a category missing from one side counts 0 and is floored at `EPS`. `ValueError` if either total is 0.
- `drift_level(value) -> "stable" | "watch" | "drift"`: `watch` from 0.1, `drift` from 0.25.
- `p95(values)`: nearest-rank, i.e. `sorted[ceil(0.95·n) - 1]`.
- `Thresholds(min_samples=50, judge_drop=0.05, refusal_rate=0.05, p95_latency_ms=4000, cost_per_conv=0.10)`.
- `check_window(baseline, window, t=Thresholds()) -> list[dict]`. `baseline` is `{"input_len": [...], "intents":
  {...}, "judge_pass": float}`. Window records are `{"input_len", "intent", "judge_pass": bool | None, "refused",
  "latency_ms", "cost"}`.
  - With fewer than `min_samples` records, return only
    `{"metric": "samples", "level": "info", "value": n, "message": "only n records; need N before alerting"}`.
  - Otherwise emit alerts `{"metric", "level", "value"}` in this order, only when triggered:

| Metric | Level | Triggers when |
|---|---|---|
| `input_len_psi` | the drift level | the level isn't `stable` |
| `intent_psi` | the drift level | the level isn't `stable` |
| `judge_pass` | `page` | at least `min_samples` records were judged, and the pass rate (4 dp) is below `baseline - judge_drop` |
| `refusal_rate` | `page` | rate (4 dp) > threshold |
| `p95_latency_ms` | `page` | > threshold |
| `cost_per_conv` | `watch` | mean (4 dp) > threshold |

- `sample_for_review(records, rate, always=...) -> list[str]`: a record is picked if
  `always(record)` returns true, or if `int(sha256(id).hexdigest()[:8], 16) / 0xFFFFFFFF < rate`. Return the
  picked ids in input order. `ValueError` unless `0 ≤ rate ≤ 1`.

## Field notes
Offline evals answer "is this version good?"; online monitoring answers "is it still good *for today's traffic*?".
When drift fires, the first action is to pull a sample into review and grow the golden set, not to change the prompt.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch12-llm-evaluation/ex100-online-monitoring-drift`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch12-llm-evaluation/ex100-online-monitoring-drift`:
  all 8 pass.
- **Tests:** `test_monitoring.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Thresholds are fixed constants and alerts are returned, not routed. A production monitor
  calibrates PSI and judge thresholds on its own traffic, pages through the on-call system with deduplication, tracks
  the judge's model version so a judge upgrade isn't read as quality drift, and de-identifies conversations before
  they reach human reviewers.

## Prompt kit
**Learn (tutor prompt)**
```text
Teach me production monitoring for an LLM feature. Explain input drift vs. quality drift, how the population
stability index works (with a 3-bucket numeric example), why online LLM-judge scores need minimum sample sizes, and
which 6 signals you would put on a dashboard for a support copilot. Close with a runbook: what to do in the first
hour after a drift alert.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch12-llm-evaluation/ex100-online-monitoring-drift/starter.py so test_monitoring.py passes. Follow
the README formulas exactly (quantile edges, EPS floor, nearest-rank p95, alert order). Standard library only
(math, hashlib). Don't edit the tests. Run pytest on the folder and show the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review this monitor as the on-call engineer who will be paged by it. Which alerts will be noisy at low traffic?
Is PSI on input length a good proxy for the drift that matters? What happens to judge_pass when the judge model
itself is upgraded? Suggest thresholds for a feature with 2,000 conversations/day.
```
**Online judge prompt (sampled production traffic)**
```text
You are auditing one support-copilot conversation from production. The copilot drafts replies that a human agent
edits and sends. Judge only the copilot's draft.

<conversation>{conversation}</conversation>
<copilot_draft>{draft}</copilot_draft>
<knowledge_used>{retrieved_passages}</knowledge_used>

Check: (1) every factual claim is supported by knowledge_used; (2) the draft answers the customer's actual
question; (3) the draft follows the tone guide: friendly, no promises about timelines. Reply in JSON:
{"supported": bool, "answers_question": bool, "tone_ok": bool, "pass": bool, "evidence": "<one sentence>"}
```
