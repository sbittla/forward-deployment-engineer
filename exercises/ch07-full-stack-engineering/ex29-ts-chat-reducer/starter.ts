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

export function reduce(state: ChatState, action: Action): ChatState {
  throw new Error("not implemented");
}

export function transcript(state: ChatState): string {
  throw new Error("not implemented");
}
