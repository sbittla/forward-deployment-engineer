import hashlib
import json

GENESIS = "0" * 64


def _digest(prev_hash: str, body: dict) -> str:
    return hashlib.sha256((prev_hash + json.dumps(body, sort_keys=True)).encode()).hexdigest()


class AuditLog:
    def __init__(self):
        self.entries: list[dict] = []

    def append(self, record: dict) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        body = {**record, "prev_hash": prev}
        entry = {**body, "hash": _digest(prev, body)}
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = GENESIS
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            if e.get("prev_hash") != prev or _digest(prev, body) != e.get("hash"):
                return False
            prev = e["hash"]
        return True


class AccessController:
    def __init__(self, roles: dict[str, dict]):
        self.roles = roles
        self.audit = AuditLog()

    def permissions(self, role: str, _seen=None) -> set[str]:
        seen = _seen if _seen is not None else set()
        if role in seen or role not in self.roles:
            return set()
        seen.add(role)
        perms = set(self.roles[role].get("permissions", []))
        for parent in self.roles[role].get("inherits", []):
            perms |= self.permissions(parent, seen)
        return perms

    @staticmethod
    def _matches(perm: str, action: str, resource: dict) -> bool:
        if perm == "*":
            return True
        if "<=" in perm:
            name, limit = perm.split("<=", 1)
            return name == action and resource.get("amount", float("inf")) <= float(limit)
        if perm.endswith(":*"):
            return action.split(":", 1)[0] == perm[:-2]
        return perm == action

    def _decide(self, user: dict, action: str, resource: dict) -> tuple[bool, str]:
        if user["tenant"] != resource.get("tenant"):
            return False, "tenant mismatch"
        perms = set().union(*(self.permissions(r) for r in user["roles"])) if user["roles"] else set()
        for perm in sorted(perms):
            if self._matches(perm, action, resource):
                return True, f"granted by {perm}"
        return False, "no matching permission"

    def check(self, user: dict, action: str, resource: dict) -> bool:
        allowed, reason = self._decide(user, action, resource)
        self.audit.append({"user_id": user["id"], "action": action, "tenant": resource.get("tenant"),
                           "allowed": allowed, "reason": reason})
        return allowed
