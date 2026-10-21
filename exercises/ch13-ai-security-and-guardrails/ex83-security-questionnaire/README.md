# ex83 · Security and procurement questionnaire responder with regulatory triage

**Chapter:** 13 · AI Security and Guardrails (`exercises/ch13-ai-security-and-guardrails/`) · **Covers:** R43 Regulatory frameworks, R17 Security & compliance, R33 Delivery (procurement gates) ·
**Time:** 60 min

## Learning objectives
- Answer security questionnaires from a single source of system facts.
- Route low-confidence answers to a human review queue.
- Find contradictions between sales claims and how the system works.

## Scenario
Anthropic's Staff FDE posting: "anticipate security and procurement gates". The pilot is done, and now a 180-question
vendor security questionnaire (CAIQ/SIG-style) stands between you and production. Answers must be consistent with
how the system actually works. One contradiction ("we retain no data" vs a 30-day log retention) can stall a deal
for a month. You'll answer from a single source of system facts, flag what needs a human, and triage which
regulations apply.

## Your task
`facts` describes the deployed system: `{"data_retention_days", "encryption_at_rest", "encryption_in_transit",
"subprocessors": [...], "data_residency", "trains_on_customer_data": bool, "sso": bool, "pen_test_date",
"incident_notification_hours", "processes_personal_data": bool, "processes_health_data": bool}`.

1. `answer(question, facts) -> Answer(text, source_fact, confidence)` — rule table `RULES` maps keyword groups to
   facts (retention, encryption, subprocessor, residency/location, training, SSO, penetration test, breach/incident).
   A keyword matches when a word in the question **starts with** it (stems: `retain` matches `retained`).
   Confidence = matched keywords / keywords in the best rule (2 dp). No rule with ≥ 1 keyword match → text
   `"NEEDS SECURITY TEAM REVIEW"`, `source_fact=None`, confidence 0.0.
2. `answer_all(questions, facts, min_confidence=0.5)` → `(answers, review_queue)`: answers below `min_confidence`
   go to the review queue (by question index) instead of being auto-answered.
3. `contradictions(claims: dict[str, str], facts) -> list[str]` — free-text claims from sales collateral checked
   against facts: claims saying "no data retention"/"zero retention" while `data_retention_days > 0`; "never train"
   while `trains_on_customer_data`; "EU only" while residency isn't EU; return the claim keys, sorted.
4. `regulatory_triage(use_case: dict) -> dict`:
   - `gdpr_dpia_required`: personal data and (large scale, or special category/health data, or systematic monitoring)
   - `hipaa_baa_required`: health data processed for a US covered entity
   - `eu_ai_act_tier`: `"prohibited"` if social scoring; `"high"` if domain in `HIGH_RISK_DOMAINS`; `"limited"` if it
     interacts with people (chatbot) or generates content; else `"minimal"`
   - `obligations`: sorted list built from the above (`"DPIA"`, `"BAA"`, `"EU AI Act conformity assessment"` for high,
     `"AI transparency notice"` for limited or high).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Security and procurement
questionnaire responder with regulatory triage". Before I write code, teach me vendor security questionnaires
(CAIQ/SIG style), consistency of answers, and which regulations apply to a deployment. Use short Python examples
that are not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell
me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch13-ai-security-and-guardrails/ex83-security-questionnaire/starter.py so that test_questionnaire.py
passes. README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public
API: `Answer`, `answer`, `answer_all`, `contradictions`, `regulatory_triage`. Constraints: Python 3.11+, the
standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify
the tests or fde_kit. When you're done, run `pytest exercises/ch13-ai-security-and-guardrails/ex83-security-questionnaire` and
show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Security and procurement questionnaire responder with regulatory triage" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Does prefix matching create false matches
('train' matching 'training room')? Are contradictions checked for every claim? Which answers should never be
auto-generated? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
