"""Security questionnaire gate: auto-answer from system facts, route everything else to the security team."""
import re

RULES = {
    ("retain", "retention", "stored", "delet"): ("data_retention_days", "Customer content is retained for {value} days."),
    ("encrypt", "rest"): ("encryption_at_rest", "Encrypted at rest with {value}."),
    ("encrypt", "transit", "tls"): ("encryption_in_transit", "Encrypted in transit with {value}."),
    ("subprocessor", "third", "party"): ("subprocessors", "Subprocessors: {value}."),
    ("residency", "location", "region", "hosted"): ("data_residency", "Hosted in {value}."),
    ("train", "training", "model"): ("trains_on_customer_data", "Used for model training: {value}."),
    ("sso", "saml", "single", "sign"): ("sso", "SSO supported: {value}."),
    ("penetration", "pen", "test"): ("pen_test_date", "Last penetration test: {value}."),
}
ESCALATE = ("physical", "model risk", "mrm", "insurance", "background check")


def _fmt(v):
    return ("Yes" if v else "No") if isinstance(v, bool) else ", ".join(v) if isinstance(v, list) else str(v)


def answer(question: str, facts: dict):
    low = question.lower()
    if any(term in low for term in ESCALATE):
        return None                                  # always a human answer, whatever the keywords say
    words = re.findall(r"[a-z]+", low)
    best = None
    for keys, (fact, tpl) in RULES.items():
        hits = sum(any(w.startswith(k) for w in words) for k in keys)
        if hits and (best is None or hits / len(keys) > best[0]):
            best = (hits / len(keys), fact, tpl)
    if best is None or best[0] < 0.25:
        return None
    return best[2].format(value=_fmt(facts[best[1]]))


def security_gate(questions: list[str], facts: dict) -> dict:
    answered, open_items = {}, []
    for q in questions:
        a = answer(q, facts)
        if a is None:
            open_items.append(q)
        else:
            answered[q] = a
    return {"answered": answered, "open": open_items, "status": "open" if open_items else "clear"}
