import json

import pytest

from fde_kit import FakeLLM

SCHEMA = {
    "type": "object",
    "required": ["claim_id", "amount", "claimant", "category"],
    "additionalProperties": False,
    "properties": {
        "claim_id": {"type": "string", "minLength": 3},
        "amount": {"type": "number", "minimum": 0},
        "claimant": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}},
        "category": {"enum": ["auto", "home", "health"]},
        "injuries": {"type": "integer", "minimum": 0, "maximum": 20},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}
GOOD = {"claim_id": "CL-1", "amount": 1250.5, "claimant": {"name": "Ana"}, "category": "auto", "tags": ["rear-end"]}


def test_extract_from_prose_and_fences(impl):
    text = 'Sure! Here it is:\n```json\n{"a": "brace } in string", "b": [1, {"c": 2}]}\n```\nAnything else?'
    assert impl.extract_json(text) == {"a": "brace } in string", "b": [1, {"c": 2}]}
    assert impl.extract_json('noise [1, 2] {"x": 1}') == [1, 2]
    assert impl.extract_json('bad {not json} then {"ok": true}') == {"ok": True}
    with pytest.raises(ValueError):
        impl.extract_json("no json here")


def test_validate_ok(impl):
    assert impl.validate(GOOD, SCHEMA) == []


@pytest.mark.parametrize("patch,needle", [
    ({"amount": "1250"}, "$.amount"),
    ({"amount": -1}, "$.amount"),
    ({"amount": True}, "$.amount"),
    ({"claimant": {}}, "$.claimant.name"),
    ({"category": "boat"}, "$.category"),
    ({"injuries": 2.5}, "$.injuries"),
    ({"injuries": 21}, "$.injuries"),
    ({"tags": ["a", 3]}, "$.tags[1]"),
    ({"claim_id": "C"}, "$.claim_id"),
    ({"extra": 1}, "extra"),
])
def test_validate_errors(impl, patch, needle):
    errs = impl.validate({**GOOD, **patch}, SCHEMA)
    assert errs and any(needle in e for e in errs)


def test_missing_required(impl):
    obj = dict(GOOD)
    del obj["category"]
    assert any("category" in e for e in impl.validate(obj, SCHEMA))


def test_repair_loop(impl):
    bad = {**GOOD, "amount": "lots"}
    llm = FakeLLM([f"Here you go: {json.dumps(bad)}", json.dumps(GOOD)])
    obj, attempts = impl.complete_structured(llm, "Email: ...", SCHEMA)
    assert obj == GOOD and attempts == 2
    assert '"claim_id"' in llm.calls[0]["system"]
    assert "$.amount" in llm.calls[1]["messages"][-1]["content"]


def test_gives_up(impl):
    llm = FakeLLM(["{}"] * 3)
    with pytest.raises(ValueError) as e:
        impl.complete_structured(llm, "x", SCHEMA, max_repairs=2)
    assert "claim_id" in str(e.value) and len(llm.calls) == 3
