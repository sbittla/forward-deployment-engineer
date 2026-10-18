# ex87 · Review and fix an AI-agent-written pull request; write agent instructions

**Module:** m14 · **Covers:** R37 AI-assisted engineering, R29 Debugging, R17 Security · **Hands-on:** AI coding
tools workflow · **Time:** 60 min

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
