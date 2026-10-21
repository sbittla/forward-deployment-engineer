# ex40 hints · RAG answers with citations and abstention

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `build_prompt` first and check its exact line format against `test_prompt`: `[1] (doc_id) text`, numbered from
1, then a blank line and `Question: ...` at the end. Then write the abstention path in `answer`. It returns before the
model is called, which is the cheapest guardrail you have.
</details>

<details>
<summary>Hint 2 · The approach</summary>

One regex handles all three citation forms: square brackets around one number or a comma-separated list, such as
`\[(\d+(?:\s*,\s*\d+)*)\]`. `[1][2]` is just two matches. Use `re.sub` with a **function**. For each match, split the
numbers and sort them into valid and invalid: valid numbers add their doc id to the citations if it isn't there yet,
and invalid numbers go to `invalid_citations`. The function returns the replacement text, rebuilt from the valid
numbers only.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Check for the model's own abstention by comparing the **stripped** reply with `ABSTAIN_TEXT`.
- Both abstention paths count as `grounded=True`: saying "I can't find it" is a grounded answer.
- `grounded` otherwise needs at least one valid citation *and* no invalid ones.
- Deduplicate citations in first-seen order: `[2] … [1][2]` gives `policy-9.1, policy-7.2`.
- Removing `[7]` can leave a space before the full stop. Tidying that up is a nice touch.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_prompt` | Sources numbered from 0; question not at the end; abstain text missing from the system prompt |
| `test_cited_answer` | `[1, 3]` not parsed; duplicate doc ids in citations |
| `test_invalid_citation_removed` | Invalid marker left in the text, or the answer still marked grounded |
| `test_no_citations_not_grounded` | `grounded` defaults to True when there are no citations |
| `test_abstain_low_score_skips_llm` | Model called even though the top score is below `min_score` |
| `test_model_abstains` | Reply not stripped before comparing, so the abstention isn't recognized |
| `test_k_passed` | `retrieve` called with a hard-coded k |
| `test_boundary_valid_citation_not_checked_for_support` | `grounded` made to depend on something other than valid citation numbers; ex40 deliberately doesn't check that a source supports its claim |
| `test_retrieved_text_stays_data` | Source text copied into the system prompt, or newlines kept so a chunk can start a forged `[2]` line |
| `test_boundary_injected_instructions_still_reach_the_model` | Source text dropped or rewritten instead of passed through as data; ex40 deliberately doesn't filter instruction-like text (Chapter 13 does) |
