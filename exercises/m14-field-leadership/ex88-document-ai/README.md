# ex88 · Document AI: layout-aware extraction from OCR output and PDF/vision requests

**Module:** m14 · **Covers:** R38 Document & multimodal AI, R08 LLM apps, R14 Human-in-the-loop · **Time:** 75 min

## Learning objectives
- Reconstruct lines, key-value pairs and tables from OCR words with boxes.
- Route low-confidence or missing fields to human review.
- Build PDF and image requests for multimodal models.

## Scenario
Insurance, banking and healthcare customers run on scanned forms, PDFs and photos. OCR services (AWS Textract,
Azure Document Intelligence, Google Document AI) return **words with bounding boxes and confidences**, not tidy
text. Modern models can also read PDFs and images directly. You need both paths, plus a rule for when a human
must look.

## Your task
OCR words: `{"text", "page", "x0", "y0", "x1", "y1", "conf"}` (y grows downward).

1. `group_lines(words, y_tol=5) -> list[Line(page, y, text, conf)]`: per page, a word joins a line when its vertical
   center is within `y_tol` of the line's first word's center; words in a line are ordered by `x0` and joined with a
   space; `y` = the first word's center (rounded to 1 dp); `conf` = the minimum word confidence. Lines are sorted by
   page then `y`.
2. `key_values(lines, labels) -> {label: (value, conf)}`: find the first line whose text starts with the label
   (case-insensitive). The value is the rest of that line after the label, stripped of leading `:`/`#` and spaces;
   if that's empty, use the next line on the same page. Missing labels are absent from the result.
3. `extract_table(words, headers, page) -> list[dict]`: find the line containing all header words; each header's
   column spans from its `x0` to the next header's `x0` (last column to infinity). Assign each word on the following
   lines to a column by its horizontal center. Stop at the first line that has no word in the first column.
4. `route(fields, required, min_conf=0.85) -> (decision, reasons)`: `"human_review"` with reasons
   `missing:<label>` / `low_confidence:<label>` (in `required` order, then the low-confidence ones for any field),
   else `"auto"` with `[]`.
5. `vision_request(path, question) -> list[dict]`: Messages API user content. `.pdf` →
   `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": ...}}`; `.png`,
   `.jpg`/`.jpeg`, `.gif`, `.webp` → `{"type": "image", "source": {"type": "base64", "media_type": ...}}`; the text
   question block comes **after** the file block. Unsupported extension or a file over 32 MB → `ValueError`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Document AI: layout-aware extraction
from OCR output and PDF/vision requests". Before I write code, teach me document AI: OCR output with bounding boxes
and confidences, layout reconstruction, table extraction, confidence-based routing, and sending PDFs/images to
multimodal models. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m14-field-leadership/ex88-document-ai/starter.py so that test_document_ai.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Line`,
`group_lines`, `key_values`, `extract_table`, `route`, `vision_request`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/m14-field-leadership/ex88-document-ai` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Document AI: layout-aware extraction from OCR output and PDF/vision requests" as a senior
forward deployed engineer would before it ships to a customer. Specifically: Is line grouping stable when words are
slightly skewed? Does table extraction stop at the right row? Are low-confidence fields routed even when present?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
Read the attached claim form (PDF). Extract: policy_number, claimant_name, date_of_loss (YYYY-MM-DD), loss_description, and estimated_amount (number). Return only JSON. For each field also return a confidence of high, medium or low. Use null and low confidence when a field is unreadable or missing; do not infer values from other fields.
```
