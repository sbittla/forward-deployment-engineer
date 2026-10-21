"""A deterministic load model: replay cases against the copilot with simulated latency and real (fake-model) tokens.

Latency is *simulated* from a fixed model of the service: retrieval time on every policy question, plus a model call
priced in time by its tokens (time to first token, input processing, output generation). Cost is *computed* from the
tokens the model reported. Same inputs, same numbers, on any machine; a real load test (Section 14.3) replaces the
latency model with measurements.
"""
import math
from dataclasses import dataclass

from .evals import _case_passes


@dataclass(frozen=True)
class LatencyModel:
    routing_ms: float = 5.0
    retrieval_ms: float = 60.0
    first_token_ms: float = 400.0
    ms_per_1k_input_tokens: float = 40.0
    ms_per_output_token: float = 25.0


class _TimedLLM:
    def __init__(self, llm, model: LatencyModel):
        self.llm, self.model, self.elapsed_ms = llm, model, 0.0

    def __getattr__(self, name):
        return getattr(self.llm, name)

    def complete(self, messages, **kw):
        raise NotImplementedError


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (p in 0..100)."""
    raise NotImplementedError


def run_load(copilot, cases: list[dict], principal=None, repeats: int = 5,
             latency: LatencyModel = LatencyModel()) -> dict:
    """Replay `cases` `repeats` times; report latency percentiles and cost per successful answer."""
    raise NotImplementedError
