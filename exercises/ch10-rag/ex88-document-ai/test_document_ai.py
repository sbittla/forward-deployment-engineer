import base64

import pytest


def W(text, x0, y0, page=1, conf=0.99, w=None):
    return {"text": text, "page": page, "x0": x0, "y0": y0, "x1": x0 + (w or 8 * len(text)), "y1": y0 + 10, "conf": conf}


WORDS = [
    W("CLAIM", 50, 20), W("FORM", 110, 21),
    W("Policy", 50, 60), W("Number:", 110, 61), W("POL-882311", 180, 59, conf=0.97),
    W("Claimant", 50, 80), W("Name", 130, 80),
    W("Maria", 50, 96, conf=0.91), W("Lopez", 100, 95, conf=0.62),
    W("Date", 50, 120), W("of", 90, 121), W("Loss:", 110, 120), W("2026-10-03", 170, 120),
    W("Item", 50, 160), W("Qty", 200, 160), W("Amount", 300, 160),
    W("Laptop", 50, 180), W("1", 205, 181), W("1,299.00", 300, 180),
    W("Water", 50, 200), W("heater", 100, 200), W("1", 205, 201), W("850.00", 300, 200),
    W("Total", 250, 230), W("2,149.00", 300, 230),
    W("Page2", 50, 20, page=2),
]


def test_group_lines(impl):
    lines = impl.group_lines(WORDS)
    assert lines[0].text == "CLAIM FORM" and lines[0].page == 1
    pol = next(l for l in lines if l.text.startswith("Policy"))
    assert pol.text == "Policy Number: POL-882311" and pol.conf == 0.97
    assert next(l for l in lines if l.text.startswith("Maria")).conf == 0.62
    assert lines[-1].page == 2


def test_key_values(impl):
    kv = impl.key_values(impl.group_lines(WORDS), ["Policy Number", "Claimant Name", "Date of Loss", "Adjuster"])
    assert kv["Policy Number"] == ("POL-882311", 0.97)
    assert kv["Claimant Name"] == ("Maria Lopez", 0.62)
    assert kv["Date of Loss"][0] == "2026-10-03" and "Adjuster" not in kv


def test_table(impl):
    rows = impl.extract_table(WORDS, ["Item", "Qty", "Amount"], page=1)
    assert rows == [{"Item": "Laptop", "Qty": "1", "Amount": "1,299.00"},
                    {"Item": "Water heater", "Qty": "1", "Amount": "850.00"}]


def test_route(impl):
    kv = impl.key_values(impl.group_lines(WORDS), ["Policy Number", "Claimant Name", "Date of Loss", "Adjuster"])
    decision, reasons = impl.route(kv, ["Policy Number", "Claimant Name", "Adjuster"])
    assert decision == "human_review" and reasons == ["missing:Adjuster", "low_confidence:Claimant Name"]
    assert impl.route({"Policy Number": ("P", 0.99)}, ["Policy Number"]) == ("auto", [])


def test_vision_request(impl, tmp_path):
    pdf = tmp_path / "claim.pdf"
    pdf.write_bytes(b"%PDF-1.7 fake")
    content = impl.vision_request(pdf, "Extract the policy number.")
    assert content[0] == {"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                                         "data": base64.b64encode(b"%PDF-1.7 fake").decode()}}
    assert content[1] == {"type": "text", "text": "Extract the policy number."}
    png = tmp_path / "damage.PNG"
    png.write_bytes(b"\x89PNG")
    assert impl.vision_request(png, "q")[0]["source"]["media_type"] == "image/png"
    jpg = tmp_path / "x.jpeg"
    jpg.write_bytes(b"\xff\xd8")
    assert impl.vision_request(jpg, "q")[0]["type"] == "image" and impl.vision_request(jpg, "q")[0]["source"]["media_type"] == "image/jpeg"
    with pytest.raises(ValueError):
        impl.vision_request(tmp_path / "notes.docx", "q")


def test_vision_request_rejects_oversized_file(impl, tmp_path):
    big = tmp_path / "scan.pdf"
    with open(big, "wb") as f:
        f.truncate(32 * 1024 * 1024 + 1)  # sparse: one byte over the limit, nothing sent onward
    with pytest.raises(ValueError):
        impl.vision_request(big, "q")
    exact = tmp_path / "ok.pdf"
    with open(exact, "wb") as f:
        f.truncate(32 * 1024 * 1024)
    assert impl.vision_request(exact, "q")[0]["type"] == "document"
