from dataclasses import dataclass
from datetime import date


@dataclass
class RaidItem:
    kind: str  # "R" risk, "A" assumption, "I" issue, "D" decision
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
        raise NotImplementedError

    def score(self, item: RaidItem) -> int:
        raise NotImplementedError

    def top_risks(self, n: int = 5) -> list[RaidItem]:
        raise NotImplementedError

    def overdue(self, today: date) -> list[RaidItem]:
        raise NotImplementedError

    def escalations(self, today: date) -> list[RaidItem]:
        raise NotImplementedError

    def to_markdown(self) -> str:
        raise NotImplementedError
