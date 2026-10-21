# ex37 · Chunking strategies

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R10 RAG & retrieval

## Learning objectives
- Compare fixed, recursive and heading-aware chunking strategies.
- Keep chunk offsets exact so citations point at source text.
- Choose chunking based on document structure and retrieval behavior.
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
4. `chunk_key(doc_id, path, text, ordinal=0) -> str` — the SHA-256 hex digest of
   `json.dumps([doc_id, path, text, ordinal])`, so a chunk's key changes when its document, heading path or text
   changes. `chunk_keys(doc_id, chunks) -> list[str]` keys a whole document in order: `ordinal` counts earlier
   chunks with the same path and text (a chunk without `meta["path"]` uses `""`), so two identical chunks in one
   document ("Sign here.") get different keys instead of collapsing into one. Offsets are deliberately not in the
   key: an edit early in the document would otherwise re-embed every later chunk.
5. `plan_reindex(doc_id, current, incoming) -> (to_add, to_delete, to_update)` — incremental re-indexing for one
   document. `current` maps chunk key → index id for what the index holds now (keys from `chunk_keys`); `incoming`
   is the freshly re-chunked document. `to_add` lists the incoming chunks whose key is not in `current`, in
   incoming order; `to_delete` lists the index ids whose key no longer appears, in `current`'s order; `to_update`
   lists `(index_id, chunk)` for every incoming chunk whose key is already indexed, in incoming order, so its new
   offsets and metadata (effective dates) are written without re-embedding. An edited chunk is therefore one add
   plus one delete; `incoming == []` (the document was removed from the source) deletes every chunk.
6. `filter_effective(chunks, on: date) -> list[Chunk]` — keep, in order, the chunks in force on `on`:
   `meta["effective_from"] <= on < meta["effective_to"]`. Both are ISO dates (`"2026-03-01"`) or `date` objects; a
   missing or `None` bound is open-ended, so a chunk with neither is always in force.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch10-rag/ex37-chunking`.
- **Expected output:** all 11 tests fail against the starter; when you're done, all 11 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch10-rag/ex37-chunking`: all 11 pass.
- **Tests:** `test_chunking.py` (11 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Chunks are character windows over in-memory markdown, and `plan_reindex` only plans the
  change. A production pipeline also converts PDFs reliably, applies the add/delete plan atomically with the
  embeddings, treats a document missing from the source as an explicit deletion event, and monitors chunk counts and
  newest-document age per source.

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
Implement exercises/ch10-rag/ex37-chunking/starter.py so that test_chunking.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Chunk`,
`fixed_chunks`, `recursive_chunks`, `heading_chunks`, `chunk_key`, `chunk_keys`, `plan_reindex`,
`filter_effective`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest exercises/ch10-rag/ex37-chunking`
and show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Chunking strategies" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Does concatenating recursive chunks reproduce the input exactly? Can an empty chunk be
produced? Which strategy would keep an exclusion clause with the coverage it modifies? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
