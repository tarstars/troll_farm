# Banana-ring successor — implementation delta against the published factory source

Base: `68ed41a5e7ac14a703aedf36a92b19abd83665cb`  
Purpose: minimize local implementation time by modifying only the already proven publication path.

## A. Start from the accepted publication artifacts

Reuse:

- `cgauto/make_banana_factory_b100_candidate.py` for exact parent/control checks and constructor
  activation;
- `cgauto/slim_banana_factory_b100_candidate.py` for the compiler-proven dead-item inventory and
  factory-aware specialization;
- `local_codex_1/banana-factory-b100-owner-override/` for filenames, sidecars, build manifest,
  compile/equality/latency commands;
- `data/analysis/live-agent-6553250/owner-banana-factory-b100-preflight-20260802T155654Z.json`
  for the exact eight-stream gate shape.

Do not reuse the rejected old-general slimmer path.

## B. Source transform

Generate from the exact sacred formatted source; never edit it in place.

### B1. Constructor

```rust
pub fn banana_ring_opponent_crop_b100_e6() -> Self {
    let mut bot = Self::banana_seed_factory();
    bot.inner.opponent_crop_bonus = 100;
    bot.inner.opponent_crop_eta_limit = 6;
    bot.inner.opponent_crop_start_turn = 1;
    bot.inner.opponent_crop_min_seen = 1;
    bot
}
```

Standalone `main` uses this constructor.

### B2. Ring/front-door helpers

Add private helpers on `SecureOrchardBot`:

```rust
const RING_PICK_STEPS: i32 = 2;
const RING_RAID_R: i32 = 4;
const RING_LIQUIDATION_TURNS: i32 = 34;
const CHOKE_THRESHOLD: i32 = 8;
const MIN_FARM_CELLS: usize = 4;

fn ring_is_diagonal(view: &GameState, cell: Cell) -> bool;
fn ring_frontdoor(view: &GameState) -> Option<Cell>;
fn ring_cells(view: &GameState) -> Vec<Cell>;
fn ring_goal(&self, view: &GameState) -> usize;
fn release_mothers(view: &GameState) -> bool;
```

`ring_frontdoor` and `ring_cells` are a direct type-adapted port of
`botmain::tactics::{compute_door,compute_ring}`; preserve constants and deterministic sorting.

### B3. Replace `banana_factory_plant_cell`

Candidate vocabulary is `ring_cells(view)` only. Filter occupied/planted/unreachable cells.

Selection key:

1. while no live diagonal BANANA mother exists, diagonal before orthogonal;
2. otherwise minimum worker BFS distance;
3. lexicographic cell.

This guarantees a mother without forcing diagonal-first forever.

### B4. Cap bootstrap and stop full-ring PICK

In `banana_factory_starter_command`:

```rust
let goal = min(initial_budget, ring_cells(view).len());
let target = legal_empty_ring_target(...);
```

A carried BANANA plants only when `target.is_some()`; with no target return `None`, allowing the
resident’s existing carried-fruit bank command to emit MOVE/DROP.

A tent BANANA PICK is possible only when:

```rust
target.is_some()
&& move_turns(starter, target) <= 2
&& inventory[BANANA] > 0
&& no harvestable diagonal mother at Manhattan distance <= 1
```

Never route to the tent for a seed when the ring is full.

### B5. Replace harvest target

`banana_factory_harvest_target` enumerates live ripe BANANA trees that are:

- in `ring_cells(view)`;
- diagonal;
- reachable.

It does not harvest orthogonal cut trees. The nearest target wins deterministically.

If the ring has an empty cell, harvested carry plants there. If not, the starter falls through to
existing bank logistics and deposits the BANANA.

After an observed DROP (carry BANANA zero, no pending harvest/plant), clear
`banana_factory_seed_from_harvest`.

### B6. Reserve/protection

`banana_factory_promote_reserve` may name only a live diagonal ring BANANA. The reserve remains a
harvest-priority/telemetry representative; it is no longer the whole protection set.

Before conflict resolution build:

```rust
forbidden_for_non_starter = all diagonal ring cells
```

outside endgame/raid. This reserves empty mothers as well as live mothers.

### B7. Replace wood command

Build resident chop/bank candidates, remove diagonal ring tree candidates unless
`release_mothers(view)`, then apply current opponent-crop priority.

Choose:

```text
urgent known opponent crop ETA<=6
    else orthogonal ring BANANA size>=2
    else resident max candidate
    else WAIT
```

Do not infer urgency solely from a score bonus: verify target provenance and ETA directly.

### B8. Replace factory wrapper

For every non-starter every turn, call the corrected `banana_factory_wood_command`; do not preserve
an old command merely because its verb is MOVE/CHOP/WAIT. Then run the existing priority-aware move
resolver with starter priority and diagonal forbidden cells.

Continue calling `remember_own_plant_attempts` after final resolution so our ring trees never enter
`opponent_crops`.

## C. Tests to reuse directly

Historical files already encode the intended semantics:

- `rust/tests/ringfarm.rs` — placement, orthogonal cut, diagonal keep/release, front-door;
- `rust/tests/ringfix3.rs` — immediate PICK and harvest-before-PICK.

Port these fixtures to the generated `SecureOrchardBot` tests rather than designing new expected
behavior. Add the new missing assertion:

```text
full ring + carried/harvested BANANA -> DROP at tent, never PLANT/MOVE-to-plant
```

Also assert initial budget 24 (or any value > ring capacity) does not cause repeated PICK/DROP.

## D. Slimmer delta

Clone `cgauto/slim_banana_factory_b100_candidate.py`.

Keep its:

- `DEAD_ITEMS` / `DEAD_FRAGMENTS` reuse;
- inactive selector/task-market/worker-three removals;
- exact compact-parent guard;
- constructor-exact specialization;
- `<100,000` rejection.

Change only:

1. its compact parent hash after the new research transform;
2. the compact replacements for `banana_factory_wood_command` and
   `banana_factory_commands`, preserving the ring semantics above;
3. retain newly added `SecureOrchardBot` ring helpers;
4. remove embedded tests in the Arena source as before.

The previous accepted artifact had 560 bytes of nominal headroom. If the first ring-aware slim is
over the limit, remove telemetry-only counters and dead full-factory geography before changing any
behavior. Full-source/Arena-source equality decides correctness.

## E. Fast gate commands/result shape

Repeat the exact prior gate:

- optimized research-source test binary;
- optimized Arena-source standalone compile;
- empty input;
- mutated-parent rejection;
- eight streams, seeds `1300..1303`, both seats, `ringfix3`/`taskplan`;
- 2,400 command strings exactly equal;
- zero stderr;
- latency report;
- byte count and SHA sidecar.

Add a compact telemetry report containing:

```json
{
  "max_own_banana_chebyshev_from_tent": 1,
  "max_concurrent_ring_bananas": "<= eligible_ring_cells",
  "diagonal_harvest_successes": "> 0 when mothers ripen",
  "banana_drop_successes_after_full_ring": "> 0",
  "orthogonal_chop_successes": "> 0",
  "diagonal_ordinary_chops": 0,
  "plants_outside_ring": 0,
  "full_ring_bank_picks": 0,
  "eta6_opponent_crop_displacements": 0
}
```

Any nonzero forbidden count closes the candidate before publication.