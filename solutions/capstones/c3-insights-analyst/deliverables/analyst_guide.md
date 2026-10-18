# Transaction insights assistant: guide for relationship managers

## How to ask
- Ask one business question at a time: "Total spend by category in February 2026".
- Name the period explicitly (month, quarter or date range) and the customer if you mean one customer.
- Every answer shows the SQL it ran, so a data analyst can verify it. Numbers in the summary are read straight
  from the query result, never written by the model.

## What it will not do
- Change data. Only single read-only `SELECT` queries run, and edits, deletes and schema changes are blocked.
- Reach tables outside `transactions`, `accounts` and `monthly_spend` (no system tables, no other databases).
- Return personal identifiers that are not in the warehouse, such as SSNs. It refuses instead of guessing.
- Return more than 1,000 rows. Ask for an aggregate instead.

## Metric definitions
| Metric | Definition |
|---|---|
| Total spend | Sum of USD amounts with refunds netted out |
| Refund count | Number of transactions with a negative amount |
| Average transaction | Average purchase size in USD, excluding refunds |
| Monthly spend | Pre-aggregated spend per account, month and category |

Foreign-currency transactions are converted to USD at the month-end rates in the FX table (SEK 0.095, EUR 1.08).

## Data freshness
The warehouse loads nightly at 02:00 UTC from the core banking export. Rows that fail checks (unknown account,
unparseable amount or date) are quarantined and reported to Data Engineering. They are not silently dropped.

## When to escalate
- The assistant refuses a question you believe is answerable: send the question to data-help@bank.example.
- A number looks wrong: forward the answer with its SQL to the analytics on-call.
- You need customer-level data for a regulatory request: use the formal data request process, not the assistant.
