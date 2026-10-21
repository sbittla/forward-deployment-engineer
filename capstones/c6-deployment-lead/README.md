# Capstone 6 · Deployment Lead: a partner-delivered, multi-workstream engagement

**Covers:** R33 Delivery management · R34 Adoption & change · R35 Enablement · R40 Technical leadership ·
R43 Regulatory/security gates · R19 Executive communication · R30 Value · R20 Ambiguity · R23 Product feedback ·
R13 Measurement
**Builds on:** ex05, ex07, ex08, ex81–ex84, ex90
**Take after:** Part V, last: after ex81, ex82 and ex84 (Part I), ex83 (Part III) and ex90.

## The engagement
You are the **Deployment Lead** (OpenAI's title; Anthropic's Staff FDE does the same job) for Meridian Bank's
relationship-manager briefing assistant. You own delivery but don't write most of the code: two of five
workstreams belong to a systems integrator, Atlas SI, and you set the quality bar for work you don't build. It's
week 3. The steering committee meets Friday and wants one answer: *are we on track to go live, and if not, what do
you need from us?*

Data in `data/`: the plan with three-point estimates and reported progress (`engagement.json`), Atlas SI's two
deliverables with designs and test/eval evidence (`partner_deliverables.json`), pilot usage events and before/after
KPI measurements for pilot vs control teams (`adoption.json`), and the bank's security questionnaire with your
system facts (`security.json`). `engagement.json` also holds last week's snapshot (`last_week`: `as_of_day` and
`progress`) and the RAID log (`raid`: `id`, `type`, `text`, `owner`, `due`, `status`).

## What you build (`starter/deliverylead/`)
| Module | Responsibility |
|---|---|
| `plan.py` | PERT estimates, critical path, P50/P90; **forecast** from reported progress (slip vs baseline); per-workstream earned-value variance → RAG; `next_milestone(eng)`: the first milestone task with progress below 1.0, by baseline finish, as `{"milestone", "task", "acceptance", "baseline_day", "forecast_day"}` (days to 1 dp; forecast from the re-planned schedule), or `None` when all are done |
| `reviews.py` | Partner design checklist (blocker/major/minor) + evidence gate → accept / conditional / reject with reasons |
| `adoption.py` | Funnel, lagging teams, difference-in-differences impact against the control group |
| `security.py` | Auto-answer the questionnaire from system facts; anything about physical security or model risk always goes to humans |
| `readiness.py` | Go-live decision: explicit blockers (rejected deliverables, open security items, slip > 10 days) and conditions (conditional deliverables, activation < 60%, weak impact) |
| `steering.py` | The Friday steering update, generated from all of the above, in Section 16.3's order (one `##` heading each): **Decisions needed** (one bullet per blocker, then condition, or `- none`); **Overall** (the status line); **Changed since last week**: `- Delivered: <tasks that reached 1.0 since `last_week`>.`, `- Slipped or newly at risk: <ws OLD -> NEW; ...>.` (workstreams whose RAG got worse), `- Forecast finish: day X, was day Y last week (+Z days).`, then `### Workstreams` and `### Partner deliverables` tables (or `- No previous snapshot to compare with.` when `last_week` is absent); **Adoption and impact**; **Risks and asks**: open `raid` items by due date as `- <id> <type>: <text> (owner: <owner or UNASSIGNED>, due <due or NO DATE>)`, then the security line; **Next milestone**: `- <milestone> (<task>): forecast day X vs baseline Y. Acceptance: <acceptance>.` |

## Deliverables (`starter/deliverables/`)
- `sow.md`: the SOW including **partner responsibilities**, acceptance criteria per milestone, **support
  boundaries** (who supports what after go-live, for how long, and what isn't covered), **exit criteria** (when the
  engagement closes, each with its evidence) and a P50/P90 estimate.
- `partner_review_memo.md`: findings on Atlas SI's deliverables, conditions for acceptance, re-review date.
- `enablement_plan.md`: audiences, workshops, champions, knowledge-transfer exit criteria, adoption targets.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run
```bash
pytest capstones/c6-deployment-lead
pytest --solutions capstones/c6-deployment-lead
```

## Reflection prompts
1. The UI is off the critical path, yet it blocks go-live. How do you explain that to a CFO in one sentence?
2. Impact is strong (−37% vs control) but activation is 50%. Which would you fix first, and how?
3. What would you push back to your own product team after this engagement?

## Assessment
Assessed with the shared [capstone rubric](../RUBRIC.md): gates first (tests, critical correctness, security and
privacy, honest reporting, plus this capstone's own gates), then a weighted score across nine dimensions. The bar is
every gate passing, a weighted score of at least 3.0 and no dimension below 2. Section 4 of the rubric lists C6's
acceptance criteria and gates. Submit your scorecard as `starter/deliverables/scorecard.md`.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest capstones/c6-deployment-lead`.
- **Expected output:** all 14 tests fail against the starter; when you're done, all 14 pass.
- **Check the reference solution:** `pytest --solutions capstones/c6-deployment-lead`: all 14 pass.
- **Tests:** `tests/test_c6_deliverables.py`, `tests/test_c6_gates.py`, `tests/test_c6_plan.py` (14 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** the plan, adoption funnel and impact use a few synthetic tasks and eight users, so the 37%
  effect has no confidence interval, and the go-live function decides from thresholds alone. A real go-live also
  needs named decision owners, residual risk accepted in writing by the customer's risk owner, sponsor sign-off,
  tested escalation paths and a booked post-launch review (Chapter 16's go-live checklist).

