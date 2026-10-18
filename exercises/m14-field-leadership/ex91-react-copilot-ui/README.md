# ex91 · React copilot UI component and hook without a build step

**Module:** m14 · **Covers:** R02 Full-stack/TypeScript, R21 Prototyping · **Hands-on:** React · **Time:** 75 min

## Scenario
28% of FDE postings mention front-end work; OpenAI asks for full-stack engineers and Palantir for "front-end
frameworks". Most customer front ends are React. Here you write a real React component and hook, authored against
React's own `createElement` and `useReducer` APIs and injected as factories. That way they drop into the customer's
app unchanged (`makeCopilotPanel(React.createElement)`), yet they test in plain Node with no bundler or JSX
transform.

## Your task (`starter.ts`)
1. `chatReducer(state, action)` (state `{messages, pending, error, draft}`) handling `draft`, `send` (ignored
   when pending or the trimmed draft is empty; appends a user message with `id`, clears the draft, sets pending),
   `reply` (appends an assistant message, clears pending), `fail` (sets error, clears pending), `retry` (clears
   error, sets pending). Never mutate the state.
2. `makeUseChat(useReducer, sendToApi)` returns a hook `useChat()` → `{state, setDraft(text), send(), retry()}`.
   `send()` dispatches `send`, then calls `sendToApi(text)` and dispatches `reply` with the answer or `fail` with
   the error message. `retry()` re-sends the last user message. Generate ids as `m1`, `m2`… per hook instance.
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
