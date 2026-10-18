export type Msg = { id: string; role: "user" | "assistant"; text: string; status: "done" | "streaming" | "error" };
export type ChatState = { messages: Msg[]; pending: boolean; error: string | null };
export type Action =
  | { type: "send"; id: string; text: string }
  | { type: "stream_start"; id: string }
  | { type: "delta"; id: string; text: string }
  | { type: "stream_end"; id: string }
  | { type: "stream_error"; id: string; error: string }
  | { type: "retry" }
  | { type: "clear" };

export const initialState: ChatState = { messages: [], pending: false, error: null };

export function reduce(state: ChatState, action: Action): ChatState {
  throw new Error("not implemented");
}

export function transcript(state: ChatState): string {
  throw new Error("not implemented");
}
