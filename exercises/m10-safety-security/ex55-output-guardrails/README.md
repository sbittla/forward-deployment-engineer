# ex55 · Output guardrails and groundedness

**Module:** m10 · **Covers:** R14 Guardrails & responsible AI · **Time:** 50 min

## Scenario
Legal reviewed your copilot and set rules for anything shown to policyholders: no legal or medical advice, no
promises ("guaranteed approval"), no personal data that wasn't in the retrieved sources, and every sentence must be
supported by a source. Violations of the first three block the answer; unsupported sentences are removed.

## Your task
`check_output(answer, sources, policy) -> GuardResult(allowed, violations, safe_text)`

`Policy(blocked_topics: dict[name, list[keyword]], banned_phrases: list[str], min_support=0.5, fallback=...)`

Split the answer into sentences on `(?<=[.!?])\s+`. Content tokens = `fde_kit.tokenize(s)`.
1. **Topics** (block): any keyword (case-insensitive, whole word/phrase) → violation `"topic:<name>"`.
2. **Banned phrases** (block): substring match, case-insensitive → `"phrase:<phrase>"`.
3. **PII leak** (block): any email or `###-##-####` in the answer that does not appear in any source → `"pii_leak"`.
4. **Groundedness** (warn): a sentence is supported if, for some source, the share of the sentence's content tokens
   that appear in that source's tokens is ≥ `min_support`. Each unsupported sentence → `"ungrounded:<sentence>"`.
   Sentences with no content tokens count as supported.

Result: if any block-level violation → `allowed=False`, `safe_text=policy.fallback`. Otherwise `allowed=True` and
`safe_text` = the supported sentences joined by a single space (or `policy.fallback` if none remain).
Violations are listed in the order of the checks above (sentences in order).
