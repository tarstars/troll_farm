# D35c provenance-aware competitive-bundle oracle — protocol (2026-07-20)

## Question

D35b proves that factorized persistent two-worker bundles have broad production
value but fail only the two opponent-suppression gates.  Selected bundles that
contain `FELL_BANK` are the strongest suppressive family, while the frozen
catalog cannot distinguish a natural/own tree from an opponent-created
renewable lineage.

D35c asks one bounded question: **does exact crop provenance as a target factor
move the same one-bundle hindsight upper bound into the required joint
production/suppression region?**

This is a representation upper bound.  Terminal hindsight and local opponent
identity are non-deployable.  A pass authorizes only a learned assignment
environment; it cannot create a candidate or authorize platform activity.

## Fresh data and controls

- Exact D33 official generator and referee/stall semantics.
- Productive `private2` farm, independent stable-resident safety reference, and
  D34's same eight mechanism opponents.
- Development seeds: signed official seeds **9,300,000--9,300,009**, both seats.
- Sealed confirmation seeds: **9,300,010--9,300,029**.
- First eligible two-worker roots at or after turns 50 and 100, with a complete
  per-task manifest for scenarios that never reach a root.
- Exact common roots and opponent prefixes for the generic and enriched
  catalogs.  Control is the uninterrupted warmed farm.

## Exact prefix provenance

Initial plants are `natural`.  Before every prefix referee step, record each
side's exact `PLANT` claims from the issuing unit's pre-turn cell.  When a new
post-step plant appears, label it:

- `own` for an exclusive analyzed-side claim;
- `opponent` for an exclusive rival claim;
- `ambiguous` when both sides made a successful same-cell claim; or
- `natural` only for plants present in the initial board.

Remove attribution when its plant disappears.  Never resolve an ambiguous plant
in favor of either side.  At every root, the attributed cell set must equal the
live plant cell set exactly.  Both seat orientations and simultaneous-plant
tests are required before outcomes.

## Frozen paired catalogs

Training is removed from both catalogs.  D35b observed zero successful train
goals and selected `train=none` at all 238 changed roots, so retaining three
global variants would triple this target-factor experiment without changing the
paired upper bound.

### Generic control catalog

Reproduce the D35b no-train unit grammar and ordering exactly:

- `KEEP`, `BANK`, `FELL_BANK`, `HARVEST_BANK`, `RENEW`, and `MINE_BANK`;
- at most two generic targets per acquisition kind per worker;
- collision-safe Cartesian products;
- reward-rate, ETA, then role/target-key order; and
- at most 96 generic joint bases, with all-`KEEP` represented by control.

### Provenance-aware extension

For `FELL_BANK`, `HARVEST_BANK`, and `RENEW`, independently retain the two best
eligible `opponent` targets and the two best eligible `ambiguous` targets per
worker under the same ETA/reward/cell order.  Merge exact target duplicates with
the generic unit jobs; provenance is an immutable target attribute, not a new
unit role.

Form additional collision-safe joint bases containing at least one attributed
competitive target and absent from the generic base set.  Order them by:

1. more `opponent` targets;
2. more `ambiguous` targets;
3. summed predicted reward rate;
4. maximum ETA; and
5. role/ownership/target key.

Retain at most 64 additional competitive bases per root.  The enriched oracle
is the exact superset of control, generic bases, and competitive bases.  Both
oracles use the D35b terminal-margin tie break: control, fewer overrides, then
lexicographic key.

Execution, invalidation, deterministic banking, planting, completion, warmed
farm continuation, and warmed opponent continuation are unchanged from D35b.
Record target ownership for both worker factors and whether each plan belongs to
the generic or competitive extension.

## Integrity gate

Before outcome selection require:

1. all 10 × two-seat × eight-opponent tasks represented in a scenario manifest;
2. at least 240 exact eligible roots and 10,000 total non-control bundles;
3. byte-identical one-seed row and scenario-manifest repeats;
4. exact control identity, generic-subset identity, and reference consistency;
5. zero duplicate options/keys, target collisions, invalid direct commands,
   attribution-cell mismatches, or workers above three;
6. generic bases are an exact subset of enriched bases at every root;
7. at least 80 roots expose an attributed competitive target and at least 5,000
   competitive extension bundles; and
8. at least 20 roots expose `opponent` targets in each of `FELL_BANK` and one of
   `HARVEST_BANK`/`RENEW`; ambiguous targets are reported separately and do not
   count toward those minima.

## Frozen development upper-bound gate

Select generic and enriched hindsight oracles independently at every root.  The
provenance-aware representation passes only if all conditions hold:

1. a competitive extension bundle is selected on at least 15% of roots and at
   least 40 roots;
2. enriched mean margin gain over farm is at least +20;
3. enriched mean own-score delta from farm is at least -20;
4. enriched mean opponent-score delta from farm is at most **-20**;
5. relative to resident, enriched own-score advantage is at least +68 and
   opponent-score excess is at most **+65**;
6. versus the paired generic oracle, the enriched oracle reduces opponent score
   by at least 10 points on average and never reduces mean margin;
7. all eight opponent-family enriched mean margin gains are nonnegative and at
   least six are +10 or better;
8. selected competitive bundles span at least four opponent families, at least
   two role tuples, and at least ten exclusive-`opponent` targets; and
9. catastrophe frequency and negative-margin mass do not exceed either the farm
   control or the paired generic oracle.

If every gate passes, freeze the unchanged 20-seed confirmation.  Otherwise
leave confirmation sealed, close one-shot target-provenance enrichment, and
advance to repeated job-boundary control.  Do not tune target quotas, extension
capacity, roots, thresholds, or ownership treatment on D35c outcomes.

## Planned artifacts

- runner: `rust/src/bin/d35c_provenance_competitive_bundle_oracle.rs`;
- analyzer: `cgauto/analyze_d35c_provenance_competitive_bundle_oracle.py`;
- focused attribution, catalog-subset, execution, and analyzer tests;
- development rows, task manifest, JSON analysis, and written verdict.
