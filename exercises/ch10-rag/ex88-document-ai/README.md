# ex88 · Document AI: layout-aware extraction from OCR output and PDF/vision requests

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R38 Document & multimodal AI, R08 LLM apps, R14 Human-in-the-loop

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch10-rag/ex88-document-ai`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch10-rag/ex88-document-ai`: all 6 pass.
- **Tests:** `test_document_ai.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The OCR words are synthetic and well aligned, and `vision_request` only builds the request.
  Real scans need skew, multi-column and multi-page handling, thresholds tuned on measured field accuracy, a
  human-review queue with an audit trail, and file limits checked against the approved provider's current
  documentation (as of October 2026 they change regularly).

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
Implement exercises/ch10-rag/ex88-document-ai/starter.py so that test_document_ai.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Line`,
`group_lines`, `key_values`, `extract_table`, `route`, `vision_request`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch10-rag/ex88-document-ai` and show me the output.
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
