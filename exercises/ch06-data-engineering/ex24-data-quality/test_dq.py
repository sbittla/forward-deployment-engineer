from datetime import datetime, timedelta

ROWS = [
    {"policy_number": "PN-0001", "premium": 1200, "state": "CA", "updated": "2026-10-15T08:00:00"},
    {"policy_number": "", "premium": 900, "state": "NY", "updated": "2026-10-15T09:00:00"},
    {"policy_number": "PN-0003", "premium": -5, "state": "TX", "updated": "2026-10-14T09:00:00"},
    {"policy_number": "PN-0003", "premium": None, "state": "ZZ", "updated": "2026-10-13T09:00:00"},
    {"policy_number": "pn-9", "premium": 150000, "state": "CA", "updated": "2026-10-12T09:00:00"},
]
NOW = datetime(2026, 10, 16, 8)


def by_name(report):
    return {r.name: r for r in report.results}


def test_row_checks(impl):
    rep = impl.run_checks(ROWS, [
        impl.not_null("policy_number"),
        impl.unique("policy_number"),
        impl.in_range("premium", 0, 100000),
        impl.matches("policy_number", r"PN-\d{4}"),
        impl.accepted_values("state", {"CA", "NY", "TX"}, severity="warn"),
    ])
    r = by_name(rep)
    assert r["not_null(policy_number)"].sample_rows == [1]
    assert r["unique(policy_number)"].sample_rows == [2, 3]
    assert r["in_range(premium,0,100000)"].sample_rows == [2, 4]
    assert r["matches(policy_number,PN-\\d{4})"].sample_rows == [1, 4]
    assert r["accepted_values(state)"].severity == "warn" and r["accepted_values(state)"].failed_count == 1
    assert rep.ok is False


def test_warn_only_does_not_block(impl):
    rep = impl.run_checks(ROWS, [impl.accepted_values("state", {"CA"}, severity="warn")])
    assert rep.ok is True and rep.results[0].passed is False


def test_dataset_checks(impl):
    rep = impl.run_checks(ROWS, [impl.row_count_between(1, 10), impl.fresh("updated", timedelta(hours=24), NOW)])
    assert rep.ok
    rep = impl.run_checks(ROWS, [impl.row_count_between(10, 20), impl.fresh("updated", timedelta(hours=12), NOW)])
    assert [x.passed for x in rep.results] == [False, False]
    assert rep.results[0].sample_rows == []


def test_sample_cap(impl):
    rows = [{"x": None}] * 12
    res = impl.run_checks(rows, [impl.not_null("x")]).results[0]
    assert res.failed_count == 12 and res.sample_rows == [0, 1, 2, 3, 4]


def test_markdown(impl):
    md = impl.run_checks(ROWS, [impl.not_null("policy_number"), impl.row_count_between(1, 10)]).to_markdown()
    assert md.splitlines()[0] == "| Check | Severity | Status | Failed |"
    assert "| not_null(policy_number) | error | FAIL | 1 |" in md
    assert "| row_count_between(1,10) | error | PASS | 0 |" in md


# Part B · pseudonymisation and data contracts

KEY = b"analytics-pseudonym-key"


def test_pseudonymise_is_keyed_and_stable(impl):
    import hashlib
    import hmac
    token = impl.pseudonymise("Ana@Example.com", KEY)
    assert token == hmac.new(KEY, b"ana@example.com", hashlib.sha256).hexdigest()[:32]
    assert impl.pseudonymise(" ana@example.com ", KEY) == token  # normalised before hashing
    assert impl.pseudonymise("Ana@Example.com", b"another-pseudonym-key") != token
    assert token != hashlib.sha256(b"ana@example.com").hexdigest()[:32]  # not a plain hash


CONTRACT = {
    "dataset": "claims.policies",
    "schema": {
        "policy_number": {"type": "string", "nullable": False, "pattern": r"PN-\d{4}"},
        "premium": {"type": "decimal", "range": [0, 100000]},
        "state": {"type": "string", "values": ["CA", "NY", "TX"]},
    },
    "checks_blocking": ["not_null(policy_number)", "unique(policy_number)"],
}


def test_checks_from_contract(impl):
    checks = impl.checks_from_contract(CONTRACT)
    assert [(c.name, c.severity) for c in checks] == [
        ("not_null(policy_number)", "error"),
        (r"matches(policy_number,PN-\d{4})", "warn"),
        ("in_range(premium,0,100000)", "warn"),
        ("accepted_values(state)", "warn"),
        ("unique(policy_number)", "error"),
    ]
    r = by_name(impl.run_checks(ROWS, checks))
    assert r["unique(policy_number)"].sample_rows == [2, 3]
    clean = [row for row in ROWS if row["policy_number"] == "PN-0001"]
    assert impl.run_checks(clean, checks).ok is True


def test_contract_rejects_unknown_blocking_check(impl):
    import pytest
    bad = {**CONTRACT, "checks_blocking": ["row_count_between(1,10)"]}
    with pytest.raises(ValueError, match="unknown blocking check: row_count_between"):
        impl.checks_from_contract(bad)


def test_pseudonymise_rejects_weak_key(impl):
    # Fail closed: a missing or short key would make tokens a plain, dictionary-attackable hash.
    import pytest
    for key in (b"", b"short", None):
        with pytest.raises(ValueError, match="key must be at least 16 bytes"):
            impl.pseudonymise("ana@example.com", key)
