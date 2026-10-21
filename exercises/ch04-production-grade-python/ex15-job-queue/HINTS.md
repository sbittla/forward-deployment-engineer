# ex15 hints · Idempotent job queue with dead-letter handling

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Model a `Job` dataclass with everything the README mentions: `id`, `kind`, `payload`, `available_at`, `attempts`,
`lease_owner`, `lease_until`, a `status` (`queued`, `done` or `dead`) and `last_error`. Keep jobs in a dict by id,
plus a second dict from idempotency key to job id.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- A job is **leased** when it has an owner *and* `lease_until > now`. Write that as a helper. An expired lease needs
  no clean-up: the helper simply stops returning True.
- `claim` picks, from queued jobs that are available and not leased, the one with the smallest
  `(available_at, id)`. It sets the lease and increments `attempts`.
- `ack` and `fail` share a lease check: the caller must be the owner and the lease must still be live. Otherwise
  raise `LeaseError`.
- `extend` reuses the same lease check, then moves `lease_until` forward from *now*. It doesn't count as an attempt.
- `stats` counts queued jobs as `leased` or `queued` depending on the helper.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Backoff uses the attempt count *after* the claim: the first failure waits `base_backoff ** 1`, the second
  `base_backoff ** 2`.
- Dead-lettering happens in `fail` when `attempts >= max_attempts`, before any backoff is scheduled.
- In `run_worker`, an unknown kind is a failure: raise (or record) `"no handler for <kind>"` and send it through
  `fail`, so it's counted as processed and dead-lettered like any other error.
- Use `try / except / else`: ack in the `else`, so an exception raised by `ack` isn't mistaken for a handler failure.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_idempotent_enqueue_and_fifo` | Duplicate key creates a new job; claim returns a job that's already leased |
| `test_lease_expiry_and_stale_ack` | Expired lease still blocks `claim`; `ack` checks only the owner, not the lease time |
| `test_extend_keeps_lease_alive` | Lease end not moved forward, so `w2` claims the job; or `extend` increments `attempts` |
| `test_extend_requires_live_lease` | `extend` skips the lease check, so a non-owner or an expired worker revives the lease |
| `test_backoff_then_dead_letter` | Backoff exponent off by one, or the job dead-lettered one attempt late |
| `test_run_worker` | Unknown kind raises out of `run_worker` instead of being failed, or failures aren't counted as processed |
