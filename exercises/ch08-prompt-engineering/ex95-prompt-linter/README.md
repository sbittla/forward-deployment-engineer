# ex95 · Prompt linter for CI

**Chapter:** 8 · Prompt Engineering (`exercises/ch08-prompt-engineering/`) · **Covers:** R09 Prompt & context engineering, R07 CI/CD

## Learning objectives
- Name the prompt defects that most often break customer deployments: undelimited untrusted input, missing output
  contracts, template/variable drift, cache-busting system prompts, and contradictory instructions.
- Turn prompt review into a deterministic check that runs before any token is spent on evals.
- Explain why aggressive all-caps emphasis now hurts more than it helps on current models.

## Scenario
The customer has 40 prompt templates spread across three services, edited by six people. Last month a teammate
renamed `{ticket}` to `{ticket_text}` in the code but not the template, and the model received the literal string
`{ticket}` for two days. A second incident: a support email containing "ignore previous instructions" was pasted into a
prompt with no delimiters. You'll build the linter that would have caught both, ready to run in CI next to the
eval gate from ex51.

## Your task
`Finding(rule, severity, message)` is a frozen dataclass. Placeholders are `{name}` with `name` matching
`[a-z_][a-z0-9_]*`; `{{literal}}` is an escaped brace and is not a placeholder.

- `placeholders(template) -> list[str]`: unique names in first-seen order.
- `lint(system, template, variables: set[str], tools=None) -> list[Finding]`:

| Rule | Severity | Fires when |
|---|---|---|
| P001 | error | `system` is empty or whitespace |
| P002 | error | a placeholder whose name contains one of `UNTRUSTED_HINTS` is not directly wrapped in a matching XML tag pair, e.g. `<doc>{ticket_text}</doc>` (whitespace allowed inside the tags). The message contains `{name}` |
| P003 | warning | neither `system` nor `template` mentions an output format (`OUTPUT_FORMAT` regex) |
| P004 | warning | 3 or more all-caps emphasis words (`EMPHASIS`) across system + template; message starts with the count, e.g. `"3 all-caps..."` |
| P005 | error | one per placeholder (first-seen order) that is not in `variables` |
| P006 | warning | one per variable (sorted) that the template never uses |
| P007 | warning | one per tool whose description is under 20 characters (stripped), and one per `input_schema.properties` entry with no `description` |
| P008 | warning | the system prompt contains a placeholder or a date/time (`DYNAMIC`) |
| P009 | warning | the system prompt contains both a `CONCISE` and a `VERBOSE` word |

  Return findings sorted by severity (errors first), then rule id; the sort is stable within a rule.
- `score(findings) -> int`: `max(0, 10 - 3 × errors - warnings)`.
- `render(template, values) -> str`: substitute placeholders (leave `{{...}}` untouched); raise `KeyError` naming
  every missing value. Values are inserted verbatim, not escaped: escaping untrusted values is the caller's job.

## Field notes
Linting is cheap and catches the boring failures; evals catch the interesting ones. Put both in CI and the
prompt becomes code with a review process, not a string someone edits in production.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch08-prompt-engineering/ex95-prompt-linter`.
- **Expected output:** all 11 tests fail against the starter; when you're done, all 11 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch08-prompt-engineering/ex95-prompt-linter`: all 11
  pass.
- **Tests:** `test_prompt_linter.py` (11 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linter checks a template's structure, not the data that fills it: `render` inserts
  values verbatim, so a value containing `</ticket>` can close its own tag, and P002 recognizes untrusted input only
  by placeholder name. In production, escape untrusted values before rendering, wire `lint` into CI over every
  template file, and keep injection defenses in code and in the golden set (Chapter 13).

## Prompt kit
**Learn (tutor prompt)**
```text
I'm an engineer learning prompt engineering for customer deployments. Explain, with one bad and one fixed example
each, why these prompt defects cause production incidents: untrusted input without XML delimiters, no output format,
template variables that drift from code, timestamps in the system prompt (prompt caching), and all-caps emphasis on
current Claude models. Keep each example under 6 lines. Then quiz me with 3 short prompts to diagnose.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch08-prompt-engineering/ex95-prompt-linter/starter.py so that test_prompt_linter.py passes.
Follow the rule table in README.md exactly (ids, severities, ordering). Use only the standard library. Do not edit
the tests. Keep the regex constants at module level so the rules can be tuned without touching logic. Run
`pytest exercises/ch08-prompt-engineering/ex95-prompt-linter` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review this prompt linter as a skeptical staff engineer. For each rule, give one false positive and one false
negative it would produce on real customer templates, and say whether the rule should be an error, a warning, or
removed. Flag any rule that would push authors toward worse prompts.
```
