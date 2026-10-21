import re
from datetime import datetime, timezone


class MappingError(Exception):
    def __init__(self, field: str, message: str = "required field missing"):
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


def _date_iso(v) -> str:
    if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
        return datetime.fromtimestamp(int(v), tz=timezone.utc).date().isoformat()
    s = str(v).strip()
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
        return datetime.strptime(s, "%m/%d/%Y").date().isoformat()
    return datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()


TRANSFORMS: dict = {
    "strip": lambda v: str(v).strip(),
    "lower": lambda v: str(v).lower(),
    "upper": lambda v: str(v).upper(),
    "int": lambda v: int(v),
    "date_iso": _date_iso,
}


def register_transform(name: str, fn) -> None:
    TRANSFORMS[name] = fn


def _resolve_transform(spec: str):
    if spec.startswith("map:"):
        table = dict(pair.split("=", 1) for pair in spec[4:].split(",") if pair)
        return lambda v: table.get(v, v)
    if spec not in TRANSFORMS:
        raise ValueError(f"unknown transform {spec!r}")
    return lambda v: TRANSFORMS[spec](v)  # late-bound so re-registration takes effect


_MISSING = object()
_TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def _get(record, path: str):
    cur = record
    for key, idx in _TOKEN.findall(path):
        try:
            cur = cur[int(idx)] if idx else cur[key]
        except (KeyError, IndexError, TypeError):
            return _MISSING
    return cur


class Connector:
    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self._pipelines = {f: [_resolve_transform(t) for t in spec.get("transforms", [])] for f, spec in fields.items()}

    @classmethod
    def from_config(cls, cfg: dict) -> "Connector":
        if not cfg.get("name") or not isinstance(cfg.get("fields"), dict):
            raise ValueError("config needs 'name' and 'fields'")
        for f, spec in cfg["fields"].items():
            if "path" not in spec:
                raise ValueError(f"field {f!r} has no path")
        return cls(cfg["name"], cfg["fields"])

    def transform(self, record: dict) -> dict:
        out = {}
        for f, spec in self.fields.items():
            value = _get(record, spec["path"])
            if value is _MISSING or value is None:
                if spec.get("required"):
                    raise MappingError(f)
                out[f] = spec.get("default")
                continue
            for step in self._pipelines[f]:
                value = step(value)
            out[f] = value
        return out

    def run(self, records: list[dict]):
        rows, errors = [], []
        for i, r in enumerate(records):
            try:
                rows.append(self.transform(r))
            except MappingError as e:
                errors.append((i, e.field, e.message))
            except (ValueError, TypeError) as e:
                errors.append((i, "?", str(e)))
        return rows, errors
