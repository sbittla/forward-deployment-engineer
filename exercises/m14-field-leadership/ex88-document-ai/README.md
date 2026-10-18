# ex88 · Document AI: layout-aware extraction from OCR output and PDF/vision requests

**Module:** m14 · **Covers:** R38 Document & multimodal AI, R08 LLM apps, R14 Human-in-the-loop · **Time:** 75 min

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
