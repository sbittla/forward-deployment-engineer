import json
import re
from dataclasses import dataclass

KEYS = ("as_a", "i_want", "so_that", "acceptance_criteria")


@dataclass(frozen=True)
class Story:
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: tuple[str, ...]


SYSTEM = (
    "You turn customer discovery interview transcripts into user stories.\n"
    "Return ONLY a JSON array. Each element is an object with keys: "
    '"as_a" (role), "i_want" (capability), "so_that" (business outcome), '
    '"acceptance_criteria" (list of testable strings, at least one).\n'
    "Use the customer's own words. Do not invent requirements that are not in the transcript."
)


def build_prompt(transcript: str) -> tuple[str, str]:
    return SYSTEM, f"<transcript>\n{transcript}\n</transcript>\n\nExtract the user stories."


def parse_stories(text: str) -> list[Story]:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    raw = fenced.group(1) if fenced else text
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"reply is not valid JSON: {e}") from None
    if not isinstance(data, list):
        raise ValueError("reply JSON must be an array of stories")
    seen, out = set(), []
    for i, s in enumerate(data):
        if not isinstance(s, dict):
            raise ValueError(f"story {i} is not an object")
        for k in KEYS:
            if k not in s:
                raise ValueError(f"story {i} is missing key '{k}'")
        for k in KEYS[:3]:
            if not isinstance(s[k], str) or not s[k].strip():
                raise ValueError(f"story {i} has empty '{k}'")
        ac = s["acceptance_criteria"]
        if not isinstance(ac, list) or not ac or not all(isinstance(a, str) and a.strip() for a in ac):
            raise ValueError(f"story {i} needs at least one acceptance criterion")
        key = (s["as_a"].strip().lower(), s["i_want"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(Story(s["as_a"].strip(), s["i_want"].strip(), s["so_that"].strip(), tuple(ac)))
    return out


def extract(transcript: str, llm, max_attempts: int = 2) -> list[Story]:
    system, user = build_prompt(transcript)
    messages = [{"role": "user", "content": user}]
    last_err = None
    for _ in range(max_attempts):
        reply = llm.complete(messages, system=system).text
        try:
            return parse_stories(reply)
        except ValueError as e:
            last_err = e
            messages = messages + [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": f"Your reply could not be used: {e}. Return only the JSON array."},
            ]
    raise ValueError(f"model did not return valid stories after {max_attempts} attempts: {last_err}")
