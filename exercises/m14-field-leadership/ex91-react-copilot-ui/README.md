# ex91 · React copilot UI component and hook without a build step

**Module:** m14 · **Covers:** R02 Full-stack/TypeScript, R21 Prototyping · **Hands-on:** React · **Time:** 75 min

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
Implement exercises/m14-field-leadership/ex91-react-copilot-ui/starter.ts so that panel.test.ts passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `initialState`,
`chatReducer`, `makeUseChat`, `makeCopilotPanel`. Constraints: TypeScript executed directly by Node 22.18+ type
stripping: no npm packages, no build step, and only erasable type syntax (no enums, namespaces or parameter
properties). Do not modify the tests. When you're done, run `node --test
exercises/m14-field-leadership/ex91-react-copilot-ui/panel.test.ts` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "React copilot UI component and hook without a build step" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does any reducer case mutate state? Is the message list
announced to screen readers? Does retry re-send the last user message exactly once? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
