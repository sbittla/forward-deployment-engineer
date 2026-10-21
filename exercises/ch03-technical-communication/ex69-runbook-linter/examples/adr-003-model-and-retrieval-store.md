# ADR-3: The model through Northwind's cloud; retrieval in Northwind's Postgres
Status: accepted

*Filled-in example of `playbook/design/adr.md` for the Northwind reference engagement (Appendix E.4, ADR-3).
Northwind, its people and its numbers are fictional and illustrative. This record passes ex90's `lint_adr`; the
playbook template's "Options" heading appears here as "Alternatives considered", the name ex90 checks for.*

## Context
- Data must stay in Northwind's cloud region; only redacted text may cross trust boundary B3 (Table E.4).
- A new model-vendor contract would take 8 to 12 weeks through procurement; the pilot is six weeks.
- Northwind's cloud agreement already covers the same model family through the cloud marketplace.
- The platform team already runs Postgres, but can't provision pgvector before week 5 (RAID decision D-14).
- Retrieval scale: 600 policy forms with versions; re-embedding all of them takes about 40 minutes.

## Alternatives considered
- The provider's API directly: newest features first, but the contract misses the pilot by 2 to 6 weeks.
- The same models through Northwind's cloud marketplace: covered by the existing agreement, in region.
- A self-hosted open-weights model: no contract, but Northwind has no GPU capacity or team to run it.
- For retrieval: a managed vector database (a new store to approve) or Postgres with pgvector (already operated).

## Decision
Use the model through Northwind's cloud marketplace, and Postgres with pgvector for production retrieval. The pilot
runs on a managed vector database until pgvector is provisioned (D-14).
decided-by: Dana Ruiz, VP Claims, with Priya (IT Security) and the platform engineering lead consulted; week 2.

## Consequences
- Benefit: no new contract and no new production datastore; the security review covers one known cloud path.
- Downside: new model features can reach the cloud marketplace later than the provider's own API.
- Downside: model identifiers differ between the marketplace and the provider, so the adapter layer (ex86) stays,
  with its test cost.
- Risk: index builds load a shared Postgres cluster; re-embedding runs off-peak through the batch API (ADR-4).

## Revisit when
- A self-hosted model comes within two held-out points of the current model at a lower cost per successful task.
- Monthly model spend passes $40,000.
- Re-embedding the corpus takes longer than the nightly maintenance window.
