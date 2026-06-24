# Troll Farm Simulator + Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A faithful offline simulator of the league-2 referee, a Python port of the league-2 boss, league-2 map generation, and a harness that plays `bot/main.py`'s `decide` against the boss over seeded maps — so we can reproduce the troll-3 movement deadlock (with full per-turn positions) and measure/tune win-rate instead of guessing.

**Architecture:** A dev-only `sim/` package holds a mutable `GameState` and pure functions that mirror the referee: pathing, per-player move resolution (the part that produces the deadlock), harvest/drop/pick/plant/train application, plant ticking, and a `step()` that applies both players' command strings in referee priority order. A `build_view` adapter turns `GameState` into the `bot.main.State` our `decide` already consumes (in-process, no stdio), so the harness can run thousands of games fast. Mechanics constants and helpers are imported from `bot.main` (one source of truth).

**Tech Stack:** Python 3.11, stdlib only. Tests with pytest via `uv run pytest`.

## Global Constraints

- `sim/` is **dev-only** — never imported by `bot/main.py`. The dependency arrow points one way: `sim` imports from `bot.main`, never the reverse.
- Reuse from `bot.main` (do not re-implement): `PLANT_COOLDOWN` ({PLUM:8, LEMON:8, APPLE:9, BANANA:6}), `MAX_SIZE`(4), `MAX_FRUITS`(3), `ITEM_NAMES` (`["PLUM","LEMON","APPLE","BANANA","IRON","WOOD"]`), `ITEM_INDEX`, `training_cost(n, talents)`, `bfs_distances(walkable, sources)`, and `State`, `Troll`, `Tree`, `decide`, `PARAMS`.
- Referee facts the sim must honour (from `docs/mechanics.md`, verified against the Java referee):
  - Item order/indices: PLUM 0, LEMON 1, APPLE 2, BANANA 3, IRON 4, WOOD 5. Score = sum of inventory indices 0..3.
  - Map: only GRASS is walkable; shacks are not walkable; a troll **spawns on its shack cell**. League 2: `height=8`, `width=16`, no water/rock/iron.
  - Turn apply order by task priority (ascending): MOVE(1) → HARVEST(2) → PLANT(3) → PICK(5) → TRAIN(6) → DROP(7); **then** plants tick; then scores recompute; then turn advances.
  - `bfs_distances` seeds source cells at 0 regardless of walkability and only expands into walkable cells.
  - Harvest is resolved in rounds i=1..3 over all trolls sharing the tree cell; in round i every troll with `harvestPower>=i` and free capacity does `inventory++` **before** the plant's fruit is decremented (last-fruit duplication). Max 2 trolls per cell (1 per team).
  - Move resolution is **per player**: two of one team's trolls can't end on the same cell; the contested cell goes to the **highest unit id**; circular swaps resolve as a group; a unit that can't move stays. Enemy units never block our moves.
  - `TRAIN m c h chop`: cost `n+m²` PLUM, `n+c²` LEMON, `n+h²` APPLE (`n`=own troll count); chop must be 0; new unit spawns on the shack; blocked if a troll occupies the shack cell.
  - `PLANT id type`: troll on a GRASS cell with no plant and carrying ≥1 of `type` → consumes 1 carried, creates a size-0 plant. `PICK id type`: troll next to shack → moves 1 of `type` from shack inventory into carry. `DROP id`: troll next to shack → all carried items move to the shack inventory.
- **Determinism:** the referee breaks equidistant move ties randomly; the sim breaks them deterministically by smallest `(x, y)`. Document this where it matters; it does not affect deadlock reproduction or win-rate trends.
- TDD: every function gets a failing test first. Commit after each task.

---

## File Structure

- Create: `sim/__init__.py` — empty package marker.
- Create: `sim/state.py` — `SimUnit`, `SimPlant`, `GameState`, `from_ascii`, small accessors.
- Create: `sim/engine.py` — `next_cell`, `apply_moves`, harvest/drop/pick/plant/train, `tick_plants`, `recompute_scores`, `step`.
- Create: `sim/views.py` — `build_view(game, player) -> bot.main.State`.
- Create: `sim/boss.py` — `boss_decide(game, player) -> list[str]` (port of `config/level2/Boss.cs`).
- Create: `sim/mapgen.py` — `generate(seed) -> GameState` (league-2 maps).
- Create: `sim/runner.py` — `play_game(...)`, `win_rate(...)`, and a `__main__` CLI.
- Create: `tests/test_sim_state.py`, `tests/test_sim_engine.py`, `tests/test_sim_views.py`, `tests/test_sim_boss.py`, `tests/test_sim_mapgen.py`, `tests/test_sim_runner.py`.

---

## Task 1: Sim data model + ASCII loader

**Files:**
- Create: `sim/__init__.py` (empty)
- Create: `sim/state.py`
- Test: `tests/test_sim_state.py`

**Interfaces:**
- Produces:
  - `SimUnit(id:int, player:int, x:int, y:int, ms:int, cc:int, hp:int, chop:int, carry:list[int])` with `.pos -> (x,y)`, `.total -> sum(carry)`, `.free -> cc - total`.
  - `SimPlant(type:str, x:int, y:int, size:int, health:int, fruits:int, cooldown:int)` with `.pos`.
  - `GameState(width, height, walkable:set, shacks:list[tuple], inventories:list[list[int]], units:list[SimUnit], plants:list[SimPlant], scores:list[int], turn:int, next_id:int)`.
  - `from_ascii(rows:list[str], talents=(1,1,1,0)) -> GameState` — `.`=grass(walkable), `0`/`1`=shacks (not walkable, `shacks[0]`/`shacks[1]`), spawns one unit per player on its shack with `talents`, empty inventories, `turn=1`, `next_id` past the spawned units.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_state.py
