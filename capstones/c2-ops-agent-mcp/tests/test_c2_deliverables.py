import re

import pytest

PACKAGE = "opsagent"

REQUIRED = {
    "design_doc.md": ["Architecture", "Tool contracts", "Refund policy", "Security model", "Failure modes",
                      "Observability"],
    "runbook.md": ["Overview", "Deploy", "Rollback", "Approval queue", "Monitoring", "Escalation"],
    "product_feedback.md": ["Summary", "Requests", "Evidence"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverable(cap_dir, name):
    text = (cap_dir / "deliverables" / name).read_text(encoding="utf-8")
    headings = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for section in REQUIRED[name]:
        assert any(section.lower() in h for h in headings), f"{name}: missing '{section}'"
    assert not re.search(r"TODO|TBD|FIXME", text)
    if name == "product_feedback.md":
        assert len(re.findall(r"^\s*(?:\d+\.|-)\s+\*\*", text, re.M)) >= 3, "list at least 3 bolded requests"
