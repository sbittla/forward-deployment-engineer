import sys
import types

import pytest

SOURCE = '''
"""Claims connector for the policy admin system.

Longer description that should not appear in the summary.
"""
import json
from os import path

def search_claims(query: str, limit: int = 10) -> list:
    """Search claims by free text.

    Args:
        query (str): Text to match against claim
            titles and notes.
        limit: Maximum number of results.

    Returns:
        A list of claim dicts, newest first.
    """
    return []

def get_claim(claim_id):
    return None

def _helper():
    """private"""

class ClaimsClient:
    """HTTP client for the claims API."""

    def __init__(self, base_url: str, token: str = ""):
        self.base_url = base_url

    def fetch(self, claim_id):
        """Fetch one claim."""

    def update(self, claim_id, fields):
        pass

    def _sign(self):
        pass
'''


@pytest.fixture
def mod():
    m = types.ModuleType("claims_connector")
    sys.modules["claims_connector"] = m
    exec(SOURCE, m.__dict__)
    yield m
    del sys.modules["claims_connector"]


def test_public_api(impl, mod):
    assert impl.public_api(mod) == ["ClaimsClient", "get_claim", "search_claims"]
    mod.__all__ = ["search_claims"]
    assert impl.public_api(mod) == ["search_claims"]


def test_parse_docstring(impl, mod):
    d = impl.parse_google_docstring(mod.search_claims.__doc__)
    assert d["summary"] == "Search claims by free text."
    assert d["args"] == {"query": "Text to match against claim titles and notes.", "limit": "Maximum number of results."}
    assert d["returns"] == "A list of claim dicts, newest first."
    assert impl.parse_google_docstring(None) == {"summary": "", "args": {}, "returns": ""}


def test_render(impl, mod):
    md = impl.render_reference(mod)
    lines = md.splitlines()
    assert lines[0] == "# claims_connector"
    assert "Claims connector for the policy admin system." in md and "Longer description" not in md
    assert "## `search_claims(query: str, limit: int = 10) -> list`" in md
    assert "| query | Text to match against claim titles and notes. |" in md
    assert "**Returns:** A list of claim dicts, newest first." in md
    assert "## class `ClaimsClient(base_url: str, token: str = '')`" in md
    assert md.index("ClaimsClient") < md.index("get_claim") < md.index("search_claims(")


def test_missing_docs(impl, mod):
    assert impl.missing_docs(mod) == ["ClaimsClient.update", "get_claim"]
