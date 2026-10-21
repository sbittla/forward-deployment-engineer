import re
from dataclasses import dataclass, field
from pathlib import Path

from fde_kit import tokenize

NAME = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED = ("anthropic", "claude")


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
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, m.group(2)


def parse_skill(skill_dir) -> Skill:
    d = Path(skill_dir)
    meta, body = parse_frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
    name, desc = meta.get("name", ""), meta.get("description", "")
    if not NAME.match(name) or any(r in name for r in RESERVED):
        raise ValueError(f"invalid skill name {name!r}")
    if not 1 <= len(desc) <= 1024 or "<" in desc or ">" in desc:
        raise ValueError("description must be 1-1024 characters without XML tags")
    if not body.strip():
        raise ValueError("skill body is empty")
    resources = sorted(p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file() and p.name != "SKILL.md")
    return Skill(name, desc, body, resources)


class SkillRegistry:
    def __init__(self, root):
        self.root = Path(root)
        self.skills: dict[str, Skill] = {}
        self.dirs: dict[str, Path] = {}
        for d in sorted(p.parent for p in self.root.glob("*/SKILL.md")):
            s = parse_skill(d)
            if s.name in self.skills:
                raise ValueError(f"duplicate skill name {s.name!r}")
            self.skills[s.name], self.dirs[s.name] = s, d

    def metadata_prompt(self) -> str:
        return "\n".join(f"- {n}: {s.description}" for n, s in sorted(self.skills.items()))

    def select(self, task: str, k: int = 1) -> list[str]:
        q = set(tokenize(task))
        scored = [(len(q & set(tokenize(s.description))), n) for n, s in self.skills.items()]
        return [n for score, n in sorted(scored, key=lambda x: (-x[0], x[1])) if score > 0][:k]

    def load(self, name: str) -> str:
        return self.skills[name].body

    def read_resource(self, name: str, path: str) -> str:
        base = self.dirs[name].resolve()
        target = (base / path).resolve()
        if base not in target.parents:
            raise ValueError("resource path escapes the skill folder")
        return target.read_text(encoding="utf-8")


def parse_subagent(text: str) -> Subagent:
    meta, body = parse_frontmatter(text)
    tools = [t.strip() for t in meta["tools"].split(",") if t.strip()] if meta.get("tools") else None
    return Subagent(meta["name"], meta.get("description", ""), tools, meta.get("model") or None, body.strip())


def delegate(sub: Subagent, task: str, llm, available_tools: list[dict]) -> str:
    names = {t["name"] for t in available_tools}
    if sub.tools is not None:
        unknown = [t for t in sub.tools if t not in names]
        if unknown:
            raise ValueError(f"subagent {sub.name} requests unavailable tools: {unknown}")
        tools = [t for t in available_tools if t["name"] in sub.tools]
    else:
        tools = list(available_tools)
    # Fresh context: the subagent never sees the parent's conversation, and the parent only gets the result back.
    resp = llm.complete([{"role": "user", "content": task}], system=sub.system_prompt, tools=tools, model=sub.model)
    return resp.text
