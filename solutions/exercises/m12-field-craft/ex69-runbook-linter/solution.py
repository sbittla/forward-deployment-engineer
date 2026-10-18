import re

REQUIRED = ("Overview", "Prerequisites", "Deploy", "Rollback", "Monitoring", "Escalation")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
VAR = re.compile(r"<([A-Z_]+)>")


def lint_runbook(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    line_issues, doc_issues = [], []
    in_code = False
    prev_level = 0
    sections: dict[str, dict] = {}   # required name -> {"code": bool, "text": str}
    current = None
    prose: list[str] = []
    code_vars: list[str] = []

    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                line_issues.append(f"L{n}: code-lang")
            if not in_code and current:
                sections[current]["code"] = True
            in_code = not in_code
            continue
        if in_code:
            code_vars += [v for v in VAR.findall(line) if v not in code_vars]
            continue
        prose.append(line)
        if re.search(r"TODO|TBD|FIXME", line):
            line_issues.append(f"L{n}: placeholder")
        m = HEADING.match(line)
        if m:
            level = len(m.group(1))
            if prev_level and level > prev_level + 1:
                line_issues.append(f"L{n}: heading-skip")
            prev_level = level
            title = m.group(2).lower()
            current = next((r for r in REQUIRED if r.lower() in title), None)
            if current:
                sections.setdefault(current, {"code": False, "text": ""})
            continue
        if current:
            sections[current]["text"] += line + "\n"

    doc_issues += [f"missing-section:{r}" for r in REQUIRED if r not in sections]
    if "Rollback" in sections and not sections["Rollback"]["code"]:
        doc_issues.append("rollback-command")
    if "Escalation" in sections:
        text = sections["Escalation"]["text"]
        if not EMAIL.search(text) and not PHONE.search(text):
            doc_issues.append("escalation-contact")
    prose_text = "\n".join(prose)
    doc_issues += [f"undocumented-variable:{v}" for v in code_vars if not re.search(rf"\b{v}\b", prose_text)]
    return line_issues + doc_issues
