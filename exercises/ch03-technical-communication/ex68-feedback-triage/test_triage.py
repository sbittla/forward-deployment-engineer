ITEMS = [
    {"customer": "Acme", "text": "Need SSO login with Okta", "arr": 500_000, "severity": "major"},
    {"customer": "Globex", "text": "Export answers to PDF", "arr": 200_000, "severity": "minor"},
    {"customer": "Initech", "text": "Need SSO login with Azure AD", "arr": 1_200_000, "severity": "blocker"},
    {"customer": "Acme", "text": "Okta SSO login please", "arr": 500_000, "severity": "minor"},
    {"customer": "Hooli", "text": "Answers export to PDF format", "arr": 300_000, "severity": "major"},
    {"customer": "Umbrella", "text": "Dark mode", "arr": 50_000, "severity": "minor"},
]


def test_cluster(impl):
    assert impl.cluster(ITEMS) == [[0, 2, 3], [1, 4], [5]]


def test_score(impl):
    sso = [ITEMS[i] for i in (0, 2, 3)]
    # 2 customers -> 20 ; ARR 1.7M -> 17 ; severities 2+5+1 = 8
    assert impl.score(sso) == 45.0


def test_brief(impl):
    md = impl.brief(ITEMS, top=2)
    lines = md.splitlines()
    assert lines[0] == "# Field feedback brief"
    assert lines[1] == "## 1. Need SSO login with Okta"
    assert "- Customers: 2 (Acme, Initech)" in md
    assert "- ARR represented: $1,700,000" in md
    assert "- Severity: 1 blocker, 1 major, 1 minor" in md
    assert '> "Need SSO login with Azure AD" — Initech' in md
    assert "## 2. Export answers to PDF" in md
    assert "Dark mode" not in md


def test_empty_feedback(impl):
    assert impl.cluster([]) == [] and impl.brief([]).strip() == "# Field feedback brief"
