import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Tool:
    description: str
    input_schema: dict
    fn: Callable


@dataclass
class AgentResult:
    final_text: str
    steps: int
    messages: list = field(default_factory=list)


class AgentLoopError(Exception):
    pass


class BudgetExceeded(AgentLoopError):
    pass


class RepeatedCallError(AgentLoopError):
    pass


@dataclass
class RunBudget:
    max_steps: int = 8
    max_tokens: int = 200_000
    max_seconds: float = 120.0
    max_usd: float = 2.0
    steps: int = 0
    tokens: int = 0
    usd: float = 0.0

    def charge(self, tokens: int, usd: float, elapsed_s: float) -> None:
        raise NotImplementedError


def call_fingerprint(name: str, arguments: dict) -> str:
    raise NotImplementedError


def run_agent(llm, tools: dict[str, Tool], user_msg: str, system: str | None = None, max_steps: int = 8, *,
              budget: RunBudget | None = None, usd_per_mtok: tuple[float, float] = (0.0, 0.0),
              tool_caps: dict[str, int] | None = None, max_repeats: int = 3,
              clock: Callable[[], float] = time.monotonic) -> AgentResult:
    raise NotImplementedError
