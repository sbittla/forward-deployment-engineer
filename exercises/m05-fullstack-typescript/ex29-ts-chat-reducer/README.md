# ex29 · TypeScript: chat UI state reducer

**Module:** m05 · **Covers:** R02 TypeScript/full-stack · **Time:** 45 min

## Scenario
Your copilot demo's chat widget has state bugs: double-sends while streaming, retry duplicates messages, and an
error leaves the spinner on forever. Pull all state transitions into one **pure reducer** you can unit test —
the same pattern React's `useReducer` and Redux use.

## Your task (`starter.ts`)
`reduce(state: ChatState, action: Action): ChatState` — must never mutate `state`.

```ts
type Msg = { id: string; role: "user" | "assistant"; text: string; status: "done" | "streaming" | "error" };
type ChatState = { messages: Msg[]; pending: boolean; error: string | null };
```

| Action | Effect |
|---|---|
| `{type:"send", id, text}` | ignored if `pending` or `text.trim()===""`; else append user msg (`done`), `pending=true`, `error=null` |
| `{type:"stream_start", id}` | append assistant msg `{text:"", status:"streaming"}` |
| `{type:"delta", id, text}` | append text to that assistant msg (ignore unknown ids) |
| `{type:"stream_end", id}` | status `done`, `pending=false` |
| `{type:"stream_error", id, error}` | status `error`, `pending=false`, `error=<error>` |
| `{type:"retry"}` | if the last message is an assistant `error`: remove it, `pending=true`, `error=null`; else no-op |
| `{type:"clear"}` | back to `initialState` |

Also export `initialState` and `transcript(state): string` → lines `"user: ..."`/`"assistant: ..."` for `done`
messages only, joined with `\n`.

## Run
```
node --test exercises/m05-fullstack-typescript/ex29-ts-chat-reducer/reducer.test.ts
```
