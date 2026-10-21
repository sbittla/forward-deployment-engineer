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
    raise NotImplementedError


def load_principals(path) -> dict[str, Principal]:
    raise NotImplementedError


def can_read(principal, acl) -> bool:
    """Fail closed: no principal, no ACL, a different tenant or no shared group all mean no access."""
    raise NotImplementedError


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
        raise NotImplementedError

    def search(self, query: str, principal, k: int = 4) -> list:
        raise NotImplementedError
