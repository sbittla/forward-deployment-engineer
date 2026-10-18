# ex15 · Idempotent job queue with dead-letter handling

**Module:** m02 · **Covers:** R28 Backend architecture, R22 Production hardening · **Time:** 60 min

## Scenario
The customer wants every inbound email triaged by an LLM. Emails arrive in bursts; the LLM call can fail; a
worker pod can die mid-job. You need at-least-once processing with safe retries and a place where poison
messages go to be inspected rather than retried forever.

## Your task
Implement an in-memory `JobQueue(clock, max_attempts=3, base_backoff=2.0)`:

- `enqueue(kind, payload, idempotency_key=None) -> job_id` — duplicates (same key) return the existing id.
- `claim(worker, lease_s=30) -> Job | None` — returns the oldest job whose `available_at <= now` and which is not
  leased (or whose lease expired). Sets `lease_owner`, `lease_until`, increments `attempts`.
- `ack(job_id, worker)` — marks done. Raises `LeaseError` if `worker` no longer owns the lease.
- `fail(job_id, worker, error)` — if `attempts >= max_attempts` move to the dead-letter list; otherwise make it
  available again at `now + base_backoff ** attempts`. Records `last_error`. Same lease check as `ack`.
- `stats() -> {"queued", "leased", "done", "dead"}`.
- `run_worker(queue, handlers, worker, max_jobs)` — claims up to `max_jobs` jobs, dispatches to
  `handlers[job.kind](job.payload)`, acks on success, fails on exception (unknown kinds fail with
  `"no handler for <kind>"`). Returns the number of jobs processed (successes + failures).

## Field notes
Show the customer the dead-letter queue on day one. It is the difference between "the AI lost my email" and
"three emails need a human — here they are".