from sim.state import from_ascii, SimUnit


def test_from_ascii_sets_walkable_shacks_and_spawns_units():
    g = from_ascii(["....", "0..1"])
    assert g.width == 4 and g.height == 2
    assert g.shacks == [(0, 1), (3, 1)]
    assert (0, 1) not in g.walkable and (3, 1) not in g.walkable
    assert (0, 0) in g.walkable
    assert [(u.player, u.pos) for u in g.units] == [(0, (0, 1)), (1, (3, 1))]
    assert g.turn == 1 and g.next_id == 2
    assert g.inventories == [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]


def test_simunit_capacity_helpers():
    u = SimUnit(0, 0, 1, 1, 1, 4, 2, 0, [1, 0, 1, 0, 0, 0])
    assert u.pos == (1, 1) and u.total == 2 and u.free == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_state.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/__init__.py  (empty file)
```

```python
# sim/state.py
from dataclasses import dataclass, field


@dataclass
class SimUnit:
    id: int
    player: int
    x: int
    y: int
    ms: int
    cc: int
    hp: int
    chop: int
    carry: list  # length 6

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def total(self):
        return sum(self.carry)

    @property
    def free(self):
        return self.cc - self.total


@dataclass
class SimPlant:
    type: str
    x: int
    y: int
    size: int
    health: int
    fruits: int
    cooldown: int

    @property
    def pos(self):
        return (self.x, self.y)


@dataclass
class GameState:
    width: int
    height: int
    walkable: set
    shacks: list
    inventories: list
    units: list
    plants: list
    scores: list
    turn: int
    next_id: int


def from_ascii(rows, talents=(1, 1, 1, 0)):
    width = len(rows[0])
    height = len(rows)
    walkable = set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                shacks[0] = (x, y)
            elif ch == "1":
                shacks[1] = (x, y)
            else:
                walkable.add((x, y))
    units = []
    for p in (0, 1):
        sx, sy = shacks[p]
        units.append(SimUnit(p, p, sx, sy, talents[0], talents[1],
                             talents[2], talents[3], [0] * 6))
    return GameState(width=width, height=height, walkable=walkable, shacks=shacks,
                     inventories=[[0] * 6, [0] * 6], units=units, plants=[],
                     scores=[0, 0], turn=1, next_id=len(units))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_state.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add sim/__init__.py sim/state.py tests/test_sim_state.py
git commit -m "feat(sim): GameState data model + ASCII loader"
```

---

## Task 2: Plant ticking + scoring

**Files:**
- Create: `sim/engine.py`
- Test: `tests/test_sim_engine.py`

**Interfaces:**
- Consumes: `bot.main.PLANT_COOLDOWN`, `MAX_SIZE`, `MAX_FRUITS`; `SimPlant`, `GameState`.
- Produces:
  - `tick_plants(game)` — advances every plant one referee tick (grow until size 4, then produce until 3 fruits), mutating in place. (No water in league 2, so cooldown resets to the base `PLANT_COOLDOWN[type]`.)
  - `recompute_scores(game)` — sets `game.scores[p] = sum(game.inventories[p][0:4])`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_engine.py
from sim.state import GameState, SimPlant, SimUnit, from_ascii
from sim.engine import tick_plants, recompute_scores


def test_tick_plants_grows_then_produces():
    g = from_ascii(["....", "0..1"])
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 2, 1)]   # full size, cd 1
    tick_plants(g)                                    # cd->0 -> +1 fruit
    p = g.plants[0]
    assert p.fruits == 3 and p.cooldown == 8


def test_tick_plants_growing_tree_increases_size_no_fruit():
    g = from_ascii(["....", "0..1"])
    g.plants = [SimPlant("BANANA", 2, 0, 2, 6, 0, 1)]
    tick_plants(g)
    assert g.plants[0].size == 3 and g.plants[0].fruits == 0


def test_recompute_scores_counts_only_fruit():
    g = from_ascii(["....", "0..1"])
    g.inventories[0] = [3, 2, 1, 4, 9, 0]   # iron/wood don't score
    recompute_scores(g)
    assert g.scores[0] == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: FAIL — `ImportError: cannot import name 'tick_plants'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/engine.py
from bot.main import (PLANT_COOLDOWN, MAX_SIZE, MAX_FRUITS, ITEM_INDEX,
                      ITEM_NAMES, training_cost, bfs_distances)
from sim.state import SimUnit, SimPlant


def tick_plants(game):
    base = PLANT_COOLDOWN
    for p in game.plants:
        if p.cooldown > 0:
            p.cooldown -= 1
        if p.cooldown == 0 and p.health > 0:
            if p.size < MAX_SIZE:
                p.size += 1
                p.cooldown = base[p.type]
            elif p.fruits < MAX_FRUITS:
                p.fruits += 1
                p.cooldown = base[p.type]


def recompute_scores(game):
    for p in (0, 1):
        game.scores[p] = sum(game.inventories[p][0:4])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add sim/engine.py tests/test_sim_engine.py
