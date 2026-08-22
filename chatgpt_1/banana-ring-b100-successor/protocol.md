# Banana-ring + b100/e6 successor — fast qualification and publication protocol

Prepared UTC: 2026-08-02T16:32:00Z  
Base commit: `68ed41a5e7ac14a703aedf36a92b19abd83665cb`  
Status: **PRE-LOCK SUCCESSOR SPECIFICATION — NO ARENA AUTHORITY**

## 1. Owner-observed defects in the live full factory

The live owner-override candidate is agent `6590083`, submission `41081195`, source
`local_codex_1/banana-factory-b100-owner-override/banana-factory-b100-e6.arena.rs`,
99,440 bytes, SHA-256
`2d164ecbaf8a06092f91fffd253f295ec6d6233f2094ac707eda152b28cb2533`.

The owner inspected actual play and identified four concrete defects:

1. the banana plantation spreads too far from the tent and becomes too expensive for our
   two-worker roster to cut;
2. ripe bananas are recycled into more planting instead of being deposited in the tent;
3. placement ignores the established tent-gate/front-door geometry;
4. all planted bananas are treated as one farm class instead of separating transient wood trees
   from persistent seed mothers.

These observations match the source:

- `banana_factory_plant_cell` scans the whole walkable home half rather than a bounded ring;
- `banana_factory_initial_budget` is the full banked BANANA count, with no geometry-capacity cap;
- a successful own-crop harvest sets `banana_factory_seed_from_harvest=true`, after which a
  carried banana is routed to another plant cell whenever one exists;
- `banana_factory_wood_command` protects only one reserve and does not assign positional roles.

The successor is therefore **not** another threshold on the full factory. The geography and
lifecycle are replaced.

## 2. Required behavior

### 2.1 Gate-aware tent ring

The banana farm is the up-to-eight Chebyshev-distance-1 cells around our tent and nothing else.
A cell is eligible only when it is walkable, reachable, and accepted by the existing front-door
logic.

Reuse the historical `v1.54.0-frontdoor` / `v1.56.0-ringfarm` rule exactly:

- collect walkable orthogonal tent gates;
- if fewer than two gates exist, there is no straddle decision;
- compute true BFS distances between gates;
- if the maximum pairwise gate distance is at most `8`, the map is open and all reachable ring
  cells are eligible;
- otherwise choose one viable gate with at least four walkable cells within radius `2`, maximizing
  BFS distance from the opponent tent, deterministic lexicographic tie-break;
- on a straddling map retain only ring cells at BFS distance at most `2` from that chosen gate.

No banana may be planted outside this ring. The bootstrap goal is
`min(initial bank BANANAs, eligible ring-cell count)`; a large initial bank must never cause a
PICK/DROP retry loop after the ring is full.

### 2.2 Positional roles

For an eligible ring cell relative to our tent:

- **diagonal** (`|dx|=|dy|=1`) — mother tree: harvest fruit, keep standing, use its fruit for an
  empty ring cell when necessary, and bank surplus;
- **orthogonal** (`|dx|+|dy|=1`) — cut tree: fell at size at least `2`, bank wood, and make the
  empty cell eligible for replant.

Diagonal mothers are excluded from ordinary own chopping. Release them only when either:

- at most `34` game turns remain; or
- an opponent troll is within BFS distance `4` of our tent (local raid).

All eligible diagonal cells are protected, not merely one `banana_factory_reserve` cell.

### 2.3 Collection and seed use

The starter may harvest ripe BANANA fruit only from eligible diagonal mothers. After harvest:

- an empty eligible ring cell exists → plant one banana there;
- the ring is full → return to an orthogonal tent gate and `DROP` the banana into the tent.

A bank `PICK ... BANANA` is legal only if:

- an empty eligible ring target exists;
- that target is within at most two movement turns of the starter’s current position;
- no ripe diagonal mother is current or adjacent and harvestable;
- bank stock is positive and carry capacity is free.

Thus harvesting a nearby mother beats fetching a tent banana, and a full ring cannot consume
another bank seed.

When the observed starter carry returns to zero with no pending harvest or plant, clear the
`seed_from_harvest` flag. This prevents a banked surplus banana from contaminating the provenance
of a later bank bootstrap.

### 2.4 Wood and suppression ordering

For every trained worker, regenerate its wood/logistics command through the factory wrapper on
every turn; do not retain an arbitrary resident MOVE merely because its verb is nominally a wood
verb.

Priority is frozen:

1. known opponent-created crop with ETA at most `6` under the current flat `+100` b100/e6 policy;
2. eligible orthogonal ring BANANA at size at least `2`;
3. the current resident’s remaining chop/bank command;
4. `WAIT` only if none is legal.

Before endgame/raid, remove every diagonal-ring tree candidate from the trained worker’s chop
vocabulary and reserve all diagonal landing cells against non-starter movement.

## 3. Fast implementation route — reuse the successful publication pipeline

Do **not** rebuild packaging infrastructure. The immediately preceding owner override already
proved the following path:

