import re
from dataclasses import dataclass, field

VAGUE = {"fast", "faster", "better", "soon", "all", "real-time", "accurate", "easy", "scalable", "seamless", "smart"}

QUESTIONS = {
    "metric": "Which number should move, from what baseline to what target?",
    "users": "Who exactly will use this day to day?",
    "data": "What data or systems does the answer come from today?",
    "deadline": "Is there a date or business event this must be live for?",
    "volume": "Roughly how many requests per day or month?",
}

DEFAULT_ASSUMPTIONS = {
    "metric": "We will baseline average handle time in week 1 and target a 20% reduction.",
    "users": "Primary users are the internal support agents, not end customers.",
    "data": "Answers will be grounded in the existing help-center articles and resolved tickets.",
    "deadline": "Pilot readout in 6 weeks from kickoff.",
    "volume": "Design for 5,000 requests per day at pilot scale.",
}

MONTHS = "january february march april may june july august september october november december"
DIMENSIONS = {
    "metric": re.compile(r"\d+(\.\d+)?\s*(%|min\b|minutes\b|sec\b|seconds\b|hours\b|x\b)", re.I),
    "users": re.compile(r"\b(agents?|adjusters?|analysts?|customers?|team|reps?|users?)\b", re.I),
    "data": re.compile(r"\b(tickets?|documents?|pdfs?|database|crm|emails|logs)\b", re.I),
    "deadline": re.compile(r"\b(\d{4}-\d{2}-\d{2}|q[1-4]|" + "|".join(MONTHS.split()) + r")\b", re.I),
    "volume": re.compile(r"\d[\d,]*\s*(/day|per day|/month|per month|tickets|calls)", re.I),
}
VAGUE_RE = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, VAGUE), key=len, reverse=True)) + r")(?![\w-])", re.I)


@dataclass
class Analysis:
    vague_terms: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


def analyze(request: str) -> Analysis:
    a = Analysis()
    a.vague_terms = [m.group(1).lower() for m in VAGUE_RE.finditer(request)]
    a.missing = [dim for dim, rx in DIMENSIONS.items() if not rx.search(request)]
    a.questions = [QUESTIONS[d] for d in a.missing]
    a.questions += [f'What does "{t}" mean in measurable terms?' for t in a.vague_terms]
    a.assumptions = [DEFAULT_ASSUMPTIONS[d] for d in a.missing]
    return a
