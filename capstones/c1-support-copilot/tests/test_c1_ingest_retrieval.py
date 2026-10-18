PACKAGE = "copilot"


def test_chunks_keep_section_paths(cap, cap_data):
    chunks = cap.load_corpus(cap_data / "policies")
    by_id = {c.id: c for c in chunks}
    flood = by_id["homeowners#flood"]
    assert flood.doc_id == "homeowners" and flood.path == "Homeowners Policy HO-3 > Coverage > Flood"
    assert flood.text.startswith("Flood damage from rising surface water")
    assert "homeowners#coverage" not in by_id          # heading with no body of its own
    assert {c.doc_id for c in chunks} == {"homeowners", "auto", "claims-process"}
    assert len(chunks) == 14


def test_retrieval_ranks_the_right_section(cap, cap_data):
    r = cap.HybridRetriever(cap.load_corpus(cap_data / "policies"))
    assert r.search("burst pipe water damage", k=3)[0].chunk.id == "homeowners#water-damage"
    assert r.search("rental car per day", k=3)[0].chunk.id == "auto#rental-reimbursement"
    assert r.search("appeal a claim decision", k=3)[0].chunk.id == "claims-process#appeals"
    hits = r.search("cryptocurrency mining overheating", k=4)
    assert all(h.coverage < 0.4 for h in hits)


def test_coverage_definition(cap, cap_data):
    r = cap.HybridRetriever(cap.load_corpus(cap_data / "policies"))
    top = r.search("jewelry theft limited", k=1)[0]
    assert top.chunk.id == "homeowners#personal-property" and top.coverage == 1.0
