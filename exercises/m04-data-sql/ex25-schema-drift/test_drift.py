import pytest

EXPECTED = {
    "claim_id": {"type": "str", "nullable": False},
    "amount": {"type": "int", "nullable": False},
    "filed_at": {"type": "datetime", "nullable": False},
    "adjuster": {"type": "str", "nullable": True},
    "fraud_flag": {"type": "bool", "nullable": False},
}
RECORDS = [
    {"claim_id": "C1", "amount": 100, "filed_at": "2026-10-01T10:00:00", "fraud_flag": False, "channel": "web"},
    {"claim_id": "C2", "amount": 250.5, "filed_at": "2026-10-02", "fraud_flag": "no", "channel": None},
    {"claim_id": "C3", "amount": 75, "filed_at": None, "fraud_flag": True, "channel": "phone"},
]


@pytest.mark.parametrize("v,t", [(None, "null"), (True, "bool"), (3, "int"), (3.5, "float"),
                                 ("2026-10-01T10:00:00", "datetime"), ("2026-10-01", "datetime"),
                                 ("hello", "str"), ("12", "str")])
def test_infer_type(impl, v, t):
    assert impl.infer_type(v) == t


def test_infer_schema(impl):
    s = impl.infer_schema(RECORDS)
    assert s["amount"] == {"type": "float", "nullable": False}
    assert s["filed_at"] == {"type": "datetime", "nullable": True}
    assert s["fraud_flag"] == {"type": "str", "nullable": False}
    assert s["channel"] == {"type": "str", "nullable": True}
    assert "adjuster" not in s


def test_diff(impl):
    changes = impl.diff(EXPECTED, impl.infer_schema(RECORDS))
    got = [(c.kind, c.column, c.detail, c.severity) for c in changes]
    assert got == [
        ("removed", "adjuster", "", "error"),
        ("type_changed", "amount", "int->float", "warn"),
        ("added", "channel", "str", "warn"),
        ("nullability_changed", "filed_at", "not null->nullable", "error"),
        ("type_changed", "fraud_flag", "bool->str", "error"),
    ]


def test_migration_sql(impl):
    obs = impl.infer_schema(RECORDS)
    sql = impl.migration_sql("claims", impl.diff(EXPECTED, obs), obs)
    assert "ALTER TABLE claims ADD COLUMN channel TEXT" in sql
    assert "-- manual: removed adjuster ()" in sql
    assert "-- manual: type_changed fraud_flag (bool->str)" in sql
    assert len(sql) == 5
