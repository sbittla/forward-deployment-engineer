# ex85 hints · Claude Agent Skills and subagents: package, route, delegate

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`parse_frontmatter` is the foundation: one DOTALL regex that captures what's between the opening `---` line and the
closing `---` line, and everything after it as the body. Split each frontmatter line on its **first** colon only, so a
description like `does y: z` survives.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **parse_skill:** validate the name with a regex like `^[a-z0-9-]{1,64}$` plus the reserved-word check, then the
  description's length and the absence of `<` and `>`, then a non-empty body. Resources are every other file under the
  folder, as sorted POSIX relative paths.
- **SkillRegistry:** load each `*/SKILL.md` folder, and raise on a duplicate name. `metadata_prompt` lists only names
  and descriptions. That's progressive disclosure: bodies load only when a skill is chosen.
- **select:** score each skill by `|tokens(task) ∩ tokens(description)|`, sort by `(-score, name)`, drop zeros, and
  take `k`.
- **delegate:** check the requested tools exist, filter the tool specs, and call the model with a brand-new message
  list.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `read_resource` must refuse `../b/SKILL.md`. Resolve both the skill folder and the target, then require the folder
  to be one of the target's parents.
- `tools` absent means `None` (inherit everything), which is different from an empty list. Same for `model`.
- "Fresh context" means the subagent sees only `[{"role": "user", "content": task}]`, never the parent's history, and
  the parent gets back only the text.
- Your own `SKILL.md` description must say **when** to use it (the test looks for "use when"), and the subagent's
  system prompt needs at least 20 words.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_frontmatter` | Splitting on every colon; missing frontmatter returns empty data instead of raising |
| `test_parse_skill_and_validation` | Uppercase or reserved names accepted; `SKILL.md` listed among the resources |
| `test_registry_progressive_disclosure` | Bodies included in the metadata prompt; zero-overlap skills returned; path traversal allowed |
| `test_duplicate_names` | Second skill silently overwrites the first |
| `test_subagent_delegation` | Parent history passed in; tools not filtered; model not forwarded |
| `test_subagent_inherits_and_unknown_tool` | `None` tools treated as "no tools"; unknown tool not rejected |
| `test_your_skill_and_subagent` | Your files are missing `reference/routing-rules.md`, a "use when" phrase, or a long enough prompt |
