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
