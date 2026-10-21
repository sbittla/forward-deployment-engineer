# ex55 hints · Output guardrails and groundedness

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Keep two lists, **blocking** violations and **warnings**, and run the four checks in the README's order, appending to
the right list. The final result is then simple: if anything is blocking, return the fallback; otherwise keep the
supported sentences.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Topics:** for each topic, `re.search(rf"\b{re.escape(k)}\b", answer, re.I)` for any keyword.
- **Banned phrases:** a lowercase substring check.
- **PII leak:** find emails and SSN patterns in the answer. Flag a leak if any of them doesn't appear in the joined
  source text.
- **Groundedness:** tokenize each source once into a set. For each sentence, compute the share of its content tokens
  found in a source's set, and call the sentence supported if any source reaches `min_support`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Topic keywords need word boundaries: "pursue" must not match "sue". That's what `test_whole_word_topics` checks.
- An email that *is* in the sources (`claims@northwind.com`) isn't a leak; only new ones are.
- Ungrounded sentences are warnings, not blocks. The answer is still allowed, minus those sentences, unless nothing
  supported remains, in which case use the fallback.
- An ungrounded violation contains the full original sentence, including its punctuation: `ungrounded:<sentence>`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_clean_grounded` | Support threshold computed over all tokens (stopwords included) instead of `tokenize` output |
| `test_ungrounded_removed` | Ungrounded sentences treated as blocking; split pattern loses the `!` |
| `test_blocked` | Violations not in check order; source emails flagged as leaks |
| `test_whole_word_topics` | Substring topic matching (`pursue` matches `sue`) |
| `test_all_ungrounded_falls_back` | Empty string returned instead of the fallback |
| `test_ssn_leak` | SSN pattern missing from the PII check |
| `test_boundary_poisoned_source_counts_as_grounded` | Sources other than the first ignored for support or PII checks; this test pins that output checks trust every source |
