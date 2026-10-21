import difflib
import hashlib
import re
from dataclasses import dataclass

VAR = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass(frozen=True)
class Rendered:
    text: str
    name: str
    version: str
    sha: str


def _semver(v: str) -> tuple[int, int, int]:
    major, minor, patch = (int(x) for x in v.split("."))
    return major, minor, patch


class PromptRegistry:
    def __init__(self):
        self._t: dict[str, dict[str, str]] = {}

    def register(self, name: str, version: str, template: str) -> None:
        _semver(version)  # validates format
        versions = self._t.setdefault(name, {})
        if version in versions and versions[version] != template:
            raise ValueError(f"{name}@{version} already registered with a different template; bump the version")
        versions[version] = template

    def _get(self, name, version):
        versions = self._t[name]
        version = version or max(versions, key=_semver)
        return version, versions[version]

    def variables(self, name: str, version: str | None = None) -> set[str]:
        return set(VAR.findall(self._get(name, version)[1]))

    def render(self, name: str, version: str | None = None, **vars) -> Rendered:
        version, template = self._get(name, version)
        needed = set(VAR.findall(template))
        missing = sorted(needed - vars.keys())
        if missing:
            raise KeyError(f"missing prompt variables: {', '.join(missing)}")
        extra = sorted(vars.keys() - needed)
        if extra:
            raise TypeError(f"unexpected prompt variables: {', '.join(extra)}")
        text = VAR.sub(lambda m: str(vars[m.group(1)]), template)
        return Rendered(text, name, version, hashlib.sha256(template.encode()).hexdigest()[:12])

    def diff(self, name: str, v1: str, v2: str) -> list[str]:
        a, b = self._t[name][v1].splitlines(), self._t[name][v2].splitlines()
        return list(difflib.unified_diff(a, b, fromfile=f"{name}@{v1}", tofile=f"{name}@{v2}", lineterm=""))
