# Ownership-aware complete economy — frozen protocol, 2026-07-19

## Hypothesis

The top `lean_m2c2h0k2` farm is highly productive and keeps 97.15% of the wood from its planted
trees, but it stops contesting the opponent's renewable loop.  A single closed-loop controller can
retain the private near-shack farm while diverting its chopper to an attributed opponent crop only
when the **race-conditioned margin value per complete work cycle** exceeds the farm target's own
conversion value per cycle.

This is not the rejected resident dual-value rule.  It has no flat bonus or multiplier, does not
double every reachable crop, and cannot override banking, funding, planting, training, or idle
states.  It explicitly prices the displaced farm target and counts denial only in a race we are
predicted to win.

## Fixed controller

Start from the exact `lean_m2c2h0k2` complete policy: at most two workers, one `2/2/0/2` chopper,
farm radius three, farm cap twelve, two protected banana seed trees, and unchanged starter loop.

Track tree provenance from state transitions.  A newly appeared tree is opponent-created unless
its cell was the target of our immediately preceding PLANT attempt.  Natural initial trees are
never crops.

For the pure chopper only:

1. Ask the unchanged farm controller for its complete command first.
2. Continue unchanged unless that command targets an existing tree by CHOP-at-current-cell or
   MOVE-to-tree, the chopper has free capacity, and the normal endgame-bank guard is inactive.
3. For a tree, define our cycle turns as
   `ceil(path_to_tree/ms) + ceil(health/chop) + ceil(path_tree_to_home_drop/ms) + 1 DROP`.
   Collectable wood is `min(tree_size, free_capacity)`.  Ordinary value rate is
   `4 * collectable_wood / cycle_turns`.
4. Consider only attributed opponent-created trees of size at least two that can finish and bank
   before turn 300.
5. Estimate the fastest opponent chopper with positive chop power and free capacity.  Denied wood
   is `min(tree_size, enemy_free_capacity)` only when our travel-plus-chop completion is strictly
   earlier than that enemy completion.  Otherwise denied wood is zero.
6. Opponent-crop margin rate is
   `4 * (our_collectable_wood + denied_wood) / our_cycle_turns`.
7. Override the base farm target only when the best opponent-crop rate is strictly greater than the
   base target's ordinary rate.  Ties preserve the farm command; crop ties use lexicographic cell
   order.  Re-evaluate each turn from current state.

No coefficient, ETA cap, turn gate, commitment, extra worker, action type, farm parameter, or
fallback threshold may be added.

## Data split and controls

- Consumed seeds 0--29 may be used only for implementation integrity: exact resident atom, exact
  same-build farm-shadow command parity inside the wrapper, provenance accounting, deterministic
  repeat-run identity, and runtime.  The older complete-economy TSV is informational only because
  several research sparring controllers/engine paths have evolved; no historical outcome match is
  required.  This integrity repair was frozen before opening any 1660+ seed.
- Discovery: newly designated seeds 1660--1719, both seats, the same eight structural opponents;
  960 common cells for resident, unchanged farm, and ownership-aware farm.
- Confirmation: seeds 1720--1779 remain unopened unless the unchanged discovery controller clears
  every gate.
- Run with 20 workers.  Report complete score/margin/wood, worker count, activation/displacement,
  first activation, opponent identity, and crop provenance conversion.

## Discovery gates

All integrity checks must pass, then ownership-aware versus exact resident must satisfy:

- mean margin delta at least +10 and 5%-trimmed mean at least +5;
- mean own-score delta at least +50 and mean own-wood delta at least +10;
- at least six of eight opponent-specific mean margin deltas nonnegative;
- worst opponent mean margin delta at least -5;
- adaptive-Gold mean margin delta nonnegative;
- at least 200/960 activated cells overall and 30/120 against adaptive Gold.

Mechanism preservation against unchanged farm on adaptive Gold additionally requires mean opponent
score delta at most -25 while mean own-score delta is at least -50.  These conditions require
suppression without simply abandoning the productive economy.

## Confirmation and stop rule

Run the same single controller on 1720--1779 only after a full discovery pass.  Confirmation uses
the same gates, except mean/trimmed margin floors are both +10.  Any failure closes this exact
race-conditioned representation without formula, threshold, farm, or worker tuning.  A complete
pass qualifies only for source packaging and a field-prefix mechanism audit; it does not authorize
arena submission.
