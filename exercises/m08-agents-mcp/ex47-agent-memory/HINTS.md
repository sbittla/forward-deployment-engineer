# ex47 hints · Conversation memory and summarisation

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Keep three pieces of state: the running summary string (starting as `""`), the list of un-summarised messages, and a
dict of pins. `context()` only reads them, so write it first and get `test_pins` and `test_empty_memory_context`
passing before you write the folding logic.
</details>

<details>
<summary>Hint 2 · The approach</summary>

In `add`, append the message, then loop: **while** the un-summarised total is over budget *and* there are more than
`keep_recent` messages:

- take everything except the last `keep_recent` messages as the batch to fold;
- build the prompt with the previous summary and the batch as `role: content` lines;
- call the model once, replace the summary with its reply, remove the folded messages, and increment the counter.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The first prompt still contains the tags with an empty summary inside them: `<previous_summary></previous_summary>`.
- Both conditions are needed. With `keep_recent=3` and three huge messages, nothing can be folded, so the loop must
  stop rather than call the model over and over.
- The system prompt must mention keeping **numbers** (and names, decisions and open questions). The test checks for
  the word.
- In `context()`, sort pins by key and join the two parts with a blank line. With neither part, return `""`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_no_summary_under_budget` | Summarising even when under budget, or returning an addendum with empty headings |
| `test_rolls_up_oldest` | Folding the recent messages too; previous summary not passed into the next prompt |
| `test_keep_recent_respected` | Missing the `len(messages) > keep_recent` condition |
| `test_pins` | Pins not sorted by key, or re-pinning appends instead of overwriting |
| `test_empty_memory_context` | `context()` fails on a fresh instance or returns `None` |
