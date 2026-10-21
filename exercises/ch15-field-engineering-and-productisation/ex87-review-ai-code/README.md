# ex87 · Review and fix an AI-agent-written pull request; write agent instructions

**Chapter:** 15 · Field Engineering and Productisation (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R37 AI-assisted engineering, R29 Debugging, R17 Security · **Hands-on:** AI coding
tools workflow

## Learning objectives
- Review AI-written code for security, correctness and reliability bugs.
- Fix injection, path traversal, secret logging, pagination and state leaks.
- Write agent instructions that prevent the same mistakes next time.

## Scenario
Anthropic's Staff FDE posting expects "everyday use of AI coding tools with the judgment to review and steer";
IBM's forward-deployed units "use AI to accelerate AI implementation"; Deloitte trains client engineers on these
tools. The productivity is real, and so is the failure mode: plausible code that passes a glance and ships a
vulnerability. A coding agent produced `starter.py` (a ticket-export module) for the customer overnight. It runs.
It's also wrong in at least six ways.

## Your task
1. **Fix `starter.py`** (keep the function signatures) so it passes the tests:
   - `find_tickets(conn, customer)` must be safe against SQL injection (parameterised query)
   - `export_csv(rows, filename, out_dir)` must refuse filenames that escape `out_dir` (`ValueError`) and must quote
     CSV fields properly
   - `fetch_all(client, total_pages)` must fetch every page (pages are 1-based, inclusive)
   - `call_api(client, token, log)` must never write the token to the log
   - `load_tickets(path)` must not swallow errors: a missing file raises `FileNotFoundError`, bad JSON raises
     `ValueError` naming the file
   - `tag_counts(rows, counts=None)` must not leak state between calls
2. **Write `REVIEW.md`**: one bullet per finding, formatted `- [category] <file>:<function>: <problem> → <fix>`,
   category one of `security`, `correctness`, `reliability`. At least 6 findings, at least 2 security.
3. **Write `AGENT_INSTRUCTIONS.md`**, the instruction file you'd commit for the coding agent (the CLAUDE.md
   pattern), so this doesn't happen again. Required sections: `Project overview`, `Commands` (including the exact
   test command in backticks), `Conventions`, `Never do` (must cover secrets in logs, string-built SQL and
   unvalidated paths), `Before you finish` (verification steps).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Review and fix an AI-agent-written
pull request; write agent instructions". Before I write code, teach me reviewing AI coding agent output: the common
failure patterns (SQL injection, path traversal, logging secrets, off-by-one pagination, swallowed errors, mutable
defaults) and how to steer agents with an instruction file. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Fix the AI-written bugs in exercises/ch15-field-engineering-and-productisation/ex87-review-ai-code/starter.py so that test_review.py
passes. README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public
API: `find_tickets`, `export_csv`, `fetch_all`, `call_api`, `load_tickets`, `tag_counts`. Also create REVIEW.md,
AGENT_INSTRUCTIONS.md in the same folder, exactly as the README specifies. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch15-field-engineering-and-productisation/ex87-review-ai-code` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Review and fix an AI-agent-written pull request; write agent instructions" as a senior
forward deployed engineer would before it ships to a customer. Specifically: Did the fixes keep every signature? Is
each REVIEW.md finding reproducible from the description? Would AGENT_INSTRUCTIONS.md have prevented each bug, and
is it short enough that an agent follows it? Rank findings by customer impact, quote the line for each, and say
which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
# Agent instructions (excerpt)
- Use parameterised SQL only; never build queries with f-strings.
- Resolve file paths and refuse anything outside the configured output directory.
- Never log tokens, keys or Authorization headers; log a redacted form.
- Don't catch broad exceptions to return defaults; raise with context.
- Run the test suite and include its output in your summary before declaring done.
```
