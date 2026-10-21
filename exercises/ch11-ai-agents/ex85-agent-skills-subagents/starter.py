from dataclasses import dataclass, field
from pathlib import Path

from fde_kit import tokenize


@dataclass
class Skill:
    name: str
    description: str
    body: str
    resources: list[str] = field(default_factory=list)


@dataclass
class Subagent:
    name: str
    description: str
    tools: list[str] | None
    model: str | None
    system_prompt: str


def parse_frontmatter(text: str) -> tuple[dict, str]:
    raise NotImplementedError


def parse_skill(skill_dir) -> Skill:
    raise NotImplementedError


class SkillRegistry:
    def __init__(self, root):
        self.root = Path(root)

    def metadata_prompt(self) -> str:
        raise NotImplementedError

    def select(self, task: str, k: int = 1) -> list[str]:
        raise NotImplementedError

    def load(self, name: str) -> str:
        raise NotImplementedError

    def read_resource(self, name: str, path: str) -> str:
        raise NotImplementedError


def parse_subagent(text: str) -> Subagent:
    raise NotImplementedError


def delegate(sub: Subagent, task: str, llm, available_tools: list[dict]) -> str:
    raise NotImplementedError
