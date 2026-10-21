import hashlib
import json
from datetime import date

import pytest

DOC = """Intro text before headings.

# Policy
General terms apply to all insured parties.

## Coverage
Water damage from burst pipes is covered. Storm damage is covered up to the limit.

### Exclusions
Flood damage is excluded. Wear and tear is excluded.

## Claims
File within 30 days. Include photos.

# Appendix
Glossary.
"""


def test_fixed(impl):
    text = "abcdefghij" * 3
    chunks = impl.fixed_chunks(text, 12, 4)
    assert [c.start for c in chunks] == [0, 8, 16, 24]
    assert all(c.text == text[c.start:c.end] for c in chunks)
    assert chunks[-1].end == 30 and len(chunks[0].text) == 12
    with pytest.raises(ValueError):
        impl.fixed_chunks(text, 5, 5)


def test_recursive_invariants(impl):
    for max_chars in (40, 80, 200):
        chunks = impl.recursive_chunks(DOC, max_chars)
        assert "".join(c.text for c in chunks) == DOC
        assert all(0 < len(c.text) <= max_chars for c in chunks)
        assert all(DOC[c.start:c.end] == c.text for c in chunks)


def test_recursive_prefers_paragraphs(impl):
    chunks = impl.recursive_chunks(DOC, 120)
    assert any(c.text.startswith("### Exclusions") for c in chunks)
    assert not any("covered. St" in c.text and c.text.endswith("St") for c in chunks)


def test_recursive_hard_split(impl):
    chunks = impl.recursive_chunks("x" * 25, 10)
    assert [len(c.text) for c in chunks] == [10, 10, 5]


def test_heading_paths(impl):
    chunks = impl.heading_chunks(DOC)
    paths = [c.meta["path"] for c in chunks]
    assert paths == ["", "Policy", "Policy > Coverage", "Policy > Coverage > Exclusions", "Policy > Claims", "Appendix"]
    excl = chunks[3]
    assert excl.text.startswith("### Exclusions") and "Flood damage is excluded." in excl.text
    assert "File within" not in excl.text
    assert "".join(c.text for c in chunks) == DOC


def test_chunk_key(impl):
    expected = hashlib.sha256(json.dumps(["pol-7", "Policy > Coverage", "Flood is excluded.", 0]).encode()).hexdigest()
    assert impl.chunk_key("pol-7", "Policy > Coverage", "Flood is excluded.") == expected
    assert impl.chunk_key("pol-7", "Policy", "x") != impl.chunk_key("pol-8", "Policy", "x")
    assert impl.chunk_key("pol-7", "Policy", "x", 1) != impl.chunk_key("pol-7", "Policy", "x", 0)


def test_chunk_keys_distinguish_identical_chunks(impl):
    Chunk = impl.Chunk
    chunks = [Chunk("Sign here.", 0, 10, {"path": "Form"}), Chunk("Intro", 10, 15, {}),
              Chunk("Sign here.", 15, 25, {"path": "Form"})]
    keys = impl.chunk_keys("pol-7", chunks)
    assert keys == [impl.chunk_key("pol-7", "Form", "Sign here.", 0), impl.chunk_key("pol-7", "", "Intro", 0),
                    impl.chunk_key("pol-7", "Form", "Sign here.", 1)]
    to_add, _, _ = impl.plan_reindex("pol-7", {}, chunks)
    assert len(to_add) == 3


def test_plan_reindex_touches_only_changes(impl):
    old = impl.heading_chunks(DOC)
    current = {key: f"idx-{i}" for i, key in enumerate(impl.chunk_keys("pol-7", old))}
    new_doc = DOC.replace("File within 30 days.", "File within 14 days.")
    to_add, to_delete, to_update = impl.plan_reindex("pol-7", current, impl.heading_chunks(new_doc))
    assert [c.meta["path"] for c in to_add] == ["Policy > Claims"]
    assert "14 days" in to_add[0].text
    assert to_delete == ["idx-4"]
    assert [idx for idx, _ in to_update] == ["idx-0", "idx-1", "idx-2", "idx-3", "idx-5"]
    assert impl.plan_reindex("pol-7", current, old) == ([], [], [(f"idx-{i}", c) for i, c in enumerate(old)])


def test_plan_reindex_refreshes_moved_chunks(impl):
    # Text unchanged but shifted: no re-embedding, yet the index must get the new offsets and metadata.
    old = impl.heading_chunks(DOC)
    current = {key: f"idx-{i}" for i, key in enumerate(impl.chunk_keys("pol-7", old))}
    new = impl.heading_chunks(DOC.replace("Intro text", "Longer intro text"))
    for c in new:
        c.meta["effective_from"] = "2026-03-01"
    to_add, to_delete, to_update = impl.plan_reindex("pol-7", current, new)
    assert to_delete == ["idx-0"] and [c.text for c in to_add] == [new[0].text]
    appendix = dict(to_update)["idx-5"]
    assert appendix.start == old[5].start + len("Longer ") and DOC.replace("Intro text", "Longer intro text")[
        appendix.start:appendix.end] == appendix.text
    assert appendix.meta["effective_from"] == "2026-03-01"


def test_plan_reindex_document_removed(impl):
    current = {key: f"idx-{i}" for i, key in enumerate(impl.chunk_keys("pol-7", impl.heading_chunks(DOC)))}
    to_add, to_delete, to_update = impl.plan_reindex("pol-7", current, [])
    assert to_add == [] and to_update == [] and to_delete == [f"idx-{i}" for i in range(6)]
    added, _, _ = impl.plan_reindex("pol-7", {}, impl.fixed_chunks("abcdef", 4, 1))
    assert [c.text for c in added] == ["abcd", "def"]


def test_filter_effective(impl):
    Chunk = impl.Chunk
    chunks = [
        Chunk("v1 wording", 0, 10, {"effective_from": "2026-01-01", "effective_to": "2026-03-01"}),
        Chunk("v2 wording", 0, 10, {"effective_from": "2026-03-01"}),
        Chunk("glossary", 0, 8, {}),
    ]
    assert [c.text for c in impl.filter_effective(chunks, date(2026, 2, 14))] == ["v1 wording", "glossary"]
    assert [c.text for c in impl.filter_effective(chunks, date(2026, 3, 1))] == ["v2 wording", "glossary"]
    assert [c.text for c in impl.filter_effective(chunks, date(2025, 12, 31))] == ["glossary"]
