# Opponent-crop harvest-on-contact local prototype — frozen protocol, 2026-07-19

## Scope

This is the authorized follow-up to the passed exact-state diagnostic.  It reuses the fully
consumed generated seeds 1300--1359 and cannot qualify a candidate.  Every seed runs both seats
against the same eight existing deterministic local opponents, for 960 scenario cells.

Each cell runs three complete policies from the identical initial map:

1. exact resident;
2. exact opponent-crop `b100_e6`; and
3. `b100_e6` plus the one-action harvest-on-contact residual.

The primary estimand is harvest residual minus exact `b100_e6`.  Resident comparisons are retained
to expose destructive interaction but do not substitute for the incremental comparison.

## Frozen implementation

- Keep provenance, bonus 100, ETA limit 6, start turn 1, and minimum-seen 1 unchanged.
- Run the ordinary complete assignment and movement-conflict resolution first.
- Rewrite only a selected `CHOP id` when that unit currently occupies a ripe tracked opponent crop,
  has empty cargo, and has positive harvest power.
- Rewrite at most once while that crop generation remains alive.
- Do not alter movement, target scores, training, planting, banking, or any other action.

## Frozen continuation gate

All checks are required before this mechanism may receive a new prospective protocol:

1. at least 80/960 cells activate and at least 100 harvest rewrites occur, with activation against
   all eight opponents;
2. incremental mean margin and five-percent-trimmed mean margin versus `b100_e6` are both strictly
   positive, with at least as many favorable as unfavorable cells;
3. the mean of the 60 per-seed mean-margin deltas is strictly positive and its five-percent-trimmed
   mean is strictly positive;
4. mean own-score delta is nonnegative and mean own-wood delta is nonnegative;
5. mean opponent-score delta is nonpositive;
6. at least six of eight opponent-specific mean-margin deltas are nonnegative, and the worst is at
   least -2 points.

Failure closes the one-action harvest residual.  Do not add timing, fruit-count, tree-kind,
health, score-state, or distance filters on these results.  Such filters would tune on consumed
arena-derived diagnosis and consumed local seeds.

A pass still authorizes no fresh games, packaging, submission, or resident change.  It would only
justify writing a separate prospective discovery/replication protocol on untouched data.
