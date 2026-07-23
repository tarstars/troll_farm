# D87a fresh-harvest regeneration commitment — frozen protocol (2026-07-21)

## Question

D86 rejects a static opening selector for yaichi's renewable mode, but exact field evidence shows
that the stable resident already reaches the necessary local state: in the D61p target union it
issues HARVEST in 26/60 games and never follows with `HARVEST -> PLANT`.  Does converting only an
already-selected, non-orchard HARVEST into the resident's existing regeneration lifecycle improve
the complete two-worker policy?

This is not the closed sparse-farming controller.  It creates no map/tree-count gate, selects no
farmer, seeks no new source, and changes no current HARVEST decision.  It changes the continuation
only after the resident has independently selected the immediate harvest.

## Frozen source and intervention

Start from `rust/src/bin/yamo_orchard_live.rs`, SHA-256
`ab7a290d6e008f5cc2e1c11c9ea414cf4ead8fd3c371003943661e21b0aba84e`.  Preserve
`SecureOrchardBot::new()` exactly as control.  Add one research constructor whose sole semantic
switch is:

1. after the inner resident has selected commands, inspect each selected immediate `HARVEST id`;
2. require that the unit is standing on a live, ripe plant, has positive harvest power and free
   capacity, and the plant is not the secure wrapper's protected mother;
3. remember that visible plant species in the already-existing per-unit regeneration commitment;
4. on the next observed state, the unchanged commitment reconciler keeps the commitment only if
   the worker actually carries that species (or is completing the existing plant/chop/bank
   lifecycle);
5. the unchanged persistent-regeneration candidates choose the feasible empty planting cell,
   PLANT, conversion CHOP, and bank return, or bank directly when no feasible lifecycle exists.

PICK commitments, opening TRAIN, worker specs, candidate scores, plant-cell enumeration, target
ties, secure-orchard setup/forced HARVEST/DROP stream, opponent-crop contact rewriting, movement
resolution, and every other command remain unchanged.  In particular, an outer forced mother
HARVEST is not an inner selected HARVEST and cannot create this commitment.

No turn, score, map, opponent, ownership, distance, species, fruit-count, crop-count, or history
threshold may be added after outcomes are seen.

## Frozen implementation telemetry and parity

The candidate runs beside an exact-resident shadow on its own game states.  Record selected fresh
HARVEST commitments, first commitment turn, command mismatches before the first commitment,
candidate/shadow divergence turns, successful own `HARVEST -> PLANT` transitions, successful
plants by species, fruit and wood provenance, scores, margins, worker count, action hashes, and
terminal state.

Require unit tests showing:

- the default constructor remains command-identical before and after the new code;
- PICK behavior is unchanged;
- immediate nonprotected HARVEST creates exactly one species commitment;
- protected-mother and failed/unripe HARVEST do not create one; and
- a harvested carried fruit uses the pre-existing regeneration candidate path.

## Frozen prospective panel

Use previously unopened official maps `9,914,000--9,914,015`, both seats, and all eight unchanged
complete-economy opponents (`compact_gold`, adaptive Gold, `gold_elite`, `mybot`, `printer_bot`,
`sched_bot`, `script_boss`, `silver_boss`).  This is 256 paired resident/candidate tasks and 512
rows per repeat.  Run the full matrix twice with 20 threads, sort by
`(seed, seat, opponent, profile)`, and require byte identity.

Maps `9,914,016--9,914,031` are sealed confirmation and remain unopened unless every discovery
gate passes.  Do not reuse the consumed sparse-farming panel or D86 replay labels for value
selection.

## Frozen integrity and activation gates

All must hold before interpreting paired value:

1. complete byte-identical repeats and complete 300-turn-or-stalled games;
2. exact resident repeat parity, zero unknown/invalid commands, and at least 95% assigned fruit and
   wood provenance;
3. zero candidate/shadow command mismatch before the first selected fresh-HARVEST commitment;
4. every inactive candidate task is terminal/action/state-identical to resident;
5. every commitment names the exact visible species under an eligible worker, and no protected
   mother creates a commitment;
6. at least 32/256 tasks commit, at least 24 produce a successful `HARVEST -> PLANT`, both seats
   activate, and at least six opponent families activate; and
7. candidate worker count always equals resident worker count for the paired task.

Integrity failure permits only a mechanical repair.  Activation failure closes this action-local
bridge without widening eligibility.

## Frozen value and safety gates

On all 256 paired discovery tasks, require all:

1. overall mean margin delta at least +0.5 and map-cluster 95% lower bound nonnegative;
2. active-task mean margin delta at least +4.0 and mean own-score delta at least +2.0;
3. strictly more active tasks improve than regress, with at most 35% active regressions;
4. at least five of eight opponent-family mean deltas are nonnegative and the worst is at least
   -5.0;
5. active tenth-percentile margin delta at least -12 and active worst at least -30;
6. crop creation remains 100%, catastrophic losses (`margin <= -100`) do not increase, and
   negative-margin mass is at most 100% of resident; and
7. added successful plants and own-crop harvested fruit are both positive while own final wood
   falls by at most one per active task on average.

Report sparse versus sustained commitment cohorts separately so the secure-orchard stream cannot
hide a harmful general continuation.

## Decision rule

- **All discovery gates pass:** open the sealed 16-map confirmation under identical gates except
  active mean margin >= +3 and own score >= +1.  Passing confirmation permits source-size/runtime
  qualification, not submission.
- **Integrity or accounting failure:** repair only the defect and repeat unchanged.
- **Activation failure:** close fresh-HARVEST commitment without broadening to forced orchard,
  opponent-contact, MOVE-to-harvest, banked fruit, or a map selector.
- **Value/safety failure:** reject the candidate and close this direct semantic bridge.  Do not
  tune cell choice, species, turn, or commitment lifetime on consumed maps.

No branch authorizes TestSession, submission, resident replacement, Arena writes, or sealed replay
access.
