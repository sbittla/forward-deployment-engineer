from dataclasses import dataclass, field


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
    status: str = "queued"  # queued | done | dead
    last_error: str = ""


class JobQueue:
    def __init__(self, clock, max_attempts: int = 3, base_backoff: float = 2.0):
        self.clock = clock
        self.max_attempts = max_attempts
        self.base_backoff = base_backoff

    def enqueue(self, kind: str, payload: dict, idempotency_key: str | None = None) -> int:
        raise NotImplementedError

    def claim(self, worker: str, lease_s: float = 30) -> Job | None:
        raise NotImplementedError

    def extend(self, job_id: int, worker: str, lease_s: float) -> None:
        raise NotImplementedError

    def ack(self, job_id: int, worker: str) -> None:
        raise NotImplementedError

    def fail(self, job_id: int, worker: str, error: str) -> None:
        raise NotImplementedError

    @property
    def dead_letter(self) -> list[Job]:
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError


def run_worker(queue: JobQueue, handlers: dict, worker: str, max_jobs: int) -> int:
    raise NotImplementedError
