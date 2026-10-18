import json

import pytest

from fde_kit import FakeLLM

GOOD = json.dumps([
    {"as_a": "claims adjuster", "i_want": "to search policy clauses by question",
     "so_that": "I answer customers on the first call", "acceptance_criteria": ["returns clause and page"]},
    {"as_a": "Claims Adjuster", "i_want": "To search policy clauses by question",
     "so_that": "dup", "acceptance_criteria": ["x"]},
    {"as_a": "ops manager", "i_want": "a weekly usage report", "so_that": "I can track adoption",
     "acceptance_criteria": ["emailed Monday", "per-team breakdown"]},
])


def test_prompt_shape(impl):
    system, user = impl.build_prompt("we lose time searching PDFs")
    assert "JSON" in system and "acceptance_criteria" in system
    assert "<transcript>" in user and "we lose time searching PDFs" in user and "</transcript>" in user


def test_parse_dedupes_and_handles_fence(impl):
    stories = impl.parse_stories("```json\n" + GOOD + "\n```")
    assert len(stories) == 2
    assert stories[1].acceptance_criteria == ("emailed Monday", "per-team breakdown")


@pytest.mark.parametrize("bad,needle", [
    ("not json", "json"),
    (json.dumps([{"as_a": "x", "i_want": "y", "so_that": "z"}]), "acceptance_criteria"),
    (json.dumps([{"as_a": "x", "i_want": "", "so_that": "z", "acceptance_criteria": ["a"]}]), "i_want"),
    (json.dumps([{"as_a": "x", "i_want": "y", "so_that": "z", "acceptance_criteria": []}]), "acceptance"),
])
def test_parse_rejects(impl, bad, needle):
    with pytest.raises(ValueError) as e:
        impl.parse_stories(bad)
    assert needle in str(e.value).lower()


def test_extract_retries_with_error_feedback(impl):
    llm = FakeLLM(["Sure! Here are your stories...", GOOD])
    stories = impl.extract("transcript", llm)
    assert len(stories) == 2 and len(llm.calls) == 2
    retry_msgs = llm.calls[1]["messages"]
    assert retry_msgs[-2]["role"] == "assistant" and retry_msgs[-1]["role"] == "user"
    assert "json" in retry_msgs[-1]["content"].lower()


def test_extract_gives_up(impl):
    llm = FakeLLM(["nope", "still nope"])
    with pytest.raises(ValueError):
        impl.extract("t", llm, max_attempts=2)
