# ex92 hints · Ontology modeling: objects, links and governed actions

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Store objects as `type name -> {primary key -> row dict}`. With that one structure, `get` is two dict lookups,
duplicate detection is `pk in store`, and integrity checking is "does this foreign key exist in the target's dict?".
Write `load` first, with one error string per bad row and no exceptions.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **load:** for each row, check the primary key is present, then the property types, then for a duplicate. Report the
  first problem as `"<type>:<index>: <problem>"` and skip the row.
- **Types:** `float` accepts ints too, `None` is always allowed, and booleans don't count as ints or floats.
- **traverse:** a forward link reads the foreign key from the source object and looks it up in the target type. A
  reverse link (`~name`) scans the source type for objects whose foreign key equals the given key.
- **execute:** check the role, then the parameters (missing, wrong type, unexpected), then the action's own
  `validate`. Only then call `apply` and append to the audit log.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `isinstance(True, int)` is True, so check booleans explicitly when the declared type isn't `bool`.
- Every check in `execute` must run **before** `apply`. A rejected action leaves the objects and the audit log
  untouched. For extra safety, snapshot the objects and restore them if `apply` raises.
- The reverse traversal returns shipments in primary-key order (`S1`, `S2`). Sort when you scan.
- The audit `seq` starts at 1 and records the parameters as a plain dict.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_types_validated` | Link to an unknown type accepted; error index or wording wrong; invalid rows loaded anyway |
| `test_traverse` | Reverse links (`~`) not supported; reverse results not sorted by key |
| `test_unknown_object_and_refusals_are_logged` | `validate` runs before the object's existence is checked (`TypeError` on `None`); a refusal or failed `apply` not appended to `rejected`; changes not rolled back |
| `test_actions` | Audit written before validation; missing parameters not rejected; role checked after the parameters |
