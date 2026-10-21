# ex96 · Dynamic few-shot example selection

**Chapter:** 8 · Prompt Engineering (`exercises/ch08-prompt-engineering/`) · **Covers:** R09 Prompt & context engineering, R10 RAG

## Learning objectives
- Treat few-shot examples as retrieved context: choose them per query instead of hard-coding them.
- Balance relevance against diversity with maximal marginal relevance (MMR), and drop near-duplicates.
- Respect a token budget and label coverage, and format examples so the model can't confuse them with input.

## Scenario
A ticket-routing prompt uses five fixed examples, four of them about passwords. Accuracy on billing tickets is 61%
and the team's fix was to add more examples until the prompt hit 9k tokens. You'll replace the fixed list with
selection from a 2,000-example pool: the examples most like the incoming ticket, without five copies of the same one,
and with every label represented when it matters.

## Your task
Examples are `{"input": str, "output": str}`. Similarity is `cosine(hash_embed(a), hash_embed(b))` from
`fde_kit.text` on the `input` text.

- `approx_tokens(example) -> int`: `max(1, (len(input) + len(output)) // 4)`.
- `select_examples(query, pool, k=3, lam=0.7, max_tokens=None) -> list[dict]`
  - Raise `ValueError` if `k < 1`.
  - Greedy MMR: repeatedly take the candidate maximising `lam * rel - (1 - lam) * max_sim_to_already_chosen`
    (0 when none chosen); break ties by lower pool index. Every candidate is considered once.
  - Skip a candidate whose similarity to any chosen example is `>= DUPLICATE_SIM` (0.95), or whose tokens exceed
    the remaining budget; keep going until `k` are chosen or candidates run out.
  - Return chosen examples ordered by relevance **ascending** (ties: higher index first), so the most relevant
    example is last, nearest the query.
- `ensure_label_coverage(selected, pool, labels, query) -> list[dict]`: for each label in order that has no example
  in the list, take the pool example with that label most relevant to the query (not already present) and replace the
  first example in the list whose label appears more than once; if none does, prepend it. Skip labels with no pool
  examples. Return sorted by relevance ascending.
- `format_examples(examples) -> str`: `<examples>` wrapper, one `<example>` per item with `<input>`/`<output>` children,
  newline-separated (see tests), HTML-escaping `<`, `>`, `&` in the text.
- `build_messages(query, pool, k=3) -> list[dict]`: one user message: the formatted examples, a blank line, the
  instruction `Classify the ticket below the same way as the examples. Reply with the label only.`, then the escaped
  query inside `<ticket>...</ticket>` on its own line at the end.

## Field notes
Few-shot examples are the strongest steering signal in a prompt, so models copy their quirks: length, phrasing,
even typos. Curate the pool like a golden set, and include hard negatives.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
Explain dynamic few-shot selection to an engineer who knows RAG. Cover: why fixed examples bias a classifier toward
over-represented labels, how maximal marginal relevance works (show the formula and a 4-item worked example), why
near-duplicates waste tokens, and why the most relevant example should sit closest to the query. Finish with two
failure modes of dynamic selection and how to evaluate it against a fixed set.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch08-prompt-engineering/ex96-few-shot-selection/starter.py so test_few_shot.py passes. Use
fde_kit.text.hash_embed and cosine for similarity; no third-party packages. Follow the README's tie-break and ordering
rules exactly, since the tests depend on them. Do not edit tests. Run pytest on the folder and show the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Here is my few-shot selector. Check: (1) Is the MMR loop O(k·n) per query, or worse? (2) Can label coverage swap out
the single most relevant example? (3) Does escaping break any example that legitimately contains XML? (4) What would
you log in production to know whether selection is helping?
```
**Production prompt (what this code produces)**
```text
<examples>
<example>
<input>Reset email not arriving after invoice change</input>
<output>billing</output>
</example>
...
</examples>

Classify the ticket below the same way as the examples. Reply with the label only.
<ticket>{ticket_text}</ticket>
```
