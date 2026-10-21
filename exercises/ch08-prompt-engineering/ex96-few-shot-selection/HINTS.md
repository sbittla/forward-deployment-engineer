# ex96 hints · Dynamic few-shot example selection

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Precompute everything once: the query embedding, every example's embedding, and each example's relevance (cosine to
the query). Then work with **indices** into the pool rather than the example dicts. Index order is also the
tie-breaker.
</details>

<details>
<summary>Hint 2 · The approach</summary>

The greedy loop runs while there are candidates and fewer than `k` chosen:

1. Score every remaining candidate: `lam * relevance - (1 - lam) * (highest similarity to anything already chosen)`.
2. Take the best candidate, with ties going to the lower index (a key of `(score, -index)` with `max` works), and
   remove it from the candidates.
3. Skip it if it's a near-duplicate of something chosen, or doesn't fit the remaining token budget. Otherwise choose
   it and charge its tokens.

At the end, sort the chosen indices by relevance **ascending**, so the most relevant example sits last, right before
the query.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A skipped candidate is gone for good ("every candidate is considered once"). Don't put it back.
- `#8` is a near-duplicate of `#0` (similarity ≥ 0.95), so it never appears, even with `lam=1.0`.
- In `ensure_label_coverage`, replace the first example whose label appears **more than once**. If no label is
  repeated, prepend the new example instead.
- Escape with `html.escape(text, quote=False)`: `<`, `>` and `&` only.
- The ticket goes inside `<ticket>…</ticket>` on the **last** line, after the instruction.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_relevance_order_and_duplicate_suppression` | Output in selection order instead of relevance ascending; duplicates not suppressed |
| `test_lower_lambda_trades_relevance_for_diversity` | Redundancy term uses the average instead of the maximum similarity; ties broken by higher index |
| `test_token_budget` | Over-budget candidates stop the loop instead of being skipped; integer division wrong in `approx_tokens` |
| `test_bad_k` | `k=0` returns `[]` instead of raising |
| `test_label_coverage` | Replacing the wrong example; labels with no pool examples cause an error |
| `test_format_escapes_and_wraps` | Newline layout differs from the expected string; quotes escaped too |
| `test_build_messages` | Ticket not escaped or not at the end; more than one message |
| `test_injected_ticket_cannot_close_its_tag` | The ticket inserted raw, so a `</ticket>` inside it ends the block early and the text after it reads as instructions |
