"""Assemble the copilot from the data directory: the v0 thin slice (deliberately failing) or the remediated build.

v0 is what the first demo ran: every document in one index with no ACLs, and no abstention threshold. It looks
fine on a happy-path demo. The gates in `golive.py` catch both of its defects (see the README's "v0 and its
remediation").
"""
from pathlib import Path

from .answer import Copilot
from .ingest import load_corpus
from .intent import IntentRouter
from .retrieval import HybridRetriever
from .tenancy import PermissionAwareRetriever, load_acl


def load_all_chunks(data_dir) -> list:
    raise NotImplementedError


def build_copilot(llm, data_dir, naive: bool = False) -> Copilot:
    raise NotImplementedError
