# ex37 hints · Chunking strategies

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

All three chunkers share one invariant: `chunk.text == source[chunk.start:chunk.end]`. The easiest way to keep it is to
work with **string pieces** that concatenate back to the input, and compute offsets only at the end by walking a
running position. `fixed_chunks` is a `range(0, len(text), size - overlap)` loop that stops once a window reaches the
end.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Write `recursive_chunks` as a recursive helper that returns a list of strings:

1. If the text fits, return it as one piece.
2. Pick the first separator that occurs in the text. If none does, hard-split into `max_chars` slices.
3. Split on that separator, *keeping it attached* to the end of each piece except the last.
4. Recurse (with only the remaining separators) into any piece that is still too long.
5. Greedily merge neighboring pieces while the merged length stays within `max_chars`.

For headings, use a multiline regex `^(#{1,6})\s+(.+?)\s*$`. Section boundaries are the heading start positions.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `text.split(sep)` throws the separator away. Add it back to every piece but the last, or the concatenation check
  fails.
- When the text ends with the separator, `split` produces a trailing empty string. Drop it, because chunks must be
  non-empty.
- Heading trail: on a heading of level *L*, keep only the trail entries with level **less than** *L*, then append the
  new heading. That pops siblings and deeper levels.
- The text before the first heading is its own chunk with `path == ""`. Only add it if it's non-empty.
- `plan_reindex` is set differences on keys: build `{key: chunk}` from `chunk_keys` first, then compare in both
  directions. An edited chunk has a new key, so it shows up once in each list; a kept key goes to `to_update` with
  its fresh chunk, because its offsets may have moved.
- `chunk_keys` needs a counter per `(path, text)` pair, so the second identical chunk gets `ordinal` 1.
- Effective dates: `effective_to` is exclusive, so a version ending on 1 March is not in force on 1 March. Convert
  ISO strings with `date.fromisoformat` before comparing.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_fixed` | Extra empty or duplicate chunk at the end; no check for `overlap >= size` |
| `test_recursive_invariants` | Separators lost (concatenation differs from the input), or a merged chunk exceeds `max_chars` |
| `test_recursive_prefers_paragraphs` | Trying separators in the wrong order, so sentences are cut before paragraphs |
| `test_recursive_hard_split` | No fallback when no separator occurs |
| `test_heading_paths` | Trail not popped for equal levels (Claims nested under Coverage); preamble chunk missing |
| `test_chunk_key` | Hashing a different serialization (e.g. `f"{doc_id}{path}{text}"`) instead of the JSON list, or leaving out `ordinal` |
| `test_chunk_keys_distinguish_identical_chunks` | Ordinal counted per document instead of per `(path, text)` pair, or not counted, so identical chunks share a key |
| `test_plan_reindex_touches_only_changes` | Comparing whole documents, so every chunk is re-added; the deleted index id missing |
| `test_plan_reindex_refreshes_moved_chunks` | Kept keys dropped instead of returned in `to_update` with the incoming chunk, so stale offsets and dates stay in the index |
| `test_plan_reindex_document_removed` | Empty `incoming` treated as "nothing to do"; missing `meta["path"]` raises `KeyError` |
| `test_filter_effective` | `effective_to` treated as inclusive; a chunk with no dates dropped instead of always kept |
