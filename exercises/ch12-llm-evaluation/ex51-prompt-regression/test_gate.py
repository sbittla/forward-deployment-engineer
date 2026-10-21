import json


def run(results):
    return {"run_id": "r", "results": {k: {"passed": p, "tags": t} for k, (p, t) in results.items()}}


BASE = run({f"c{i}": (True, []) for i in range(9)} | {"s1": (True, ["safety"]), "c9": (False, [])})


def test_pass_with_fix(impl):
    cand = run({f"c{i}": (True, []) for i in range(10)} | {"s1": (True, ["safety"])})
    g = impl.compare(BASE, cand)
    assert g.passed and g.fixes == ["c9"] and g.regressions == []
    assert g.base_rate == round(10 / 11, 4) and g.cand_rate == 1.0


def test_critical_regression_fails_even_if_rate_up(impl):
    cand = run({f"c{i}": (True, []) for i in range(10)} | {"s1": (False, ["safety"])})
    g = impl.compare(BASE, cand, max_drop=0.5)
    assert not g.passed and g.critical_regressions == ["s1"] and g.delta == 0.0


def test_rate_drop(impl):
    cand = run({f"c{i}": (i > 1, []) for i in range(10)} | {"s1": (True, ["safety"])})
    g = impl.compare(BASE, cand, max_drop=0.05)
    assert not g.passed and g.regressions == ["c0", "c1"]
    assert impl.compare(BASE, cand, max_drop=0.2).passed


def test_missing(impl):
    cand = run({f"c{i}": (True, []) for i in range(8)} | {"s1": (True, ["safety"])})
    g = impl.compare(BASE, cand, max_drop=1)
    assert not g.passed and g.missing == ["c8", "c9"]


def test_render(impl):
    cand = run({f"c{i}": (i != 3, []) for i in range(10)} | {"s1": (False, ["safety"])})
    md = impl.render(impl.compare(BASE, cand))
    lines = md.splitlines()
    assert lines[0] == "## Eval gate: FAIL"
    assert "Pass rate: 0.9091 -> 0.8182 (-0.0909)" in md
    assert "- s1 (critical)" in md and "- c3" in md and "- c9" in md
    assert md.count("- none") == 1


def test_main(impl, tmp_path, capsys):
    b, c = tmp_path / "b.json", tmp_path / "c.json"
    b.write_text(json.dumps(BASE))
    c.write_text(json.dumps(run({f"c{i}": (True, []) for i in range(10)} | {"s1": (True, ["safety"])})))
    assert impl.main([str(b), str(c)]) == 0
    assert "Eval gate: PASS" in capsys.readouterr().out
    c.write_text(json.dumps(run({f"c{i}": (False, []) for i in range(10)} | {"s1": (True, ["safety"])})))
    assert impl.main([str(b), str(c), "--max-drop", "0.05"]) == 1
