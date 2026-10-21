export type Msg = { id: string; role: "user" | "assistant"; text: string; status: "done" | "streaming" | "error" | "stopped" };
export type ChatState = { messages: Msg[]; pending: boolean; error: string | null };
export type Action =
  | { type: "send"; id: string; text: string }
  | { type: "stream_start"; id: string }
  | { type: "delta"; id: string; text: string }
  | { type: "stream_end"; id: string }
  | { type: "stream_error"; id: string; error: string }
  | { type: "cancel" }
  | { type: "auth_expired" }
  | { type: "retry" }
  | { type: "clear" };

export const SESSION_EXPIRED = "Your session has expired. Sign in again.";

export const initialState: ChatState = { messages: [], pending: false, error: null };

function patch(state: ChatState, id: string, f: (m: Msg) => Msg): Msg[] {
  return state.messages.map((m) => (m.id === id && m.role === "assistant" ? f(m) : m));
}

export function reduce(state: ChatState, action: Action): ChatState {
  switch (action.type) {
    case "send":
      if (state.pending || action.text.trim() === "") return state;
      return {
        messages: [...state.messages, { id: action.id, role: "user", text: action.text, status: "done" }],
        pending: true,
        error: null,
      };
    case "stream_start":
      return { ...state, messages: [...state.messages, { id: action.id, role: "assistant", text: "", status: "streaming" }] };
    case "delta":  // only a streaming message grows: deltas that arrive after cancel or an error are dropped
      return { ...state, messages: patch(state, action.id, (m) => (m.status === "streaming" ? { ...m, text: m.text + action.text } : m)) };
    case "stream_end":
      return { ...state, pending: false, messages: patch(state, action.id, (m) => ({ ...m, status: "done" })) };
    case "stream_error":
      return { ...state, pending: false, error: action.error, messages: patch(state, action.id, (m) => ({ ...m, status: "error" })) };
    case "cancel":
      if (!state.pending) return state;
      return { ...state, pending: false, error: null,
        messages: state.messages.map((m) => (m.status === "streaming" ? { ...m, status: "stopped" } : m)) };
    case "auth_expired":
      return { ...state, pending: false, error: SESSION_EXPIRED,
        messages: state.messages.map((m) => (m.status === "streaming" ? { ...m, status: "error" } : m)) };
    case "retry": {
      if (state.error === SESSION_EXPIRED) return state;  // sign in first; a retry would only earn another 401
      const last = state.messages[state.messages.length - 1];
      if (!last || last.role !== "assistant" || last.status !== "error") return state;
      return { messages: state.messages.slice(0, -1), pending: true, error: null };
    }
    case "clear":
      return initialState;
    default:
      return state;
  }
}

export function transcript(state: ChatState): string {
  return state.messages.filter((m) => m.status === "done").map((m) => `${m.role}: ${m.text}`).join("\n");
}
