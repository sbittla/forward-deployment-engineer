# ex17 · Webhook receiver with HMAC and replay protection

**Module:** m03 · **Covers:** R05 Integration, R17 Security · **Time:** 45 min

## Scenario
The customer's CRM will push "case updated" events to your service. Their security team's review checklist:
signatures verified with a shared secret, constant-time comparison, stale timestamps rejected, replays ignored,
and duplicate deliveries acknowledged without double-processing.

## Your task
Signature header: `X-Signature: t=<unix_ts>,v1=<hex>` where `hex = HMAC_SHA256(secret, f"{t}.{body}")` and `body`
is the raw request body string.

1. `sign(body, secret, t) -> str` — returns the header value (useful for tests and for the customer's devs).
2. `WebhookReceiver(secret, clock=time.time, tolerance=300, dedupe_ttl=3600)` with
   `handle(headers, body) -> (status, message)`:
   - missing/malformed header or bad signature → `(401, ...)` (compare with `hmac.compare_digest`)
   - `|now - t| > tolerance` → `(400, "stale")`
   - body not JSON or missing `id` → `(400, ...)`
   - event `id` already seen within `dedupe_ttl` → `(200, "duplicate")` and do **not** process again
   - otherwise append the parsed event to `self.processed` and return `(202, "accepted")`
   - expired dedupe entries are purged on each call.

Header names are case-insensitive.
