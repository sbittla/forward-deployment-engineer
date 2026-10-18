import re

import pytest

PACKAGE = "deliverylead"

REQUIRED = {
    "sow.md": ["Objectives", "In scope", "Out of scope", "Deliverables and acceptance criteria", "Timeline",
               "Assumptions", "Customer responsibilities", "Partner responsibilities", "Change control", "Estimate"],
    "partner_review_memo.md": ["Summary", "Findings", "Conditions for acceptance", "Re-review date"],
    "enablement_plan.md": ["Audiences", "Workshops", "Champions", "Knowledge-transfer exit criteria", "Adoption targets"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverable(cap_dir, name):
    text = (cap_dir / "deliverables" / name).read_text(encoding="utf-8")
    heads = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for s in REQUIRED[name]:
        assert any(s.lower() in h for h in heads), f"{name}: missing '{s}'"
    assert not re.search(r"TODO|TBD|FIXME", text)
    if name == "sow.md":
        assert re.search(r"P50", text) and re.search(r"P90", text) and "|" in text
    if name == "partner_review_memo.md":
        assert "D-fe-1" in text and re.search(r"\d{4}-\d{2}-\d{2}", text)
    if name == "enablement_plan.md":
        assert re.search(r"\d+%", text)
