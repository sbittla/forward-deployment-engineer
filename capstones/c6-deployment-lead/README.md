# Capstone 6 · Deployment Lead: a partner-delivered, multi-workstream engagement

**Covers:** R33 Delivery management · R34 Adoption & change · R35 Enablement · R40 Technical leadership ·
R43 Regulatory/security gates · R19 Executive communication · R30 Value · R20 Ambiguity · R23 Product feedback ·
R13 Measurement
**Suggested time:** 2 days · **Builds on:** ex05, ex07, ex08, ex81–ex84, ex90

## The engagement
You are the **Deployment Lead** (OpenAI's title; Anthropic's Staff FDE does the same job) for Meridian Bank's
relationship-manager briefing assistant. You own delivery but don't write most of the code: two of five
workstreams belong to a systems integrator, Atlas SI, and you set the quality bar for work you don't build. It's
week 3. The steering committee meets Friday and wants one answer: *are we on track to go live, and if not, what do
you need from us?*

Data in `data/`: the plan with three-point estimates and reported progress (`engagement.json`), Atlas SI's two
deliverables with designs and test/eval evidence (`partner_deliverables.json`), pilot usage events and before/after
KPI measurements for pilot vs control teams (`adoption.json`), and the bank's security questionnaire with your
system facts (`security.json`).

## What you build (`starter/deliverylead/`)
| Module | Responsibility |
|---|---|
| `plan.py` | PERT estimates, critical path, P50/P90; **forecast** from reported progress (slip vs baseline); per-workstream earned-value variance → RAG |
| `reviews.py` | Partner design checklist (blocker/major/minor) + evidence gate → accept / conditional / reject with reasons |
| `adoption.py` | Funnel, lagging teams, difference-in-differences impact against the control group |
| `security.py` | Auto-answer the questionnaire from system facts; anything about physical security or model risk always goes to humans |
| `readiness.py` | Go-live decision: explicit blockers (rejected deliverables, open security items, slip > 10 days) and conditions (conditional deliverables, activation < 60%, weak impact) |
| `steering.py` | The Friday steering update, generated from all of the above |

## Deliverables (`starter/deliverables/`)
- `sow.md`: the SOW including **partner responsibilities**, acceptance criteria per milestone and a P50/P90 estimate.
- `partner_review_memo.md`: findings on Atlas SI's deliverables, conditions for acceptance, re-review date.
- `enablement_plan.md`: audiences, workshops, champions, knowledge-transfer exit criteria, adoption targets.

## Run
```bash
pytest capstones/c6-deployment-lead
pytest --solutions capstones/c6-deployment-lead
```

## Reflection prompts
1. The UI is off the critical path, yet it blocks go-live. How do you explain that to a CFO in one sentence?
2. Impact is strong (−37% vs control) but activation is 50%. Which would you fix first, and how?
3. What would you push back to your own product team after this engagement?
