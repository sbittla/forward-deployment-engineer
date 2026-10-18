from dataclasses import dataclass
from datetime import datetime

SQL_TYPES = {"int": "INTEGER", "float": "REAL", "bool": "INTEGER", "datetime": "TEXT", "str": "TEXT", "null": "TEXT"}


@dataclass
class Change:
    kind: str
    column: str
    detail: str
    severity: str


def infer_type(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return "datetime" if "-" in value else "str"
        except ValueError:
            return "str"
    return "str"


def _merge(types: set[str]) -> str:
    types = types - {"null"}
    if not types:
        return "null"
    if len(types) == 1:
        return types.pop()
    if types == {"int", "float"}:
        return "float"
    return "str"


def infer_schema(records: list[dict]) -> dict:
    cols = []
    for r in records:
        cols += [c for c in r if c not in cols]
    schema = {}
    for c in cols:
        values = [r.get(c) for r in records]
        schema[c] = {
            "type": _merge({infer_type(v) for v in values}),
            "nullable": any(c not in r or r[c] is None for r in records),
        }
    return schema


def diff(expected: dict, observed: dict) -> list[Change]:
    out = []
    for col in sorted(set(expected) | set(observed)):
        e, o = expected.get(col), observed.get(col)
        if e is None:
            out.append(Change("added", col, o["type"], "warn"))
        elif o is None:
            out.append(Change("removed", col, "", "error"))
        else:
            if e["type"] != o["type"] and o["type"] != "null":
                widening = (e["type"], o["type"]) == ("int", "float")
                out.append(Change("type_changed", col, f"{e['type']}->{o['type']}", "warn" if widening else "error"))
            if not e["nullable"] and o["nullable"]:
                out.append(Change("nullability_changed", col, "not null->nullable", "error"))
    return out


def migration_sql(table: str, changes: list[Change], observed: dict) -> list[str]:
    sql = []
    for c in changes:
        if c.kind == "added":
            sql.append(f"ALTER TABLE {table} ADD COLUMN {c.column} {SQL_TYPES[observed[c.column]['type']]}")
        else:
            sql.append(f"-- manual: {c.kind} {c.column} ({c.detail})")
    return sql
