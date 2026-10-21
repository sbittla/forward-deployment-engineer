# Lakeside intake pilot: week 3 update

## Status
**GREEN.** On track for the board readout. The POC runs end to end on de-identified real calls, with 100% urgent
recall on the labeled sample.

## Done this week
- Red-flag override shipped. The chest-pain call that the model under-triaged is now escalated to emergency.
- PHI guard blocks any prompt containing names, dates of birth, MRNs, phones or emails, and is tested on all
  sample calls.
- Eval set of 4 labeled calls agreed with the Nurse Manager. It grows to 50 next week.

## Next week
- Deploy the pipeline inside the clinic's Azure tenant (milestone 4).
- Expand the eval set to 50 calls and run it in CI.

## Risks
- The recording retention period is still unconfirmed. We are assuming 30 days and no copies leave the tenant.
- Red-flag list ownership is pending; the CMO is assumed to be the owner until confirmed.

## Asks
- Dr. Okafor: confirm red-flag list ownership by Thursday.
- Sam Patel: approve the model endpoint egress rule in the clinic firewall.
