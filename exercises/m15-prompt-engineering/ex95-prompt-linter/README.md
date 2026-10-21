# ex95 · Prompt linter for CI

**Module:** m15 · **Covers:** R09 Prompt & context engineering, R07 CI/CD · **Time:** 60 min

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
  every missing value.

## Field notes
Linting is cheap and catches the boring failures; evals catch the interesting ones. Put both in CI and the
prompt becomes code with a review process, not a string someone edits in production.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

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
Implement exercises/m15-prompt-engineering/ex95-prompt-linter/starter.py so that test_prompt_linter.py passes.
Follow the rule table in README.md exactly (ids, severities, ordering). Use only the standard library. Do not edit
the tests. Keep the regex constants at module level so the rules can be tuned without touching logic. Run
`pytest exercises/m15-prompt-engineering/ex95-prompt-linter` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review this prompt linter as a skeptical staff engineer. For each rule, give one false positive and one false
negative it would produce on real customer templates, and say whether the rule should be an error, a warning, or
removed. Flag any rule that would push authors toward worse prompts.
```
