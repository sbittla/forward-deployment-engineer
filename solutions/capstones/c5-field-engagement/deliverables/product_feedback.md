# Product feedback from the Lakeside intake engagement

## Summary
Healthcare deployments repeat the same three safety components. Shipping them in the platform would remove an
estimated two weeks of custom build from every clinical engagement, and it would make the security review shorter.

## Requests
1. **Pre-send PHI guard as a platform feature.** Scan every outbound prompt against configurable identifier types
   plus per-request name lists, and block on match. We built `_GuardedLLM` by hand.
2. **Deterministic rules layer on structured outputs.** Let customers declare "if transcript mentions X, set field
   Y to Z" overrides that can never be downgraded by the model (our red-flag triage).
3. **Voice-call analytics export.** Turn latency, barge-ins and silences per call into metrics, so voice quality is
   visible without custom parsing of event streams.

## Evidence
- The scripted extraction model under-triaged the chest-pain call. Only the rules layer brought urgent recall
  from 67% to 100%.
- The Privacy Officer's first two review questions were about prompt-level PHI controls and audit evidence.
- Two other health-system prospects asked for the same red-flag override pattern during discovery.
