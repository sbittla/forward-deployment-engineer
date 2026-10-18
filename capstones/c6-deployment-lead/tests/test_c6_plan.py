import copy

import pytest

PACKAGE = "deliverylead"


@pytest.fixture
def eng(cap, cap_data):
    return cap.load_json(cap_data / "engagement.json")


def test_baseline(cap, eng):
    assert cap.critical_path(eng["tasks"]) == ["discovery", "landing-zone", "ingest", "agent-evals", "go-live"]
    assert cap.estimate(eng["tasks"]) == (23.3, 26.3)
    s = cap.schedule(eng["tasks"])
    assert s["ui"]["slack"] > 0 and s["ingest"]["slack"] == 0


def test_forecast_and_slip(cap, eng):
    assert cap.forecast(eng) == {"baseline_finish_day": 23.3, "forecast_finish_day": 24.8, "slip_days": 1.5}
    late = copy.deepcopy(eng)
    late["progress"]["ingest"] = 0.0
    late["as_of_day"] = 20
    assert cap.forecast(late)["slip_days"] > 10


def test_rag(cap, eng):
    rag = cap.workstream_rag(eng)
    assert {ws: r["rag"] for ws, r in rag.items()} == {"platform": "amber", "data": "amber", "agent": "amber",
                                                       "frontend": "green", "enablement": "green"}
    assert rag["agent"]["variance"] == -0.145


def test_cycle_rejected(cap):
    with pytest.raises(ValueError):
        cap.schedule([{"id": "a", "o": 1, "m": 1, "p": 1, "deps": ["b"]}, {"id": "b", "o": 1, "m": 1, "p": 1, "deps": ["a"]}])
