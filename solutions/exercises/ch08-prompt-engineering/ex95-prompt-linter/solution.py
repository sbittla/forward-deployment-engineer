"""Static checks for prompt templates, run in CI before any eval spends tokens."""
import re
from dataclasses import dataclass

PLACEHOLDER = re.compile(r"(?<!\{)\{([a-z_][a-z0-9_]*)\}(?!\})")
UNTRUSTED_HINTS = ("document", "email", "ticket", "input", "message", "page", "transcript", "content", "comment")
EMPHASIS = re.compile(r"\b(CRITICAL|IMPORTANT|MUST|NEVER|ALWAYS|ABSOLUTELY)\b")
OUTPUT_FORMAT = re.compile(r"\b(json|xml|yaml|markdown|format|respond with|output|return only)\b", re.I)
DYNAMIC = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}:\d{2}\b")
CONCISE = re.compile(r"\b(concise|brief|short|terse)\b", re.I)
VERBOSE = re.compile(r"\b(detailed|comprehensive|exhaustive|thorough)\b", re.I)
SEVERITY_ORDER = {"error": 0, "warning": 1}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str


def placeholders(template: str) -> list[str]:
    seen: list[str] = []
    for name in PLACEHOLDER.findall(template):
        if name not in seen:
            seen.append(name)
    return seen


def _is_untrusted(name: str) -> bool:
    return any(h in name for h in UNTRUSTED_HINTS)


def _delimited(template: str, name: str) -> bool:
    return re.search(r"<([a-z_][a-z0-9_-]*)[^>]*>\s*\{" + re.escape(name) + r"\}\s*</\1>", template) is not None


def lint(system: str, template: str, variables: set[str], tools: list[dict] | None = None) -> list[Finding]:
    out: list[Finding] = []
    names = placeholders(template)
    if not system.strip():
        out.append(Finding("P001", "error", "system prompt is empty: state the role, audience and task context"))
    for name in names:
        if _is_untrusted(name) and not _delimited(template, name):
            out.append(Finding("P002", "error", f"untrusted input {{{name}}} is not wrapped in XML tags"))
    if not OUTPUT_FORMAT.search(system + "\n" + template):
        out.append(Finding("P003", "warning", "no output format specified"))
    shouted = EMPHASIS.findall(system + "\n" + template)
    if len(shouted) >= 3:
        out.append(Finding("P004", "warning",
                           f"{len(shouted)} all-caps emphasis words: modern models over-apply shouted rules; "
                           "explain why instead"))
    for name in names:
        if name not in variables:
            out.append(Finding("P005", "error", f"template uses {{{name}}} but no value is provided"))
    for name in sorted(variables - set(names)):
        out.append(Finding("P006", "warning", f"variable {name!r} is provided but never used"))
    for tool in tools or []:
        if len(tool.get("description", "").strip()) < 20:
            out.append(Finding("P007", "warning", f"tool {tool.get('name')!r} has a thin description"))
        for prop, schema in tool.get("input_schema", {}).get("properties", {}).items():
            if not schema.get("description"):
                out.append(Finding("P007", "warning", f"tool {tool.get('name')!r} parameter {prop!r} has no description"))
    if PLACEHOLDER.search(system) or DYNAMIC.search(system):
        out.append(Finding("P008", "warning", "dynamic content in the system prompt breaks prompt caching; "
                                              "move it to the user turn"))
    if CONCISE.search(system) and VERBOSE.search(system):
        out.append(Finding("P009", "warning", "system prompt asks for both brevity and exhaustive detail"))
    return sorted(out, key=lambda f: (SEVERITY_ORDER[f.severity], f.rule))


def score(findings: list[Finding]) -> int:
    errors = sum(f.severity == "error" for f in findings)
    warnings = len(findings) - errors
    return max(0, 10 - 3 * errors - warnings)


def render(template: str, values: dict) -> str:
    """Fill placeholders; refuse missing values rather than sending a literal '{name}' to the model."""
    missing = [n for n in placeholders(template) if n not in values]
    if missing:
        raise KeyError(f"missing values: {', '.join(missing)}")
    return PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), template)
