# ex17 · Webhook receiver with HMAC and replay protection

**Chapter:** 5 · Enterprise Integration (`exercises/ch05-enterprise-integration/`) · **Covers:** R05 Integration, R17 Security

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
Signature header: `X-Signature: t=<unix_ts>,v1=<hex>` where `hex = HMAC_SHA256(secret, f"{t}.".encode() + body)`
and `body` is the raw request body as `bytes`. `sign` and `handle` also accept a `str` body, which they UTF-8 encode
first, so both forms give the same signature.

1. `sign(body, secret, t) -> str` — returns the header value (useful for tests and for the customer's devs).
2. `WebhookReceiver(secret, clock=time.time, tolerance=300, dedupe_ttl=3600)` with
   `handle(headers, body) -> (status, message)`. `secret` is one string, or a list of active secrets during rotation
   (`[new, old]`): a signature made with any of them is valid, and an empty list accepts nothing.
   - missing/malformed header → `(401, ...)`; a signature that matches no active secret →
     `(401, "bad signature")` (compare with `hmac.compare_digest` on bytes, so a non-ASCII `v1` value is a 401, not a
     `TypeError`)
   - `|now - t| > tolerance`, in the past or the future → `(400, "stale")`
   - body not JSON or missing `id` → `(400, ...)`
   - event `id` already seen within `dedupe_ttl` → `(200, "duplicate")` and do **not** process again
   - otherwise append the parsed event to `self.processed` and return `(202, "accepted")`
   - expired dedupe entries are purged on each call.

Header names are case-insensitive.

The negative tests also replay a captured signature with `t` rewritten to the current time (401, because `t` is
signed), send a timestamp 301 seconds in the future (stale), and rotate secrets: `[new, old]` accepts both, and once
`old` is dropped its signatures get 401.

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch05-enterprise-integration/ex17-webhook-hmac`.
- **Expected output:** all 17 tests fail against the starter; when you're done, all 17 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch05-enterprise-integration/ex17-webhook-hmac`: all
  17 pass.
- **Tests:** `test_webhook.py` (17 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Seen event ids live in one process's memory, so a restart or a second replica forgets
  earlier deliveries, and the secrets are passed in at construction. Production keeps seen ids in a shared store with
  a TTL, loads the rotation list from a secret manager, syncs clocks with NTP, caps the body size and queues accepted
  events for asynchronous processing.

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
Implement exercises/ch05-enterprise-integration/ex17-webhook-hmac/starter.py so that test_webhook.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `sign`,
`WebhookReceiver`, `apply_update`, `reconcile`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch05-enterprise-integration/ex17-webhook-hmac` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Webhook receiver with HMAC and replay protection" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Is the signature computed over the raw body exactly as received? Is
compare_digest used for every comparison? Can the dedupe cache grow without bound? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
