from dataclasses import dataclass


@dataclass
class Change:
    kind: str
    column: str
    detail: str
    severity: str


def infer_type(value) -> str:
    raise NotImplementedError


def infer_schema(records: list[dict]) -> dict:
    raise NotImplementedError


def diff(expected: dict, observed: dict) -> list[Change]:
    raise NotImplementedError


def migration_sql(table: str, changes: list[Change], observed: dict) -> list[str]:
    raise NotImplementedError
