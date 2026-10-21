"""Permission-aware retrieval: tenant and group ACLs applied before ranking, failing closed.

Every document carries an ACL copied from the source system at ingestion (`data/acl.json` stands in for the policy
archive's export metadata). A principal sees a chunk only when the chunk's document has an ACL, the tenants match and
the principal belongs to one of the ACL's groups. A missing ACL, a missing principal or an unknown tenant means no
access: the copilot then abstains instead of searching everything.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from .retrieval import HybridRetriever


@dataclass(frozen=True)
class Principal:
    user: str
    tenant: str
    groups: frozenset


@dataclass(frozen=True)
class Acl:
    tenant: str
    groups: frozenset


def load_acl(path) -> dict[str, Acl]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {doc: Acl(v["tenant"], frozenset(v["groups"])) for doc, v in raw.items()}


def load_principals(path) -> dict[str, Principal]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {name: Principal(v["user"], v["tenant"], frozenset(v["groups"])) for name, v in raw.items()}


def can_read(principal, acl) -> bool:
    """Fail closed: no principal, no ACL, a different tenant or no shared group all mean no access."""
    if principal is None or acl is None or not principal.tenant:
        return False
    return principal.tenant == acl.tenant and bool(principal.groups & acl.groups)


class PermissionAwareRetriever:
    """Filters chunks by ACL *before* ranking, with one index per permission set.

    Filtering first (rather than dropping forbidden hits after ranking) means another tenant's documents can't
    crowd out allowed ones, and their term statistics don't shape this tenant's scores.
    """
    permission_aware = True

    def __init__(self, chunks, acl: dict[str, Acl], **retriever_kw):
        self.chunks, self.acl, self.retriever_kw = list(chunks), acl, retriever_kw
        self._indexes: dict[tuple, HybridRetriever] = {}

    def visible_chunks(self, principal) -> list:
        return [c for c in self.chunks if can_read(principal, self.acl.get(c.doc_id))]

    def search(self, query: str, principal, k: int = 4) -> list:
        if principal is None:
            return []
        key = (principal.tenant, principal.groups)
        if key not in self._indexes:
            self._indexes[key] = HybridRetriever(self.visible_chunks(principal), **self.retriever_kw)
        hits = self._indexes[key].search(query, k)
        # defense in depth: re-check every hit, so a stale cached index can never return a forbidden chunk
        return [h for h in hits if can_read(principal, self.acl.get(h.chunk.doc_id))]
