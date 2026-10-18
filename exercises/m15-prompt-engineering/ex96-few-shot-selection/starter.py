"""Pick few-shot examples per query: relevant, diverse, label-balanced and within a token budget."""
from html import escape

from fde_kit.text import cosine, hash_embed

DUPLICATE_SIM = 0.95


def approx_tokens(example: dict) -> int:
    raise NotImplementedError


def select_examples(query: str, pool: list[dict], k: int = 3, lam: float = 0.7,
                    max_tokens: int | None = None) -> list[dict]:
    """Maximal marginal relevance with near-duplicate suppression and a token budget.

    Returned least relevant first, so the most relevant example sits closest to the query.
    """
    raise NotImplementedError


def ensure_label_coverage(selected: list[dict], pool: list[dict], labels: list[str], query: str) -> list[dict]:
    """Swap in the most relevant example for any label missing from `selected` (replacing the least relevant)."""
    raise NotImplementedError


def format_examples(examples: list[dict]) -> str:
    raise NotImplementedError


def build_messages(query: str, pool: list[dict], k: int = 3) -> list[dict]:
    raise NotImplementedError
