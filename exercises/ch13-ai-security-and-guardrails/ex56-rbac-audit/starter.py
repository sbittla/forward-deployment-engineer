import hashlib
import json


class AuditLog:
    def __init__(self):
        self.entries: list[dict] = []

    def append(self, record: dict) -> dict:
        raise NotImplementedError

    def verify(self) -> bool:
        raise NotImplementedError


class AccessController:
    def __init__(self, roles: dict[str, dict]):
        self.roles = roles
        self.audit = AuditLog()

    def permissions(self, role: str) -> set[str]:
        raise NotImplementedError

    def check(self, user: dict, action: str, resource: dict) -> bool:
        raise NotImplementedError
