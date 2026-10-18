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
    raise NotImplementedError


def answer(question: str, facts: dict):
    raise NotImplementedError


def security_gate(questions: list[str], facts: dict) -> dict:
    raise NotImplementedError
