# ex55 · Output guardrails and groundedness

**Chapter:** 13 · AI Security and Guardrails (`exercises/ch13-ai-security-and-guardrails/`) · **Covers:** R14 Guardrails & responsible AI

## Learning objectives
- Block policy-violating answers before they reach end users.
- Remove sentences that are not supported by retrieved sources.
- Detect PII that appears in the answer but not in sources.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch13-ai-security-and-guardrails/ex55-output-guardrails`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch13-ai-security-and-guardrails/ex55-output-guardrails`: all 7 pass.
- **Tests:** `test_guardrails.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Keyword topics and token-overlap groundedness are crude, and every source is trusted: an
  answer copied from a poisoned document passes (`test_boundary_poisoned_source_counts_as_grounded`). Production adds
  judge-based faithfulness checks offline, a model-based support check for high-stakes answers, and ingestion
  controls on who can write to the indexed sources.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Output guardrails and groundedness".
Before I write code, teach me output guardrails, topic and phrase blocking, lexical groundedness checks, and their
failure modes. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch13-ai-security-and-guardrails/ex55-output-guardrails/starter.py so that test_guardrails.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Policy`, `GuardResult`, `check_output`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch13-ai-security-and-guardrails/ex55-output-guardrails` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Output guardrails and groundedness" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Is whole-word topic matching correct for multi-word phrases? Can paraphrased
unsupported claims pass the token-overlap check? What fallback text would Legal accept? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
