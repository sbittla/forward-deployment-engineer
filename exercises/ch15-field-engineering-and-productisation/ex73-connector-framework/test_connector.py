import pytest

ACME = {"name": "acme", "fields": {
    "case_id": {"path": "Id", "required": True},
    "subject": {"path": "Subject", "transforms": ["strip"]},
    "priority": {"path": "Priority__c", "transforms": ["lower", "map:p1=urgent,p2=high,p3=normal"], "default": "normal"},
    "opened": {"path": "Created.When", "transforms": ["date_iso"]},
    "account": {"path": "Account.Name"}}}
GLOBEX = {"name": "globex", "fields": {
    "case_id": {"path": "ticket.number", "required": True, "transforms": ["upper"]},
    "subject": {"path": "ticket.title"},
    "priority": {"path": "ticket.sev", "transforms": ["int", "sev_to_priority"]},
    "opened": {"path": "ticket.created_epoch", "transforms": ["date_iso"]},
    "account": {"path": "org.contacts[0].company"}}}
INITECH = {"name": "initech", "fields": {
    "case_id": {"path": "case", "required": True},
    "subject": {"path": "summary", "transforms": ["strip"]},
    "priority": {"path": "prio", "default": "normal"},
    "opened": {"path": "date", "transforms": ["date_iso"]},
    "account": {"path": "customer"}}}

EXPECTED = {"case_id": "C-1", "subject": "Login broken", "priority": "urgent", "opened": "2026-10-01", "account": "Acme Corp"}


@pytest.fixture(autouse=True)
def custom(impl):
    impl.register_transform("sev_to_priority", lambda v: {1: "urgent", 2: "high"}.get(v, "normal"))


def test_three_customers_same_canonical_output(impl):
    a = impl.Connector.from_config(ACME).transform(
        {"Id": "C-1", "Subject": "  Login broken ", "Priority__c": "P1", "Created": {"When": "2026-10-01T09:30:00Z"},
         "Account": {"Name": "Acme Corp"}})
    g = impl.Connector.from_config(GLOBEX).transform(
        {"ticket": {"number": "c-1", "title": "Login broken", "sev": "1", "created_epoch": 1790847000},
         "org": {"contacts": [{"company": "Acme Corp"}]}})
    i = impl.Connector.from_config(INITECH).transform(
        {"case": "C-1", "summary": "Login broken\n", "prio": "urgent", "date": "10/01/2026", "customer": "Acme Corp"})
    assert a == g == i == EXPECTED


def test_defaults_and_passthrough(impl):
    c = impl.Connector.from_config(ACME)
    out = c.transform({"Id": "C-2", "Priority__c": "P9"})
    assert out["priority"] == "p9" and out["subject"] is None and out["account"] is None
    assert c.transform({"Id": "C-3"})["priority"] == "normal"


def test_run_collects_errors(impl):
    rows, errors = impl.Connector.from_config(ACME).run([{"Id": "A"}, {"Subject": "no id"}, {"Id": "B"}])
    assert [r["case_id"] for r in rows] == ["A", "B"]
    assert errors == [(1, "case_id", "required field missing")]


@pytest.mark.parametrize("cfg", [
    {"fields": {}},
    {"name": "x"},
    {"name": "x", "fields": {"a": {}}},
    {"name": "x", "fields": {"a": {"path": "a", "transforms": ["teleport"]}}},
])
def test_config_validation(impl, cfg):
    with pytest.raises(ValueError):
        impl.Connector.from_config(cfg)
