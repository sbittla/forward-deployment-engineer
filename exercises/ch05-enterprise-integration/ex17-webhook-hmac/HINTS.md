# ex17 hints · Webhook receiver with HMAC and replay protection

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `sign` first: `hmac.new(secret.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()`, formatted as
`t=...,v1=...`. `test_sign_format` tells you straight away whether it's right, and the receiver uses the same MAC
function to verify.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Run the checks in `handle` in the order the README lists them, returning as soon as one fails:

1. find the header, ignoring case;
2. parse `t` and `v1`;
3. compare signatures with `hmac.compare_digest`;
4. check the timestamp;
5. parse the JSON and read `id`;
6. dedupe.

Keep a dict of `event_id -> time first seen` for deduplication, and purge old entries at the start of every call.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Verify the signature **before** checking the timestamp or parsing the body. An attacker controls both, and only a
  valid signature makes them trustworthy.
- A malformed header (no `=`, no `t`, a non-numeric `t`) must return 401, not crash. Catch `KeyError` and
  `ValueError` around the parsing.
- The staleness boundary is `abs(now - t) > tolerance`: exactly 300 seconds old is still accepted.
- Sign and verify the **raw** body string. Re-serializing the parsed JSON changes the bytes.
- Part B: compare with `>=`, not `>`. An equal version is a duplicate and must not be applied. `reconcile` should
  call `apply_update` rather than write to the store itself, so both paths obey the same rule.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_sign_format` | Message joined without the `.`, or the secret/body not encoded to bytes |
| `test_accept_then_duplicate` | Header lookup is case-sensitive (`x-signature`), or duplicates processed again |
| `test_bad_signature_and_missing` | Malformed header raises instead of returning 401; tampered body accepted |
| `test_raw_body_bytes_are_signed` | `bytes` body formatted into an f-string (`b'...'` gets signed), or a `str` body not UTF-8 encoded |
| `test_non_ascii_signature_is_401_not_a_crash` | `hmac.compare_digest` called on `str` values, which raises `TypeError` for non-ASCII text |
| `test_stale` | Boundary uses `>=`; or staleness checked with the wrong sign |
| `test_bad_json` | Missing `id` raises `KeyError` instead of returning 400 |
| `test_dedupe_expires` | Seen ids never purged, so the event is a duplicate forever |
| `test_apply_update_rejects_stale_and_duplicate` | Comparison uses `>` so an equal version is re-applied, or the return value is missing |
| `test_shuffled_and_duplicated_deliveries_converge` | Last write wins: the record is stored without comparing versions |
| `test_reconcile_uses_the_same_path` | Wrong path or params passed to `list_all`, or records written without `apply_update` |
| `test_receiver_ignores_stale_redelivery` | `store` ignored, or `event["data"]` stored directly instead of through `apply_update` |
| `test_boundary_replay_outside_window_is_stale` | Staleness not checked, or checked with the wrong sign, so a replay is accepted once its seen id expires |
| `test_boundary_dedupe_is_per_process` | Seen ids kept in a class-level or module-level dict shared between receivers instead of per instance |
| `test_rewritten_timestamp_is_rejected` | The MAC computed without `t`, or the timestamp checked before the signature |
| `test_future_timestamp_is_stale` | `now - t > tolerance` without `abs`, so a future timestamp passes |
| `test_rotation_accepts_either_secret_during_overlap` | A list of secrets treated as one string, or only the first secret checked |
