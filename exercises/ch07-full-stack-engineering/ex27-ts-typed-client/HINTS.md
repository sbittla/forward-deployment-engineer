# ex27 hints · TypeScript: runtime-validated API client

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Every builder returns the same shape: an object with one method, `parse(value, path = "$")`. Write a tiny
`fail(path, what): never` helper that throws `ValidationError` with the `"<path>: expected <what>"` message, then
write the primitives (`str`, `num`, `bool`) as one-liners that either return the value or call `fail`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

The containers build the path as they go down:

- `arr(item)` checks `Array.isArray`, then parses each element with the path `` `${path}[${i}]` ``.
- `obj(shape)` rejects anything that isn't a plain object, then loops over the **shape's** keys (not the input's),
  parsing `src[key]` with the path `` `${path}.${key}` ``. Building a new output object is what drops the extra keys.
- `optional(inner)` returns `undefined` for `undefined` and otherwise delegates to `inner`, passing the same path.

The client is a fetch, an `ok` check, then `TicketSchema.parse(await res.json())`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `typeof NaN === "number"`, so `num()` must also check `Number.isFinite`.
- `typeof null === "object"` and `typeof [] === "object"`. `obj` needs `v === null` and `Array.isArray(v)` checks.
- `literal`'s message joins the allowed values with `|`: `expected one of low|high`.
- Trim trailing slashes from `baseUrl` so `https://a/` and `https://a` build the same URL.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `primitives` | `num()` accepts `NaN` or the string `"3"`; message lacks the `$: ` prefix |
| `nested paths` | Paths not passed down to children; arrays accepted as objects |
| `extra keys dropped, optional, literal` | Output built by copying the input (extra keys survive); literal message format |
| `client validates and sends headers` | `Accept` header missing, or the URL has a double slash |
| `client rejects drifted schema and http errors` | Response not validated, or `HttpError` lacks a `status` field |
