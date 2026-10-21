# ex29 hints · TypeScript: chat UI state reducer

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `reduce` as one `switch (action.type)`, with a case per row of the README table. Every case returns either the
**same** `state` object (for a no-op) or a brand-new object built with spreads. It never assigns to a property of
`state` or pushes to `state.messages`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Three actions (`delta`, `stream_end` and `stream_error`) change one assistant message by id. A small helper that
returns `state.messages.map(m => m.id === id && m.role === "assistant" ? f(m) : m)` covers all three. An unknown id
matches nothing, so the array comes back with the same contents. Adding a message is
`[...state.messages, newMsg]`, and removing the last one is `state.messages.slice(0, -1)`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A no-op `retry` must return the **same** object (`assert.equal(reduce(s, retry), s)` checks identity). Return
  `state` itself, not `{ ...state }`.
- A rejected `send` (pending, or blank after `trim()`) likewise returns `state` unchanged.
- `clear` returns `initialState`. The test compares with `deepEqual`, so returning the constant is fine.
- `transcript` includes only messages whose status is `done`, so a failed or still-streaming answer never shows up.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `happy path streaming` | `stream_end` doesn't clear `pending`; deltas replace the text instead of appending |
| `no double send while pending, no empty send` | `pending` not checked, or whitespace-only text not trimmed |
| `error then retry` | Retry removes the user message too; or the no-op retry returns a copy instead of the same object |
| `immutability and unknown ids` | A message changed in place (for example `msg.text += ...`) instead of copied |
| `boundary: connection lost mid-stream` | `stream_error` leaves `pending` set, so the next `send` is ignored; or the partial answer is marked `done` and leaks into the transcript |
