# ex37 · Chunking strategies

**Module:** m07 Retrieval & RAG · **Covers:** R10 RAG & retrieval · **Time:** 50 min

## Scenario
Policy documents are 80-page PDFs converted to markdown. Fixed-size chunks cut exclusions in half ("…is covered" /
"except flood damage"), and retrieval misses the critical sentence. You'll implement three strategies and compare.

## Your task
`Chunk(text, start, end, meta)` — `start/end` are character offsets into the source (`text == source[start:end]`).

1. `fixed_chunks(text, size, overlap)` — windows of `size` chars stepping by `size - overlap`; the last chunk may be
   shorter; raise `ValueError` if `overlap >= size`. No empty chunks.
2. `recursive_chunks(text, max_chars, separators=("\n\n", "\n", ". ", " "))` — split on the first separator that
   occurs, keep the separator attached to the end of the preceding piece, greedily merge adjacent pieces while the
   merged length ≤ `max_chars`, and recurse with the remaining separators into any single piece still too long.
   If no separator remains, hard-split. Every chunk satisfies `len ≤ max_chars` and concatenating all chunk texts
   reproduces the input exactly.
3. `heading_chunks(markdown)` — one chunk per section starting at each ATX heading (`#`..`######`); text before the
   first heading is its own chunk with `meta["path"] == ""`. `meta["path"]` is the heading trail joined by
   `" > "` (e.g. `"Policy > Coverage > Exclusions"`); a heading pops deeper/equal levels off the trail.