git commit -m "feat(sim): plant ticking + scoring"
```

---

## Task 3: Pathing — `next_cell` (faithful getNextCell)

**Files:**
- Modify: `sim/engine.py`
- Test: `tests/test_sim_engine.py`

**Interfaces:**
- Consumes: `bot.main.bfs_distances`.
- Produces: `next_cell(walkable, current, target, speed) -> (x, y)` — mirrors referee `Board.getNextCell`. If `target` is reachable within `speed`, return it. If unreachable, aim at the reachable cell(s) with smallest Manhattan distance to `target`. Otherwise return the in-range reachable cell minimising BFS distance to the goal; **break ties by smallest `(x, y)`** (referee is random here).

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_sim_engine.py
from sim.engine import next_cell


def line(n, blocked=()):
    return {(x, 0) for x in range(n)} - set(blocked)


def test_next_cell_direct_when_in_range():
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (3, 0), (5, 0), 2) == (5, 0)   # 2 away, speed 2


def test_next_cell_steps_toward_far_target():
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (1, 0), (5, 0), 1) == (2, 0)   # one step closer


def test_next_cell_routes_to_nearest_reachable_when_unreachable():
    # target (0,0) is the shack (unwalkable); a banking troll parks adjacent
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (3, 0), (0, 0), 1) == (2, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_engine.py::test_next_cell_direct_when_in_range -v`
Expected: FAIL — `ImportError: cannot import name 'next_cell'`.

- [ ] **Step 3: Write minimal implementation** (append to `sim/engine.py`)

```python
def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def next_cell(walkable, current, target, speed):
    source_dist = bfs_distances(walkable, [current])
    if target in source_dist and source_dist[target] <= speed:
        return target

    if target not in source_dist:
        # target unreachable: aim at reachable cells closest (Manhattan) to it
        best = min(_manhattan(target, c) for c in source_dist)
        goals = [c for c in source_dist if _manhattan(target, c) == best]
        target_dist = bfs_distances(walkable, goals)
    else:
        target_dist = bfs_distances(walkable, [target])

    in_range = [c for c, d in source_dist.items() if d <= speed and c in target_dist]
    best = min(target_dist[c] for c in in_range)
    return min(c for c in in_range if target_dist[c] == best)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: PASS (all engine tests so far).

- [ ] **Step 5: Commit**

```bash
git add sim/engine.py tests/test_sim_engine.py
git commit -m "feat(sim): faithful next_cell pathing"
```

---

## Task 4: Move resolution (per-player conflict — the deadlock path)

**Files:**
- Modify: `sim/engine.py`
- Test: `tests/test_sim_engine.py`

**Interfaces:**
- Consumes: `next_cell`, `GameState`, `SimUnit`.
- Produces: `apply_moves(game, intents:dict[int,tuple])` — `intents` maps `unit_id -> (target_x, target_y)` for units that issued a MOVE this turn. Mirrors `MoveTask.apply` per player: compute each mover's `next_cell`, then resolve so no two own units share a cell — non-movers hold their cells; among movers wanting one cell the **highest id** wins; circular swaps resolve as a group; a unit that cannot move stays put. Mutates `unit.x/unit.y`.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_sim_engine.py
from sim.state import from_ascii, SimUnit
from sim.engine import apply_moves


def two_unit_state():
    # 6x1 corridor, shack at (0,0); two of player 0's units
    g = from_ascii(["0....."])
    g.units = [SimUnit(0, 0, 2, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(1, 0, 3, 0, 1, 1, 1, 0, [0]*6)]
    g.next_id = 2
    return g


def test_two_movers_take_distinct_cells():
    g = two_unit_state()
    apply_moves(g, {0: (5, 0), 1: (5, 0)})   # both want to go right
    cells = sorted(u.pos for u in g.units)
    assert cells == [(3, 0), (4, 0)] or len(set(cells)) == 2  # no overlap


def test_unit_blocked_by_stationary_teammate_stays_put():
    # unit 0 sits still on (2,0); unit 1 at (1,0) wants (2,0) -> blocked, stays
    g = two_unit_state()
    g.units[0].x, g.units[0].y = 2, 0
    g.units[1].x, g.units[1].y = 1, 0
    apply_moves(g, {1: (2, 0)})              # unit 0 issued no move
    assert g.units[0].pos == (2, 0)
    assert g.units[1].pos == (1, 0)          # could not enter occupied cell


def test_higher_id_wins_contested_cell():
    g = two_unit_state()
    g.units[0].x, g.units[0].y = 1, 0
    g.units[1].x, g.units[1].y = 3, 0
    apply_moves(g, {0: (2, 0), 1: (2, 0)})   # both want (2,0); id 1 wins
    assert g.units[1].pos == (2, 0)
    assert g.units[0].pos == (1, 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_engine.py::test_two_movers_take_distinct_cells -v`
Expected: FAIL — `ImportError: cannot import name 'apply_moves'`.

- [ ] **Step 3: Write minimal implementation** (append to `sim/engine.py`)

