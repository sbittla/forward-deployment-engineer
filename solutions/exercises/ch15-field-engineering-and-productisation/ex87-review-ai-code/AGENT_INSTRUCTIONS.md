# Agent instructions: claims ticket export service

## Project overview
Python 3.12 utilities that export a customer's support tickets from the claims database to CSV for the customer's
auditors. The data is customer-confidential; exports land in a per-customer directory.

## Commands
- Run tests: `pytest -q`
- Lint: `ruff check .`

## Conventions
- Database access goes through parameterised queries only (`conn.execute(sql, params)`).
- CSV output uses the `csv` module; files are written UTF-8 with `newline=""`.
- Errors are raised with context (file name, record id), never silently swallowed.
- No mutable default arguments.

## Never do
- Never log, print or return secrets: API tokens, passwords, connection strings.
- Never build SQL with f-strings, `%` or string concatenation.
- Never write to a path derived from user input without resolving it and checking it stays inside the allowed directory.
- Never catch bare `Exception` to return an empty result.

## Before you finish
1. Write a failing test for each behaviour you change, then make it pass.
2. Run `pytest -q` and paste the summary line in the PR description.
3. List every external input (user strings, file names, API responses) and say how each is validated.
