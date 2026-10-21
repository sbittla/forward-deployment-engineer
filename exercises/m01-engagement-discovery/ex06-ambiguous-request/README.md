# ex06 · Ambiguous request to clarifying questions and assumptions

**Module:** m01 · **Covers:** R18 Customer discovery, R20 Comfort with ambiguity, R19 Communication · **Time:** 45 min

## Learning objectives
- Turn an ambiguous executive request into high-leverage clarifying questions.
- Write explicit working assumptions so work can start before answers arrive.
- Detect vague terms and missing dimensions (metric, users, data, deadline, volume).

## Scenario
A Slack message from the customer's COO: *"We need an AI that makes support faster and better for all our
customers, ideally real-time, soon."* Every FDE gets these. Your job is to turn it into a short list of
high-leverage questions **and** a set of explicit working assumptions, so you can start building today
instead of waiting for perfect answers.

## Your task
`analyze(request: str) -> Analysis` with fields:

- `vague_terms`: vague words found (case-insensitive, whole word), in order of appearance, from
  `VAGUE = {"fast","faster","better","soon","all","real-time","accurate","easy","scalable","seamless","smart"}`.
- `missing`: which of these dimensions the request does **not** pin down, in this priority order:
  1. `metric` — no number followed by `%`, `min`, `sec`, `seconds`, `minutes`, `hours`, `x`
  2. `users` — none of `agent(s)`, `adjuster(s)`, `analyst(s)`, `customer(s)`, `team`, `rep(s)`, `user(s)`
  3. `data` — none of `ticket(s)`, `document(s)`, `pdf(s)`, `database`, `crm`, `emails`, `logs`
  4. `deadline` — no `YYYY-MM-DD`, no `Q1`–`Q4`, no month name
  5. `volume` — no number followed by `/day`, `per day`, `/month`, `per month`, `tickets`, `calls`
- `questions`: one question per missing dimension (same order), then one per vague term
  (`'What does "<term>" mean in measurable terms?'`).
- `assumptions`: one entry per missing dimension using `DEFAULT_ASSUMPTIONS[dim]`.

## Field notes
Send the questions *and* your assumptions together: "Unless you tell me otherwise by Thursday, I will assume…".
That converts waiting into progress.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Ambiguous request to clarifying
questions and assumptions". Before I write code, teach me how FDEs handle vague requests: which dimensions to pin
down first, how to phrase questions that get numbers back, and how to pair questions with default assumptions and a
deadline. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m01-engagement-discovery/ex06-ambiguous-request/starter.py so that test_ambiguous.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Analysis`, `analyze`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m01-engagement-discovery/ex06-ambiguous-request` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Ambiguous request to clarifying questions and assumptions" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Do the regexes miss common phrasings ("2 hrs", "next
quarter", "500 a day")? Are the questions ones a COO would answer quickly? Is any assumption risky enough that it
should be a question instead? Rank findings by customer impact, quote the line for each, and say which ones a test
should catch.
```
