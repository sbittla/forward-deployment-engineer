import re
from datetime import date, timedelta

RESTRICTED_ZIP3 = {"036", "059", "102", "203", "556", "692", "790", "821", "823", "830", "831", "878", "879",
                   "884", "890", "893"}
ALLOWED_PURPOSES = {"treatment", "operations", "research-irb-approved"}

DROP = ("patient_name", "mrn", "phone", "email", "dob", "zip", "visit_date")
MRN = re.compile(r"MRN[:#\s]*\d+", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")


def _age(dob: date, today: date) -> int:
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _scrub_note(note: str, name: str) -> str:
    # Structured identifiers first, so an email like maria@... is caught whole before name scrubbing.
    note = MRN.sub("[MRN]", note)
    note = EMAIL.sub("[EMAIL]", note)
    note = DATE.sub("[DATE]", note)  # before phones: dates look like digit runs
    note = PHONE.sub("[PHONE]", note)
    for part in sorted(set(name.split()), key=len, reverse=True):
        note = re.sub(rf"\b{re.escape(part)}\b", "[NAME]", note, flags=re.I)
    return note


def deidentify(record: dict, today: date) -> dict:
    out = {k: v for k, v in record.items() if k not in DROP}
    dob = date.fromisoformat(record["dob"])
    age = _age(dob, today)
    if age >= 90:
        out["birth_year"], out["age_group"] = None, "90+"
    else:
        decade = age // 10 * 10
        out["birth_year"], out["age_group"] = dob.year, f"{decade}-{decade + 9}"
    zip3 = record["zip"][:3]
    out["zip3"] = "000" if zip3 in RESTRICTED_ZIP3 else zip3
    out["visit_year"] = date.fromisoformat(record["visit_date"]).year
    out["note"] = _scrub_note(record["note"], record["patient_name"])
    return out


def apply_retention(records: list[dict], today: date, retention_days: int, legal_holds: set):
    cutoff = today - timedelta(days=retention_days)
    kept, purged = [], []
    for r in records:
        if date.fromisoformat(r["created"]) < cutoff and r["id"] not in legal_holds:
            purged.append(r["id"])
        else:
            kept.append(r)
    return kept, sorted(purged)


def access_log_entry(user: str, purpose: str, record_ids: list, today: date) -> dict:
    if not isinstance(user, str) or not user.strip():
        raise ValueError("every access needs an identified user")
    if purpose not in ALLOWED_PURPOSES:
        raise ValueError(f"purpose {purpose!r} is not an allowed use of this data")
    return {"user": user, "purpose": purpose, "record_count": len(record_ids), "date": today.isoformat()}
