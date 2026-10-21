# ex61 hints · SLOs and error-budget burn alerts

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write two private helpers: `_good(request)` (status below 500 **and** latency within the threshold) and
`_window(requests, now, window_s)` (requests with `now - window_s < ts <= now`). Every public method is a few lines on
top of them.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **SLI:** good requests over all requests in the window, or `None` for an empty window.
- **Burn rate:** `(1 - sli) / error_budget`. A burn rate of 1 spends exactly the budget over the SLO period; 14.4
  over one hour spends 2% of a 30-day budget.
- **alerts:** a helper `burning(long_window, short_window, threshold)` that requires **both** windows to burn at or
  above the threshold. Check page first, and return straight away if it fires, so a page never comes with a ticket.
- **budget_remaining:** `1 - bad / (total * error_budget)` over the period.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The window is open at the start and closed at the end. A request at exactly `now - window_s` is outside.
- A slow but successful request is still **bad**: latency counts towards the SLI.
- The short window is there to stop alerts once an incident is over. The long window is there to stop alerts on a
  brief spike. That's why a five-minute spike alone mustn't page.
- `budget_remaining` can go negative when the budget is overspent; don't clamp it.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_budget_and_sli` | Empty window returns 0 or 1 instead of `None`; burn rate not rounded |
| `test_latency_counts_as_bad` | Only status codes considered |
| `test_window_bounds` | Window includes `ts == now - window_s` |
| `test_page` | Only one window checked, or the ticket check runs as well as the page |
| `test_ticket_not_page` | Ticket thresholds or windows wrong (6 over 6 h and 30 min) |
| `test_short_spike_no_page` | Paging on the short window alone |
| `test_budget_remaining` | Formula inverted, or no requests returns 0 instead of 1.0 |
