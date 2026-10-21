# ex29 · TypeScript: chat UI state reducer

**Chapter:** 7 · Full-Stack Engineering (`exercises/ch07-full-stack-engineering/`) · **Covers:** R02 TypeScript/full-stack

## Learning objectives
- Model chat UI state transitions as a pure reducer.
- Prevent double-sends, duplicate retries and stuck spinners.
- Model user cancellation and session expiry as their own states, not as generic errors.
- Unit test UI behavior without a browser.

## Scenario
Your copilot demo's chat widget has state bugs: double-sends while streaming, retry duplicates messages, and an
error leaves the spinner on forever. Pull all state transitions into one **pure reducer** you can unit test —
the same pattern React's `useReducer` and Redux use.

## Your task (`starter.ts`)
`reduce(state: ChatState, action: Action): ChatState` — must never mutate `state`.

```ts
type Msg = { id: string; role: "user" | "assistant"; text: string; status: "done" | "streaming" | "error" | "stopped" };
type ChatState = { messages: Msg[]; pending: boolean; error: string | null };
```

| Action | Effect |
|---|---|
| `{type:"send", id, text}` | ignored if `pending` or `text.trim()===""`; else append user msg (`done`), `pending=true`, `error=null` |
| `{type:"stream_start", id}` | append assistant msg `{text:"", status:"streaming"}` |
| `{type:"delta", id, text}` | append text to that assistant msg if it is `streaming` (ignore unknown ids and deltas for a stopped or failed msg) |
| `{type:"stream_end", id}` | status `done`, `pending=false` |
| `{type:"stream_error", id, error}` | status `error`, `pending=false`, `error=<error>` |
| `{type:"cancel"}` | the user pressed Stop: if not `pending`, no-op (same object); else every `streaming` msg becomes `stopped` (text kept), `pending=false`, `error=null` |
| `{type:"auth_expired"}` | the BFF answered 401: every `streaming` msg becomes `error`, `pending=false`, `error=SESSION_EXPIRED`; the user's question is kept |
| `{type:"retry"}` | no-op (same object) when `error === SESSION_EXPIRED`; if the last message is an assistant `error`: remove it, `pending=true`, `error=null`; else no-op |
| `{type:"clear"}` | back to `initialState` |

The starter exports `SESSION_EXPIRED = "Your session has expired. Sign in again."`. Also export `initialState` and
`transcript(state): string` → lines `"user: ..."`/`"assistant: ..."` for `done`
messages only, joined with `\n`.

## Run
```
node --test exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/reducer.test.ts
```

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root;
  Node.js 22.18 or later (24 LTS recommended) for the TypeScript tests, with no `npm install`. No API key or network
  access is needed.
- **Run your work:** from the repository root,
  `node --test exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/reducer.test.ts`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:**
  `FDE_SOLUTIONS=1 node --test exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/reducer.test.ts`
  (PowerShell:
  `$env:FDE_SOLUTIONS=1; node --test exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/reducer.test.ts`):
  all 7 pass.
- **Tests:** `reducer.test.ts` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root; a Node.js error about the `.ts` extension means Node is older than 22.18. For a failing test,
  [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The reducer models one stream at a time. A production version is driven by a hook with
  timeouts (ex28's `streamAnswer` and ex91's hook), keeps the user's draft across sign-in, and lets the user edit and
  resend a stopped question.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "TypeScript: chat UI state reducer".
Before I write code, teach me reducers and immutable state updates, the useReducer pattern, and the chat streaming
lifecycle. Use short TypeScript examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/starter.ts so that reducer.test.ts passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`initialState`, `reduce`, `transcript`. Constraints: TypeScript executed directly by Node 22.18+ type stripping: no
npm packages, no build step, and only erasable type syntax (no enums, namespaces or parameter properties). Do not
modify the tests. When you're done, run `node --test
exercises/ch07-full-stack-engineering/ex29-ts-chat-reducer/reducer.test.ts` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "TypeScript: chat UI state reducer" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does any action mutate the previous state object or arrays? Is retry a no-op in
every state where it should be? What race would still exist when wired to a real stream? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
