"""Build stage: permission-aware retrieval that fails closed; incremental ingestion with a blocking quality check."""
import importlib

PACKAGE = "copilot"


def _platform(cap, cap_data):
    tenancy = importlib.import_module("copilot.tenancy")
    chunks = cap.load_corpus(cap_data / "policies") + cap.load_corpus(cap_data / "platform")
    retriever = tenancy.PermissionAwareRetriever(chunks, tenancy.load_acl(cap_data / "acl.json"))
    return tenancy, retriever, tenancy.load_principals(cap_data / "principals.json")


def test_cross_tenant_chunks_never_retrieved(cap, cap_data):
    tenancy, r, who = _platform(cap, cap_data)
    northwind = {"homeowners", "auto", "claims-process"}
    for query in ("boats stored in a marina", "marina fire marine deductible", "burst pipe water damage"):
        assert all(h.chunk.doc_id in northwind for h in r.search(query, who["adjuster"]))
        assert all(h.chunk.doc_id == "harbor-marine" for h in r.search(query, who["harbor_adjuster"]))
    assert r.search("boats stored in a marina", who["harbor_adjuster"])[0].chunk.id == "harbor-marine#boat-storage"
    # a Northwind investigator's extra group doesn't cross the tenant line
    assert all(h.chunk.doc_id != "harbor-marine" for h in r.search("marina fire", who["investigator"]))


def test_restricted_groups_and_missing_acl_fail_closed(cap, cap_data):
    tenancy, r, who = _platform(cap, cap_data)
    q = "fraud referral indicators special investigations"
    assert all(h.chunk.doc_id != "siu-referrals" for h in r.search(q, who["adjuster"]))
    assert r.search(q, who["investigator"])[0].chunk.doc_id == "siu-referrals"
    # draft-bulletin has no ACL entry: invisible to everyone, including supervisors and investigators
    for name in ("adjuster", "supervisor", "investigator"):
        assert all(h.chunk.doc_id != "draft-bulletin" for h in r.search("coastal deductible 2027 draft", who[name]))
    assert not tenancy.can_read(who["adjuster"], None)
    assert not tenancy.can_read(None, tenancy.Acl("northwind", frozenset({"claims"})))
    stranger = tenancy.Principal("u-x", "unknown-tenant", frozenset({"claims"}))
    assert r.search("burst pipe water damage", stranger) == []


def test_copilot_without_principal_fails_closed(cap, cap_data, llm):
    tenancy, r, who = _platform(cap, cap_data)
    c = cap.Copilot(llm, r, cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl"))
    q = "Is water damage from a burst pipe covered?"
    assert c.ask(q).abstained and llm.calls == []           # no principal: nothing retrieved, model never called
    r1 = c.ask(q, principal=who["adjuster"])
    assert not r1.abstained and r1.citations == ["homeowners"]
    assert c.ask("Are boats stored in a marina covered?", principal=who["adjuster"]).abstained


def test_incremental_sync_reindexes_only_changes(cap, cap_data, tmp_path):
    ingest = importlib.import_module("copilot.ingest")
    for p in (cap_data / "policies").glob("*.md"):
        (tmp_path / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    state, report = ingest.sync_corpus(tmp_path)
    assert sorted(report["added"]) == ["auto", "claims-process", "homeowners"] and len(ingest.chunks_of(state)) == 14
    state2, report2 = ingest.sync_corpus(tmp_path, state)
    assert report2["added"] == report2["changed"] == [] and sorted(report2["unchanged"]) == sorted(report["added"])
    assert state2["auto"][1] is state["auto"][1]               # unchanged documents aren't re-chunked
    (tmp_path / "auto.md").write_text("# Auto Policy\n\n## Towing\nTowing is covered up to 15 miles.\n", "utf-8")
    (tmp_path / "claims-process.md").unlink()
    state3, report3 = ingest.sync_corpus(tmp_path, state2)
    assert report3["changed"] == ["auto"] and report3["removed"] == ["claims-process"]
    assert [c.id for c in state3["auto"][1]] == ["auto#towing"] and "claims-process" not in state3


def test_sync_blocks_empty_document_and_keeps_previous(cap, cap_data, tmp_path):
    ingest = importlib.import_module("copilot.ingest")
    source = (cap_data / "policies" / "homeowners.md").read_text(encoding="utf-8")
    (tmp_path / "homeowners.md").write_text(source, encoding="utf-8")
    state, _ = ingest.sync_corpus(tmp_path)
    (tmp_path / "homeowners.md").write_text("# Homeowners Policy HO-3\n\n## Coverage\n", "utf-8")  # broken export
    state2, report = ingest.sync_corpus(tmp_path, state)
    assert report["blocked"] == ["homeowners"] and report["changed"] == []
    assert state2["homeowners"] == state["homeowners"]         # the previous version keeps serving