```python
def apply_moves(game, intents):
    by_id = {u.id: u for u in game.units}
    for player in (0, 1):
        units = [u for u in game.units if u.player == player]
        # desired final cell for each unit (movers via next_cell, others stay)
        target = {}
        for u in units:
            if u.id in intents:
                target[u.id] = next_cell(game.walkable, u.pos, intents[u.id], u.ms)
            else:
                target[u.id] = u.pos
        occupied = {u.pos for u in units}
        # drop non-movers (cell already occupied and unchanged)
        movers = [u for u in units if target[u.id] != u.pos]
        # process by descending id so the highest id wins a contested cell
        movers.sort(key=lambda u: -u.id)
        progress = True
        resolve_blocking = False
        while progress:
            progress = False
            freq = {}
            for u in movers:
                freq[target[u.id]] = freq.get(target[u.id], 0) + 1
            for u in list(movers):
                cell = target[u.id]
                if (resolve_blocking or freq[cell] == 1) and cell not in occupied:
                    occupied.discard(u.pos)
                    occupied.add(cell)
                    u.x, u.y = cell
                    movers.remove(u)
                    progress = True
                    resolve_blocking = False
            if progress:
                continue
            # circular swaps: follow target -> occupant chains looking for a loop
            pos_to_unit = {u.pos: u for u in movers}
            for start in list(movers):
                path = [start]
                while True:
                    nxt = pos_to_unit.get(target[path[-1].id])
                    if nxt is None:
                        break
                    if nxt is path[0]:
                        for u in path:
                            u.x, u.y = target[u.id]
                            movers.remove(u)
                        progress = True
                        break
                    if nxt in path:
                        break
                    path.append(nxt)
                if progress:
                    break
            if not progress and not resolve_blocking:
                resolve_blocking = True
                progress = True
    _ = by_id  # (kept for readability; not otherwise needed)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: PASS (all engine tests).

- [ ] **Step 5: Commit**

```bash
git add sim/engine.py tests/test_sim_engine.py
git commit -m "feat(sim): per-player move resolution (deadlock-faithful)"
```

---

## Task 5: Harvest / Drop / Pick / Plant / Train application

**Files:**
- Modify: `sim/engine.py`
- Test: `tests/test_sim_engine.py`

**Interfaces:**
- Consumes: `training_cost`, `ITEM_INDEX`, `ITEM_NAMES`, `MAX_FRUITS`; `SimUnit`, `SimPlant`, `GameState`.
- Produces (each mutates `game`; `unit` resolved by id; invalid actions are silently skipped, matching the referee's non-critical errors):
  - `apply_harvest(game, unit_ids:list[int])` — group by tree cell; rounds i=1..3; each troll on the cell with `hp>=i` and free capacity gains a fruit (inventory++ before the plant decrement → last-fruit duplication).
  - `apply_drop(game, unit_ids)` — if next to own shack, move all carry into the player's inventory.
  - `apply_pick(game, picks:list[tuple])` — `(unit_id, type_name)`; if next to shack and stock>0, move one from inventory into carry.
  - `apply_plant(game, plants:list[tuple])` — `(unit_id, type_name)`; if on grass, no plant present, carrying that type → consume one, add a size-0 `SimPlant`.
  - `apply_train(game, player, talents)` — if affordable and the shack cell is free, deduct cost and spawn a `SimUnit` on the shack with `next_id`.
  - `_near_shack(game, unit) -> bool`, `_plant_at(game, cell) -> SimPlant | None` helpers.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_sim_engine.py
from sim.engine import (apply_harvest, apply_drop, apply_pick, apply_plant,
                        apply_train)


def test_harvest_takes_one_fruit_for_capacity_one_troll():
    g = from_ascii(["0....."])
    g.units = [SimUnit(0, 0, 1, 0, 1, 1, 1, 0, [0]*6)]
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 3, 5)]
    apply_harvest(g, [0])
    assert g.units[0].carry[0] == 1 and g.plants[0].fruits == 2


def test_last_fruit_duplicates_across_two_trolls():
    g = from_ascii(["0....."])
    g.units = [SimUnit(0, 0, 1, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(9, 1, 1, 0, 1, 1, 1, 0, [0]*6)]  # enemy on same cell
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 1, 5)]      # only 1 fruit
    apply_harvest(g, [0, 9])
    assert g.units[0].carry[0] == 1 and g.units[1].carry[0] == 1   # both got one
    assert g.plants[0].fruits == 0


def test_drop_moves_carry_to_inventory_when_next_to_shack():
    g = from_ascii(["0....."])
    g.units = [SimUnit(0, 0, 1, 0, 1, 9, 1, 0, [2, 0, 1, 0, 0, 0])]
    apply_drop(g, [0])
    assert g.inventories[0][0] == 2 and g.inventories[0][2] == 1
    assert g.units[0].total == 0


def test_train_costs_and_spawns_on_shack():
    g = from_ascii(["0....."])
    g.units[0].x, g.units[0].y = 2, 0       # move existing unit off the shack
    g.inventories[0] = [5, 5, 5, 5, 0, 0]
    apply_train(g, 0, (1, 1, 1, 0))         # n=1 -> cost 2/2/2
    assert g.inventories[0][:3] == [3, 3, 3]
    spawned = [u for u in g.units if u.id == 1]
    assert spawned and spawned[0].pos == g.shacks[0]


def test_train_blocked_when_shack_occupied():
    g = from_ascii(["0....."])                # unit 0 still on the shack
    g.inventories[0] = [5, 5, 5, 5, 0, 0]
    apply_train(g, 0, (1, 1, 1, 0))
    assert len(g.units) == 2                  # no new unit
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_engine.py::test_harvest_takes_one_fruit_for_capacity_one_troll -v`
Expected: FAIL — `ImportError: cannot import name 'apply_harvest'`.

- [ ] **Step 3: Write minimal implementation** (append to `sim/engine.py`)

