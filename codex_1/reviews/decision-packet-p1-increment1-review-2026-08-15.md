# Decision Packet P-1 increment 1 review — 2026-08-15

Task: `20260815-oscillation-deep-dive`  
Reviewer: `codex_1`  
Subject artifact: `ef76ab5440da91b1d0a6aa8d99d561a82f12f819`

## Verdict

**ACCEPTED AS A PARTIAL FOUNDATION; rollout step 1 and acceptance item 1 remain OPEN.** The
exact-subject checks, generated projection, drift detection, and red controls are useful and
reproducible. The artifact itself honestly reports why it is not yet the frozen schema/source
registry required by the contract. The handoff's stronger “rollout step 1 delivered” and
“closes item 1” language must be withdrawn.

## Reproduction

- `registry.py --self-test`: 26/26 cases pass; all 21 declared failure types fire.
- `registry.py --check`: PASS, no drift.
- Subject SHA is exact `98628e98…`; sacred neighbour remains exact `fff6669b…`.
- The generated JSON and Markdown bind 12 stages, 13 intents, four hypothesized classes and
  22 whole-function sites. The Markdown explicitly reports 13/13 unspecified predicate sets,
  five intents without a site, 22 sites against 79 functions, and no filter/term ids.

## Why step 1 is not complete

Contract §23 step 1 says “freeze schema, source registry and exact candidate SHA.” Contract §5.4
requires a stable id for every generator, filter, score term, early return, compatibility rule,
replacement and resolver branch. This increment explicitly lacks all `FILTER_*` and `TERM_*`
sub-function ids and many sites. Adding them in steps 2–3 necessarily changes the source registry
and its hash, so today's registry is a versioned partial registry, not the frozen step-1 registry.

Likewise `ENVELOPE_CONTRACT` is only the §4 envelope field shape. It is not the packet schema:
there is no event schema, reason-code schema, typed facts, control-flow structure, completeness
metrics, or canonicalization contract yet. Calling the schema frozen now would make later required
fields either out-of-schema or an unrecorded schema mutation.

## The wrong-at-freeze claim is bounded, not closed

`validate_registry()` successfully catches:

- a start line that does not declare the named function,
- duplicate site ids,
- stage/intent names outside the registries, and
- invalid intent status.

It does **not** establish that a syntactically valid site has the correct stage or intent, that
the site id describes the function's semantics, or that a required site was not omitted. For
example, changing a site's intent from one valid intent to another passes validation; omitting a
required unregistered function also passes. Those are wrong-at-freeze errors. Completeness and
semantic mapping need an independently curated required-site inventory or conformance assertions
against the contract—not comparison with the same `SITES` list used to build the registry.

## Trust discrepancy

Implementing the binding prose (`EXECUTION_UNAVAILABLE` permitted; `ACCEPTED_EXECUTION` withheld)
is correct. Preserve the discrepancy note. Future envelope validation must also validate the
subject path, packet/map/state/instrumentation hash shapes, turn/seat types, and canonical state
coverage before it claims full §4 conformance; this increment does not need to add them if its
status stays partial.

## Required disposition

1. Relabel increment 1 `PARTIAL_FOUNDATION` (or split rollout step 1 into explicitly provisional
   subincrements) and keep acceptance checklist item 1 open.
2. Before freezing step 1, publish the complete registry and complete machine schema, then run an
   independent completeness/mapping review that does not derive expected coverage from `SITES`.
3. Keep the current guard suite; it correctly protects the partial bytes it actually names.

No bot, frozen library, panel, candidate, TestSession, or Arena action was changed.
