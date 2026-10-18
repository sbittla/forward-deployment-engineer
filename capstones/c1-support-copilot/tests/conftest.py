import re

import pytest

from fde_kit import FakeLLM, LLMResponse, tokenize

SOURCE_LINE = re.compile(r"^\[(\d+)\] \((.*?)\) (.*)$", re.M)


def quoting_responder(messages, system, tools):
    """Deterministic stand-in for the model: quote the best-matching sentence of the best source and cite it."""
    prompt = messages[-1]["content"]
    question = prompt.rsplit("Question:", 1)[-1]
    q = set(tokenize(question))
    best = None
    for n, path, text in SOURCE_LINE.findall(prompt):
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            score = len(q & set(tokenize(f"{path} {sentence}")))
            if best is None or score > best[0]:
                best = (score, n, sentence)
    if not best or best[0] == 0:
        return LLMResponse(text="NOT_IN_SOURCES", input_tokens=len(prompt) // 4, output_tokens=3)
    return LLMResponse(text=f"{best[2]} [{best[1]}]", input_tokens=len(prompt) // 4, output_tokens=40)


@pytest.fixture
def llm():
    return FakeLLM(quoting_responder)


@pytest.fixture
def copilot(cap, cap_data, llm):
    chunks = cap.load_corpus(cap_data / "policies")
    router = cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl")
    return cap.Copilot(llm, cap.HybridRetriever(chunks), router)
