# FDE interview questions and answers

127 questions in the style of Forward Deployed Engineer interview loops, seven or eight per chapter of *The Forward
Deployed Engineer*, each with a model answer, the signals of a strong answer and the common red flags. The book
prints the questions at the end of each chapter and the answers in Appendix J; this file is generated from the book
(`book/scoring/export_interview.py`), so the two match.

**How to use them.** Answer each question aloud before reading the model answer, then check yourself against its
*Strong signals* and *Red flags*. For a mock loop, pick one question of each type (technical, coding, debugging,
system design, customer scenario, behavioral) from different chapters. Section numbers refer to the book; exercise
ids (ex01 to ex100) are in `exercises/chNN-<chapter>/` in this repository.

## Contents
- [Chapter 1 · The Forward Deployed Engineer](#chapter-1--the-forward-deployed-engineer) (7 questions)
- [Chapter 2 · Discovery and Scoping](#chapter-2--discovery-and-scoping) (8 questions)
- [Chapter 3 · Technical Communication](#chapter-3--technical-communication) (8 questions)
- [Chapter 4 · Production-Grade Python](#chapter-4--production-grade-python) (7 questions)
- [Chapter 5 · Enterprise Integration](#chapter-5--enterprise-integration) (8 questions)
- [Chapter 6 · Data Engineering](#chapter-6--data-engineering) (8 questions)
- [Chapter 7 · Full-Stack Engineering](#chapter-7--full-stack-engineering) (7 questions)
- [Chapter 8 · Prompt Engineering](#chapter-8--prompt-engineering) (7 questions)
- [Chapter 9 · LLM Application Engineering](#chapter-9--llm-application-engineering) (7 questions)
- [Chapter 10 · Retrieval-Augmented Generation (RAG)](#chapter-10--retrieval-augmented-generation-rag) (8 questions)
- [Chapter 11 · AI Agents](#chapter-11--ai-agents) (8 questions)
- [Chapter 12 · LLM Evaluation](#chapter-12--llm-evaluation) (8 questions)
- [Chapter 13 · AI Security and Guardrails](#chapter-13--ai-security-and-guardrails) (7 questions)
- [Chapter 14 · LLMOps and SRE](#chapter-14--llmops-and-sre) (8 questions)
- [Chapter 15 · Field Engineering and Productization](#chapter-15--field-engineering-and-productization) (7 questions)
- [Chapter 16 · Delivery Leadership](#chapter-16--delivery-leadership) (7 questions)
- [Chapter 17 · FDE Careers](#chapter-17--fde-careers) (7 questions)

## Chapter 1 · The Forward Deployed Engineer

### 1.1 · Behavioral

**Q.** Tell me about a time you had to start building before the requirements were clear. How did you avoid both waiting and guessing?

Use situation, action, result. Situation: a question that mattered (who the users were, what success meant) had no
answer, and waiting would have cost real time. Action, the core: you listed the open questions, paired each with a
working assumption and a deadline, and started work the same day. The model sentence: "Unless you tell me otherwise
by Thursday, I'll assume adjusters, not policyholders, are the users." Result: the assumption held and you'd made
progress meanwhile, or stating it surfaced a disagreement while changing course was cheap. Close with the habit:
dated, written assumptions, so silence becomes recorded agreement (Section 1.4; ex06).

*Strong signals:* the assumption was written and dated; disagreement surfaced early because of it; links this to
bias to action, not recklessness. *Red flags:* "I waited until the requirements were signed off"; building on
assumptions nobody else saw.

### 1.2 · Customer scenario

**Q.** Three weeks after launch, your Tailspin Logistics assistant scores 94% on its evaluation set, but only 18% of invited dispatchers have opened it once. What do you do in the next two weeks?

The model isn't the problem: 94% on the evaluation set and 18% activation is an adoption failure, the "Adopt" step
of the operating loop. Gather evidence: usage logs by team (in the chapter's case most questions came from the IT
team that hosted the pilot), then an afternoon or two beside the dispatchers. The cause: they live in the dispatch
console, and the assistant sits in a separate tab behind a second login. Fix the root causes: a sponsor in
operations (the head of dispatch), the assistant as a panel inside the console using the existing session, and
activation instrumented by team and reported weekly. Next time, in week one: a named sponsor, an afternoon with five
real users and activation instrumented before the first demo (Section 1.6, Table 1.2).

*Strong signals:* treats this as a discovery gap, not a model gap; goes to watch users; names an operations sponsor.
*Red flags:* tuning the model or prompts to raise accuracy; sending reminder emails and calling it adoption work.

### 1.3 · Debugging

**Q.** During a demo, your retrieval prototype answers a coverage question wrongly in front of the customer's head of compliance. Walk me through what you do between then and tomorrow morning.

Acknowledge the miss in the room, then treat it as a bug with a reproduction. Trace it through the pipeline: in the
chapter's day-on-site example, a chunking boundary separated an exclusion from the clause it modified, a retrieval
problem, not a model problem (Chapter 10). Fix it and add that exact question to the evaluation set so it can't
silently regress (Chapter 12). Put failure, cause and fix in the next status note, so the head of compliance and the
sponsor hear it from you, in writing, with evidence (Chapter 3). The whole loop, from embarrassing demo to regression
test to status note, fits in an afternoon and is the job (Section 1.1).

*Strong signals:* locates the failure in a component before changing anything; adds a regression case; reports it
proactively. *Red flags:* patching the prompt for that one question with no evaluation; hoping nobody brings it up.

### 1.4 · System design

**Q.** Walk me through how you'd structure an engagement from kickoff to handover, and what you'd put in place at each stage to catch its most likely failure early.

Use the operating loop with an early warning for each step (Section 1.4, Table 1.2). Discover: find the sponsor,
the metric and the constraints; the failure is solving the wrong problem, warned by no named sponsor or no baseline
metric. Scope: the charter and, with procurement, the statement of work; the failure is unbounded scope, warned by no
written out-of-scope list. Prototype honestly: the smallest thing that tests the riskiest assumption; the failure is
a demo that can't be measured, warned by no evaluation set before the demo. Harden: security, evaluation,
observability, rollback; the failure is a late security block, warned by security not consulted in week one. Deploy
and drive adoption: the failure is nobody using it, warned by uninstrumented activation. Hand off and productize: the
failure is a customer who can't run it, warned by a runbook the customer has never executed. The loop isn't strictly
sequential: discovery continues throughout, and parts get hardened while others are still being scoped.

*Strong signals:* a concrete early warning per step; feeds learning back to the product team. *Red flags:* a
waterfall plan that ends at "deploy"; no adoption or handover stage.

### 1.5 · Customer scenario

**Q.** On a fixed-price engagement, the customer's operations manager stops you in a corridor and asks whether you can "just add" CRM write-back by the end of the month. How do you respond?

Neither yes nor no. A hallway promise can create a contractual obligation, and on a fixed-price statement of work
every change needs a change request (Section 1.5, Table 1.3; Chapter 16). Respond positively without committing:
you'll look at what it involves and come back with the impact. Involve your commercial counterpart (account
executive, deployment strategist or engagement manager); you should already have agreed who speaks to the customer
about price, scope and dates. The request becomes a written change with its effect on effort and dates, usually
traded against planned work. The operations manager may not be able to change scope at all: the sponsor who owns the
budget decides.

*Strong signals:* sees the contractual risk; routes it through the commercial counterpart and a change request; stays
helpful. *Red flags:* "Sure, it's only a couple of days"; a flat refusal that damages the relationship.

### 1.6 · Technical

**Q.** The sponsor wants to see your prototype next week. What has to exist before that demo, and why?

"Prototype honestly" means the smallest thing that tests the riskiest assumption, measured (Section 1.4; ex70).
Three things must exist first. An evaluation set: the prototype step's characteristic failure is a demo that can't be
measured, warned by no evaluation set before the demo (Table 1.2). A baseline for the sponsor's metric: baselines
before demos, evaluations before launches, control groups before claims. And, from the Tailspin case, activation
instrumented before the first demo, so you see who uses it (Section 1.6). The payoff is the most persuasive sentence
an FDE can say to a sponsor: one with a number and the word "measured".

*Strong signals:* an evaluation set before the demo; ties the demo to the sponsor's baseline metric. *Red flags:*
polishing the interface; hand-picked examples with no measured result.

### 1.7 · Behavioral

**Q.** Engineers come to this role from different backgrounds. Which gaps does yours leave, and what are you doing to close them?

Self-awareness and a plan, not modesty. Name your starting point (backend or platform, data engineering, machine
learning, solutions architecture or consulting) and its typical gap. Gaps reflect the failures you've lived through:
a backend engineer knows why retries need jitter but may never have watched a perfect system go unused; a consultant
knows why adoption needs a plan but may never have been paged at 3 a.m. (Section 1.6). The plan: exercises in your
weak areas first, under time pressure, noting what surprised you, with a capstone as the running example. Show
evidence you've started, and pitch your level honestly against the Introduction's Foundation, Independent
Practitioner and Production-ready FDE levels.

*Strong signals:* a specific gap tied to a specific missing experience; a concrete plan with evidence of progress.
*Red flags:* claiming no gaps; "I'd need to know everything first", which the chapter lists as a misconception.

## Chapter 2 · Discovery and Scoping

### 2.1 · Customer scenario

**Q.** You arrive at Northwind Insurance for a six-week pilot. By Wednesday, the VP of claims wants shorter handle times, compliance wants fewer coverage errors and IT security hasn't heard of the project. What do you do this week?

None of this is a modeling problem, and any of it can sink the pilot: no agreed success, no clear owner, and a
security team that will surface late (Section 2.1). Draft the charter this week and let its gaps drive the
conversations (Section 2.3; ex01). Find the sponsor: "If the VP of claims and compliance disagree, who decides?" A
committee isn't a sponsor. Write both goals as metrics with a numeric baseline, target and unit; measure missing
baselines in week one. Send open questions with dated working assumptions (ex06). Map IT security as high influence,
start the security review in week one, and log it in the RAID log (Section 2.5; ex04, ex07). Take the charter's gaps
to a sponsor meeting instead of guessing.

*Strong signals:* forces one named decider; measurable metrics with baselines; security in week one. *Red flags:*
picking one goal and building; proposing a retrieval architecture before the metric and users are known.

### 2.2 · Technical

**Q.** Walk me through building a business case for an AI assistant that a CFO will accept. What goes in, and what does the CFO actually need to see?

Five pieces (Section 2.4; ex03). Labor savings: tasks per month × 12 × adoption × minutes saved ÷ 60 × loaded hourly
cost. Model cost: tokens per call (input and output priced separately) × price × calls per task × tasks per year.
Run cost: model cost plus platform cost. Net benefit is savings minus run cost; first-year ROI is (net − one-time
cost) ÷ (one-time cost + run cost); payback is one-time cost ÷ monthly net benefit. For Northwind that gives $864,000
of savings, $720,960 net, 120% ROI and 4.2 months' payback. The CFO needs the sensitivity: halving adoption cuts
net benefit by 60%, doubling token price by about 3%, so adoption decides ROI. Then make it complete: human review
and ongoing operations drop ROI to 84% and stretch payback to 4.7 months. Label every line measured, quoted,
estimated, assumed or projected, use finance's loaded labor cost, and point out your conservative choices.

*Strong signals:* adoption explicit, with a sensitivity table; costs pilots usually omit; a status label per line.
*Red flags:* one ROI number with no sensitivity; obsessing over token price while assuming full adoption.

### 2.3 · Customer scenario

**Q.** The sponsor wants eleven features in a six-week pilot. You have 25 engineer-days, and the must-haves alone need 30. How do you handle it?

MoSCoW (Section 2.6; ex08), musts and their dependencies first. The musts alone need 30 days against 25 of capacity,
so stop planning and open a conversation with the sponsor on the exact gap ("musts need 30 days, capacity 25"). The
sponsor chooses: demote something to a should, add capacity or move the date. Once the musts fit, add shoulds, then
coulds, by value per day of effort, each only if it fits and its dependencies are in; won'ts are always deferred. The
trade-off message lists what's included, what's deferred to phase two and the slack left: zero slack is a plan to be
late. Never cut quality silently; dropping tests, evaluation or security review moves the cost to production. Cut
scope loudly, in writing.

*Strong signals:* quantifies the overrun and hands the trade to the sponsor; keeps visible slack; protects quality.
*Red flags:* "we'll work weekends"; quietly skipping evaluation or security review to fit.

### 2.4 · Technical

**Q.** How would you estimate the delivery date for a pilot's statement of work, and which date would you give the customer?

Three estimates per task: optimistic, most likely, pessimistic. PERT gives expected = (o + 4m + p) / 6 and standard
deviation = (p − o) / 6; for 3, 5 and 13 days that's 6 days and 1.67, above the most likely value because pessimistic
tails are longer (Section 2.6; ex81). Critical path method: a forward pass for earliest starts, a backward pass for
latest, slack as the difference; zero-slack tasks form the critical path. The P50 sums expected durations along it;
the P90 approximates as P50 + 1.2816 × the square root of the summed critical-path variances. Quote the P90 to the
customer; plan internally to the P50. Two caveats: the formula ignores near-critical paths, so the true P90 is longer
and you add an explicit contingency line for integration and customer dependencies; and customer dependencies on or
near the critical path go into the RAID log and the SOW's customer responsibilities.

*Strong signals:* a range, not a date; knows the P90 is still optimistic; tracks low-slack customer dependencies.
*Red flags:* a single-date estimate; invisible padding on every task instead of a visible contingency.

### 2.5 · Customer scenario

**Q.** Midway through the pilot, a team lead asks, "Could it also handle the Spanish-language tickets?" How do you respond, that day and that week?

Scope creep arrives as a reasonable question answered with a reasonable "probably" (Section 2.3), so don't say it.
If the charter's out-of-scope list covers it, say so: "That's on the phase-two list; shall we discuss swapping it for
something?" The same day, in writing: "Happy to look at this. I'll send a change note by Friday with the impact",
then do it (Section 2.6). The note states what's asked, why, the effect on effort and dates from a re-run estimate,
what it displaces, and who approves. The sponsor approves scope changes; you approve nothing for the customer, and a
team lead may not be able to either. Most requests become trades, such as Spanish support in, CRM write-back deferred
to phase two.

*Strong signals:* says yes to the process, not to the feature; re-runs the estimate; routes approval to the sponsor.
*Red flags:* agreeing informally to keep the customer happy; a flat no with no path forward.

### 2.6 · Coding

**Q.** You want to use an LLM to turn discovery interview transcripts into user stories. How would you build it so a malformed reply never reaches the backlog, and what happens to the output afterward?

Follow ex02 (Section 2.2). Ask for structured output that must parse against a fixed schema: each story has
`as_a`, `i_want`, `so_that` and a list of `acceptance_criteria`. Treat the transcript as untrusted input and
delimit it, for example inside `<transcript>` tags. Validate the reply at the boundary and, on failure, send the
error back so the model can repair its answer; a malformed reply never reaches the backlog (Chapter 9 develops the
pattern). The step that matters more than the code: read the drafted backlog back to the customer, in their words.
The model drafts in seconds, but the customer owns the backlog. One they didn't review is yours, and when it's wrong
it's your fault.

*Strong signals:* schema validation plus a repair loop; delimited untrusted input; customer review built in.
*Red flags:* raw model output pasted into the tracker; the model's draft treated as the requirements.

### 2.7 · Behavioral

**Q.** Tell me about a time a stakeholder with real influence found out about your project late. What would you do differently now?

Use situation, action, result, with a lesson about process. The problem was the communication plan, not the system,
like Legal at Northwind arriving two weeks in with an unscheduled review though nothing had changed (Section 2.5).
What you did then and would do now: score every stakeholder 1 to 5 on influence and interest, and set cadence and
channel by quadrant. High influence and high interest: managed closely, weekly, one to one. High influence alone: an
executive summary every two weeks, which in the chapter's example would have surfaced the review in week one. Add
RACI with exactly one accountable person per workstream, and take any unowned workstream to the next steering meeting
with a proposed owner (ex04).

*Strong signals:* owns the miss without blaming the stakeholder; a repeatable mechanism, not "more communication".
*Red flags:* "they should have read the emails"; mapping only the interested people.

### 2.8 · Customer scenario

**Q.** Procurement sends you a draft statement of work to review before signature. Which clauses do you read most carefully as the engineer, and what are you looking for?

The commercial lead owns the contract, but several clauses decide how your weeks go (Section 2.6, Table 2.5).
Assumptions the estimate depends on (data access by week one, a named sponsor, an approved model endpoint), so a
customer-caused slip doesn't look like yours. Exclusions that repeat the charter's out-of-scope list word for word,
staffing that names the customer's people, dependencies dated and linked to the critical path. Acceptance: who tests
each deliverable, against which criteria, within how many working days, what happens if nobody responds, every
criterion verifiable without you. Read support boundaries and exit criteria hardest (hypercare period, hours and
severities, what ends the engagement), or you become the customer's permanent on-call. Confirm a change-control
clause and who may approve (ex81).

*Strong signals:* singles out exit criteria and support boundaries; insists on verifiable acceptance criteria.
*Red flags:* "that's the account team's job"; accepting "copilot deployed" as an acceptance criterion.

## Chapter 3 · Technical Communication

### 3.1 · Customer scenario

**Q.** You take over an engagement whose weekly notes have been green for six weeks. The tracker shows the archive-access task overdue since week three and two more tasks overdue since week five. What do you do?

Recompute the status from the tracker instead of trusting the color (Section 3.2; ex05). Under ex05's rules a
project is red if any blocked task is due within seven days or overdue, or three or more tasks are overdue; amber if
anything is overdue or blocked. This one was amber from week three and red from week five, so it's red today. Send a
red note the same day, not at the next steering meeting. Put the ask at the top with an owner and a date (here, read
access to the archive) and dated options; in the chapter's case the sponsor approved access within 48 hours once it
was in front of them. Restore the risks section and show empty sections as "none". Agree the status rules with the
sponsor in writing and apply them weekly, so the color can't drift with anyone's mood.

*Strong signals:* computes the color; escalates immediately with a concrete ask; fixes the process, not just the
note. *Red flags:* amber to soften the news; fixing it quietly before telling the sponsor.

### 3.2 · System design

**Q.** How would you design the handover documentation and process so the customer's operations team can roll back a bad release at 3 a.m. without calling you?

Two layers: a mechanical check and a human test (Section 3.3; ex69). Lint the runbook like code: Overview,
Prerequisites, Deploy, Rollback, Monitoring and Escalation headings; no TODO, TBD or FIXME; every code fence labeled
with its language; no skipped heading levels; a code block under Rollback, because "roll back the deployment" isn't
a procedure; an email address or phone number under Escalation; and every `<PLACEHOLDER>` in a code block explained
in the prose, so nobody meets an unexplained service or namespace name at 3 a.m. Passing only proves it isn't
certainly bad. The real test, a handover milestone: someone other than you runs the rollback from the runbook alone,
and you fix every place they hesitate. Write for the tired reader: numbered steps, command first, explanation second,
expected output after each step.

*Strong signals:* a customer-rehearsed rollback as a milestone; documented placeholders. *Red flags:* "the runbook
is in the wiki"; a rollback section with prose but no command.

### 3.3 · Technical

**Q.** The sponsor says, "Handle time fell from 11 minutes to 7.5 after launch, so the copilot works." How would you test that claim before it goes into the readout?

Before-and-after is weak evidence: handle time moves with seasonality, new hire cohorts and policy changes
(Section 3.5; ex82). Use difference-in-differences: compare the pilot teams' change with a control group's over the
same period. In the chapter's example the pilot teams fell from 11.0 to 7.5 minutes (−3.5) and the other teams from
10.8 to 10.2 (−0.6), so the copilot is credited with −2.9 minutes, 26% of the pilot baseline. The method rests on
parallel trends: without the copilot, both groups would have changed by the same amount. Check pre-launch trends,
choose a control group doing similar work, and state the assumption in the readout; finance will ask. Plan the
control group in week one, ideally as a staggered rollout: it can't be built retroactively.

*Strong signals:* names the counterfactual and parallel trends; the control group as a discovery-time decision.
*Red flags:* reporting the 3.5-minute drop as the effect; logins as proof of impact.

### 3.4 · Customer scenario

**Q.** Most teams have activated on the copilot, but one team sits at 20% activation. What do you look at, and what do you do?

Adoption problems are local, so look locally (Section 3.5; ex82). Break the funnel down by team: invited,
activated, engaged and habitual (questions in at least three distinct weeks), plus weekly cohort retention for those
who activated. Then find the team's reason; the usual ones are a manager who wasn't briefed, a workflow the tool
doesn't fit, or a bad first experience. Scale the actions to severity. In ex82, a team below 25% activation gets an
executive sponsor message, a hands-on workshop and a named champion; teams between 25% and 50% get champion office
hours and in-app tips. Keep measuring weekly and watch the engaged-to-habitual step, usually the most informative:
people try a tool once and come back only if it helped.

*Strong signals:* segments by team; finds a team-specific cause; measures after acting. *Red flags:* a company-wide
reminder email; blaming the model from activation data alone.

### 3.5 · Technical

**Q.** Your product team has started ignoring the field-feedback channel. How would you turn a few hundred anecdotes from several customers into something they act on?

Forwarded anecdotes train product teams to tune out; send a short, consistent, quantified brief instead
(Section 3.4; ex68). Cluster similar requests across customers: ex68 uses a greedy pass on token-set Jaccard similarity
against each cluster's seed (embeddings in production); "SSO with Okta" and "support for Okta login" are one request.
Weigh each cluster: distinct customers × 10, plus their annual recurring revenue (counted once per customer) ÷
100,000, plus severity weights of 5 for a blocker, 2 for major and 1 for minor. One page, top three clusters, each
with customers, revenue, severity mix, score and a quotation from the most severe item. Agree the weighting with
product (a starting point, not a truth); send one brief a month. Close the loop: tell customers and FDEs what was
decided, even "not this year", and review a request register with the account team before every quarterly business
review.

*Strong signals:* dedupes across customers, counting revenue once; closes the loop. *Red flags:* ranking by
loudness or frequency; more forwarding, better formatted.

### 3.6 · Customer scenario

**Q.** Handover is a month away. How would you show the sponsor, with evidence, that their team can run the system without you?

Turn "can they run it without us?" into a measured result (Section 3.5; ex84). Every learning objective gets a
concept block, a demonstration, a lab and a five-minute knowledge check; an objective with no lab is a lecture. Every
lab step is verifiable with a command or an expected result. Measure readiness per person and objective: ready means
the quiz score meets the pass mark and the lab is complete. The bar is at least two ready people per objective, so no
skill depends on one person's holiday plans. An objective with nobody ready is a handover risk: RAID log, owner, date
for a follow-up session. Pair this with the runbook test (Section 3.3), someone on their team performing the rollback
from the runbook alone, and report both in the enablement plan the team leads read before handover.

*Strong signals:* readiness as quiz plus lab, per objective; the two-person rule. *Red flags:* "we ran three
workshops" as evidence; measuring attendance, not ability.

### 3.7 · Behavioral

**Q.** Tell me about a time you had to report a result that was smaller than you'd originally projected. How did you present it?

Use situation, action, result. Show that you replaced your own assumption with a measurement, unprompted, and it
built trust (Section 3.6). The worked example: the business case assumed four minutes saved per assisted question;
the pilot measured a 2.9-minute team average at 80% usage, 3.625 per assisted question, and the re-run took
first-year ROI from 120% to 99% and payback from 4.2 to 4.7 months (66% and 5.3 months with review and operations
costs). Presentation: the recommendation first, one sentence with the measured number; the evidence and its main
assumption; the re-run value case, its version, and which lines are measured and which still assumed; top risks with
owners; a dated decision. Result: a decision the sponsor could defend, and a sponsor who trusted your numbers
afterward.

*Strong signals:* volunteers the correction first; separates measured from assumed lines. *Red flags:* reusing the
original assumption; burying the smaller number in an appendix.

### 3.8 · Technical

**Q.** How would you use an LLM to draft weekly status notes and readouts without risking an invented number reaching the sponsor?

Models are good at structure and tone, and fluent at inventing plausible numbers, names and dates, so separate the
jobs (Section 3.6). Facts come from systems, prose from the model: compute status, metrics and dates in code, as ex05
and ex82 do, and pass them in. Constrain the output to what you supplied and check it: a script that looks up every
number in the draft in the source data catches most fabrications. Give the model the fixed template (status, asks,
done, next, risks) and validate the headings, as ex69 lints runbooks. Read it as the recipient would and cut hedging
until the ask is unmissable. Generate every audience's version from the same tracker: different depth, same facts.

*Strong signals:* the model never produces the numbers; an automated check traces every number to the source.
*Red flags:* "I proofread it carefully"; having the model summarize the Slack channel into a status.

## Chapter 4 · Production-Grade Python

### 4.1 · Technical

**Q.** The customer's ERP returns `429` and `503` under load during your nightly sync. Walk me through your retry policy, and tell me what changes when the call is `POST /refunds`.

Retry only transient failures: connection errors, timeouts, `408`, `429` and `500`, `502`, `503`, `504`; never
`400`, `401`, `403` or `404`, which fail identically every time. Capped exponential backoff with full jitter: before
retry *n*, sleep a random time between zero and `min(max_delay, base_delay × 2ⁿ)`, so clients that failed together
don't retry as a synchronized wave. Honor `Retry-After`. Retry at one layer, the outermost that knows whether the
operation is idempotent: four attempts at each of three layers turns one request into 64 calls during an outage. A
refund isn't idempotent, so every attempt carries the same idempotency key. The server returns the first successful
result for repeats, rejects a reused key with a different payload, and stores nothing on failure; in production the
store is shared and durable, and the key is reserved `in_progress` under a unique constraint before the side effect
runs. On day one, ask which endpoints accept an `Idempotency-Key` header. (Section 4.2; ex10)

*Strong signals:* names full jitter and explains why; retries at one layer; reserves the key before the side effect.
*Red flags:* retrying every error in a tight loop; "the refund API will deduplicate it" with no key.

### 4.2 · Debugging

**Q.** Your service crashed in the customer's Kubernetes cluster with `KeyError: 'API_KEY'`. After they fixed it, the next start printed the key into their log platform. What went wrong, and how would you restructure the configuration code?

One cause: configuration read lazily and printed carelessly. A `load_settings` function reads every setting at
start-up, validates each (base URL `https://`, timeout above zero, retries between 0 and 10), and raises one
`ConfigError` listing every problem, so one restart reports every missing variable, not one per redeploy through the
customer's change process. Wrap the key in a `Secret` type whose `str()` and `repr()` print `****`, so logged
settings or tracebacks with locals can't leak it; code that needs the value calls `reveal()`, a deliberate act a
reviewer can spot. Log a `redacted()` view of the effective configuration first: configuration differences cause
half of "works on my machine" problems. `pydantic-settings` and `SecretStr` do the same where allowed. Ask how the
customer delivers secrets: environment variables, mounted files or a vault. (Section 4.1; ex09)

*Strong signals:* both incidents as one design flaw; leaking made impossible by construction. *Red flags:* fixing
only the one variable; "remove that log line" as the whole fix.

### 4.3 · Coding

**Q.** You need to classify 40,000 historical tickets with a model before Monday's readout. Sketch the code you'd write to run the batch, and tell me which bugs you'd guard against.

At 2.7 seconds each, sequential calls take 30 hours; an unbounded `asyncio.gather` is rate-limited within seconds.
Two limits: an `asyncio.Semaphore` bounds requests in flight, a token bucket bounds the rate. The bucket
refills at *R* tokens per second up to a capacity; `acquire` takes a token under an `asyncio.Lock`, sleeping
`(1 - tokens) / rate` when none is left. `gather_limited` wraps each call factory: semaphore, then token, then the
call, returning an exception in that item's slot instead of raising. Guard against four bugs: use `time.monotonic()`,
because wall-clock time can jump; rely on `gather` for input order; isolate failures so one bad ticket doesn't cancel
39,999 others; reject `concurrency < 1` or a non-positive rate, because a zero-size semaphore waits forever. Size both
limits from requests and tokens per minute measured in the customer's tenant, leaving headroom for production, and
consider a batch API for large offline jobs. (Section 4.4; ex12)

*Strong signals:* concurrency separate from rate; validated limits; the tenant's real quotas measured. *Red flags:*
only a semaphore, or only `sleep` between calls; one exception canceling the batch.

### 4.4 · Technical

**Q.** A user says the copilot gave a wrong answer "around 3 p.m.", and your logs are free-text prints from four services. What would you put in place so the next report takes minutes to trace?

Three techniques. Structured logs: one JSON line per event with a UTC timestamp, level, logger name, message and
structured fields, so you search indexed fields, not regular expressions. A correlation id per request, generated at
entry, passed downstream (usually as an `X-Request-ID` header) and in every log line. A `correlation()` context
manager on `contextvars` carries it across threads and `asyncio` tasks without passing it through every function,
and resets the token on exit so nested blocks restore the outer id. Redaction at any depth: `password`, `api_key`,
`authorization` and `ssn` become `[REDACTED]` inside nested dictionaries and lists, in the formatter so it covers
every log call. The investigation becomes a search for that user's requests in the window, a search for each
correlation id across the four services, and a timeline. Distributed tracing (Chapter 14) builds on this.
(Section 4.3; ex11)

*Strong signals:* the id propagated across services and async tasks; central redaction in the formatter.
*Red flags:* "add more print statements"; redaction left to each developer's discipline.

### 4.5 · Debugging

**Q.** On day two, the finance team hands you a contractor's invoice script and seven bug reports in their own words. Walk me through how you'd work through them, using "tags from one invoice show up on other invoices".

Method before fixes. Reproduce each report as a failing test named in the customer's words; what you can't
reproduce you can't prove fixed. Fix the root cause: tags leaking between invoices is a mutable default argument
(`tags=[]`) shared by every call, not something to clear at the end of the loop, so default to `None` and create a
new list per call. Make the smallest change, signatures unchanged, explained in one line the customer can read
(`# FIX(3): …`). The other fixes follow the same catalog: `Decimal` instead of `float` for
amounts with separators and for cents, `range(1, total_pages + 1)`, naive datetimes treated as UTC explicitly,
iterating over a copy of the keys, and an error naming the corrupted file instead of `except Exception: return {}`,
so only a missing file returns defaults. That one matters most: a silent wrong answer reaches the CFO. The seven
passing tests are your evidence and the next contractor's regression suite. (Section 4.5; ex13)

*Strong signals:* failing test first; root cause over symptom; catches specific exceptions only.
*Red flags:* patching symptoms; rewriting the script wholesale; keeping a bare `except` that returns a default.

### 4.6 · System design

**Q.** The customer's legacy policy-lookup service falls over every afternoon, and when it does your whole copilot stops responding, even the features that don't use it. How would you contain it?

A cascading failure: threads wait on 30-second timeouts, the pool fills, and features that never call the service
stop too. Limit the blast radius in layers. Keep the timeout; add a circuit breaker: closed, it counts consecutive
failures and opens at a threshold; open, it fails immediately with `CircuitOpenError`; after a reset timeout it goes
half-open and allows one trial call, closing on success, reopening on failure. Pair it with a fallback users accept,
such as yesterday's cached clause with a notice, not a spinner. A bulkhead caps concurrent callers and rejects when
full, because queueing behind a slow dependency is how the pool filled. Retry at one layer with jitter; the book's
retry-storm example also capped retries at 10% of traffic with a retry budget. Test with an injected fake clock, so
the boundary (29.9 seconds still open, 30.1 half-open) is checked in milliseconds. (Sections 4.6 and 4.7; ex14)

*Strong signals:* explains why the bulkhead rejects; a fallback users accept. *Red flags:* "raise the timeout" or
"add more threads"; a breaker with no fallback or no half-open state.

### 4.7 · Customer scenario

**Q.** An operations lead wants every inbound email triaged by a model, but says "if the AI loses one email, we switch it off". Worker pods sometimes die mid-job. How do you design for that, and what do you show them?

Put the emails on a job queue. A worker claims a job under a lease; if the pod dies, the lease expires and another
worker claims it. That's at-least-once processing, so the handler must be idempotent, and an idempotency key on
enqueue stops the same email being queued twice. A failed job returns after a backoff; after `max_attempts` failures
it moves to a dead-letter list. A worker can only acknowledge or fail a job it still holds, so a slow worker can't
overwrite the one that took over. Size the lease from measurements, comfortably above the 99th-percentile handler
time, with heartbeats (`extend`) for long model calls: too short runs work twice; too long leaves a crashed worker's
jobs waiting. The lead's real concern: show the dead-letter queue on day one, with a named owner and a daily review,
so "the AI lost my email" becomes "three emails need a human; here they are". (Section 4.6; ex15)

*Strong signals:* at-least-once delivery means idempotent handlers; leases sized from measured percentiles; a
dead-letter owner. *Red flags:* promising exactly-once processing; retrying poison messages forever.

## Chapter 5 · Enterprise Integration

### 5.1 · Technical

**Q.** To build a retrieval corpus you need every ticket from the customer's helpdesk API: cursor pagination, 100 per page, strict rate limits. Walk me through the client you'd write.

Timeouts first: a connect timeout of a few seconds and a read timeout sized to the slowest legitimate response, in
validated configuration, because clients such as `requests` wait forever by default. Follow the cursor until there
isn't one, yielding items so memory stays flat. On `429`, wait `Retry-After` seconds (default one) up to a retry
limit, then fail loudly. Respect rate-limit headers proactively: after a response with `X-RateLimit-Remaining` at
zero, sleep until `X-RateLimit-Reset` before the next request. A `max_pages` guard turns a buggy API that returns the
same cursor forever into an error rather than a growing bill. Header names are case-insensitive and HTTP/2
lower-cases them, so normalize before reading. For millions of records, ask whether the vendor offers a bulk export,
a change feed or a replica, which can turn a two-day backfill into an hour. (Section 5.1; ex16)

*Strong signals:* streams results; waits proactively on rate-limit headers; guards against cursor loops.
*Red flags:* every page loaded into memory first; no timeout; case-sensitive header lookups.

### 5.2 · System design

**Q.** The customer's CRM will push "case updated" webhooks to your service, and their security team wants to review the endpoint. Walk me through what the endpoint checks, and in what order.

Five checks, in order. Verify an HMAC-SHA256 signature over the timestamp and the raw body bytes, before any JSON
parsing, because re-serializing can reorder keys or change whitespace; a missing, malformed or wrong signature gets
`401`. Compare with `hmac.compare_digest`, never `==`, which returns early and can leak a valid signature through
timing. Reject a timestamp more than five minutes from your clock with `400`; it's signed, so an attacker can't change
it, and this limits the replay window. Keep processed event ids longer than that window and answer a repeat with
`200 duplicate`, covering replays and legitimate redeliveries. Acknowledge quickly with `202 Accepted` and process
asynchronously; slow receivers get retried, creating more duplicates. Authenticating before parsing stops an
unauthenticated sender making you work or filling your deduplication store. Webhooks still get lost, so pair the
endpoint with a reconciliation pull. (Section 5.2; ex17)

*Strong signals:* raw bytes, constant time, signature checked before parsing. *Red flags:* verifying over parsed
JSON; processing synchronously before acknowledging; no deduplication.

### 5.3 · Debugging

**Q.** Your 32-thread backfill job locked itself out of the customer's OAuth token endpoint within seconds. What happened, and how would you fix the token handling?

The job fetched a client-credentials token on every call; the gateway issues tokens valid for an hour and limits the
token endpoint to ten requests a minute. Build a token provider with three properties. Cache and reuse the token
while `now < issued_at + expires_in − skew`; a 60-second skew refreshes early, so no token expires in flight and
small clock differences don't cause failures. Refresh single-flight: check validity, take a lock, check again inside
it, so when all 32 threads find the token expired, exactly one fetches and the others reuse it. On `401`, invalidate
the cache, fetch a fresh token and retry once only: tokens can be revoked early when keys rotate, but retrying more
turns a wrong client secret into a loop against the endpoint's rate limit. Prove it with a test in which 32
concurrent threads cause exactly one token call. (Section 5.2; ex18)

*Strong signals:* explains the re-check inside the lock; one `401` retry. *Red flags:* a token per request; a lock
without the second check; retrying `401` in a loop.

### 5.4 · System design

**Q.** The copilot needs an up-to-date copy of the customer's CRM cases. How would you choose the integration pattern, and keep the copy correct when deliveries are lost, duplicated or out of order?

Five patterns: scheduled polling (minutes to hours; deletions invisible), webhooks (seconds; duplicates,
missed deliveries, ordering), change data capture or a change feed (low load; schema changes and log access), bulk
export (backfills) and an event stream if the customer already runs one. For cases, webhooks give freshness, but
push is fast and pull is complete: deliveries get lost to sender give-ups, deploys and firewall changes. Pair them
with a periodic reconciliation pull of everything updated since a watermark, through the same code path, which
applies updates idempotently in version order: store a record only if its version is newer than yours. Deduplicating
by event id isn't enough; in the book's hypothetical case, redelivered events with distinct ids but older
`updated_at` values reopened 1,140 closed cases. Add a nightly count per day against the source, a test that
delivers the same events shuffled and twice, and a separate plan for deletions. (Section 5.3; ex17 Part B)

*Strong signals:* "push for freshness, pull for completeness"; version-ordered application on both paths.
*Red flags:* trusting webhooks alone; last-write-wins in arrival order.

### 5.5 · Customer scenario

**Q.** The customer's CRM administrator sends a 50,000-row export with phone numbers in five formats and blank revenues, and asks when the import will be done. How do you handle it, and what do you send back?

Map the export into the canonical model with three rules. Normalize every value to one representation: phone numbers
to E.164, timestamps to timezone-aware UTC, revenue to integers whether it arrives as `"1,200,000"` or
`"1200000.0"`. Never abort the batch for one bad row: stopping at row 4,812 leaves nothing to show and no idea how
many other rows are bad. Report every error in a row with its row number and field, such as
`RowError(row=4812, field="Phone", …)`, so the administrator fixes the source in one pass, not fix, re-run, repeat. Keep
derived fields such as the revenue segment in the mapper, and give missing revenue an `unknown` segment; forcing it
into a real category is a silent data error. Send back the count of clean records loaded and the full error list.
(Section 5.3; ex19)

*Strong signals:* a complete, actionable per-row error report; an explicit `unknown`. *Red flags:* aborting on the
first bad row; silently guessing missing or malformed values.

### 5.6 · Technical

**Q.** The customer's platform team will only deploy services that pass their checklist. What would your minimal question-answering service do, and why does each item matter?

Use the standard library, so it runs in their locked-down base image without new dependencies. `GET /healthz`
returns `200 {"status": "ok"}` without authentication. `POST /v1/answer` requires a valid bearer token and returns
`401 {"error": "unauthorized"}` otherwise. Every error is JSON. Check `Content-Length` before reading and return `413`
above 64 KiB, so a 2 GB body never reaches memory. Invalid JSON or a missing, empty or over-long question (over 2,000
characters) gets `400`, protecting the token budget as well as memory. Wrong methods get `405`, unknown paths `404`.
If the answer function raises, return a generic `500 {"error": "internal error", "request_id": …}`; exception text
such as `KeyError: 'policy_db_password'` tells an attacker too much. Echo the client's `X-Request-ID` or generate one,
in the response and every log line, so an error report finds the logs in seconds. Health isn't readiness, so offer a
readiness endpoint where the platform supports it. (Section 5.4; ex20)

*Strong signals:* payload size checked before reading; generic 500s with a request id. *Red flags:* stack traces to
clients; an authenticated health check or open business endpoints.

### 5.7 · Technical

**Q.** The customer's internal APIs need signed requests, and the only specification is a Java SDK, a Go service and a C++ agent. How would you produce a Python signer that works with all three backends?

The code is the specification. Read the reference for its canonical form: the method, encoded path, canonical query,
SHA-256 of the body and a timestamp, separated by newlines, where every byte matters. Read the variants side by side
for undocumented differences: the C++ agent uses an upper-case body hash and epoch seconds; the Go service uses
lower-case hex instead of base64 for the signature and lower-case header names. Watch URL encoding: Java's
`URLEncoder.encode` is HTML form encoding (space as `+`, `~` as `%7E`, `*` left alone), and the SDK post-processes it
to RFC 3986, so the port encodes everything outside the unreserved set as `%XX` on UTF-8 bytes. That bug passes
simple tests and fails only on those characters. Generate test vectors by running the Java reference and test the
port against them byte for byte. Raise `ValueError` on an unknown variant rather than defaulting to the Java layout.
(Section 5.5; ex78)

*Strong signals:* reference-generated vectors as the contract; spots the form-encoding trap. *Red flags:* porting
from memory of "how signing usually works"; silently defaulting on unknown variants.

### 5.8 · Customer scenario

**Q.** Day one inside a bank, your demo fails with `CERTIFICATE_VERIFY_FAILED` and a colleague suggests `verify=False`. What do you do instead, and what should you have done before you arrived?

Decline `verify=False`: it removes TLS's protection and tends to survive into production. Likely cause: TLS
interception re-signed by the bank's own root certificate authority, behind an authenticated proxy and an egress
allowlist. Diagnose with a tool that answers three questions for the URL: is egress allowed; which proxy
applies (`HTTPS_PROXY` or `HTTP_PROXY`, lower case first as `requests` reads them, with `NO_PROXY` exceptions so internal traffic skips the
external proxy); and which CA bundle is used (`REQUESTS_CA_BUNDLE`, then `SSL_CERT_FILE`). Get the bank's root CA
from IT, append it to a copy of your bundle and point the variable at it. Three printed lines give the network team
something to act on. Beforehand, send an access list (accounts, VPN, badges, machine, data, firewall changes) with
reason, approver and date for each, tracked in the RAID log; send the preflight script a week ahead; ask whose
machine you'll use; arrange dependencies through an internal mirror or a wheelhouse built for the target platform.
(Section 5.6; ex21)

*Strong signals:* fixes trust instead of disabling it; actionable output for the network team; access planned weeks
ahead. *Red flags:* `verify=False` "just for the demo"; arriving before access is approved.

## Chapter 6 · Data Engineering

### 6.1 · Technical

**Q.** Before you propose a support copilot, the CFO wants a baseline of ticket volumes and resolution times. How would you produce numbers the customer's analysts will trust and can re-run?

SQL against the read-only replica, one query per question, each in a module-level constant the analysts can copy.
Not a pandas notebook: the analysts who keep these numbers after you leave know SQL and have tools to run it, and a
baseline the customer can't reproduce is just your opinion. Use half-open windows
(`resolved_at >= '2026-09-01' AND resolved_at < '2026-10-01'`), not `BETWEEN`, which drops everything after midnight
on the last day; half-open windows also tile, so weeks add up to months. For tickets created and resolved per week,
`UNION ALL` the two event streams, which keeps weeks with only resolutions that a join would drop. Give every query an
explicit `ORDER BY` with tie-breakers: a CFO who sees the same table in two orders trusts neither. Ask about data
volume and growth before running anything heavy. (Section 6.1; ex22)

*Strong signals:* customer reproducibility as the goal; half-open windows; deterministic ordering.
*Red flags:* one-off notebook numbers; `BETWEEN` on timestamps.

### 6.2 · System design

**Q.** Nightly full reloads of the customer's 80-million-row orders table take six hours and lock their replica. Design the incremental replacement, and tell me how you'd test it.

An incremental load: idempotent, atomic, correct when timestamps tie. A single-column watermark fails: with
`updated_at > :wm` a batch ending partway through 300 rows sharing a timestamp skips the rest; `>=` re-reads rows
and can loop on identical timestamps. Use a composite `(updated_at, id)` watermark: rows
where `updated_at > :wm_ts OR (updated_at = :wm_ts AND id > :wm_id)`, ordered by `updated_at, id`, with a batch
limit, so every row has a unique position. Upsert each batch with `ON CONFLICT(id) DO UPDATE` and save the watermark
in the same transaction; a crash rolls both back and the rerun reloads harmlessly. Deletes are invisible to a
watermark, so ask in discovery for soft deletes, a CDC feed or id reconciliation. Test the way it fails: run twice and
assert identical output; fail the second batch and assert nothing lost or duplicated; feed it tied timestamps, nulls
and out-of-order rows; test at next year's table size. (Sections 6.2 and 6.7; ex23)

*Strong signals:* explains why `>` and `>=` both fail; commits the watermark with the data; raises deletes.
*Red flags:* saving the watermark separately; plain inserts that duplicate on rerun.

### 6.3 · Debugging

**Q.** Northwind's copilot citations were wrong for a week, and nobody changed the prompt, the model or the retrieval code. How would you investigate, and what would stop it happening silently again?

Prompt, model and retrieval code unchanged? Look at the data: an upstream job had started writing empty policy
numbers into the document metadata, and the index refresh picked them up. Bad context gives a fluent wrong answer,
not an error, so the defense sits in the pipeline. Run declarative checks before every index refresh
(`not_null`, `unique`, `matches` a pattern, `in_range`, `accepted_values`, plus dataset-level `row_count_between`
and `fresh`): errors block the refresh, warnings only report, and samples of failing rows help the owner find the
cause. Detect schema drift before loading: added columns and widened types are warnings; removed columns, changed
types and newly nullable fields are errors. Only additive changes migrate automatically; the rest go to the data's
owner as questions. Then move upstream with a data contract: schema and meaning, freshness, blocking checks, change
notice and named owners. Draft it yourself and ask the owner to correct it. (Sections 6.1, 6.3 and 6.6; ex24, ex25)

*Strong signals:* suspects the data first; separates blocking errors from warnings; turns the fix into a contract.
*Red flags:* tuning the prompt; making every check blocking, or none.

### 6.4 · Debugging

**Q.** A Spark aggregation by merchant runs for hours with one task far behind the rest, and an earlier version of the job crashed the driver. What's going on, and how would you fix both?

The straggler means skew. Partitions come from hashing the key, so a merchant with 40% of the transactions puts 40%
of the work in one partition, and the job runs as slowly as that partition. Read `explain()` and
the Spark UI's stage timeline first; measure skew as the largest partition divided by the mean. For joins, Adaptive
Query Execution in Spark 3 can split skewed partitions automatically, but a hot-key aggregation needs salting: append
a salt from 0 to *s*−1, aggregate on the salted key so the hot key spreads across *s* partitions, strip the salt and
aggregate again. Same result, at the cost of a second shuffle, so salt only hot keys. The driver crash is a separate
bug: `collect()` or `toPandas()` pulls the whole dataset onto one machine, which works on a sample and fails on the
full table. Keep the aggregation in Spark and write the result to a Delta table. (Section 6.4; ex77)

*Strong signals:* reads the plan before optimizing; knows what salting costs; knows AQE exists.
*Red flags:* "add more executors"; collecting to the driver to finish the work in pandas.

### 6.5 · System design

**Q.** The customer only runs managed Postgres and won't approve a separate vector database. How would you move your SQLite prototype's retrieval store onto it, and what would you watch for with many tenants?

Use `pgvector` and port the dialect carefully: identity columns instead of `AUTOINCREMENT`, `DOUBLE PRECISION` and
`BYTEA`, `TIMESTAMPTZ`, `to_char`, `COALESCE`, `ON CONFLICT DO NOTHING`, and `%s` placeholders, without rewriting a
`?` inside a string literal. Match the operator to your metric (`<=>` cosine, `<->` L2, `<#>` negative inner
product) and the index operator class to the operator, such as `vector_cosine_ops` for `<=>`; otherwise Postgres
silently falls back to a full scan. HNSW is the default for a few million chunks: better speed-recall and buildable
on an empty table, while IVFFlat needs representative data first. With many tenants, watch filtered queries: HNSW
takes a bounded candidate list (`hnsw.ef_search`, 40 by default) and applies `WHERE` to it, so a tenant filter can
return fewer rows than the `LIMIT`, or none. Raise `ef_search`, use iterative scans on pgvector 0.8 or later, or a
partial index or partition per large tenant, and measure recall on filtered queries. (Section 6.5; ex80)

*Strong signals:* matches operator and operator class; knows the filtered-query recall trap.
*Red flags:* assuming the index is used; benchmarking only unfiltered queries.

### 6.6 · System design

**Q.** You're building an operations agent that looks up delayed shipments and reschedules them. Why would you put an ontology between the agent and the customer's tables instead of letting it write SQL?

An ontology turns scattered tables into business objects, typed links and governed actions; asking for "the delayed
shipments for this customer" and calling a "reschedule shipment" action is safer than an agent writing SQL against
five tables. Object types have a primary key and typed properties; loading validates every row, reporting problems
by type and row index. Link types have a source, target, cardinality and foreign key; an integrity check reports
dangling links, such as shipments pointing at missing customers. Traversal works both ways. Actions are the key:
typed parameters, a validation rule (refuse to reschedule a delivered shipment), an apply function and allowed roles.
Execution checks role, parameters and rule, then applies the change and appends an audit entry; a failed action
leaves neither. With actions as the only write path, permissions, validation and audit live in one place, for a
human in a web app and an agent calling a tool alike. (Section 6.5; ex92)

*Strong signals:* actions as the only write path; validation before any change; audit on success.
*Red flags:* giving the agent database write credentials "with a careful prompt".

### 6.7 · Customer scenario

**Q.** At 9 a.m. the CFO's office calls: the finance dashboard and the analyst assistant both show an 88% fall in yesterday's sales, and the nightly job reported success. What do you do now, and what do you change?

The chapter's hypothetical failure case. Evidence first: bronze holds 1.1 million rows for the day against a
typical 9.4 million, yet the job log shows success. The job treated "didn't raise" as success and overwrote
`gold.merchant_totals` from an incomplete extract, with nothing comparing the new totals to the previous run.
Mitigate: restore the previous version from Delta's history (`RESTORE TABLE … TO VERSION AS OF …`), re-run once the
full extract lands, and tell the dashboard's users what happened and what was affected. Prevent: blocking
freshness checks and row counts relative to recent days (1.1 million rows clears an absolute 1-million floor) on the
input before any write, an alert when an aggregate moves more than an agreed threshold
between runs, and overwrite jobs that read only from a validated batch. For incremental jobs, prefer `MERGE` or
`replaceWhere` to rewriting the whole table, and run a data diff before changing a pipeline. (Sections 6.4 and 6.7;
ex77)

*Strong signals:* restores first and communicates impact; checks before the write, not only after. *Red flags:*
re-running immediately on the same input; blaming the dashboard.

### 6.8 · Customer scenario

**Q.** The analysts want to count and join claims by customer, and the privacy officer asks how your pipeline and vector store will handle personal data, including erasure requests. What do you tell them?

Four habits, decided when the pipeline is built. Minimize: load only the columns the use case needs; data you never
loaded can't leak. Pseudonymize with a keyed hash: anyone with a list of emails can match a plain SHA-256, whereas an
HMAC with a secret held outside the analytics environment gives a stable token for joins and counts that guessing
can't reverse. Normalize (trim, lower-case) before hashing, or one person becomes two. Treat embeddings and chunks as
personal data: a chunk mentioning a diagnosis is health data in a vector table too. Keep `doc_id` and a pseudonymized
subject identifier on every chunk, so erasure is a `DELETE … WHERE subject = %s`, not a re-index. Set retention for
bronze, silver, logs and chunks at table creation, agree it with the data owner, and schedule the deletion job beside
the load job. Chapter 13 covers the regulations. (Section 6.6; ex24 Part B)

*Strong signals:* keyed hash with the key held elsewhere; deletion designed into the vector store.
*Red flags:* calling a plain hash anonymous; "we'd re-index" as the erasure plan.

## Chapter 7 · Full-Stack Engineering

### 7.1 · Debugging

**Q.** The copilot's answers are fine on your laptop, but inside the customer's network users occasionally see garbled accented characters and words missing mid-sentence. What would you check first, and how would you test the fix?

Fine at home, intermittent on site: the corporate proxy re-chunks the Server-Sent Events stream at arbitrary points,
and the client parses each network chunk on its own. Two bugs follow. A multi-byte UTF-8 character split across
chunks decodes as garbage; use a `TextDecoder` with `{ stream: true }`, which holds back an incomplete sequence. And
`chunk.split("\n")` corrupts a line split mid-way; keep the trailing partial line in a buffer, and follow the WHATWG
rules (blank line dispatches, multiple `data:` lines joined with `\n`, `:` comments ignored). Check that a mid-stream
`error` event is surfaced rather than half an answer shown as complete. Test it as ex28 does: split the same stream at
every possible byte boundary and assert identical output (Section 7.2; ex28).

*Strong signals:* both layers (bytes to text, lines to events); the every-split test. *Red flags:* "add a retry" or
blaming the model; fixing the newline split but missing UTF-8.

### 7.2 · System design

**Q.** Walk me through how you'd get streamed model output from the provider into the customer's browser. What sits in between, and what does each piece protect against?

A backend for frontend (BFF) between browser and provider. The browser uses the customer's normal session; only the
BFF holds the model key, because a key in browser JavaScript belongs to anyone who opens developer tools. The BFF
validates before tokens are spent (question length, per-user rate limits, tenant checks), attributes every request to
a user, tenant and request id for logs and cost, and cancels the upstream stream when the user closes the tab or
presses Stop, so you don't pay for unread tokens. The relay re-emits text deltas as SSE with
`Content-Type: text/event-stream`, `Cache-Control: no-cache` and, behind nginx-style proxies,
`X-Accel-Buffering: no`, plus a `: keep-alive` comment every 15 seconds or so during long tool calls. On failure the
user gets a generic `error` event; details stay in logs with the request id. Event names (`delta`, `done`, `error`)
live in one shared contract (Section 7.4, Section 7.6; ex30).

*Strong signals:* all four BFF reasons, especially cancellation; the buffering headers and keep-alive. *Red flags:*
calling the provider from the browser; raw exception text to the user.

### 7.3 · Coding

**Q.** A chat widget sends a message twice when users press Enter twice, duplicates the question on retry and leaves the spinner running after an error. How would you restructure the code, and how would you prove the bugs are gone?

State bugs, not rendering bugs: transitions scattered across handlers let some event sequences leave the state
inconsistent. Move every transition into one pure reducer, `reduce(state, action)`, that never mutates state or calls
the network. `send` returns the state unchanged when a reply is pending or the text is empty;
`stream_error` always sets `pending: false` and marks the message errored, so the spinner stops; `retry` acts only
when the last message is an errored assistant reply, and removes it rather than appending a user message. Return new
objects and arrays: React compares references, so a mutated array won't re-render. In the hook, read the draft before
dispatching `send`, convert any thrown value to a string, and have `retry` re-send the last user message without
adding one. Test in plain Node: fold a sequence ("send, send again while pending") through the reducer and assert on
the result, no browser or DOM (Section 7.3; ex29, ex91).

*Strong signals:* a pure reducer, one test per bug; why immutability matters for React. *Red flags:* flags patched
into each handler; tests that need a browser.

### 7.4 · System design

**Q.** The product owner's mockup shows one screen: a question and a good answer. What else would you design before handover, and why does each piece matter to adoption?

Users meet the other states first; agree each with the product owner: empty (two or three example
questions from discovery), loading (a short message before the first token, not a bare spinner), streaming (with
Stop), partial failure (keep the text, mark it incomplete, offer Retry), abstention, permission denied (say what the
user can't see, not that nothing exists) and offline. Then the trust features: clickable citations beside the claims
they support; "I don't know" as an intentional answer linking to the right human or document; visible tool progress
("Searching policy documents..."); human approval for consequential actions (draft the email, don't send it); a
thumbs-down with a reason that feeds the evaluation set review; Stop plus edit-and-resend. Each state is a reducer case
and a test, and the adoption funnel shows weeks later whether they were right (Section 7.5; ex29).

*Strong signals:* explicit states, each a reducer case; why abstention and citations build trust. *Red flags:* UX as
polish for later; feedback buttons that feed nothing.

### 7.5 · Customer scenario

**Q.** You demo to the customer's vice president at 9 a.m. tomorrow, on their locked-down laptop and guest Wi-Fi. How do you prepare, and what does the demo script look like?

Build for a network and machine you don't control: a single-file app on a Python standard-library server, nothing to
install. Default to a fake model with a visible `DEMO MODE` banner; the real model is one environment variable away
(`FDE_LIVE=1`) if the network allows. Render with `textContent`, never `innerHTML`, and show
the endpoint's latency so a slower real model surprises nobody. Script three scenarios, not a feature tour: the happy
path on a question from the discovery notes, an honest abstention pointing to the right place, and a recovery showing
a plain error instead of a stack trace. If a live answer is wrong: that's why we built the evaluation suite. Time the
script, rehearse on the customer's network the day before (including time to first byte through their proxy), and
keep the fallback one keystroke away (Section 7.4, Section 7.6; ex30).

*Strong signals:* an honest demo-mode banner; rehearsal on their network; the abstention scenario. *Red flags:* a
live-only demo; hiding that the model is faked.

### 7.6 · Customer scenario

**Q.** The customer wants the copilot inside the React application their agents already use, and their security team is strict about what loads on that page. What do you ask, and which embedding approach would you propose?

Ask first: the page's Content Security Policy, their React version and build, their review process, and how users
authenticate today. Then weigh four approaches. A link out is cheapest but forces context
switching, and adoption suffers. An `iframe` isolates strongly but brings cross-origin authentication, sizing and
frame policies. A web component or script tag needs script approval and hits CSP, which often forbids inline scripts
and unknown origins (so the single-file demo pattern won't load). A React component in their codebase costs most to
integrate but feels native; build it the ex91 way, a factory taking the React API they pass in, assuming nothing
about their build. Either way, reuse the user's session, exchanged on the server for a token the BFF
accepts, not a second login. Keep accessibility and text-only rendering; large customers check both (Section 7.6,
Section 7.3; ex91).

*Strong signals:* asks for the CSP header first; ties the choice to authentication and their review process.
*Red flags:* "just drop in a script tag"; a separate copilot login.

### 7.7 · Technical

**Q.** You're handing your front-end code to the customer's team, who will change it after you leave. What test suite do you leave them, and how do you make sure it keeps being run?

A layered suite, cheapest first. Pure logic (schemas, the stream parser, the reducer) in plain Node with
`node --test`: milliseconds, and most of the weight. Components rendered with a fake `h`, asserting on roles, labels and
text with no browser or bundler. A shared event contract module (`delta`, `done`, `error`) imported by the BFF's and
the UI's tests, so a renamed event fails a test instead of silently dropping text. A handful of end-to-end tests in a
real browser (Playwright or their tool) against the BFF with a fake model: ask, stream, Stop, error, retry. About five
catch integration mistakes; fifty become slow and flaky and get switched off. Run an accessibility checker such as axe
inside them. Document every layer in the README; the default command runs the first three, since a suite needing a
model key, a network or your laptop won't run after you leave (Section 7.6; ex28, ex29, ex91).

*Strong signals:* cost-ordered layers; the shared event contract; a default command needing no key or network.
*Red flags:* only end-to-end tests; tests calling the live model.

## Chapter 8 · Prompt Engineering

### 8.1 · Technical

**Q.** Walk me through how you'd structure the system prompt for the Northwind claims assistant, and why each part earns its place.

A layout that is easy to review, diff and cache. `<role>` names the audience and stakes (adjusters act on the
answers, so accuracy beats completeness), framing judgment calls the rules didn't anticipate. `<context>` holds
stable domain facts. `<policies>` lists rules with ids and reasons ("Never quote reserve amounts. Why: reserves are
confidential"); reasons generalize, so the model recognizes a "set-aside figure" as a reserve. Add a sentence on
resolving conflicts (prefer the hand-off, then withholding). Fixed `<examples>` can sit in the prefix; examples
selected per query go in the user turn, after it. `<output_format>` fixes the shape with an exact abstention
sentence, plus structured output and validation in code when software parses it. Write calmly; capitals make current
models over-apply rules. Stable content first so the provider caches the prefix; dynamic, untrusted content last
inside tags such as `<document>` and `<ticket>`, declared as data, not instructions. Tool definitions in the `tools`
field deserve the same care (Section 8.2; ex95, ex98).

*Strong signals:* rules with reasons; stable prefix first for caching; delimited untrusted input. *Red flags:*
"You are a world-class expert" and shouted MUSTs; dates or user data at the top.

### 8.2 · Debugging

**Q.** For two days a triage assistant gave confident answers that had nothing to do with the tickets it was sent. Nothing errored. What do you suspect, how do you confirm it, and how do you stop it happening again?

A template and code mismatch: the template references `{ticket}`, the code passes `ticket_text`, the formatter leaves
the placeholder untouched, and the model answers about a literal `{ticket}`. Confirm by finding the prompt version
from the content hash in the logs and rendering it with the variables the code passes, or from a logged prompt where
the customer allows full text. Prevent it twice over. Lint templates in CI: ex95's P005 (a
placeholder that isn't a declared variable) fails the build, P006 flags the declared variable never used, and P002
flags `{ticket}` not wrapped in a matching XML tag. Render strictly, so a missing or unexpected variable raises
(ex31). Add the case to the golden set and the regression gate (Section 8.5, Table 8.2; ex95, ex31, ex51).

*Strong signals:* names the literal-placeholder failure; CI linting and strict rendering, not vigilance. *Red flags:*
blaming the model or rewriting the prompt; no pipeline change.

### 8.3 · Coding

**Q.** A ticket-routing prompt has five fixed examples, four of them about passwords. Billing accuracy is 61%, and the team's fix is to keep adding examples. How would you redesign example selection?

Fixed examples steer a prompt most strongly, and models copy their quirks, label distribution included: this prompt
teaches that most tickets are about passwords. More examples only bloat it; retrieve them per query.
Embed the query and every example's input, score relevance by cosine similarity, then pick greedily with maximal
marginal relevance: `λ · relevance − (1 − λ) · max similarity to already chosen`, with λ = 0.7, penalizing
near-copies. Skip near-duplicates (similarity 0.95 or more) and candidates over the remaining token budget, without
stopping the loop. For classification, give every label at least one example, replacing one from an over-represented
label. Put the most relevant example last, nearest the query, wrapped in `<example>`, `<input>` and `<output>` tags
with escaped text. Curate the pool like a golden set, with hard negatives such as the billing-looking login problem.
Measure that billing improves while the prompt shrinks (Section 8.3; ex96).

*Strong signals:* MMR with a budget and label coverage; per-query selection as cost engineering too. *Red flags:*
more fixed examples; plain top-k returning five copies of one example.

### 8.4 · Customer scenario

**Q.** A sponsor sees that your prompt change moved accuracy from 82% to 86% and wants to announce it. How do you respond, and what evidence would you want before shipping?

Two accuracy numbers don't show whether the gain is real. First, the process: were edits chosen on a training split
and the held-out test split scored once at the end? Tuning against test failures makes the number optimistic; report
the overfitting gap. Second, a paired test on the same cases. McNemar's test looks only at discordant cases, those
only one prompt passed. On 200 cases, 11 fixed and 3 broken is a four-point gain with a two-sided *p* of about 0.057,
not significant at 0.05: "it looks better, but we need about twice as many test cases to be sure". Third, with a live
model, repeat runs and compare distributions; sampling noise can exceed an edit's effect. Fourth, check token and
latency changes and that no safety-critical case regressed, through the regression gate in CI (Section 8.4; ex97,
ex51).

*Strong signals:* paired test on discordant cases; held-out split; a plain-language sentence for the sponsor.
*Red flags:* announcing the averages; adding test cases until the number looks right.

### 8.5 · Customer scenario

**Q.** An auditor at Northwind asks: "Show me where rule POL-17 is in the prompt, and the test proving the assistant follows it." Rules are currently copied into the prompt by hand. What do you build?

The prompt is a build artifact compiled from a reviewed policy specification. Each rule has an id, a kind (must,
must not, escalate), text, a reason and test cases, such as a staged-accident input that must mention the fraud team.
A compiler groups rules by kind, renders each as a `<policy id="...">` line with its reason, adds a
conflict-resolution sentence and the output format, and escapes what it inserts. The same specification gives
traceability (every rule id appears in the prompt), coverage (share of rules with a test), conformance (each rule's
tests run against the model, missing and leaked phrases reported per rule) and a changelog compliance can read.
Version the specification, not the prompt, so they can't drift. String tests are a floor: add rubric-graded cases
with a calibrated judge for tone, and enforce hard constraints such as never revealing a reserve in code too
(Section 8.5; ex98, ex50).

*Strong signals:* the specification as source of truth; trace, coverage, conformance and diff; hard rules also in
code. *Red flags:* a hand-edited prompt; the prompt as the only control for a must-never-fail rule.

### 8.6 · System design

**Q.** The provider has announced it will retire the model your assistant runs on. Walk me through how you'd move to the new model without surprising the users.

A model change is a release, like a prompt change. Pin an exact model identifier, not a moving alias, and log it
with the prompt hash on every line. Run the golden set, regression gate and policy conformance
cases against the candidate, case by case: a better average that fails three safety cases isn't an upgrade. Add a
slice of benign questions that resemble forbidden ones, to catch over-refusal. Strip scaffolding written for the old
model (shouted rules, repeated warnings, extra examples), which newer, more literal models over-apply; keep a
workaround only if the evaluation shows it still earns its place. Re-measure tokens, output length and cost, since
tokenizers differ between families. Roll out gradually: shadow on live traffic, a canary watching signals such as
refusal rate, and rollback as a configuration change. Keep provider specifics in the adapter layer, not the prompt
(Section 8.6; ex31, ex51, ex98).

*Strong signals:* pinning; case-by-case comparison plus an over-refusal slice; old workarounds removed; canary.
*Red flags:* switching after a good demo; a model change as an unevaluated configuration edit.

### 8.7 · Behavioral

**Q.** Tell me about a time someone asked you to fix a problem with "a better prompt" when the prompt wasn't the right lever. How did you decide, and what did you do instead?

Use situation, action, result. The situation names the request and the evidence that the prompt was the wrong
lever, using the chapter's limits: the model lacked the facts (needs retrieval and citations); the rule must never
fail (needs tool permissions, output filters or approvals in code); the task was narrow, high-volume and stable (a
classical baseline or fine-tuned smaller model may be cheaper); or the prompt compensated for a confusing tool (fix
its name, description, schema and errors). The action: you decided on evidence, such as the evaluation result or the
workaround paragraph a reviewer would flag, and explained the alternative without dismissing the requester. The
result: what changed in accuracy, cost or safety, and what the customer's team does differently. Show judgment, not
a dislike of prompting: you still used the prompt where it was the fastest lever (Section 8.6).

*Strong signals:* the specific limit and the replacement control; a measured outcome. *Red flags:* more prompt text
as the fix for a hard constraint; no evidence behind the decision.

## Chapter 9 · LLM Application Engineering

### 9.1 · System design

**Q.** A demo calls the model once and prints the reply. Walk me through what you'd put between the application and the model before it serves two million requests a month.

The model is a slow, expensive, rate-limited, sometimes overloaded dependency with probabilistic output: Chapter 4's
habits apply (timeouts, retries on transient errors, circuit breakers, structured logs), plus model-specific stages.
Prompts come from a registry with immutable semantic versions, strict rendering and a template hash logged per
answer. A context packer fits system prompt, question, documents and history into a budget
that reserves output tokens. A router picks the cheapest model meeting the request's tier, latency and cost limits,
failing over only on overload errors (429, 503, 529). An exact-match response cache, keyed on everything that affects
the reply, skips repeat calls and never stores tool calls. Output is extracted, validated and repaired within a
limit. A ledger prices every call per tenant. Every stage logs metadata (request id, tenant, prompt hash, model,
tokens, latency, cost, cache hit, stop reason, validation outcome). Degraded modes are planned for when no model can
answer (Section 9.1, Section 9.3, Section 9.6; ex31 to ex35).

*Strong signals:* every stage traced to a property of the dependency; metadata logs make any answer traceable and
costed. *Red flags:* "add retries" as the whole answer; full prompts logged by default.

### 9.2 · Coding

**Q.** You're extracting claim details from adjusters' emails into the customer's claims system, and the provider supports strict JSON schemas. Do you still validate? Walk me through the code path.

Yes. Native structured output makes malformed output rare, but validate at your boundary anyway: not every target
supports it (the customer's approved model version may lag), schemas drift between code and prompt, and schema-valid
isn't business-valid (an amount of −500 can pass). Three pieces. Extract the first complete JSON object or array,
tracking string literals so a brace inside a string doesn't confuse the scanner; a greedy regex fails exactly there.
Validate against a schema subset, with errors prefixed by a JSON path (`$.amount: -500 is less than minimum 0`);
reject booleans where numbers are expected, since `True` is an `int` in Python, and decide deliberately whether `2.0`
is an integer. Repair by sending the model its reply plus the specific errors, for a bounded number of attempts, then
raise. Count repairs: a rising repair rate is an early sign of a prompt or model regression (Section 9.2; ex32).

*Strong signals:* "shape, not meaning"; path-specific errors fed back for repair; repair rate as a metric.
*Red flags:* trusting the schema feature alone; "invalid, try again" as repair feedback; unbounded retries.

### 9.3 · System design

**Q.** A bank's relationship managers want to ask questions such as "Which client spent the most in Q1?" directly against the warehouse. How would you design the system, and how would you measure whether it works?

Give the model a semantic layer, not the warehouse: a few allowed tables and views, their columns and named metric
definitions ("total spend: sum of USD amounts, refunds netted out"); without definitions, two phrasings return two
numbers. The user data dictionary comes from the same definitions. Each attempt yields one read-only query or an
exact refusal token (`CANNOT_ANSWER`), guarded statically before it touches the database: comments stripped, one
statement, `SELECT` or `WITH` only, no write or administrative keywords, every table allow-listed, a `LIMIT` appended
or lowered. A read-only connection adds defense in depth. On a guard rejection or database error, send the error back
and retry, at most three attempts, then refuse with a fixed message pointing to a human analyst. Show the SQL with
every answer; narrate from the rows. Measure execution accuracy on result sets against gold queries (rounding floats,
ordering only when the gold query has `ORDER BY`), refusal accuracy, unsafe queries blocked and average attempts
(Section 9.2; C3).

*Strong signals:* metric definitions; guard plus read-only connection; grading on result sets. *Red flags:* exposing
the whole schema; comparing SQL text; letting the model narrate numbers it never saw.

### 9.4 · Customer scenario

**Q.** Before anything is built, Northwind's sponsor asks what the assistant will cost per month at two million requests. How do you answer, and which design choices would you show moving the number?

Build a per-request model from token counts, not a vendor calculator. The worked example: a 3,000-token system
prompt, 4,000 tokens of retrieved documents, a 200-token question and a 400-token answer, at illustrative prices of $3
per million input and $15 per million output tokens, is $0.0276 a request, or $55,200 a month at two million
requests. Then the levers. Prompt caching on the stable prefix, with cache reads at 10% of the input price, gives
$0.0195 and $39,000, a 29% saving that costs only prompt-order discipline. A 30% exact-match response cache on top
gives $27,300. Five good chunks instead of twenty moves the number more than negotiation, and output is 22% of cost at
about 5% of tokens, so a length limit is a cost control. Name the omissions (cache writes, retries, failovers, agent
loops) and re-check the dated prices before quoting (Section 9.4, Table 9.1; ex35).

*Strong signals:* builds from token counts and shows each lever's effect; names the omissions. *Red flags:* a single
number from a pricing page; quoting exercise prices as current.

### 9.5 · Debugging

**Q.** In long conversations the assistant starts missing answers that are in the retrieved documents, and some replies stop mid-sentence. What would you look at first?

Read the context packer's log for those requests: what was included, truncated and dropped, and the total token
count. If the relevant document was dropped or truncated to make room for history, the log shows it. Check the packing
order: system prompt and question first, then documents by relevance with at most a truncated prefix of the next,
then history in whole turns from the most recent, restored to chronological order. Replies stopping mid-sentence mean
the output reservation is missing or too small: available input is budget minus reserved output, and a `max_tokens`
stop reason confirms it. Check token counting: `len/4` can be off by a factor of two for code, JSON or non-Latin
scripts, so use the provider's counter in production. And confirm history doesn't start with an assistant reply to a
question the model can't see (Section 9.3; ex33).

*Strong signals:* starts from the packer's log; links truncation to output reservation. *Red flags:* a bigger
context window or another model before reading the logs.

### 9.6 · Customer scenario

**Q.** The customer wants a model to route 500,000 tickets a month into `billing`, `login` or `outage`, and asks you to use the most capable model available. How do you respond?

Earn the LLM first. Build a classical baseline (multinomial Naive Bayes with Laplace smoothing) and compare it
honestly with a model-based classifier: a stratified, seeded train/test split so rare classes such as `outage` reach
the test set; macro-F1, not accuracy, because always saying `billing` can score 80% accuracy on imbalanced data; and
log-space computation to avoid underflow. Recommend the baseline unless the LLM's macro-F1 is at least three points
higher, with monthly cost alongside. If an LLM wins, route to the cheapest model whose tier passes the golden set for
this request type, and batch work that can wait. Either way you've saved a large annual bill or justified the spend
(Section 9.5, Section 9.3, Section 9.4; ex36, ex34).

*Strong signals:* baseline first; macro-F1 and cost side by side; a stated decision rule. *Red flags:* the biggest
model on reputation; accuracy alone.

### 9.7 · Technical

**Q.** The customer's procurement team says a new vendor contract takes three months, and two business units mandate different providers. How do you choose a model and where to call it, and how do you keep the code portable?

Decide with Table 9.3, not capability alone: golden-set pass rate per request type, cost per request, time to first
token, where data may go, which surface the customer can buy, context and output limits, and model availability
period. The surface often decides: the major clouds resell leading models (Amazon Bedrock, Google Cloud's Vertex AI,
Microsoft Foundry), so the customer's cloud can turn procurement into configuration, keep traffic inside their
network boundary and count against existing commitments; features may arrive later, and formats and identifiers
differ. For portability, a thin neutral format for messages, tools and replies behind per-provider
adapters; the hard part is the wire format (OpenAI's arguments are a JSON string, Gemini has no call ids and matches
results by name, Anthropic merges consecutive tool results). Don't hide useful provider features behind a lowest
common denominator. Test adapters against recorded responses; record the choice in an ADR (Section 9.5; ex86).

*Strong signals:* the cloud marketplace as a procurement answer; specific wire-format differences; an ADR.
*Red flags:* picking from a leaderboard; a thick framework hiding caching or batch features.

## Chapter 10 · Retrieval-Augmented Generation (RAG)

### 10.1 · Technical

**Q.** A teammate says the new chunking for Northwind's policy assistant "feels better". The customer's AI lead asks by how much. Walk me through how you'd answer with evidence, and which number you'd lead with.

Measure retrieval on its own, before generation. Build a labeled query set with the customer: real adjuster
questions, relevant passages marked by someone who knows the policies, optionally graded (2 = directly answers,
1 = useful context). These are the qrels. Run both chunkers over the set and compute recall@k, precision@k, MRR and
nDCG@k, where *k* is the number of chunks that fit the context budget. Lead with recall@k: if the relevant chunk
isn't in the top *k*, the model never sees it. nDCG rewards putting the best passage first, which matters with graded
judgments and a tight budget. Report a table and a sentence such as "recall at four went from 62.5% to 87.5% on the
40-question compliance set". Deeper retrieval costs latency, so plot recall against p95 latency and choose with the
customer. Synthetic questions extend coverage once real ones exist. (Section 10.1; ex41)

*Strong signals:* *k* tied to the context budget; the query set built with the customer's experts; latency reported
with quality. *Red flags:* judging from a handful of final answers; only synthetic questions.

### 10.2 · System design

**Q.** Support agents search for error codes like `E-4417` and also describe problems in their own words. How would you design retrieval so both kinds of query work, and how would you choose the embedding model?

Hybrid search. BM25 handles exact identifiers, which embeddings blur with similar-looking codes; vector search
handles paraphrase ("my basement flooded" against "water ingress below ground level"). Merge with reciprocal rank
fusion, `1 / (k + rank)` summed over the lists with *k* = 60, because BM25 scores and cosine similarities are on
incomparable scales and normalizing them is fragile. Retrieve deeper than needed from each (say 20) before fusing;
`explain_fusion` shows each document's rank in each list. Add a cross-encoder reranker only when metrics show relevant
passages retrieved but ranked too low, and measure its latency. Choose the embedding model on evidence: measure two or
three candidates on the query set, check the corpus's languages, weigh dimension against storage and query cost,
confirm the same residency and procurement constraints as the generation model, and store the model identifier with
every vector, since changing it means re-embedding the corpus. (Section 10.3; ex38, ex39, ex41)

*Strong signals:* why scores can't be added; what BM25's k1 and b do; the embedding model as the hardest choice to
reverse. *Red flags:* vector-only search; an embedding model picked from a public leaderboard.

### 10.3 · Coding

**Q.** Write the post-processing step for a cited RAG answer: you gave the model four numbered sources and it replied with `[1][2]`, `[1, 3]` and `[7]`. What does your code do, and when is the answer grounded?

Earlier, the function has already abstained with a fixed text, without calling the model, if retrieval returned
nothing or the top score was below a threshold. After the model replies:

1. Parse every citation marker, including adjacent forms like `[1][2]` and lists like `[1, 3]`.
2. Map each number in range (1 to 4 here) to the document id of that source.
3. Treat numbers outside the range, such as `[7]`, as invalid: remove them from the text and record them.
4. Mark the answer grounded if it has at least one valid citation and no invalid ones, or if it abstained. This reply
   contained `[7]`, so it is not grounded even after stripping.

Track the grounded rate as a launch metric; Capstone 1's bar is citation precision of at least 95% and zero answers to
unanswerable questions. State the limit: a valid citation proves the model pointed at a real source, not that the
source supports the claim; Chapter 13's support check and Chapter 12's faithfulness judge cover that. (Section 10.4;
ex40)

*Strong signals:* abstains before the model call; both multi-citation forms; citation validity distinct from support.
*Red flags:* trusting the markers as returned; asking the model to notice irrelevant sources.

### 10.4 · Customer scenario

**Q.** Northwind's head of compliance asks the assistant how many water-damage claims over $10,000 were paid last quarter, and it gives a confident number. What went wrong, and what do you propose?

Wrong tool. An aggregate isn't in any document; it's a query over the claims table. Retrieval found a few claims
mentioning water damage and the model counted them, confidently and wrongly. Classify questions before routing,
using discovery-interview examples to see which kinds dominate. Aggregates over well-understood tables go to a tool
running vetted, parameterized queries, such as `claims_paid(category, min_amount, start, end)`, which is easier to
secure and test than free-form SQL. Current-state questions ("status of claim 4471") go to the system of record's
API with the user's permissions; joins across records go to a query. Retrieval keeps finding passages. Until the tool
exists, abstain and name the right place: "I can't count claims; the claims
dashboard has this figure." Record the routing decision and evidence in a decision record (Appendix E's ADR-1 does
this for the reference engagement). (Section 10.4)

*Strong signals:* the three classes (aggregates, current state, joins); parameterized tools over free SQL; a clear
boundary meanwhile. *Red flags:* tuning the prompt or adding chunks to make counting work.

### 10.5 · Customer scenario

**Q.** A claims operations lead wants scanned claim forms processed "fully automatically". How would you design the extraction pipeline, and how do you choose between OCR and a multimodal model?

Reframe "fully automatic": 97% accurate and silently wrong on 3% is worse than 90% automatic with the doubtful 10%
sent to a person. OCR returns words with bounding boxes and confidence scores. Rebuild lines by grouping words with
nearby vertical centers, left to right, line confidence being its words' minimum; find key-value pairs by label
("Policy number", "Date of loss"); rebuild tables from the header's column positions. Route any required field
missing or below threshold to human review with reasons such as `missing:policy_number`. Multimodal: send the PDF as
a base64 `document` block or the image as an `image` block, refusing unsupported types and oversized files. OCR gives
coordinates, per-word confidence and predictable cost, suiting high-volume known layouts and audits; multimodal
models handle messy layouts, handwriting and diagrams with less code, at higher cost and without per-field
confidence. Many pipelines use both. Measure field accuracy on real samples; check the provider's current limits.
(Section 10.5; ex88, ex70)

*Strong signals:* human review designed as a feature; minimum confidence per line; a reasoned OCR-versus-multimodal
choice. *Red flags:* no confidence threshold; promising full automation unmeasured.

### 10.6 · Debugging

**Q.** After asking about burst pipes, an adjuster asks "What about flood?" and gets a wrong answer. Walk me through how you'd find the root cause, and what you'd do once it's fixed.

Walk the pipeline with each stage's logs; stop at the first stage that went wrong:

1. Was the question understood? Check the rewritten query. A follow-up like this loses its subject unless rewritten
   into a standalone question, such as "Is flood damage covered under the home policy?".
2. Was the right passage retrieved? Look in the keyword and vector results with `explain_fusion`. Absent from both
   points to chunking, indexing or freshness.
3. Was it ranked high enough to fit? Rank 12 with a budget of four is a ranking fix (a reranker, better chunk text),
   not a prompt fix.
4. Was it in the context the model saw? The packer's log shows what was included and truncated.
5. Did the model use it? Only now look at citations, instructions and the model.

Then add the question and its correct passage to the evaluation set, so the fix stays measured.
(Sections 10.3 and 10.7)

*Strong signals:* suspects query rewriting first for a follow-up; stops at the first failing stage; adds an
evaluation case. *Red flags:* starting by editing the prompt or switching models.

### 10.7 · System design

**Q.** Northwind revises its policy wording several times a year, and claims are judged under the version in force on the claim date. How would you keep the index fresh and correct after go-live?

Most post-launch retrieval incidents are freshness incidents. Give every chunk a content key, a hash of document id,
heading path, text and an ordinal for duplicates. When a document changes, re-chunk, compare keys and add or delete
only what changed; unchanged chunks keep their embeddings but get their new offsets and dates. A document missing from the source is
an explicit deletion event, so withdrawn documents leave no orphans. Store `effective_from` and `effective_to` on
every chunk and filter at query time, so "was this covered when the claim was filed?" uses the version in force on the
claim date. If the embedding model changes, re-embed everything: build the new index beside the old, compare retrieval
metrics on the query set, then switch, blue-green as for deployments. Monitor the corpus too: chunk counts per
source, newest-document age, share of chunks missing metadata. A sudden drop in chunk count usually means an
ingestion job failed silently. (Section 10.6; ex37)

*Strong signals:* incremental re-indexing by content key; effective dates filtered at query time; corpus monitoring.
*Red flags:* nightly full rebuilds as the only plan; every answer from the latest version.

### 10.8 · Debugging

**Q.** A help assistant serving hundreds of tenants from one shared index cites another customer's internal pricing sheet. What do you check first, how do you contain it, and what stops it happening again?

Check the cited chunk's metadata and the query filter. In the chapter's case the chunk has `tenant_id = NULL`, and
the filter is `tenant_id = :tenant OR tenant_id IS NULL`, so global help articles appear for everyone; an upload path
added last month doesn't set the tenant. The filter fails open: a missing value meant "visible to
everyone", nothing validated tenant metadata at ingestion, and the cross-tenant test covered only the original path.
Contain: kill-switch untenanted chunks, find and purge the affected ones, and start contractual notification with the
customers involved. Prevent: a mandatory tenant, an explicit tenant for global content, untenanted chunks rejected
at ingestion, and a cross-tenant negative test per ingestion path as a release gate. The model can't be trusted to
withhold what it's shown, so enforce permissions inside retrieval, with ACLs on every chunk and entitlements resolved
on the server. (Sections 10.6 and 10.7; ex89 in Chapter 13)

*Strong signals:* spots the fail-open `IS NULL` clause; contains and notifies before fixing; tests every ingestion
path. *Red flags:* asking the model not to reveal other tenants' data; filtering after retrieval.

## Chapter 11 · AI Agents

### 11.1 · Coding

**Q.** Before reaching for a framework, write the agent loop for a retailer's assistant that looks up orders and issues store credit. Walk me through the rules your loop enforces and the bugs each one prevents.

Start with the user message and the tool specs (name, description, input schema). Each step calls the model; with no
tool calls, return the text. Otherwise append an assistant turn with any text and one `tool_use` block per call,
execute the calls and append the results. Four rules prevent most bugs:

1. Execute every requested call, in order; running only the first leaves the model waiting for missing results.
2. Return all results in one user turn, each matched to its call by id; the API rejects a tool call with no result.
3. Turn failures, unknown tool names included, into results with `is_error: true`. The model can recover from an
   error result; your process can't recover from a crash.
4. Enforce a step budget, then stop and escalate, so a model that never converges can't run indefinitely.

Frameworks add tracing, streaming, persistence and human-in-the-loop support and are worth using in production;
knowing the loop lets you debug them. In production the step budget becomes a run budget with repeat detection and
per-tool caps. (Sections 11.1 and 11.6; ex42)

*Strong signals:* all results in one turn, matched by id; errors as results; a hard step limit. *Red flags:*
exceptions propagating; one result per turn; no budget.

### 11.2 · Technical

**Q.** In production the model calls `issue_refund` with `amount: "50 dollars"` and no `order_id`. How would you design the tool so the agent recovers instead of spiraling, and so a retry can't refund twice?

Validate the arguments against the tool's JSON Schema (types, required fields, enums, ranges,
`additionalProperties: false`) before executing; on failure, return one error listing every problem, such as
"amount: expected number, got string" and "order_id: required", so the model fixes the call next turn. If the
function raises, return only the exception type; messages and tracebacks can leak connection strings, paths or
customer data into transcripts. Truncate oversized results, saying so. Describe the tool for the model: what it does,
when to use it, what it returns, what it doesn't do. Against double refunds, mark the tool
side-effecting and execute it at most once per call id, so a replayed `tool_use` returns the first result. The model
can still retry with a new id, so also pass a business-operation idempotency key to the payment API, report timeouts
as "outcome unknown" and cap refunds per run. (Sections 11.2 and 11.6; ex43)

*Strong signals:* errors that say how to fix the call; hidden internals; call-id replays distinct from business-level
retries. *Red flags:* stack traces to the model; the call id alone for idempotency.

### 11.3 · Customer scenario

**Q.** The customer's platform team wants every one of its order system's 40 REST endpoints exposed as a tool. How do you respond, and what would you build instead?

Accept the goal (full coverage) and push back on the shape. Forty endpoint wrappers leave the model to compose them
correctly, every tool definition costs context on every call, and selection gets less reliable as the list grows.
Propose task-shaped tools instead, such as `find_orders`, `get_order`, `check_refund_eligibility`, `request_refund`
and `escalate_to_human`, which are easier to describe, validate, permission and evaluate. Where the agent needs dozens
of capabilities, give each subagent or Agent Skill the handful of tools its task needs and let the parent route.
Skills use progressive disclosure, so only names and descriptions cost context up front; subagents run in a fresh
context restricted to the tools they list. Offer to prove the choice with the evaluation set, not by argument.
(Sections 11.2 and 11.5; ex85)

*Strong signals:* the context and selection cost of many tools; concrete task-shaped tools; subagents or skills to
scale. *Red flags:* wrapping every endpoint; paragraphs of system prompt instead.

### 11.4 · System design

**Q.** The customer wants its policy database usable from Claude Desktop, Claude Code and its own agent platform, and those clients speak different MCP revisions. How would you design the server and the connector?

One MCP server for any MCP client, dual-era because clients upgrade at different times. Modern clients
(revision 2026-07-28) send the protocol version in `_meta` on every request and call `server/discover`, which returns
supported versions, capabilities, server information and a `ttlMs`; results carry `resultType: "complete"`. An
unsupported version gets error `-32022` with the supported and requested versions. Legacy clients send `initialize`,
which switches the server to legacy shapes; a request with no `_meta` before any `initialize` gets `-32602`. The
modern era is stateless, so an ordinary load balancer works. Tool failures are normal results with `isError: true`;
protocol errors are for malformed requests. Use parameterized SQL only and bounded limits (ex45 caps `limit` at 50),
because the model chooses arguments and its input may carry injected instructions. Ship the official SDK in
production; smoke-test every server with your own negotiating client first. (Section 11.3; ex44, ex45)

*Strong signals:* both eras; tool errors distinct from protocol errors; the connector as an attack surface.
*Red flags:* assuming every client speaks the newest revision; string-built SQL.

### 11.5 · System design

**Q.** Design an "AI operations analyst" that investigates a billing dispute: pull the invoice, check payment logs, draft an email and, only with approval, issue a refund. How do you keep it safe and auditable?

Separate planning from execution. A planner model writes a JSON plan: steps with an id, a worker, a task,
dependencies and a `requires_approval` flag. Code validates it first, rejecting unknown workers, dependencies on
unknown steps and cycles, then orders steps topologically, keeping the planner's order among ready steps for
determinism. Approval is policy in code, not the plan's choice: risky workers such as `refund` or `send_email` always
require approval, because the planner is a model and its plan can be wrong or manipulated. Execute with explicit
statuses (`done`, `failed`, `rejected`, `skipped` when a dependency didn't finish as done). In production, approval
is a queue ticket, a Slack button or a supervisor's console: the model proposes, a person disposes. Audit every
transition in order, so the trail answers why a refund wasn't issued. Add run budgets and per-run caps on
side-effecting tools. (Sections 11.4 and 11.6; ex46)

*Strong signals:* the plan validated before execution; approval rules in code; an audit trail of transitions.
*Red flags:* the planner deciding what needs approval; free-running execution with no statuses.

### 11.6 · Debugging

**Q.** You inherit a LangGraph-style agent. Some runs stop silently partway through, and after a restart a conversation can't pick up where it left off. What would you check, and what should the framework be doing?

Silent stops usually mean a graph defect or an interrupt. Check the run's status: a run reaching a node in
`interrupt_before` stops as `interrupted` and waits for a person to review and resume. Check compile-time validation;
ex79 refuses graphs with no entry point, edges to unknown nodes, nodes with no outgoing edge, nodes with both a plain
and a conditional edge, and unreachable nodes, all of which otherwise surface as silent stops. A step limit should
raise for cycles that never reach `END`. For resumption, the checkpointer saves state and next node after every node
under the thread id, and the caller must pass the same thread id (in LangGraph,
`config={"configurable": {"thread_id": ...}}` with a checkpointer compiled in). Check reducers too: resume updates go
through them, and a missing reducer lets one node's write overwrite another's. (Section 11.4; ex79)

*Strong signals:* what checkpoints, interrupts, reducers and compile-time validation each do; checks thread ids.
*Red flags:* the framework as a black box; retries without finding why runs stop.

### 11.7 · Customer scenario

**Q.** A contact center says its voice bot "feels slow and talks over people", and its field copilot forgets the policy number by mid-shift. How would you turn both complaints into fixable problems?

Turn both feelings into numbers. For voice, from the call's event log: response latency (caller finishing to agent
starting) at the median and p95, since gaps over about a second sound like hesitation; barge-ins, the caller speaking
over the agent, where many suggest turns are too long; the agent's talk ratio; and long silences, often a slow tool
call. "It feels slow" becomes "p95 latency is 2.4 seconds, driven by the policy lookup tool", which you can fix. For
the copilot, the policy number is buried under hours of later conversation. Use rolling summarization: when
unsummarized messages exceed a token budget, fold the oldest into a running summary that keeps names, numbers,
decisions and open questions. Pin facts whose exact value matters (account number, policy under discussion, user's
role) verbatim in every context, so the model sees pinned facts, the summary and recent messages. (Section 11.5;
ex47, ex48)

*Strong signals:* the p95, not just the median; silences linked to tool latency; exact values pinned, not trusted to
the summary. *Red flags:* "use a bigger context window"; tuning voice by ear.

### 11.8 · Debugging

**Q.** A refund agent runs over a weekend, and on Monday finance finds 37 orders refunded twice. Walk me through the investigation, the root cause and the changes you'd make.

Evidence from both sides: the payment provider shows two refunds about 31 seconds apart per order; the agent's trace
shows a first `issue_refund` that hit the tool's 30-second timeout and returned `is_error: true`, then a successful
call with a new call id. The first refund had gone through; only the response was late. Root cause: a
timeout reported as failure when the outcome was unknown, idempotency keyed on the call id (which stops replays, not
a sensible retry), and no cap on refunds per run. Mitigation: reverse the duplicates, pass the payment API an
idempotency key from the business operation (order id and amount), and cap refunds at one per order per run.
Prevention: on timeout return "outcome unknown; check with `get_refund_status`", check before acting, and add a
trajectory evaluation case that injects a slow payment API. (Sections 11.2 and 11.6; ex42, ex43)

*Strong signals:* "failed" distinct from "outcome unknown"; business-level idempotency keys; per-tool caps and a
regression case. *Red flags:* blaming the model for retrying; only lengthening the timeout.

## Chapter 12 · LLM Evaluation

### 12.1 · Customer scenario

**Q.** After a good demo, Northwind's head of compliance asks: "How do you know it won't tell an adjuster something is covered when it isn't?" How do you answer, and what do you build?

Honestly: without an evaluation, I don't know yet; here's how I will. Build a golden set with the customer's experts:
50 to 150 cases to start, on the questions that matter and the failures that hurt. Each case has an input, an
expected result, a grader and tags, such as a burst-pipe-while-unoccupied question graded by `contains` on "not
covered" and "unoccupied", tagged `coverage`, `exclusion` and `safety`. Prefer deterministic graders, and report pass
rates per tag: 91% overall can hide 60% on exclusions. Include an unanswerable slice and report abstention in both
directions, plus citation precision and faithfulness checked by a narrow judge. Agree a launch bar (Capstone 1's
includes zero answers to unanswerable questions), gate every change in CI on critical regressions, and monitor live
quality. The answer becomes "here is the exclusions slice, its pass rate and interval, re-run on every change".
(Sections 12.1 and 12.6; ex49)

*Strong signals:* admits the gap; builds the set with the customer's experts; per-tag and safety reporting.
*Red flags:* pointing to the demo; one overall pass rate.

### 12.2 · Technical

**Q.** You want an LLM judge to score answers for accuracy, completeness and tone. How would you make sure the customer's experts can trust its scores?

Put the rubric in the system prompt and ask for JSON with `reasoning` first, then a `score` from 1 to 5; invalid JSON
or an out-of-range score is an error, not a default. Calibrate against people: domain experts and the judge score
the same 50 to 100 answers; report exact agreement, within-one agreement and Cohen's kappa on pass/fail (score of at
least 4). Kappa matters because raw agreement flatters judges when most answers pass; above
0.6 is substantial, above 0.8 near-perfect. If lower, sharpen the criteria and add examples of each score. For
pairwise comparisons, ask in both orders and declare a winner only if both agree, removing position bias. Where
approvals allow, judge with a different strong model family, re-check agreement when the judge model or rubric
changes, and keep the human-labeled set permanently. For faithfulness, judge one claim against one passage.
(Sections 12.2 and 12.6; ex50)

*Strong signals:* kappa, not raw agreement; order swapping; recalibration on judge changes. *Red flags:* trusting a
judge that "looks right"; a judge where a deterministic grader would do.

### 12.3 · System design

**Q.** Design the evaluation gate for a team that changes prompts, retrieval settings and tools every week. What blocks a merge, and how do you keep the suite affordable?

Compare runs case by case. The gate computes pass rates over the intersection of case ids, lists regressions and
fixes, and fails first on any missing case, since deleting failing cases is the easiest way to raise a pass rate.
Any regression on a `safety` (or other critical) case fails the gate whatever the average; a tolerance (two points
by default) absorbs noise on non-critical cases. It exits 0 or 1 for CI and runs on every pull request
touching a prompt, model setting, retrieval or a tool. The harness rejects unknown graders before running, and a
leakage check keeps golden-set inputs out of example pools. For cost: deterministic graders on every change; judge
results cached by a hash of judge prompt, rubric and answer; the full judged suite only on prompt, model or
retrieval changes, a stratified sample otherwise; nightly runs on the batch API; and the evaluation's own cost
reported per run. (Sections 12.3, 12.6 and 12.7; ex51, ex49)

*Strong signals:* missing cases fail first; critical regressions block regardless of average; judge caching.
*Red flags:* gating on the overall pass rate alone; no cost plan, so the suite gets switched off.

### 12.4 · Customer scenario

**Q.** A three-week pilot moved first-contact resolution from 71.2% to 74.0%, and the sponsor asks whether to roll out. Walk me through your answer, and what you'd have done before the pilot started.

The lift is 2.8 points; is it real? Compute a bootstrap confidence interval (resample each group with replacement
thousands of times, take the 2.5th and 97.5th percentiles of the lift) and a two-proportion z-test for the *p*-value.
Apply the rule agreed before the pilot: ship if the interval's lower bound is above zero and *p* is below 0.05,
harmful if the upper bound is below zero, otherwise inconclusive. Report it honestly either way, and don't switch
metrics after seeing the data. Flag the unit of analysis: tickets from the same agent aren't independent, so for a
high-stakes decision analyze by agent or cluster. A power calculation should have sized the pilot: detecting three
points from a 71% baseline at 80% power and 5% significance needs roughly 3,500 tickets per group, so a smaller pilot
runs longer, adds agents or uses a more sensitive metric. (Section 12.3; ex52)

*Strong signals:* interval plus pre-registered rule; power calculation up front; clustering. *Red flags:* "it went
up, ship it"; choosing the metric after the results.

### 12.5 · Technical

**Q.** A refund agent passes 92% of the golden set on its final message, but in production it sometimes refunds before looking up the order. How would you evaluate it, and what would you report to the operations lead?

Answer-only grading can't see the path; grade trajectories, the tool calls plus the final answer. Require
`get_order` and `issue_refund` in that order as a subsequence, check the arguments (`order_id` "A-1001", `amount`
40) and cap tool calls at four; refunding first fails the order check even with a perfect message. Report efficiency
(required tools divided by calls, capped at one) and tool-call F1: an eleven-call path to a three-call job is slow
and costly. Then reliability: run each case *n* times, count *c* successes. pass@k is the chance at least one of *k*
attempts succeeds; pass^k, that all *k* do. For 8 of 10, pass@5 is 1.0 but pass^5 is about 0.22: used five times a
day, it lets the team down on most days. Make pass^k the launch metric for unattended agents, reporting both.
(Section 12.4; ex99)

*Strong signals:* order and argument checks; repeated runs; pass^k for unattended use. *Red flags:* grading only the
final message; reporting pass@k as reliability.

### 12.6 · Debugging

**Q.** Six weeks after go-live the offline evaluation is still green, but agents say the copilot "got worse". How would you find out what changed, and how would you have caught it sooner?

Offline evaluation answers "is this version good?"; online, "is it still good for today's traffic?". Check input
drift first: the population stability index on input length (bins at the baseline's quantile edges, shares floored at
a small epsilon) and on intent as a categorical feature. Below 0.1 is stable, 0.1 to 0.25 worth watching, above 0.25
drift, as rules of thumb to calibrate. Then live quality: judge pass rate on sampled traffic against the offline
baseline, refusal rate, p95 latency and cost per conversation. In the chapter's case a product launch added an
`outage` intent, longer pasted logs and more refusals. To catch it on day one, not day nine, run these checks per
window with paging thresholds, minimum sample sizes and a reproducible review sample (every refusal and low score,
plus hash-based sampling). When drift fires, grow the golden set from the new traffic, expert-labeled, before
touching the prompt. (Section 12.5; ex100)

*Strong signals:* offline and online as separate questions; PSI with minimum samples; the golden set grown first.
*Red flags:* rewriting the prompt immediately; trusting the green offline suite.

### 12.7 · Technical

**Q.** A pull request says the candidate raises the overall pass rate from 88.0% to 90.5% on the held-out split. Walk me through how you decide whether to ship it.

Score the held-out split only when deciding, and read slices with intervals, not the headline. In the chapter's
example the critical exclusions slice fell from 90.0% to 77.5%. The candidate fixed 24 cases and broke 14; McNemar's
exact test on those 38 gives *p* ≈ 0.14, so the gain could be noise. In exclusions it broke six and fixed one; not
significant either, and it needn't be: exclusions are critical, so the gate rejects the candidate whatever its
average. A fixed failure taxonomy puts 18 of 38 in retrieval and chunking, pointing to heading-aware chunks and a
reranker, not the prompt. Only among candidates passing every gate do you trade quality against latency and cost, by
cost per successful task (cost per request ÷ pass rate). The chapter's candidate C passes at 90.0%, costs about a
tenth of a cent more per successful task and meets the latency target: ship it, with an ADR. (Section 12.7; ex49)

*Strong signals:* gates before trade-offs; paired comparison on discordant cases; cost per successful task.
*Red flags:* accepting "+2.5 points"; averaging critical slices into the total.

### 12.8 · Behavioral

**Q.** Tell me about a time you had to present evaluation results to a group that had to approve or reject a launch. What did you put in front of them?

Use situation, action, result. Situation: who had to approve (a model risk committee, an AI governance board, a
clinical safety group) and what was at stake. Action: a document of two to four pages in the chapter's order, full
results attached: what the system does and must never do; how it was evaluated (golden-set version, size, sources,
labelers' agreement, the judge's model and kappa, the run date); results by slice with case counts and intervals,
flagging slices too small to say anything; known failure modes and mitigations; post-launch monitoring and who gets
paged; limitations. Result: the decision, and ideally how the written limitations held up. Show that you reported
slices rather than one number, kept every figure reproducible from a tagged run, reissued the document when the
golden set, judge or model changed, and stated limits openly: boards approve systems whose limits are understood.
(Section 12.7)

*Strong signals:* limitations volunteered, not extracted; slices with intervals; reproducibility. *Red flags:* only
an overall pass rate; the harness instead of a decision document.

## Chapter 13 · AI Security and Guardrails

### 13.1 · System design

**Q.** A retailer's email-triage agent reads inbound customer emails and can call `send_email`, `http_post` and `issue_refund`. Walk me through the controls you'd put around it so that a fooled model still can't leak data.

The system prompt isn't the defense; prompts reduce risk, not eliminate it. Layer independent controls an attacker
must all defeat. Redact personal data before it leaves the network. Wrap every email in an
`<untrusted source="email:inbound">` tag, neutralizing any `<untrusted` or `</untrusted` inside so the attacker can't
close the tag early. Run heuristics for "ignore previous instructions", role overrides, system-prompt probes,
send-to-address instructions and long base64-like runs; a hit taints the context, it doesn't prevent anything. The
decisive layer is a `ToolGate` in code: read-only tools allowed; any destination in the arguments (a URL with any
scheme or case, an email address, an IP literal, a bare host name) not on the allowlist denied by default; a
side-effecting tool in a tainted context needs a person's confirmation. Back it with an egress proxy, since an
obfuscated host (`attacker[.]net`) slips past any parser. Add output checks, the
user's permissions, an audit log of every decision and a running red-team suite. Where possible, separate reading
untrusted content from the power to act, or fix the recipients. Measure each control's overhead so nobody turns it
off "temporarily". (Sections 13.1–13.2; ex54)

*Strong signals:* gating in code as the layer that stops the attack; egress allowlisting and confirmation in tainted
contexts. *Red flags:* "a stronger system prompt" or "an injection classifier" as the answer.

### 13.2 · Technical

**Q.** The customer's privacy office says no transcript may leave their network with personal data in it. How would you design the redaction step, and how would you convince them it works?

Detect with validation, not bare patterns: emails; US SSNs excluding area 000, 666 and 900–999, group 00 and serial
0000; credit cards of 13 to 19 digits passing the Luhn checksum (otherwise every order number is "a card"); US phone
formats; IPv4 octets of 0–255. Replace each value with a consistent numbered token per type, so the same address is
always `[EMAIL_1]` and the model can still reason about who did what. Keep the mapping inside the network and
`restore` the originals before the user sees the answer. Limits: regex is a floor; names, addresses and free text
need named-entity recognition, which also misses things. Measure and report recall on a labeled sample of real data;
a documented recall beats a claim of completeness. That recall plus a review of sampled logs is the evidence for the
sensitive-data release gate. (Section 13.2, Section 13.6; ex53)

*Strong signals:* consistent, reversible tokens, mapping kept local; recall measured on labeled data. *Red flags:*
masking everything as `[EMAIL]`; claiming a regex catches all personal data.

### 13.3 · Coding

**Q.** Your backend receives an OIDC ID token from the customer's identity provider. Walk me through the checks your validation function performs, in order, and what changes when you move from a test setup to Entra ID or Okta.

In order: structure (three base64url segments); algorithm, compared with exactly the expected value, rejecting `none`
explicitly; signature, checked against a key the service already holds and compared in constant time
(`hmac.compare_digest`); issuer (`iss`) is the customer's identity provider; audience (`aud`, a string or a list)
includes your application, because another application's valid token isn't valid for yours; expiry (`exp`) and
not-before (`nbf`) against the current time; then the ID-token checks: a `typ` of `at+jwt` (an access token) is
rejected, `azp` must be your client id when present or when `aud` has several values, and `nonce` must match the one
your sign-in request sent. Nothing in the token is trusted until the signature verifies, and the header's `alg` is
compared, never used to choose how to verify. The ID token only starts your session; APIs take access tokens issued
for their own audience and check scope and `typ: at+jwt`, never an ID token. ex89 is a teaching implementation: HS256
with a shared secret keeps the tests self-contained. Production providers sign with RS256 or ES256 and publish public keys at a JWKS endpoint: select the
key by the token's `kid`, cache the key set, and use a well-maintained library with an explicit algorithm allowlist.
User id, email and groups for authorization come only from the verified claims. (Section 13.3; ex89)

*Strong signals:* audience as well as signature; the `alg: none` attack and why `alg` is compared, not obeyed; ID
token versus access token.
*Red flags:* reading claims before verifying; hand-rolled RS256 in production.

### 13.4 · Technical

**Q.** A bank's security architecture review asks for role inheritance, strict tenant isolation, refund approval limits and a tamper-evident audit log. How would you build the access check and the log, and what doesn't the log protect against?

Roles carry permissions and may inherit others (`supervisor` inherits `agent`); compute the set transitively,
guarding against cycles. Permissions match exactly, by wildcard (`ticket:*`, `*`) or with a limit
(`refund:approve<=500`), which matches only if the resource's amount is within it. Check tenant isolation before any
permission: a user from another tenant is denied even with `*`, because isolation is a boundary, not a grantable
permission. Append every decision to the audit log with user, action, tenant, outcome and reason. Each entry stores
the previous entry's hash and its own SHA-256 over its content plus that hash; `verify()` recomputes the chain, so
editing or deleting any entry breaks every later hash. It doesn't stop an attacker with write access rebuilding the
whole chain, so in production ship entries to write-once storage or an external log service, or periodically anchor
the latest hash where the application can't write. (Section 13.3; ex56)

*Strong signals:* the tenant check first and immune to `*`; the chain proves after-the-fact edits only. *Red flags:*
tenancy as a permission; calling a hash chain "tamper-proof".

### 13.5 · System design

**Q.** Your copilot indexes the customer's whole SharePoint and Confluence estate, and a claims adjuster just got a colleague's HR disciplinary document as the top result. How would you redesign retrieval and the downstream calls?

Nothing was hacked; retrieval ignored permissions. Copy each document's ACL onto every chunk at ingestion. Build the
principal (user id, email, groups) from the verified ID token, never from client or model input. Apply the ACL with
an explicit deny group winning, then allow by name, shared group or `everyone`. Filter candidates *before* ranking:
ranking first leaks through result counts, generated snippets and relevance scores, and filtering a top 20 can leave
almost nothing when permitted chunks existed lower down. Titles, snippets and citations are disclosures too; record
how many candidates were considered, permitted and denied. Ask how often ACLs synchronize, since a document tightened
yesterday mustn't be visible today. For downstream APIs, use OAuth 2.0 token exchange (RFC 8693; Entra ID's
"on-behalf-of") for a token scoped to that API and user, not a god-mode service account or the user's token passed
straight through. (Sections 13.3 and 13.5; ex89)

*Strong signals:* filter before ranking, with the reasons; ACL freshness; acting on behalf of the user. *Red flags:*
post-filtering the top-k; a service account that can read every claim.

### 13.6 · Debugging

**Q.** An email-triage agent forwarded invoices to an outside address, although the design had an egress allowlist and confirmation for side effects in tainted contexts. The audit log shows `send_email` as tainted and "confirmed". What would you check first?

If both controls existed, check the configuration that ran in production, not the design. A tainted call that was
"confirmed" points at the confirmation function: a staging stub that always returns true? An outside address that
passed egress points at the allowlist: a wildcard such as `*.com` added for a test? Where did the red-team suite run?
Only against staging means it never tested what shipped. Respond first: kill `send_email` with its switch, revoke and
rotate affected credentials, preserve transcripts, tool calls and authorization decisions, and notify the customer on
the contract's clock. Prevent: lint configuration for wildcard allowlist entries, forbid confirmation stubs outside
test builds, run the injection release gate against the production configuration before every release, and add the
attack to the red-team suite before closing the incident. (Section 13.6; ex54, ex93)

*Strong signals:* the shipped configuration and audit evidence before blaming the model; contain, then fix with a
test. *Red flags:* "the model was tricked, so improve the prompt".

### 13.7 · Customer scenario

**Q.** Two days before go-live, the golden set passes at 96% but a negative test finds one cross-tenant leak. The sponsor asks you to ship now and fix it next sprint. What do you say, and who can decide?

The system isn't 96% ready; it's not ready. Security gates aren't scores to average: a failed gate blocks release
whatever else passes, and tenant isolation can never be waived. Where a gate allows a waiver, only the customer's named
risk owner, often the CISO, can accept the residual risk, in writing, naming the gap, the compensating control and an
expiry date, recorded in the RAID log; nobody on the delivery team, you included, waives a gate for the customer. The
path forward: fix the leak, re-run the tenant-isolation negative test through every ingestion and query path and
every cache against the shipping configuration, and bring the report as evidence. The production-readiness scorecard
applies the same rule: gates first; no weighted score compensates. (Section 13.6; Table 13.2)

*Strong signals:* a calm, firm refusal with a concrete route to green; who owns a waiver and which gates allow none.
*Red flags:* shipping with a follow-up ticket; averaging security into a readiness score.

## Chapter 14 · LLMOps and SRE

### 14.1 · Debugging

**Q.** During a short database outage, every pod of your copilot went into a restart loop. What would you check first, and how would you change the deployment so it doesn't happen again?

Check the probes. A failing liveness probe restarts the container; a failing readiness probe removes it from the
load balancer. If liveness checks the database, a database outage fails liveness on every pod and Kubernetes restarts
them all in a loop, though the processes were fine. Point liveness at a cheap "process is alive" endpoint and
readiness at "dependencies are reachable", so pods drop out of rotation during the outage and return with the
database. Encode the platform's admission policy as a linter and run it before submitting: at least two
replicas, requests and limits for every container, both probes, pinned images, secrets via `secretKeyRef`,
`runAsNonRoot`, a read-only root filesystem, a Service selector matching the pod labels, and an autoscaler with at
least two minimum replicas. (Section 14.1; ex58)

*Strong signals:* what each probe's failure does; "alive" separate from "ready". *Red flags:* removing probes or
lengthening timeouts without understanding the cause.

### 14.2 · Technical

**Q.** An adjuster asks "why was that answer slow?", and nobody can tell whether retrieval, the model or a tool call was responsible. How would you instrument the service so you can answer next time?

Trace every request as a tree of timed spans with attributes: a root `request` span and child spans for retrieval,
reranking, tool calls and the model call, sharing the root's trace id and recording their parent. `contextvars` makes
nesting work across threads and async tasks; a span that raises records `status = "error"` and the exception type
before re-raising. The model client's span carries the model, input and output tokens and cost. From the spans,
compute a per-model summary (call count, p50 and p95 latency, tokens, cost) for finance and the platform team, and
the critical path: from the root, follow the longest child repeatedly, giving something like "request →
generate → llm.complete". In production, use the OpenTelemetry SDK, the customer's tracing backend and
OpenTelemetry's generative-AI semantic conventions so their dashboards read your traces. The same stage spans measure
each line of the latency budget. (Section 14.2; ex60)

*Strong signals:* critical path from spans; token and cost attributes on the model span; standard conventions.
*Red flags:* "add timing logs" with no request correlation.

### 14.3 · Technical

**Q.** The customer's SRE team won't take your copilot into their on-call rotation with "alert when the error rate exceeds 1%". Walk me through the SLO and the alerting you'd propose instead.

Good means no server error, within the journey's latency threshold (for streamed answers, first token within
3,000 ms, as in ex61); the SLI is good over total in a window. A 99.5% objective over 30 days gives an error budget of 0.5% of requests. Burn rate is (1 − SLI) ÷ budget:
1 spends exactly the budget over 30 days; 14.4 sustained for an hour spends 2% of it. Two windows per alert: page at
14.4 or more over both the last hour and the last five minutes; ticket at 6 or more over both six hours and 30
minutes (adapted from the SRE Workbook, which pages at 6 and tickets at 1 over three days). The long window shows significance, the short one that it's still happening, so the alert resets quickly
after a fix. A fixed 1% threshold can't tell a two-minute blip from a slow leak that drains the month without
crossing it. Remaining budget drives release decisions. For an AI service, decide whether refusals, failed parses or
low judge scores count; many teams keep separate quality SLOs. (Section 14.2; ex61)

*Strong signals:* the formula and two-window logic; budget linked to release priority. *Red flags:* a single
threshold alert; every quality signal folded into availability.

### 14.4 · System design

**Q.** Go-live is Monday with 400 adjusters, and the sponsor asks "will it hold?" Walk me through how you'd answer, from the capacity arithmetic to the performance test plan.

Little's Law, L = λ × W: at a peak of 2 requests a second and 6 seconds each, about 12 are in flight; two replicas
with ten workers give 20 slots, a maximum of 20 ÷ 6 ≈ 3.3 a second. At 12 seconds' latency, 24 are in flight: over
capacity. The plan: a workload model (journey mix, token counts from pilot logs, open arrivals, bursts to 4 a
second); at twice the peak that's roughly two million input tokens a minute, so a tokens-per-minute quota may bind
first, and 24 in flight already needs a third replica. Targets separating first token (p95 2.0 s) from full response
(8 s / 12 s, 15 s for JSON claim summaries). A per-stage latency budget. A test matrix: baseline, peak, stress,
spike, soak, cold cache, prompt growth, model change, rate limits, degraded dependency, retry amplification, with
real-model runs budgeted. Use an open-model generator (avoiding coordinated omission), count errors' latency, check
quality under load, and label every number by status. (Section 14.3; ex62)

*Strong signals:* numbers, including a bad-day scenario; tokens per minute as a limit; open versus closed load.
*Red flags:* one latency number; percentiles from a closed-loop generator.

### 14.5 · Technical

**Q.** A defense customer's network has no internet access, and everything arrives on approved media. How would you deliver your service, and how would their security officer verify what arrived?

Ship a bundle the security officer can verify independently: a manifest listing every file with its SHA-256 and
size, plus the version, and a signature over the manifest's canonical JSON (sorted keys, no whitespace). ex64 uses an
HMAC with a shared key; production uses an asymmetric signature, such as GPG or Sigstore tooling, so the verifier
never needs the signing key. Verification reports a bad signature, a missing manifest, missing or unexpected files,
checksum mismatches and unsafe paths: absolute paths, `..` components, symbolic links and hard links. Extraction
verifies first and extracts nothing if a single problem is found, because a member named `../../etc/cron.d/job`
writes outside the target when extracted naively. Python 3.12's `tarfile` filters help, but verifying first is still
the right design. Pin images by digest where required, and send a preflight script ahead so their IT team finds
environment problems before you arrive. (Section 14.4; ex64, ex63)

*Strong signals:* verify-then-extract, all or nothing; asymmetric signing in production. *Red flags:* extracting,
then checking; trusting the transfer medium.

### 14.6 · System design

**Q.** You want to move the copilot to a new prompt and a new model version. Walk me through the release path, and tell me what would make you roll back.

Prompts, model identifiers and retrieval parameters are versioned files reviewed like code, and every response logs
the versions that produced it. Shadow first: a bounded share of live traffic for a bounded period, answers hidden,
comparing latency, cost, refusal rate and judge scores on a sample. Then a canary: a small percentage of users,
compared with the current version over the same window, after a minimum number of requests (500 in the book's
example), since a judge rate over forty conversations is noise. Roll back if the error rate exceeds 1.5 times the
base plus 0.1 points, p95 exceeds the base by 20%, the judge pass rate falls more than 3 points or the refusal rate
rises more than 2; otherwise promote. Agree thresholds with the SRE team and put them in the runbook. Prompt or model
rollback is a configuration change, effective in minutes without a build, rehearsed by the customer's operations
team. (Section 14.6)

*Strong signals:* a quality signal and over-refusal in the canary; a minimum sample. *Red flags:* error-rate-only
canaries; prompts edited in a console.

### 14.7 · Customer scenario

**Q.** At 02:14 on Saturday the customer's gateway started returning 502s on the copilot. By the time you join the bridge it has recovered, and three teams are blaming each other. What do you do that night and on Monday?

End the blame with evidence: JSON logs from the gateway, API, retriever and vector database, plus the dependency map.
Parse them, counting malformed lines rather than crashing, and find each service's first error. The suspect is the
service whose dependencies, transitively, had no errors before its own first error (the earliest if several
qualify); a gateway that failed after the API is a victim. List the blast radius by first error and build timelines
for sample request ids. It's the first hypothesis; the cause could sit outside these logs (a network change, a
certificate expiry, a noisy neighbor). Customer updates follow fixed stages (investigating, identified, monitoring,
resolved), in plain language about user impact, with the next update time and no pod names, internal service names,
IP or email addresses. Monday: a blameless postmortem with summary (duration, time to mitigate, peak affected
users), timeline, root cause, contributing factors, what went well, and action items with owners and due dates.
(Section 14.5; ex66, ex94)

*Strong signals:* timestamps plus dependencies separate cause from victim; what the system allowed, not who erred.
*Red flags:* a person or team as the cause; action items with no owner.

### 14.8 · Customer scenario

**Q.** The sponsor asks "is it ready?" The weighted readiness score is 2.95, and the customer's operations team hasn't yet rehearsed a rollback. What do you tell them?

"Not yet", for two reasons, in order. Gates come first, and rollback of code, prompt and model rehearsed by the
customer's operations team is a gate; a failed gate means not ready, whatever the score, so schedule that rehearsal.
Second, the weighted score must reach 3.0 with no dimension below 2, so 2.95 misses. Make the gap specific: find the
dimension with the weakest evidence and say what would lift it. In the book's Northwind review, replacing the
estimated cost per task with the one measured in the performance test lifts economics from 2 to 3 and the total to
3.05. A dimension still at 2, such as adoption there, can be a condition of go-live rather than a blocker. The
weights were agreed with the sponsor, and the score is for coaching and conversation; the gates decide. After go-live
approval, hold the operational readiness review and finish with your access revoked. (Section 14.7)

*Strong signals:* gates before score; "not yet" as named actions with evidence. *Red flags:* rounding 2.95 up; the
rehearsal as a nice-to-have.

## Chapter 15 · Field Engineering and Productization

### 15.1 · Technical

**Q.** Globex wants the SLA report you wrote on site at Acme, full of Acme's priority names, SLA hours and contacts. How would you turn it into something Globex can use without changing a line of Acme's output?

Copying and editing the constants is consulting, and the third customer pays for it again. Keep
`legacy_acme_report` untouched as the reference and write a golden-output (characterization) test asserting that the
new `build_report` configured for Acme produces exactly the same output; that test lets you refactor aggressively.
Extract every customer-specific value into a `ReportConfig`: customer name, SLA hours per priority, priority aliases
("P1" and "Sev1" for Acme, perhaps "Sev-A" for Globex), UTC offset and escalation contact. Validate it: every
canonical priority an alias maps to needs an SLA, and SLAs must be positive. Add a test that fails if the library
source names any customer, so a hard-coded fallback can never show "Acme" to a Globex user. Globex becomes a
configuration, not a copy. Several copied adapters already? Replace them with one configuration-driven engine that
validates mappings at load and collects per-record errors. (Section 15.1; ex67, ex73)

*Strong signals:* behavior pinned before changing it; validated configuration; no customer names in library code.
*Red flags:* refactoring the legacy function in place; "I'd fork it for Globex".

### 15.2 · Customer scenario

**Q.** An accounts-payable manager asks "Can AI read our vendor invoices?" and gives you until lunch. Walk me through what you'd build and what your readout would say.

A feasibility question deserving a fast, honest answer, not a production build. Deterministic rules where they
work: invoice numbers, dates in several formats with the customer's day-first convention explicit, totals after
"Total", "Amount Due" or "Balance Due" but not "Subtotal", and the vendor as the first line. Call the model only for
fields the rules missed, as JSON, merged without ever overriding a rule value, and record each field's source (`rule`
or `llm`), keeping the POC cheap and explainable. Evaluate on hand-labeled invoices: accuracy per field, overall, and
how many fields the model filled; one overall number hides the field that matters most. The readout lists every field
below 90% as a next step, states the conditions behind each number (sample count, how chosen), and ends with "Run on
200 labeled invoices before any production decision." A POC on 15 samples proves feasibility, not accuracy.
(Section 15.2; ex70)

*Strong signals:* rules first, model for gaps, provenance per field; explicit limits of the evidence. *Red flags:*
one headline accuracy; an over-engineered POC.

### 15.3 · Customer scenario

**Q.** A health system wants intake notes summarized for research dashboards, and their privacy officer asks what happens to patient data. How would you answer, and where does your responsibility end?

A pipeline the privacy officer can verify. De-identify each record: drop direct identifiers (name, medical record
number, phone, email); reduce dates of birth and visit dates to the year; group ages of 90 or over as "90+" and
remove their birth year; cut ZIP codes to three digits, 000 for small-population areas. Scrub free text by tokenizing MRNs, emails, dates and phone
numbers first, then each part of the patient's name as a whole word, case-insensitively. Purge records past
retention unless under legal hold, which always wins. Log every access with who, an allowed purpose and the record
count, never contents: a log that copies patient data is itself a store of it. The boundary: this is modeled on HIPAA
Safe Harbor's 18 identifier categories, and free text is hard to de-identify completely. Real programs use the full
list, specialized tools, expert determination where appropriate, and privacy and legal sign-off. You build it so
they can verify it; you aren't the final authority. (Section 15.3; ex72)

*Strong signals:* legal holds over retention; access logs without contents; the final call left to privacy and
legal. *Red flags:* "we strip names, so it's de-identified".

### 15.4 · Debugging

**Q.** A customer fine-tuned a smaller model on their best support replies. The validation score was excellent, but the model disappoints in use. What would you look at, and what would you have done differently?

Suspect leakage: near-identical conversations on both sides of the train/validation split give an excellent
validation score and a disappointing model. Support data is full of templated replies, so check that de-duplication
happened before the split, on normalized content (lower-case, digits replaced with 0, whitespace collapsed), which
treats "Your order 4471 has shipped" and "Your order 8812 has shipped" as one example. Rebuild the pipeline: resolved,
high-satisfaction conversations with at least one agent turn; chat format with merged consecutive turns, ending on an
assistant message; emails and phone numbers redacted; de-duplicated; split by intent, stratified and seeded, so every
intent reaches validation; filtered to the service's token limit. Revisit the decision too: fine-tuning suits style,
format and narrow stable tasks, not changing facts, which retrieval handles. Compare with the best
prompt-and-retrieval system on the same golden set, including the operational cost of a model to version, evaluate
and retrain. (Section 15.4; ex71)

*Strong signals:* normalized de-duplication before splitting; questions whether fine-tuning was right. *Red flags:*
"train longer" or "add more data" without checking the split.

### 15.5 · Behavioral

**Q.** Tell me about a time you reviewed code you didn't write, from a colleague or a coding agent, that ran fine but was wrong.

Use situation, action, result. Situation: what the code did and why it looked acceptable (it ran, it was fluent).
The action shows a method: you read it as if a capable stranger wrote it; checked boundaries first (SQL, file paths,
shell commands, credentials, network calls, deserialization); ran the tests, then read them for tests that test
nothing or were weakened; hunted silent failure (broad exception handlers, defaults that hide errors, unbounded
retries); and asked for the reasoning behind suspicious choices. Name defects like ex87's: SQL built with an
f-string, an unchecked output path, an off-by-one that skips the last page, a bearer token in the logs. Close the
loop: a precise review, one categorized finding per bullet, and for agent code "never do" rules in the instruction
file so the next run doesn't repeat them. Result: what was fixed and what changed afterward. You own the code you
approve. (Section 15.5; ex87)

*Strong signals:* a review method, not luck; findings turned into prevention. *Red flags:* "it passed the tests, so I
approved it"; blaming the tool or the author.

### 15.6 · Customer scenario

**Q.** The customer's security lead asks why they should let you use a coding agent on their repository. What do you agree with them before you start?

Don't argue for the tool; agree four rules in writing before you start. Which tools are approved: enterprises often
allow only specific assistants under their own agreements, and an unapproved tool can breach the engagement contract
however good it is. What the agent can see: secrets in the secret manager, not the repository; synthetic fixtures;
directories holding customer data excluded from its context. What it can do: least privilege, no production
credentials, no pushing to protected branches, approval before shell commands that change anything outside the
working tree. What gets recorded: transcripts can contain code, data and decisions, so agree storage and retention as
for any log. Put the rules in the project's instruction file, where the agent reads them: commands to run, paths
never to touch, checks to pass before finishing. And you review agent output as rigorously as any code.
(Section 15.5)

*Strong signals:* the four agreements; the instruction file as enforcement. *Red flags:* a personal or unapproved
tool because it's better; production credentials for the agent.

### 15.7 · Behavioral

**Q.** Tell me about a time you had to decide whether something built for one customer should become part of the product.

Use situation, decision, result, and show the reasoning. Situation: the code, the customers who needed it, and its
upkeep cost. The decision uses three outcomes: it stays field code (one customer, likely to change, low risk if it
breaks), becomes configuration of an existing feature (several customers, same behavior, different parameters) or
becomes a product feature (several customers, a stable need, real cost when missing). The third-customer rule: build
the first for the customer, generalize the second carefully, and by the third it's product or configuration. Show the
discipline: a field-code register per customer with an owner and a review date, so "temporary" scripts don't become
permanent obligations. Show the hand-over: the customers, the configuration that varied, the golden-output tests and
the incidents the field code caused; a request with tests and data gets built, an anecdote gets a ticket. Name the
risk: a fix reaching only one of several copies. (Section 15.6; ex67, ex73)

*Strong signals:* an evidence-based hand-off to product; field code is cheap to write and expensive to keep.
*Red flags:* productizing everything; copies with no owner.

## Chapter 16 · Delivery Leadership

### 16.1 · Technical

**Q.** Meridian Bank's security team won't approve a new data store, so retrieval will run on the bank's Postgres with pgvector. Walk me through the decision record you'd write, and what makes it useful after you leave.

An architecture decision record: short, numbered, never edited after acceptance (a later decision supersedes it with
a new ADR). Context: the constraint and the scale; security won't approve a new store before go-live, and retrieval
needs about 2M chunks. Decision: the bank's managed Postgres with pgvector and an HNSW index, with a named decider
(the Head of Platform Engineering). At least two alternatives: a managed vector database (faster to start, but an
8–12 week vendor assessment) and an already-approved search engine the team can't operate. Consequences: benefits
(data stays where it lives, existing backups and access controls) and at least one downside: index builds load the
shared cluster, and you accept pgvector lock-in. A "Revisit when" section with measurable triggers, such as the
corpus passing 20 million chunks or p95 retrieval latency exceeding 300 ms, lets the customer's team monitor the
decision after you've gone (Section 16.1; ex90).

*Strong signals:* insists on a named downside, because it shows what was knowingly given up and that the decider
accepted it; numeric revisit triggers. *Red flags:* only benefits, which reads as advocacy; no alternatives, so it
wasn't really a decision.

### 16.2 · System design

**Q.** An SI partner is building two of your five workstreams. How would you design the review and acceptance process for their designs and deliverables, and what would a rejection look like on paper?

Start before the work: put the quality bar in the partner's statement of work (design checklist, golden set and pass
threshold, security requirements and the gate), share the evaluation harness and CI gate from week one, and review
early and small: designs before code, a thin end-to-end slice before the full build. The design checklist has three
severities: blockers (authentication, data flow, PII handling, rollback, or PII "sent to model" without redaction)
must be fixed; majors (evaluation plan, observability, threat model) make acceptance conditional; minors (cost
estimate, SLO) are tracked. The deliverable gate decides on evidence, not assurances: reject if any blocker or open
critical defect remains; conditional if majors remain, any test fails or the evaluation pass rate is below 90%;
otherwise accept. Every triggered condition is a listed reason, such as "Conditional: 2 major findings (evaluation
plan, threat model); test pass rate 97% (184/190)" (Sections 16.1 and 16.4; ex90).

*Strong signals:* criteria in the contract before work starts; the test report, evaluation run and security sign-off,
not slides; reasons a partner can act on. *Red flags:* accepting on assurance; new criteria at acceptance, which
turns review into a dispute.

### 16.3 · Technical

**Q.** Three weeks into a six-week engagement, tasks are partly done and the steering committee asks if you'll land on time. How would you produce the forecast, and how do you decide which workstreams are slipping?

Report the forecast, not the baseline. With the Chapter 2 plan as baseline, re-plan the remaining work: each task's
remaining duration is its expected duration times the share not done. Schedule it from today with the critical path
method; forecast finish minus baseline finish is the slip (say, baseline day 42.0, forecast day 49.5, slip 7.5 days).
Per workstream, compute an earned-value-style schedule variance: reported progress minus the progress the baseline
planned for today, weighted by expected effort. More than 10% behind is amber, more than 25% red, and a workstream
whose critical-path task is more than 10% behind is at least amber, because it moves the whole date. Two cautions: a
workstream off the critical path still blocks go-live if its deliverable fails the quality gate, and "80% done" is an
estimate, so measure progress by acceptance criteria met where you can (Section 16.2; Capstone 6).

*Strong signals:* baseline separate from forecast; why the critical path gets a tighter threshold; schedule and
quality as different signals. *Red flags:* averaging owners' percent-complete figures; the original date because
nothing is "officially" late.

### 16.4 · Customer scenario

**Q.** On Friday the steering committee wants to know if you can go live. The forecast has slipped 7.5 days, one partner deliverable is conditional, one is rejected and activation is 50%. How do you run the meeting?

The go-live call comes from thresholds agreed with the sponsor in advance, not from feel. Blockers: a rejected partner
deliverable, open security questionnaire items needing human answers, or a forecast slip over ten days. Conditions: a
conditionally accepted deliverable, activation below 60%, or weak measured impact. The rejected deliverable is a
blocker, so it's *no go* as things stand; the 7.5-day slip is under the ten-day line, and the conditional deliverable
and 50% activation are conditions. Send the update a day early, in the fixed order: the decision needed today (say,
extend the rejected workstream or descope it to phase 2), a computed one-line status, what changed, value so far,
risks and asks with owners and dates from the RAID log, the next milestone. Spend the meeting on the decision, offer
options with costs, record the outcome. Fix activation before impact, team by team, with an owner (Sections 16.2 and
16.3; Capstone 6).

*Strong signals:* "why no go" as facts the committee agreed would block; the decision before the status.
*Red flags:* a status tour with no decision; thresholds invented in the room.

### 16.5 · Customer scenario

**Q.** A senior customer executive emails your VP saying the engagement is behind and nobody told them. What do you do in the next day, and afterward?

Fast and factual. Acknowledge the concern the same day, without arguing. Before replying in substance, gather facts
from the RAID log, the status history and the evidence, and brief your manager and the account executive before
they're asked. Reply with what happened, what you're changing and when the executive will see the difference, copying
everyone copied on the escalation. "Nobody told them" makes it a surprise problem; most escalations are about
surprise, not substance. Record the trigger in the RAID log so the same gap can't cause a second one, and fix the
communication path: material forecast changes go to the sponsor the same day, in person or by phone, then in
writing. Watch the leading indicators (decision latency, sponsor attendance, days blocked on access), which often show
trouble before the status color does (Section 16.5).

*Strong signals:* same-day acknowledgment, then a fact-based reply; own side briefed first; the cause fixed, not
just the email. *Red flags:* a defensive point-by-point rebuttal; replying from memory.

### 16.6 · Behavioral

**Q.** Tell me about a time you had to tell a sponsor that a date was going to slip.

Use STAR (situation, task, action, result) with what *you* did and a measured result, in the chapter's shape for bad
news. Timing: the sponsor heard it from you, the same day the forecast moved, in person or by phone and then in
writing, not first in a steering meeting. Content: what happened in one sentence with a number; the impact on outcome
and date; two or three options with costs; your recommendation and why; what you needed from them and by when. Show
that you escalated inside your company first (manager, account executive), and re-planned formally once the decision
was made: a new baseline, a RAID log entry, a change request if scope changed. Close with which option was chosen,
what date was met, and what it did for trust (Section 16.5).

*Strong signals:* options with costs and a clear recommendation; a decision deadline; a formal re-plan. *Red flags:*
"the UI is late" with no options; the sponsor hearing it from someone else.

### 16.7 · Behavioral

**Q.** Tell me about a time you were accountable for work done by people who didn't report to you, such as a partner or another team. How did you hold the quality bar?

Use STAR, showing that you led through review, not by writing the code. You understood the other party's incentives
(hourly and fixed-deliverable partners are rewarded differently from the customer's outcome); the quality bar was
agreed up front, ideally in the statement of work, so it was a shared standard, not a dispute; you shared the evidence
infrastructure (evaluation harness, golden set, CI gate) so they saw their own regressions early; the RACI named one
accountable person across the company boundary and who decided disagreements; you reviewed early and small. The
action includes a gate decision on evidence with explicit reasons. The result is measured, such as findings closed
before acceptance or a deliverable accepted on time, plus measured knowledge transfer to the customer's team
(Sections 16.1 and 16.4).

*Strong signals:* evidence-based acceptance with reasons; criteria set before work started; the partner's exit
planned. *Red flags:* "we" did everything; rewriting the partner's work instead of gating it.

## Chapter 17 · FDE Careers

### 17.1 · System design

**Q.** An insurer wants a copilot that answers 400 adjusters' coverage questions from 80-page policy PDFs, with citations. You have 45 minutes. Walk me through how you'd spend them.

Follow the operating loop and spend the time where deployments fail. Discover (about 5 minutes): the users, what
success means and how it's measured today, how many policy forms and versions, permissions, what can't leave the
network, who signs off on launch. State numeric assumptions (about 2 minutes) and invite correction: say 600 policy
forms, 40,000 questions a month, answers within five seconds, a $40,000 monthly model budget, citations and refusals
required. Design (about 15 minutes): heading-based chunking with heading path, version and effective dates; hybrid
retrieval with permission filters; abstention when retrieval is weak; validated citations; output guardrails; a BFF
that holds the key and streams; the customer's Postgres and identity provider reused. Evaluate (about 8), operate
(about 5) and adopt (about 5). Go deep wherever the interviewer pushes (Sections 17.2 and 17.3).

*Strong signals:* questions before drawing; numbers as stated assumptions; real time on evaluation, operations and
adoption. *Red flags:* a vector database in the first two minutes; twenty minutes on embedding models.

### 17.2 · System design

**Q.** Same copilot: the interviewer says "Fine, but how will you know it works, before launch and after it's live?" What do you say?

Before launch: a golden set of about 150 questions built with senior adjusters, with an unanswerable slice to test
abstention; recall@4 for retrieval; citation precision and abstention accuracy for answers; a case-by-case regression
gate in CI so a change can't silently break passing cases. Then a pilot with a control group and a decision rule
agreed with the sponsor in advance. After launch: tracing, an availability SLO and a quality monitor; canary releases
with a quality check; kill switches. Measure value too: the activation funnel by team, a measured readout at six
weeks, the business case re-run with measured numbers. Tie it to discovery's success metrics (fewer wrong coverage
answers, shorter handle time) (Section 17.3).

*Strong signals:* separate retrieval and answer metrics; an unanswerable slice; a decision rule agreed before the
data. *Red flags:* "users will give thumbs up" as the only measure; evaluating once.

### 17.3 · Customer scenario

**Q.** I'm the chief operating officer: "We need AI that makes support faster and better, soon." How do you respond?

This tests turning vagueness into a plan without agreeing to everything or getting defensive. Don't pitch a solution.
Acknowledge the goal, then make "faster", "better" and "soon" measurable: which support team and channel, what's
measured today (handle time, resolution, quality scores) and its baseline, what "soon" means and what drives it,
what data and systems exist, who must sign off. Where answers aren't available, state dated assumptions and how you'll
confirm them. Close with a concrete next step: a short discovery, a charter with a success metric, scope and an
out-of-scope list, and a date for a first decision. Hold scope politely if pushed to promise everything at once
(Section 17.2; ex06).

*Strong signals:* adjectives turned into metrics with baselines; dated assumptions; a proposed next step.
*Red flags:* agreeing to "faster and better" with a date and no definition; jumping to a demo.

### 17.4 · Customer scenario

**Q.** A logistics company wants to use AI to reduce delivery exceptions. You have six weeks and two engineers. What do you do?

The decomposition or case round, testing Chapters 2 and 16. Metric first: how exceptions are counted today, the
baseline rate and which types cost most. Cut scope to one exception type or one part of the flow that two engineers
can deliver and measure in six weeks, with an explicit out-of-scope list. Estimate in ranges, sequence the work so a
thin end-to-end slice exists early, and test the riskiest assumption first (say, that the data to predict or explain
exceptions exists and is accessible). Build in measurement: how you'll know at week six whether exceptions fell,
ideally against a comparison group, and what decision follows (Section 17.2).

*Strong signals:* metric and baseline before solution; ranges; riskiest assumption first; an out-of-scope list.
*Red flags:* no measurement and no out-of-scope list; promising every exception type.

### 17.5 · Behavioral

**Q.** Tell me about a time you owned an outcome beyond your job description.

STAR (situation, task, action, result), in about two minutes. The situation makes clear what was outside your role
and why it mattered to the customer's outcome. The action is what *you* did, first person, with the judgment calls
visible: what you took on, what you said no to, and who you told. The result is measured (a metric moved, a date
held, an incident avoided) with the number. Anonymize real customer work and stay within your confidentiality
obligations. Keep this as one of six to eight stories covering ownership, cutting scope, bad news, disagreement,
failure and productization (Section 17.2).

*Strong signals:* a clear "I"; a measured result; a judgment call to probe. *Red flags:* "we" did everything; ending
with effort, not a result.

### 17.6 · Behavioral

**Q.** Can you show us the readout from your last customer engagement? It would help us judge your work.

Decline politely and offer something better. Engagement artifacts belong to the customer and usually fall under a
confidentiality agreement, so real readouts, screenshots, logs, data (even redacted) and figures can't be shown.
Offer a capstone or other synthetic engagement published with its code: a two-page design record with ADRs,
evaluation results with an honest account of failures, a one-page executive readout and its scorecard, every number
labeled measured, assumed or projected. Offer to describe the real engagement as an anonymized story; handling this
well is itself evidence of judgment (Section 17.4).

*Strong signals:* refuses without fuss, redirects to capstone evidence; knows what a good readout contains.
*Red flags:* sharing customer material "just this once"; claiming redaction makes it safe.

### 17.7 · Behavioral

**Q.** Suppose you join us next month as an FDE. What would your first 90 days look like?

Learn, then own a workstream, then an engagement. Days 1–30: shadow at least two engagements, including a discovery
session and a steering meeting; learn the platform well enough to debug it, not just demo it; ship one fix or small
improvement to a customer deployment; write one product brief from the field. Days 31–60: own a workstream as the
responsible person in the RACI; run a discovery session and write the charter; set up an evaluation suite if the
engagement lacks one. Days 61–90: own an engagement end to end with a sponsor, charter, plan and measured outcome;
contribute one reusable component to the product; teach something, such as a customer workshop or an internal
session (Section 17.5; ex68, ex01, ex84).

*Strong signals:* resists proving yourself with week-one features; ends with ownership and a measured outcome.
*Red flags:* "I'll start coding on day one"; no learning phase and no teaching.
