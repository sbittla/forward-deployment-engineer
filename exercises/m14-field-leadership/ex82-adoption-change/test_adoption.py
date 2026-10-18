def E(user, team, event, week):
    return {"user": user, "team": team, "event": event, "week": week}


EVENTS = (
    [E(u, "claims-east", "invited", 1) for u in ("a", "b", "c", "d")]
    + [E(u, "claims-west", "invited", 1) for u in ("e", "f", "g", "h")]
    + [E(u, "subrogation", "invited", 1) for u in ("i", "j")]
    + [E("a", "claims-east", "login", 1), E("a", "claims-east", "query", 1), E("a", "claims-east", "query", 2),
       E("a", "claims-east", "query", 3),
       E("b", "claims-east", "login", 1), E("b", "claims-east", "query", 1), E("b", "claims-east", "login", 3),
       E("c", "claims-east", "login", 2), E("c", "claims-east", "query", 2),
       E("e", "claims-west", "login", 1),
       E("i", "subrogation", "login", 2), E("i", "subrogation", "query", 2), E("i", "subrogation", "query", 3),
       E("i", "subrogation", "query", 4)]
)


def test_funnel(impl):
    f = impl.funnel(EVENTS)
    assert f == {"invited": 10, "activated": 5, "engaged": 4, "habitual": 2, "activation_rate": 0.5, "habit_rate": 0.2}


def test_retention(impl):
    # week-1 cohort: a, b, e -> week1 3/3, week2 a 1/3, week3 a,b 2/3, week4 none
    assert impl.weekly_retention(EVENTS, 1) == [1.0, 0.333, 0.667, 0.0]


def test_lagging_and_plan(impl):
    lag = impl.lagging_teams(EVENTS)
    assert lag == [("claims-west", 0.25)]
    lag = impl.lagging_teams(EVENTS, threshold=0.9)
    assert lag == [("claims-west", 0.25), ("subrogation", 0.5), ("claims-east", 0.75)]
    plan = impl.change_plan([("claims-west", 0.2), ("subrogation", 0.5)])
    assert plan == ["claims-west: executive sponsor message + hands-on workshop + named champion",
                    "subrogation: champion office hours + in-app tips"]


def test_diff_in_diff(impl):
    r = impl.diff_in_diff([11, 12, 10], [8, 9, 7], [11, 11, 11], [10.5, 10, 10.5])
    assert r == {"treatment_change": -3.0, "control_change": -0.67, "effect": -2.33, "effect_pct": -21.21}
