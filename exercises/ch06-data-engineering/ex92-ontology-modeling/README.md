# ex92 · Ontology modelling: objects, links and governed actions

**Chapter:** 6 · Data Engineering (`exercises/ch06-data-engineering/`) · **Covers:** R42 Ontology / semantic modelling, R03 Data modelling, R31 Data platforms ·
**Time:** 75 min

## Learning objectives
- Model business objects, typed links and governed actions as an ontology.
- Validate loaded data and detect dangling links.
- Make actions the only way users and agents change state.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch06-data-engineering/ex92-ontology-modeling`.
- **Expected output:** all 3 tests fail against the starter; when you're done, all 3 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch06-data-engineering/ex92-ontology-modeling`: all
  3 pass.
- **Tests:** `test_ontology.py` (3 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The ontology lives in memory: roles are strings passed by the caller, the audit log is a
  Python list and atomicity comes from a deep copy. A production version authenticates the actor, enforces roles
  server-side, writes changes and audit entries in one database transaction to an append-only store, and makes
  actions idempotent so a retried agent call can't apply twice.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Ontology modelling: objects, links
and governed actions". Before I write code, teach me ontology modelling (object types, link types, cardinality,
reverse traversal) and governed actions with role checks, validation and audit, as in Palantir Foundry. Use short
Python examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a
time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch06-data-engineering/ex92-ontology-modeling/starter.py so that test_ontology.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ObjectType`, `LinkType`, `Ontology`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package
only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/ch06-data-engineering/ex92-ontology-modeling` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Ontology modelling: objects, links and governed actions" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Are partial loads safe (valid rows loaded, invalid rows
reported)? Does reverse traversal work for one-to-many links? Can an action bypass validation when called by an
agent? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
