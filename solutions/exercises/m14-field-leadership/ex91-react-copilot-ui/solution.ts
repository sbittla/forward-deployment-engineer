export type Msg = { id: string; role: "user" | "assistant"; text: string };
export type ChatState = { messages: Msg[]; pending: boolean; error: string | null; draft: string };
export type Action =
  | { type: "draft"; text: string }
  | { type: "send"; id: string }
  | { type: "reply"; id: string; text: string }
  | { type: "fail"; error: string }
  | { type: "retry" };

export const initialState: ChatState = { messages: [], pending: false, error: null, draft: "" };

export type CreateElement = (type: string, props: Record<string, unknown> | null, ...children: unknown[]) => unknown;
export type UseReducer = <S, A>(reducer: (s: S, a: A) => S, init: S) => [S, (a: A) => void];

export function chatReducer(state: ChatState, action: Action): ChatState {
  switch (action.type) {
    case "draft":
      return { ...state, draft: action.text };
    case "send": {
      const text = state.draft.trim();
      if (state.pending || !text) return state;
      return { ...state, draft: "", pending: true, error: null,
        messages: [...state.messages, { id: action.id, role: "user", text }] };
    }
    case "reply":
      return { ...state, pending: false, messages: [...state.messages, { id: action.id, role: "assistant", text: action.text }] };
    case "fail":
      return { ...state, pending: false, error: action.error };
    case "retry":
      return { ...state, error: null, pending: true };
    default:
      return state;
  }
}

export function makeUseChat(useReducer: UseReducer, sendToApi: (text: string) => Promise<string>) {
  let counter = 0;
  const nextId = () => `m${++counter}`;
  return function useChat() {
    const [state, dispatch] = useReducer<ChatState, Action>(chatReducer, initialState);
    async function call(text: string) {
      try {
        const answer = await sendToApi(text);  // take an id only once there is a reply to show
        dispatch({ type: "reply", id: nextId(), text: answer });
      } catch (err) {
        dispatch({ type: "fail", error: err instanceof Error ? err.message : String(err) });
      }
    }
    return {
      state,
      setDraft: (text: string) => dispatch({ type: "draft", text }),
      async send() {
        const text = state.draft.trim();
        if (state.pending || !text) return;
        dispatch({ type: "send", id: nextId() });
        await call(text);
      },
      async retry() {
        const last = [...state.messages].reverse().find((x) => x.role === "user");
        if (!last) return;
        dispatch({ type: "retry" });
        await call(last.text);
      },
    };
  };
}

type PanelProps = {
  state: ChatState;
  title: string;
  onDraft: (text: string) => void;
  onSend: () => void;
  onRetry: () => void;
};

export function makeCopilotPanel(h: CreateElement) {
  return function CopilotPanel({ state, title, onDraft, onSend, onRetry }: PanelProps) {
    // Text is passed as children, so React escapes it; nothing here uses dangerouslySetInnerHTML.
    const items = state.messages.map((msg) => h("li", { key: msg.id, "data-role": msg.role }, msg.text));
    return h("section", { "aria-label": title },
      h("h2", null, title),
      h("ul", { role: "log", "aria-live": "polite" }, ...items),
      state.error
        ? h("div", { role: "alert" }, state.error, h("button", { type: "button", onClick: () => onRetry() }, "Retry"))
        : null,
      h("form", { onSubmit: (e: { preventDefault: () => void }) => { e.preventDefault(); onSend(); } },
        h("input", { value: state.draft, "aria-label": "Message",
          onChange: (e: { target: { value: string } }) => onDraft(e.target.value) }),
        h("button", { type: "submit", disabled: state.pending }, "Send")),
    );
  };
}
