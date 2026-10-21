from dataclasses import dataclass

HIGH_RISK_DOMAINS = {"employment", "credit_scoring", "education", "essential_services", "law_enforcement",
                     "migration", "critical_infrastructure", "biometrics", "insurance_pricing"}

# keyword group -> (fact key, answer template using {value})
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


@dataclass
class Answer:
    text: str
    source_fact: str | None
    confidence: float


def answer(question: str, facts: dict) -> Answer:
    raise NotImplementedError


def answer_all(questions: list[str], facts: dict, min_confidence: float = 0.5):
    raise NotImplementedError


def contradictions(claims: dict[str, str], facts: dict) -> list[str]:
    raise NotImplementedError


def regulatory_triage(use_case: dict) -> dict:
    raise NotImplementedError
