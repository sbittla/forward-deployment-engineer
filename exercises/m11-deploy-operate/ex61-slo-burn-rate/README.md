# ex61 · SLOs and error-budget burn alerts

**Module:** m11 · **Covers:** R15 Reliability & monitoring · **Time:** 50 min

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
