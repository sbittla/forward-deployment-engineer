import math


class ConversationMemory:
    def __init__(self, llm, max_tokens: int = 1000, keep_recent: int = 4):
        self.llm = llm
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent
        self.summaries_made = 0

    def add(self, role: str, content: str) -> None:
        raise NotImplementedError

    def pin(self, key: str, value: str) -> None:
        raise NotImplementedError

    def context(self) -> tuple[str, list[dict]]:
        raise NotImplementedError