1. exact formatted parent
   `rust/src/bin/yamo_orchard_live.rs`, SHA-256
   `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
2. exact fallback
   `candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`, SHA-256
   `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`;
3. fail-closed full-source constructor injection;
4. `compact_rust_source.compact`;
5. factory-aware specialized slimmer based on
   `cgauto/slim_banana_factory_b100_candidate.py`;
6. embedded semantic tests;
7. standalone optimized `rustc`, empty-input exit, source-size check;
8. exact full-source/Arena-source equality on the existing eight streams: seeds
   `1300..1303`, both seats, opponents `ringfix3` and `taskplan`, 2,400 commands;
9. stderr and interactive-latency checks;
10. exact artifact SHA, fresh IDE/fallback recovery, controller-only submission.

The old general specialization must not be reused: it already compiled under the size limit but
failed all eight equality streams, first at turn 7. Clone the accepted factory-aware slimmer and
change only its two command-method specializations plus the new ring helpers.

### Files/methods that change in the generated research source

- add constructor `banana_ring_opponent_crop_b100_e6`;
- add gate-aware ring helpers and role predicates;
- replace `banana_factory_plant_cell`;
- replace `banana_factory_promote_reserve` so reserve candidates are diagonal mothers only;
- replace `banana_factory_harvest_target` so only diagonal mothers are harvested;
- replace `banana_factory_starter_command` with empty-ring/immediate-PICK/bank-surplus logic;
- replace `banana_factory_wood_command` with suppression → orthogonal cut → resident ordering;
- replace `banana_factory_commands` so every non-starter uses the corrected wood command and all
  diagonal cells are protected;
- add the post-DROP `seed_from_harvest` reconciliation;
- switch standalone `main` to the new constructor.

No shared formatted source edit is necessary: generation is from its exact bytes, and the sacred
file remains unchanged.

## 4. Focused semantic gates

Retain all 23 tests that passed for the published factory and add at least these tests:

1. `plant_target_is_never_outside_tent_ring`;
2. `large_initial_bank_is_capped_by_ring_capacity`;
3. `full_ring_banks_surplus_instead_of_spreading`;
4. `no_pick_when_ring_is_full`;
5. `no_pick_when_target_is_more_than_two_move_turns`;
6. `nearby_ripe_mother_harvest_beats_bank_pick`;
7. `diagonal_is_harvested_but_orthogonal_is_not`;
8. `orthogonal_size_two_is_chopped`;
9. `diagonal_is_not_chopped_outside_endgame_or_raid`;
10. `diagonal_is_released_in_endgame`;
11. `diagonal_is_released_under_local_raid`;
12. `frontdoor_excludes_far_side_ring_cells`;
13. `urgent_eta6_opponent_crop_beats_orthogonal_cut`;
14. `own_ring_plant_is_not_classified_as_opponent_crop`;
15. `no_pick_drop_or move_retarget_oscillation`.

Kill immediately on a plant outside the eligible ring, a diagonal ordinary chop, a full-ring
bank PICK, failure to DROP surplus, an own-crop provenance error, a hard b100/e6 displacement,
or any invalid/runtime command.

## 5. Reused mechanical publication gate

The successor must repeat the exact accepted preflight shape:

- all embedded tests pass;
- standalone compile and empty-input exit pass;
- Arena source `<100,000` bytes;
- research vs Arena command streams exact on all eight existing streams;
- zero stderr;
- p95 latency at most `1.05 ×` the current accepted pipeline’s p95, unless the absolute result is
  still below `2 ms`; maximum below `10 ms`;
- mutated parent is rejected;
- sacred source SHA remains exact.

Because the pipeline and harness already exist, these are reruns, not new infrastructure work.

## 6. Short behavioral/value smoke before any handoff

Use open/consumed data only. Compare three arms on a small paired block:

- exact b100/e6 fallback;
- currently live unbounded factory+b100/e6;
- bounded ring successor+b100/e6.

Required behavioral observations:

- maximum own banana distance from tent is exactly one Chebyshev step;
- successful plants never exceed eligible ring capacity concurrently;
- at least one diagonal mother is established when geometry permits;
- diagonal harvested BANANAs have positive tent-DROP count once the ring is full;
- orthogonal successful chops and corresponding wood deposits are positive;
- no diagonal ordinary chops;
- no increase in ETA<=6 opponent-crop misses;
- no new door deadlock, repeated command, or stalled cargo cycle.

For speed this first smoke may use the existing eight streams plus a capped paired simulator batch,
but it must report own score, opponent score, margin, catastrophes, and negative-margin mass. A
severe tail regression or failure of any behavioral invariant closes the candidate before Arena.

## 7. Arena discipline

This protocol authorizes no mutation. Only `local_codex_1` may submit, after:

- a pushed exact artifact and complete preflight;
- owner notification naming that the current live full factory will be replaced;
- exact fallback verification;
- no other cycle in flight;
- a recorded decision on whether the current full-factory observation is complete enough to end
  its read-only monitoring window.

One submission, no ambiguous retry. Record agent/submission identity and immutable checkpoints.
Restoration target remains the exact 64,522-byte b100/e6 fallback unless the owner explicitly
selects a different resident.

## 8. Completion states

- `MECHANICALLY_READY`: compile/tests/equality/size/runtime pass; no Arena implication.
- `SMOKE_QUALIFIED`: all mechanical and bounded behavioral/value smoke gates pass.
- `CLOSED`: first failed invariant recorded; no threshold tuning on the same block.
- `ARENA_HANDOFF`: controller receives exact artifact/hash/fallback and owner direction.

The current live full factory is evidence and a source parent only. It is not the geometry to
repair incrementally by increasing chop power or changing a plantation-size threshold.