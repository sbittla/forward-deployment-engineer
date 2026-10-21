# ex61 · SLOs and error-budget burn alerts

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R15 Reliability & monitoring

## Learning objectives
- Define an SLO and error budget for an AI service.
- Alert on multi-window burn rates instead of raw error rates.
- Track remaining budget over a 30-day period.

## Scenario
The customer's SRE team will only accept your copilot into their on-call rotation if it has an SLO and
burn-rate alerts (the multi-window approach from the Google SRE workbook), not "alert when error rate > 1%".

## Your task
Requests: `(ts_seconds, status_code, latency_ms)`. A request is **good** if `status < 500` and
`latency_ms <= latency_threshold_ms`. The SLO models one user journey, the copilot's **streamed answers**, so
`latency_ms` is the time to first token and the default threshold is 3,000 ms. A non-streamed journey (a full
structured response, say) gets its own `SLO` with its own threshold on total time.

`SLO(target=0.995, latency_threshold_ms=3000)`:
- `error_budget` → `1 - target`
- `sli(requests, now, window_s)` → good / total for requests with `now - window_s < ts <= now`; `None` if no requests
- `burn_rate(requests, now, window_s)` → `(1 - sli) / error_budget` (0.0 when sli is None), rounded to 2 dp
- `alerts(requests, now)` → list of alert names:
  - `"page"` if burn ≥ 14.4 over **both** 1 h and 5 min
  - `"ticket"` if burn ≥ 6 over **both** 6 h and 30 min (and not already paging)
- `budget_remaining(requests, now, period_s=30*86400)` → `1 - (bad / (total * error_budget))` over the period,
  rounded to 4 dp (can go negative; 1.0 when there are no requests)
- `canary_action(canary_requests, now, window_s=HOUR, max_burn=2.0, min_requests=500)` → the release decision for a
  canary from its own error-budget burn over the window: `"rollback"` as soon as its bad requests exceed
  `max_burn * error_budget * min_requests` (it has already overspent what its minimum sample may, so don't wait);
  otherwise `"wait"` while it has fewer than `min_requests` requests; then `"rollback"` if its burn rate is above
  `max_burn`, else `"promote"`.

**Thresholds are inclusive:** a burn rate of exactly 14.4 on both windows pages (`>=`, after rounding to 2 dp).

`test_worked_example_alert_times` replays Chapter 14's worked release (Table 14.7) on a simulated clock: 1 request a
second from 07:00, 2 a second from 08:30, when 15% start returning 503. With the default `SLO`, checked every 20
seconds, the ticket fires at 08:41:20 and the page at 08:49:00; after a rollback at 09:01:00 the page clears at
09:03:40. Synthetic traffic, so the times show how the windows behave, not how a real service would.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex61-slo-burn-rate`.
- **Expected output:** all 10 tests fail against the starter; when you're done, all 10 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex61-slo-burn-rate`: all 10
  pass.
- **Tests:** `test_slo.py` (10 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Burn rates are computed over an in-memory list, and every non-5xx response under the
  threshold counts as good. In production, compute SLIs from recorded metrics in the customer's monitoring system,
  route alerts to their rotation, and agree with the SRE team what counts as bad for an AI service.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "SLOs and error-budget burn alerts".
Before I write code, teach me SLIs, SLOs, error budgets, and multi-window multi-burn-rate alerting from the Google
SRE workbook. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch14-llmops-and-sre/ex61-slo-burn-rate/starter.py so that test_slo.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `SLO`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch14-llmops-and-sre/ex61-slo-burn-rate` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "SLOs and error-budget burn alerts" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Are the window boundaries half-open as specified? Does 'ticket' suppress when
'page' fires? Should slow responses count against the same budget as errors for this customer? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
