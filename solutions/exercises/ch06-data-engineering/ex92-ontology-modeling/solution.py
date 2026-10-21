import copy
from dataclasses import dataclass, field

TYPES = {"int": int, "float": (int, float), "str": str, "bool": bool}


@dataclass
class ObjectType:
    name: str
    primary_key: str
    properties: dict


@dataclass
class LinkType:
    name: str
    source: str
    target: str
    cardinality: str
    foreign_key: str


def _type_ok(value, type_name) -> bool:
    if value is None:
        return True
    if type_name != "bool" and isinstance(value, bool):
        return False
    return isinstance(value, TYPES[type_name])


class Ontology:
    def __init__(self):
        self.object_types: dict[str, ObjectType] = {}
        self.link_types: dict[str, LinkType] = {}
        self.objects: dict[str, dict] = {}
        self.audit: list[dict] = []
        self.rejected: list[dict] = []       # refused and failed actions: what a security review asks for first
        self.actions: dict[str, dict] = {}

    def add_object_type(self, ot: ObjectType) -> None:
        self.object_types[ot.name] = ot
        self.objects.setdefault(ot.name, {})

    def add_link_type(self, lt: LinkType) -> None:
        for t in (lt.source, lt.target):
            if t not in self.object_types:
                raise ValueError(f"link {lt.name} references unknown object type {t}")
        self.link_types[lt.name] = lt

    def load(self, type_name: str, rows: list[dict]) -> list[str]:
        ot = self.object_types[type_name]
        store = self.objects[type_name]
        errors = []
        for i, row in enumerate(rows):
            pk = row.get(ot.primary_key)
            if pk is None:
                errors.append(f"{type_name}:{i}: missing primary key {ot.primary_key}")
                continue
            bad = [p for p, t in ot.properties.items() if not _type_ok(row.get(p), t)]
            if bad:
                errors.append(f"{type_name}:{i}: wrong type for {', '.join(bad)}")
                continue
            if pk in store:
                errors.append(f"{type_name}:{i}: duplicate primary key {pk}")
                continue
            store[pk] = {p: row.get(p) for p in ot.properties}
        return errors

    def integrity(self) -> list[str]:
        out = []
        for lt in self.link_types.values():
            targets = self.objects[lt.target]
            for pk, obj in self.objects[lt.source].items():
                fk = obj.get(lt.foreign_key)
                if fk is not None and fk not in targets:
                    out.append(f"{lt.name}:{pk}->{fk}")
        return sorted(out)

    def get(self, type_name: str, pk):
        return self.objects[type_name].get(pk)

    def traverse(self, type_name: str, pk, link: str):
        if link.startswith("~"):
            lt = self.link_types[link[1:]]
            if lt.target != type_name:
                raise ValueError(f"{link} does not end at {type_name}")
            return [o for _, o in sorted(self.objects[lt.source].items()) if o.get(lt.foreign_key) == pk]
        lt = self.link_types[link]
        if lt.source != type_name:
            raise ValueError(f"{link} does not start at {type_name}")
        fk = self.get(type_name, pk).get(lt.foreign_key)
        target = self.objects[lt.target].get(fk)
        return target if lt.cardinality == "one" else ([target] if target else [])

    def register_action(self, name, object_type, params, validate, apply, allowed_roles) -> None:
        self.actions[name] = dict(object_type=object_type, params=params, validate=validate, apply=apply,
                                  roles=set(allowed_roles))

    def _check(self, name: str, role: str, params: dict) -> dict:
        a = self.actions.get(name)
        if a is None:
            raise ValueError(f"unknown action {name}")
        if role not in a["roles"]:
            raise PermissionError(f"role {role!r} may not run {name}")
        missing = [p for p in a["params"] if p not in params]
        bad = [p for p, t in a["params"].items() if p in params and not _type_ok(params[p], t)]
        if missing or bad or set(params) - set(a["params"]):
            raise ValueError(f"bad parameters: missing={missing} wrong_type={bad}")
        ot = self.object_types[a["object_type"]]
        if ot.primary_key in params and self.get(ot.name, params[ot.primary_key]) is None:
            raise ValueError(f"unknown {ot.name} {params[ot.primary_key]}")
        problem = a["validate"](self, **params)
        if problem:
            raise ValueError(problem)
        return a

    def execute(self, name: str, actor: str, role: str, **params):
        snapshot = copy.deepcopy(self.objects)
        try:
            a = self._check(name, role, params)
            a["apply"](self, **params)
        except Exception as exc:
            self.objects = snapshot          # actions are atomic
            self.rejected.append({"action": name, "actor": actor, "role": role, "error": str(exc)})
            raise
        self.audit.append({"action": name, "actor": actor, "params": dict(params), "seq": len(self.audit) + 1})
