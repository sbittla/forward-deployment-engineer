import re

import pytest

PACKAGE = "engagement"

REQUIRED = {
    "handoff_runbook.md": ["Overview", "Daily operation", "Red-flag list changes", "PHI incident response",
                           "Monitoring", "Escalation"],
    "product_feedback.md": ["Summary", "Requests", "Evidence"],
    "stakeholder_update.md": ["Status", "Done this week", "Next week", "Risks", "Asks"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverable(cap_dir, name):
    text = (cap_dir / "deliverables" / name).read_text(encoding="utf-8")
    headings = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for section in REQUIRED[name]:
        assert any(section.lower() in h for h in headings), f"{name}: missing '{section}'"
    assert not re.search(r"TODO|TBD|FIXME", text)
    if name == "stakeholder_update.md":
        assert re.search(r"\b(GREEN|AMBER|RED)\b", text), "status update needs a RAG status"
