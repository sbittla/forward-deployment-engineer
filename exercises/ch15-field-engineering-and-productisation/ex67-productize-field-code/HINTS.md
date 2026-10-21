# ex67 hints · Productise a one-off field script

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Read `legacy_acme_report` line by line and list every hard-coded customer fact: the header name, the alias lists, the
SLA hours, the `-5` hour offset and the escalation address. Each one becomes a `ReportConfig` field. `ACME_CONFIG` is
those facts written down once; `build_report` must contain none of them.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Turn the legacy `if/elif` alias chains into one dict, `priority_aliases`, looked up with `raw.lower()`. Anything not
  found becomes `"normal"`.
- Keep the legacy logic otherwise identical: age in hours, breach when the age exceeds the limit, local time =
  opened + offset, lines sorted by overage descending, the total line, and the escalation line only when there are
  breaches.
- Write the parity test first and keep it green while you refactor. Byte-for-byte parity is the contract with the
  existing customer.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The header is the customer name **upper-cased** (`Acme Corp` becomes `ACME CORP`), so store the natural name in the
  config.
- With no tickets, the legacy output has the header and `Total breaches: 0`, and no escalation line.
- `validate()` checks that every alias target has an SLA, and that every SLA is positive. Call it at the start of
  `build_report`, so a bad config fails loudly rather than raising a `KeyError` halfway through.
- The test reads `build_report`'s source code for customer names. Default values in the config class are a common
  place for them to leak in.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_parity_with_legacy` | Header case, sort order or float formatting differs; escalation line printed with zero breaches |
| `test_other_customer` | Offset or alias lookup still hard-coded; alias lookup not case-insensitive |
| `test_unknown_priority_without_normal_sla_is_config_error` | `validate` doesn't check alias targets against the SLA keys, or allows a 0-hour SLA |
| `test_no_customer_names_in_library_code` | A customer name or address appears in `build_report` |
