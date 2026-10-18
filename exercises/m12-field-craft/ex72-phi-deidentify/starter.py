import re
from datetime import date

RESTRICTED_ZIP3 = {"036", "059", "102", "203", "556", "692", "790", "821", "823", "830", "831", "878", "879",
                   "884", "890", "893"}
ALLOWED_PURPOSES = {"treatment", "operations", "research-irb-approved"}


def deidentify(record: dict, today: date) -> dict:
    raise NotImplementedError


def apply_retention(records: list[dict], today: date, retention_days: int, legal_holds: set):
    raise NotImplementedError


def access_log_entry(user: str, purpose: str, record_ids: list, today: date) -> dict:
    raise NotImplementedError
