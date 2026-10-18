from dataclasses import dataclass, field

FIELDS = ("invoice_number", "invoice_date", "total", "vendor")


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
