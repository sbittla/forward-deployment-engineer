from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Step:
    id: str
    worker: str
    task: str
    depends_on: list[str] = field(default_factory=list)
    requires_approval: bool = False


@dataclass
class RunReport:
    steps: list[Step]
    statuses: dict[str, str]
    outputs: dict[str, str]
    audit: list[str]


class Orchestrator:
    def __init__(self, planner_llm, workers: dict[str, Callable[[str, dict], str]], approve: Callable[[Step], bool],
                 always_approve=frozenset()):
        self.planner_llm = planner_llm
        self.workers = workers
        self.approve = approve
        self.always_approve = frozenset(always_approve)

    def plan(self, goal: str) -> list[Step]:
        raise NotImplementedError

    def run(self, goal: str) -> RunReport:
        raise NotImplementedError
