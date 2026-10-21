from dataclasses import dataclass


class LeaseError(Exception):
    pass


@dataclass
class Job:
    id: int
    kind: str
    payload: dict
    created: float
    available_at: float
    attempts: int = 0
    lease_owner: str | None = None
    lease_until: float = 0.0
    status: str = "queued"
    last_error: str = ""


class JobQueue:
    def __init__(self, clock, max_attempts: int = 3, base_backoff: float = 2.0):
        self.clock = clock
        self.max_attempts = max_attempts
        self.base_backoff = base_backoff
        self._jobs: dict[int, Job] = {}
        self._keys: dict[str, int] = {}

    def enqueue(self, kind: str, payload: dict, idempotency_key: str | None = None) -> int:
        if idempotency_key and idempotency_key in self._keys:
            return self._keys[idempotency_key]
        now = self.clock()
        job = Job(id=len(self._jobs) + 1, kind=kind, payload=payload, created=now, available_at=now)
        self._jobs[job.id] = job
        if idempotency_key:
            self._keys[idempotency_key] = job.id
        return job.id

    def _leased(self, j: Job, now: float) -> bool:
        return j.lease_owner is not None and j.lease_until > now

    def claim(self, worker: str, lease_s: float = 30) -> Job | None:
        now = self.clock()
        ready = [j for j in self._jobs.values()
                 if j.status == "queued" and j.available_at <= now and not self._leased(j, now)]
        if not ready:
            return None
        job = min(ready, key=lambda j: (j.available_at, j.id))
        job.lease_owner, job.lease_until = worker, now + lease_s
        job.attempts += 1
        return job

    def _owned(self, job_id: int, worker: str) -> Job:
        j = self._jobs[job_id]
        if j.lease_owner != worker or not self._leased(j, self.clock()):
            raise LeaseError(f"{worker} does not hold the lease on job {job_id}")
        return j

    def extend(self, job_id: int, worker: str, lease_s: float) -> None:
        j = self._owned(job_id, worker)
        j.lease_until = self.clock() + lease_s

    def ack(self, job_id: int, worker: str) -> None:
        j = self._owned(job_id, worker)
        j.status, j.lease_owner = "done", None

    def fail(self, job_id: int, worker: str, error: str) -> None:
        j = self._owned(job_id, worker)
        j.last_error, j.lease_owner = error, None
        if j.attempts >= self.max_attempts:
            j.status = "dead"
        else:
            j.available_at = self.clock() + self.base_backoff ** j.attempts

    @property
    def dead_letter(self) -> list[Job]:
        return [j for j in self._jobs.values() if j.status == "dead"]

    def stats(self) -> dict:
        now = self.clock()
        st = {"queued": 0, "leased": 0, "done": 0, "dead": 0}
        for j in self._jobs.values():
            if j.status == "queued":
                st["leased" if self._leased(j, now) else "queued"] += 1
            else:
                st[j.status] += 1
        return st


def run_worker(queue: JobQueue, handlers: dict, worker: str, max_jobs: int) -> int:
    processed = 0
    while processed < max_jobs:
        job = queue.claim(worker)
        if job is None:
            break
        handler = handlers.get(job.kind)
        try:
            if handler is None:
                raise LookupError(f"no handler for {job.kind}")
            handler(job.payload)
        except Exception as exc:
            queue.fail(job.id, worker, str(exc))
        else:
            queue.ack(job.id, worker)
        processed += 1
    return processed
