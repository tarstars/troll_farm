# Curriculum Level 5 natural-forager D1 protocol — frozen 2026-07-19

## Question and prior boundary

Can the accepted Level-4 controller cross the first active-opponent boundary when interaction is
limited to movement and competition for initial natural fruit?

The complete deterministic Rhea/SchedBot opponent is closed as the first jump after failing the
frozen D0 teacher-feasibility gate at 57.4%.  Its consumed seeds 0--499 may not tune this branch.
The earlier selection protocol explicitly reserved a no-growth natural forager if the complete
baseline proved infeasible.  D1 uses fresh development seeds 500--999.

## Exact opponent policy

Player 1 retains only its reset starter and never issues TRAIN.  The set of eligible plants is
frozen from plant positions present at episode reset.  On every referee turn the starter follows
this deterministic cascade:

1. if carrying fruit and either full or no eligible initial plant currently has fruit, DROP when
   adjacent to its shack, otherwise MOVE to the nearest walkable shack-adjacent cell;
2. if standing on an eligible initial plant with fruit and free capacity, HARVEST;
3. otherwise MOVE to the currently fruited eligible initial plant minimizing navigation distance,
   then `(y, x)`;
4. if no target exists, bank carried fruit as in step 1; otherwise MOVE to its current cell.

The policy may not CHOP, PLANT, PICK, MINE, or TRAIN.  It never targets a crop created after reset.
No randomness, search, time budget, learned policy, reservation, denial score, or tuned constant is
allowed.

Player 0 retains the accepted eight recipes, automatic requested TRAIN, sequential farmer/chopper
control, 240-turn horizon, reward, success contract, observation/action ABI, teacher, and network.

## D1 consumed readiness gates

Run the unchanged teacher on exactly seeds 500--999.  Require:

- at least 90% overall and 85% nontrivial success;
- at least 75% success in every recipe and 80% in every height;
- at least 90% tracked-crop creation and 85% renewable harvest;
- zero opponent workers above one in every episode; and
- positive opponent score in at least 50% of episodes, proving material resource competition.

Also require deterministic repeated batches, unchanged waiting/complete-opponent modes, legal
player-0 masks, and passing focused Rust/Python tests.  Record random legal and the accepted
Level-4 actor zero-shot on the same consumed seeds only after the teacher run.  Those diagnostics
cannot repair a failed teacher gate.

Failure closes this exact forager cascade without threshold or target tuning on seeds 500--999.
Passing D1 permits—but does not itself execute—the exact prospective preflight on still-sealed
seeds 2,019,000--2,020,999 under a separate frozen record.

## Scope exclusions

D1 does not add opponent growth, created-crop interaction, autonomous recipe selection, a third
controlled worker, self-play, mixtures, margin reward, deployment, field qualification, or Arena
writes.  The complete deterministic opponent remains a future strength target, not a teacher or
promotion oracle.
