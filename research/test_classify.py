"""Pins the false-positive fixes in classify.py and the published numbers in postings-index.csv.

Run: python -m pytest research -q
"""
import csv
from pathlib import Path

import analyze_index
from classify import build_index, classify, include_reason, strip_boilerplate

HERE = Path(__file__).parent


def test_job_title_does_not_count_as_production_deployment():
    assert classify("As a Forward Deployed Engineer you join our FDE team.")["R22"] == 0
    assert classify("You will take agents to production.")["R22"] == 1


def test_ownership_and_internship_are_not_shipping():
    assert classify("Ownership and partnership matter. This internship lasts 12 weeks.")["R22"] == 0


def test_architect_alone_is_not_distributed_systems():
    assert classify("Architecting solutions with customers.")["R28"] == 0
    assert classify("Experience with distributed systems.")["R28"] == 1


def test_deliver_alone_is_not_measurable_value():
    assert classify("Deliver great work for customers.")["R30"] == 0
    assert classify("Tie every deployment to measurable business impact and KPIs.")["R30"] == 1


def test_connector_is_not_mcp():
    assert classify("Build data connectors for Salesforce.")["R12"] == 0
    assert classify("Build MCP servers for internal tools.")["R12"] == 1


def test_interest_is_not_rest_and_enable_is_not_enablement():
    assert classify("Strong interest in customers; we enable teams.")["R05"] == 0
    assert classify("Strong interest in customers; we enable teams.")["R24"] == 0
    assert classify("Design REST APIs.")["R05"] == 1


def test_benefits_boilerplate_is_not_a_regulated_sector():
    text = "Benefits: medical, dental and vision insurance.\nHealthcare, paid leave and life insurance."
    assert classify(text)["R25"] == 0
    assert classify("You will work with healthcare providers.")["R25"] == 1


def test_office_policy_is_not_travel():
    text = "If the posting is specified as Onsite, you are required to work from an office."
    assert classify(text)["R26"] == 0
    assert classify("Travel to customer sites up to 25% of the time.")["R26"] == 1


def test_travel_software_is_an_industry_not_travel():
    assert classify("We sell travel software to airlines.")["R26"] == 0


def test_stripped_text_keeps_the_requirement_sentences():
    out = strip_boilerplate("Build pipelines in Python.\nWe offer 401(k) matching.")
    assert "Python" in out and "401" not in out


def test_exclusions():
    assert include_reason("jobgether", "Forward Deployed Engineer") == (False, "aggregator")
    assert include_reason("cursor", "RVP, Forward Deployed Engineering - EMEA")[0] is False
    assert include_reason("rogo", "Forward Deployed Banker")[0] is False
    assert include_reason("openai", "Forward Deployed Engineer - London") == (True, "")


def test_location_variants_are_one_role():
    posts = [dict(company="openai", title="Forward Deployed Engineer - London", location="London, UK", text="a"),
             dict(company="openai", title="Forward Deployed Engineer - Paris", location="Paris, France", text="b"),
             dict(company="openai", title="Forward Deployed Security Engineer", location="Washington, DC",
                  text="c")]
    rows = build_index(posts)
    assert [r["dedupe_group"] for r in rows] == [1, 1, 2]
    assert [r["representative"] for r in rows] == ["y", "n", "y"]


def test_published_index_reproduces_book_sample():
    with open(HERE / "postings-index.csv", encoding="utf-8", newline="") as f:
        a = analyze_index.analyze(list(csv.DictReader(f)))
    assert (a["collected"], a["roles"], a["companies"]) == (464, 157, 44)
    pct = {r["id"]: r["pct"] for r in a["requirements"]}
    assert (pct["R22"], pct["R28"], pct["R30"], pct["R25"], pct["R26"], pct["R12"]) == \
        (89.8, 48.4, 40.8, 35.7, 66.2, 6.4)


def test_published_index_reproduces_book_figures():
    """Every other posting figure cited in Chapters 1 and 17 (whole percentages as printed)."""
    with open(HERE / "postings-index.csv", encoding="utf-8", newline="") as f:
        a = analyze_index.analyze(list(csv.DictReader(f)))
    whole = {r["id"]: round(r["pct"] + 1e-9) for r in a["requirements"]}
    assert [whole[k] for k in ("R17", "R01", "R05", "R02", "R19", "R18", "R20", "R11", "R08", "R13", "R10",
                               "R14", "R23", "R24", "R43", "R34")] == \
        [73, 70, 67, 66, 93, 89, 86, 57, 43, 41, 26, 20, 75, 69, 25, 47]
    assert [round(a["extra"][k]["pct"]) for k in ("aws", "azure", "gcp")] == [36, 31, 29]
    assert dict(a["by_company"])["palantir"] == 37 and dict(a["by_company"])["anthropic"] == 2
    assert a["extra"]["clearance"]["count"] == 45 and dict(a["clearance_by_company"])["palantir"] == 28
    years = a["years_roles_per_figure"]
    assert sorted(years, key=years.get, reverse=True)[:3] == [5, 6, 2] and a["years_8_plus"] == 9
    assert a["travel_figure_stated"] == 77
    assert sum(20 <= t <= 50 for t in a["travel_max_figures"]) == 71
