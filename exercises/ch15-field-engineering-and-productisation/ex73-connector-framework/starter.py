from datetime import datetime, timezone


class MappingError(Exception):
    def __init__(self, field: str, message: str = "required field missing"):
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


TRANSFORMS: dict = {}


def register_transform(name: str, fn) -> None:
    raise NotImplementedError


class Connector:
    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields

    @classmethod
    def from_config(cls, cfg: dict) -> "Connector":
        raise NotImplementedError

    def transform(self, record: dict) -> dict:
        raise NotImplementedError

    def run(self, records: list[dict]):
        raise NotImplementedError
