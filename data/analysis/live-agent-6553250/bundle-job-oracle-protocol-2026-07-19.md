# Persistent job-bundle oracle — frozen representation protocol, 2026-07-19

## Purpose

Test whether persistent, completion-valued work is a materially better control representation than
the resident's one-command candidate scores before building or fitting another policy.

This is an offline hindsight upper-bound audit. It cannot become a candidate, and its use of the
actual local opponent family is deliberately non-deployable. Its only question is whether the
fixed job grammar contains enough counterfactual value to justify a later selection problem.

## Why this is a new discriminator

The closed resident residual changed one MOVE target, held it for at most eight turns, and valued a
4/16-turn leaf. The closed orchard market repriced an immediate ripe-mother action but did not
commit to the alternative work or preserve the recurring location option. This audit instead:

- executes a complete multi-action job until success, invalidation, or terminal time;
- includes travel, direct work, cargo, banking, and then the exact resident continuation;
- scores the actual terminal game under exact stall semantics; and
- measures a hindsight grammar upper bound, with no online runtime or learned selector claim.

## Frozen root states

Use consumed seeds 0--9, both seats, and all eight fixed opponents. Replay the exact resident and
capture its state and cloned internal controller at the first eligible decision at or after turns
50, 100, and 150. A root is eligible when at least one own unit's exact resident action is MOVE or
WAIT; never interrupt TRAIN or a unit already issuing CHOP, HARVEST, DROP, PICK, PLANT, or MINE.

The control branch continues the cloned exact resident from that root. Every alternative changes
one eligible unit and completes one job before returning it to the same resident continuation.
Other units always use their exact resident continuation.

## Frozen job grammar

Enumerate at most five deterministic targets per job kind and unit, ordered by completion ETA,
terminal reward, and cell:

1. **FELL_BANK(tree):** move to a reachable live tree, CHOP until the tree disappears or the unit
   first gains wood, then move to the nearest reachable own door and DROP all cargo.
2. **HARVEST_BANK(tree):** move to a reachable currently ripe tree, HARVEST once when empty with
   capacity, then move to the nearest reachable own door and DROP all cargo.
3. **BANK:** if carrying anything, move to the nearest reachable own door and DROP all cargo.

A job terminates without further override when its target becomes invalid, its required capability
is absent, its intended cargo cannot be obtained, or it cannot finish within turn 300. Direct
commands are emitted only when legal in the current state. Target ties are lexicographic. Do not
add planting, training, species, ownership, opponent, turn, or score coefficients after outcomes.

The first audit intentionally excludes seed-to-crop and training bundles: a simpler current-asset
grammar must first prove that persistent completion and terminal valuation matter. Passing expands
the representation; failing closes this resident-local job layer and forces a complete economy
grammar rather than another target catalog.

## Output and integrity

For every root/option record seed, seat, actual opponent, checkpoint, root turn, unit, job kind,
target, predicted completion ETA, terminal own/opponent score, margin, wood, terminal turn, job
completion/invalidation/timeout, actions overridden, and delta versus the exact control branch.

Require:

- all 160 resident games and every eligible frozen root represented;
- exact control terminal outcomes equal the uninterrupted resident outcome;
- no root captured before its checkpoint and no direct resident work interrupted;
- every command legal by construction and every completed job satisfies its cargo/bank invariant;
- option ordering and row output byte-identical in a 20-worker repeat; and
- no fresh seed, arena read, controlled game, or submission write.

## Frozen representation gate

At each root, the oracle selects control or the largest terminal margin option. Control makes every
oracle delta nonnegative by definition, so the audit must clear magnitude and breadth, not merely
sign:

- at least 240 eligible roots and at least 2,400 valid non-control options;
- non-control selected on at least 10% of roots;
- overall mean oracle margin delta at least +8.0 per root;
- mean selected-root delta at least +20.0;
- at least two job kinds selected in at least ten roots each;
- mean oracle delta at least +3.0 in six of eight opponent families; and
- the weakest opponent-family mean nonnegative.

A pass authorizes a larger consumed-data teacher and expansion to production/training bundles. It
does not authorize a deployable selector. A fail closes resident-local one-job target redirection;
do not tune target count, checkpoints, or job termination on this block.

