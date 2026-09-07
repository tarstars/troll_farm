# Frozen plan — event-timed finite fruit service (2026-09-07, run 060006Z)

Frozen BEFORE any source edit. Prior dispatch family archived under `archive/`
(`claude_candidate_dispatch_core.rs` 1741a60d, tests fe543c6c).

## Reproducer (done first, real unmodified map, real referee, adaptive opponent)

`repro/` (run-local Cargo package, run-local target
`/data/separate_troll_farm-working/tmp/cargo-target-repro`) replays the candidate
`eb14e6cb` as the actual seat against the existing 12 adaptive opponents on the
unmodified development maps 9947500..07, in map/seat/opponent/turn order, and at
every turn recomputes what `fruit_service`/`jobs_for` promise against what the
referee's own ripening law can physically deliver.

FIRST occurrence — `REPRODUCER.txt`, map_seed **9947503**, seat **1**, opponent
**5 (mybot)**, turn **250**, defect *"`bill_units` can claim a full first load
before fruit exists"*:

  worker 5 @(4,3) ms1/cc2/hp1/chop1, free=2, standing ON
  BANANA @(4,3) size=4 fruits=1 cooldown=4 (effective cooldown 4, near water)
  `fruit_service` promise: banked=6, busy=41, turns=41, first bank offset **9**
  `jobs_for` bill_units[BANANA] = **2**
  referee truth: the first load can hold **1** fruit (harvest window
  `+1 => s4f0c3`, `+0 => s4f0c2`); to load 2 the worker must stay **5** turns,
  so the first bank lands at offset **12**, not 9.
  Feasible alternatives for this worker on this tree: HARVEST (6 pts / 41 busy)
  vs CHOP (2 wood -> 8 pts).

Full referee state, plant cooldowns/ripening and the next 20 real referee turns
(moves and banking) are in `REPRODUCER.txt`.

## One candidate: event-timed finite service

1. `ripen`: the referee's `tick_plants` law as one step (cooldown down; on zero,
   one size or one fruit capped at `MAX_FRUITS`, cooldown reset).
2. `fruit_service` takes the plant's ACTUAL `cooldown` and simulates the real
   schedule: travel out, harvest `hp` per turn from what is actually hanging,
   carry home, DROP, repeat from the door — the plant ripening on every one of
   those turns. It returns the truly deliverable `(banked, busy, turns,
   first_bank_time, first_load)`. No trip is counted that cannot be banked
   inside the horizon. There is no waiting on an empty tree, so no empty
   HARVEST can be offered, and `busy` is real worker time, not a free lifetime.
3. `jobs_for` drops the `plant.fruits > 0` gate and offers the service whenever
   fruit exists at ARRIVAL; `bill_units` carries the projected FIRST load only,
   and `bill_busy` its real first bank time.
4. `service_reservations` keeps the worker identity of the commitment
   `(cell, value, unit id)`; the reserved value is that worker's executable
   service, released unchanged on hp0 roster/contest/unreachable/own grove/
   endgame.
5. `plant_job` prices a fresh tree with its real post-ripening cooldown.

No new coefficient, no tuning scan, no second variant.

## Comparison and decision rule

Baseline: policy-flat parent `95ee691e`. 192 known pairs 9947500..07, 12 adaptive
opponents, both seats, `ALLOW_ANY_MAP_SEED=1`; all 192 baseline command arrays
verified against gap `20260906T210944Z-3184968-1`. Positive whole-panel W+0.5D
AND 0 candidate issues supports further evaluation. 142.5/146.5 are descriptive.

## Prerequisites before the panel (all required, else no panel)

Focused fixtures pass under actual Rust 1.90; compact <= 100,000 UTF-16;
original == pruned == compact on the 16 archived streams; per-turn max < 50 ms
measured idle; run-local Cargo target built after the source freeze.
