# ex91 · React copilot UI component and hook without a build step

**Chapter:** 7 · Full-Stack Engineering (`exercises/ch07-full-stack-engineering/`) · **Covers:** R02 Full-stack/TypeScript, R21 Prototyping · **Hands-on:** React

## Learning objectives
- Write a React component and hook against React's own APIs, injected as factories.
- Keep chat state transitions pure and accessible markup correct.
- Test React logic in plain Node without a bundler.

## Scenario
60% of FDE postings mention TypeScript, JavaScript or full-stack work; OpenAI asks for full-stack engineers and
Palantir for "front-end frameworks". Most customer front ends are React. Here you write a real React component and hook, authored against
React's own `createElement` and `useReducer` APIs and injected as factories. That way they drop into the customer's
app unchanged (`makeCopilotPanel(React.createElement)`), yet they test in plain Node with no bundler or JSX
transform.

## Your task (`starter.ts`)
1. `chatReducer(state, action)` (state `{messages, pending, error, draft}`; the starter exports `initialState`) handling `draft`, `send` (ignored
   when pending or the trimmed draft is empty; appends a user message with `id`, clears the draft, sets pending),
   `reply` (appends an assistant message, clears pending), `fail` (sets error, clears pending), `retry` (clears
   error, sets pending). Never mutate the state.
2. `makeUseChat(useReducer, sendToApi)` returns a hook `useChat()` → `{state, setDraft(text), send(), retry()}`.
   `send()` dispatches `send`, then calls `sendToApi(text)` and dispatches `reply` with the answer or `fail` with
   the error message. `retry()` re-sends the last user message. Generate ids as `m1`, `m2`… from one counter per
   `makeUseChat` call, shared by every hook it returns (a counter inside `useChat` would reset on each render).
3. `makeCopilotPanel(h)` returns a component `CopilotPanel(props)` where props are `{state, onDraft, onSend,
   onRetry, title}`, rendering:
   - `section` with `aria-label` = title, containing an `h2` with the title
   - `ul` with `role="log"` and `aria-live="polite"`; one `li` per message with `key` = id, `data-role` = role,
     and the text as a child (**never** `dangerouslySetInnerHTML`)
   - when `state.error`: a `div` with `role="alert"` showing the error and a `button` "Retry" whose `onClick`
     calls `onRetry`
   - a `form` whose `onSubmit(e)` calls `e.preventDefault()` then `onSend()`; inside it an `input` (`value` =
     draft, `onChange(e)` → `onDraft(e.target.value)`, `aria-label` "Message") and a submit `button` "Send" with
     `disabled` = pending

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root;
  Node.js 22.18 or later (24 LTS recommended) for the TypeScript tests, with no `npm install`. No API key or network
  access is needed.
- **Run your work:** from the repository root,
  `node --test exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/panel.test.ts`.
- **Expected output:** all 3 tests fail against the starter; when you're done, all 3 pass.
- **Check the reference solution:**
  `FDE_SOLUTIONS=1 node --test exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/panel.test.ts`
  (PowerShell:
  `$env:FDE_SOLUTIONS=1; node --test exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/panel.test.ts`): all
  3 pass.
- **Tests:** `panel.test.ts` (3 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root; a Node.js error about the `.ts` extension means Node is older than 22.18. For a failing test,
  [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The hook calls a non-streaming `sendToApi` with no timeout or cancellation, and shows
  whatever message the thrown error carries. In production, map errors to plain user-facing messages (never raw
  exception text), abort in-flight requests on unmount or Stop with an `AbortController`, and test the rendered panel
  with axe and a real screen reader.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "React copilot UI component and hook
without a build step". Before I write code, teach me React's createElement and useReducer APIs, dependency injection
for testability, ARIA live regions, and safe rendering without dangerouslySetInnerHTML. Use short TypeScript
examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a time,
and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/starter.ts so that panel.test.ts passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `initialState`,
`chatReducer`, `makeUseChat`, `makeCopilotPanel`. Constraints: TypeScript executed directly by Node 22.18+ type
stripping: no npm packages, no build step, and only erasable type syntax (no enums, namespaces or parameter
properties). Do not modify the tests. When you're done, run `node --test
exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/panel.test.ts` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "React copilot UI component and hook without a build step" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does any reducer case mutate state? Is the message list
announced to screen readers? Does retry re-send the last user message exactly once? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
