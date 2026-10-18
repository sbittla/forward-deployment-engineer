from datetime import date

TODAY = date(2026, 10, 16)


def T(title, due, status, owner="Lee", **kw):
    return dict(title=title, due=due, status=status, owner=owner, **kw)


def test_green(impl):
    tasks = [T("a", "2026-10-30", "in_progress"), T("b", "2026-10-01", "done", completed="2026-10-01")]
    assert impl.overall_status(tasks, TODAY) == "green"


def test_amber_blocked_far_out(impl):
    assert impl.overall_status([T("a", "2026-11-30", "blocked")], TODAY) == "amber"


def test_amber_one_overdue(impl):
    assert impl.overall_status([T("a", "2026-10-10", "in_progress")], TODAY) == "amber"


def test_red_blocked_soon(impl):
    assert impl.overall_status([T("a", "2026-10-20", "blocked")], TODAY) == "red"


def test_red_three_overdue(impl):
    tasks = [T(str(i), "2026-10-01", "not_started") for i in range(3)]
    assert impl.overall_status(tasks, TODAY) == "red"


def test_render(impl):
    tasks = [
        T("Index policy PDFs", "2026-10-14", "done", completed="2026-10-14"),
        T("Old thing", "2026-09-01", "done", completed="2026-09-01"),
        T("SSO integration", "2026-10-21", "blocked", owner="Priya", ask="Need IdP metadata from IT"),
        T("Eval set v1", "2026-10-25", "in_progress"),
        T("Load test", "2026-10-19", "not_started"),
        T("Exec readout", "2026-12-15", "not_started"),
    ]
    md = impl.render(tasks, TODAY, "Claims Copilot")
    lines = md.splitlines()
    assert lines[0] == "# Claims Copilot — status 2026-10-16"
    assert "**Overall: RED**" in md
    order = [md.index(h) for h in ("## Done this week", "## Next up", "## Risks & blockers", "## Asks")]
    assert order == sorted(order)
    done = md[md.index("## Done this week"):md.index("## Next up")]
    assert "Index policy PDFs" in done and "Old thing" not in done
    nxt = md[md.index("## Next up"):md.index("## Risks")]
    assert nxt.index("Load test") < nxt.index("SSO integration") < nxt.index("Eval set v1")
    assert "Exec readout" not in nxt
    risks = md[md.index("## Risks"):md.index("## Asks")]
    assert "SSO integration" in risks and "Priya" in risks
    assert "Need IdP metadata from IT" in md[md.index("## Asks"):]


def test_render_empty_sections(impl):
    md = impl.render([], TODAY, "P")
    assert md.count("- none") == 4