```python
def _plant_at(game, cell):
    for p in game.plants:
        if p.pos == cell:
            return p
    return None


def _near_shack(game, unit):
    sx, sy = game.shacks[unit.player]
    return abs(unit.x - sx) + abs(unit.y - sy) <= 1


def apply_harvest(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    cells = {}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None:
            continue
        plant = _plant_at(game, u.pos)
        if plant is not None and plant.fruits > 0:
            cells.setdefault(u.pos, []).append(u)
    for cell, trolls in cells.items():
        plant = _plant_at(game, cell)
        idx = ITEM_INDEX[plant.type]
        for i in range(1, MAX_FRUITS + 1):
            if plant.fruits == 0:
                break
            for u in trolls:
                if u.hp >= i and u.total < u.cc:
                    u.carry[idx] += 1
                    if plant.fruits > 0:
                        plant.fruits -= 1


def apply_drop(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None or not _near_shack(game, u):
            continue
        for i in range(6):
            game.inventories[u.player][i] += u.carry[i]
            u.carry[i] = 0


def apply_pick(game, picks):
    by_id = {u.id: u for u in game.units}
    for uid, type_name in picks:
        u = by_id.get(uid)
        if u is None or not _near_shack(game, u) or u.free <= 0:
            continue
        idx = ITEM_INDEX[type_name]
        if game.inventories[u.player][idx] > 0:
            game.inventories[u.player][idx] -= 1
            u.carry[idx] += 1


def apply_plant(game, plants):
    by_id = {u.id: u for u in game.units}
    for uid, type_name in plants:
        u = by_id.get(uid)
        if u is None or u.pos not in game.walkable or _plant_at(game, u.pos):
            continue
        idx = ITEM_INDEX[type_name]
        if u.carry[idx] > 0:
            u.carry[idx] -= 1
            game.plants.append(SimPlant(type_name, u.x, u.y, 0, 6, 0, 6))


def apply_train(game, player, talents):
    n = sum(1 for u in game.units if u.player == player)
    cost = training_cost(n, talents)
    inv = game.inventories[player]
    if any(inv[i] < cost[i] for i in range(6)):
        return
    if any(u.pos == game.shacks[player] for u in game.units):
        return
    for i in range(6):
        inv[i] -= cost[i]
    sx, sy = game.shacks[player]
    game.units.append(SimUnit(game.next_id, player, sx, sy,
                             talents[0], talents[1], talents[2], talents[3], [0]*6))
    game.next_id += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: PASS (all engine tests).

- [ ] **Step 5: Commit**

```bash
git add sim/engine.py tests/test_sim_engine.py
git commit -m "feat(sim): harvest/drop/pick/plant/train application"
```

---

## Task 6: `step` — one full referee turn

**Files:**
- Modify: `sim/engine.py`
- Test: `tests/test_sim_engine.py`

**Interfaces:**
- Consumes: `apply_moves`, `apply_harvest`, `apply_plant`, `apply_pick`, `apply_train`, `apply_drop`, `tick_plants`, `recompute_scores`.
- Produces: `step(game, cmds0:list[str], cmds1:list[str])` — parse both players' command lists (each item one command; `MSG ...` and `WAIT` ignored), bucket by verb, apply in referee priority order MOVE → HARVEST → PLANT → PICK → TRAIN → DROP, then `tick_plants`, `recompute_scores`, `game.turn += 1`. A troll may be named in at most one command per player (later duplicates ignored, matching the referee's used-unit rule).

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_sim_engine.py
from sim.engine import step


def test_step_moves_then_harvests_in_priority_order():
    g = from_ascii(["0....."])
    g.units = [SimUnit(0, 0, 1, 0, 1, 1, 1, 0, [0]*6)]
    g.plants = [SimPlant("PLUM", 2, 0, 4, 4, 3, 5)]
    # turn 1: move onto the tree (can't harvest same turn)
    step(g, ["MOVE 0 2 0"], [])
    assert g.units[0].pos == (2, 0) and g.turn == 2
    # turn 2: harvest it
    step(g, ["HARVEST 0"], [])
    assert g.units[0].carry[0] == 1


def test_step_ignores_msg_and_wait_and_advances_turn():
    g = from_ascii(["0....."])
    step(g, ["MSG hi", "WAIT"], ["WAIT"])
    assert g.turn == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_engine.py::test_step_moves_then_harvests_in_priority_order -v`
Expected: FAIL — `ImportError: cannot import name 'step'`.

- [ ] **Step 3: Write minimal implementation** (append to `sim/engine.py`)

```python
def _parse(cmds):
    moves, harvests, plants, picks, drops, trains = {}, [], [], [], [], []
    used = set()
    for raw in cmds:
        parts = raw.strip().split()
        if not parts:
            continue
        verb = parts[0].upper()
        if verb in ("MSG", "WAIT"):
            continue
        if verb == "TRAIN":
            trains.append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
            continue
        uid = int(parts[1])
        if uid in used:
            continue
        used.add(uid)
        if verb == "MOVE":
            moves[uid] = (int(parts[2]), int(parts[3]))
        elif verb == "HARVEST":
            harvests.append(uid)
        elif verb == "DROP":
            drops.append(uid)
        elif verb == "PLANT":
            plants.append((uid, parts[2].upper()))
        elif verb == "PICK":
            picks.append((uid, parts[2].upper()))
    return moves, harvests, plants, picks, drops, trains


def step(game, cmds0, cmds1):
    parsed = [_parse(cmds0), _parse(cmds1)]
    # MOVE (priority 1) — both players resolved together, per-player internally
    apply_moves(game, {**parsed[0][0], **parsed[1][0]})
    # HARVEST (2)
    apply_harvest(game, parsed[0][1] + parsed[1][1])
    # PLANT (3)
    apply_plant(game, parsed[0][2] + parsed[1][2])
    # PICK (5)
    apply_pick(game, parsed[0][3] + parsed[1][3])
    # TRAIN (6)
    for player in (0, 1):
        for talents in parsed[player][5]:
            apply_train(game, player, talents)
    # DROP (7)
    apply_drop(game, parsed[0][4] + parsed[1][4])
    tick_plants(game)
    recompute_scores(game)
    game.turn += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_engine.py -v`
Expected: PASS (all engine tests).

- [ ] **Step 5: Commit**

