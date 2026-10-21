import math

SUMMARY_SYSTEM = (
    "You maintain a running summary of a support conversation. Merge the previous summary with the new messages. "
    "Keep names, account and policy numbers, amounts, dates, decisions made and open questions. Be concise; "
    "reply with the updated summary only."
)


def _tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


class ConversationMemory:
    def __init__(self, llm, max_tokens: int = 1000, keep_recent: int = 4):
        self.llm = llm
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent
        self.summaries_made = 0
        self.summary = ""
        self.messages: list[dict] = []
        self.pins: dict[str, str] = {}

    def _total(self) -> int:
        return sum(_tokens(m["content"]) for m in self.messages)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        while self._total() > self.max_tokens and len(self.messages) > self.keep_recent:
            fold = self.messages[: len(self.messages) - self.keep_recent]
            body = "\n".join(f"{m['role']}: {m['content']}" for m in fold)
            prompt = f"<previous_summary>{self.summary}</previous_summary>\n<messages>\n{body}\n</messages>"
            self.summary = self.llm.complete([{"role": "user", "content": prompt}], system=SUMMARY_SYSTEM).text.strip()
            self.messages = self.messages[len(fold):]
            self.summaries_made += 1

    def pin(self, key: str, value: str) -> None:
        self.pins[key] = value

    def context(self) -> tuple[str, list[dict]]:
        parts = []
        if self.pins:
            parts.append("Pinned facts:\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(self.pins.items())))
        if self.summary:
            parts.append(f"Conversation summary:\n{self.summary}")
        return "\n\n".join(parts), [dict(m) for m in self.messages]
