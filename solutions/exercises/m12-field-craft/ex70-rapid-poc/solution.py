import json
import re
from dataclasses import dataclass, field
from datetime import datetime

FIELDS = ("invoice_number", "invoice_date", "total", "vendor")

NUMBER = re.compile(r"(?i:\binvoice\s*(?:no\.?|number|#)|\binv\b\.?)\s*[:#]?\s*([A-Z0-9-]*\d[A-Z0-9-]*)")
DATE_LABEL = re.compile(r"(?i:\b(?:invoice\s+)?date)\s*:?\s*(.+)")
TOTAL = re.compile(r"(?i:(?<![a-z])total|amount\s+due|balance\s+due)\b[^\d\n]*?([\d][\d.,]*)")
DATE_SHAPES = [
    (re.compile(r"\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
    (re.compile(r"\d{2}/\d{2}/\d{4}"), "%d/%m/%Y"),
    (re.compile(r"[A-Z][a-z]{2} \d{1,2}, \d{4}"), "%b %d, %Y"),
    (re.compile(r"\d{1,2} [A-Z][a-z]+ \d{4}"), "%d %B %Y"),
]


@dataclass
class Extraction:
    fields: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)


def normalize_date(s: str) -> str | None:
    for rx, fmt in DATE_SHAPES:
        m = rx.search(s)
        if m:
            try:
                return datetime.strptime(m.group(0), fmt).date().isoformat()
            except ValueError:
                continue
    return None


def parse_amount(s: str) -> float | None:
    s = re.sub(r"[^\d.,]", "", str(s))
    if not s:
        return None
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
    elif "," in s:
        dec = "," if re.search(r",\d{2}$", s) else None
    else:
        dec = "."
    thousands = {",", "."} - {dec}
    for t in thousands:
        s = s.replace(t, "")
    if dec == ",":
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def rule_extract(text: str) -> dict:
    out = {}
    if m := NUMBER.search(text):
        out["invoice_number"] = m.group(1)
    for m in DATE_LABEL.finditer(text):
        if d := normalize_date(m.group(1)):
            out["invoice_date"] = d
            break
    if m := TOTAL.search(text):
        amount = parse_amount(m.group(1))
        if amount is not None:
            out["total"] = amount
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    if first and not first.lower().startswith("invoice"):
        out["vendor"] = first
    return out


def _normalize(name, value):
    if name == "invoice_date":
        return normalize_date(str(value))
    if name == "total":
        return parse_amount(value)
    return str(value).strip() or None


def extract(text: str, llm=None) -> Extraction:
    found = rule_extract(text)
    ex = Extraction(dict(found), {k: "rule" for k in found})
    missing = [f for f in FIELDS if f not in found]
    if missing and llm is not None:
        prompt = f"Fields: {', '.join(missing)}\n\n{text}"
        system = ("Extract the listed invoice fields. Reply with only a JSON object containing those keys; "
                  "omit a key if the invoice does not contain it.")
        reply = llm.complete([{"role": "user", "content": prompt}], system=system).text
        m = re.search(r"\{.*\}", reply, re.S)
        data = json.loads(m.group(0)) if m else {}
        for f in missing:
            if f in data and (v := _normalize(f, data[f])) is not None:
                ex.fields[f] = v
                ex.sources[f] = "llm"
    return ex


def _equal(a, b) -> bool:
    if isinstance(b, float):
        return isinstance(a, (int, float)) and abs(a - b) < 0.005
    return a == b


def evaluate(samples: list[str], gold: list[dict], llm=None) -> dict:
    correct = {f: 0 for f in FIELDS}
    llm_fields = 0
    for text, g in zip(samples, gold):
        ex = extract(text, llm)
        llm_fields += sum(1 for s in ex.sources.values() if s == "llm")
        for f in FIELDS:
            correct[f] += _equal(ex.fields.get(f), g[f])
    n = len(samples)
    out = {f: round(c / n, 4) for f, c in correct.items()}
    out["overall"] = round(sum(correct.values()) / (n * len(FIELDS)), 4)
    out["llm_fields"] = llm_fields
    return out


def poc_readout(metrics: dict) -> str:
    lines = ["| Field | Accuracy |", "|---|---|"]
    lines += [f"| {f} | {metrics[f]} |" for f in FIELDS]
    lines += ["", f"Overall: {metrics.get('overall')} · fields filled by the LLM: {metrics.get('llm_fields', 0)}",
              "", "## Next steps"]
    lines += [f"- Improve {f} extraction" for f in FIELDS if metrics[f] < 0.9]
    lines.append("- Run on 200 labelled invoices before any production decision")
    return "\n".join(lines) + "\n"
