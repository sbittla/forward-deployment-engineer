# ex91 hints · React copilot UI component and hook without a build step

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `chatReducer` first. It's pure and is tested on its own. Every case returns a new object built with spreads, and
a `send` that should be ignored (pending, or a blank draft after `trim()`) returns the **same** `state` object. The
test checks identity with `assert.equal`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **makeUseChat:** declare the id counter inside `makeUseChat`, *outside* the returned `useChat` function. Inside
  `useChat`, call the injected `useReducer(chatReducer, initialState)` and return the state plus three actions.
- `send()` reads the draft from the state it has, dispatches `send` with a new id, then awaits the API inside
  `try/catch`, dispatching `reply` (with another new id) or `fail` with the error message.
- `retry()` finds the last user message, dispatches `retry`, and calls the API with that text.
- **makeCopilotPanel(h):** call `h(type, props, ...children)` exactly as `React.createElement` would. Message text goes
  in as a **child**, never as HTML.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Take the reply's id only once the reply has arrived. The failed first attempt must not use up `m2`, because the
  test expects the eventual answer to be `m2`.
- The store the test injects updates synchronously, but the `state` you captured is from the render, so `send()` must
  remember the trimmed text **before** dispatching, not read it again afterward.
- `onSubmit(e)` must call `e.preventDefault()` before `onSend()`. Without it, a real browser reloads the page.
- The alert (with its Retry button) only renders when `state.error` is set. Pass `null` otherwise; the test's `h`
  filters it out.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `reducer` | State changed in place; an ignored `send` returns a copy instead of the same object; draft not trimmed |
| `hook sends, replies and retries` | Counter inside `useChat` (ids restart); id taken before the API call fails; retry doesn't reuse the last user text |
| `panel renders accessible, safe markup` | Text set with `dangerouslySetInnerHTML`; missing `role`/`aria-*` props; `preventDefault` not called; Send not disabled while pending |
| `hook: stop aborts the request and shows Stopped, not an error` | No `signal` passed to `sendToApi`; the controller kept inside `useChat` (lost on re-render); the abort rejection dispatched as `fail` |
| `hook: a 401 asks the user to sign in and never retries` | 401 dispatched as `fail`, so Retry is offered; `retry()` or the reducer's `retry` not guarded on `authExpired` |
| `panel: every failure state is announced with plain text and one labeled action` | Retry shown for an expired session; Stopped rendered as an alert; a button without `type: "button"`; Stop shown when idle |
