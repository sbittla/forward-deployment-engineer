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
    data_dir = Path(data_dir)
    return load_corpus(data_dir / "policies") + load_corpus(data_dir / "platform")


def build_copilot(llm, data_dir, naive: bool = False) -> Copilot:
    data_dir = Path(data_dir)
    chunks = load_all_chunks(data_dir)
    router = IntentRouter.from_jsonl(data_dir / "intents.jsonl")
    if naive:   # v0: one shared index, no permissions, answers whatever it retrieves
        return Copilot(llm, HybridRetriever(chunks), router, min_coverage=0.0)
    return Copilot(llm, PermissionAwareRetriever(chunks, load_acl(data_dir / "acl.json")), router)
