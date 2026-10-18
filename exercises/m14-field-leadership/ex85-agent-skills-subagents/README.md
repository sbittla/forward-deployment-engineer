# ex85 · Claude Agent Skills and subagents: package, route, delegate

**Module:** m14 · **Covers:** R36 Vendor AI platforms, R11 Agents, R12 Connectors · **Hands-on:** Claude Agent Skills,
Claude Code subagents · **Time:** 75 min

## Scenario
Anthropic's FDE posting lists the artifacts you hand customers: "MCP servers, sub-agents, and agent skills that will
be used in production workflows". Two packaging formats matter:

- **Agent Skill**: a folder with a `SKILL.md` whose YAML frontmatter has `name` and `description`, a markdown body of
  instructions, and optional extra files (references, scripts). Only `name` + `description` are loaded up front
  (progressive disclosure). The body is read when the skill is relevant, and extra files only when needed.
- **Subagent** (Claude Code): a markdown file (e.g. `.claude/agents/<name>.md`) with frontmatter `name`,
  `description`, optional `tools` (comma-separated; omitted = inherit all) and optional `model`. The body is the
  subagent's system prompt. It runs in its own context and returns only its result to the parent.

You'll implement a loader/validator and a tiny runtime for both, then author a real skill and subagent for the
claims customer.

## Your task
1. `parse_frontmatter(text) -> (dict, body)`: text starts with `---\n`, simple `key: value` lines, closing `---`.
   Missing frontmatter → `ValueError`.
2. `parse_skill(skill_dir) -> Skill(name, description, body, resources)`. Validate: `name` is 1–64 chars of
   lowercase letters, digits and hyphens, and must not contain `anthropic` or `claude`; `description` is 1–1024 chars
   with no `<`/`>` (no XML tags); the body is non-empty. `resources`: sorted relative POSIX paths of every other
   file in the folder.
3. `SkillRegistry(root)`: loads every subfolder containing `SKILL.md`. Duplicate names → `ValueError`.
   - `metadata_prompt()` → lines `- <name>: <description>` sorted by name (what goes into the system prompt)
   - `select(task, k=1)` → names of up to `k` skills ranked by content-token overlap (`fde_kit.tokenize`) between
     the task and the description (ties by name), excluding zero-overlap skills
   - `load(name)` → the body; `read_resource(name, path)` → file text, refusing paths that escape the skill folder
4. `parse_subagent(text) -> Subagent(name, description, tools: list[str] | None, model: str | None, system_prompt)`.
5. `delegate(sub, task, llm, available_tools)`: raise `ValueError` if the subagent lists a tool not in
   `available_tools`. Call `llm.complete([{"role": "user", "content": task}], system=sub.system_prompt,
   tools=[tool specs filtered to sub.tools, or all if None], model=sub.model)` in a **fresh context** (no parent
   history) and return only the result text.
6. Author `skills/claims-triage/SKILL.md` (+ a `reference/routing-rules.md`) and `agents/policy-researcher.md`
   (tools: `search_policies, read_policy`) that pass your own validators. The tests also check that the skill's
   description says *when* to use it.
