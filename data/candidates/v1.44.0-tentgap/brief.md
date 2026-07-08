# D4 builder brief — v1.44.0-tentgap (shack cells are walkable; fix the phantom wall)

**Origin:** user replay finding #5 (2026-07-08, game 895493013 vs Sasso_Stark, 16x8 map):
lake + our tent + boulder column form a wall from the north lake to the south edge; the only
gap IS the tent cell (13,4). Our bot walked the y=0 top corridor around the map for every
west↔east transition.

## Root cause (verified in source + replay)

- **Referee truth** (our engine mirror `rust/src/game/state.rs:75-92`, arena-validated):
  `'0'`/`'1'` shack cells ARE WALKABLE (trolls walk over and stand on tents — that is also
  why TRAIN requires "shack unoccupied", engine.rs:498-500, and why a picker can block a
  tent). `'+'` iron and `'~'` water are NOT walkable (bot already agrees on those).
- **Live bot** `rust/src/botmain.rs::parse_grid` (~:190-196): `'0'`/`'1'` only set
  `my_shack`/`opp_shack` and are NEVER inserted into `walkable` → both tents are modeled as
  rocks. Every BFS (`d`, farm_d, camp/park/bank routing, solve_moves landing candidates)
  inherits the error.

## Measured impact (game 895493013, replay-parsed)

- BFS (12,4)→(14,4): bot model **24 steps**, real **2 steps**.
- Our MOVE destinations: unit1 made 9 W↔E treks, unit3 made 4 — all via the top corridor
  (~18-22 extra steps each) ≈ **200+ wasted troll-turns of ~600 total**. Won anyway (214-81)
  because Sasso never crossed; vs a competent opponent this is a losing handicap on any
  pinch map. Command census & side-sequences: `docs/silver-experiment-log.md` entry
  2026-07-08 ("tent-wall analysis").

## The fix (small, but with three guard rails)

1. `parse_grid`: insert `'0'` and `'1'` cells into `walkable` (2 lines). This matches the
   engine mirror exactly.
2. **Guard: never PLANT on a shack.** Engine's apply_plant checks only walkable+empty, so
   after (1) the plant-spot search could propose the shack cell. Exclude BOTH shack cells
   from plant candidates (plant_cell hunt in planner.rs + any tactics farm-spot search).
3. **Guard: never PARK/idle-land on a shack.** Parking on OUR shack blocks TRAIN and
   re-creates the corridor blockage (it is the door!); parking on THEIRS is out of scope.
   Exclude both shack cells from park/camp candidate cells (motion::pick_camp_cell /
   park_cmd) — transit and en-route landings through the shack remain allowed (that is the
   point of the fix); only DELIBERATE stationary placement is banned. NOTE: banking does
   NOT require standing on the shack — near_shack is manhattan ≤ 1 (engine.rs:197-199),
   adjacent DROP/PICK already works and existing flows stop adjacent.
4. Leave `'+'` iron non-walkable (bot already correct; engine agrees).

## Tests (TDD)

1. `parse_grid_shacks_walkable`: grid with '0'/'1' → both cells in walkable, shack coords
   still correct. RED first (currently not in walkable).
2. `bfs_through_tent_gap`: reduced Sasso geometry (wall of water+shack+boulder splitting a
   corridor) → d(west,east) small (through shack), not the long way. RED first.
3. `never_plant_on_shack`: farm state where the shack is the nearest "free walkable" plant
   spot → plant target ≠ either shack cell. Must pass post-fix (RED if written against the
   naive fix — verify it actually triggers: construct so the shack WOULD be chosen without
   the guard, flip-check style).
4. `never_park_on_shack`: idle troll whose best park ring cell would be the shack → parks
   elsewhere. Same flip-check discipline.
5. EXPECT EXISTING TESTS TO SHIFT: pickloop/motion_corridor fixtures encode the old
   walkability (tent-as-wall). Re-run all; where a fixture's premise was "tent blocks the
   corridor", re-read the test's intent before touching the assertion — the livelock/
   errand semantics must survive; only distance/route expectations may legitimately change.
   Document every changed assertion in the report with the reason. Full suite green at the
   end + self-determinism equality 8 seeds + bundle/minify/compile gates + artifacts frozen.

## Gate watchlist

- This is a pure execution waste-cut (the class that transfers: race check +1.3). Expected
  gate signature: wood ≥ reference on average maps; LARGE gains only on pinch maps (map-
  dependent variance — do not expect uniform lift).
- Watch: trolls standing on the tent at TRAIN time (should be impossible via the park
  guard, but check @TFFARM for train timing anomalies); plant spots on shack (grep PLANT
  destinations vs shack coords in probe games).
- Composes with D2 (yield): the tent-door cell will now see real teammate-occupancy
  conflicts — D2's yield handles the temporary blocker; this fix removes the phantom wall.
