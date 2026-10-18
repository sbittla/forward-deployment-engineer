import re
from dataclasses import dataclass

HIGH_RISK_DOMAINS = {"employment", "credit_scoring", "education", "essential_services", "law_enforcement",
                     "migration", "critical_infrastructure", "biometrics", "insurance_pricing"}

RULES = {
    ("retain", "retention", "stored", "delet"): ("data_retention_days",
                                                   "Customer content is retained for {value} days, then deleted."),
    ("encrypt", "rest"): ("encryption_at_rest", "Data at rest is encrypted with {value}."),
    ("encrypt", "transit", "tls"): ("encryption_in_transit", "Data in transit is protected with {value}."),
    ("subprocessor", "third", "party"): ("subprocessors", "Subprocessors: {value}."),
    ("residency", "location", "region", "hosted"): ("data_residency", "Data is hosted in {value}."),
    ("train", "training", "model"): ("trains_on_customer_data", "Customer data used for model training: {value}."),
    ("sso", "saml", "single", "sign"): ("sso", "SSO (SAML/OIDC) supported: {value}."),
    ("penetration", "pen", "test"): ("pen_test_date", "Most recent third-party penetration test: {value}."),
    ("breach", "incident", "notify", "notification"): ("incident_notification_hours",
                                                      "Customers are notified of security incidents within {value} hours."),
}
NEEDS_REVIEW = "NEEDS SECURITY TEAM REVIEW"


@dataclass
class Answer:
    text: str
    source_fact: str | None
    confidence: float


def _fmt(value) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(value)
    return str(value)


def answer(question: str, facts: dict) -> Answer:
    words = set(re.findall(r"[a-z]+", question.lower()))
    best = None
    for keywords, (fact, template) in RULES.items():
        hits = sum(1 for k in keywords if any(w.startswith(k) for w in words))  # stems: retain~retained
        if hits and (best is None or hits / len(keywords) > best[0]):
            best = (hits / len(keywords), fact, template)
    if best is None:
        return Answer(NEEDS_REVIEW, None, 0.0)
    conf, fact, template = best
    return Answer(template.format(value=_fmt(facts[fact])), fact, round(conf, 2))


def answer_all(questions: list[str], facts: dict, min_confidence: float = 0.5):
    answers, queue = {}, []
    for i, q in enumerate(questions):
        a = answer(q, facts)
        if a.source_fact is not None and a.confidence >= min_confidence:
            answers[i] = a
        else:
            queue.append(i)
    return answers, queue


def contradictions(claims: dict[str, str], facts: dict) -> list[str]:
    bad = []
    for key, text in claims.items():
        t = text.lower()
        if re.search(r"\b(no|zero) (data )?retention|never store", t) and facts.get("data_retention_days", 0) > 0:
            bad.append(key)
        elif re.search(r"never train", t) and facts.get("trains_on_customer_data"):
            bad.append(key)
        elif re.search(r"\beu only\b|eu-only|in the eu only", t) and "EU" not in str(facts.get("data_residency", "")):
            bad.append(key)
    return sorted(bad)


def regulatory_triage(use_case: dict) -> dict:
    personal = use_case.get("personal_data", False)
    dpia = personal and (use_case.get("large_scale", False) or use_case.get("health_data", False)
                         or use_case.get("special_category", False) or use_case.get("systematic_monitoring", False))
    baa = use_case.get("health_data", False) and use_case.get("us_covered_entity", False)
    if use_case.get("social_scoring"):
        tier = "prohibited"
    elif use_case.get("domain") in HIGH_RISK_DOMAINS:
        tier = "high"
    elif use_case.get("chatbot") or use_case.get("generates_content"):
        tier = "limited"
    else:
        tier = "minimal"
    obligations = []
    if dpia:
        obligations.append("DPIA")
    if baa:
        obligations.append("BAA")
    if tier == "high":
        obligations.append("EU AI Act conformity assessment")
    if tier in ("high", "limited"):
        obligations.append("AI transparency notice")
    return {"gdpr_dpia_required": dpia, "hipaa_baa_required": baa, "eu_ai_act_tier": tier,
            "obligations": sorted(obligations)}
