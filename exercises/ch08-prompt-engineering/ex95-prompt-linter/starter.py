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
    raise NotImplementedError


def _is_untrusted(name: str) -> bool:
    raise NotImplementedError


def _delimited(template: str, name: str) -> bool:
    raise NotImplementedError


def lint(system: str, template: str, variables: set[str], tools: list[dict] | None = None) -> list[Finding]:
    raise NotImplementedError


def score(findings: list[Finding]) -> int:
    raise NotImplementedError


def render(template: str, values: dict) -> str:
    """Fill placeholders; refuse missing values rather than sending a literal '{name}' to the model."""
    raise NotImplementedError
