# Troll Farm — verified mechanics (from referee source)

Primary source: https://github.com/eulerscheZahl/Troll-Farm at commit
`290129129db7a7539d98739ebdb0ed63ee6ceb50` (re-audited 2026-07-30).
These are facts read directly from the Java referee, more authoritative than the
statement. Executable source/local checks and the complete conformance matrix are in
`cgauto/mechanics_rederivation_audit.py` and
`docs/reviews/2026-07-30-local_codex_1-x1-mechanics-rederivation.md`.

## Leagues & available actions
Task → required league: MOVE 1, HARVEST 1, DROP 1, WAIT 1, TRAIN 2, PLANT 2, PICK 2,
CHOP 3, MINE 3.
**Wood (league 1) = only MOVE / HARVEST / DROP / WAIT.**

## Starting state (`Board.createMap`, `Player.init`)
Legend starts with exactly one troll per player at
**movementSpeed=1, carryCapacity=1, harvestPower=1, chopPower=1**. In leagues below 3,
starting chopPower is 0; Wood is therefore `(1,1,1,0)`.

In Legend, the referee makes five independent inclusive-uniform draws from **2..10**:
PLUM, LEMON, APPLE, BANANA, and IRON. The same drawn inventory is assigned to both
players. Expected starting fruit is **24** and expected starting iron is **6**. Initial
score is the four fruit draws, not zero.

You start with exactly **one** troll and cannot train in Wood. Trees can't be chopped
in Wood (chopPower 0, CHOP is league 3), so trees never die ⇒ **every Wood game runs the
full 100 turns** (`hasStalled` returns false while plants exist).

## Map (`Board.createMap`)
- Point-symmetric: your half is mirrored to the opponent. In Legend,
  `height` is uniform over **8..11** and `width=2*height`; leagues ≤2 use
  `height=8`, `width=16`. Your shack is in your half (`x < width/2`).
- Cell types: GRASS `.`, WATER `~`, ROCK `#`, IRON `+`, SHACK `0`/`1`. In Wood the map is
  all GRASS + the two shacks (water/iron/rock appear league 3+).
- **Only GRASS is walkable** (`isWalkable` = type==GRASS). The shack cell is NOT walkable,
  so a troll can never stand on it — it DROPs from an orthogonally-adjacent GRASS cell.
- Trees are placed only on empty GRASS cells; the cell stays GRASS, so you stand on the
  tree's cell to harvest.

## Pathing & movement (`Board.getNextCell`, `getDistances`)
- Distances are **BFS over GRASS cells**; other units do NOT block distance.
- `MOVE id x y`: if target reachable within `movementSpeed`, go to it; else step to the
  in-range reachable cell with the smallest BFS distance to the target. **Ties broken
  randomly.** If target is unreachable, routes to the reachable cell with min Manhattan
  distance to it (this parks you next to the unwalkable shack).
- With speed 1 you advance exactly one cell/turn along a shortest path.
- GOTCHA: a troll **spawns on its shack cell** (`Unit` ctor sets cell = shack), and the
  shack is NOT walkable. `getDistances` seeds the *source* cell at distance 0 regardless
  of walkability and only gates *expansion* on walkable neighbours — so BFS from a troll
  sitting on the shack still works. A bot that filters non-walkable source cells will see
  "no reachable cells" on turn 1, output WAIT, and stay frozen on the shack forever.

## Move conflict resolution (`MoveTask.apply`) — per player only
- Collisions are resolved **within each player's own units** separately. Two of YOUR
  units can't end on the same cell (contested cell → highest unit ID wins; circular
  swaps allowed). **Enemy units CAN share a cell with yours** — no cross-player blocking.
- A unit that can't move emits a non-critical MOVE_BLOCKED error and stays put.

## Harvesting (`HarvestTask.apply`, `Unit.harvest`)
- Must be ON the tree cell with `fruits>0`, free capacity, and harvestPower>0.
- A troll gains `min(harvestPower, freeCapacity, fruitsOnTree)` per turn. **Wood = 1 fruit
  then full.** A troll can't MOVE and HARVEST in the same turn.
- Resolved in rounds i=1..3 over all trolls sharing the cell (both players). In round i,
  every troll with `harvestPower>=i` and free capacity does `inventory++` **before** the
  plant's fruit count is decremented. ⇒ **last-fruit duplication**: if a tree has 1 fruit
  and 2 trolls harvest, both get one. Capped at +1 (max 2 trolls/cell, 1 per team).

## Trees / cooldown (`Plant.tick`, `Constants`)
- `type` ∈ {PLUM,LEMON,APPLE,BANANA}; max size 4; max 3 fruits.
- Base cooldown per type: PLUM 8, LEMON 8, APPLE 9, BANANA 6 (ticks per step).
- Near water: cooldown reduced by {PLUM 5, LEMON 5, APPLE 7, BANANA 2} (league 3+ only).
- Each time cooldown hits 0 (health>0): if size<4 → grow a size (no fruit); else if
  fruits<3 → produce a fruit; then cooldown resets to the (water-adjusted) base.
