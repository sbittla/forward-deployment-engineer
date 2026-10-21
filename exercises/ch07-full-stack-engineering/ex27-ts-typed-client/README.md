# ex27 · TypeScript: runtime-validated API client

**Chapter:** 7 · Full-Stack Engineering (`exercises/ch07-full-stack-engineering/`) · **Covers:** R02 TypeScript/full-stack, R05 APIs

## Learning objectives
- Validate API responses at runtime because TypeScript types vanish at runtime.
- Produce precise error paths like $.items[2].id.
- Build a typed client that fails loudly on contract drift.

## Scenario
TypeScript types vanish at runtime. When the customer's API silently changed `priority` from a string to a
number, your typed frontend rendered `undefined` for a week. Build a tiny runtime schema library (the core idea
behind zod/valibot) and a client that validates every response at the boundary.

## Your task (in `starter.ts`)
1. Schema builders returning `Schema<T>` with `parse(value: unknown, path = "$"): T`:
   `str()`, `num()`, `bool()`, `arr(item)`, `obj(shape)`, `optional(inner)`, `literal(...values)`.
   - On failure throw `ValidationError` whose `message` is `"<path>: expected <what>"`, e.g.
     `"$.items[2].id: expected number"`. `obj` paths use `.key`; `arr` paths use `[i]`.
   - `obj` rejects non-objects and arrays; extra keys are dropped from the result; `optional` accepts `undefined`.
   - `literal("low","high")` expects one of the values: message `expected one of low|high`.
2. `createClient(baseUrl, fetchFn)` returning `{ getTicket(id: number): Promise<Ticket> }`:
   - `GET {baseUrl}/tickets/{id}` with header `Accept: application/json`
   - non-2xx → throw `HttpError` with `.status`
   - validate the JSON with `TicketSchema` (export it): `{ id: number, title: string,
     priority: "low"|"normal"|"high"|"urgent", tags: string[], assignee?: string }`

## Run
```
node --test exercises/ch07-full-stack-engineering/ex27-ts-typed-client/client.test.ts
FDE_SOLUTIONS=1 node --test exercises/ch07-full-stack-engineering/ex27-ts-typed-client/client.test.ts   # reference
```
Requires Node ≥ 22.18; Node 24 LTS recommended (native TypeScript type stripping; no build step, no npm install).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "TypeScript: runtime-validated API
client". Before I write code, teach me runtime schema validation in TypeScript (the idea behind zod), type inference
from schema builders, and validating at the trust boundary. Use short TypeScript examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch07-full-stack-engineering/ex27-ts-typed-client/starter.ts so that client.test.ts passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ValidationError`, `HttpError`, `str`, `num`, `bool`, `arr`, `obj`, `optional`, `literal`, `TicketSchema`,
`createClient`. Constraints: TypeScript executed directly by Node 22.18+ type stripping: no npm packages, no build
step, and only erasable type syntax (no enums, namespaces or parameter properties). Do not modify the tests. When
you're done, run `node --test exercises/ch07-full-stack-engineering/ex27-ts-typed-client/client.test.ts` and show me
the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "TypeScript: runtime-validated API client" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Do arrays pass the obj() check by accident? Are extra keys dropped, not passed
through? Is the inferred Ticket type identical to the schema's runtime behaviour? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
