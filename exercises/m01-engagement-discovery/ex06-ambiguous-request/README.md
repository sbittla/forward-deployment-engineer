# ex06 · Ambiguous request to clarifying questions and assumptions

**Module:** m01 · **Covers:** R18 Customer discovery, R20 Comfort with ambiguity, R19 Communication · **Time:** 45 min

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
