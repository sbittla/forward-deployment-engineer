# ex37 · Chunking strategies

**Module:** m07 Retrieval & RAG · **Covers:** R10 RAG & retrieval · **Time:** 50 min

## Learning objectives
- Compare fixed, recursive and heading-aware chunking strategies.
- Keep chunk offsets exact so citations point at source text.
- Choose chunking based on document structure and retrieval behaviour.
- Keep an index fresh: re-index incrementally by content key and filter by effective date.

## Scenario
Policy documents are 80-page PDFs converted to markdown. Fixed-size chunks cut exclusions in half ("…is covered" /
"except flood damage"), and retrieval misses the critical sentence. You'll implement three strategies and compare.
The wording also changes: the March revision must replace February's chunks without re-embedding the whole policy,
and a claim filed in February must still be answered from the version in force then.

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
4. `chunk_key(doc_id, path, text) -> str` — the SHA-256 hex digest of `json.dumps([doc_id, path, text])`, so a
   chunk's key changes when its document, heading path or text changes.
5. `plan_reindex(doc_id, current, incoming) -> (to_add, to_delete)` — incremental re-indexing for one document.
   `current` maps chunk key → index id for what the index holds now; `incoming` is the freshly re-chunked document
   (a chunk without `meta["path"]` uses `""`). `to_add` lists the incoming chunks whose key is not in `current`, in
   incoming order; `to_delete` lists the index ids whose key no longer appears, in `current`'s order. An edited chunk
   is therefore one add plus one delete; unchanged chunks are untouched; `incoming == []` (the document was removed
   from the source) deletes every chunk.
6. `filter_effective(chunks, on: date) -> list[Chunk]` — keep, in order, the chunks in force on `on`:
   `meta["effective_from"] <= on < meta["effective_to"]`. Both are ISO dates (`"2026-03-01"`) or `date` objects; a
   missing or `None` bound is open-ended, so a chunk with neither is always in force.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Chunking strategies". Before I write
code, teach me chunking strategies for RAG, overlap, separator hierarchies, heading paths as metadata, and how
chunking affects retrieval recall. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m07-retrieval-rag/ex37-chunking/starter.py so that test_chunking.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Chunk`,
`fixed_chunks`, `recursive_chunks`, `heading_chunks`, `chunk_key`, `plan_reindex`, `filter_effective`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest exercises/m07-retrieval-rag/ex37-chunking`
and show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Chunking strategies" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Does concatenating recursive chunks reproduce the input exactly? Can an empty chunk be
produced? Which strategy would keep an exclusion clause with the coverage it modifies? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
