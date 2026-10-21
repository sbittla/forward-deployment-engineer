# ex61 · SLOs and error-budget burn alerts

**Module:** m11 · **Covers:** R15 Reliability & monitoring · **Time:** 50 min

## Learning objectives
- Define an SLO and error budget for an AI service.
- Alert on multi-window burn rates instead of raw error rates.
- Track remaining budget over a 30-day period.

## Scenario
The customer's SRE team will only accept your copilot into their on-call rotation if it has an SLO and
burn-rate alerts (the multi-window approach from the Google SRE workbook), not "alert when error rate > 1%".

## Your task
Requests: `(ts_seconds, status_code, latency_ms)`. A request is **good** if `status < 500` and
`latency_ms <= latency_threshold_ms`.

`SLO(target=0.995, latency_threshold_ms=3000)`:
- `error_budget` → `1 - target`
- `sli(requests, now, window_s)` → good / total for requests with `now - window_s < ts <= now`; `None` if no requests
- `burn_rate(requests, now, window_s)` → `(1 - sli) / error_budget` (0.0 when sli is None), rounded to 2 dp
- `alerts(requests, now)` → list of alert names:
  - `"page"` if burn ≥ 14.4 over **both** 1 h and 5 min
  - `"ticket"` if burn ≥ 6 over **both** 6 h and 30 min (and not already paging)
- `budget_remaining(requests, now, period_s=30*86400)` → `1 - (bad / (total * error_budget))` over the period,
  rounded to 4 dp (can go negative; 1.0 when there are no requests)

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

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
Implement exercises/m11-deploy-operate/ex61-slo-burn-rate/starter.py so that test_slo.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `SLO`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m11-deploy-operate/ex61-slo-burn-rate` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "SLOs and error-budget burn alerts" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Are the window boundaries half-open as specified? Does 'ticket' suppress when
'page' fires? Should slow responses count against the same budget as errors for this customer? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
