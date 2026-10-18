import re

import pytest

PACKAGE = "insights"

REQUIRED = {
    "analyst_guide.md": ["How to ask", "What it will not do", "Metric definitions", "Data freshness",
                         "When to escalate"],
    "exec_readout.md": ["Summary", "Results", "Controls", "Risks", "Next steps"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverable(cap_dir, name):
    text = (cap_dir / "deliverables" / name).read_text(encoding="utf-8")
    headings = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for section in REQUIRED[name]:
        assert any(section.lower() in h for h in headings), f"{name}: missing '{section}'"
    assert not re.search(r"TODO|TBD|FIXME", text)
    if name == "exec_readout.md":
        assert re.search(r"\d+(\.\d+)?%", text), "readout must report measured percentages"
