import json
import re
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
        self.always_approve = frozenset(always_approve)  # policy in code: the plan can't switch these off

    def _approved(self, step: Step) -> bool:
        try:
            return self.approve(step) is True  # fail closed: errors and anything but True mean "no"
        except Exception:
            return False

    def _system(self) -> str:
        return ("You are a planner. Break the goal into steps for these workers: "
                f"{', '.join(sorted(self.workers))}. Reply with only a JSON array of objects with keys "
                '"id", "worker", "task", "depends_on" (list of step ids), "requires_approval" (true for any step '
                "that moves money, deletes data or contacts a customer).")

    def plan(self, goal: str) -> list[Step]:
        text = self.planner_llm.complete([{"role": "user", "content": goal}], system=self._system()).text
        match = re.search(r"\[.*\]", text, re.S)
        raw = json.loads(match.group(0) if match else text)
        steps = [Step(s["id"], s["worker"], s["task"], list(s.get("depends_on", [])), bool(s.get("requires_approval")))
                 for s in raw]
        ids = {s.id for s in steps}
        for s in steps:
            if s.worker not in self.workers:
                raise ValueError(f"step {s.id} uses unknown worker {s.worker!r}")
            missing = set(s.depends_on) - ids
            if missing:
                raise ValueError(f"step {s.id} depends on unknown steps {sorted(missing)}")
        ordered, placed = [], set()
        while len(ordered) < len(steps):
            ready = [s for s in steps if s.id not in placed and set(s.depends_on) <= placed]
            if not ready:
                raise ValueError("plan has a dependency cycle")
            ordered.append(ready[0])
            placed.add(ready[0].id)
        return ordered

    def run(self, goal: str) -> RunReport:
        steps = self.plan(goal)
        statuses, outputs, audit = {}, {}, [f"plan: {len(steps)} steps"]
        for s in steps:
            approved = True
            blocked = any(statuses.get(d) != "done" for d in s.depends_on)
            if not blocked and (s.requires_approval or s.worker in self.always_approve):
                audit.append(f"{s.id}: approval requested")
                approved = self._approved(s)
            if blocked:
                statuses[s.id] = "skipped"
            elif not approved:
                statuses[s.id] = "rejected"
            else:
                try:
                    outputs[s.id] = self.workers[s.worker](s.task, {d: outputs[d] for d in s.depends_on})
                    statuses[s.id] = "done"
                except Exception as exc:
                    outputs[s.id] = f"{type(exc).__name__}: {exc}"
                    statuses[s.id] = "failed"
            audit.append(f"{s.id}: {statuses[s.id]}")
        return RunReport(steps, statuses, outputs, audit)
