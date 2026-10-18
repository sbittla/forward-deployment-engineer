# ex92 · Ontology modelling: objects, links and governed actions

**Module:** m14 · **Covers:** R42 Ontology / semantic modelling, R03 Data modelling, R31 Data platforms ·
**Time:** 75 min

## Scenario
Palantir FDSEs and Deloitte's Palantir FDEs spend much of their time turning a customer's scattered tables into an
**ontology**: business objects (Customer, Shipment, Warehouse), typed links between them, and governed **actions**
that are the *only* way operational users and AI agents change state. Once the ontology exists, apps and LLM agents
query "shipments for this customer that are delayed" instead of joining five tables. Build the core of that model.

## Your task
1. `ObjectType(name, primary_key, properties: dict[name, type])` and
   `LinkType(name, source, target, cardinality: "one"|"many", foreign_key)`: the foreign key lives on the **source**
   object and points at the target's primary key.
2. `Ontology.add_object_type`, `add_link_type` (unknown types → `ValueError`), and
   `load(type_name, rows)`: validate every row has the primary key, property types match (`int`, `float`, `str`,
   `bool`; `None` allowed), and no duplicate primary keys. Return a list of `"<type>:<row index>: <problem>"` errors
   and load only the valid rows.
3. `integrity()` → dangling links: `"<link>:<source pk>-><missing target pk>"` sorted.
4. `get(type, pk)`; `traverse(type, pk, link)` → linked objects (a list for `many`, a single object or `None` for
   `one`). Traversal works in reverse too: `traverse("Customer", "C1", "~ships_to")` returns the shipments whose
   `ships_to` link points at C1.
5. `register_action(name, object_type, params: dict[name, type], validate, apply, allowed_roles)` and
   `execute(name, actor, role, **params)`: check the role (`PermissionError`), parameter presence and types
   (`ValueError`), and `validate(ontology, **params)` (returns an error string or `None`, raised as `ValueError`).
   Then call `apply(ontology, **params)`, which mutates objects, and append an audit entry `{"action", "actor",
   "params", "seq"}`. A failed action leaves no audit entry and no changes.
