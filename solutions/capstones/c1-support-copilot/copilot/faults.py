"""Failure injection: wrappers that make the model or the index fail on purpose, so degraded modes can be tested."""


class FaultyLLM:
    """Wraps an LLM. Raises `error` on the 1-based call numbers in `fail_on`, or on every call when it's None."""

    def __init__(self, llm, error: Exception | None = None, fail_on: set | None = None):
        self.llm, self.fail_on = llm, fail_on
        self.error = error or TimeoutError("model call timed out")
        self.attempts = 0

    @property
    def calls(self):
        return self.llm.calls

    def complete(self, messages, **kw):
        self.attempts += 1
        if self.fail_on is None or self.attempts in self.fail_on:
            raise self.error
        return self.llm.complete(messages, **kw)


class FaultyRetriever:
    """Wraps a retriever whose index is unreachable: every search raises `error`."""

    def __init__(self, retriever, error: Exception | None = None):
        self.retriever = retriever
        self.permission_aware = getattr(retriever, "permission_aware", False)
        self.error = error or ConnectionError("vector index unavailable")

    def search(self, *args, **kw):
        raise self.error