```bash
git add sim/engine.py tests/test_sim_engine.py
git commit -m "feat(sim): step() applies a full turn in referee priority order"
```

---

## Task 7: `build_view` — GameState → `bot.main.State`

**Files:**
- Create: `sim/views.py`
- Test: `tests/test_sim_views.py`

**Interfaces:**
- Consumes: `bot.main.State`, `bot.main.Troll`, `bot.main.Tree`; `GameState`.
- Produces: `build_view(game, player) -> bot.main.State` — the per-player view our `decide` consumes: `walkable`, `my_shack`/`opp_shack` for `player`, `my_inventory`/`opp_inventory`, `trees` (as `bot.main.Tree`), `my_trolls`/`opp_trolls` (as `bot.main.Troll`, mapping sim `ms/cc/hp` to `movement_speed/carry_capacity/harvest_power`, `carry` copied), and `turn`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_views.py
from sim.state import from_ascii, SimUnit, SimPlant
from sim.views import build_view


def test_build_view_maps_state_for_player_zero():
    g = from_ascii(["....", "0..1"])
    g.units = [SimUnit(0, 0, 1, 1, 2, 3, 1, 0, [1, 0, 0, 0, 0, 0]),
               SimUnit(7, 1, 2, 1, 1, 1, 1, 0, [0]*6)]
    g.plants = [SimPlant("PLUM", 0, 0, 4, 4, 2, 5)]
    g.inventories = [[4, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0]]
    g.turn = 6
    v = build_view(g, 0)
    assert v.my_shack == (0, 1) and v.opp_shack == (3, 1)
    assert v.my_inventory == [4, 0, 0, 0, 0, 0]
    assert [t.id for t in v.my_trolls] == [0] and [t.id for t in v.opp_trolls] == [7]
    assert v.my_trolls[0].carry_capacity == 3 and v.my_trolls[0].carry == [1, 0, 0, 0, 0, 0]
    assert v.trees[0].pos == (0, 0) and v.turn == 6


