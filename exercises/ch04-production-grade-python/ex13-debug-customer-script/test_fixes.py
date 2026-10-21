from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest


def test_big_invoices_do_not_crash(impl):
    assert impl.parse_amount("1,234.50") == Decimal("1234.50")


def test_report_includes_the_last_page(impl):
    class Client:
        def get_page(self, page, size):
            return {"items": [f"p{page}"], "total_pages": 3}
    assert impl.fetch_all(Client()) == ["p1", "p2", "p3"]


def test_tags_do_not_leak_between_invoices(impl):
    a = impl.add_tag({"id": 1}, "urgent")
    b = impl.add_tag({"id": 2}, "disputed")
    assert a["tags"] == ["urgent"] and b["tags"] == ["disputed"]


def test_overdue_check_survives_the_eu_move(impl):
    now = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
    assert impl.is_overdue("2026-10-16T13:00:00+02:00", now=now) is True
    assert impl.is_overdue("2026-10-16T13:00:00", now=now) is False  # naive => UTC
    assert impl.is_overdue((datetime.now(timezone.utc) + timedelta(days=1)).isoformat()) is False


def test_totals_are_not_off_by_a_cent(impl):
    inv = [{"customer": "acme", "amount": "0.10"}] * 3 + [{"customer": "acme", "amount": "0.005"}]
    assert impl.total_by_customer(inv) == {"acme": Decimal("0.31")}
    assert impl.total_by_customer([{"customer": "x", "amount": "2.675"}]) == {"x": Decimal("2.68")}


def test_cleaning_paid_invoices_does_not_crash(impl):
    d = {1: {"paid": True}, 2: {"paid": False}, 3: {"paid": True}}
    assert impl.remove_paid(d) == {2: {"paid": False}}


def test_corrupted_config_is_not_silently_ignored(impl, tmp_path):
    bad = tmp_path / "cfg.json"
    bad.write_text("{not json")
    with pytest.raises(ValueError) as e:
        impl.load_config(str(bad))
    assert "cfg.json" in str(e.value)
    assert impl.load_config(str(tmp_path / "missing.json")) == {}


def test_fix_comments(exercise_dir):
    src = next(exercise_dir.glob("s*.py")).read_text()
    assert all(f"FIX({n})" in src for n in range(1, 8))
