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


class Ontology:
    def __init__(self):
        self.object_types: dict[str, ObjectType] = {}
        self.link_types: dict[str, LinkType] = {}
        self.objects: dict[str, dict] = {}
        self.audit: list[dict] = []

    def add_object_type(self, ot: ObjectType) -> None:
        raise NotImplementedError

    def add_link_type(self, lt: LinkType) -> None:
        raise NotImplementedError

    def load(self, type_name: str, rows: list[dict]) -> list[str]:
        raise NotImplementedError

    def integrity(self) -> list[str]:
        raise NotImplementedError

    def get(self, type_name: str, pk):
        raise NotImplementedError

    def traverse(self, type_name: str, pk, link: str):
        raise NotImplementedError

    def register_action(self, name, object_type, params, validate, apply, allowed_roles) -> None:
        raise NotImplementedError

    def execute(self, name: str, actor: str, role: str, **params):
        raise NotImplementedError
