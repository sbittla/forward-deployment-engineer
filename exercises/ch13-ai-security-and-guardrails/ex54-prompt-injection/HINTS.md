# ex54 hints · Prompt-injection defences for tool-using agents

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`wrap_untrusted` is one case-insensitive `re.sub` on the content plus a `replace` on the source. Then express
`injection_signals` as an **ordered list** of `(name, compiled_regex)` pairs: the result is the names whose regex
matches, in list order, so each signal appears at most once automatically.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **ignore_instructions:** the verb, the qualifier and the noun must appear together, so allow a short gap between
  them, such as `\b(ignore|disregard|forget)\b[^.]{0,30}\b(previous|prior|above)\b[^.]{0,20}\b(instructions?|rules)\b`.
  Excluding `.` from the gap keeps the match inside one sentence.
- **exfiltration:** a send-type verb, then `to`, then something that looks like an email address or a URL.
- **ToolGate:** read-only tools return straight away. For side-effect tools, walk every string in `args`
  (recursively), extract URLs and email domains, and deny on the first host that isn't allowed. Only then apply the
  tainted rule.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The benign cases matter as much as the attacks: "I ignored the previous email … rules for refunds" must **not**
  trigger. The full stop between "email" and "rules" is what keeps it clean.
- "Please forward my invoice" has a verb but no destination, so it isn't exfiltration.
- Allowed domains include subdomains: `eu.api.partner.io` matches `api.partner.io`, using `host.endswith("." + d)` or an
  exact match. Never use a bare `endswith(d)`.
- The deny reason names the host: `egress to evil.com blocked`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_wrap` | Case-sensitive replacement misses `<UNTRUSTED`; quotes in the source not escaped |
| `test_signals` | Signals returned in match order instead of the fixed order; base64 run length not 40 |
| `test_benign` | Gap pattern crosses sentence boundaries; a verb alone triggers exfiltration |
| `test_post_to_url_is_exfil` | Exfiltration only recognises email addresses, not URLs |
| `test_gate_read_only` | Read-only tools subjected to egress or taint checks |
| `test_gate_egress` | Subdomains of allowed domains rejected; reason text format differs |
| `test_gate_tainted` | Tainted side-effect call denied instead of allowed with confirmation |
| `test_boundary_paraphrase_evades_signals_but_gate_blocks` | Extra exfiltration verbs beyond the spec's list; or the gate only checks egress when `tainted=True` |
