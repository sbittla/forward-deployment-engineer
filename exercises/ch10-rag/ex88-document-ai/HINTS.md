# ex88 hints · Document AI: layout-aware extraction from OCR output and PDF/vision requests

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Everything builds on line grouping, so start there. Work with each word's **vertical centre** (`(y0 + y1) / 2`). Sort
the words by page, centre and `x0`, then put each word into the first existing group on the same page whose
first-word centre is within `y_tol`, or start a new group. Sort each group's words by `x0` to read them left to right.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Line confidence** is the **minimum** of its words' confidences. One shaky word makes the whole value shaky.
- **key_values:** find the first line that starts with the label (case-insensitive) and take the rest of it, stripped
  of spaces, `:` and `#`. If nothing is left, use the next line, as long as it's on the same page.
- **extract_table:** find the header line on the page, take each header's `x0` as the start of its column (the next
  header's `x0` is the end; the last column runs to infinity), and assign each following word by its horizontal
  centre. Stop at the first row with nothing in the first column.
- **vision_request:** map the lowercased extension to `(block type, media type)`, check the size, base64-encode the
  file, and put the file block **before** the text block.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- OCR baselines wobble: `Number:` sits at y=61 while `POL-882311` sits at y=59. That's what the tolerance is for.
  Compare centres, not tops.
- "Claimant Name" has its value on the **next** line in the sample, with confidence 0.62, so `route` sends it to a
  human.
- The `Total` row has no word in the Item column, which is how the table knows to stop.
- `.PNG` in upper case must work: lowercase the suffix. Reject unsupported types and files over 32 MB with
  `ValueError`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_group_lines` | Grouping by exact `y0` instead of centre within tolerance; line confidence averaged instead of the minimum |
| `test_key_values` | Next-line fallback missing; `:` not stripped; a missing label raises instead of being absent |
| `test_table` | Columns assigned by `x0` instead of centre; multi-word cells not joined; total row included |
| `test_route` | Reasons not in order (missing first, then low confidence) |
| `test_vision_request` | Text block placed before the file; extension compared case-sensitively; `.jpeg` not mapped to `image/jpeg` |
| `test_vision_request_rejects_oversized_file` | Size compared with `>=` instead of `>`, or checked after reading and encoding the whole file |
