# Evaluation plan

| | |
|---|---|
| **Owner** | FDE with the customer's domain experts |
| **When** | Before the first demo |
| **Inputs** | The charter, sample questions from users, the policy or rule set |
| **Done when** | The golden set exists, slices are defined, the launch bar and decision rule are agreed in writing |
| **Book** | Chapter 12 · ex49–ex52, ex99, ex100 |

- **Golden set:** version ______, ______ cases; sources (production samples, expert-written, red team, synthetic)
- **Splits:** development ______ cases; held-out ______ cases; refreshed every ______
- **Labelling protocol:** two labellers per case; agreement (kappa) target ______

## Slices
| Slice | Cases | Critical? | Grader | Launch bar |
|---|---|---|---|---|
| | | | | |

## Judge (if used)
Model ______; rubric version ______; kappa against experts ______; position-bias check: yes / no

## Decision rule (agreed before results)
- Gates: no critical-slice regressions; no missing cases.
- Ship if: ______
- Pilot: metric ______, control group ______, sample size for 80% power ______

## After launch
Online monitors, thresholds, who's paged, human review sample rate.
