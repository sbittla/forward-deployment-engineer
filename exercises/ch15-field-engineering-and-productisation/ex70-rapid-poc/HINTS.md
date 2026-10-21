# ex70 hints · Time-boxed POC: invoice extraction

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

This exercise is time-boxed on purpose: get *something* end to end first, then improve the field with the worst
accuracy. Write two normalisers before any regex: `normalize_date(s)`, which tries each date shape in turn and returns
ISO or `None`, and `parse_amount(s)`, which handles currency symbols and both decimal conventions.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **rule_extract:** one regex per field, returning only the fields it found.
- **Dates:** keep a list of `(shape_regex, strptime_format)` pairs, and search the text after a `Date` label for each
  shape. Note that `03/10/2026` is **DD/MM/YYYY** here.
- **extract:** run the rules, then work out the missing fields. Only call the LLM if something is missing *and* an LLM
  was given. Normalise what comes back, and fill only the missing fields, recording `"llm"` as the source.
- **evaluate:** compare each field with the gold value (floats within half a cent), count per field, and compute
  overall accuracy over every field.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `EUR 9.999,00` is a European amount. When both separators appear, whichever comes **last** is the decimal mark.
- `Subtotal` must not match `Total`. A lookbehind such as `(?<![a-z])` before `total` (case-insensitive) does it.
- An invoice number token must contain a digit, or `Invoice` on its own line matches with an empty or wrong token.
- The prompt's first line is `Fields: <missing names>`, then a blank line, then the invoice. The test checks that
  fields the rules already found aren't requested.
- LLM values never overwrite rule values, even when the LLM returns them.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_rules_inv1` | `Subtotal` matched as the total; vendor or number regex picks the wrong line |
| `test_rules_formats` | DD/MM read as MM/DD; European decimal comma misparsed; `Inv.` prefix not recognised |
| `test_llm_fills_only_missing` | LLM output overrides rule fields; prompt lists every field |
| `test_no_llm_call_when_complete` | LLM called even though nothing is missing |
| `test_evaluate` | LLM date not normalised before comparing; `llm_fields` miscounted |
| `test_evaluate_without_llm` | Overall accuracy averaged per sample instead of per field |
| `test_readout` | Threshold direction reversed (improve the fields *under* 0.9); standing next step missing |
| `test_injected_reply_cannot_add_or_override` | Every key in the reply merged, not only the missing fields; `json.loads` error not caught |
| `test_exit_gate` | Gates checked before the sample size; point estimate used where the Wilson lower bound is needed |
