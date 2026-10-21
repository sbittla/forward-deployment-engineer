from datetime import date

import pytest

TODAY = date(2026, 10, 16)
REC = {
    "patient_name": "Maria Lopez", "dob": "1981-04-02", "mrn": "88231", "zip": "94110",
    "phone": "415-555-0100", "email": "maria@example.com", "visit_date": "2026-09-30",
    "note": "Maria Lopez (MRN 88231) seen 09/30/2026 for asthma. Ms. lopez reports cough since 2026-09-20. "
            "Callback 415-555-0100 or maria@example.com. Lopezville clinic referral.",
}


def test_deidentify(impl):
    out = impl.deidentify(REC, TODAY)
    for k in ("patient_name", "mrn", "phone", "email", "dob", "zip", "visit_date"):
        assert k not in out
    assert out["birth_year"] == 1981 and out["age_group"] == "40-49"
    assert out["zip3"] == "941" and out["visit_year"] == 2026
    note = out["note"]
    assert "Maria" not in note and "Lopez " not in note and "lopez" not in note
    assert note.startswith("[NAME] [NAME] ([MRN]) seen [DATE]")
    assert "[PHONE]" in note and "[EMAIL]" in note and note.count("[DATE]") == 2
    assert "Lopezville" in note  # whole words only
    assert REC["patient_name"] == "Maria Lopez"  # input not mutated


def test_elderly_and_restricted_zip(impl):
    out = impl.deidentify({**REC, "dob": "1935-01-01", "zip": "03601"}, TODAY)
    assert out["birth_year"] is None and out["age_group"] == "90+" and out["zip3"] == "000"
    out = impl.deidentify({**REC, "dob": "1936-10-17"}, TODAY)  # 89 until tomorrow
    assert out["age_group"] == "80-89" and out["birth_year"] == 1936


def test_retention(impl):
    recs = [{"id": "a", "created": "2019-01-01"}, {"id": "b", "created": "2026-01-01"},
            {"id": "c", "created": "2018-06-01"}, {"id": "d", "created": "2020-10-17"}]
    kept, purged = impl.apply_retention(recs, TODAY, retention_days=6 * 365, legal_holds={"c"})
    assert purged == ["a"] and [r["id"] for r in kept] == ["b", "c", "d"]


def test_access_log(impl):
    e = impl.access_log_entry("dr.k", "treatment", ["a", "b"], TODAY)
    assert e == {"user": "dr.k", "purpose": "treatment", "record_count": 2, "date": "2026-10-16"}
    with pytest.raises(ValueError):
        impl.access_log_entry("analyst", "curiosity", ["a"], TODAY)


def test_access_log_fails_closed(impl):
    for user in ("", "   ", None):
        with pytest.raises(ValueError):
            impl.access_log_entry(user, "treatment", ["a"], TODAY)      # anonymous access is refused
    with pytest.raises(ValueError):
        impl.access_log_entry("dr.k", "Treatment ", ["a"], TODAY)       # purposes match exactly
    e = impl.access_log_entry("dr.k", "operations", [REC["mrn"]], TODAY)
    assert set(e) == {"user", "purpose", "record_count", "date"} and REC["mrn"] not in str(e)


def test_boundary_other_names_not_scrubbed(impl):
    # Documented limit of the teaching subset: only the patient's own name parts are replaced.
    note = "Maria Lopez seen by Dr. Chen; her son Daniel will call back."
    out = impl.deidentify({**REC, "note": note}, TODAY)
    assert out["note"] == "[NAME] [NAME] seen by Dr. Chen; her son Daniel will call back."
