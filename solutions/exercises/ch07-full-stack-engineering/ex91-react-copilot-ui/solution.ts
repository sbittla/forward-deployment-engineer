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

export type CreateElement = (type: string, props: Record<string, unknown> | null, ...children: unknown[]) => unknown;
export type UseReducer = <S, A>(reducer: (s: S, a: A) => S, init: S) => [S, (a: A) => void];

export function chatReducer(state: ChatState, action: Action): ChatState {
  switch (action.type) {
    case "draft":
      return { ...state, draft: action.text };
    case "send": {
      const text = state.draft.trim();
      if (state.pending || !text) return state;
      return { ...state, draft: "", pending: true, error: null, stopped: false,
        messages: [...state.messages, { id: action.id, role: "user", text }] };
    }
    case "reply":
      return { ...state, pending: false, messages: [...state.messages, { id: action.id, role: "assistant", text: action.text }] };
    case "fail":
      return { ...state, pending: false, error: action.error };
    case "retry":
      if (state.authExpired) return state;  // sign in first: a retry would only earn another 401
      return { ...state, error: null, pending: true, stopped: false };
    case "cancel":
      if (!state.pending) return state;
      return { ...state, pending: false, error: null, stopped: true };
    case "auth_expired":
      return { ...state, pending: false, error: SESSION_EXPIRED, authExpired: true };
    default:
      return state;
  }
}

export type SendToApi = (text: string, signal?: AbortSignal) => Promise<string>;

function isAuthError(err: unknown): boolean {
  const e = err as { name?: string; status?: number } | null;
  return !!e && (e.name === "AuthExpiredError" || e.status === 401);
}

export function makeUseChat(useReducer: UseReducer, sendToApi: SendToApi) {
  let counter = 0;
  const nextId = () => `m${++counter}`;
  let inflight: AbortController | null = null;  // like the counter, shared across renders
  return function useChat() {
    const [state, dispatch] = useReducer<ChatState, Action>(chatReducer, initialState);
    async function call(text: string) {
      const ctrl = new AbortController();
      inflight = ctrl;
      try {
        const answer = await sendToApi(text, ctrl.signal);  // take an id only once there is a reply to show
        if (!ctrl.signal.aborted) dispatch({ type: "reply", id: nextId(), text: answer });
      } catch (err) {
        if (ctrl.signal.aborted) return;                     // stop() already dispatched cancel
        if (isAuthError(err)) dispatch({ type: "auth_expired" });
        else dispatch({ type: "fail", error: err instanceof Error ? err.message : String(err) });
      } finally {
        if (inflight === ctrl) inflight = null;
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
      stop() {
        if (!inflight) return;
        inflight.abort();
        dispatch({ type: "cancel" });
      },
      async retry() {
        if (state.authExpired) return;
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
  onStop?: () => void;
  onSignIn?: () => void;
};

export function makeCopilotPanel(h: CreateElement) {
  return function CopilotPanel({ state, title, onDraft, onSend, onRetry, onStop, onSignIn }: PanelProps) {
    // Text is passed as children, so React escapes it; nothing here uses dangerouslySetInnerHTML.
    const items = state.messages.map((msg) => h("li", { key: msg.id, "data-role": msg.role }, msg.text));
    return h("section", { "aria-label": title },
      h("h2", null, title),
      h("ul", { role: "log", "aria-live": "polite" }, ...items),
      // Each failure state: plain text in an announced region, and one labeled, keyboard-reachable action.
      state.authExpired
        ? h("div", { role: "alert" }, SESSION_EXPIRED,
            h("button", { type: "button", onClick: () => onSignIn?.() }, "Sign in"))
        : state.error
          ? h("div", { role: "alert" }, state.error, h("button", { type: "button", onClick: () => onRetry() }, "Retry"))
          : null,
      state.stopped ? h("p", { role: "status" }, STOPPED) : null,
      h("form", { onSubmit: (e: { preventDefault: () => void }) => { e.preventDefault(); onSend(); } },
        h("input", { value: state.draft, "aria-label": "Message",
          onChange: (e: { target: { value: string } }) => onDraft(e.target.value) }),
        h("button", { type: "submit", disabled: state.pending }, "Send"),
        state.pending ? h("button", { type: "button", onClick: () => onStop?.() }, "Stop") : null),
    );
  };
}
