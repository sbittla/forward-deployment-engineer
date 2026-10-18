from datetime import date

import pytest

PACKAGE = "opsagent"
TODAY = date(2026, 10, 16)


@pytest.fixture
def store(cap, cap_data):
    return cap.OrderStore.from_json(cap_data / "orders.json")


def test_store(store):
    assert store.today == TODAY
    assert store.get_order("A100")["items"] == ["Ceramic mug set"]
    assert [o["order_id"] for o in store.orders_for("ana@example.com")] == ["A100", "A101", "A102", "A103"]
    assert store.refunded_total("A101") == 200.0 and store.refunded_total("A100") == 0
    rid = store.add_refund("A100", 10.0, "test", "auto-policy")
    assert rid == 2 and store.refunded_total("A100") == 10.0
    assert store.get_order("ZZZ") is None


@pytest.mark.parametrize("order_id,amount,expected", [
    ("A100", 45.0, (True, False)),
    ("A100", 46.0, (False, False)),          # above order total
    ("B200", 120.0, (True, True)),           # above auto limit -> approval
    ("A101", 100.0, (True, False)),          # remaining balance exactly
    ("A101", 100.01, (False, False)),        # over remaining balance
    ("A102", 10.0, (False, False)),          # outside window
    ("A103", 10.0, (False, False)),          # not delivered
])
def test_policy(cap, store, order_id, amount, expected):
    d = cap.RefundPolicy().evaluate(store.get_order(order_id), amount, store.refunded_total(order_id), store.today)
    assert (d.allowed, d.needs_approval) == expected and d.reason


def test_audit_chain(cap):
    log = cap.AuditLog()
    log.append("a", x=1)
    log.append("b", y=2)
    assert log.verify() and log.events() == ["a", "b"]
    log.entries[0]["data"]["x"] = 99
    assert not log.verify()
