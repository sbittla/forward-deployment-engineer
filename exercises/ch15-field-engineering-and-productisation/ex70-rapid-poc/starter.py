from dataclasses import dataclass, field

FIELDS = ("invoice_number", "invoice_date", "total", "vendor")
EXIT_GATES = {"invoice_number": 0.95, "invoice_date": 0.95, "total": 0.97, "vendor": 0.90}


@dataclass
class Extraction:
    fields: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)


def rule_extract(text: str) -> dict:
    raise NotImplementedError


def extract(text: str, llm=None) -> Extraction:
    raise NotImplementedError


def evaluate(samples: list[str], gold: list[dict], llm=None) -> dict:
    raise NotImplementedError


def poc_readout(metrics: dict) -> str:
    raise NotImplementedError


def wilson_lower(p: float, n: int, z: float = 1.96) -> float:
    raise NotImplementedError


def exit_decision(metrics: dict, n: int, gates: dict = EXIT_GATES, min_n: int = 200) -> tuple[str, list[str]]:
    raise NotImplementedError
