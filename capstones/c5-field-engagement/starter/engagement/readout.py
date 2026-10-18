"""Board-ready readout generated from the charter, measured results and the value model."""
from .discovery import assumptions_for
from .voice import p95


def render_readout(charter, metrics: dict, results, value: dict) -> str:
    raise NotImplementedError