def test_build_view_for_player_one_swaps_sides():
    g = from_ascii(["....", "0..1"])
    g.inventories = [[4, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0]]
    v = build_view(g, 1)
    assert v.my_shack == (3, 1) and v.opp_shack == (0, 1)
    assert v.my_inventory == [1, 1, 1, 1, 0, 0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_views.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim.views'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/views.py
from bot.main import State, Troll, Tree


def _troll(u):
    return Troll(id=u.id, x=u.x, y=u.y, movement_speed=u.ms,
                 carry_capacity=u.cc, harvest_power=u.hp, carry=list(u.carry))


def build_view(game, player):
    opp = 1 - player
    trees = [Tree(p.type, p.x, p.y, p.size, p.health, p.fruits, p.cooldown)
             for p in game.plants]
    my = [_troll(u) for u in game.units if u.player == player]
    their = [_troll(u) for u in game.units if u.player == opp]
    return State(walkable=set(game.walkable), my_shack=game.shacks[player],
                 opp_shack=game.shacks[opp], my_inventory=list(game.inventories[player]),
                 opp_inventory=list(game.inventories[opp]), trees=trees,
                 my_trolls=my, opp_trolls=their, turn=game.turn)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_views.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add sim/views.py tests/test_sim_views.py
git commit -m "feat(sim): build_view adapter (GameState -> bot.main.State)"
```

---

## Task 8: Boss port (`config/level2/Boss.cs`)

**Files:**
- Create: `sim/boss.py`
- Test: `tests/test_sim_boss.py`

**Interfaces:**
- Consumes: `build_view`; `GameState`.
- Produces: `boss_decide(game, player) -> list[str]` — mirrors the league-2 boss: per own troll, if full carry head to/`DROP` at the shack, else `MOVE`/`HARVEST` the **nearest fruited tree by Manhattan** (boss tie-break: among the nearest, keep the *farther* ones — `dist > closest`); and `TRAIN 1 1 1 0` while it has fewer than 2 trolls. (We omit the boss's buggy `PLANT` branch; it never set `hasPlanted` and is not needed to gate-test our bot.) Uses Manhattan distance like the boss, not BFS.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_boss.py
from sim.state import from_ascii, SimUnit, SimPlant
from sim.boss import boss_decide


def test_boss_trains_second_troll():
    g = from_ascii(["1....."])           # player 1's shack at (0,0)
    g.units = [SimUnit(0, 1, 2, 0, 1, 1, 1, 0, [0]*6)]   # only one troll
    cmds = boss_decide(g, 1)
    assert "TRAIN 1 1 1 0" in cmds


def test_boss_harvests_tree_underfoot():
    g = from_ascii(["1....."])
    g.units = [SimUnit(0, 1, 2, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(1, 1, 0, 0, 1, 1, 1, 0, [0]*6)]   # 2 trolls -> no train
    g.plants = [SimPlant("PLUM", 2, 0, 4, 4, 2, 5)]
    cmds = boss_decide(g, 1)
    assert "HARVEST 0" in cmds


def test_boss_returns_to_shack_when_full():
    g = from_ascii(["1....."])
    g.units = [SimUnit(0, 1, 3, 0, 1, 1, 1, 0, [1, 0, 0, 0, 0, 0]),
               SimUnit(1, 1, 5, 0, 1, 1, 1, 0, [0]*6)]
    cmds = boss_decide(g, 1)
    assert any(c.startswith("MOVE 0 0 0") or c == "DROP 0" for c in cmds)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_boss.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim.boss'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/boss.py
def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def boss_decide(game, player):
    shack = game.shacks[player]
    mine = [u for u in game.units if u.player == player]
    fruited = [p for p in game.plants if p.fruits > 0]
    cmds = ["MSG Eat your vegetables!"]
    for u in mine:
        if u.total >= u.cc:
            if _dist(u.pos, shack) == 1:
                cmds.append(f"DROP {u.id}")
            else:
                cmds.append(f"MOVE {u.id} {shack[0]} {shack[1]}")
            continue
        if not fruited:
            continue
        nearest = min(_dist(u.pos, p.pos) for p in fruited)
        pool = [p for p in fruited if _dist(u.pos, p.pos) > nearest] or fruited
        target = min(pool, key=lambda p: _dist(u.pos, p.pos))
        if u.pos == target.pos:
            cmds.append(f"HARVEST {u.id}")
        else:
            cmds.append(f"MOVE {u.id} {target.x} {target.y}")
    if len(mine) < 2:
        cmds.append("TRAIN 1 1 1 0")
    return cmds
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_boss.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add sim/boss.py tests/test_sim_boss.py
git commit -m "feat(sim): league-2 boss port"
```

---

## Task 9: Map generation (`sim/mapgen.py`)

**Files:**
- Create: `sim/mapgen.py`
- Test: `tests/test_sim_mapgen.py`

**Interfaces:**
- Consumes: `bot.main.PLANT_COOLDOWN`, `bot.main.bfs_distances`; `GameState`, `SimUnit`, `SimPlant`; `sim.engine.tick_plants`.
- Produces: `generate(seed:int) -> GameState` — a league-2 map: `height=8`, `width=16`, all GRASS, a point-symmetric pair of shacks (`shacks[1]` is the mirror `(w-1-x, h-1-y)` of `shacks[0]`, with `shacks[0]` in the left half and not adjacent to its mirror), starting inventories of 2..10 for PLUM/LEMON/APPLE/BANANA (IRON/WOOD 0), and 1..3 trees of each fruit type placed on random empty grass cells with their point-symmetric mirror, each aged a random number of ticks. Reproducible for a given `seed`; guarantees every walkable cell is reachable from `shacks[0]`'s neighbours and ≥1 tree starts with fruit.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_mapgen.py
from sim.mapgen import generate
from bot.main import bfs_distances


def test_generate_is_deterministic_and_symmetric():
    a = generate(42)
    b = generate(42)
    assert [u.pos for u in a.units] == [u.pos for u in b.units]
    assert [p.pos for p in a.plants] == [p.pos for p in b.plants]
    assert a.width == 16 and a.height == 8
    s0, s1 = a.shacks
    assert s1 == (a.width - 1 - s0[0], a.height - 1 - s0[1])
    assert s0[0] < a.width // 2


def test_generate_has_starting_inventory_and_fruit():
    g = generate(7)
    assert all(2 <= g.inventories[0][i] <= 10 for i in range(4))
    assert any(p.fruits > 0 for p in g.plants)
    # all walkable cells reachable from a shack neighbour
    nbrs = [(g.shacks[0][0]+dx, g.shacks[0][1]+dy)
            for dx, dy in ((0,1),(1,0),(0,-1),(-1,0))]
    dist = bfs_distances(g.walkable, [n for n in nbrs if n in g.walkable])
    assert all(c in dist for c in g.walkable)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_mapgen.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim.mapgen'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/mapgen.py
import random
from bot.main import PLANT_COOLDOWN, bfs_distances, MAX_SIZE, MAX_FRUITS
from sim.state import GameState, SimUnit, SimPlant
from sim.engine import tick_plants

WIDTH, HEIGHT = 16, 8
FRUITS = ["PLUM", "LEMON", "APPLE", "BANANA"]


def _mirror(cell):
    return (WIDTH - 1 - cell[0], HEIGHT - 1 - cell[1])


def _all_reachable(walkable, shack):
    nbrs = [(shack[0]+dx, shack[1]+dy) for dx, dy in ((0,1),(1,0),(0,-1),(-1,0))]
    dist = bfs_distances(walkable, [n for n in nbrs if n in walkable])
    return all(c in dist for c in walkable)


def generate(seed):
    rnd = random.Random(seed)
    while True:
        cells = {(x, y) for x in range(WIDTH) for y in range(HEIGHT)}
        s0 = (rnd.randrange(WIDTH // 2), rnd.randrange(HEIGHT))
        s1 = _mirror(s0)
        if s1 == s0:
            continue
        walkable = cells - {s0, s1}
        if not _all_reachable(walkable, s0):
            continue

        inv0 = [rnd.randint(2, 10) for _ in range(4)] + [0, 0]
        inv1 = list(inv0)  # symmetric start

        plants = []
        used = {s0, s1}
        for ftype in FRUITS:
            for _ in range(rnd.randint(1, 3)):
                free = list(walkable - used)
                if not free:
                    break
                cell = rnd.choice(free)
                mirror = _mirror(cell)
                if mirror in used or mirror == cell:
                    continue
                used.add(cell)
                used.add(mirror)
                base = PLANT_COOLDOWN[ftype]
                ticks = rnd.randint(1, base * (MAX_SIZE + MAX_FRUITS))
                for cpos in (cell, mirror):
                    p = SimPlant(ftype, cpos[0], cpos[1], 0, 6, 0, base)
                    plants.append(p)
                # age both identically
                tmp = GameState(WIDTH, HEIGHT, walkable, [s0, s1], [inv0, inv1],
                                [], plants[-2:], [0, 0], 1, 2)
                for _ in range(ticks):
                    tick_plants(tmp)

        units = [SimUnit(0, 0, s0[0], s0[1], 1, 1, 1, 0, [0]*6),
                 SimUnit(1, 1, s1[0], s1[1], 1, 1, 1, 0, [0]*6)]
        game = GameState(WIDTH, HEIGHT, walkable, [s0, s1], [inv0, inv1],
                         units, plants, [0, 0], 1, 2)
        if any(p.fruits > 0 for p in game.plants):
            return game
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_mapgen.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add sim/mapgen.py tests/test_sim_mapgen.py
git commit -m "feat(sim): league-2 map generation"
```

---

## Task 10: Harness — play full games, win-rate, deadlock log

**Files:**
- Create: `sim/runner.py`
- Test: `tests/test_sim_runner.py`

**Interfaces:**
- Consumes: `generate`, `step`, `build_view`, `recompute_scores`, `boss_decide`; `bot.main.decide`, `bot.main.PARAMS`.
- Produces:
  - `play_game(game, params, max_turns=300, log=None) -> (our_score, boss_score)` — our `decide` is player 0, `boss_decide` is player 1; appends `(turn, [unit dicts])` to `log` if a list is given (for debugging the deadlock: each unit's id/pos/carry). Returns the two scores after `max_turns`.
  - `win_rate(seeds, params=None) -> dict` — runs `play_game(generate(s), ...)` for each seed; returns `{"wins": int, "games": int, "win_rate": float, "avg_margin": float}` (we win when our score > boss score).
  - `__main__`: `python -m sim.runner --games N [--seed S]` prints the `win_rate` summary.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sim_runner.py
from sim.mapgen import generate
from sim.runner import play_game, win_rate
from bot.main import PARAMS


def test_play_game_runs_and_returns_scores():
    log = []
    ours, boss = play_game(generate(1), PARAMS, max_turns=30, log=log)
    assert isinstance(ours, int) and isinstance(boss, int)
    assert len(log) == 30
    assert all("id" in u and "pos" in u for u in log[0][1])


def test_win_rate_summarises_multiple_games():
    r = win_rate(range(3), PARAMS)
    assert r["games"] == 3 and 0.0 <= r["win_rate"] <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sim_runner.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sim.runner'`.

- [ ] **Step 3: Write minimal implementation**

```python
# sim/runner.py
import argparse
from bot.main import decide, PARAMS
from sim.engine import step, recompute_scores
from sim.views import build_view
from sim.boss import boss_decide
from sim.mapgen import generate


def play_game(game, params, max_turns=300, log=None):
    for _ in range(max_turns):
        ours = decide(build_view(game, 0), params)
        theirs = boss_decide(game, 1)
        if log is not None:
            log.append((game.turn, [{"id": u.id, "pos": u.pos, "carry": list(u.carry)}
                                    for u in game.units if u.player == 0]))
        step(game, ours, theirs)
    recompute_scores(game)
    return game.scores[0], game.scores[1]


def win_rate(seeds, params=None):
    params = params or PARAMS
    seeds = list(seeds)
    wins = 0
    margin = 0
    for s in seeds:
        ours, boss = play_game(generate(s), params)
        margin += ours - boss
        if ours > boss:
            wins += 1
    n = len(seeds)
    return {"wins": wins, "games": n, "win_rate": wins / n if n else 0.0,
            "avg_margin": margin / n if n else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    print(win_rate(range(args.seed, args.seed + args.games)))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_sim_runner.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Run the harness and the full suite**

Run: `uv run python -m sim.runner --games 20`
Expected: a dict like `{'wins': N, 'games': 20, 'win_rate': ..., 'avg_margin': ...}` — our first measured baseline vs the boss.
Run: `uv run pytest -q`
Expected: PASS (all tests).

- [ ] **Step 6: Commit**

```bash
git add sim/runner.py tests/test_sim_runner.py
git commit -m "feat(sim): harness — full games, win-rate, debug log"
```

---

## Self-Review

**Spec coverage** (against `docs/superpowers/specs/2026-06-23-bronze-bot-design.md`, "Simulator", "Offline harness & tuning", and the v0.5.1 loss analysis):
- Faithful referee step (priority order, harvest+duplication, move conflict resolution, train spawn/block, plant/pick/drop) → Tasks 2–6. ✓
- Per-player move resolution that can reproduce the troll-3 deadlock, with a debug log of per-turn positions → Tasks 4 and 10. ✓
- League-2 map generation (symmetric, starting inventory, aged trees) → Task 9. ✓
- Boss port → Task 8. ✓
- In-process bot driving via `build_view` → Task 7. ✓
- Harness with win-rate vs boss → Task 10. ✓
- Tuning loop over `PARAMS`: `win_rate(seeds, params)` is the measurement primitive a tuner calls; an explicit search loop is intentionally **out of scope for this plan** (next step once we have a baseline and the deadlock fix). Noted, not a gap.

**Placeholder scan:** no TBD/TODO; every code step is complete. The `_ = by_id` line in Task 4 is deliberate (keeps the id map handy and documents intent); harmless.

**Type consistency:** `GameState`/`SimUnit`/`SimPlant` fields and the `ms/cc/hp/chop/carry` naming are used consistently across Tasks 1–10; `build_view` maps them to `bot.main.Troll`'s `movement_speed/carry_capacity/harvest_power`; `step(game, cmds0, cmds1)`, `apply_moves(game, intents)`, `play_game(game, params, max_turns, log)`, and `win_rate(seeds, params)` signatures match their call sites.

**Out of scope (YAGNI):** chopping/mining/iron/water (league 3+), subprocess/stdio bot driving (we drive `decide` in-process), an automated parameter-search loop, and bit-exact reproduction of the referee's random move tie-break (we use a deterministic `(x,y)` tie-break).
