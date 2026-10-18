from dataclasses import dataclass


@dataclass(frozen=True)
class Rendered:
    text: str
    name: str
    version: str
    sha: str


class PromptRegistry:
    def register(self, name: str, version: str, template: str) -> None:
        raise NotImplementedError

    def variables(self, name: str, version: str | None = None) -> set[str]:
        raise NotImplementedError

    def render(self, name: str, version: str | None = None, **vars) -> Rendered:
        raise NotImplementedError

    def diff(self, name: str, v1: str, v2: str) -> list[str]:
        raise NotImplementedError
