import json

SYSTEM = "You are Northwind's friendly support agent."


def conv(i, intent="billing", csat=5, resolved=True, turns=None):
    return {"id": i, "intent": intent, "csat": csat, "resolved": resolved,
            "turns": turns or [{"role": "customer", "text": f"Charged twice on order {i}"},
                               {"role": "agent", "text": "Sorry! I've refunded the duplicate charge."}]}


def test_select(impl):
    cs = [conv(1), conv(2, csat=3), conv(3, resolved=False), conv(4, csat=None),
          conv(5, turns=[{"role": "customer", "text": "hello?"}])]
    assert [c["id"] for c in impl.select(cs)] == [1]


def test_to_example_merge_redact_trailing(impl):
    c = conv(1, turns=[
        {"role": "customer", "text": "Hi"}, {"role": "customer", "text": "email me at ana@example.com"},
        {"role": "agent", "text": "Sure, or call +1 (415) 555-0100."},
        {"role": "customer", "text": "thanks bye"},
    ])
    ex = impl.to_example(c, SYSTEM)
    assert ex["messages"] == [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "Hi\nemail me at [EMAIL]"},
        {"role": "assistant", "content": "Sure, or call [PHONE]."},
    ]


def test_dedupe(impl):
    exs = [impl.to_example(conv(i), SYSTEM) for i in (101, 202, 303)]
    assert len(impl.dedupe(exs)) == 1  # differ only in order number digits


def test_split_stratified_no_overlap(impl):
    exs, intents = [], []
    for i in range(10):
        exs.append({"messages": [{"role": "user", "content": f"b{i}"}]}); intents.append("billing")
    for i in range(5):
        exs.append({"messages": [{"role": "user", "content": f"l{i}"}]}); intents.append("login")
    exs.append({"messages": [{"role": "user", "content": "rare"}]}); intents.append("rare")
    train, val = impl.split(exs, intents, 0.2, seed=3)
    assert len(val) == 2 + 1 and len(train) == 16 - 3
    ids = lambda xs: {x["messages"][0]["content"] for x in xs}
    assert ids(train).isdisjoint(ids(val)) and "rare" in ids(train)
    assert impl.split(exs, intents, 0.2, seed=3) == (train, val)


def test_token_filter_jsonl_stats(impl, tmp_path):
    short = {"messages": [{"role": "user", "content": "x" * 40}]}
    long = {"messages": [{"role": "user", "content": "x" * 400}]}
    assert impl.max_tokens_filter([short, long], 50) == [short]
    p = tmp_path / "train.jsonl"
    impl.write_jsonl([short, short], p)
    lines = p.read_text().splitlines()
    assert len(lines) == 2 and json.loads(lines[0]) == short
    assert impl.stats([short], [long]) == {"train": 1, "val": 1, "avg_tokens": 55.0}
