// Renders a copilot response for the agent desktop widget.
// Security: every piece of model or customer text is HTML-escaped before markup is added.

export type CopilotResponse = {
  intent: string;
  text: string;
  citations: string[];
  chunk_ids: string[];
  abstained: boolean;
  escalated: boolean;
};

export function escapeHtml(s: string): string {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function renderAnswer(r: CopilotResponse): string {
  if (r.escalated) return '<div class="answer escalated">' + escapeHtml(r.text) + "</div>";
  if (r.abstained) return '<div class="answer abstained">' + escapeHtml(r.text) + "</div>";
  const body = escapeHtml(r.text).replace(/\[(\d+)\]/g, (_m, n) => `<sup><a href="#src-${n}">${n}</a></sup>`);
  const sources = r.chunk_ids
    .map((id, i) => `<li id="src-${i + 1}">${escapeHtml(id)}</li>`)
    .join("");
  return `<div class="answer"><p>${body}</p><ol class="sources">${sources}</ol></div>`;
}
