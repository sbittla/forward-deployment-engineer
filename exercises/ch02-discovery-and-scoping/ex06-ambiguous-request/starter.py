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


@dataclass
class Analysis:
    vague_terms: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


def analyze(request: str) -> Analysis:
    raise NotImplementedError
