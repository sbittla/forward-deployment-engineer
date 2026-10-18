# Transaction insights pilot: executive readout

## Summary
The assistant answered 100% of the answerable pilot questions correctly (execution accuracy against analyst-written
gold queries) and refused 100% of the out-of-scope or destructive requests. We recommend expanding to all
commercial relationship managers next quarter.

## Results
| Measure | Result |
|---|---|
| Execution accuracy on answerable questions | 100% (5 of 5) |
| Correct refusals (data changes, unavailable PII) | 100% (2 of 2) |
| Unsafe queries blocked before execution | 5 |
| Average model attempts per question | 1.71 |
| Rows quarantined by data-quality checks | 3 of 22 (13.6%) |

## Controls
- SQL guard: single read-only SELECT, allow-listed tables, forced row limit, comment stripping.
- Read-only database credentials in production as a second layer.
- Narratives are generated from query results in code, so the model cannot misstate a number.
- Quarantine report for every load, with reasons, sent to Data Engineering.

## Risks
- The pilot question set is small. Accuracy on open-ended questions will be lower until the set grows to 200 real
  questions.
- FX rates are monthly; intra-month swings of more than 3% would distort cross-currency comparisons.

## Next steps
- Grow the gold question set from real relationship-manager requests and run it in CI.
- Add a semantic-layer review step with Finance for every new metric.
- Instrument usage and correction feedback in the RM portal.
