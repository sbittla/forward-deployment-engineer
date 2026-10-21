# ex17 · Webhook receiver with HMAC and replay protection

**Module:** m03 · **Covers:** R05 Integration, R17 Security · **Time:** 45 min

## Learning objectives
- Verify webhook signatures with HMAC and constant-time comparison.
- Reject stale timestamps and replayed events.
- Acknowledge duplicate deliveries without double-processing.
- Apply updates in version order and reconcile missed deliveries through the same code path.

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

### Part B · Version-ordered updates and reconciliation
Deduplication by event id stops repeats, not stale deliveries of *different* events. Each record carries `id` and an
integer `version`.

3. `apply_update(store, record) -> bool` — store `record` under `record["id"]` only if `store` holds no copy or an
   older `version`; return `True` if it was applied, `False` for a duplicate or out-of-order delivery.
4. `reconcile(client, store, since) -> int` — call `client.list_all("/cases", {"updated_since": since})`, pass every
   record through `apply_update` and return how many were applied.
5. `WebhookReceiver(..., store=None)` — when `store` is a dict, every accepted event whose `data` is a dict is also
   passed through `apply_update(store, event["data"])`. The response is still `(202, "accepted")`.

Because both paths share `apply_update`, the final store must be the same whatever order the records arrive in and
however many times.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Webhook receiver with HMAC and
replay protection". Before I write code, teach me webhook signing schemes, HMAC-SHA256, timing attacks, replay
windows and idempotent event processing. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m03-apis-integration/ex17-webhook-hmac/starter.py so that test_webhook.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `sign`,
`WebhookReceiver`, `apply_update`, `reconcile`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/m03-apis-integration/ex17-webhook-hmac` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Webhook receiver with HMAC and replay protection" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Is the signature computed over the raw body exactly as received? Is
compare_digest used for every comparison? Can the dedupe cache grow without bound? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