- Turn order: tasks apply by priority
  **MOVE→HARVEST→PLANT→CHOP→PICK→TRAIN→DROP→MINE**, then all plants tick and scores
  recompute.
  A full tree idles at cooldown 0; harvesting it makes the next tick regenerate 1 fruit
  immediately, then normal cooldowns resume.
- Initial trees are randomly "aged" 1..cd*(4+3) ticks, so they start in varied states.
- Health only matters for chopping (league 3+); ignore in Wood. Full health scales
  with size per type: **`health = base + slope*size`** — PLUM/LEMON `(4,2)`, APPLE
  `(8,3)`, BANANA `(2,1)` (primary-source confirmed by `PLANT_FINAL_HEALTH`,
  `PLANT_DELTA_HEALTH`, and `Plant.tick`; also 10/10 real-replay observations:
  PLUM s1-4=6,8,10,12; LEMON s2,s4=8,12; APPLE s1,s3=11,17; BANANA s3,s4=5,6). So a
  big APPLE (≤20 hp) is ~3× tankier to chop than a BANANA (≤6). The Rust sim mapgen
  and engine model this (`engine::tree_health`); a flat health=6 over-rewarded
  chopping and inverted the local ladder.

## Legend resource actions and training
- TRAIN with `n` existing own trolls and talents `(ms,cc,hp,chop)` costs
  **PLUM=`n+ms²`, LEMON=`n+cc²`, APPLE=`n+hp²`, IRON=`n+chop²`**; BANANA and WOOD
  cost zero. TRAIN rechecks affordability and shack occupancy at apply time, after MOVE
  and PICK but before DROP.
- Same-type simultaneous PLANT commands on one cell create one plant and spend every
  planter's seed. Mixed-type simultaneous PLANT commands cancel without planting.
  A newly planted size-0 tree ticks on the creation turn.
- CHOP damage from both players applies before death is resolved. On death, wood equals
  tree size and uses the same round structure that permits **last-wood duplication**.
- MINE requires positive chopPower, free carry capacity, and orthogonal adjacency to iron;
  it collects `min(chopPower, freeCapacity)` iron.

## Scoring & turn flow (`Player.recomputeScore`, `Referee.gameTurn`)
- Score = PLUM+LEMON+APPLE+BANANA in shack inventory (+4×WOOD, irrelevant in Wood).
  Each fruit DROPped at the shack = 1 point. Fruit carried but not dropped scores 0.
- Both players' outputs parse, then `board.tick` applies tasks by ascending priority:
  MoveTask=1, HarvestTask=2, PlantTask=3, ChopTask=4, PickTask=5, TrainTask=6,
  DropTask=7, MineTask=8.
- Timeout: 1000 ms turn 1, 50 ms/turn. 3 strikes (each ≤50 ms over) or one big overage = loss.
- Unknown command / unowned-or-reused troll → error (unknown command is critical = loss;
  most others are non-critical and just skip the action).

## Local-model parity boundaries (X1)
- **Equal-best movement tie:** the referee chooses randomly; maintained Python/Rust
  engines choose the lexicographic minimum. Referee-parity work must preserve the
  post-map RNG state or prove tied moves absent.
- **Command validation:** local parsers are simpler than the referee's ownership, league,
  skill, syntax, and critical-error checks. A referee-parity harness needs full validation
  or a measured zero-invalid-command boundary.
- `rust/src/game/official_mapgen.rs` remains exact for initial-state generation
  (D33: 120/120 untouched confirmation); `sim/mapgen.py` and the historical synthetic
  Rust generator are not field-evidence substrates.

## I/O format (matches stub.txt; statement's "reserved" fields are real values)
Init: `width height`, then `height` lines of `width` chars (`.`/`0`/`1` in Wood).
Per turn:
- 2 inventory lines (you, then opponent): `plum lemon apple banana iron wood` (iron/wood 0 in Wood).
- `treeCount`, then per tree: `type x y size health fruits cooldown`.
- `trollCount`, then per troll: `id player x y movementSpeed carryCapacity harvestPower
  chopPower carryPlum carryLemon carryApple carryBanana carryIron carryWood`
  (`player`=0 if yours). NOTE: chopPower IS provided (8th field), not reserved.
Output: commands joined by `;`: `MOVE id x y`, `HARVEST id`, `DROP id`, `WAIT`, `MSG text`.

## Wood boss behaviour (config/level1/Boss.cs) — what we must beat
- Uses **Manhattan** distance only (no BFS, no obstacles in Wood so it's fine there).
- Targets trees with `fruits>0`; among the nearest, it oddly keeps the FARTHER ones
  (`Where(Dist > closest)`), i.e. a quirky tie-break. No ripeness prediction.
- If full (carry ≥ capacity): DROP if adjacent to base else MOVE to base.
- Sends `MSG Eat your vegetables!`. Beatable with BFS + ripeness-aware target selection.
