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


def run_agent(llm, tools: dict[str, Tool], user_msg: str, system: str | None = None, max_steps: int = 8) -> AgentResult:
    raise NotImplementedError
