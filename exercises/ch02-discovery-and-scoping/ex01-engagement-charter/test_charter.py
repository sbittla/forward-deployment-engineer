NOTES = """
## Customer
Northwind Insurance

## Problem
Claims adjusters spend too long searching policy documents to answer coverage questions.

## Stakeholders
- Dana Ruiz — VP Claims (exec sponsor)
- Lee Park - Claims Ops Manager
- Priya Shah — IT Security Lead

## Success metrics
- Average handle time: 11 min -> 7 min
- First-contact resolution: 62 % -> 75 %
- Escalation backlog: 3.5 days -> 1 days
- Happier adjusters

## Constraints
- PII must not leave the customer VPC
- Go-live before Q3 renewal season

## Out of scope
- Automated claim approval
"""


def test_parse_sections(impl):
    c = impl.parse_notes(NOTES)
    assert c.customer == "Northwind Insurance"
    assert c.problem.startswith("Claims adjusters")
    assert ("Dana Ruiz", "VP Claims (exec sponsor)") in c.stakeholders
    assert ("Lee Park", "Claims Ops Manager") in c.stakeholders
    assert len(c.constraints) == 2 and c.out_of_scope == ["Automated claim approval"]


def test_parse_metrics(impl):
    c = impl.parse_notes(NOTES)
    m = {x.name: x for x in c.metrics}
    assert m["Average handle time"].baseline == 11 and m["Average handle time"].target == 7
    assert m["Average handle time"].unit == "min"
    assert m["Escalation backlog"].baseline == 3.5
    assert m["Happier adjusters"].baseline is None and m["Happier adjusters"].target is None


def test_validate_flags_unmeasurable_metric(impl):
    issues = impl.validate(impl.parse_notes(NOTES))
    assert len(issues) == 1 and "Happier adjusters" in issues[0] and "measurable" in issues[0]


def test_validate_missing_sponsor_problem_scope(impl):
    c = impl.Charter(customer="X", stakeholders=[("A", "Engineer")])
    issues = " | ".join(impl.validate(c)).lower()
    assert "problem" in issues and "sponsor" in issues and "out-of-scope" in issues


def test_render_table(impl):
    c = impl.parse_notes(NOTES)
    md = impl.render(c)
    assert "| Metric | Baseline | Target | Unit |" in md
    assert "| Average handle time | 11 | 7 | min |" in md
    assert "Northwind Insurance" in md
