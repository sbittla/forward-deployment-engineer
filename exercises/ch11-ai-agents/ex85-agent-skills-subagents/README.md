# ex85 · Claude Agent Skills and subagents: package, route, delegate

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R36 Vendor AI platforms, R11 Agents, R12 Connectors · **Hands-on:** Claude Agent Skills,
Claude Code subagents

## Learning objectives
- Package expertise as Claude Agent Skills and Claude Code subagents.
- Validate frontmatter rules and progressive disclosure.
- Route tasks to skills and delegate to subagents with restricted tools.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch11-ai-agents/ex85-agent-skills-subagents`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch11-ai-agents/ex85-agent-skills-subagents`: all 7
  pass.
- **Tests:** `test_skills.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Front matter is parsed as simple `key: value` lines, and skills are trusted once loaded.
  Production uses a real YAML parser, reviews skills and their scripts before installing them, and limits subagent
  tools by the same authorization policy as the parent's.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Claude Agent Skills and subagents:
package, route, delegate". Before I write code, teach me Agent Skills (SKILL.md frontmatter, body, resources,
progressive disclosure) and Claude Code subagents (frontmatter name, description, tools, model; separate context).
Use short Python examples that are not the exercise solution. Then ask me three questions to check my understanding,
one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex85-agent-skills-subagents/starter.py so that test_skills.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Skill`, `Subagent`, `parse_frontmatter`, `parse_skill`, `SkillRegistry`, `parse_subagent`, `delegate`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch11-ai-agents/ex85-agent-skills-subagents` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Claude Agent Skills and subagents: package, route, delegate" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Are reserved words and XML tags rejected in names and
descriptions? Does an omitted tools field inherit all tools while an empty one grants none? Is the description
specific enough that routing picks this skill only when it should? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
---
name: claims-triage
description: Triage new insurance claims: classify severity, check required documents and draft the adjuster handoff. Use when a new claim or FNOL arrives.
---

# Claims triage
1. Read the claim and list any missing required documents.
2. Classify severity using references/severity.md.
3. Draft a handoff note for the adjuster: facts, gaps, recommended next step.
Never approve or deny coverage; that decision belongs to the adjuster.
```
