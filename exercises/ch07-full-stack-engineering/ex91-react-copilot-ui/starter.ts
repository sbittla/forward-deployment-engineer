export type Msg = { id: string; role: "user" | "assistant"; text: string };
export type ChatState = { messages: Msg[]; pending: boolean; error: string | null; draft: string };
export type Action =
  | { type: "draft"; text: string }
  | { type: "send"; id: string }
  | { type: "reply"; id: string; text: string }
  | { type: "fail"; error: string }
  | { type: "retry" };

export const initialState: ChatState = { messages: [], pending: false, error: null, draft: "" };

// Signature-compatible with React.createElement and React.useReducer.
export type CreateElement = (type: string, props: Record<string, unknown> | null, ...children: unknown[]) => unknown;
export type UseReducer = <S, A>(reducer: (s: S, a: A) => S, init: S) => [S, (a: A) => void];

export function chatReducer(state: ChatState, action: Action): ChatState {
  throw new Error("not implemented");
}

export function makeUseChat(useReducer: UseReducer, sendToApi: (text: string) => Promise<string>) {
  throw new Error("not implemented");
}

export function makeCopilotPanel(h: CreateElement) {
  throw new Error("not implemented");
}
