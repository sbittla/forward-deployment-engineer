import json
import math
import random
import re
from collections import defaultdict

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
ROLE = {"customer": "user", "agent": "assistant"}


def select(convs: list[dict], min_csat: int = 4) -> list[dict]:
    return [c for c in convs
            if c.get("resolved") and c.get("csat") is not None and c["csat"] >= min_csat
            and any(t["role"] == "agent" for t in c["turns"])]


def _redact(text: str) -> str:
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))


def to_example(conv: dict, system: str) -> dict:
    msgs: list[dict] = []
    for t in conv["turns"]:
        role = ROLE[t["role"]]
        text = _redact(t["text"])
        if msgs and msgs[-1]["role"] == role:
            msgs[-1]["content"] += "\n" + text
        else:
            msgs.append({"role": role, "content": text})
    while msgs and msgs[-1]["role"] != "assistant":
        msgs.pop()
    if not msgs:
        raise ValueError(f"conversation {conv.get('id')} has no agent turn")
    return {"messages": [{"role": "system", "content": system}] + msgs}


def _norm(ex: dict) -> str:
    body = " ".join(m["content"] for m in ex["messages"] if m["role"] != "system")
    return " ".join(re.sub(r"\d", "0", body.lower()).split())


def dedupe(examples: list[dict]) -> list[dict]:
    seen, out = set(), []
    for ex in examples:
        key = _norm(ex)
        if key not in seen:
            seen.add(key)
            out.append(ex)
    return out


def split(examples: list[dict], intents: list[str], val_ratio: float = 0.2, seed: int = 0):
    rng = random.Random(seed)
    groups = defaultdict(list)
    for ex, intent in zip(examples, intents):
        groups[intent].append(ex)
    train, val = [], []
    for intent in sorted(groups):
        g = list(groups[intent])
        rng.shuffle(g)
        k = max(1, round(len(g) * val_ratio)) if len(g) >= 2 else 0
        val += g[:k]
        train += g[k:]
    return train, val


def _tokens(ex: dict) -> int:
    return sum(math.ceil(len(m["content"]) / 4) for m in ex["messages"])


def max_tokens_filter(examples: list[dict], limit: int) -> list[dict]:
    return [ex for ex in examples if _tokens(ex) <= limit]


def write_jsonl(examples: list[dict], path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def stats(train: list[dict], val: list[dict]) -> dict:
    allx = train + val
    avg = sum(_tokens(x) for x in allx) / len(allx) if allx else 0.0
    return {"train": len(train), "val": len(val), "avg_tokens": round(avg, 1)}
