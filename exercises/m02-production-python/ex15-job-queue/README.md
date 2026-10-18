# ex15 · Idempotent job queue with dead-letter handling

**Module:** m02 · **Covers:** R28 Backend architecture, R22 Production hardening · **Time:** 60 min

## Learning objectives
- Process jobs at least once with leases, retries and backoff.
- Route poison messages to a dead-letter queue instead of retrying forever.
- Deduplicate enqueues with idempotency keys.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Idempotent job queue with
dead-letter handling". Before I write code, teach me at-least-once delivery, visibility timeouts/leases, exponential
backoff, dead-letter queues, and idempotent consumers. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m02-production-python/ex15-job-queue/starter.py so that test_queue.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `LeaseError`, `Job`,
`JobQueue`, `run_worker`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m02-production-python/ex15-job-queue` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Idempotent job queue with dead-letter handling" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Can a worker ack a job after its lease expired and another worker
claimed it? Is backoff computed from the right attempt count? What would an operator need to see in the dead-letter
list? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
