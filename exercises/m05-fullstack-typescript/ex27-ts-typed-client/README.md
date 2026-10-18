# ex27 · TypeScript: runtime-validated API client

**Module:** m05 Full-stack & TypeScript · **Covers:** R02 TypeScript/full-stack, R05 APIs · **Time:** 60 min

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
node --test exercises/m05-fullstack-typescript/ex27-ts-typed-client/client.test.ts
FDE_SOLUTIONS=1 node --test exercises/m05-fullstack-typescript/ex27-ts-typed-client/client.test.ts   # reference
```
Requires Node ≥ 23.6 (native TypeScript type stripping; no build step, no npm install).
