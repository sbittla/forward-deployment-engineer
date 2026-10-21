# ex08 hints · Scope negotiation with MoSCoW under a deadline

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

The core of this exercise is one helper: given a feature and the set already included, return the features you'd
need to add to ship it, *dependencies first*, or `None` if that's impossible. Write and test that helper on its own
before you write `plan`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- The helper recurses into `depends_on`. It skips dependencies that are already included and returns `None` if a
  dependency is unknown or is a `wont`.
- **Musts:** add each must's chain, whatever tier its dependencies are in (`ingest` is a should, but `rag-answers`
  needs it). Only check capacity once all musts are in.
- **Should, then could:** sort each tier by `value / effort` descending, then by name. For each candidate, get its
  chain and its total effort, and include the whole chain only if it fits.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Price the chain as a whole. A feature whose dependency doesn't fit is skipped, and the dependency isn't added on its
  own either.
- The overflow message must show whole numbers without `.0` (`musts need 17 days, capacity 15`). Do the same for
  slack.
- `deferred` is everything not included, sorted by name, including features that couldn't be included because of a
  dependency.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_plan` | A must's should-tier dependency isn't pulled in; tiers not ordered by value/effort |
| `test_musts_overflow` | Capacity checked before dependencies are added (so the total isn't 17), or the numbers print as `17.0` |
| `test_dependency_not_satisfiable` | A feature included even though its dependency is a `wont` |
| `test_message` | Punctuation or `none` wording differs from the README template |
