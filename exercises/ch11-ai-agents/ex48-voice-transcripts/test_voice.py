def ev(t, speaker, typ, text=None):
    e = {"t": t, "speaker": speaker, "type": typ}
    if text is not None:
        e["text"] = text
    return e


CALL = [
    ev(0.0, "agent", "start"), ev(0.5, "agent", "text", "Thanks for calling,"), ev(2.0, "agent", "text", "how can I help?"),
    ev(2.5, "agent", "end"),
    ev(3.0, "caller", "start"), ev(4.0, "caller", "text", "I need to reschedule"), ev(5.0, "caller", "end"),
    ev(5.2, "caller", "start"), ev(6.0, "caller", "text", "my appointment."), ev(6.5, "caller", "end"),
    ev(7.7, "agent", "start"), ev(8.0, "agent", "text", "Sure, what day works"), ev(12.0, "agent", "end"),
    ev(10.0, "caller", "start"), ev(10.5, "caller", "text", "Tuesday"), ev(11.0, "caller", "end"),
    ev(16.0, "agent", "start"), ev(17.0, "agent", "text", "Booked for Tuesday."), ev(18.0, "agent", "end"),
    ev(18.0, "caller", "end"),
]


def test_segments(impl):
    segs = impl.segments(CALL)
    assert [(s.speaker, s.start, s.end) for s in segs] == [
        ("agent", 0.0, 2.5), ("caller", 3.0, 5.0), ("caller", 5.2, 6.5), ("agent", 7.7, 12.0),
        ("caller", 10.0, 11.0), ("agent", 16.0, 18.0)]
    assert segs[0].text == "Thanks for calling, how can I help?"


def test_unclosed_segment(impl):
    segs = impl.segments([ev(0, "caller", "start"), ev(1, "caller", "text", "hello"), ev(4, "agent", "start")])
    assert (segs[0].end, segs[1].end) == (4, 4)


def test_turns_and_transcript(impl):
    t = impl.turns(impl.segments(CALL))
    assert [x.speaker for x in t] == ["agent", "caller", "agent", "caller", "agent"]
    assert t[1].text == "I need to reschedule my appointment."
    assert impl.to_transcript(t).splitlines()[1] == "Caller: I need to reschedule my appointment."


def test_latency_and_barge_in(impl):
    segs = impl.segments(CALL)
    assert impl.response_latencies(segs) == [1.2, 5.0]
    assert impl.barge_ins(segs) == [10.0]


def test_metrics(impl):
    m = impl.call_metrics(CALL, silence_threshold=3.0)
    assert m["latency_p50"] == 1.2 and m["latency_p95"] == 5.0
    assert m["barge_in_count"] == 1
    # agent talk 2.5 + 4.3 + 2 = 8.8 ; caller 2 + 1.3 + 1 = 4.3
    assert m["agent_talk_ratio"] == round(8.8 / 13.1, 3)
    assert m["long_silences"] == 1  # 11.0/12.0 -> 16.0 gap


def test_metrics_empty(impl):
    m = impl.call_metrics([ev(0, "agent", "start"), ev(1, "agent", "end")])
    assert m["latency_p50"] is None and m["barge_in_count"] == 0 and m["agent_talk_ratio"] == 1.0
