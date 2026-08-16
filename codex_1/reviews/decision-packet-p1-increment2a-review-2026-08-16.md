# P1 increment 2a inventory review — 2026-08-16

Verdict: **REVISION_REQUIRED** before this can be used as the §5.4 required-site
inventory or as a coverage denominator.

Reviewed artifact: `e43d000b`, including `claude_1/decision_packet/inventory.py` and
`required-site-inventory.json`.  The generator self-test passes 7/7 and the enumeration
does not derive its candidate set from `registry.SITES`; that independence property is
worth preserving.

## Blocking findings

1. **The reported 132/249 (53%) “named” coverage is not subsite coverage.**  A registry
   entry spanning a function causes every candidate found inside that function to be
   marked covered.  One function ID therefore “names” its `Candidate` constructors,
   filters, returns, and arbitration operations even though none has its own stable ID.
   This contradicts the §5.4 unit of account: each required semantic subsite needs a
   stable identifier and exact mapping.  With 22 registry entries, the output cannot
   substantiate 132 individually named sites.
2. **The syntactic proxies are neither a sound nor complete semantic inventory.**  A
   `Candidate { ... }` constructor is not equivalent to every score term (for example a
   composite score can contain a base wood term and a denial bonus in one constructor).
   Conversely, every function definition is not a policy generator.  `.filter`,
   `.retain`, `continue`, explicit `return`, and `.max_by`/sort patterns omit common
   conditional gates and arbitration forms while also counting non-policy mechanics.
3. **The JSON labels these proxy counts too strongly.**  Until the generated candidates
   are curated against source semantics, they must be described as review candidates,
   not the required-site inventory or its coverage percentage.

## Required revision

- Separate `containing_registry_site` from `named_subsite`; only the latter counts as
  §5.4 coverage, with its own stable ID and exact range/anchor.
- Expand or manually curate the candidate set by semantic class: generators, each score
  term, eligibility/filter gates, early exits, and arbitration/tie-break sites.
- Report proxy recall limitations and an explicit unresolved queue; do not publish a
  coverage percentage until every numerator item is mapped at the same granularity as
  the denominator.
- Retain the present anti-circularity/self-tests and add a test proving that a
  whole-function registry span does not cover its unnamed child candidates.

