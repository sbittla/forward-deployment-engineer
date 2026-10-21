def extract_json(text: str):
    raise NotImplementedError


def validate(obj, schema: dict, path: str = "$") -> list[str]:
    raise NotImplementedError


class RefusalError(ValueError):
    """The provider's safety layer declined (stop_reason "refusal"). Never repaired: route to a fallback or a person."""


class TruncatedError(ValueError):
    """The reply hit max_tokens. Repairing under the same limit truncates it again."""


DECLINE = {"status": "cannot_extract"}


def classify_reply(response) -> str:
    """Why did the model stop, and what kind of reply is this? -> "refusal" | "truncated" | "declined" | "answer"."""
    raise NotImplementedError


def complete_structured(llm, prompt: str, schema: dict, max_repairs: int = 2):
    raise NotImplementedError
