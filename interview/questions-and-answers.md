# FDE interview questions and answers

127 questions in the style of Forward Deployed Engineer interview loops, seven or eight per chapter of *The Forward
Deployed Engineer*, each with a model answer, the signals of a strong answer and the common red flags. The book
prints the questions at the end of each chapter and the answers in Appendix J.

**How to use them.** Answer each question aloud before reading the model answer, then check yourself against its
*Strong signals* and *Red flags*. For a mock loop, pick one question of each type (technical, coding, debugging,
system design, customer scenario, behavioural) from different chapters. Section numbers refer to the book; exercise
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
- [Chapter 15 · Field Engineering and Productisation](#chapter-15--field-engineering-and-productisation) (7 questions)
- [Chapter 16 · Delivery Leadership](#chapter-16--delivery-leadership) (7 questions)
- [Chapter 17 · FDE Careers](#chapter-17--fde-careers) (7 questions)

## Chapter 1 · The Forward Deployed Engineer

### 1.1 · Behavioural

**Q.** Tell me about a time you had to start building before the requirements were clear. How did you avoid both waiting and guessing?

Structure the story as situation, action, result. The situation: a piece of work where a question that mattered
(who the users were, what success meant) had no answer yet, and waiting would have cost real time. The action is the
core of the answer: you listed the open questions, paired each with an explicit working assumption and a deadline,
and started work against the assumptions the same day. The chapter's model sentence is "Unless you tell me otherwise
by Thursday, I'll assume adjusters, not policyholders, are the users." The result should show that the assumption
either held, and you'd made progress meanwhile, or that stating it surfaced a disagreement early, while it was still
cheap to change course. Close with what you'd keep doing: writing assumptions down with a date, so silence becomes
recorded agreement (Section 1.4; ex06).

*Strong signals:* the assumption was written and dated, not held in your head; disagreement surfaced early because
of it; the candidate links this to bias to action rather than recklessness. *Red flags:* "I waited until the
requirements were signed off"; building on assumptions nobody else ever saw.

### 1.2 · Customer scenario

**Q.** Three weeks after launch, your Tailspin Logistics assistant scores 94% on its evaluation set, but only 18% of invited dispatchers have opened it once. What do you do in the next two weeks?

A strong answer starts by noting that the model isn't the problem: 94% on the evaluation set and 18% activation
means an adoption failure, the "Adopt" step of the operating loop. First, gather evidence: usage logs by team (in the
chapter's case most questions came from the IT team that hosted the pilot), then sit beside the dispatchers for an
afternoon or two and watch them work. That reveals the real cause: they live in the dispatch console all day and the
assistant sits in a separate tab behind a second login. Then fix the root causes the chapter names: find a sponsor in
operations (the head of dispatch), move the assistant into a panel inside the console using the existing session,
and instrument activation by team and report it weekly. Finally, say what you'd do next time: in week one, a named
sponsor, an afternoon with five real users and activation instrumented before the first demo (Section 1.6, Table 1.2).

*Strong signals:* treats this as a discovery gap, not a model gap; goes to watch users; names an operations sponsor.
*Red flags:* tuning the model or prompts to raise accuracy; sending reminder emails and calling it adoption work.

### 1.3 · Debugging

**Q.** During a demo, your retrieval prototype answers a coverage question wrongly in front of the customer's head of compliance. Walk me through what you do between then and tomorrow morning.

Acknowledge the miss in the room rather than explaining it away, then treat it as a bug with a reproduction. Trace
the specific failure through the pipeline: in the chapter's day-on-site example, the cause was a chunking boundary
that separated an exclusion from the clause it modified, a retrieval problem rather than a model problem (Chapter
10). Fix it, then add that exact question to the evaluation set so the failure can never silently regress
(Chapter 12). Finally, write the failure, its cause and the fix into the next status note, so the head of compliance
and the sponsor hear about it from you, in writing, with the evidence (Chapter 3). The chapter's point is that this
whole loop, from embarrassing demo to regression test to status note, fits in an afternoon and is the job (Section
1.1).

*Strong signals:* locates the failure in a specific component before changing anything; adds a regression case to
the evaluation set; reports it proactively. *Red flags:* patching the prompt for that one question with no
evaluation; hoping nobody brings it up again.

### 1.4 · System design

**Q.** Walk me through how you'd structure an engagement from kickoff to handover, and what you'd put in place at each stage to catch its most likely failure early.

Use the operating loop and attach an early warning to each step (Section 1.4, Table 1.2). Discover: find the
sponsor, the metric and the constraints; the failure is solving the wrong problem, and the warning is no named
sponsor or no baseline metric. Scope: write the charter and, with procurement, the statement of work; the failure is
unbounded scope, warned by no written out-of-scope list. Prototype honestly: build the smallest thing that tests the
riskiest assumption; the failure is a demo that can't be measured, warned by no evaluation set before the demo.
Harden: security, evaluation, observability, rollback; the failure is a late security block, warned by security not
being consulted in week one. Deploy and drive adoption: the failure is nobody using it, warned by activation not
being instrumented. Hand off and productise: the failure is a customer who can't run it, warned by a runbook the
customer has never executed. Add that the loop isn't strictly sequential: discovery continues throughout, and parts
get hardened while others are still being scoped.

*Strong signals:* names a concrete early warning per step, not just the step; mentions feeding learning back to the
product team. *Red flags:* a waterfall plan that ends at "deploy"; no adoption or handover stage at all.

### 1.5 · Customer scenario

**Q.** On a fixed-price engagement, the customer's operations manager stops you in a corridor and asks whether you can "just add" CRM write-back by the end of the month. How do you respond?

Don't say yes, and don't say no. A casual promise in a hallway can create a contractual obligation, and on a fixed-
price statement of work scope is everything: every change needs a change request (Section 1.5, Table 1.3; Chapter
16). Respond positively but without committing: you'll look at what it involves and come back with the impact.
Then involve your commercial counterpart (the account executive, deployment strategist or engagement manager), since
you should already have agreed who speaks to the customer about price, scope and dates. The request then becomes a
written change with its effect on effort and dates, usually as a trade against something already planned. Also note
that the operations manager may not be the person who can change scope: the sponsor who owns the budget decides.

*Strong signals:* recognises the contractual risk of a hallway promise; routes it through the commercial counterpart
and a change request; stays helpful in tone. *Red flags:* "Sure, it's only a couple of days"; a flat refusal that
damages the relationship.

### 1.6 · Technical

**Q.** The sponsor wants to see your prototype next week. What has to exist before that demo, and why?

"Prototype honestly" means the smallest thing that tests the riskiest assumption, and measuring it (Section 1.4;
ex70). Before the demo, three things should exist. An evaluation set, because the characteristic failure of the
prototype step is a demo that can't be measured, and its early warning is having no evaluation set before the demo
(Table 1.2). A baseline for the metric the sponsor cares about, because the trait the chapter calls measurement means
baselines before demos, evaluations before launches and control groups before claims. And, from the Tailspin case,
activation instrumented before the first demo, so that once people start using it you can see who does (Section
1.6). The payoff is the sentence the chapter calls the most persuasive an FDE can say to a sponsor: one that contains
a number and the word "measured".

*Strong signals:* insists on an evaluation set before the demo; ties the demo to the sponsor's baseline metric.
*Red flags:* polishing the user interface for the demo; showing hand-picked examples with no measured result.

### 1.7 · Behavioural

**Q.** Engineers come to this role from different backgrounds. Which gaps does yours leave, and what are you doing to close them?

Answer with self-awareness and a plan, not modesty. Name your starting point (backend or platform, data engineering,
machine learning, solutions architecture or consulting) and the gap that predictably comes with it. The chapter's
framing is that gaps reflect the failures you've lived through: a backend engineer knows why retries need jitter but
may never have watched a perfect system go unused; a consultant knows why adoption needs a plan but may never have
been paged at 3 a.m. (Section 1.6). Then give your plan: working the exercises in your weak areas first, under time
pressure, writing down what surprised you, and using a capstone as the running example. Show evidence you've already
started, and pitch the level honestly against the Foundation, Independent Practitioner and Production-ready FDE
levels the Introduction defines.

*Strong signals:* a specific gap tied to a specific missing experience; a concrete closing plan with evidence of
progress. *Red flags:* claiming no gaps; "I'd need to know everything first", which the chapter lists as a
misconception.

## Chapter 2 · Discovery and Scoping

### 2.1 · Customer scenario

**Q.** You arrive at Northwind Insurance for a six-week pilot. By Wednesday, the VP of claims wants shorter handle times, compliance wants fewer coverage errors and IT security hasn't heard of the project. What do you do this week?

Recognise that none of this is a modelling problem, and that any of it can sink the pilot: no agreed success, no
clear owner and a security team that will surface late (Section 2.1). This week, draft the charter and let its gaps
drive the conversations (Section 2.3; ex01). Find the sponsor by asking, "If the VP of claims and compliance
disagree, who decides?" A committee isn't a sponsor. Write both goals as candidate metrics, each with a numeric
baseline, a target and a unit, and plan to measure the missing baselines in week one. Send open questions together
with dated working assumptions (ex06). Put IT security on the stakeholder map as high influence and get the security
review started in week one rather than when the plan says it could start, logging it as a risk in the RAID log
(Section 2.5; ex04, ex07). Then bring the list of charter failures to a sponsor meeting instead of guessing.

*Strong signals:* forces a single named decider; turns both goals into measurable metrics with baselines; engages
security in week one. *Red flags:* picking one goal and starting to build; proposing a retrieval architecture
before the metric and users are known.

### 2.2 · Technical

**Q.** Walk me through building a business case for an AI assistant that a CFO will accept. What goes in, and what does the CFO actually need to see?

Five pieces (Section 2.4; ex03). Labour savings: tasks per month × 12 × adoption × minutes saved ÷ 60 × loaded hourly
cost. Model cost: tokens per call (input and output priced separately) × price × calls per task × tasks per year.
Run cost: model cost plus platform cost. Net benefit is savings minus run cost; first-year ROI is (net − one-time
cost) ÷ (one-time cost + run cost); payback is one-time cost ÷ monthly net benefit. For Northwind that gives $864,000
of savings, $720,960 net, 120% ROI and 4.2 months' payback. But the CFO needs the sensitivity analysis: halving
adoption cuts net benefit by 60%, doubling token price by about 3%, so adoption decides ROI. Then make it complete:
add human review and ongoing operations, which drops ROI to 84% and stretches payback to 4.7 months. Label every line
measured, quoted, estimated, assumed or projected, use finance's loaded labour cost, and point out your own
conservative choices.

*Strong signals:* adoption explicit in the model with a sensitivity table; costs pilots usually omit; a status label
on every line. *Red flags:* a single ROI number with no sensitivity; obsessing over token price while assuming every
task uses the assistant.

### 2.3 · Customer scenario

**Q.** The sponsor wants eleven features in a six-week pilot. You have 25 engineer-days, and the must-haves alone need 30. How do you handle it?

Use MoSCoW prioritisation (Section 2.6; ex08). Include every must and its dependencies first. Here the musts alone
need 30 days against 25 of capacity, so stop planning: this isn't a planning problem, it's a conversation with the
sponsor, opened with the exact gap ("musts need 30 days, capacity 25"). The sponsor chooses: demote something to a
should, add capacity or move the date. Once the musts fit, add shoulds and then coulds in order of value per day of
effort, each only if it fits the remaining capacity and its dependencies are already in; won'ts are always deferred.
Write the trade-off message listing what's included, what's deferred to phase two and the slack left, because a plan
with zero slack is a plan to be late. Throughout, never cut quality silently: dropping tests, evaluation or security
review moves the cost to production. Cut scope loudly, in writing.

*Strong signals:* quantifies the overrun and hands the trade to the sponsor; keeps visible slack; protects quality.
*Red flags:* "we'll work weekends"; quietly skipping evaluation or security review to fit.

### 2.4 · Technical

**Q.** How would you estimate the delivery date for a pilot's statement of work, and which date would you give the customer?

Ask for three estimates per task: optimistic, most likely and pessimistic. PERT gives expected = (o + 4m + p) / 6 and
standard deviation = (p − o) / 6; for 3, 5 and 13 days that's 6 days and 1.67, longer than the most likely value
because pessimistic tails are longer (Section 2.6; ex81). Schedule with the critical path method: a forward pass for
earliest starts, a backward pass for latest starts, and slack as the difference. Zero-slack tasks form the critical
path. The P50 is the sum of expected durations along it; the P90 approximates as P50 + 1.2816 × the square root of
the summed variances on the critical path. Quote the P90 to the customer and plan internally to the P50. Then add two
caveats: the formula ignores near-critical paths, so the true P90 is longer and you add an explicit contingency line
for integration and customer dependencies; and any customer dependency on or near the critical path goes into the
RAID log and the SOW's customer responsibilities.

*Strong signals:* gives a range, not a date; knows the P90 is still optimistic; tracks customer dependencies with
modest slack. *Red flags:* a single-date estimate; padding every task invisibly instead of a visible contingency.

### 2.5 · Customer scenario

**Q.** Midway through the pilot, a team lead asks, "Could it also handle the Spanish-language tickets?" How do you respond, that day and that week?

This is how scope creep arrives: a reasonable question answered with a reasonable "probably" (Section 2.3). Don't
say "probably". If the charter's acknowledged out-of-scope list covers it, say so without argument: "That's on the
phase-two list; shall we discuss swapping it for something?" The same day, reply in writing, "Happy to look at this.
I'll send a change note by Friday with the impact", and then do it (Section 2.6). The change note states what's
asked, why, the effect on effort and dates from a re-run estimate rather than a guess, what it displaces, and who
approves. The sponsor approves scope changes; you approve nothing on the customer's behalf, and a team lead may not
be able to either. Most requests become trades, such as adding Spanish support and deferring CRM write-back to phase
two.

*Strong signals:* says yes to the process, not to the feature; re-runs the estimate; routes approval to the sponsor.
*Red flags:* agreeing informally to keep the customer happy; a flat no with no path forward.

### 2.6 · Coding

**Q.** You want to use an LLM to turn discovery interview transcripts into user stories. How would you build it so a malformed reply never reaches the backlog, and what happens to the output afterwards?

Follow the pattern from ex02 (Section 2.2). Ask the model for structured output that must parse against a fixed
schema: each story has `as_a`, `i_want`, `so_that` and a list of `acceptance_criteria`. Treat the transcript as
untrusted input and delimit it, for example inside `<transcript>` tags. Validate the reply at the boundary, and when
validation fails, send the error back so the model can repair its answer, so a malformed reply never reaches the
backlog. Chapter 9 develops the pattern fully. Then the step that matters more than the code: read the drafted
backlog back to the customer, in their words. The model can draft in seconds, but the customer owns the backlog. A
backlog they didn't review is yours, and when it's wrong it'll be your fault.

*Strong signals:* schema validation plus a repair loop; delimiting untrusted input; customer review as part of the
design. *Red flags:* pasting raw model output into the tracker; treating the model's draft as the requirements.

### 2.7 · Behavioural

**Q.** Tell me about a time a stakeholder with real influence found out about your project late. What would you do differently now?

Structure it as situation, action, result, and make the lesson about process. The story should show that the
problem wasn't the system but the communication plan: like Legal at Northwind, arriving two weeks in with an
unscheduled review even though nothing had changed (Section 2.5). Describe what you did then, and what you'd do now:
score every stakeholder from 1 to 5 on influence and interest, and set cadence and channel by quadrant. High
influence with high interest is managed closely, weekly and one to one; high influence alone is kept satisfied with
an executive summary every two weeks, which in the chapter's example would have surfaced the review in week one. Add
RACI with exactly one accountable person per workstream, and raise any unowned workstream at the next steering
meeting with a proposed owner (ex04).

*Strong signals:* owns the miss without blaming the stakeholder; names a repeatable mechanism, not just "more
communication". *Red flags:* "they should have read the emails"; only ever mapping the people who are interested.

### 2.8 · Customer scenario

**Q.** Procurement sends you a draft statement of work to review before signature. Which clauses do you read most carefully as the engineer, and what are you looking for?

The commercial lead owns the contract, but several clauses decide how your weeks go (Section 2.6, Table 2.5). Check
the assumptions the estimate depends on (data access by week one, a named sponsor, an approved model endpoint), so a
customer-caused slip doesn't look like yours. Check that exclusions repeat the charter's out-of-scope list word for
word, that staffing names the customer's people the plan needs, and that dependencies are dated and linked to the
critical path. Make sure acceptance says who tests each deliverable, against which criteria, within how many working
days and what happens if nobody responds, and that every criterion is verifiable without you. Read support
boundaries and exit criteria hardest: the hypercare period, hours and severities, and what ends the engagement.
Without them you become the customer's permanent on-call. Finally, confirm a change-control clause and who may
approve (ex81).

*Strong signals:* singles out exit criteria and support boundaries; insists on verifiable acceptance criteria.
*Red flags:* "that's the account team's job"; accepting "copilot deployed" as an acceptance criterion.

## Chapter 3 · Technical Communication

### 3.1 · Customer scenario

**Q.** You take over an engagement whose weekly notes have been green for six weeks. The tracker shows the archive-access task overdue since week three and two more tasks overdue since week five. What do you do?

Recompute the status from the tracker instead of trusting the colour (Section 3.2; ex05). Under ex05's rules a
project is red if any blocked task is due within seven days or already overdue, or if three or more tasks are
overdue; amber if anything is overdue or blocked. This project was amber from week three and red from week five, so
it's red today. Send a red note the same day, not at the next steering meeting. Put the ask at the top with an owner
and a date, here read access to the archive, with dated options for the sponsor to choose between; in the chapter's
case the sponsor approved access within 48 hours once it was in front of them. Restore the risks section and keep
empty sections visible as "none". Then agree the status rules with the sponsor in writing, and apply them every week
so the colour can't drift with anyone's mood.

*Strong signals:* computes rather than feels the colour; escalates immediately with a concrete ask; fixes the process,
not just this week's note. *Red flags:* moving to amber to soften the news; waiting to fix it quietly before telling
the sponsor.

### 3.2 · System design

**Q.** How would you design the handover documentation and process so the customer's operations team can roll back a bad release at 3 a.m. without calling you?

Two layers: a mechanical check and a human test (Section 3.3; ex69). Lint the runbook like code. It needs Overview,
Prerequisites, Deploy, Rollback, Monitoring and Escalation headings; no TODO, TBD or FIXME; every code fence labelled
with its language; no skipped heading levels; a code block in the Rollback section, because "roll back the
deployment" isn't a procedure; an email address or phone number under Escalation; and every `<PLACEHOLDER>` in a code
block explained in the prose, so nobody meets an unexplained service or namespace name at 3 a.m. Passing the linter
only proves it isn't certainly bad. The real test: someone other than you runs the rollback from the runbook alone
before you leave, scheduled as a handover milestone, and you fix every place they hesitate. Write for the tired
reader: numbered steps, the command first and the explanation second, and the expected output after each step.

*Strong signals:* a rehearsed rollback by the customer as an explicit milestone; documented placeholder values.
*Red flags:* "the runbook is in the wiki"; a rollback section with prose but no command.

### 3.3 · Technical

**Q.** The sponsor says, "Handle time fell from 11 minutes to 7.5 after launch, so the copilot works." How would you test that claim before it goes into the readout?

A before-and-after comparison is weak evidence: handle time moves with seasonality, new hire cohorts and policy
changes (Section 3.5; ex82). Use difference-in-differences: compare the change in the pilot teams with the change in
a control group over the same period. In the chapter's example the pilot teams fell from 11.0 to 7.5 minutes (−3.5)
and the other teams from 10.8 to 10.2 (−0.6), so the copilot is credited with −2.9 minutes, 26% of the pilot
baseline. The method rests on the parallel trends assumption, that without the copilot both groups would have changed
by the same amount. Check it by comparing the groups' trends in the weeks before launch, choose a control group doing
similar work, and state the assumption in the readout, since finance will ask. The control group has to be planned
in week one, ideally as a staggered rollout, because it can't be built retroactively.

*Strong signals:* names the counterfactual and parallel trends; knows the control group is a discovery-time decision.
*Red flags:* reporting the 3.5-minute drop as the effect; using logins as proof of impact.

### 3.4 · Customer scenario

**Q.** Most teams have activated on the copilot, but one team sits at 20% activation. What do you look at, and what do you do?

Adoption problems are local, so look locally (Section 3.5; ex82). Start with the funnel broken down by team: invited,
activated, engaged and habitual (questions in at least three distinct weeks), plus weekly cohort retention for the
users who did activate. Then find the team's specific reason; the chapter lists the usual ones: a manager who wasn't
briefed, a workflow the tool doesn't fit, or a bad first experience. Scale the change actions to severity. In ex82, a
team below 25% activation gets an executive sponsor message, a hands-on workshop and a named champion; teams between
25% and 50% get champion office hours and in-app tips. Keep measuring weekly, and watch the engaged-to-habitual
transition, which is usually the most informative: people try a tool once, and come back only if it helped.

*Strong signals:* segments by team before acting; diagnoses a team-specific cause; measures after the intervention.
*Red flags:* a company-wide reminder email; concluding the model needs improving from activation data alone.

### 3.5 · Technical

**Q.** Your product team has started ignoring the field-feedback channel. How would you turn a few hundred anecdotes from several customers into something they act on?

Forwarded anecdotes train product teams to tune out; give them a short, consistent, quantified brief instead
(Section 3.4; ex68). Cluster similar requests across customers: ex68 uses a greedy pass on token-set Jaccard
similarity against each cluster's seed, and in production you might use embeddings; "SSO with Okta" and "support for
Okta login" are one request. Weigh each cluster: distinct customers × 10, plus their annual recurring revenue
(counted once per customer) ÷ 100,000, plus severity weights of 5 for a blocker, 2 for major and 1 for minor. Write
one page with the top three clusters, each with customers, revenue, severity mix, score and a quotation from the most
severe item. Agree the weighting with product, since it's a starting point rather than a truth, and send one brief a
month. Then close the loop: tell customers and FDEs what was decided, even "not this year", and review a request
register with the account team before every quarterly business review.

*Strong signals:* dedupes across customers and counts revenue once; closes the loop with requesters. *Red flags:*
ranking by how loudly or often something was asked; more forwarding, just better formatted.

### 3.6 · Customer scenario

**Q.** Handover is a month away. How would you show the sponsor, with evidence, that their team can run the system without you?

Turn "can they run it without us?" into a measured result (Section 3.5; ex84). Build the workshop agenda so every
learning objective gets a concept block, a demonstration, a lab and a five-minute knowledge check; an objective with
no lab is a lecture. Make every lab step verifiable with a command or an expected result. Measure readiness per
person and per objective: someone is ready when their quiz score meets the pass mark and they completed the lab. The
bar is at least two ready people on every objective, so no skill depends on one person's holiday plans. Any
objective with nobody ready is a handover risk: put it in the RAID log with an owner and a date for a follow-up
session. Pair this with the runbook test from Section 3.3, someone on their team performing the rollback from the
runbook alone, and report both in the enablement plan the team leads read before handover.

*Strong signals:* readiness defined as quiz plus lab, per objective; the two-person rule. *Red flags:* "we ran three
workshops" as the evidence; measuring attendance instead of ability.

### 3.7 · Behavioural

**Q.** Tell me about a time you had to report a result that was smaller than you'd originally projected. How did you present it?

Structure it as situation, action, result. The story must show that you replaced your own assumption with a
measurement, unprompted, and that it built trust rather than costing it (Section 3.6). The chapter's worked example
shows the shape: the business case assumed four minutes saved per question; the pilot measured 2.9; re-running the
model took first-year ROI from 120% to 59% and payback from 4.2 to 6.2 months. Describe how you presented it: the
recommendation first, in one sentence with the measured number; the evidence and its main assumption; the re-run
value case, saying which version of the business case it is and which lines are now measured and which still
assumed; the top risks with owners; and a dated decision. The result should be a decision the sponsor could defend,
and a sponsor who trusted your numbers afterwards.

*Strong signals:* volunteers the correction before anyone finds it; distinguishes measured from assumed lines.
*Red flags:* reusing the original assumption in the readout; burying the smaller number in an appendix.

### 3.8 · Technical

**Q.** How would you use an LLM to draft weekly status notes and readouts without risking an invented number reaching the sponsor?

Models are good at structure and tone and fluent at inventing plausible numbers, names and dates, so separate the two
jobs (Section 3.6). First, facts come from systems and prose from the model: compute status, metrics and dates in
code, as ex05 and ex82 do, and pass them in for the model to write around. Second, constrain the output to what you
supplied, and check it: a short script that extracts every number from the draft and looks for it in the source data
catches most fabrications. Third, give the model the fixed template (status, asks, done, next, risks) and validate the
headings, as ex69 lints runbooks. Fourth, read it as the recipient would and cut hedging and filler until the ask is
impossible to miss. For different audiences, generate every version from the same tracker so they differ in depth,
never in facts.

*Strong signals:* the model never produces the numbers; an automated check that every number traces to the source.
*Red flags:* "I proofread it carefully"; asking the model to summarise the Slack channel into a status.

## Chapter 4 · Production-Grade Python

### 4.1 · Technical

**Q.** The customer's ERP returns `429` and `503` under load during your nightly sync. Walk me through your retry policy, and tell me what changes when the call is `POST /refunds`.

Start with what to retry: only transient failures, meaning connection errors, timeouts, `408`, `429` and `500`, `502`,
`503`, `504`. Never `400`, `401`, `403` or `404`, which fail the same way every time. Wait using capped exponential
backoff with full jitter: before retry *n*, sleep a random time between zero and `min(max_delay, base_delay × 2ⁿ)`.
Jitter stops clients that failed together from retrying as a synchronised wave. When the server sends `Retry-After`,
honour it. Retry at one layer only, the outermost one that knows whether the operation is idempotent, because four
attempts at each of three layers turns one request into 64 calls during an outage. A refund isn't idempotent, so
every attempt carries the same idempotency key. The server stores the first successful result under that key and
returns it for repeats, rejects a reused key with a different payload, and stores nothing on failure. In production
the store is shared and durable, and the key is reserved `in_progress` under a unique constraint before the side
effect runs. Ask the API team on day one which endpoints accept an `Idempotency-Key` header. (Section 4.2; ex10)

*Strong signals:* names full jitter and explains why; retries at one layer; reserves the key before the side effect.
*Red flags:* retrying every error in a tight loop; "the refund API will deduplicate it" with no key.

### 4.2 · Debugging

**Q.** Your service crashed in the customer's Kubernetes cluster with `KeyError: 'API_KEY'`. After they fixed it, the next start printed the key into their log platform. What went wrong, and how would you restructure the configuration code?

Both failures have one cause: configuration that's read lazily and printed carelessly. Restructure it so that a
`load_settings` function reads every setting at start-up, validates each one (the base URL must be `https://`, the
timeout must be above zero, retries between 0 and 10), collects every problem and raises a single `ConfigError`
listing them all. One restart then reports every missing variable, instead of one per redeploy through the
customer's change process. Wrap the key in a `Secret` type whose `str()` and `repr()` print `****`, so logging the
settings object or a traceback with local variables can't leak it; code that needs the value calls `reveal()`, a
deliberate act a reviewer can spot. Print a `redacted()` view of the effective configuration as the first log line,
because configuration differences cause half of "works on my machine" problems. Mention that `pydantic-settings` and
`SecretStr` do the same job where the dependency is allowed, and ask how the customer delivers secrets: environment
variables, mounted files or a vault. (Section 4.1; ex09)

*Strong signals:* treats both incidents as one design flaw; makes leaking a secret impossible by construction.
*Red flags:* fixing only the one variable; "remove that log line" as the whole fix.

### 4.3 · Coding

**Q.** You need to classify 40,000 historical tickets with a model before Monday's readout. Sketch the code you'd write to run the batch, and tell me which bugs you'd guard against.

Sequential calls at 2.7 seconds each take 30 hours, and an unbounded `asyncio.gather` gets rate-limited within
seconds, so you need two limits. An `asyncio.Semaphore` bounds requests in flight; a token bucket bounds the request
rate. The bucket refills continuously at *R* tokens per second up to a capacity, and `acquire` takes a token under an
`asyncio.Lock`, sleeping `(1 - tokens) / rate` when none is left. `gather_limited` wraps each call factory: acquire
the semaphore, then a token, then await the call, returning the exception in that item's slot instead of raising.
Guard against four bugs: use `time.monotonic()`, because wall-clock time can jump; rely on `gather` to keep results
in input order; isolate failures so one bad ticket doesn't cancel 39,999 others; and reject `concurrency < 1` or a
non-positive rate, because a zero-size semaphore waits forever without failing. Size both limits from requests and
tokens per minute measured in the customer's tenant, with headroom for production traffic, and consider a batch API
for large offline jobs. (Section 4.4; ex12)

*Strong signals:* separates concurrency from rate; validates limits; measures the tenant's real quotas.
*Red flags:* only a semaphore, or only `sleep` between calls; letting one exception cancel the whole batch.

### 4.4 · Technical

**Q.** A user says the copilot gave a wrong answer "around 3 p.m.", and your logs are free-text prints from four services. What would you put in place so the next report takes minutes to trace?

Three techniques. First, structured logs: every event is one line of JSON with a UTC timestamp, level, logger name,
message and structured fields, which log platforms index so you search fields instead of writing regular expressions.
Second, a correlation id for every request: generate it where the request enters, pass it downstream (usually as an
`X-Request-ID` header) and put it in every log line. A `correlation()` context manager on `contextvars` carries it
across threads and `asyncio` tasks without threading it through every function, and resets the token on exit so
nested blocks restore the outer id. Third, redaction at any depth: keys such as `password`, `api_key`,
`authorization` and `ssn` become `[REDACTED]` inside nested dictionaries and lists, done in the formatter so it
covers every log call, including those written by people who never read the guidelines. The investigation then
becomes a search for that user's requests in the window, a search for each correlation id across the four services,
and a timeline. Distributed tracing (Chapter 14) builds on this. (Section 4.3; ex11)

*Strong signals:* propagates the id across services and async tasks; redacts centrally in the formatter.
*Red flags:* "add more print statements"; redaction left to each developer's discipline.

### 4.5 · Debugging

**Q.** On day two, the finance team hands you a contractor's invoice script and seven bug reports in their own words. Walk me through how you'd work through them, using "tags from one invoice show up on other invoices".

Method before fixes. Reproduce each report as a failing test named in the customer's own words, because a report you
can't reproduce is one you can't prove fixed. Find the root cause rather than the symptom: tags leaking between
invoices isn't fixed by clearing the list at the end of the loop; it's a mutable default argument (`tags=[]`) shared
by every call, so default to `None` and create a new list per call. Make the smallest change that addresses the cause,
without changing signatures, and explain it in one line the customer can read (`# FIX(3): …`). The other reports
follow the same catalogue: `Decimal` instead of `float` for amounts with separators and for cents, `range(1,
total_pages + 1)`, treating naive datetimes as UTC explicitly, iterating over a copy of the keys, and replacing
`except Exception: return {}` with an error naming the corrupted file, so only a missing file returns defaults.
That last one matters most, because a silent wrong answer reaches the CFO. Finish by showing the seven passing tests:
evidence, and a regression suite for the next contractor. (Section 4.5; ex13)

*Strong signals:* failing test first; root cause over symptom; catches specific exceptions only.
*Red flags:* patching symptoms; rewriting the script wholesale; keeping a bare `except` that returns a default.

### 4.6 · System design

**Q.** The customer's legacy policy-lookup service falls over every afternoon, and when it does your whole copilot stops responding, even the features that don't use it. How would you contain it?

Name the failure first: a cascading failure. Threads wait on 30-second timeouts, the pool fills, and features that
never call the service stop too. Limit the blast radius in layers. Keep the timeout, and add a circuit breaker:
closed, it counts consecutive failures and opens at a threshold; open, it fails immediately with `CircuitOpenError`
without touching the dependency; after a reset timeout it goes half-open and allows one trial call, closing on
success and reopening on failure. Pair it with a fallback a user would accept, such as yesterday's cached clause with
a notice, rather than a spinner. Add a bulkhead that caps concurrent callers to this dependency and rejects when full
instead of queueing, because queueing behind a slow dependency is how the pool filled. Keep retries at one layer with
jitter; the book's retry-storm example also capped retries at 10% of traffic with a retry budget. Test it with an
injected fake clock, so the boundary (29.9 seconds still open, 30.1 half-open) is checked in milliseconds.
(Sections 4.6 and 4.7; ex14)

*Strong signals:* explains why the bulkhead rejects; pairs the breaker with a user-acceptable fallback.
*Red flags:* "raise the timeout" or "add more threads"; a breaker with no fallback or no half-open state.

### 4.7 · Customer scenario

**Q.** An operations lead wants every inbound email triaged by a model, but says "if the AI loses one email, we switch it off". Worker pods sometimes die mid-job. How do you design for that, and what do you show them?

Put the emails on a job queue with the semantics production queues provide. A worker claims a job under a lease; if
the pod dies, the lease expires and another worker claims it. That gives at-least-once processing, so the handler
must be idempotent, and an idempotency key on enqueue stops the same email being queued twice. A failed job comes
back after a backoff; after `max_attempts` failures it moves to a dead-letter list rather than retrying forever.
Lease checks mean a worker can only acknowledge or fail a job it still holds, so a slow worker can't overwrite the
one that took over. Choose the lease length from measurements: comfortably above the 99th-percentile handler time,
with heartbeats (`extend`) for long model calls. Too short runs work twice; too long leaves a crashed worker's jobs
waiting. Then answer the lead's real concern: show the dead-letter queue on day one, with a named owner and a daily
review, so "the AI lost my email" becomes "three emails need a human; here they are". (Section 4.6; ex15)

*Strong signals:* links at-least-once delivery to idempotent handlers; sizes leases from measured percentiles;
gives the dead-letter queue an owner. *Red flags:* promising exactly-once processing; retrying poison messages
forever.

## Chapter 5 · Enterprise Integration

### 5.1 · Technical

**Q.** To build a retrieval corpus you need every ticket from the customer's helpdesk API: cursor pagination, 100 per page, strict rate limits. Walk me through the client you'd write.

Begin with timeouts: a connect timeout of a few seconds and a separate read timeout sized to the slowest legitimate
response, held in validated configuration, because clients such as `requests` wait forever by default. Then the
client follows the cursor until there isn't one, yielding items as it goes so memory stays flat however large the
dataset. On `429` it waits `Retry-After` seconds (default one) up to a retry limit, then fails loudly. It also
respects the rate-limit headers proactively: after any response with `X-RateLimit-Remaining` at zero, it sleeps until
`X-RateLimit-Reset` before the next request, instead of waiting to be told off. A `max_pages` guard turns a buggy API
that returns the same cursor forever into an error rather than a growing bill. Header names are case-insensitive, and
HTTP/2 lower-cases them, so normalise before reading. Finally, if the corpus runs to millions of records, ask whether
the vendor offers a bulk export, a change feed or a replica, which can turn a two-day backfill into an hour.
(Section 5.1; ex16)

*Strong signals:* streams results; waits proactively on rate-limit headers; guards against cursor loops.
*Red flags:* loading every page into memory first; no timeout; header lookups that are case-sensitive.

### 5.2 · System design

**Q.** The customer's CRM will push "case updated" webhooks to your service, and their security team wants to review the endpoint. Walk me through what the endpoint checks, and in what order.

Five checks, and the order matters. First, verify an HMAC-SHA256 signature computed over the timestamp and the raw
body bytes, before any JSON parsing, because re-serialising can reorder keys or change whitespace. A missing,
malformed or wrong signature gets `401`. Second, compare with `hmac.compare_digest`, never `==`, which returns early
and can leak a valid signature through timing. Third, reject a timestamp more than five minutes from your clock with
`400`; because the timestamp is signed, an attacker can't change it, so this limits the replay window. Fourth, keep
processed event ids for longer than that window and answer a repeat with `200 duplicate`, which handles both replays
and legitimate redeliveries. Fifth, acknowledge quickly with `202 Accepted` and process asynchronously, because slow
receivers get retried and create more duplicates. Authenticating before parsing means an unauthenticated sender can't
make you do work or fill your deduplication store. Add that webhooks still get lost, so the endpoint is paired with a
reconciliation pull. (Section 5.2; ex17)

*Strong signals:* raw bytes, constant time, signature checked before parsing. *Red flags:* verifying over parsed
JSON; processing synchronously before acknowledging; no deduplication.

### 5.3 · Debugging

**Q.** Your 32-thread backfill job locked itself out of the customer's OAuth token endpoint within seconds. What happened, and how would you fix the token handling?

The job fetched a new client-credentials token on every call, while the gateway issues tokens valid for an hour and
limits the token endpoint to ten requests a minute. The fix is a token provider with three properties. Cache the
token and reuse it while `now < issued_at + expires_in − skew`; a 60-second skew refreshes a little early, so no
request leaves with a token that expires in flight and small clock differences don't cause failures. Refresh
single-flight: check validity, take a lock, then check again inside it, so when all 32 threads find the token expired
at once, exactly one fetches and the others reuse its result. And on `401`, invalidate the cache, fetch a fresh token
and retry once only, because tokens can be revoked early when keys rotate, but retrying more than once turns a wrong
client secret into a loop against the token endpoint's rate limit. Prove it with a test in which 32 concurrent threads
cause exactly one token call. (Section 5.2; ex18)

*Strong signals:* explains the re-check inside the lock; caps the `401` retry at one. *Red flags:* a token per
request; a lock without the second validity check; retrying `401` in a loop.

### 5.4 · System design

**Q.** The copilot needs an up-to-date copy of the customer's CRM cases. How would you choose the integration pattern, and keep the copy correct when deliveries are lost, duplicated or out of order?

Compare the five patterns: scheduled polling (minutes to hours; deletions invisible), webhooks (seconds; duplicates,
missed deliveries, ordering), change data capture or a change feed (low load; schema changes and log access), bulk
export (backfills) and an event stream if the customer already runs one. For cases, webhooks usually give freshness,
but push is fast and pull is complete: deliveries get lost to sender give-ups, deploys and firewall changes. So pair
them with a periodic reconciliation pull of everything updated since a watermark, through the same code path. That
path applies updates idempotently in version order: store a record only if its version is newer than the copy you
hold. Deduplicating by event id isn't enough; in the book's hypothetical case, redelivered events with distinct ids
but older `updated_at` values reopened 1,140 closed cases. Add a nightly count per day against the source, a test
that delivers the same events shuffled and twice, and a separate plan for deletions. (Section 5.3; ex17 Part B)

*Strong signals:* "push for freshness, pull for completeness"; version-ordered application on both paths.
*Red flags:* trusting webhooks alone; last-write-wins in arrival order.

### 5.5 · Customer scenario

**Q.** The customer's CRM administrator sends a 50,000-row export with phone numbers in five formats and blank revenues, and asks when the import will be done. How do you handle it, and what do you send back?

Map the export into the canonical model with three rules. Normalise every value to one representation: phone numbers
to E.164, timestamps to timezone-aware UTC, revenue to integers whether it arrives as `"1,200,000"` or
`"1200000.0"`, so downstream code never handles five formats. Never abort the batch for one bad row; collect errors
and keep going, because stopping at row 4,812 leaves nothing to show and no idea how many other rows are bad. Report
every error in a row with its row number and field, such as `RowError(row=4812, field="Phone", …)`, not just the
first, so the administrator can fix the source in one pass instead of fixing, re-running and finding the next
problem. Keep derived fields such as the revenue segment in the mapper, and give missing revenue an `unknown`
segment rather than forcing it into a real category, which would be a silent data error. What you send back is the
count of clean records loaded and the full error list for the administrator to correct. (Section 5.3; ex19)

*Strong signals:* a complete per-row error report the customer can act on; an explicit `unknown`.
*Red flags:* aborting on the first bad row; silently guessing values for missing or malformed fields.

### 5.6 · Technical

**Q.** The customer's platform team will only deploy services that pass their checklist. What would your minimal question-answering service do, and why does each item matter?

Build it on the standard library so it runs in their locked-down base image without new dependencies. `GET /healthz`
returns `200 {"status": "ok"}` without authentication. `POST /v1/answer` requires a valid bearer token and returns
`401 {"error": "unauthorized"}` otherwise. Every error is JSON. Check `Content-Length` before reading and return `413`
above 64 KiB, so a 2 GB body never reaches memory. Validate input at the edge: invalid JSON or a missing, empty or
over-long question (over 2,000 characters) gets `400`, which protects the token budget as well as memory. Wrong
methods get `405` and unknown paths `404`. If the answer function raises, return a generic `500 {"error": "internal
error", "request_id": …}`, because exception text such as `KeyError: 'policy_db_password'` tells an attacker too
much. Echo the client's `X-Request-ID` or generate one, and put it in the response and every log line, so a user's
error report finds the logs in seconds. Offer a readiness endpoint too where the platform supports it, since health
isn't readiness. (Section 5.4; ex20)

*Strong signals:* checks the payload size before reading; generic 500s that still carry a request id.
*Red flags:* returning stack traces to clients; authenticating the health check or leaving business endpoints open.

### 5.7 · Technical

**Q.** The customer's internal APIs need signed requests, and the only specification is a Java SDK, a Go service and a C++ agent. How would you produce a Python signer that works with all three backends?

Treat the code as the specification. Read the reference for its canonical form: here, the method, encoded path,
canonical query, SHA-256 of the body and a timestamp, separated by newlines, where every byte matters. Read the
variants side by side to find undocumented differences: the C++ agent uses an upper-case body hash and epoch seconds,
and the Go service uses lower-case hex instead of base64 for the signature and lower-case header names. Watch URL
encoding: Java's `URLEncoder.encode` is HTML form encoding (space as `+`, `~` as `%7E`, `*` left alone), and the SDK
post-processes it to RFC 3986, so the port encodes everything outside the unreserved set as `%XX` on UTF-8 bytes.
That bug passes simple tests and fails only for paths or queries with those characters. Generate test vectors by
compiling and running the Java reference, and test the port against them byte for byte. Raise `ValueError` on an
unknown variant rather than defaulting to the Java layout. (Section 5.5; ex78)

*Strong signals:* vectors from the reference implementation as the contract; spots the form-encoding trap.
*Red flags:* porting from memory of "how signing usually works"; silently defaulting on unknown variants.

### 5.8 · Customer scenario

**Q.** Day one inside a bank, your demo fails with `CERTIFICATE_VERIFY_FAILED` and a colleague suggests `verify=False`. What do you do instead, and what should you have done before you arrived?

Decline `verify=False`: it removes the protection TLS exists to provide and tends to survive into production. The
likely cause is TLS interception re-signed by the bank's own root certificate authority, behind an authenticated
proxy and an egress allowlist. Diagnose with a tool that answers three questions for the URL: is egress allowed by
the allowlist; which proxy applies (`HTTPS_PROXY` or `HTTP_PROXY`, upper case first, with `NO_PROXY` exceptions so
internal traffic doesn't go to the external proxy); and which CA bundle is used (`REQUESTS_CA_BUNDLE`, then
`SSL_CERT_FILE`). Get the bank's root CA from its IT team, append it to a copy of your bundle and point the variable
at it. Three printed lines are something the network team can act on. Before arriving, you should have sent an access
list (accounts, VPN, badges, machine, data, firewall changes), each with its reason, approver and date, tracked it in
the RAID log, sent the preflight script a week ahead, asked whose machine you'd use, and arranged dependencies
through an internal mirror or a wheelhouse built for the target platform. (Section 5.6; ex21)

*Strong signals:* fixes trust rather than disabling it; gives the network team actionable output; plans access
weeks ahead. *Red flags:* `verify=False` "just for the demo"; arriving before access is approved.

## Chapter 6 · Data Engineering

### 6.1 · Technical

**Q.** Before you propose a support copilot, the CFO wants a baseline of ticket volumes and resolution times. How would you produce numbers the customer's analysts will trust and can re-run?

Write the baseline in SQL against the read-only replica, one query per question, each in a module-level constant the
analysts can copy. SQL rather than a notebook of pandas, because the analysts who maintain these numbers after you
leave already know SQL and already have tools to run it; a baseline the customer can't reproduce is just your
opinion. Use half-open time windows (`resolved_at >= '2026-09-01' AND resolved_at < '2026-10-01'`) rather than
`BETWEEN`, which drops everything after midnight on the last day; half-open windows also tile, so weekly numbers add
up to monthly ones. For flows such as tickets created and resolved per week, use a `UNION ALL` of the two event
streams, which keeps weeks that only had resolutions where a join would drop them. Give every query an explicit
`ORDER BY` with tie-breakers, because a CFO who sees the same table in two orders trusts neither. Ask about data
volume and growth before running anything heavy. (Section 6.1; ex22)

*Strong signals:* reproducibility by the customer as the goal; half-open windows; deterministic ordering.
*Red flags:* one-off notebook numbers; `BETWEEN` on timestamps.

### 6.2 · System design

**Q.** Nightly full reloads of the customer's 80-million-row orders table take six hours and lock their replica. Design the incremental replacement, and tell me how you'd test it.

Replace them with an incremental load that is idempotent, atomic and correct when timestamps tie. A single-column
watermark fails: with `updated_at > :wm` a batch that ends partway through 300 rows sharing a timestamp skips the
rest, and `>=` re-reads rows and can loop on a batch of identical timestamps. Use a composite watermark of
`(updated_at, id)`: select rows where `updated_at > :wm_ts OR (updated_at = :wm_ts AND id > :wm_id)`, ordered by
`updated_at, id`, with a batch limit, so every row has a unique position. Upsert each batch with `ON CONFLICT(id) DO
UPDATE` and save the watermark in the same transaction; a crash rolls both back and the rerun reloads harmlessly.
Deletes are invisible to a watermark, so ask in discovery for soft deletes, a CDC feed or id reconciliation. Test it
the way it fails: run it twice and assert identical output, make the second batch fail and assert nothing was lost or
duplicated, and feed it tied timestamps, nulls and out-of-order rows. Test at the size the table will be in a year.
(Sections 6.2 and 6.7; ex23)

*Strong signals:* explains why `>` and `>=` both fail; commits the watermark with the data; raises deletes.
*Red flags:* saving the watermark separately; plain inserts that duplicate on rerun.

### 6.3 · Debugging

**Q.** Northwind's copilot citations were wrong for a week, and nobody changed the prompt, the model or the retrieval code. How would you investigate, and what would stop it happening silently again?

If the prompt, model and retrieval code didn't change, look at the data: here an upstream job had started writing
empty policy numbers into the document metadata, and the index refresh picked them up. A model given bad context
produces a fluent wrong answer, not an error, so the defence has to sit in the pipeline. Run declarative checks before
every index refresh (`not_null`, `unique`, `matches` a pattern, `in_range`, `accepted_values`, plus dataset-level
`row_count_between` and `fresh`), with errors blocking the refresh, warnings only reporting, and samples of failing
rows so the owner can find the cause. Detect schema drift before loading: added columns and widened types are
warnings, removed columns, changed types and newly nullable fields are errors; only additive changes are migrated
automatically, the rest go to the data's owner as questions. Then move the conversation upstream with a data
contract covering schema and meaning, freshness, blocking checks, change notice and named owners. Draft it yourself
and ask the owner to correct it. (Sections 6.1, 6.3 and 6.6; ex24, ex25)

*Strong signals:* suspects the data first; separates blocking errors from warnings; turns the fix into a contract.
*Red flags:* tuning the prompt; making every check blocking, or none.

### 6.4 · Debugging

**Q.** A Spark aggregation by merchant runs for hours with one task far behind the rest, and an earlier version of the job crashed the driver. What's going on, and how would you fix both?

The straggler points to skew. Records reach partitions by hashing the key, so if one merchant has 40% of the
transactions, one partition gets 40% of the work and the job runs as slowly as that partition. Read `explain()` and
the Spark UI's stage timeline first, and measure skew as the largest partition divided by the mean. For joins,
Adaptive Query Execution in Spark 3 can split skewed partitions automatically, but an aggregation over a hot key
needs salting: append a salt from 0 to *s*−1, aggregate on the salted key so the hot key spreads across *s*
partitions, strip the salt and aggregate again. The result is the same, at the cost of a second shuffle, so salt only
hot keys. The driver crash is a separate bug: `collect()` or `toPandas()` pulls the whole distributed dataset onto
one machine, which works on a sample and fails on the full table. Keep the aggregation in Spark and write the result
to a Delta table. (Section 6.4; ex77)

*Strong signals:* reads the plan before optimising; knows what salting costs; knows AQE exists.
*Red flags:* "add more executors"; collecting to the driver to finish the work in pandas.

### 6.5 · System design

**Q.** The customer only runs managed Postgres and won't approve a separate vector database. How would you move your SQLite prototype's retrieval store onto it, and what would you watch for with many tenants?

Use the `pgvector` extension and port the dialect carefully: identity columns instead of `AUTOINCREMENT`,
`DOUBLE PRECISION` and `BYTEA`, `TIMESTAMPTZ` for timestamps, `to_char`, `COALESCE`, `ON CONFLICT DO NOTHING`, and `%s`
placeholders, without rewriting a `?` that sits inside a string literal. Choose the operator that matches your metric
(`<=>` cosine, `<->` L2, `<#>` negative inner product) and an index operator class that matches it, such as
`vector_cosine_ops` for `<=>`; otherwise Postgres silently falls back to a full scan. HNSW is the default for a few
million chunks: better speed-recall and buildable on an empty table, while IVFFlat needs representative data first.
With many tenants, watch filtered queries: HNSW considers a bounded candidate list (`hnsw.ef_search`, 40 by default)
and applies `WHERE` to it, so a tenant filter can return fewer rows than the `LIMIT`, or none. Raise `ef_search`, use
iterative scans on pgvector 0.8 or later, or a partial index or partition per large tenant, and measure recall on
filtered queries specifically. (Section 6.5; ex80)

*Strong signals:* matches operator and operator class; knows the filtered-query recall trap.
*Red flags:* assuming the index is used; benchmarking only unfiltered queries.

### 6.6 · System design

**Q.** You're building an operations agent that looks up delayed shipments and reschedules them. Why would you put an ontology between the agent and the customer's tables instead of letting it write SQL?

An ontology turns scattered tables into business objects, typed links and governed actions, and agents are safer
asking for "the delayed shipments for this customer" and calling a "reschedule shipment" action than writing SQL
against five tables. Object types have a primary key and typed properties, and loading validates every row and
reports problems by type and row index. Link types have a source, a target, a cardinality and a foreign key, and an
integrity check reports dangling links such as shipments pointing at missing customers. Traversal works in both
directions. The key part is actions: typed parameters, a validation rule (refuse to reschedule a delivered shipment),
an apply function and allowed roles. Execution checks the role, the parameters and the rule before changing anything,
then applies the change and appends an audit entry; a failed action leaves no change and no audit entry. When
actions are the only write path, permissions, validation and audit live in one place and apply equally to a human in
a web app and an agent calling a tool. (Section 6.5; ex92)

*Strong signals:* actions as the only write path; validation before any change; audit on success.
*Red flags:* giving the agent database write credentials "with a careful prompt".

### 6.7 · Customer scenario

**Q.** At 9 a.m. the CFO's office calls: the finance dashboard and the analyst assistant both show an 88% fall in yesterday's sales, and the nightly job reported success. What do you do now, and what do you change?

This mirrors the chapter's hypothetical failure case. Check the evidence first: bronze holds 1.1 million rows for
the day against a typical 9.4 million, while the job log shows success. The root cause is that the job treated
"didn't raise" as success and overwrote `gold.merchant_totals` from an incomplete extract, with nothing comparing the
new totals to the previous run. Mitigate by restoring the previous version from Delta's history (`RESTORE TABLE …
TO VERSION AS OF …`), re-running once the full extract lands, and telling the dashboard's users what happened and
what was affected. Then prevent it: blocking row-count and freshness checks on the input before any write, an alert
when an aggregate moves by more than an agreed threshold between runs, and a rule that overwrite jobs read only from
a validated batch. For incremental jobs, prefer `MERGE` or `replaceWhere` to rewriting the whole table, and use a
data diff before changing a pipeline. (Sections 6.4 and 6.7; ex77)

*Strong signals:* restores first and communicates impact; adds checks before the write, not only after.
*Red flags:* re-running the job immediately on the same input; blaming the dashboard.

### 6.8 · Customer scenario

**Q.** The analysts want to count and join claims by customer, and the privacy officer asks how your pipeline and vector store will handle personal data, including erasure requests. What do you tell them?

Describe four habits decided when the pipeline is built. Minimise: load only the columns the use case needs, because
data you never loaded can't leak. Pseudonymise with a keyed hash, not a plain one: anyone with a list of emails can
hash them and match a plain SHA-256, whereas an HMAC with a secret held outside the analytics environment gives
analysts a stable token for joins and counts that can't be reversed by guessing. Normalise (trim, lower-case) before
hashing, or one person becomes two. Treat embeddings and chunks as personal data too: a chunk mentioning a diagnosis
is health data in a vector table as much as in a document store. Keep `doc_id` and a pseudonymised subject
identifier on every chunk, so an erasure request is a `DELETE … WHERE subject = %s`, not a re-index. Set retention
for bronze, silver, logs and chunks when the tables are created, write it down with the data owner, and schedule the
deletion job alongside the load job. Chapter 13 covers the regulations. (Section 6.6; ex24 Part B)

*Strong signals:* keyed hash with the key held elsewhere; deletion designed into the vector store.
*Red flags:* calling a plain hash anonymous; "we'd re-index" as the erasure plan.

## Chapter 7 · Full-Stack Engineering

### 7.1 · Debugging

**Q.** The copilot's answers are fine on your laptop, but inside the customer's network users occasionally see garbled accented characters and words missing mid-sentence. What would you check first, and how would you test the fix?

The pattern (fine at home, intermittent on site) points at the corporate proxy re-chunking the Server-Sent Events
stream at arbitrary points, and a client that parses each network chunk on its own. Two bugs follow. A multi-byte UTF-8
character split across chunks decodes as garbage when each chunk is decoded separately; the fix is a `TextDecoder` with
`{ stream: true }`, which holds back an incomplete sequence until the next chunk. And `chunk.split("\n")` loses or
corrupts a line split mid-way; the fix is a buffer that keeps the trailing partial line until more data arrives, and a
parser that follows the WHATWG rules (blank line dispatches, multiple `data:` lines joined with `\n`, `:` comments
ignored). While there, check that a mid-stream `error` event is surfaced rather than showing half an answer as complete.
Test it the way ex28 does: feed the parser the same stream split at every possible byte boundary and assert the output
is identical every time (Section 7.2; ex28).

*Strong signals:* names both layers (bytes to text, lines to events); proposes the every-split test so chunking bugs
can't hide. *Red flags:* "add a retry" or blaming the model; fixing only the newline split and missing UTF-8.

### 7.2 · System design

**Q.** Walk me through how you'd get streamed model output from the provider into the customer's browser. What sits in between, and what does each piece protect against?

Put a backend for frontend (BFF) between the browser and the provider. The browser authenticates to the BFF with the
customer's normal session; only the BFF holds the model key, because a key in browser JavaScript belongs to anyone who
opens developer tools. The BFF enforces limits and validation before tokens are spent (question length, per-user rate
limits, tenant checks), attributes every request to a user, tenant and request id for logs and cost, and cancels the
upstream stream when the user closes the tab or presses Stop, so you don't pay for tokens nobody reads. The relay
re-emits text deltas as SSE with `Content-Type: text/event-stream`, `Cache-Control: no-cache` and, behind nginx-style
proxies, `X-Accel-Buffering: no`, plus a `: keep-alive` comment every 15 seconds or so during long tool calls. On
failure it sends a generic `error` event to the user and keeps the details in logs with the request id. The browser
side parses the stream robustly and the event names (`delta`, `done`, `error`) live in one shared contract (Section 7.4,
Section 7.6; ex30).

*Strong signals:* all four BFF reasons, especially cancellation; knows the buffering headers and keep-alive.
*Red flags:* calling the provider directly from the browser; returning raw exception text to the user.

### 7.3 · Coding

**Q.** A chat widget sends a message twice when users press Enter twice, duplicates the question on retry and leaves the spinner running after an error. How would you restructure the code, and how would you prove the bugs are gone?

These are state bugs, not rendering bugs: state changes are scattered across event handlers, and some sequences of
events leave the state inconsistent. Move every transition into one pure reducer, `reduce(state, action)`, that never
mutates state and never calls the network. `send` returns the state unchanged when a reply is pending or the text is
empty; `stream_error` always sets `pending: false` and marks the message as errored, so the spinner stops; `retry` only
acts when the last message is an errored assistant reply and removes it rather than appending a new user message.
Return new objects and arrays, because React compares references and a mutated array won't trigger a re-render. In
the hook, read the draft before dispatching `send`, convert any thrown value into a string, and have `retry` re-send
the last user message without adding one. Prove it with unit tests in plain Node: fold a sequence of actions ("send,
send again while pending") through the reducer and assert on the result, with no browser or DOM (Section 7.3; ex29,
ex91).

*Strong signals:* pure reducer with one test per bug; explains why immutability matters for React. *Red flags:*
patching each handler with flags; tests that need a browser to reproduce the sequence.

### 7.4 · System design

**Q.** The product owner's mockup shows one screen: a question and a good answer. What else would you design before handover, and why does each piece matter to adoption?

Production users meet the other states first, so agree each with the product owner: empty (two or three example
questions from discovery), loading (a short message before the first token, not a bare spinner), streaming (with
Stop), partial failure (keep the text, mark it incomplete, offer Retry), abstention, permission denied (say what the
user can't see, not that nothing exists) and offline or unavailable. Then the trust features: clickable citations next
to the claims they support, so users can check an answer in seconds; "I don't know" designed as an intentional answer
with a link to the right human or document; visible progress when tools run ("Searching policy documents..."); human
approval for consequential actions (draft the email, don't send it); a thumbs-down with a reason that feeds the
evaluation set review; and Stop plus edit-and-resend. Each state is a reducer case and a test. The adoption funnel will
show weeks later whether these were right (Section 7.5; ex29).

*Strong signals:* lists the states explicitly and ties each to a reducer case; explains why abstention and citations
build trust. *Red flags:* treating UX as polish for later; feedback buttons with nowhere for the feedback to go.

### 7.5 · Customer scenario

**Q.** You demo to the customer's vice president at 9 a.m. tomorrow, on their locked-down laptop and guest Wi-Fi. How do you prepare, and what does the demo script look like?

Build for a network and machine you don't control. Use a single-file app served by a Python standard-library server,
so nothing needs installing. Default to a fake model with a visible `DEMO MODE` banner, and make the real model one
environment variable away (`FDE_LIVE=1`) if the network allows. Render answers with `textContent`, never `innerHTML`,
and show the latency the endpoint returns so nobody is surprised when the real model is slower. Script three
scenarios rather than a feature tour: the happy path on a question from the discovery notes, an honest abstention that
points to the right place, and a recovery that shows a plain error message instead of a stack trace. Have the sentence
ready if a live answer is wrong: that's why we built the evaluation suite. Time the script, rehearse on the customer's
network the day before, including a check of time to first byte through their proxy, and keep the fallback one
keystroke away (Section 7.4, Section 7.6; ex30).

*Strong signals:* honest demo-mode banner; rehearsal on the customer's network; the abstention scenario. *Red flags:*
a live-only demo with no fallback; hiding that the model is faked.

### 7.6 · Customer scenario

**Q.** The customer wants the copilot inside the React application their agents already use, and their security team is strict about what loads on that page. What do you ask, and which embedding approach would you propose?

Start with discovery questions: what Content Security Policy the page sends, which React version and build they use,
how their review process works, and how users authenticate today. Then weigh the four approaches. A link out is
cheapest but forces context switching, and adoption suffers. An `iframe` gives strong isolation but brings
cross-origin authentication, sizing and frame policies. A web component or script tag needs script approval and runs
into CSP, which often forbids inline scripts and unknown origins (so the single-file demo pattern won't load). A React
component in their codebase costs the most to integrate but feels native; build it the ex91 way, as a factory that
takes the React API they pass in, so it makes no assumptions about their build. Whatever the choice, reuse the user's
existing session, exchanged on the server for a token the BFF accepts, rather than a second login. Keep accessibility
and text-only rendering, since large customers check both (Section 7.6, Section 7.3; ex91).

*Strong signals:* asks for the CSP header first; links the choice to authentication and their review process.
*Red flags:* "just drop in a script tag"; a separate login for the copilot.

### 7.7 · Technical

**Q.** You're handing your front-end code to the customer's team, who will change it after you leave. What test suite do you leave them, and how do you make sure it keeps being run?

Leave a layered suite, cheapest first. Pure logic (schemas, the stream parser, the reducer) tested in plain Node with
`node --test`; these run in milliseconds and should carry most of the weight. Components rendered with a fake `h`, so
tests assert on roles, labels and text with no browser or bundler. A shared event contract module (`delta`, `done`,
`error`) imported by both the BFF's and the UI's tests, so a renamed event fails a test instead of silently dropping
text. A handful of end-to-end tests in a real browser, with Playwright or their existing tool, against the BFF running
a fake model: ask, stream, Stop, error, retry. About five catch integration mistakes; fifty become slow and flaky and
get switched off. Run an accessibility checker such as axe inside them. To keep it running, document every layer in
the README and make the default command run the first three; a suite that needs a model key, a network or your laptop
won't be run after you leave (Section 7.6; ex28, ex29, ex91).

*Strong signals:* the cost-ordered layers and the shared event contract; the default command needs no key or network.
*Red flags:* only end-to-end tests; tests that call the live model.

## Chapter 8 · Prompt Engineering

### 8.1 · Technical

**Q.** Walk me through how you'd structure the system prompt for the Northwind claims assistant, and why each part earns its place.

Use a layout that is easy to review, diff and cache. A `<role>` names the audience and stakes (adjusters act on the
answers, so accuracy beats completeness), which frames every judgement call the rules didn't anticipate. `<context>`
holds stable domain facts. `<policies>` lists rules with ids and reasons ("Never quote reserve amounts. Why: reserves
are confidential"), because reasons generalise: the model can recognise a "set-aside figure" as a reserve. Add a
sentence on resolving conflicts (prefer the hand-off, then withholding). `<examples>` are few and selected per query
when the pool is large. `<output_format>` fixes the shape, with an exact abstention sentence, and uses structured output
plus validation in code when software parses it. Write instructions calmly; capitals make current models over-apply
rules. Everything stable goes first so the provider can cache the prefix; dynamic, untrusted content goes last inside
tags such as `<document>` and `<ticket>`, and the prompt says that content in those tags is data, not instructions.
Tool definitions travel in the `tools` field but deserve the same care (Section 8.2; ex95, ex98).

*Strong signals:* rules with reasons; stable prefix first for caching; delimited untrusted input. *Red flags:*
"You are a world-class expert" and shouted MUSTs; dates or user data at the top.

### 8.2 · Debugging

**Q.** For two days a triage assistant gave confident answers that had nothing to do with the tickets it was sent. Nothing errored. What do you suspect, how do you confirm it, and how do you stop it happening again?

Suspect a template and code mismatch: the template references `{ticket}` while the code passes `ticket_text`, the
formatting library leaves the placeholder untouched, and the model receives a literal `{ticket}` and answers about a
ticket it never saw. Confirm by finding the prompt version from the content hash in the log lines and rendering it
with the variables the code actually passes, or by looking at a logged prompt where the customer allows full text.
Prevent it in two places. Lint every template in CI: ex95's P005 (a placeholder that isn't a declared variable) is an
error that fails the build, and P006 flags the declared variable that's never used; P002 would also flag `{ticket}`
not wrapped in a matching XML tag. And render strictly, so a missing or unexpected variable raises instead of passing
through (ex31). Then add the case to the golden set and the regression gate so it stays fixed (Section 8.5, Table
8.2; ex95, ex31, ex51).

*Strong signals:* names the literal-placeholder failure; fixes it with CI linting and strict rendering, not vigilance.
*Red flags:* blaming the model or rewriting the prompt; no change to the pipeline.

### 8.3 · Coding

**Q.** A ticket-routing prompt has five fixed examples, four of them about passwords. Billing accuracy is 61%, and the team's fix is to keep adding examples. How would you redesign example selection?

Fixed examples are the strongest steering signal in a prompt, and models copy their quirks, including label
distribution, so this prompt teaches that most tickets are about passwords. Adding examples only bloats it. Instead,
retrieve examples per query. Embed the query and every example's input, score relevance by cosine similarity, then
pick greedily with maximal marginal relevance: `λ · relevance − (1 − λ) · max similarity to already chosen`, with
λ = 0.7, so near-copies are penalised. Skip near-duplicates (similarity of 0.95 or more) and candidates that don't fit
the remaining token budget, without stopping the loop. For classification, make sure every label has at least one
example, replacing one from an over-represented label. Put the most relevant example last, nearest the query, and wrap
each in `<example>`, `<input>` and `<output>` tags with escaped text. Curate the pool like a golden set, with hard
negatives such as the ticket that looks like billing but is a login problem. Measure that billing improves while the
prompt shrinks (Section 8.3; ex96).

*Strong signals:* MMR with a budget and label coverage; per-query selection framed as cost engineering too.
*Red flags:* more fixed examples; plain top-k that returns five copies of the same example.

### 8.4 · Customer scenario

**Q.** A sponsor sees that your prompt change moved accuracy from 82% to 86% and wants to announce it. How do you respond, and what evidence would you want before shipping?

Thank them, then be honest that two accuracy numbers don't show whether the gain is real. First, check the process:
were edits chosen on a training split and the held-out test split scored once at the end? If anyone tuned against test
failures, the number is optimistic. Report the overfitting gap too. Second, run a paired test on the same cases.
McNemar's test looks only at discordant cases: those only the old prompt passed and those only the new one passed. On
200 cases, 11 fixed and 3 broken is a four-point gain with a two-sided *p* of about 0.057, not significant at 0.05;
the useful sentence is "it looks better, but we need about twice as many test cases to be sure". Third, with a live
model, repeat runs and compare distributions, because sampling noise can exceed an edit's effect. Fourth, check the
token and latency changes, and that no safety-critical case regressed: the change goes through the regression gate in
CI before it ships (Section 8.4; ex97, ex51).

*Strong signals:* paired test on discordant cases; held-out split; a plain-language sentence for the sponsor.
*Red flags:* announcing the averages; adding test cases until the number looks right.

### 8.5 · Customer scenario

**Q.** An auditor at Northwind asks: "Show me where rule POL-17 is in the prompt, and the test proving the assistant follows it." Rules are currently copied into the prompt by hand. What do you build?

Treat the prompt as a build artefact compiled from a reviewed policy specification. Each rule gets an id, a kind (must,
must not, escalate), the rule text, a reason and test cases, such as an input about a staged accident that must
mention the fraud team. A compiler groups rules by kind, renders each as a `<policy id="...">` line with its reason,
adds a conflict-resolution sentence and the output format, and escapes what it inserts. From the same specification
you get traceability (every rule id appears in the prompt), coverage (the share of rules with at least one test),
conformance (each rule's tests run against the model, with missing and leaked phrases reported per rule) and a
changelog of added, removed and changed rules that compliance can read. Version the specification, not the prompt,
so the two can't drift. Be clear that string tests are a floor: add rubric-graded cases with a calibrated judge for
tone, and enforce hard constraints such as never revealing a reserve in code as well (Section 8.5; ex98, ex50).

*Strong signals:* specification as the source of truth; trace, coverage, conformance and diff; hard rules also in code.
*Red flags:* pointing at a hand-edited prompt; treating the prompt as the only control for a must-never-fail rule.

### 8.6 · System design

**Q.** The provider has announced it will retire the model your assistant runs on. Walk me through how you'd move to the new model without surprising the users.

Treat the model change as a release, with the same process as a prompt change. Pin an exact model identifier, not a
moving alias, and log it with the prompt hash on every line. Run the evidence you already have against the candidate:
the golden set, the regression gate and the policy conformance cases, compared case by case, because a better average
that fails three safety cases isn't an upgrade. Add a slice of benign questions that only resemble forbidden ones, to
catch over-refusal. Strip scaffolding written for the old model (shouted rules, repeated warnings, extra examples),
since newer models follow instructions more literally and over-apply it; keep a workaround only if the evaluation shows
it still earns its place. Re-measure tokens, output length and cost, because tokenisers differ between families. Then
roll out gradually: shadow on live traffic, a canary with online signals such as refusal rate, and a rollback that is a
configuration change. Keep provider-specific details in the adapter layer, not the prompt (Section 8.6; ex31, ex51,
ex98).

*Strong signals:* pinning; case-by-case comparison plus an over-refusal slice; removing old workarounds; canary.
*Red flags:* switching after a good demo; changing the model as a plain configuration edit with no evaluation.

### 8.7 · Behavioural

**Q.** Tell me about a time someone asked you to fix a problem with "a better prompt" when the prompt wasn't the right lever. How did you decide, and what did you do instead?

Structure the story as situation, action and result. The situation should name the request and the evidence that
the prompt was the wrong lever, using the limits the chapter lists: the model lacked the facts (needs retrieval and
citations), the rule must never fail (needs permissions on tools, output filters or approvals in code), the task was
narrow, high-volume and stable (a classical baseline or fine-tuned smaller model may be cheaper), or the prompt was
compensating for a confusing tool (fix its name, description, schema and errors). The action should show how you
decided with evidence, for example the evaluation result or the paragraph of workaround text a reviewer would flag,
and how you explained the alternative to the requester without dismissing them. The result should be measurable:
what changed in accuracy, cost or safety, and what the customer's team now does differently. The story must show
judgement, not a dislike of prompting: you still used the prompt where it was the fastest lever (Section 8.6).

*Strong signals:* names the specific limit and the replacement control; a measured outcome. *Red flags:* a story
where more prompt text was the fix for a hard constraint; no evidence behind the decision.

## Chapter 9 · LLM Application Engineering

### 9.1 · System design

**Q.** A demo calls the model once and prints the reply. Walk me through what you'd put between the application and the model before it serves two million requests a month.

Treat the model as a slow, expensive, rate-limited, occasionally overloaded dependency with probabilistic output, so
Chapter 4's habits apply (timeouts, retries on transient errors, circuit breakers, structured logs), plus model-specific
stages. Prompts come from a registry with immutable semantic versions, strict rendering and a template hash logged with
every answer. A context packer fits the system prompt, question, documents and history into a budget that reserves
output tokens. A router picks the cheapest model meeting the request's tier, latency and cost limits, and fails over
only on overload errors (429, 503, 529). An exact-match response cache keyed on everything that affects the reply skips
repeat calls, never storing tool calls. Output is extracted, validated and repaired within a limit. A ledger prices
every call per tenant. Every stage logs metadata (request id, tenant, prompt hash, model, tokens, latency, cost, cache
hit, stop reason, validation outcome). And there are planned degraded modes for when no model can answer (Section
9.1, Section 9.3, Section 9.6; ex31 to ex35).

*Strong signals:* traces every stage to a reason about the dependency; logs metadata so any answer is traceable and
costed. *Red flags:* "add retries" as the whole answer; logging full prompts by default.

### 9.2 · Coding

**Q.** You're extracting claim details from adjusters' emails into the customer's claims system, and the provider supports strict JSON schemas. Do you still validate? Walk me through the code path.

Yes. Use native structured output where available, because it makes malformed output rare, but validate at your
boundary for three reasons: not every deployment target supports it (the customer's approved model version may lag),
schemas drift between code and prompt, and schema-valid isn't business-valid (an amount of −500 can pass). The path
has three pieces. Extract the first complete JSON object or array, tracking string literals so a brace inside a string
doesn't confuse the scanner; a greedy regex fails exactly there. Validate against a schema subset and return errors
prefixed with a JSON path (`$.amount: -500 is less than minimum 0`); reject booleans where numbers are expected, since
`True` is an `int` in Python, and decide deliberately whether `2.0` is an integer. Repair by sending the model its own
reply plus the specific errors, up to a bounded number of attempts, then raise. Count repairs: a rising repair rate is
an early sign of a prompt or model regression (Section 9.2; ex32).

*Strong signals:* "shape, not meaning"; path-specific errors fed back for repair; repair rate as a metric.
*Red flags:* trusting the schema feature alone; "invalid, try again" as repair feedback; unbounded retries.

### 9.3 · System design

**Q.** A bank's relationship managers want to ask questions such as "Which client spent the most in Q1?" directly against the warehouse. How would you design the system, and how would you measure whether it works?

Give the model a semantic layer, not the warehouse: a few allowed tables and views, their columns and named metric
definitions ("total spend: sum of USD amounts, refunds netted out"), since without definitions two phrasings return
two numbers. Generate the user data dictionary from the same definitions. Each attempt generates one read-only query
or an exact refusal token (`CANNOT_ANSWER`), then guards it statically before it touches the database: comments
stripped, one statement, `SELECT` or `WITH` only, no write or administrative keywords, every table on the allow-list,
and a `LIMIT` appended or lowered. Execute on a read-only connection as defence in depth. On a guard rejection or
database error, send the specific error back and retry, bounded at three attempts, then refuse with a fixed message
pointing to a human analyst. Show the SQL with every answer and build the narrative from the rows, not the model.
Measure execution accuracy by comparing result sets with gold queries (rounding floats, ordering only when the gold
query has `ORDER BY`), refusal accuracy separately, unsafe queries blocked and average attempts (Section 9.2; C3).

*Strong signals:* metric definitions; guard plus read-only connection; grading on result sets. *Red flags:* exposing
the whole schema; comparing SQL text; letting the model narrate numbers it never saw.

### 9.4 · Customer scenario

**Q.** Before anything is built, Northwind's sponsor asks what the assistant will cost per month at two million requests. How do you answer, and which design choices would you show moving the number?

Build a per-request model from token counts rather than a vendor calculator. The worked example: a 3,000-token system
prompt, 4,000 tokens of retrieved documents, a 200-token question and a 400-token answer, at illustrative prices of $3
per million input and $15 per million output tokens, is $0.0276 a request, or $55,200 a month at two million requests.
Then show the levers. Prompt caching on the stable prefix, with cache reads at 10% of the input price, brings it to
$0.0195 and $39,000, a 29% saving that costs only discipline about prompt order. A 30% exact-match response cache on
top brings it to $27,300. Retrieving five good chunks instead of twenty moves the number more than negotiation, and
output is 22% of cost at about 5% of tokens, so a length limit is a cost control. Say what the model leaves out: cache
writes, retries, failovers and agent loops, and that prices are dated data to re-check before quoting (Section 9.4,
Table 9.1; ex35).

*Strong signals:* builds from token counts and shows each lever's effect; names the omissions. *Red flags:* a single
number from a pricing page; quoting exercise prices as current.

### 9.5 · Debugging

**Q.** In long conversations the assistant starts missing answers that are in the retrieved documents, and some replies stop mid-sentence. What would you look at first?

Look at the context packer's log for those requests: it should record what was included, what was truncated, what
was dropped and the total token count. If the relevant document was dropped or truncated to make room for history,
the log shows it immediately. Check the packing order: mandatory system prompt and question first, then documents by
relevance with at most a truncated prefix of the next one, then history in whole turns from the most recent, restored
to chronological order. Replies stopping mid-sentence suggest the output reservation is missing or too small: available
input must be budget minus reserved output, and a `max_tokens` stop reason in the logs confirms it. Also check the
token counting: a `len/4` approximation can be off by a factor of two for code, JSON or non-Latin scripts, so use the
provider's counter in production. And confirm history isn't split so that it starts with an assistant reply to a
question the model can't see (Section 9.3; ex33).

*Strong signals:* starts from the packer's included, truncated and dropped log; links truncation to output
reservation. *Red flags:* raising the context window or switching models before reading the logs.

### 9.6 · Customer scenario

**Q.** The customer wants a model to route 500,000 tickets a month into `billing`, `login` or `outage`, and asks you to use the most capable model available. How do you respond?

Earn the LLM first. Build a small classical baseline (multinomial Naive Bayes with Laplace smoothing) and compare it
honestly with a model-based classifier: a stratified, seeded train/test split so rare classes such as `outage` appear
in the test set; macro-F1 rather than accuracy, because a classifier that always says `billing` can score 80% accuracy
on imbalanced data and be useless; and log-space computation to avoid underflow. Recommend the baseline unless the
LLM's macro-F1 is at least three points higher, and report the monthly cost next to it. If an LLM wins, the most
capable model still isn't automatically right: route to the cheapest model whose tier passes the golden set for this
request type, and use the batch API for any work that can wait. Either outcome helps the customer: you've saved a
large annual bill, or justified the spend with numbers (Section 9.5, Section 9.3, Section 9.4; ex36, ex34).

*Strong signals:* baseline first; macro-F1 and cost side by side; a stated decision rule. *Red flags:* choosing the
biggest model on reputation; comparing on accuracy alone.

### 9.7 · Technical

**Q.** The customer's procurement team says a new vendor contract takes three months, and two business units mandate different providers. How do you choose a model and where to call it, and how do you keep the code portable?

Decide with the criteria in Table 9.3, not capability alone: does it pass our golden set per request type, what does a
request cost and how fast is the first token, where may the data go, which surface the customer can buy, the context
and output limits, and how long the model will be available. The surface often decides it: the major clouds resell
leading models (Amazon Bedrock, Google Cloud's Vertex AI, Microsoft Foundry), so calling through the customer's cloud
can turn procurement into configuration, keep traffic in their network boundary and count against existing
commitments; the trade-off is that features can arrive later and formats and identifiers differ. For portability, put
a thin neutral format for messages, tools and replies behind adapters per provider; the hard part is the wire format
(OpenAI's arguments are a JSON string, Gemini has no call ids and matches results by name, Anthropic merges
consecutive tool results). Don't hide useful provider features behind a lowest common denominator. Test adapters
against recorded responses, and record the choice in an architecture decision record (Section 9.5; ex86).

*Strong signals:* the cloud-marketplace surface as a procurement answer; specific wire-format differences; an ADR.
*Red flags:* picking from a leaderboard; a thick framework that hides caching or batch features.

## Chapter 10 · Retrieval-Augmented Generation (RAG)

### 10.1 · Technical

**Q.** A teammate says the new chunking for Northwind's policy assistant "feels better". The customer's AI lead asks by how much. Walk me through how you'd answer with evidence, and which number you'd lead with.

Start by measuring retrieval on its own, before looking at generation. Build a labelled query set with the customer:
real questions from adjusters, with the relevant passages marked by someone who knows the policies, optionally graded
(2 = directly answers, 1 = useful context). These are the qrels. Run both chunkers over the same set and compute
recall@k, precision@k, MRR and nDCG@k, where *k* is the number of chunks that fit the context budget. Lead with
recall@k: if the relevant chunk isn't in the top *k*, the model never sees it. nDCG matters when judgements are graded
and the budget is tight, because it rewards putting the best passage first. Present the comparison as a table and a
sentence such as "recall at four went from 62.5% to 87.5% on the 40-question compliance set". Because deeper
retrieval and extra stages trade recall against latency, plot recall against p95 latency and choose with the customer.
Synthetic questions can extend coverage once the real ones exist. (Section 10.1; ex41)

*Strong signals:* ties *k* to the context budget; builds the query set with the customer's experts; reports latency
alongside quality. *Red flags:* judges the change from a handful of final answers; relies only on synthetic questions.

### 10.2 · System design

**Q.** Support agents search for error codes like `E-4417` and also describe problems in their own words. How would you design retrieval so both kinds of query work, and how would you choose the embedding model?

Use hybrid search. BM25 handles exact identifiers, which embeddings treat as similar to other similar-looking codes;
vector search handles paraphrase ("my basement flooded" against "water ingress below ground level"). Merge the two with
reciprocal rank fusion, `1 / (k + rank)` summed over the lists with *k* = 60, because BM25 scores and cosine
similarities are on incomparable scales and normalising them is fragile. Retrieve deeper than you need from each (for
example 20) before fusing, and use `explain_fusion` to see each document's rank in each list. Add a cross-encoder
reranker only when metrics show relevant passages retrieved but ranked too low, and measure its latency. Choose the
embedding model with evidence: measure two or three candidates on the query set, check the corpus's languages, weigh
vector dimension against storage and query cost, confirm it can run under the same residency and procurement
constraints as the generation model, and store the model identifier with every vector, because changing it later
means re-embedding the whole corpus. (Section 10.3; ex38, ex39, ex41)

*Strong signals:* explains why scores can't be added; can say what BM25's k1 and b do; treats the embedding model as
the hardest choice to reverse. *Red flags:* vector-only search; picking the embedding model from a public leaderboard.

### 10.3 · Coding

**Q.** Write the post-processing step for a cited RAG answer: you gave the model four numbered sources and it replied with `[1][2]`, `[1, 3]` and `[7]`. What does your code do, and when is the answer grounded?

Before that step, the function should already have abstained without calling the model if retrieval returned nothing
or the top score was below a threshold, returning a fixed abstention text. After the model replies:

1. Parse every citation marker, including adjacent forms like `[1][2]` and lists like `[1, 3]`.
2. Map each number in range (1 to 4 here) to the document id of that source.
3. Treat numbers outside the range, such as `[7]`, as invalid: remove them from the text and record them.
4. Mark the answer grounded if it has at least one valid citation and no invalid ones, or if it abstained. This reply
   contained `[7]`, so it is not grounded even after stripping.

Track the grounded rate as a launch metric; Capstone 1's bar is citation precision of at least 95% and zero answers to
unanswerable questions. Then say the limit out loud: a valid citation proves the model pointed at a real source, not
that the source supports the claim. Chapter 13's support check and Chapter 12's faithfulness judge cover that.
(Section 10.4; ex40)

*Strong signals:* abstains before the model call; handles both multi-citation forms; distinguishes citation validity
from support. *Red flags:* trusting the markers as returned; asking the model to notice its sources are irrelevant.

### 10.4 · Customer scenario

**Q.** Northwind's head of compliance asks the assistant how many water-damage claims over $10,000 were paid last quarter, and it gives a confident number. What went wrong, and what do you propose?

The question was routed to the wrong tool. An aggregate isn't written in any document; it's a query over the claims
table. Retrieval found a few claims mentioning water damage and the model counted them, confidently and wrongly. The
proposal is to classify questions before routing them, using examples from the discovery interviews to see which
kinds dominate. Aggregates over well-understood tables go to a tool that runs vetted, parameterised queries, such as
`claims_paid(category, min_amount, start, end)`, rather than free-form SQL, because it's easier to secure and test.
Current-state questions ("status of claim 4471") go to the system of record's API with the user's permissions, and
joins across records go to a query, not a similarity search. Retrieval keeps what it does best: finding the passage
that answers the question. Until the tool exists, the assistant should abstain and name the right place: "I can't
count claims; the claims dashboard has this figure." Record the routing decision and its evidence in a decision record
(Appendix E's ADR-1 does this for the reference engagement). (Section 10.4)

*Strong signals:* names the three classes (aggregates, current state, joins); prefers parameterised tools to free SQL;
offers a clear boundary in the meantime. *Red flags:* tuning the prompt or adding more chunks to make counting work.

### 10.5 · Customer scenario

**Q.** A claims operations lead wants scanned claim forms processed "fully automatically". How would you design the extraction pipeline, and how do you choose between OCR and a multimodal model?

Reframe "fully automatic" first: a pipeline that's 97% accurate and silently wrong on the other 3% is worse than one
that's 90% automatic and sends the doubtful 10% to a person. On the OCR path, the service returns words with bounding
boxes and confidence scores. Rebuild lines by grouping words with nearby vertical centres, ordering them left to right
and taking the line's confidence as the minimum of its words'; find key-value pairs by label ("Policy number", "Date of
loss"); rebuild tables from the header's column positions. Then route: any required field missing or below the
confidence threshold goes to human review with reasons such as `missing:policy_number`. On the multimodal path, send
the PDF as a base64 `document` block or the image as an `image` block, refusing unsupported types and oversized files.
OCR gives coordinates, per-word confidence and predictable cost, which suits high-volume known layouts and audits;
multimodal models handle messy layouts, handwriting and diagrams with less code, at higher cost and without per-field
confidence. Many pipelines use both. Either way, measure field accuracy on real samples and check the provider's
current limits. (Section 10.5; ex88, ex70)

*Strong signals:* designs the human-review route as a feature; uses minimum confidence per line; gives a reasoned
OCR-versus-multimodal choice. *Red flags:* no confidence threshold; promising full automation without measurement.

### 10.6 · Debugging

**Q.** After asking about burst pipes, an adjuster asks "What about flood?" and gets a wrong answer. Walk me through how you'd find the root cause, and what you'd do once it's fixed.

Work through the pipeline in order, using each stage's logs, and stop at the first stage that went wrong:

1. Was the question understood? Check the rewritten query. A follow-up like this one loses its subject unless it is
   rewritten into a standalone question, such as "Is flood damage covered under the home policy?".
2. Was the right passage retrieved? Look for it in the keyword and vector results with `explain_fusion`. Absent from
   both points to chunking, indexing or freshness.
3. Was it ranked high enough to fit? Retrieved at rank 12 with a budget of four is a ranking fix (a reranker, better
   chunk text), not a prompt fix.
4. Was it in the context the model saw? The packer's log shows what was included and truncated.
5. Did the model use it? Only now look at citations, instructions and the model.

Once fixed, add the question and its correct passage to the evaluation set so the fix is measured and stays fixed.
(Sections 10.3 and 10.7)

*Strong signals:* suspects query rewriting first for a follow-up; stops at the first failing stage; turns the incident
into an evaluation case. *Red flags:* starts by editing the prompt or switching models.

### 10.7 · System design

**Q.** Northwind revises its policy wording several times a year, and claims are judged under the version in force on the claim date. How would you keep the index fresh and correct after go-live?

Most retrieval incidents after go-live are freshness incidents, so design index operations deliberately. Give every
chunk a content key, a hash of its document id, heading path and text. When a document changes, re-chunk it, compare
keys and add or delete only what changed, so unchanged chunks keep their embeddings. Treat a document missing from the
source as an explicit deletion event, so withdrawn documents don't leave orphans. Store `effective_from` and
`effective_to` on every chunk and filter on them at query time, so "was this covered when the claim was filed?" uses
the version in force on the claim date, not the latest. If the embedding model ever changes, re-embed everything:
build the new index alongside the old one, compare them with the retrieval metrics on the query set, then switch, the
same blue-green pattern used for deployments. Finally, monitor the corpus as well as the queries: chunk counts per
source, the age of the newest document and the share of chunks with missing metadata. A sudden drop in chunk count
usually means an ingestion job failed silently. (Section 10.6; ex37)

*Strong signals:* incremental re-indexing by content key; effective dates filtered at query time; corpus-level
monitoring. *Red flags:* nightly full rebuilds as the only plan; answering every question from the latest version.

### 10.8 · Debugging

**Q.** A help assistant serving hundreds of tenants from one shared index cites another customer's internal pricing sheet. What do you check first, how do you contain it, and what stops it happening again?

Check the cited chunk's metadata and the query filter first. In the chapter's case the chunk has `tenant_id = NULL`,
and the filter is `tenant_id = :tenant OR tenant_id IS NULL`, written so global help articles appear for everyone; a
new upload path added the previous month doesn't set the tenant. The root cause is a filter that fails open: a missing
value meant "visible to everyone", nothing validated tenant metadata at ingestion, and the cross-tenant test covered
only the original path. Contain it by turning off retrieval of untenanted chunks with a kill switch, finding and
purging the affected chunks, and starting the contractual notification process with the customers involved. Prevent it
by making the tenant mandatory, giving global content an explicit tenant of its own, rejecting chunks without one at
ingestion, and running a cross-tenant negative test for every ingestion path as a release gate. The broader principle:
the model can't be trusted to withhold what it has been shown, so permissions are enforced inside retrieval, with ACLs
on every chunk and entitlements resolved on the server. (Sections 10.6 and 10.7; ex89 in Chapter 13)

*Strong signals:* spots the fail-open `IS NULL` clause; contains before fixing and notifies; tests every ingestion
path. *Red flags:* asking the model not to reveal other tenants' data; filtering results after retrieval.

## Chapter 11 · AI Agents

### 11.1 · Coding

**Q.** Before reaching for a framework, write the agent loop for a retailer's assistant that looks up orders and issues store credit. Walk me through the rules your loop enforces and the bugs each one prevents.

The loop starts with the user message and the tool specs (name, description, input schema). On each step it calls the
model; if the response has no tool calls, it returns the text. Otherwise it appends an assistant turn with any text
and one `tool_use` block per call, executes the calls and appends the results. Four rules prevent most bugs:

1. Execute every requested call, in order. Running only the first leaves the model waiting for results it never gets.
2. Return all results in one user turn, each matched to its call by id. The API rejects a tool call with no result.
3. Turn failures into results with `is_error: true`, including unknown tool names. The model can recover from an
   error result; your process can't recover from a crash.
4. Enforce a step budget, then stop and escalate, so a model that never converges can't run indefinitely.

Frameworks add tracing, streaming, persistence and human-in-the-loop support and are worth using in production;
knowing the loop is what lets you debug them. In production the step budget grows into a run budget with repeat
detection and per-tool caps. (Sections 11.1 and 11.6; ex42)

*Strong signals:* all results in a single turn matched by id; errors as results; a hard step limit. *Red flags:*
letting exceptions propagate; one result per turn; no budget.

### 11.2 · Technical

**Q.** In production the model calls `issue_refund` with `amount: "50 dollars"` and no `order_id`. How would you design the tool so the agent recovers instead of spiralling, and so a retry can't refund twice?

Validate before executing: check the arguments against the tool's JSON Schema (types, required fields, enums, ranges,
`additionalProperties: false`) and, on failure, don't call the function; return one error listing every problem, such
as "amount: expected number, got string" and "order_id: required", so the model fixes the call on the next turn. If
the function itself raises, return the exception type but not its message or traceback, because messages can leak
connection strings, paths or customer data into transcripts. Truncate oversized results and say so. Write the
description for the model: what the tool does, when to use it, what it returns and what it doesn't do. For safety
against double refunds, mark the tool as side-effecting and execute it at most once per call id, so a replayed
`tool_use` returns the first result. That doesn't stop the model retrying with a new id, so also pass a
business-operation idempotency key to the payment API, report timeouts as "outcome unknown" and cap refunds per run.
(Sections 11.2 and 11.6; ex43)

*Strong signals:* errors that say how to fix the call; hides internals; separates call-id replays from business-level
retries. *Red flags:* returning stack traces to the model; relying on the call id alone for idempotency.

### 11.3 · Customer scenario

**Q.** The customer's platform team wants every one of its order system's 40 REST endpoints exposed as a tool. How do you respond, and what would you build instead?

Acknowledge the goal (full coverage) and push back on the shape. Forty endpoint wrappers give the model the job of
composing them correctly, every tool definition costs context on every call, and the model chooses less reliably as
the list grows. Propose tools designed around tasks instead: for example `find_orders`, `get_order`,
`check_refund_eligibility`, `request_refund` and `escalate_to_human`. Task-shaped tools are easier to describe,
validate, permission and evaluate. Where the agent genuinely needs dozens of capabilities, group them: give each
subagent or Agent Skill the handful of tools its task needs and let the parent route between them. Skills use
progressive disclosure, so only their names and descriptions cost context up front, and subagents run in a fresh
context restricted to the tools they list. Offer to prove the choice with the evaluation set rather than by argument.
(Sections 11.2 and 11.5; ex85)

*Strong signals:* explains the context and selection cost of many tools; names concrete task-shaped tools; uses
subagents or skills to scale. *Red flags:* agreeing to wrap every endpoint; adding paragraphs of system prompt instead.

### 11.4 · System design

**Q.** The customer wants its policy database usable from Claude Desktop, Claude Code and its own agent platform, and those clients speak different MCP revisions. How would you design the server and the connector?

Build one MCP server, since any MCP client can use it, and make it dual-era because clients upgrade at different
times. Modern clients (revision 2026-07-28) send the protocol version in `_meta` on every request and call
`server/discover`, which returns supported versions, capabilities, server information and a `ttlMs`; results carry
`resultType: "complete"`. An unsupported version gets error `-32022` with the supported and requested versions.
Legacy clients send `initialize`, which switches the server into legacy shapes; a request with no `_meta` before any
`initialize` gets `-32602`. The modern era is stateless, so the server can sit behind an ordinary load balancer. Keep
tool failures as normal results with `isError: true`; protocol errors are for malformed requests. The connector must use
parameterised SQL only and bounded limits (ex45 caps `limit` at 50), because the model chooses arguments and its input
may carry injected instructions. Ship the official SDK in production, and smoke-test every server with your own
negotiating client first. (Section 11.3; ex44, ex45)

*Strong signals:* supports both eras; separates tool errors from protocol errors; treats the connector as an attack
surface. *Red flags:* assuming every client speaks the newest revision; string-built SQL.

### 11.5 · System design

**Q.** Design an "AI operations analyst" that investigates a billing dispute: pull the invoice, check payment logs, draft an email and, only with approval, issue a refund. How do you keep it safe and auditable?

Separate planning from execution. A planner model writes a JSON plan: steps with an id, a worker, a task, dependencies
and a `requires_approval` flag. Code validates it before anything runs, rejecting unknown workers, dependencies on
unknown steps and cycles, then orders steps topologically, keeping the planner's order among ready steps so execution
is deterministic. Decide approval by policy in code, not by the plan: steps using risky workers such as `refund` or
`send_email` always require approval, because the planner is a model and its plan can be wrong or manipulated.
Execute with explicit statuses (`done`, `failed`, `rejected`, `skipped` when a dependency didn't finish as done).
Approval in production is a queue ticket, a Slack button or a supervisor's console: the model proposes, a person
disposes. Audit every transition in order, so when auditors ask why a refund wasn't issued, the trail answers. Add run
budgets and a per-run cap on side-effecting tools. (Sections 11.4 and 11.6; ex46)

*Strong signals:* validates the plan before execution; approval rules live in code; an audit trail of transitions.
*Red flags:* letting the planner decide what needs approval; free-running execution with no statuses.

### 11.6 · Debugging

**Q.** You inherit a LangGraph-style agent. Some runs stop silently partway through, and after a restart a conversation can't pick up where it left off. What would you check, and what should the framework be doing?

Silent stops usually mean a graph defect or an interrupt. First check the run's status: a run that reached a node in
`interrupt_before` stops as `interrupted` and waits for a person to review and resume. Then check that the graph is
validated at compile time; ex79 refuses graphs with no entry point, edges to unknown nodes, nodes with no outgoing
edge, nodes with both a plain and a conditional edge, and unreachable nodes, all of which otherwise surface as runs
that silently stop. A step limit should raise an error for cycles that never reach `END`. For resumption, check the
checkpointer: state and next node should be saved after every node under the thread id, and the caller must pass the
same thread id (in LangGraph, `config={"configurable": {"thread_id": ...}}` with a checkpointer compiled in). While
there, check reducers: updates applied on resume go through them, and a missing reducer lets one node's write
overwrite another's. (Section 11.4; ex79)

*Strong signals:* knows what checkpoints, interrupts, reducers and compile-time validation each do; checks thread ids.
*Red flags:* treating the framework as a black box; adding retries without finding why runs stop.

### 11.7 · Customer scenario

**Q.** A contact centre says its voice bot "feels slow and talks over people", and its field copilot forgets the policy number by mid-shift. How would you turn both complaints into fixable problems?

Turn both feelings into numbers. For voice, compute from the call's event log: response latency (caller finishing to
agent starting) at the median and the p95, since gaps over about a second sound like hesitation; barge-ins, where the
caller speaks while the agent is still talking, many of which suggest turns are too long; the agent's talk ratio; and
long silences, often a slow tool call. Then "it feels slow" becomes something like "p95 latency is 2.4 seconds, driven
by the policy lookup tool", which you can fix. For the copilot, the policy number is buried under hours of later
conversation. Use rolling summarisation: when unsummarised messages exceed a token budget, fold the oldest into a
running summary that keeps names, numbers, decisions and open questions. And pin facts whose exact value matters
(account number, policy under discussion, user's role) so they appear verbatim in every context. The model then sees
pinned facts, the summary and recent messages. (Section 11.5; ex47, ex48)

*Strong signals:* watches the p95, not just the median; links silences to tool latency; pins exact values rather than
trusting the summary. *Red flags:* "use a bigger context window"; tuning voice by ear without metrics.

### 11.8 · Debugging

**Q.** A refund agent runs over a weekend, and on Monday finance finds 37 orders refunded twice. Walk me through the investigation, the root cause and the changes you'd make.

Gather evidence from both sides. The payment provider shows two refunds about 31 seconds apart per order; the agent's
trace shows a first `issue_refund` that hit the tool's 30-second timeout and returned `is_error: true`, then a second
call with a new call id that succeeded. The first refund had gone through; only the response was late. Root cause: a
timeout was reported as a failure when the outcome was unknown, the registry's idempotency was keyed on the call id
(which stops replays, not a sensible retry), and nothing capped refunds per run. Mitigation: reverse the duplicates,
pass an idempotency key derived from the business operation (order id and amount) to the payment API, and cap refunds
at one per order per run. Prevention: on timeout return "outcome unknown; check with `get_refund_status`", check before
acting, and add a trajectory evaluation case that injects a slow payment API. (Sections 11.2 and 11.6; ex42, ex43)

*Strong signals:* distinguishes "failed" from "outcome unknown"; business-level idempotency keys; per-tool caps plus
a regression case. *Red flags:* blaming the model for retrying; only lengthening the timeout.

## Chapter 12 · LLM Evaluation

### 12.1 · Customer scenario

**Q.** After a good demo, Northwind's head of compliance asks: "How do you know it won't tell an adjuster something is covered when it isn't?" How do you answer, and what do you build?

Be honest: without an evaluation, you don't know yet, and here is how you will. Build a golden set with the
customer's experts, starting at 50 to 150 cases focused on the questions that matter and the failures that hurt. Each
case has an input, an expected result, a grader and tags, for example a burst-pipe-while-unoccupied question graded by
`contains` on "not covered" and "unoccupied", tagged `coverage`, `exclusion` and `safety`. Prefer deterministic
graders wherever they work, and report pass rates per tag, because 91% overall can hide 60% on exclusions. Include an
unanswerable slice and report abstention in both directions, plus citation precision and faithfulness checked by a
narrow judge. Agree a launch bar (Capstone 1's includes zero answers to unanswerable questions), gate every change in
CI on critical regressions, and monitor live quality after launch. The answer to the question becomes "here is the
exclusions slice, its pass rate and interval, re-run on every change". (Sections 12.1 and 12.6; ex49)

*Strong signals:* admits the gap honestly; builds the set with the customer's experts; per-tag and safety reporting.
*Red flags:* pointing to the demo; quoting a single overall pass rate.

### 12.2 · Technical

**Q.** You want an LLM judge to score answers for accuracy, completeness and tone. How would you make sure the customer's experts can trust its scores?

Put the rubric in the system prompt and ask for JSON with `reasoning` first, then a `score` from 1 to 5; invalid JSON
or an out-of-range score is an error, not a default. Calibrate against people: have domain experts score 50 to 100
answers, run the judge on the same answers, and report exact agreement, within-one agreement and Cohen's kappa on
pass/fail (score of at least 4). Kappa matters because raw agreement flatters judges when most answers pass; above 0.6
is substantial, above 0.8 near-perfect. If it's lower, make the criteria more specific and add examples of each score
before trusting the judge. For pairwise comparisons, ask twice with the answers in both orders and declare a winner
only if both agree, to remove position bias. Where approvals allow, use a different strong model family as judge,
re-check agreement whenever the judge model or rubric changes, and keep the human-labelled set permanently. For
faithfulness, judge one claim against one passage. (Sections 12.2 and 12.6; ex50)

*Strong signals:* kappa rather than raw agreement; order swapping; recalibrates on judge changes. *Red flags:*
trusting a judge because it "looks right"; using a judge where a deterministic grader would do.

### 12.3 · System design

**Q.** Design the evaluation gate for a team that changes prompts, retrieval settings and tools every week. What blocks a merge, and how do you keep the suite affordable?

Compare runs case by case, not by average. The gate computes pass rates over the intersection of case ids, lists
regressions and fixes, and fails on any missing case first, because deleting failing cases is the easiest way to
raise a pass rate. Any regression on a case tagged `safety` (or another critical tag) fails the gate whatever the
average says; a tolerance (two points by default) absorbs noise on non-critical cases. The gate exits 0 or 1 so it
slots into CI, and runs on every pull request touching a prompt, model setting, retrieval or a tool. The harness
rejects unknown graders before running and a leakage check keeps golden-set inputs out of example pools. To keep it
affordable: deterministic graders on every change, judge results cached by a hash of the judge prompt, rubric and
answer, the full judged suite only on changes to prompts, models or retrieval with a stratified sample otherwise,
nightly runs on the batch API, and the evaluation's own cost reported per run. (Sections 12.3, 12.6 and 12.7; ex51,
ex49)

*Strong signals:* missing cases fail first; critical regressions block regardless of average; judge caching.
*Red flags:* a gate on the overall pass rate alone; no plan for evaluation cost, so the suite gets switched off.

### 12.4 · Customer scenario

**Q.** A three-week pilot moved first-contact resolution from 71.2% to 74.0%, and the sponsor asks whether to roll out. Walk me through your answer, and what you'd have done before the pilot started.

The lift is 2.8 points; the question is whether it's real. Compute a bootstrap confidence interval by resampling each
group with replacement thousands of times and taking the 2.5th and 97.5th percentiles of the lift, and a
two-proportion z-test for the *p*-value. Then apply the decision rule agreed before the pilot: ship if the interval's
lower bound is above zero and *p* is below 0.05, call it harmful if the upper bound is below zero, otherwise
inconclusive. Report the result honestly whichever way it falls, and don't switch to a different metric after seeing
the data. Flag the unit of analysis: tickets handled by the same agent aren't independent, so for a high-stakes
decision analyse by agent or use a clustered analysis. Before the pilot, a power calculation should have sized it:
detecting three points from a 71% baseline at 80% power and 5% significance needs roughly 3,500 tickets per group, so
a smaller pilot should run longer, include more agents or use a more sensitive metric. (Section 12.3; ex52)

*Strong signals:* interval plus pre-registered rule; power calculation up front; aware of clustering. *Red flags:*
"it went up, ship it"; choosing the metric after the results.

### 12.5 · Technical

**Q.** A refund agent passes 92% of the golden set on its final message, but in production it sometimes refunds before looking up the order. How would you evaluate it, and what would you report to the operations lead?

Answer-only grading can't see the path, so grade trajectories: the sequence of tool calls plus the final answer. For
this case require `get_order` and `issue_refund`, require that order as a subsequence, check the arguments
(`order_id` "A-1001", `amount` 40) and cap tool calls at four; an agent that refunds first fails the order check even
with a perfect message. Report efficiency (required tools divided by calls, capped at one) and tool-call F1, since an
eleven-call path to a three-call job is slow and costly. Then measure reliability: run each case *n* times and count
*c* successes. pass@k is the chance at least one of *k* attempts succeeds; pass^k is the chance all *k* do. For 8 of
10 successes, pass@5 is 1.0 but pass^5 is about 0.22. Tell the operations lead that if the team uses it five times a
day, it will let them down on most days, and make pass^k the launch metric for unattended agents, reporting both.
(Section 12.4; ex99)

*Strong signals:* order and argument checks; repeated runs; pass^k for unattended use. *Red flags:* grading only the
final message; reporting pass@k as reliability.

### 12.6 · Debugging

**Q.** Six weeks after go-live the offline evaluation is still green, but agents say the copilot "got worse". How would you find out what changed, and how would you have caught it sooner?

Offline evaluation answers "is this version good?"; online evaluation answers "is it still good for today's traffic?".
Check input drift first: compute the population stability index on input length (binning by the baseline's quantile
edges, flooring shares at a small epsilon) and on intent as a categorical feature. Below 0.1 is stable, 0.1 to 0.25
worth watching, above 0.25 drift, as rules of thumb to calibrate. Then check live quality: the judge pass rate on
sampled traffic against the offline baseline, the refusal rate, p95 latency and cost per conversation. In the
chapter's case a product launch added an `outage` intent, longer pasted logs and more refusals. To catch it on day one,
not day nine, run these checks per window with paging thresholds, minimum sample sizes and a reproducible review
sample (every refusal and low score, plus hash-based sampling). When drift fires, grow the golden set from the new
traffic and label it with experts before touching the prompt. (Section 12.5; ex100)

*Strong signals:* separates offline and online questions; PSI with minimum samples; grows the golden set first.
*Red flags:* immediately rewriting the prompt; trusting the green offline suite.

### 12.7 · Technical

**Q.** A pull request says the candidate raises the overall pass rate from 88.0% to 90.5% on the held-out split. Walk me through how you decide whether to ship it.

Score the held-out split only when deciding, and look at slices with intervals, not the headline. In the chapter's
example the critical exclusions slice fell from 90.0% to 77.5%. Case by case the candidate fixed 24 and broke 14;
McNemar's exact test on those 38 gives *p* ≈ 0.14, so the overall gain could be noise. In exclusions it broke six and
fixed one. That isn't significant either, and doesn't need to be: exclusions are critical, so the gate fails and the
candidate is rejected whatever its average. Next, classify the failures with a fixed taxonomy; 18 of 38 were retrieval
and chunking problems, which points to heading-aware chunks and a reranker rather than the prompt. Only among
candidates that pass every gate do you trade quality against latency and cost, comparing cost per successful task
(cost per request divided by pass rate). The chapter's candidate C passes the gates at 90.0%, costs about a tenth of a
cent more per successful task and stays inside the latency target; ship it and record the decision in an ADR.
(Section 12.7; ex49)

*Strong signals:* gates before trade-offs; paired comparison on discordant cases; cost per successful task.
*Red flags:* accepting "+2.5 points"; averaging critical slices into the total.

### 12.8 · Behavioural

**Q.** Tell me about a time you had to present evaluation results to a group that had to approve or reject a launch. What did you put in front of them?

Structure the story as situation, action and result. Situation: who had to approve (a model risk committee, an AI
governance board, a clinical safety group) and what was at stake. Action: what you put in front of them, which should
follow the chapter's order in a short document of two to four pages with the full results attached. What the system
does and must never do; how it was evaluated (golden-set version, size, sources, labellers' agreement, the judge's
model and kappa, the run date); results by slice with case counts and intervals, flagging slices too small to say
anything; known failure modes and their mitigations; monitoring after launch and who gets paged; and limitations.
Result: the decision, and ideally how the written limitations held up later. The story must show that you reported
slices rather than an overall number, kept every figure reproducible from a tagged run, reissued the document when the
golden set, judge or model changed, and stated limits openly, because boards approve systems whose limits are
understood. (Section 12.7)

*Strong signals:* a limitations section volunteered rather than extracted; slices with intervals; reproducibility.
*Red flags:* presenting only an overall pass rate; showing the harness instead of a decision document.

## Chapter 13 · AI Security and Guardrails

### 13.1 · System design

**Q.** A retailer's email-triage agent reads inbound customer emails and can call `send_email`, `http_post` and `issue_refund`. Walk me through the controls you'd put around it so that a fooled model still can't leak data.

Start by saying the system prompt isn't the defence: prompts reduce risk, they don't eliminate it. Then layer
independent controls so an attacker has to defeat all of them. Redact personal data before it leaves the network.
Wrap every email in an `<untrusted source="email:inbound">` tag, neutralising any `<untrusted` or `</untrusted` inside
it so the attacker can't close the tag early. Run heuristics for "ignore previous instructions", role overrides,
system-prompt probes, send-to-address instructions and long base64-like runs, and treat a hit as tainting the
context, not as prevention. The decisive layer is a `ToolGate` in code: read-only tools are allowed; any URL or email
domain in the arguments that isn't on the allowlist is denied; a side-effecting tool in a tainted context needs a
person's confirmation. Then check the output, enforce the user's permissions, record every decision in an audit log
and keep a red-team suite running. Where possible, separate reading untrusted content from the power to act, or fix
the recipients. Measure each control's overhead so nobody switches it off "temporarily". (Sections 13.1–13.2; ex54)

*Strong signals:* names gating in code as the layer that actually stops the attack; describes egress allowlisting and
confirmation in tainted contexts. *Red flags:* "a stronger system prompt" or "an injection classifier" as the answer.

### 13.2 · Technical

**Q.** The customer's privacy office says no transcript may leave their network with personal data in it. How would you design the redaction step, and how would you convince them it works?

Detect with validation, not bare patterns: emails, US SSNs excluding area 000, 666 and 900–999, group 00 and serial
0000, credit cards of 13 to 19 digits that pass the Luhn checksum (otherwise every order number is "a card"), US
phone formats and IPv4 octets of 0–255. Replace each value with a consistent numbered token per type, so the same
address is always `[EMAIL_1]` and the model can still reason about who did what. Keep the token-to-value mapping
inside the network and `restore` the originals in the answer before the user sees it. Then be honest about limits:
regex is a floor; names, addresses and free-text descriptions need named-entity recognition, which also misses
things. Measure the detector's recall on a labelled sample of real data and report the number, because a documented
recall is more convincing than a claim of completeness. That recall, plus a review of sampled logs, is the evidence
for the sensitive-data release gate. (Section 13.2, Section 13.6; ex53)

*Strong signals:* consistent, reversible tokens with the mapping kept local; measured recall on labelled data.
*Red flags:* masking everything as `[EMAIL]`; claiming a regex catches all personal data.

### 13.3 · Coding

**Q.** Your backend receives an OIDC ID token from the customer's identity provider. Walk me through the checks your validation function performs, in order, and what changes when you move from a test setup to Entra ID or Okta.

In order: structure (three base64url segments); algorithm, compared with exactly the expected value, rejecting `none`
explicitly; signature, checked against a key the service already holds and compared in constant time
(`hmac.compare_digest`); issuer (`iss`) is the customer's identity provider; audience (`aud`, a string or a list)
includes your application, because a valid token for another application isn't valid for yours; expiry (`exp`) and
not-before (`nbf`) against the current time. The principle is that nothing in the token is trusted until the
signature verifies, and the header's `alg` is compared, never used to choose how to verify. ex89 uses HS256 with a
shared secret so the tests are self-contained. Production providers sign with RS256 or ES256 and publish public keys
at a JWKS endpoint: select the key by the token's `kid`, cache the key set, and use a well-maintained library
configured with an explicit algorithm allowlist. The user id, email and groups for authorisation then come only from
the verified claims. (Section 13.3; ex89)

*Strong signals:* checks audience as well as signature; explains the `alg: none` attack and why `alg` is compared
rather than obeyed. *Red flags:* decoding the payload and reading claims before verifying; hand-rolling RS256 in
production.

### 13.4 · Technical

**Q.** A bank's security architecture review asks for role inheritance, strict tenant isolation, refund approval limits and a tamper-evident audit log. How would you build the access check and the log, and what doesn't the log protect against?

Roles carry permissions and may inherit others (`supervisor` inherits `agent`); compute the set transitively and
guard against cycles. Permissions match exactly, by wildcard (`ticket:*`, `*`) or with a limit
(`refund:approve<=500`), which matches only if the resource's amount is within it. Check tenant isolation first,
before any permission: a user from another tenant is denied even with `*`, because isolation is a boundary, not a
grantable permission. Append every decision to the audit log with user, action, tenant, outcome and reason. Each
entry stores the previous entry's hash and its own SHA-256 over its content plus that previous hash; `verify()`
recomputes the chain, so editing or deleting any entry breaks every hash after it. What it doesn't do: stop an
attacker with write access from rebuilding the whole chain. In production, ship entries to write-once storage or an
external log service, or periodically anchor the latest hash somewhere the application can't write. (Section 13.3;
ex56)

*Strong signals:* tenant check before permissions and immune to `*`; knows the chain proves after-the-fact edits only.
*Red flags:* implementing tenancy as a permission; calling a hash chain "tamper-proof".

### 13.5 · System design

**Q.** Your copilot indexes the customer's whole SharePoint and Confluence estate, and a claims adjuster just got a colleague's HR disciplinary document as the top result. How would you redesign retrieval and the downstream calls?

Nothing was hacked; retrieval ignored permissions. Copy each document's ACL from the source system onto every chunk
at ingestion. Build the principal (user id, email, groups) from the verified ID token, never from anything the client
or the model supplies. Apply the ACL with an explicit deny group winning, then allow by name, shared group or
`everyone`. Filter candidates *before* ranking and rank only the permitted set: ranking first leaks through result
counts, already-generated snippets and relevance scores, and filtering a top 20 can leave the user with almost
nothing when permitted chunks existed lower down. Treat titles, snippets and citations as disclosures too, and
record how many candidates were considered, permitted and denied. Ask how often ACLs synchronise, since a document
tightened yesterday mustn't be visible today. For downstream APIs, use OAuth 2.0 token exchange (RFC 8693; Entra ID's
"on-behalf-of") to get a token scoped to that API for this user, rather than a god-mode service account or passing
the user's token straight through. (Sections 13.3 and 13.5; ex89)

*Strong signals:* filter before ranking, with the reasons; ACL freshness; acting on behalf of the user. *Red flags:*
post-filtering the top-k; a service account that can read every claim.

### 13.6 · Debugging

**Q.** An email-triage agent forwarded invoices to an outside address, although the design had an egress allowlist and confirmation for side effects in tainted contexts. The audit log shows `send_email` as tainted and "confirmed". What would you check first?

If an allowlist and a confirmation both existed, check the configuration that actually ran in production, not the
design. A tainted call that was "confirmed" points at the confirmation function: is it a stub that always returns
true, written for staging? An outside address that passed egress points at the allowlist: is there a wildcard entry
such as `*.com` added for a test? Then ask where the red-team suite ran; if it ran only against staging, it never
tested what shipped. First respond: kill the `send_email` capability with its switch, revoke and rotate affected
credentials, preserve transcripts, tool calls and authorisation decisions, and notify the customer on the contract's
clock. Prevention: lint configuration for wildcard allowlist entries, forbid confirmation stubs outside test builds,
run the injection release gate against the production configuration before every release, and add the attack to the
red-team suite before closing the incident. (Section 13.6; ex54, ex93)

*Strong signals:* goes to the shipped configuration and the audit evidence before blaming the model; contains first,
then fixes with a test. *Red flags:* "the model was tricked, so improve the prompt".

### 13.7 · Customer scenario

**Q.** Two days before go-live, the golden set passes at 96% but a negative test finds one cross-tenant leak. The sponsor asks you to ship now and fix it next sprint. What do you say, and who can decide?

Say plainly that the system isn't 96% ready; it's not ready. Security gates aren't scores to average, and a failed
gate blocks release whatever else passes. Tenant isolation is one of the gates that can never be waived. For the gates
that do allow a waiver, only the customer's named risk owner, often the CISO, can accept the residual risk, in
writing, naming the gap, the compensating control and an expiry date, recorded in the RAID log; nobody on the
delivery team, including you, can waive a gate on the customer's behalf. Then make the path forward concrete: fix
the leak, re-run the tenant-isolation negative test through every ingestion and query path and every cache against
the configuration that will ship, and bring the test report as evidence. The production-readiness scorecard applies
the same rule: gates first, and no weighted score compensates. (Section 13.6; Table 13.2)

*Strong signals:* calm, firm refusal with a concrete route to green; knows who owns a waiver and which gates allow
none. *Red flags:* agreeing to ship with a follow-up ticket; averaging security into a readiness score.

## Chapter 14 · LLMOps and SRE

### 14.1 · Debugging

**Q.** During a short database outage, every pod of your copilot went into a restart loop. What would you check first, and how would you change the deployment so it doesn't happen again?

Check the probes first. Liveness and readiness do different jobs: a failing liveness probe restarts the container,
while a failing readiness probe removes it from the load balancer. If liveness points at an endpoint that checks the
database, a database outage fails liveness on every pod and Kubernetes restarts them all in a loop, although the
processes themselves were fine. The fix is to point liveness at a cheap "process is alive" endpoint and readiness at
"dependencies are reachable", so pods drop out of rotation during the outage and come back when the database does.
Then encode the rest of the platform's admission policy as a linter and run it before submitting: at least two
replicas, requests and limits for every container, both probes, pinned images, secrets via `secretKeyRef`,
`runAsNonRoot`, a read-only root filesystem, a Service selector that matches the pod labels and an autoscaler with at
least two minimum replicas. (Section 14.1; ex58)

*Strong signals:* explains the different consequences of the two probes; separates "alive" from "ready". *Red flags:*
removing the probes or lengthening timeouts without understanding the cause.

### 14.2 · Technical

**Q.** An adjuster asks "why was that answer slow?", and nobody can tell whether retrieval, the model or a tool call was responsible. How would you instrument the service so you can answer next time?

Trace every request as a tree of timed spans with attributes: a root `request` span, child spans for retrieval,
reranking, tool calls and the model call, all sharing the root's trace id and recording their parent. Use
`contextvars` so nesting works across threads and async tasks, and make a span that raises record `status = "error"`
and the exception type before re-raising. Wrap the model client so its span carries the model, input and output
tokens and cost. From the spans, compute a per-model summary (call count, p50 and p95 latency, tokens, cost), which
finance and the platform team both want, and the critical path: from the root, repeatedly follow the longest child,
giving something like "request → generate → llm.complete". In production, use the OpenTelemetry SDK, send spans to
the customer's tracing backend and use OpenTelemetry's generative-AI semantic conventions so their dashboards can
read your traces. The same stage spans measure each line of the latency budget. (Section 14.2; ex60)

*Strong signals:* critical path from spans; token and cost attributes on the model span; standard conventions.
*Red flags:* "add timing logs" with no request correlation.

### 14.3 · Technical

**Q.** The customer's SRE team won't take your copilot into their on-call rotation with "alert when the error rate exceeds 1%". Walk me through the SLO and the alerting you'd propose instead.

Define good: a request that didn't fail with a server error and finished within the latency threshold (3,000 ms in
ex61). The SLI is good over total in a window. With a 99.5% objective over 30 days, the error budget is 0.5% of
requests. Burn rate is (1 − SLI) ÷ budget: 1 spends exactly the budget over 30 days, and 14.4 sustained for an hour
spends 2% of it. Use two windows per alert: page when the burn rate is at least 14.4 over both the last hour and the
last five minutes; open a ticket when it's at least 6 over both six hours and 30 minutes. The long window shows the
problem is significant, the short one that it's still happening, so the alert resets quickly after a fix. A fixed 1%
threshold can't tell a two-minute blip from a slow leak that drains the month without crossing it. Budget remaining
then drives release decisions. For an AI service, decide deliberately whether refusals, failed parses or low judge
scores count; many teams keep those as separate quality SLOs. (Section 14.2; ex61)

*Strong signals:* the formula and the two-window logic; links budget to release priority. *Red flags:* a single
threshold alert; folding every quality signal into availability.

### 14.4 · System design

**Q.** Go-live is Monday with 400 adjusters, and the sponsor asks "will it hold?" Walk me through how you'd answer, from the capacity arithmetic to the performance test plan.

Start with Little's Law, L = λ × W. At a peak of 2 requests a second and 6 seconds each, about 12 requests are in
flight; two replicas with ten workers give 20 slots, so maximum throughput is 20 ÷ 6 ≈ 3.3 a second. If latency
doubles to 12 seconds, in flight doubles to 24: over capacity. Then write the plan. A workload model with the journey
mix, token counts from pilot logs, open arrivals and bursts to 4 a second; at twice the peak that is roughly two
million input tokens a minute, so a tokens-per-minute quota may bind first, and 24 in flight already calls for a third
replica. Targets that separate first token (p95 2.0 s) from full response (8 s / 12 s, 15 s for JSON claim summaries).
A per-stage latency budget. A test matrix: baseline, peak, stress, spike, soak, cold cache, prompt growth, model
change, rate limits, degraded dependency and retry amplification, real-model runs budgeted. Measure user-facing
latency with an open-model generator to avoid coordinated omission, count errors' latency, check quality under load,
and label every reported number by status. (Section 14.3; ex62)

*Strong signals:* numbers, including a bad-day scenario; tokens per minute as a limit; open versus closed load.
*Red flags:* one latency number; percentiles from a closed-loop generator.

### 14.5 · Technical

**Q.** A defence customer's network has no internet access, and everything arrives on approved media. How would you deliver your service, and how would their security officer verify what arrived?

Ship a bundle the security officer can verify independently. It contains a manifest listing every file with its
SHA-256 and size, plus the version, and a signature over the canonical JSON of that manifest (sorted keys, no
whitespace). ex64 uses an HMAC with a shared key; in production use an asymmetric signature, for example with GPG or
Sigstore tooling, so the verifier never needs the signing key. Verification reports a bad signature, a missing
manifest, missing or unexpected files, checksum mismatches and unsafe paths: absolute paths, `..` components,
symbolic links and hard links. Extraction verifies first and refuses to extract anything if a single problem is
found, because a member named `../../etc/cron.d/job` writes outside the target when extracted naively. Python 3.12's
`tarfile` extraction filters help, but verifying the manifest first is still the right design. Pin images by digest
where the customer requires it, and send a preflight script ahead so their IT team finds environment problems before
you arrive. (Section 14.4; ex64, ex63)

*Strong signals:* verify-then-extract, all or nothing; asymmetric signing in production. *Red flags:* extracting and
then checking; relying on the transfer medium being trusted.

### 14.6 · System design

**Q.** You want to move the copilot to a new prompt and a new model version. Walk me through the release path, and tell me what would make you roll back.

Prompts, model identifiers and retrieval parameters are versioned files reviewed like code, and every response logs
the versions that produced it. First, shadow: send a bounded share of live traffic to the new version for a bounded
period without showing its answers, and compare latency, cost, refusal rate and judge scores on a sample. Then a
canary: route a small percentage of users to it and compare with the current version over the same window. Wait
until it has a minimum number of requests (500 in the book's example), because a judge rate over forty conversations
is noise. Roll back if the error rate exceeds 1.5 times the base plus 0.1 points, p95 exceeds the base by 20%, the
judge pass rate falls by more than 3 points or the refusal rate rises by more than 2; otherwise promote. Agree the
thresholds with the SRE team and write them into the runbook. Rollback of a prompt or model must be a configuration
change that takes effect in minutes without a build, rehearsed by the customer's operations team. (Section 14.6)

*Strong signals:* a quality signal and over-refusal in the canary; a minimum sample. *Red flags:* error-rate-only
canaries; prompts edited in a console.

### 14.7 · Customer scenario

**Q.** At 02:14 on Saturday the customer's gateway started returning 502s on the copilot. By the time you join the bridge it has recovered, and three teams are blaming each other. What do you do that night and on Monday?

End the blame with evidence. Collect the JSON logs from the gateway, API, retriever and vector database and the
dependency map. Parse them, counting malformed lines rather than crashing; find each service's first error; the
suspect is the service with errors whose dependencies, transitively, had none before its own first error, the
earliest if several qualify. A gateway that failed after the API is a victim. List the blast radius in order of first
error and build timelines for sample request ids. Present it as the first hypothesis, since the cause could sit
outside these logs: a network change, a certificate expiry, a noisy neighbour. Keep customer updates in the fixed
stages (investigating, identified, monitoring, resolved), in plain language about user impact, with the time of the
next update and no pod names, internal service names, IP or email addresses. On Monday, a blameless postmortem:
summary with duration, time to mitigate and peak affected users, timeline, root cause, contributing factors, what
went well, and action items each with an owner and a due date. (Section 14.5; ex66, ex94)

*Strong signals:* timestamps plus dependencies to separate cause from victim; describes what the system allowed, not
who erred. *Red flags:* naming a person or team as the cause; action items with no owner.

### 14.8 · Customer scenario

**Q.** The sponsor asks "is it ready?" The weighted readiness score is 2.95, and the customer's operations team hasn't yet rehearsed a rollback. What do you tell them?

The answer is "not yet", for two reasons, and the order matters. Gates come first, and rollback of code, prompt and
model rehearsed by the customer's operations team is a gate; a failed gate means not ready, whatever the score. So the
first action is to schedule that rehearsal. Second, the weighted score must reach 3.0 with no dimension below 2, so
2.95 misses the bar. Make the gap specific: find the dimension whose evidence is weakest and say what would lift it.
In the book's Northwind review, replacing the estimated cost per task with the one measured in the performance test
lifts economics from 2 to 3 and the total to 3.05. A dimension still at 2, such as adoption there, can become a
condition of go-live rather than a blocker. Remind the sponsor that the weights were agreed with them and the score is
for coaching and conversation; the gates decide. After go-live approval, hold the operational readiness review and
finish with your access revoked. (Section 14.7)

*Strong signals:* gates before score; turns "not yet" into named actions with evidence. *Red flags:* rounding 2.95 up;
treating the rehearsal as a nice-to-have.

## Chapter 15 · Field Engineering and Productisation

### 15.1 · Technical

**Q.** Globex wants the SLA report you wrote on site at Acme, full of Acme's priority names, SLA hours and contacts. How would you turn it into something Globex can use without changing a line of Acme's output?

Don't copy and edit the constants; that's consulting, and the third customer pays for it again. Keep
`legacy_acme_report` untouched as the reference and write a golden-output test, a characterisation test, asserting
that the new `build_report` configured for Acme produces exactly the same output. That test is what lets you refactor
aggressively. Extract every customer-specific value into a `ReportConfig`: customer name, SLA hours per priority,
priority aliases ("P1" and "Sev1" for Acme, perhaps "Sev-A" for Globex), UTC offset and escalation contact. Validate
it: every canonical priority an alias maps to needs an SLA, and SLAs must be positive. Add a test that fails if the
library source mentions any customer by name, so a hard-coded fallback can never show "Acme" to a Globex user. Globex
is then a configuration, not a copy. If several copied adapters already exist, replace them with one
configuration-driven engine that validates mappings when they load and collects per-record errors. (Section 15.1;
ex67, ex73)

*Strong signals:* pins behaviour before changing it; validated configuration; no customer names in library code.
*Red flags:* refactoring the legacy function in place; "I'd fork it for Globex".

### 15.2 · Customer scenario

**Q.** An accounts-payable manager asks "Can AI read our vendor invoices?" and gives you until lunch. Walk me through what you'd build and what your readout would say.

Treat it as a feasibility question that deserves a fast, honest answer, not a production build. Use deterministic
rules where they work: invoice numbers, dates in several formats with the customer's day-first convention made
explicit, totals after "Total", "Amount Due" or "Balance Due" but not "Subtotal", and the vendor as the first line.
Call the model only for the fields the rules missed, as JSON, merge them without ever overriding a rule value, and
record each field's source (`rule` or `llm`), which keeps the POC cheap and explainable. Evaluate against
hand-labelled invoices and report accuracy per field, overall, and how many fields the model filled; one overall
number hides the field that matters most. The readout lists every field below 90% as a next step, states the
conditions behind every number (how many samples, how chosen), and ends with "Run on 200 labelled invoices before any
production decision." A POC on 15 samples proves feasibility, not accuracy. (Section 15.2; ex70)

*Strong signals:* rules first, model for gaps, provenance per field; explicit limits of the evidence. *Red flags:* a
single headline accuracy; over-engineering the POC.

### 15.3 · Customer scenario

**Q.** A health system wants intake notes summarised for research dashboards, and their privacy officer asks what happens to patient data. How would you answer, and where does your responsibility end?

Describe a pipeline the privacy officer can verify. De-identify each record: drop direct identifiers (name, medical
record number, phone, email); reduce dates of birth and visit dates to the year; group ages of 90 or over as "90+";
cut ZIP codes to three digits, using 000 for small-population areas. Scrub free text by tokenising MRNs, emails, dates
and phone numbers first, then each part of the patient's name as a whole word, case-insensitively. Enforce retention
by purging records past the period unless they're under legal hold, which always wins. Log every access with who,
a purpose from an allowed list and how many records, never the contents, since a log that copies patient data is
itself a store of it. Then be clear about the boundary: this is modelled on HIPAA Safe Harbor, which lists 18
identifier categories, and free-text de-identification is hard to do completely. Real programmes use the full list,
specialised tools, expert determination where appropriate and sign-off from privacy and legal. Your job is to build
it so they can verify it, not to be the final authority. (Section 15.3; ex72)

*Strong signals:* legal holds over retention; access logs without contents; deferring the final call to privacy and
legal. *Red flags:* "we strip names, so it's de-identified".

### 15.4 · Debugging

**Q.** A customer fine-tuned a smaller model on their best support replies. The validation score was excellent, but the model disappoints in use. What would you look at, and what would you have done differently?

Suspect leakage first: near-identical conversations on both sides of the train/validation split give an excellent
validation score and a disappointing model. Support data is full of templated replies, so check whether
de-duplication happened before the split and on normalised content (lower-case, digits replaced with 0, whitespace
collapsed), which catches "Your order 4471 has shipped" and "Your order 8812 has shipped" as one example. Rebuild the
pipeline: select resolved, high-satisfaction conversations with at least one agent turn; convert to chat format with
merged consecutive turns, ending on an assistant message; redact emails and phone numbers; de-duplicate; split by
intent, stratified and seeded, so every intent appears in validation; filter to the service's token limit. Then
revisit the decision itself: fine-tuning suits style, format and narrow stable tasks, not facts that change, which
retrieval handles. Compare the fine-tuned model with the best prompt-and-retrieval system on the same golden set and
include the operational cost of a model to version, evaluate and retrain. (Section 15.4; ex71)

*Strong signals:* de-duplicate before splitting, with normalisation; questions whether fine-tuning was the right
tool. *Red flags:* "train longer" or "add more data" without checking the split.

### 15.5 · Behavioural

**Q.** Tell me about a time you reviewed code you didn't write, from a colleague or a coding agent, that ran fine but was wrong.

Structure the story as situation, action, result. The situation: what the code did and why it looked acceptable (it
ran, it was fluent). The action is the core, and should show a method: you read it as if a capable stranger wrote it;
checked the boundaries first (SQL, file paths, shell commands, credentials, network calls, deserialisation); ran the
tests and then read them, looking for tests that test nothing or were weakened; hunted for silent failure such as
broad exception handlers, default values that hide errors and unbounded retries; and asked for the reasoning behind
suspicious choices. The defects in ex87 are the kind to name: SQL built with an f-string, an unchecked output path,
an off-by-one that skips the last page, a bearer token in the logs. Then show you closed the loop: a precise review
with one categorised finding per bullet, and, for agent code, "never do" rules in the instruction file so the next run
doesn't repeat them. The result: what was fixed, and what changed afterwards. Make clear you own the code you approve.
(Section 15.5; ex87)

*Strong signals:* a review method, not luck; findings turned into prevention. *Red flags:* "it passed the tests, so I
approved it"; blaming the tool or the author.

### 15.6 · Customer scenario

**Q.** The customer's security lead asks why they should let you use a coding agent on their repository. What do you agree with them before you start?

Don't argue for the tool; agree the rules, in writing, before you start. Four things. Which tools are approved:
enterprises often allow only specific assistants under their own agreements, and an unapproved tool can breach the
engagement contract however good it is. What the agent can see: secrets stay in the secret manager rather than the
repository, fixtures are synthetic, and directories holding customer data are excluded from its context. What the
agent can do: least privilege, with no production credentials, no pushing to protected branches and approval before
shell commands that change anything outside the working tree. What gets recorded: transcripts can contain code, data
and decisions, so agree where they're stored and for how long, as for any other log. Then put the rules where the
agent reads them, in the project's instruction file: the commands to run, the paths never to touch and the checks to
pass before finishing. Add that you review agent output as rigorously as any other code. (Section 15.5)

*Strong signals:* the four agreements; instruction file as enforcement. *Red flags:* using a personal or unapproved
tool because it's better; giving the agent production credentials.

### 15.7 · Behavioural

**Q.** Tell me about a time you had to decide whether something built for one customer should become part of the product.

Structure it as situation, decision, result, and show the reasoning. Situation: the code, the customers who needed
it, and what it cost to keep. The decision should use the three outcomes: it stays field code (one customer, likely
to change, low risk if it breaks), becomes configuration of an existing feature (several customers, same behaviour,
different parameters) or becomes a new product feature (several customers, a stable need, real cost when it's
missing). Mention the third-customer rule: build the first for the customer, generalise the second carefully, and by
the third it should be product or configuration. Show the discipline around it: a field-code register per customer
with an owner and a review date, so "temporary" scripts don't become permanent obligations. And show how you handed
it over: the customers, the configuration that varied, the golden-output tests and the incidents the field code
caused, because a request with tests and data gets built while an anecdote gets a ticket. The risk to name is a fix
reaching only one of several copies. (Section 15.6; ex67, ex73)

*Strong signals:* evidence-based hand-off to product; awareness that field code is cheap to write and expensive to
keep. *Red flags:* productising everything; leaving copies with no owner.

## Chapter 16 · Delivery Leadership

### 16.1 · Technical

**Q.** Meridian Bank's security team won't approve a new data store, so retrieval will run on the bank's Postgres with pgvector. Walk me through the decision record you'd write, and what makes it useful after you leave.

Write it as an architecture decision record: short, numbered, and never edited after acceptance (a later decision
supersedes it with a new ADR). The context states the constraint and the scale: security won't approve a new store
before go-live, and retrieval needs about 2M chunks. The decision is the bank's managed Postgres with pgvector and an
HNSW index, with a named decider (the Head of Platform Engineering). Alternatives considered: at least two, here a
managed vector database (faster to start, but an 8–12 week vendor assessment) and an already-approved search engine
the team can't operate. Consequences name the benefits (data stays where it lives, existing backups and access
controls) and at least one downside: index builds load the shared cluster, and you accept pgvector lock-in. Then add a
"Revisit when" section with measurable triggers, such as the corpus passing 20 million chunks or p95 retrieval latency
exceeding 300 ms, so the customer's team can monitor the decision after you've gone (Section 16.1; ex90).

*Strong signals:* insists on a named downside and explains why (it shows what was knowingly given up, and whether the
decider accepted it); adds revisit triggers with numbers. *Red flags:* an ADR that lists only benefits, which reads as
advocacy; no alternatives, which means it wasn't really a decision.

### 16.2 · System design

**Q.** An SI partner is building two of your five workstreams. How would you design the review and acceptance process for their designs and deliverables, and what would a rejection look like on paper?

Start before the work: put the quality bar in the partner's statement of work (the design checklist, the golden set
and its pass threshold, the security requirements and the gate), share the evaluation harness and CI gate from week
one, and review early and small: designs before code, a thin end-to-end slice before the full build. The design review
checks a checklist with three severities: blockers (authentication, data flow, PII handling, rollback, or PII "sent to
model" without redaction) must be fixed; majors (evaluation plan, observability, threat model) make acceptance
conditional; minors (cost estimate, SLO) are tracked. The deliverable gate decides on evidence, not assurances: reject
if any blocker or open critical defect remains; conditional if majors remain, any test fails or the evaluation pass
rate is below 90%; accept otherwise. Every triggered condition is listed as a reason, for example "Conditional: 2
major findings (evaluation plan, threat model); test pass rate 97% (184/190)" (Sections 16.1 and 16.4; ex90).

*Strong signals:* criteria agreed in the contract before work starts; asks for the test report, evaluation run and
security sign-off rather than slides; reasons a partner can act on. *Red flags:* accepting on the partner's assurance;
introducing new acceptance criteria at acceptance, which turns review into a dispute.

### 16.3 · Technical

**Q.** Three weeks into a six-week engagement, tasks are partly done and the steering committee asks if you'll land on time. How would you produce the forecast, and how do you decide which workstreams are slipping?

Report the forecast, not the baseline. Take the Chapter 2 plan as the baseline, then re-plan the remaining work: each
task's remaining duration is its expected duration times the share not yet done. Schedule that remaining work from
today with the critical path method and compare the forecast finish with the baseline finish; the difference is the
slip (for example, baseline day 42.0, forecast day 49.5, slip 7.5 days). For each workstream, compute an
earned-value-style schedule variance: reported progress minus the progress the baseline planned for today, weighted by
expected effort. More than 10% behind is amber, more than 25% is red, and a workstream whose critical-path task is more
than 10% behind is at least amber, because it moves the whole date. Two cautions: a workstream off the critical path
can still block go-live if its deliverable fails the quality gate, and "80% done" is an estimate, so measure progress by
acceptance criteria met where you can (Section 16.2; Capstone 6).

*Strong signals:* separates baseline from forecast; explains why the critical path gets a tighter threshold; treats
schedule and quality as different signals. *Red flags:* averaging owners' percentage-complete figures; reporting the
original plan date because nothing is "officially" late.

### 16.4 · Customer scenario

**Q.** On Friday the steering committee wants to know if you can go live. The forecast has slipped 7.5 days, one partner deliverable is conditional, one is rejected and activation is 50%. How do you run the meeting?

First, the go-live call comes from thresholds agreed with the sponsor in advance, not from feel. Blockers: a rejected
partner deliverable, open security questionnaire items needing human answers, or a forecast slip of more than ten days.
Conditions: a conditionally accepted deliverable, activation below 60%, or weak measured impact. Here the rejected
deliverable is a blocker, so the answer is *no go* as things stand, while the 7.5-day slip is under the ten-day line and
the conditional deliverable and 50% activation are conditions. Send the update a day early, in the fixed order: the
decision needed today first (for example, extend the rejected workstream or descope it to phase 2), a computed one-line
status, what changed, value so far, risks and asks with owners and dates from the RAID log, and the next milestone.
Spend the meeting on the decision, offer options with costs, and record the outcome. On activation, propose fixing it
before impact, team by team, with an owner (Sections 16.2 and 16.3; Capstone 6).

*Strong signals:* the "why no go" answer is a list of facts the committee agreed would block; leads with the decision,
not the status. *Red flags:* a status tour that ends without a decision; inventing thresholds in the room.

### 16.5 · Customer scenario

**Q.** A senior customer executive emails your VP saying the engagement is behind and nobody told them. What do you do in the next day, and afterwards?

Respond fast and factually. Acknowledge the concern the same day, without arguing. Before replying in substance, gather
the facts from the RAID log, the status history and the evidence. Brief your own manager and the account executive
before they're asked. Then reply with what happened, what you're changing and when the executive will see the
difference, copying the people who were copied on the escalation. Because the complaint is "nobody told them", treat
it as a surprise problem: most escalations are about surprise rather than substance. Afterwards, record what triggered
the escalation in the RAID log so the same gap can't cause a second one, and fix the communication path: material
forecast changes go to the sponsor the same day, in person or by phone, then in writing. Check the leading indicators
too (decision latency, sponsor attendance, days blocked on access), which often show trouble before the status colour
does (Section 16.5).

*Strong signals:* same-day acknowledgement but a fact-based substantive reply; briefs its own side first; fixes the
cause, not just the email. *Red flags:* a defensive point-by-point rebuttal; replying from memory without evidence.

### 16.6 · Behavioural

**Q.** Tell me about a time you had to tell a sponsor that a date was going to slip.

Use STAR (situation, task, action, result) with what *you* did and a measured result. The story must show the
chapter's shape for bad news. Timing: the sponsor heard it from you, early, the same day the forecast moved, in person
or by phone and then in writing, not first in a steering meeting. Content: what happened in one sentence with a
number; the impact on the outcome and the date; two or three options, each with its cost; your recommendation and why;
what you needed from them and by when. It should also show that you escalated inside your own company before the
customer heard (manager, account executive), and that once the decision was made you re-planned formally: a new
baseline, a RAID log entry and a change request if scope changed. Close with the result: which option was chosen, what
date was met, and what it did for trust (Section 16.5).

*Strong signals:* options with costs and a clear recommendation; the decision deadline; a formal re-plan afterwards.
*Red flags:* "the UI is late" with no options; a story where the sponsor found out from someone else.

### 16.7 · Behavioural

**Q.** Tell me about a time you were accountable for work done by people who didn't report to you, such as a partner or another team. How did you hold the quality bar?

Use STAR, and make the story show that you led through review rather than by writing the code. Strong elements to
show: you understood the other party's incentives (hourly versus fixed-deliverable partners are rewarded differently
from the customer's outcome); the quality bar was agreed up front, ideally in the statement of work, so it was a shared
standard rather than a dispute; you shared the evidence infrastructure (evaluation harness, golden set, CI gate) so they
saw their own regressions early; the RACI named one accountable person across the company boundary and who decided
disagreements; and you reviewed early and small. The action should include a gate decision made on evidence with
explicit reasons. The result should be measured, such as findings closed before acceptance or a deliverable accepted
on time, plus how knowledge transfer to the customer's team was measured (Sections 16.1 and 16.4).

*Strong signals:* evidence-based acceptance with reasons; criteria set before work started; planning the partner's
exit. *Red flags:* "we" did everything; rewriting the partner's work yourself instead of gating it.

## Chapter 17 · FDE Careers

### 17.1 · System design

**Q.** An insurer wants a copilot that answers 400 adjusters' coverage questions from 80-page policy PDFs, with citations. You have 45 minutes. Walk me through how you'd spend them.

Follow the operating loop and spend the time where deployments fail. Discover (about 5 minutes): who the users are,
what success means and how it's measured today, how many policy forms and versions, permissions, what can't leave the
network, and who signs off on launch. State assumptions with numbers (about 2 minutes) and invite correction: for
example 600 policy forms, 40,000 questions a month, answers within five seconds, a $40,000 monthly model budget,
citations and refusals required. Design (about 15 minutes): heading-based chunking with the heading path, version and
effective dates; hybrid retrieval with permission filters; abstention when retrieval is weak; validated citations;
output guardrails; a BFF that holds the key and streams; reuse of the customer's Postgres and identity provider.
Evaluate (about 8), operate (about 5) and adopt (about 5). If the interviewer pushes on one area, go deep there
(Sections 17.2 and 17.3).

*Strong signals:* asks questions before drawing anything; numbers stated as assumptions; real time on evaluation,
operations and adoption. *Red flags:* a vector database in the first two minutes; twenty minutes on embedding models.

### 17.2 · System design

**Q.** Same copilot: the interviewer says "Fine, but how will you know it works, before launch and after it's live?" What do you say?

Before launch: a golden set of about 150 questions built with senior adjusters, including an unanswerable slice so
abstention is tested; recall@4 for retrieval; citation precision and abstention accuracy for answers; and a
case-by-case regression gate in CI so a change can't silently break cases that passed. Then a pilot with a control
group and a decision rule agreed with the sponsor in advance. After launch: tracing, an availability SLO and a quality
monitor; canary releases with a quality check; kill switches. Value is measured too: the activation funnel by team, a
measured readout at six weeks and the business case re-run with measured numbers. Tie it back to the success metrics
from discovery (fewer wrong coverage answers, shorter handle time) (Section 17.3).

*Strong signals:* separate retrieval and answer metrics; an unanswerable slice; a decision rule agreed before the data
arrives. *Red flags:* "we'll have users give thumbs up" as the only measure; evaluating once and never again.

### 17.3 · Customer scenario

**Q.** I'm the chief operating officer: "We need AI that makes support faster and better, soon." How do you respond?

This tests whether you can turn vagueness into a plan without agreeing to everything or getting defensive. Don't pitch
a solution. Acknowledge the goal, then ask clarifying questions that make "faster", "better" and "soon" measurable:
which support team and channel, what's measured today (handle time, resolution, quality scores) and its baseline, what
"soon" means and what's driving it, what data and systems exist, and who must sign off. Where answers aren't available,
state dated assumptions and say how you'll confirm them. Close with a concrete next step: a short discovery, a charter
with a success metric, scope and an out-of-scope list, and a date for a first decision. Hold scope politely if asked to
promise everything at once (Section 17.2; ex06).

*Strong signals:* converts adjectives into metrics with baselines; dated assumptions; a proposed next step. *Red
flags:* agreeing to "faster and better" with a date and no definition; jumping straight to a demo.

### 17.4 · Customer scenario

**Q.** A logistics company wants to use AI to reduce delivery exceptions. You have six weeks and two engineers. What do you do?

This is the decomposition or case round, testing the Chapters 2 and 16 skills. Find the metric first: how exceptions
are counted today, the baseline rate and which exception types cost the most. Cut scope to one exception type or one
part of the flow that two engineers can deliver and measure in six weeks, and write an explicit out-of-scope list.
Estimate with ranges rather than single numbers, sequence the work so a thin end-to-end slice exists early, and name the
riskiest assumption (for example, that the data needed to predict or explain exceptions exists and can be accessed)
and test it first. Build in measurement: how you'll know at week six whether exceptions fell, ideally against a
comparison group, and what decision follows (Section 17.2).

*Strong signals:* metric and baseline before solution; ranges; riskiest assumption tested first; an out-of-scope list.
*Red flags:* a plan with no measurement and no out-of-scope list; promising every exception type.

### 17.5 · Behavioural

**Q.** Tell me about a time you owned an outcome beyond your job description.

Answer in the STAR shape: situation, task, action, result. Keep it to about two minutes. The situation should make
clear what was outside your role and why it mattered to the customer's outcome. The action must be what *you* did, in
the first person, with the judgement calls visible: what you chose to take on, what you said no to, and who you told.
The result must be measured, for example a metric moved, a date held or an incident avoided, with the number. If the
experience is from real customer work, anonymise it and stay within your confidentiality obligations. Have this story
ready as one of six to eight that together cover ownership, cutting scope, bad news, disagreement, failure and
productisation (Section 17.2).

*Strong signals:* a clear "I"; a measured result; a judgement call the interviewer can probe. *Red flags:* "we" did
everything; a story that ends with effort rather than a result.

### 17.6 · Behavioural

**Q.** Can you show us the readout from your last customer engagement? It would help us judge your work.

Decline, politely, and offer something better. Engagement artefacts belong to the customer and usually fall under a
confidentiality agreement, so a real readout, real screenshots, logs or data (even redacted) and real figures can't be
shown. Offer instead a capstone or other synthetic engagement published with its code, a two-page design record with
ADRs, the evaluation results with an honest account of failures, a one-page executive readout and its scorecard, every
number labelled as measured, assumed or projected. Then offer to describe the real engagement as an anonymised story
without identifying details. Handling this well is itself evidence of the judgement the role needs (Section 17.4).

*Strong signals:* refuses without fuss and redirects to capstone evidence; knows what a good readout contains.
*Red flags:* sharing customer material "just this once"; claiming redaction makes it safe.

### 17.7 · Behavioural

**Q.** Suppose you join us next month as an FDE. What would your first 90 days look like?

Learn first, then own a workstream, then an engagement. Days 1–30: shadow at least two engagements, including a
discovery session and a steering meeting; learn the platform deeply enough to debug it, not just demo it; ship one fix
or small improvement to a customer deployment; write one product brief from what you've seen in the field. Days 31–60:
own a workstream with your name as the responsible person in the RACI; run a discovery session and write the charter;
set up an evaluation suite if the engagement lacks one. Days 61–90: own an engagement end to end with a sponsor,
charter, plan and measured outcome; contribute one reusable component back to the product; teach something, such as a
customer workshop or an internal session (Section 17.5; ex68, ex01, ex84).

*Strong signals:* resists proving yourself by shipping features in week one; ends with ownership and a measured
outcome. *Red flags:* "I'll start coding on day one"; a plan with no learning phase and no teaching.
