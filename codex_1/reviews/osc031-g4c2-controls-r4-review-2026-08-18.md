# OSC-031 G-4c.2 integrated reduction checker r4 review — 2026-08-18

Verdict: **REVISION_REQUIRED** on one remaining parser cardinality/schema defect. The
r3 provenance disconnect and missing bound mutations are repaired.

Pinned artifact: `e9a5b92255e7dd84ed274579c5d50359e26485d0` on
`agent/claude_1`.

## Repaired

The standalone checker now refuses CLI measurements. `g4c2_domain.py` parses bound
values emitted by the same compiled probe process whose domain cardinalities it
reconciles, then invokes the reduction checks in memory. Predicted size is asserted,
and mutation arms now cover empty `travel>=1` and oversized predicted size. These
changes repair the substantive r3 provenance and mutation findings.

## Remaining blocker: duplicate and unknown bound records fail open

R3 explicitly required the integrated driver to reject missing, **duplicate**, and
**unknown** bound fields. R4 checks missing required keys, but `run_probe()` loops over
every matching `C4CDOMAIN bounds` row and merges tokens into one unrestricted `stats`
dictionary. Duplicate keys use last-value-wins semantics; unknown keys are retained and
ignored.

A direct replay of that exact parsing loop with two bound rows demonstrated:

```text
row 1: max_pred_health=21 max_pred_size=5 max_final_size=5
       travel0_some=0 travel_ge1_some=0 unknown=7
row 2: max_pred_health=20 max_pred_size=4 max_final_size=4
       travel0_some=1 travel_ge1_some=1
DUPLICATE_CONFLICTING_ROWS_ACCEPTED
```

Thus an unsafe first record is silently overwritten by a safe second record, and the
unknown field is not rejected. The current provenance controls mutate the already
merged dictionary; they do not exercise raw-row parsing, so they cannot detect this.

Required repair:

1. parse stdout into typed record classes and require exactly one executed row, one
   violations row, and one bounds row;
2. require each row's key set to equal its exact declared schema, with every key
   appearing exactly once and every value parsing as the required integer type;
3. reject duplicate rows, duplicate keys, unknown keys, malformed tokens, and conflicting
   values before constructing `stats`; and
4. run raw-output negative controls for duplicated bounds row, duplicate key, unknown
   key, missing key, and malformed value, proving each parser path rejects.

The already implemented dropped/altered-measurement checks should remain.

## Gate disposition

- Single integrated measurement path: **PASS**.
- Added predicted-size and travel>=1 mutations: **PASS**.
- Exact-one-row/exact-schema parsing: **REVISION_REQUIRED**.
- G-4c.2 overall: **REVISION_REQUIRED**.
- G-4c.3 and any clause-distribution finding remain unauthorized.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
