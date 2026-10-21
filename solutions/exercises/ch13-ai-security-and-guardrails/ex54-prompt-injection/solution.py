import re
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass
class Decision:
    allowed: bool
    needs_confirmation: bool
    reason: str


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
URL = re.compile(r"https?://[^\s\"'<>]+")

SIGNALS = [
    ("ignore_instructions", re.compile(
        r"\b(ignore|disregard|forget)\b[^.]{0,30}\b(previous|prior|above|earlier)\b[^.]{0,20}\b(instructions?|rules|prompts?)\b", re.I)),
    ("role_override", re.compile(r"\byou are now\b|\bact as\b|\bnew system prompt\b", re.I)),
    ("system_prompt_probe", re.compile(r"\bsystem prompt\b|\byour instructions\b", re.I)),
    ("exfiltration", re.compile(
        r"\b(send|forward|email|post|upload)\b[^.]{0,80}\bto\b\s+(\S+@\S+|https?://\S+)", re.I)),
    ("encoded_payload", re.compile(r"[A-Za-z0-9+/=]{40,}")),
]


def wrap_untrusted(content: str, source: str) -> str:
    safe = re.sub(r"<(/?untrusted)", r"&lt;\1", content, flags=re.I)
    return f'<untrusted source="{source.replace(chr(34), "&quot;")}">\n{safe}\n</untrusted>'


def injection_signals(text: str) -> list[str]:
    return [name for name, rx in SIGNALS if rx.search(text)]


class ToolGate:
    def __init__(self, side_effect_tools: set[str], allowed_domains: set[str]):
        self.side_effect_tools = side_effect_tools
        self.allowed_domains = allowed_domains

    def _allowed_host(self, host: str) -> bool:
        host = host.lower()
        return any(host == d or host.endswith("." + d) for d in self.allowed_domains)

    def _strings(self, obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for v in obj.values():
                yield from self._strings(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from self._strings(v)

    def authorize(self, tool: str, args: dict, tainted: bool) -> Decision:
        if tool not in self.side_effect_tools:
            return Decision(True, False, "read-only tool")
        for s in self._strings(args):
            for url in URL.findall(s):
                host = urlsplit(url).hostname or ""
                if not self._allowed_host(host):
                    return Decision(False, False, f"egress to {host} blocked")
            for domain in EMAIL.findall(s):
                if not self._allowed_host(domain):
                    return Decision(False, False, f"egress to {domain} blocked")
        if tainted:
            return Decision(True, True, "tainted context")
        return Decision(True, False, "ok")
