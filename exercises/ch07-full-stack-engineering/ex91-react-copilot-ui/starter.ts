export type Msg = { id: string; role: "user" | "assistant"; text: string };
export type ChatState = {
  messages: Msg[]; pending: boolean; error: string | null; draft: string; stopped: boolean; authExpired: boolean;
};
export type Action =
  | { type: "draft"; text: string }
  | { type: "send"; id: string }
  | { type: "reply"; id: string; text: string }
  | { type: "fail"; error: string }
  | { type: "retry" }
  | { type: "cancel" }
  | { type: "auth_expired" };

export const SESSION_EXPIRED = "Your session has expired. Sign in again.";
export const STOPPED = "Stopped. Edit your question or send it again.";

export const initialState: ChatState = {
  messages: [], pending: false, error: null, draft: "", stopped: false, authExpired: false,
};

// Signature-compatible with React.createElement and React.useReducer.
export type CreateElement = (type: string, props: Record<string, unknown> | null, ...children: unknown[]) => unknown;
export type UseReducer = <S, A>(reducer: (s: S, a: A) => S, init: S) => [S, (a: A) => void];

export function chatReducer(state: ChatState, action: Action): ChatState {
  throw new Error("not implemented");
}

export type SendToApi = (text: string, signal?: AbortSignal) => Promise<string>;

export function makeUseChat(useReducer: UseReducer, sendToApi: SendToApi) {
  throw new Error("not implemented");
}

export function makeCopilotPanel(h: CreateElement) {
  throw new Error("not implemented");
}
