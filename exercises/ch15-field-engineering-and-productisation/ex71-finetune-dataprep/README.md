# ex71 · Fine-tuning dataset preparation

**Chapter:** 15 · Field Engineering and Productisation (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R16 Fine-tuning / ML fundamentals

## Learning objectives
- Select high-quality training conversations for fine-tuning.
- Format, redact and deduplicate examples in chat format.
- Split train/validation without leakage.

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

**Errors:** `to_example` raises `ValueError` when no assistant message remains (nothing to learn from).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Fine-tuning dataset preparation".
Before I write code, teach me fine-tuning dataset preparation: selection criteria, chat formatting, PII redaction,
near-duplicate removal, stratified splits, and token limits. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch15-field-engineering-and-productisation/ex71-finetune-dataprep/starter.py so that test_dataprep.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `select`,
`to_example`, `dedupe`, `split`, `max_tokens_filter`, `write_jsonl`, `stats`. Constraints: Python 3.11+, the
standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify
the tests or fde_kit. When you're done, run `pytest exercises/ch15-field-engineering-and-productisation/ex71-finetune-dataprep` and show me
the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Fine-tuning dataset preparation" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Can near-duplicates still land in both train and validation? Does redaction run on
every message, including merged turns? Would you fine-tune at all, or improve the prompt first, and why? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
