# ex02 hints · Discovery interview to user stories

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `parse_stories` first. It's pure, it takes most of the tests, and `extract` is a short loop around it. Get it
right on a clean JSON string, then add fence handling, then each validation rule.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- If the reply contains a ```` ``` ```` fence (with or without `json`), parse what's inside it. Otherwise parse the
  whole reply.
- Turn `json.JSONDecodeError` into a `ValueError` whose message says the reply isn't valid JSON.
- Check each story in a fixed order: is it an object, are the four keys present, are the three text fields non-empty
  strings, is `acceptance_criteria` a non-empty list of strings. Put the key's name in each message.
- Remove duplicates with a `seen` set of `(as_a.lower(), i_want.lower())`, keeping the first occurrence.
- In `extract`, keep a growing `messages` list. On failure, append the model's reply as `assistant` and the error as
  `user`, then try again.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `Story.acceptance_criteria` is compared with a **tuple**. Convert the list before you store it.
- The retry message must mention JSON (the test checks the last user message). Telling the model "return only the
  JSON array" is also the instruction that actually fixes the reply.
- `llm.complete(...)` returns a response object. The text is on `.text`.
- After `max_attempts` failures, raise a `ValueError`. Don't return an empty list: a silent empty result is the worst
  outcome on site.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_prompt_shape` | Transcript not wrapped in `<transcript>` tags, or the system prompt doesn't name `acceptance_criteria` |
| `test_parse_dedupes_and_handles_fence` | Fence regex isn't non-greedy or misses `json` after the backticks; dedupe is case-sensitive; criteria kept as a list |
| `test_parse_rejects` | An error message that doesn't name the problem field (`i_want`, `acceptance_criteria`) or say `json` |
| `test_extract_retries_with_error_feedback` | Retry builds a fresh message list instead of appending the bad reply and the error |
| `test_extract_gives_up` | Loop returns `[]` or `None` after the last attempt instead of raising |
