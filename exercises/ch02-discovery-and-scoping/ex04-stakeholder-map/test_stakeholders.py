import pytest


@pytest.fixture
def people(impl):
    S = impl.Stakeholder
    return [
        S("Dana", "VP Claims", 5, 5, {"pilot": "A", "security": "I"}),
        S("Priya", "Security Lead", 4, 2, {"security": "A"}),
        S("Lee", "Ops Manager", 2, 5, {"pilot": "R"}),
        S("Sam", "Procurement", 2, 1, {}),
        S("Ana", "Legal", 4, 4, {"security": "C"}),
    ]


def test_quadrants(impl, people):
    q = {p.name: impl.quadrant(p) for p in people}
    assert q == {"Dana": "manage closely", "Priya": "keep satisfied", "Lee": "keep informed",
                 "Sam": "monitor", "Ana": "manage closely"}


def test_raci_missing_responsible(impl, people):
    issues = impl.validate_raci(people, ["pilot", "security"])
    assert len(issues) == 1 and "security" in issues[0] and "R" in issues[0]


def test_raci_two_accountable_unknown_letter_unknown_ws(impl, people):
    people[2].raci = {"pilot": "A", "security": "R", "legal": "R"}
    people[3].raci = {"pilot": "X"}
    issues = " | ".join(impl.validate_raci(people, ["pilot", "security"]))
    assert "pilot" in issues and "one A" in issues
    assert "'X'" in issues
    assert "legal" in issues


def test_comms_plan(impl, people):
    plan = impl.comms_plan(people)
    assert [p[0] for p in plan] == ["Dana", "Ana", "Priya", "Lee", "Sam"]
    assert plan[0] == ("Dana", "manage closely", "weekly", "1:1")
    assert plan[2] == ("Priya", "keep satisfied", "biweekly", "exec summary")
    assert plan[-1] == ("Sam", "monitor", "monthly", "newsletter")
