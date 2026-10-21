import re
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass
class Decision:
    allowed: bool
    needs_confirmation: bool
    reason: str


# Destinations in the arguments of side-effect tools, matched case-insensitively and tried in this order. Anything
# that looks like a place to send data counts as egress; the gate denies it unless its host is allowlisted.
URL = re.compile(r"[a-z][a-z0-9+.-]*://[^\s\"'<>]*|(?<![\w:/])//[^\s\"'<>]+", re.I)  # any scheme, or scheme-relative
EMAIL = re.compile(r"[^\s\"'<>@/]+@(\[[^\]\s]+\]|[^\s\"'<>/@,;]+)")                 # user@host, user@[ip]
IPV6 = re.compile(r"\[([0-9a-f]*:[0-9a-f:.]*)\]", re.I)                            # bracketed IPv6 literal
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
DOMAIN = re.compile(r"(?<![\w.-])(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}(?![\w-])", re.I)  # bare host

SIGNALS = [
    ("ignore_instructions", re.compile(
        r"\b(ignore|disregard|forget)\b[^.]{0,30}\b(previous|prior|above|earlier)\b[^.]{0,20}\b(instructions?|rules|prompts?)\b", re.I)),
    ("role_override", re.compile(r"\byou are now\b|\bact as\b|\bnew system prompt\b", re.I)),
    ("system_prompt_probe", re.compile(r"\bsystem prompt\b|\byour instructions\b", re.I)),
    ("exfiltration", re.compile(
        r"\b(send|forward|email|post|upload)\b[^.]{0,80}\bto\b\s+(\S+@\S+|https?://\S+)", re.I)),
    ("encoded_payload", re.compile(r"[A-Za-z0-9+/=]{40,}")),
]


def _host(raw: str) -> str:
    return raw.strip("[]").rstrip(".").lower()


def _url_host(url: str) -> str:
    try:
        return _host(urlsplit(url if "://" in url else "x:" + url).hostname or "")
    except ValueError:                                  # e.g. an unbalanced bracket: unparsable, so it fails closed
        return ""


def destinations(text: str) -> list[str]:
    """Every host a string could send data to, lowercased; "" for a URL with no parsable host."""
    found = []
    for rx in (URL, EMAIL, IPV6, IPV4, DOMAIN):
        def take(m, rx=rx):
            if rx is URL:
                found.append(_url_host(m.group(0)))
            else:
                found.append(_host(m.group(1) if rx in (EMAIL, IPV6) else m.group(0)))
            return " "                                  # consume the match so later patterns don't re-read it
        text = rx.sub(take, text)
    return found


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
        return bool(host) and any(host == d or host.endswith("." + d) for d in self.allowed_domains)

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
        for s in self._strings(args):                  # every string, at any depth
            for host in destinations(s):
                if not self._allowed_host(host):         # deny by default: only allowlisted hosts pass
                    return Decision(False, False, f"egress to {host or '<unknown>'} blocked")
        if tainted:
            return Decision(True, True, "tainted context")
        return Decision(True, False, "ok")
