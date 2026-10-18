from dataclasses import dataclass
from datetime import date, timedelta

NAMES = {"R": "Risk", "A": "Assumption", "I": "Issue", "D": "Decision"}


@dataclass
class RaidItem:
    kind: str
    title: str
    owner: str = ""
    created: date | None = None
    due: date | None = None
    probability: int | None = None
    impact: int | None = None
    mitigation: str = ""
    rationale: str = ""
    decided_by: str = ""
    status: str = "open"
    id: str = ""


class RaidLog:
    def __init__(self):
        self.items: list[RaidItem] = []

    def add(self, item: RaidItem) -> RaidItem:
        if item.kind not in NAMES:
            raise ValueError(f"unknown RAID kind {item.kind!r}")
        if not item.owner:
            raise ValueError("every RAID item needs an owner")
        if item.kind == "R":
            for f in ("probability", "impact"):
                v = getattr(item, f)
                if not isinstance(v, int) or not 1 <= v <= 5:
                    raise ValueError(f"risk {f} must be an int 1-5")
            if not item.mitigation:
                raise ValueError("risk needs a mitigation")
        if item.kind == "D" and not (item.rationale and item.decided_by):
            raise ValueError("decision needs rationale and decided_by")
        item.id = f"{item.kind}-{len(self.items) + 1}"
        self.items.append(item)
        return item

    def score(self, item: RaidItem) -> int:
        return item.probability * item.impact if item.kind == "R" else 0

    def _open(self, kind=None):
        return [i for i in self.items if i.status == "open" and (kind is None or i.kind == kind)]

    def top_risks(self, n: int = 5) -> list[RaidItem]:
        return sorted(self._open("R"), key=lambda r: (-self.score(r), r.created or date.min))[:n]

    def overdue(self, today: date) -> list[RaidItem]:
        return [i for i in self._open() if i.due and i.due < today]

    def escalations(self, today: date) -> list[RaidItem]:
        hot = {i.id: i for i in self._open("R") if self.score(i) >= 15}
        for i in self._open("I"):
            if i.due and today - i.due > timedelta(days=3):
                hot[i.id] = i
        return sorted(hot.values(), key=lambda i: int(i.id.split("-")[1]))

    def to_markdown(self) -> str:
        rows = ["| ID | Type | Title | Owner | Score | Status |", "|---|---|---|---|---|---|"]
        rows += [f"| {i.id} | {NAMES[i.kind]} | {i.title} | {i.owner} | {self.score(i)} | {i.status} |" for i in self.items]
        return "\n".join(rows) + "\n"
