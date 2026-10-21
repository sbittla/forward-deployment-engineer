import base64
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024
MEDIA = {".pdf": ("document", "application/pdf"), ".png": ("image", "image/png"), ".jpg": ("image", "image/jpeg"),
         ".jpeg": ("image", "image/jpeg"), ".gif": ("image", "image/gif"), ".webp": ("image", "image/webp")}


@dataclass
class Line:
    page: int
    y: float
    text: str
    conf: float


def _cy(w):
    return (w["y0"] + w["y1"]) / 2


def _cx(w):
    return (w["x0"] + w["x1"]) / 2


def _line_groups(words, y_tol):
    groups = []   # (page, center_y, [words])
    for w in sorted(words, key=lambda w: (w["page"], _cy(w), w["x0"])):
        for g in groups:
            if g[0] == w["page"] and abs(g[1] - _cy(w)) <= y_tol:
                g[2].append(w)
                break
        else:
            groups.append((w["page"], _cy(w), [w]))
    return sorted(groups, key=lambda g: (g[0], g[1]))


def group_lines(words: list[dict], y_tol: float = 5) -> list[Line]:
    out = []
    for page, y, ws in _line_groups(words, y_tol):
        ws = sorted(ws, key=lambda w: w["x0"])
        out.append(Line(page, round(y, 1), " ".join(w["text"] for w in ws), min(w["conf"] for w in ws)))
    return out


def key_values(lines: list[Line], labels: list[str]) -> dict:
    out = {}
    for label in labels:
        for i, line in enumerate(lines):
            if line.text.lower().startswith(label.lower()):
                value = line.text[len(label):].lstrip(" :#").strip()
                conf = line.conf
                if not value and i + 1 < len(lines) and lines[i + 1].page == line.page:
                    value, conf = lines[i + 1].text, lines[i + 1].conf
                if value:
                    out[label] = (value, conf)
                break
    return out


def extract_table(words: list[dict], headers: list[str], page: int) -> list[dict]:
    groups = [g for g in _line_groups([w for w in words if w["page"] == page], 5)]
    for idx, (_, _, ws) in enumerate(groups):
        texts = [w["text"] for w in ws]
        if all(h in texts for h in headers):
            starts = [next(w["x0"] for w in ws if w["text"] == h) for h in headers]
            break
    else:
        return []
    bounds = [(s, starts[i + 1] if i + 1 < len(starts) else float("inf")) for i, s in enumerate(starts)]
    rows = []
    for _, _, ws in groups[idx + 1:]:
        cells = {h: [] for h in headers}
        for w in sorted(ws, key=lambda w: w["x0"]):
            for h, (lo, hi) in zip(headers, bounds):
                if lo <= _cx(w) < hi:
                    cells[h].append(w["text"])
        if not cells[headers[0]]:
            break
        rows.append({h: " ".join(v) for h, v in cells.items()})
    return rows


def route(fields: dict, required: list[str], min_conf: float = 0.85) -> tuple[str, list[str]]:
    reasons = [f"missing:{r}" for r in required if r not in fields]
    reasons += [f"low_confidence:{k}" for k, (_, conf) in fields.items() if conf < min_conf]
    return ("human_review", reasons) if reasons else ("auto", [])


def vision_request(path, question: str) -> list[dict]:
    p = Path(path)
    kind = MEDIA.get(p.suffix.lower())
    if kind is None:
        raise ValueError(f"unsupported file type {p.suffix!r}")
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("file exceeds the 32 MB request limit")
    data = base64.b64encode(p.read_bytes()).decode()
    return [{"type": kind[0], "source": {"type": "base64", "media_type": kind[1], "data": data}},
            {"type": "text", "text": question}]
