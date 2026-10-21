FACTS = {"data_retention_days": 30, "encryption_at_rest": "AES-256", "encryption_in_transit": "TLS 1.2+",
         "subprocessors": ["Anthropic", "AWS"], "data_residency": "EU (Frankfurt)", "trains_on_customer_data": False,
         "sso": True, "pen_test_date": "2026-08-14", "incident_notification_hours": 72,
         "processes_personal_data": True, "processes_health_data": False}


def test_answers(impl):
    a = impl.answer("How long is customer data retained before deletion?", FACTS)
    assert a.text == "Customer content is retained for 30 days, then deleted." and a.source_fact == "data_retention_days"
    assert a.confidence == 0.5
    a = impl.answer("Is data encrypted at rest?", FACTS)
    assert a.text == "Data at rest is encrypted with AES-256." and a.confidence == 1.0
    a = impl.answer("List all subprocessors and third party providers", FACTS)
    assert a.text == "Subprocessors: Anthropic, AWS."
    assert impl.answer("Is customer data used for model training?", FACTS).text.endswith(": No.")
    assert impl.answer("Do you support SAML single sign-on?", FACTS).text == "SSO (SAML/OIDC) supported: Yes."


def test_unknown_goes_to_humans(impl):
    a = impl.answer("Describe your physical badge access policy", FACTS)
    assert a.text == "NEEDS SECURITY TEAM REVIEW" and a.source_fact is None and a.confidence == 0.0


def test_answer_all(impl):
    qs = ["Is data encrypted at rest?", "Where is data hosted?", "Badge policy?", "Is data stored?"]
    answers, queue = impl.answer_all(qs, FACTS, min_confidence=0.5)
    assert set(answers) == {0} and queue == [1, 2, 3]
    answers, queue = impl.answer_all(qs, FACTS, min_confidence=0.25)
    assert set(answers) == {0, 1, 3} and queue == [2]


def test_contradictions(impl):
    claims = {"deck-p4": "Zero retention: we never store your prompts.",
              "faq-2": "We never train on your data.",
              "site": "Hosted in the EU only.",
              "blog": "Enterprise-grade security."}
    assert impl.contradictions(claims, FACTS) == ["deck-p4"]
    assert impl.contradictions(claims, {**FACTS, "trains_on_customer_data": True, "data_residency": "US"}) == [
        "deck-p4", "faq-2", "site"]


def test_regulatory_triage(impl):
    r = impl.regulatory_triage({"personal_data": True, "large_scale": True, "health_data": True, "us_covered_entity": True,
                                "domain": "healthcare", "chatbot": True})
    assert r["gdpr_dpia_required"] and r["hipaa_baa_required"] and r["eu_ai_act_tier"] == "limited"
    assert r["obligations"] == ["AI transparency notice", "BAA", "DPIA"]
    r = impl.regulatory_triage({"personal_data": True, "domain": "credit_scoring"})
    assert r["eu_ai_act_tier"] == "high" and not r["gdpr_dpia_required"]
    assert r["obligations"] == ["AI transparency notice", "EU AI Act conformity assessment"]
    assert impl.regulatory_triage({"social_scoring": True})["eu_ai_act_tier"] == "prohibited"
    assert impl.regulatory_triage({"domain": "logistics"}) == {"gdpr_dpia_required": False, "hipaa_baa_required": False,
                                                              "eu_ai_act_tier": "minimal", "obligations": []}
