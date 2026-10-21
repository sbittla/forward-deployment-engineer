# ex94 hints · Blameless postmortem and customer incident communications

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`status_update` is mostly string assembly: the stage template, then `Impact: …`, then the next-update line (except
when resolved), then the ETA if one is given, joined with single spaces. Put the jargon, IP and email checks **first**,
so a bad update never gets built.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Jargon:** match each term as a whole word on the lowercased text (`\bpod\b`), so ordinary words that contain a
  term aren't flagged.
- **impact_summary:** sort the events by time, keep the first timestamp seen for each type, and compute whole minutes
  between `detected` and `resolved`, and between `detected` and `mitigated`. The peak is the maximum
  `affected_users`.
- **blame_lint:** one regex with alternatives: the fixed phrases, plus a capitalised name followed by
  broke/caused/forgot/missed. `finditer` returns the matches in order.
- **render_postmortem:** lint first, validate the action items next, then render.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Don't double the full stop: if the impact text already ends with `.`, strip it before adding `Impact: ….`.
- `\bfault\b` needs word boundaries, or "default" in a perfectly blameless root cause gets flagged.
- The name pattern is case-sensitive on purpose (`Priya forgot`, `Sam broke`); "the client library defaulted" is
  blameless.
- Timeline times come from the ISO timestamps formatted as `%H:%M`, followed by `UTC`.
- An action with an empty owner (or no due date) raises `ValueError`. An action nobody owns doesn't get done.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_status_updates` | Next-update line included when resolved; spacing or punctuation differs from the template |
| `test_status_rejects_jargon_and_pii` | Jargon matched case-sensitively; IP or email not checked |
| `test_impact` | Minutes measured from the wrong events; events not sorted by time |
| `test_blame_lint` | Matches out of order; name pattern too broad (flags blameless sentences) |
| `test_postmortem` | Sections out of order; blame not checked in the root cause; missing owner accepted |
| `test_postmortem_requires_fields` | A blank root cause, an empty action list or a timeline without `resolved` accepted |
