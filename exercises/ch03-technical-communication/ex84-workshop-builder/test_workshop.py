import pytest

OBJ = [
    {"id": "o1", "title": "How retrieval works", "concept_min": 20, "demo_min": 10, "lab_min": 40},
    {"id": "o2", "title": "Running the eval suite", "concept_min": 15, "demo_min": 10, "lab_min": 30},
    {"id": "o3", "title": "Deploy and roll back", "concept_min": 10, "demo_min": 10, "lab_min": 30},
]


def test_agenda(impl):
    a = impl.build_agenda(OBJ)
    assert a[:4] == [("09:00", "09:20", "concept", "o1"), ("09:20", "09:30", "demo", "o1"),
                     ("09:30", "10:10", "lab", "o1"), ("10:10", "10:15", "check", "o1")]
    # 75 min so far -> no break before o2; after o2 (135 min) a break
    assert a[4] == ("10:15", "10:30", "concept", "o2")
    assert a[8] == ("11:15", "11:30", "break", None)
    assert a[-1] == ("12:20", "12:25", "check", "o3")
    assert [x[2] for x in a].count("break") == 1


def test_agenda_validation(impl):
    with pytest.raises(ValueError):
        impl.build_agenda(OBJ, total_minutes=120)
    with pytest.raises(ValueError):
        impl.build_agenda([{**OBJ[0], "lab_min": 0}])


def test_lab_steps(impl):
    steps = [
        {"instruction": "Run the eval suite", "verify": "`pytest evals/` returns 12 passed"},
        {"instruction": "Open the dashboard", "verify": ""},
        {"instruction": "Roll back", "verify": "You should see revision 41 serving traffic"},
        {"instruction": "Think about it", "verify": "Understand the design"},
    ]
    assert impl.lab_steps_valid(steps) == [1, 3]


def test_readiness(impl):
    people = [
        {"name": "Lee", "quiz": {"o1": 0.9, "o2": 0.85, "o3": 0.6}, "labs_done": ["o1", "o2", "o3"]},
        {"name": "Ana", "quiz": {"o1": 1.0, "o2": 0.9, "o3": 0.95}, "labs_done": ["o1", "o2"]},
        {"name": "Sam", "quiz": {"o1": 0.8, "o2": 0.5, "o3": 0.9}, "labs_done": ["o1", "o3"]},
    ]
    r = impl.readiness(people, ["o1", "o2", "o3"])
    assert r["per_person"] == {"Lee": 0.67, "Ana": 0.67, "Sam": 0.67}
    assert r["uncovered"] == [] and r["can_operate_without_fde"] is False   # o3 only has Sam
    people[1]["labs_done"].append("o3")
    assert impl.readiness(people, ["o1", "o2", "o3"])["can_operate_without_fde"] is True
    r = impl.readiness(people[:1], ["o1", "o2", "o3"])
    assert r["uncovered"] == ["o3"]
