from datetime import datetime, timezone

import pytest

ROWS = [
    {"Id": " 001A ", "AccountName": "Acme   Corp", "Phone": "(415) 555-0100",
     "CreatedDate": "2024-03-01T10:00:00.000+0000", "AnnualRevenue": "120,000,000"},
    {"Id": "001B", "AccountName": "Globex", "Phone": "", "CreatedDate": "2024-03-02T23:30:00.000-0500",
     "AnnualRevenue": ""},
    {"Id": "001C", "AccountName": "Initech", "Phone": "12345", "CreatedDate": "yesterday",
     "AnnualRevenue": "lots"},
    {"Id": "", "AccountName": "Hooli", "Phone": "+1 650 555 0199", "CreatedDate": "2024-01-01T00:00:00.000+0000",
     "AnnualRevenue": "15000000.0"},
    {"Id": "001E", "AccountName": "Umbrella", "Phone": "1-212-555-0142",
     "CreatedDate": "2024-01-05T08:00:00.000+0000", "AnnualRevenue": "2500000"},
]


def test_good_rows(impl):
    customers, _ = impl.map_records(ROWS)
    by = {c.id: c for c in customers}
    assert set(by) == {"001A", "001B", "001E"}
    a = by["001A"]
    assert a.name == "Acme Corp" and a.phone_e164 == "+14155550100"
    assert a.created_at == datetime(2024, 3, 1, 10, tzinfo=timezone.utc)
    assert a.annual_revenue == 120_000_000 and a.segment == "enterprise"
    b = by["001B"]
    assert b.phone_e164 is None and b.annual_revenue is None and b.segment == "unknown"
    assert b.created_at == datetime(2024, 3, 3, 4, 30, tzinfo=timezone.utc)
    assert by["001E"].phone_e164 == "+12125550142" and by["001E"].segment == "smb"


def test_errors_collected_per_field(impl):
    _, errors = impl.map_records(ROWS)
    row2 = {e.field for e in errors if e.row == 2}
    assert row2 == {"phone_e164", "created_at", "annual_revenue"}
    row3 = {e.field for e in errors if e.row == 3}
    assert row3 == {"id"}
    assert all(e.message for e in errors)


@pytest.mark.parametrize("raw", ["415.555.0100", "+1 415 555 0100", "4155550100", "1 (415) 555-0100"])
def test_phone_formats(impl, raw):
    row = dict(ROWS[0], Phone=raw)
    customers, errors = impl.map_records([row])
    assert errors == [] and customers[0].phone_e164 == "+14155550100"


def test_mid_market(impl):
    customers, _ = impl.map_records([dict(ROWS[0], AnnualRevenue="10000000")])
    assert customers[0].segment == "mid_market"
