import operator

import pytest


def build(impl, interrupt=()):
    g = impl.StateGraph(reducers={"log": operator.add})
    g.add_node("classify", lambda s: {"intent": "refund" if "refund" in s["text"] else "faq", "log": ["classify"]})
    g.add_node("faq", lambda s: {"answer": "See our FAQ.", "log": ["faq"]})
    g.add_node("draft_refund", lambda s: {"answer": f"Refund of ${s['amount']} drafted.", "log": ["draft"]})
    g.add_node("issue_refund", lambda s: {"issued": s.get("approved", False), "log": ["issue"]})
    g.set_entry_point("classify")
    g.add_conditional_edges("classify", lambda s: "draft_refund" if s["intent"] == "refund" else "faq")
    g.add_edge("faq", impl.END)
    g.add_edge("draft_refund", "issue_refund")
    g.add_edge("issue_refund", impl.END)
    cp = impl.MemoryCheckpointer()
    return g.compile(checkpointer=cp, interrupt_before=interrupt), cp


def test_simple_path_and_reducer(impl):
    app, _ = build(impl)
    r = app.invoke({"text": "how do I reset my password", "log": []})
    assert r.status == "done" and r.state["answer"] == "See our FAQ." and r.state["log"] == ["classify", "faq"]
    assert r.steps == 2


def test_interrupt_and_resume_with_checkpoints(impl):
    app, cp = build(impl, interrupt=("issue_refund",))
    r = app.invoke({"text": "refund please", "amount": 40, "log": []}, thread_id="t1")
    assert r.status == "interrupted" and r.next == "issue_refund" and "issued" not in r.state
    assert cp.latest("t1")["next"] == "issue_refund"
    r2 = app.resume("t1", {"approved": True, "log": ["human-approved"]})
    assert r2.status == "done" and r2.state["issued"] is True
    assert r2.state["log"] == ["classify", "draft", "human-approved", "issue"]
    nexts = [c["next"] for c in cp.history("t1")]
    assert nexts == ["draft_refund", "issue_refund", "issue_refund", impl.END]


def test_validation(impl):
    g = impl.StateGraph()
    with pytest.raises(ValueError):
        g.compile()                                  # no entry point
    g.add_node("a", lambda s: {})
    g.set_entry_point("a")
    with pytest.raises(ValueError):
        g.compile()                                  # a has no outgoing edge
    g.add_edge("a", "ghost")
    with pytest.raises(ValueError):
        g.compile()                                  # unknown node
    g2 = impl.StateGraph()
    for n in ("a", "b", "orphan"):
        g2.add_node(n, lambda s: {})
    g2.set_entry_point("a")
    g2.add_edge("a", "b")
    g2.add_edge("b", impl.END)
    g2.add_edge("orphan", impl.END)
    with pytest.raises(ValueError):
        g2.compile()                                 # orphan unreachable
    g3 = impl.StateGraph()
    g3.add_node("a", lambda s: {})
    g3.set_entry_point("a")
    g3.add_edge("a", impl.END)
    g3.add_conditional_edges("a", lambda s: impl.END)
    with pytest.raises(ValueError):
        g3.compile()                                 # both edge kinds on one node


def test_max_steps(impl):
    g = impl.StateGraph(reducers={"n": operator.add})
    g.add_node("loop", lambda s: {"n": 1})
    g.set_entry_point("loop")
    g.add_conditional_edges("loop", lambda s: "loop")
    with pytest.raises(RuntimeError):
        g.compile(max_steps=5).invoke({"n": 0})
