PACKAGE = "engagement"


def test_voice_metrics(cap, calls):
    c2 = next(c for c in calls if c["call_id"] == "C2")
    m = cap.call_metrics(c2["events"])
    assert m["barge_ins"] == 1 and m["max_latency_s"] == 2.8 and m["duration_s"] == 17.9
    t = cap.caller_transcript(c2["events"]).splitlines()
    assert t[0].startswith("Agent: ") and t[1].startswith("Caller: John Carter here.")


def test_deidentify_removes_all_phi(cap, calls):
    c1 = calls[0]
    raw = cap.caller_transcript(c1["events"])
    safe, mapping = cap.deidentify(raw, [c1["patient_name"]])
    assert cap.phi_scan(raw, [c1["patient_name"]]) == ["MRN", "DATE", "PHONE", "NAME"]
    assert cap.phi_scan(safe, [c1["patient_name"]]) == []
    assert "fever and a cough" in safe and "[NAME_1]" in safe and "[MRN_1]" in safe
    assert set(mapping.values()) >= {"MRN 88231", "04/02/1981", "415-555-0100"}


def test_names_mentioned_by_agent_and_emails(cap, calls):
    c3, c4 = calls[2], calls[3]
    safe3, _ = cap.deidentify(cap.caller_transcript(c3["events"]), [c3["patient_name"]])
    assert "wei.zhang@example.com" not in safe3 and "[EMAIL_1]" in safe3 and "Zhang" not in safe3
    safe4, _ = cap.deidentify(cap.caller_transcript(c4["events"]), [c4["patient_name"]])
    assert "Grace" not in safe4 and "(773) 555-0123" not in safe4
