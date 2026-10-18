// Renders a copilot response for the agent desktop widget.
// Security: every piece of model or customer text must be HTML-escaped before markup is added.

export type CopilotResponse = {
  intent: string;
  text: string;
  citations: string[];
  chunk_ids: string[];
  abstained: boolean;
  escalated: boolean;
};

export function escapeHtml(s: string): string {
  throw new Error("not implemented");
}

export function renderAnswer(r: CopilotResponse): string {
  throw new Error("not implemented");
}
