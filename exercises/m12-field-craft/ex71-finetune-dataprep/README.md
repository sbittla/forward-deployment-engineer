# ex71 · Fine-tuning dataset preparation

**Module:** m12 · **Covers:** R16 Fine-tuning / ML fundamentals · **Time:** 60 min

## Scenario
Prompting got the customer's tone-of-voice 80% of the way. They want to try fine-tuning a smaller model on their
best historical support replies. The model is only as good as the dataset — and the most common failure is
**leakage**: near-identical conversations in both train and validation sets, giving a fake great score.

## Your task
Input conversations: `{"id", "intent", "csat" (1–5 or None), "resolved": bool, "turns": [{"role": "customer"|"agent",
"text"}]}`.

1. `select(convs, min_csat=4)` — keep resolved conversations with `csat >= min_csat` that contain at least one
   agent turn.
2. `to_example(conv, system) -> dict` — chat format `{"messages": [{"role": "system", ...}, then "user" for customer
   turns and "assistant" for agent turns]}`; consecutive turns by the same role are merged with `"\n"`; the example
   must end with an assistant message (drop trailing customer turns). Redact emails → `[EMAIL]` and phone numbers
   (`\+?\d[\d\s().-]{7,}\d`) → `[PHONE]` in every message.
3. `dedupe(examples) -> list` — drop examples whose normalised content (lower-case, digits replaced by `0`,
   whitespace collapsed, over all non-system messages) has been seen; keep the first.
4. `split(examples, intents, val_ratio=0.2, seed=0) -> (train, val)` — stratified by intent (parallel list), using
   `random.Random(seed)`; each intent contributes `max(1, round(n * val_ratio))` validation examples when it has ≥ 2
   examples, else 0.
5. `max_tokens_filter(examples, limit)` — drop examples whose total `ceil(len(content)/4)` over all messages exceeds
   `limit`.
6. `write_jsonl(examples, path)` and `stats(train, val) -> {"train", "val", "avg_tokens"}` (avg over all, 1 dp).
