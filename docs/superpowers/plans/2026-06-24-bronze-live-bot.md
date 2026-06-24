# Bronze Live Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve `bot/main.py` from a single-troll Wood gatherer into a multi-troll league-2 bot that gathers efficiently (capacity > 1), trains trolls economically, and can plant a near-shack orchard — strong enough to beat boss 2 with hand-set parameters.

**Architecture:** `bot/main.py` stays the single-file CodinGame submission and the shared library. We replace the single-troll `choose_action(state)` with `decide(state, params) -> list[str]` built from small, testable helpers (`bfs_distances`, `predict_fruits`, `training_cost`, `best_tree`, `gather_command`, `training_command`, planting). The simulator/harness/tuning is a separate follow-up plan; here all knobs live in a `PARAMS` dict with sensible defaults.

**Tech Stack:** Python 3.11, stdlib only (`collections.deque`, `dataclasses`). Tests with pytest via `uv run pytest`.

## Global Constraints

- Submission is a single file: `bot/main.py`. All runtime code lives there; dev-only tooling (later plan) imports from it. No third-party runtime deps.
- Pure logic at module level; the stdin/stdout loop runs only under `if __name__ == "__main__"`.
- League 2 facts (verbatim from `docs/statement_bronze.md` / `docs/mechanics.md`):
  - Total turns: **300**. Map `height=8`, `width=16`. Only GRASS walkable; shack not walkable; trolls spawn on their shack.
  - Item order (inventory + per-troll carry lines): `PLUM LEMON APPLE BANANA IRON WOOD` (indices 0..5). IRON/WOOD always 0 in league 2.
  - Per-troll input fields: `id player x y movementSpeed carryCapacity harvestPower chopPower carryPlum carryLemon carryApple carryBanana carryIron carryWood`. `player==0` is ours.
  - `TRAIN m c h chop` cost (paid from shack inventory), with `n` = current own troll count: `PLUM = n + m²`, `LEMON = n + c²`, `APPLE = n + h²`. `chop` must be 0; `m∈[1,128]`, `c∈[0,1000]`, `h∈[0,3]`. New troll spawns on the shack; TRAIN is blocked if a troll occupies the shack cell.
  - Tree growth cooldowns by type: PLUM 8, LEMON 8, APPLE 9, BANANA 6. Max size 4, max 3 fruits.
  - Score = banked PLUM+LEMON+APPLE+BANANA. Bananas are never a training cost.
- TDD: every new function gets a failing test first. Commit after each task.

---

## File Structure

- Modify: `bot/main.py` — model, mechanics, `decide`, `PARAMS`, game loop.
- Modify: `tests/test_action.py` — migrate single-troll tests to the new `gather_command`/`decide` API.
- Modify: `tests/test_parse.py` — multi-troll `parse_turn`.
- Create: `tests/test_decide.py` — multi-troll orchestration, training, planting.
- Create: `tests/test_training.py` — `training_cost` and the training policy.
- Modify: `tests/sample_input.txt` — a league-2 turn (multiple trolls, real inventories).

Existing, unchanged: `predict_fruits`, `bfs_distances`, `parse_grid`, `_ortho_neighbors`, `_is_adjacent`, `_ticks_until_ripe`, `PLANT_COOLDOWN`, `RIPEN_HORIZON`.

---

## Task 1: Multi-troll data model

**Files:**
- Modify: `bot/main.py` (replace `Troll` and `State` dataclasses; add item constants and `TOTAL_TURNS`)
- Test: `tests/test_model.py` (create)

**Interfaces:**
- Produces:
  - `ITEM_NAMES = ["PLUM","LEMON","APPLE","BANANA","IRON","WOOD"]`, `ITEM_INDEX: dict[str,int]`, `TOTAL_TURNS = 300`.
  - `Troll(id:int, x:int, y:int, movement_speed:int, carry_capacity:int, harvest_power:int, carry:list[int])` with `.pos -> (x,y)`, `.total_carried -> int`, `.free_capacity -> int`.
  - `Tree(type:str, x:int, y:int, size:int, health:int, fruits:int, cooldown:int)` with `.pos`.
  - `State(walkable:set, my_shack:tuple, opp_shack:tuple, my_inventory:list[int], opp_inventory:list[int], trees:list[Tree], my_trolls:list[Troll], opp_trolls:list[Troll], turn:int)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_model.py
from bot.main import Troll, Tree, State, ITEM_INDEX, TOTAL_TURNS


def test_troll_carry_totals_and_free_capacity():
    t = Troll(id=3, x=2, y=5, movement_speed=2, carry_capacity=4,
              harvest_power=3, carry=[1, 0, 2, 0, 0, 0])
    assert t.pos == (2, 5)
    assert t.total_carried == 3
    assert t.free_capacity == 1


def test_item_index_and_turn_constant():
    assert ITEM_INDEX["BANANA"] == 3
    assert TOTAL_TURNS == 300


def test_state_holds_both_sides():
    s = State(walkable={(0, 0)}, my_shack=(0, 0), opp_shack=(15, 7),
              my_inventory=[2, 2, 2, 2, 0, 0], opp_inventory=[3, 3, 3, 3, 0, 0],
              trees=[], my_trolls=[], opp_trolls=[], turn=1)
    assert s.opp_shack == (15, 7)
    assert s.my_inventory[0] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_model.py -v`
Expected: FAIL — `ImportError` (`ITEM_INDEX`/`TOTAL_TURNS` not defined) and `Troll.__init__` signature mismatch.

- [ ] **Step 3: Write minimal implementation**

In `bot/main.py`, add constants near the top (after `PLANT_COOLDOWN`):

```python
ITEM_NAMES = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
ITEM_INDEX = {name: i for i, name in enumerate(ITEM_NAMES)}
TOTAL_TURNS = 300
```

Replace the `Troll` dataclass with:

```python
@dataclass
class Troll:
    id: int
    x: int
    y: int
    movement_speed: int
    carry_capacity: int
    harvest_power: int
    carry: list  # counts per item index (length 6)

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def total_carried(self):
        return sum(self.carry)

    @property
    def free_capacity(self):
        return self.carry_capacity - self.total_carried
```

Replace the `State` dataclass with:

```python
@dataclass
class State:
    walkable: set
    my_shack: tuple
    opp_shack: tuple
    my_inventory: list   # counts per item index (length 6)
    opp_inventory: list
    trees: list
    my_trolls: list
    opp_trolls: list
    turn: int
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_model.py -v`
Expected: PASS (3 tests).

Note: `tests/test_action.py`, `tests/test_parse.py`, and the old `choose_action` now reference the old `State`/`Troll` shape and will fail to import — they are migrated in Tasks 2 and 4. To keep the suite runnable between tasks, temporarily comment out the body of `choose_action` is NOT needed; instead run only the targeted test files shown in each task's commands until Task 4 restores a green full suite.

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_model.py
git commit -m "feat(bronze): multi-troll Troll/State model + item constants"
```

---

## Task 2: Parse a full league-2 turn

**Files:**
- Modify: `bot/main.py` (`parse_turn`; `parse_grid` already returns `opp_shack`)
- Modify: `tests/test_parse.py`

**Interfaces:**
- Consumes: `parse_grid(grid_lines) -> (walkable:set, my_shack, opp_shack)` (unchanged).
- Produces: `parse_turn(lines, walkable, my_shack, opp_shack, turn) -> State`. `lines` is an iterator of input lines for one turn. Collects ALL trolls into `my_trolls`/`opp_trolls`, reads both inventories, sets `turn`.

- [ ] **Step 1: Write the failing test** (replace the two `parse_turn` tests in `tests/test_parse.py`)

```python
def test_parse_turn_collects_all_trolls_and_inventories():
    walkable = {(x, y) for x in range(16) for y in range(8)} - {(5, 3), (10, 4)}
    lines = [
        "2 3 4 5 0 0",                      # my inventory
        "1 1 1 1 0 0",                      # opponent inventory
        "1",                                 # tree count
        "PLUM 6 1 4 4 2 5",
        "3",                                 # troll count
        "0 0 5 3 1 1 1 0 0 0 0 0 0 0",       # my troll, on my shack
        "2 0 6 1 2 4 3 0 1 0 1 0 0 0",       # my troll, carrying plum+apple=2
        "1 1 10 4 1 1 1 0 0 0 0 0 0 0",      # opponent troll
    ]
    state = parse_turn(iter(lines), walkable, my_shack=(5, 3),
                       opp_shack=(10, 4), turn=7)
    assert state.turn == 7
    assert state.my_inventory == [2, 3, 4, 5, 0, 0]
    assert state.opp_inventory == [1, 1, 1, 1, 0, 0]
    assert [t.id for t in state.my_trolls] == [0, 2]
    assert [t.id for t in state.opp_trolls] == [1]
    second = state.my_trolls[1]
    assert second.carry == [1, 0, 1, 0, 0, 0]
    assert second.total_carried == 2
    assert second.carry_capacity == 4
    assert state.trees == [Tree("PLUM", 6, 1, 4, 4, 2, 5)]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_parse.py::test_parse_turn_collects_all_trolls_and_inventories -v`
Expected: FAIL — `parse_turn` has the old signature / returns single `my_troll`.

- [ ] **Step 3: Write minimal implementation** (replace `parse_turn` in `bot/main.py`)

```python
def parse_turn(lines, walkable, my_shack, opp_shack, turn):
    """Build a State for this turn from an iterator of input lines."""
    my_inventory = [int(v) for v in next(lines).split()]
    opp_inventory = [int(v) for v in next(lines).split()]
    tree_count = int(next(lines))
    trees = []
    for _ in range(tree_count):
        t = next(lines).split()
        trees.append(Tree(t[0], int(t[1]), int(t[2]), int(t[3]),
                          int(t[4]), int(t[5]), int(t[6])))
    troll_count = int(next(lines))
    my_trolls = []
    opp_trolls = []
    for _ in range(troll_count):
        f = [int(v) for v in next(lines).split()]
        troll = Troll(id=f[0], x=f[2], y=f[3], movement_speed=f[4],
                      carry_capacity=f[5], harvest_power=f[6],
                      carry=f[8:14])
        if f[1] == 0:
            my_trolls.append(troll)
        else:
            opp_trolls.append(troll)
    return State(walkable=walkable, my_shack=my_shack, opp_shack=opp_shack,
                 my_inventory=my_inventory, opp_inventory=opp_inventory,
                 trees=trees, my_trolls=my_trolls, opp_trolls=opp_trolls,
                 turn=turn)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_parse.py -v`
Expected: PASS (the grid test plus the new turn test). Remove the obsolete `test_parse_turn_sums_carried_items` if present (its behavior is covered above).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_parse.py
git commit -m "feat(bronze): parse all trolls + inventories into multi-troll State"
```

---

## Task 3: Training cost helper

**Files:**
- Modify: `bot/main.py` (add `training_cost`)
- Test: `tests/test_training.py` (create)

**Interfaces:**
- Produces: `training_cost(n:int, talents:tuple[int,int,int,int]) -> list[int]` of length 6. `talents = (movementSpeed, carryCapacity, harvestPower, chopPower)`. Returns per-item costs: index PLUM=`n+ms²`, LEMON=`n+cc²`, APPLE=`n+hp²`, others 0.

- [ ] **Step 1: Write the failing test** (uses the statement's worked example)

```python
# tests/test_training.py
from bot.main import training_cost


def test_training_cost_matches_statement_example():
    # 2 existing trolls, TRAIN 2 3 1 0 -> 6 PLUM, 11 LEMON, 3 APPLE
    cost = training_cost(2, (2, 3, 1, 0))
    assert cost == [6, 11, 3, 0, 0, 0]


def test_training_cost_zero_stats():
    assert training_cost(0, (1, 0, 0, 0)) == [1, 0, 0, 0, 0, 0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_training.py -v`
Expected: FAIL — `ImportError: cannot import name 'training_cost'`.

- [ ] **Step 3: Write minimal implementation**

```python
def training_cost(n, talents):
    """Per-item resource cost to TRAIN a troll with `talents` given `n` own trolls.

    PLUM<-movementSpeed, LEMON<-carryCapacity, APPLE<-harvestPower; cost = n + stat².
    chopPower (talents[3]) costs IRON only in league 3+, so 0 here.
    """
    ms, cc, hp, _chop = talents
    cost = [0, 0, 0, 0, 0, 0]
    cost[ITEM_INDEX["PLUM"]] = n + ms * ms
    cost[ITEM_INDEX["LEMON"]] = n + cc * cc
    cost[ITEM_INDEX["APPLE"]] = n + hp * hp
    return cost
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_training.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_training.py
git commit -m "feat(bronze): training_cost helper (n + stat^2 per resource)"
```

---

## Task 4: Per-troll gather decision (generalized for capacity > 1)

**Files:**
- Modify: `bot/main.py` (add `best_tree`, `gather_command`; remove old `choose_action`)
- Modify: `tests/test_action.py` (migrate to `gather_command`)

**Interfaces:**
- Consumes: `bfs_distances`, `_ticks_until_ripe`, `_ortho_neighbors`, `_is_adjacent`, `predict_fruits`.
- Produces:
  - `best_tree(state, troll, reserved:set, dist_t:dict, return_dist:dict, params:dict) -> Tree | None` — the lowest round-trip-cost tree whose `.pos` is not in `reserved`, reachable from the troll and back to the shack, and that ripens within the horizon. Cost key `(ripe + return_dist[pos], walk)`.
  - `gather_command(state, troll, reserved:set, dist_t:dict, return_dist:dict, params:dict) -> tuple[str, tuple|None]` — `(command, reserved_pos)`. `reserved_pos` is the tree cell this troll commits to (so the caller can reserve it), or `None` for bank/wait.

Decision rules:
1. If on a fruited tree and `free_capacity > 0`: `HARVEST` (reserve that tree).
2. Else if carrying (`total_carried > 0`) and (`free_capacity == 0` or no `best_tree` within `params["topup_radius"]` steps): bank — `DROP` if adjacent to shack else `MOVE` to shack (reserve `None`).
3. Else pick `best_tree`; if none → `WAIT`. If on it (unripe) → `WAIT` camp. Else `MOVE` toward it. Reserve its pos.

- [ ] **Step 1: Write the failing tests** (replace the whole body of `tests/test_action.py` with these, importing `gather_command`)

```python
from bot.main import (gather_command, best_tree, State, Troll, Tree,
                      bfs_distances, _ortho_neighbors)


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


PARAMS = {"topup_radius": 0}  # default: never top up; bank when carrying


def fields(state, troll):
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    return bfs_distances(state.walkable, [troll.pos]), bfs_distances(state.walkable, shack_adj)


def make(walkable, shack, trees, troll):
    return State(walkable=walkable, my_shack=shack, opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=[troll], opp_trolls=[], turn=1)


def test_harvest_when_on_fruited_tree_with_capacity():
    w = grid(4, 4, blocked=[(0, 0)])
    tr = Troll(0, 2, 2, 1, 1, 1, [0]*6)
    st = make(w, (0, 0), [Tree("PLUM", 2, 2, 4, 4, 2, 5)], tr)
    dt, rd = fields(st, tr)
    assert gather_command(st, tr, set(), dt, rd, PARAMS) == ("HARVEST 0", (2, 2))


def test_full_troll_banks_via_move_then_drop():
    w = grid(4, 4, blocked=[(0, 0)])
    far = Troll(0, 3, 3, 1, 1, 1, [1, 0, 0, 0, 0, 0])    # full (cap 1)
    st = make(w, (0, 0), [], far)
    dt, rd = fields(st, far)
    assert gather_command(st, far, set(), dt, rd, PARAMS) == ("MOVE 0 0 0", None)
    near = Troll(0, 0, 1, 1, 1, 1, [1, 0, 0, 0, 0, 0])
    st2 = make(w, (0, 0), [], near)
    dt2, rd2 = fields(st2, near)
    assert gather_command(st2, near, set(), dt2, rd2, PARAMS) == ("DROP 0", None)


def test_empty_troll_moves_to_best_round_trip_tree():
    w = grid(8, 2, blocked=[(0, 0)])
    tr = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    near = Tree("PLUM", 3, 0, 4, 4, 1, 5)
    far = Tree("PLUM", 5, 0, 4, 4, 1, 5)
    st = make(w, (0, 0), [near, far], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, set(), dt, rd, PARAMS)
    assert cmd == "MOVE 0 3 0" and res == (3, 0)


def test_reserved_tree_is_skipped():
    w = grid(8, 2, blocked=[(0, 0)])
    tr = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    near = Tree("PLUM", 3, 0, 4, 4, 1, 5)
    far = Tree("PLUM", 5, 0, 4, 4, 1, 5)
    st = make(w, (0, 0), [near, far], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, {(3, 0)}, dt, rd, PARAMS)
    assert cmd == "MOVE 0 5 0" and res == (5, 0)


def test_spawn_on_shack_routes_out():
    w = grid(4, 1, blocked=[(0, 0)])
    tr = Troll(0, 0, 0, 1, 1, 1, [0]*6)        # on the shack
    st = make(w, (0, 0), [Tree("PLUM", 2, 0, 4, 4, 2, 5)], tr)
    dt, rd = fields(st, tr)
    cmd, _ = gather_command(st, tr, set(), dt, rd, PARAMS)
    assert cmd == "MOVE 0 2 0"


def test_tops_up_a_second_tree_when_radius_allows():
    w = grid(6, 1, blocked=[(0, 0)])
    tr = Troll(0, 2, 0, 1, 2, 1, [1, 0, 0, 0, 0, 0])   # cap 2, carrying 1
    st = make(w, (0, 0), [Tree("PLUM", 3, 0, 4, 4, 1, 5)], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, set(), dt, rd, {"topup_radius": 5})
    assert cmd == "MOVE 0 3 0" and res == (3, 0)


def test_waits_when_no_reachable_tree():
    w = grid(4, 4, blocked=[(0, 0)])
    tr = Troll(0, 2, 2, 1, 1, 1, [0]*6)
    st = make(w, (0, 0), [], tr)
    dt, rd = fields(st, tr)
    assert gather_command(st, tr, set(), dt, rd, PARAMS) == ("WAIT", None)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_action.py -v`
Expected: FAIL — `ImportError: cannot import name 'gather_command'`.

- [ ] **Step 3: Write minimal implementation** (in `bot/main.py`; delete the old `choose_action`)

```python
def best_tree(state, troll, reserved, dist_t, return_dist, params):
    best = None
    best_key = None
    for tree in state.trees:
        if tree.pos in reserved:
            continue
        if tree.pos not in dist_t or tree.pos not in return_dist:
            continue
        walk = dist_t[tree.pos]
        ripe = _ticks_until_ripe(tree, walk)
        if ripe is None:
            continue
        key = (ripe + return_dist[tree.pos], walk)
        if best_key is None or key < best_key:
            best_key = key
            best = tree
    return best


def _bank_command(troll, state):
    if _is_adjacent(troll.pos, state.my_shack):
        return f"DROP {troll.id}"
    return f"MOVE {troll.id} {state.my_shack[0]} {state.my_shack[1]}"


def gather_command(state, troll, reserved, dist_t, return_dist, params):
    # 1. Opportunistic harvest: standing on a fruited tree with room.
    if troll.free_capacity > 0:
        for tree in state.trees:
            if tree.pos == troll.pos and tree.fruits > 0:
                return f"HARVEST {troll.id}", tree.pos

    target = best_tree(state, troll, reserved, dist_t, return_dist, params)

    # 2. Carrying: bank unless a worthwhile top-up tree is within radius.
    if troll.total_carried > 0:
        if (troll.free_capacity == 0 or target is None
                or dist_t.get(target.pos, 1 << 30) > params["topup_radius"]):
            return _bank_command(troll, state), None

    # 3. Head for the target tree (or wait/camp).
    if target is None:
        return "WAIT", None
    if target.pos == troll.pos:
        return "WAIT", None  # camping a not-yet-ripe target
    return f"MOVE {troll.id} {target.x} {target.y}", target.pos
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_action.py -v`
Expected: PASS (8 tests).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_action.py
git commit -m "feat(bronze): per-troll gather_command with reservations + capacity top-up"
```

---

## Task 5: `decide` — multi-troll orchestration

**Files:**
- Modify: `bot/main.py` (add `decide`, `PARAMS`)
- Test: `tests/test_decide.py` (create)

**Interfaces:**
- Consumes: `gather_command`, `bfs_distances`, `_ortho_neighbors`.
- Produces:
  - `PARAMS: dict` with at least `{"topup_radius": int, "max_trolls": int, "train_specs": list, "min_turns_left_to_train": int, "score_reserve": int, "plant_enabled": bool}`.
  - `decide(state, params) -> list[str]` — gather command per troll (deterministic order by id), reserving each chosen tree so two trolls never target the same one. Returns `["WAIT"]` if empty. (Training/planting appended in later tasks.)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_decide.py
from bot.main import decide, State, Troll, Tree, PARAMS


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def base(walkable, trees, my_trolls):
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=my_trolls, opp_trolls=[], turn=1)


def gather_only():
    p = dict(PARAMS)
    p["max_trolls"] = 0          # no training in this test
    p["plant_enabled"] = False
    return p


def test_two_trolls_do_not_target_the_same_tree():
    w = grid(8, 2, blocked=[(0, 0)])
    a = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    b = Troll(1, 4, 1, 1, 1, 1, [0]*6)
    trees = [Tree("PLUM", 3, 0, 4, 4, 1, 5), Tree("PLUM", 5, 0, 4, 4, 1, 5)]
    cmds = decide(base(w, trees, [a, b]), gather_only())
    targets = {c.split()[-2] + "," + c.split()[-1] for c in cmds if c.startswith("MOVE")}
    assert targets == {"3,0", "5,0"}     # distinct trees, no double-booking


def test_empty_returns_wait():
    w = grid(4, 4, blocked=[(0, 0)])
    cmds = decide(base(w, [], []), gather_only())
    assert cmds == ["WAIT"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_decide.py -v`
Expected: FAIL — `ImportError: cannot import name 'decide'` / `PARAMS`.

- [ ] **Step 3: Write minimal implementation**

```python
PARAMS = {
    "topup_radius": 4,        # keep gathering across trees within this many steps
    "max_trolls": 5,          # cap on own troll count
    "train_specs": [(2, 3, 3, 0)],   # preferred (ms, cc, hp, chop), most-wanted first
    "min_turns_left_to_train": 25,   # stop training near the end
    "score_reserve": 0,       # min banked total to keep after a train
    "plant_enabled": False,   # orchard off until tuned (Plan 2)
}


def decide(state, params):
    commands = []
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    return_dist = bfs_distances(state.walkable, shack_adj)
    reserved = set()
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        dist_t = bfs_distances(state.walkable, [troll.pos])
        cmd, reserved_pos = gather_command(state, troll, reserved, dist_t,
                                           return_dist, params)
        if reserved_pos is not None:
            reserved.add(reserved_pos)
        commands.append(cmd)
    if not commands:
        commands = ["WAIT"]
    return commands
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_decide.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_decide.py
git commit -m "feat(bronze): decide() orchestrates multi-troll gather with reservations"
```

---

## Task 6: Training policy

**Files:**
- Modify: `bot/main.py` (add `training_command`; call it in `decide`)
- Modify: `tests/test_training.py`

**Interfaces:**
- Consumes: `training_cost`, `TOTAL_TURNS`.
- Produces: `training_command(state, params) -> str | None` — returns `"TRAIN m c h 0"` when: own troll count `< params["max_trolls"]`; `TOTAL_TURNS - state.turn > params["min_turns_left_to_train"]`; the shack cell is unoccupied by an own troll; and the first affordable spec in `params["train_specs"]` leaves at least `params["score_reserve"]` total banked fruit. Else `None`. `decide` appends it to the command list when non-`None`.

- [ ] **Step 1: Write the failing test** (append to `tests/test_training.py`)

```python
from bot.main import training_command, State, Troll, Tree


def _state(turn, my_trolls, inv):
    return State(walkable={(0, 1)}, my_shack=(0, 0), opp_shack=(15, 7),
                 my_inventory=inv, opp_inventory=[0]*6, trees=[],
                 my_trolls=my_trolls, opp_trolls=[], turn=turn)


def _params(**over):
    p = {"max_trolls": 3, "train_specs": [(1, 1, 1, 0)],
         "min_turns_left_to_train": 25, "score_reserve": 0}
    p.update(over)
    return p


def test_trains_first_affordable_spec_when_resources_allow():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)            # off the shack
    st = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(st, _params()) == "TRAIN 1 1 1 0"


def test_no_train_when_cannot_afford():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    st = _state(1, [troll], [0, 0, 0, 0, 0, 0])
    assert training_command(st, _params()) is None


def test_no_train_when_shack_occupied():
    troll = Troll(0, 0, 0, 1, 1, 1, [0]*6)            # sitting on the shack
    st = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(st, _params()) is None


def test_no_train_when_at_cap_or_near_end():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    at_cap = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(at_cap, _params(max_trolls=1)) is None
    near_end = _state(290, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(near_end, _params()) is None


def test_score_reserve_blocks_overspending():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    # cost of (1,1,1) at n=1 is 2/2/2; inventory 2/2/2/3 totals 9, spend 6 -> 3 left
    st = _state(1, [troll], [2, 2, 2, 3, 0, 0])
    assert training_command(st, _params(score_reserve=5)) is None
    assert training_command(st, _params(score_reserve=3)) == "TRAIN 1 1 1 0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_training.py -v`
Expected: FAIL — `ImportError: cannot import name 'training_command'`.

- [ ] **Step 3: Write minimal implementation**

```python
def training_command(state, params):
    n = len(state.my_trolls)
    if n >= params["max_trolls"]:
        return None
    if TOTAL_TURNS - state.turn <= params["min_turns_left_to_train"]:
        return None
    if any(t.pos == state.my_shack for t in state.my_trolls):
        return None  # shack cell occupied; TRAIN would be rejected
    banked = sum(state.my_inventory[:4])
    for spec in params["train_specs"]:
        cost = training_cost(n, spec)
        if all(state.my_inventory[i] >= cost[i] for i in range(6)):
            if banked - sum(cost) >= params["score_reserve"]:
                return f"TRAIN {spec[0]} {spec[1]} {spec[2]} {spec[3]}"
    return None
```

Then wire into `decide` — after the gather loop, before the `if not commands` guard:

```python
    train = training_command(state, params)
    if train is not None:
        commands.append(train)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_training.py tests/test_decide.py -v`
Expected: PASS (all training tests; decide tests still pass because they set `max_trolls=0`).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_training.py
git commit -m "feat(bronze): economic training policy wired into decide"
```

---

## Task 7: Planting (orchard role, gated)

**Files:**
- Modify: `bot/main.py` (add `planting_commands`; call in `decide`)
- Modify: `tests/test_decide.py`

**Interfaces:**
- Consumes: `bfs_distances`, `ITEM_INDEX`, `_is_adjacent`.
- Produces: `planting_commands(state, params, used_ids:set) -> list[str]` — when `params["plant_enabled"]`, picks ONE idle (empty-handed, not already used) troll to grow the orchard: if it is adjacent to the shack and we have a seed of `params["plant_type"]` banked, emit `PICK id <TYPE>`; if it already carries that seed and stands on an empty grass cell that is one of the `params["orchard_cells"]`, emit `PLANT id <TYPE>`; if it carries the seed but isn't on a target cell, `MOVE` it to the nearest empty target cell. Returns `[]` when disabled or no action. `decide` integrates this so a planting troll is not also issued a gather command.

  `params` gains: `"plant_type": str` (e.g. `"BANANA"`), `"orchard_cells": list[tuple]` (target grass cells; empty list disables planting in practice), `"max_orchard": int`.

- [ ] **Step 1: Write the failing test** (append to `tests/test_decide.py`)

```python
from bot.main import planting_commands


def plant_params(cells):
    p = dict(PARAMS)
    p["plant_enabled"] = True
    p["plant_type"] = "BANANA"
    p["orchard_cells"] = cells
    p["max_orchard"] = 4
    return p


def test_picks_a_seed_when_idle_at_shack_and_orchard_wanted():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 0, 1, 1, 1, 1, [0]*6)      # empty, adjacent to shack
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0, 0, 0, 5, 0, 0], opp_inventory=[0]*6,
               trees=[], my_trolls=[troll], opp_trolls=[], turn=1)
    cmds = planting_commands(st, plant_params([(1, 1)]), set())
    assert cmds == ["PICK 0 BANANA"]


def test_plants_seed_on_target_cell():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 1, 1, 1, 1, 1, [0, 0, 0, 1, 0, 0])   # carries a banana seed
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=[],
               my_trolls=[troll], opp_trolls=[], turn=1)
    cmds = planting_commands(st, plant_params([(1, 1)]), set())
    assert cmds == ["PLANT 0 BANANA"]


def test_planting_disabled_returns_nothing():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 0, 1, 1, 1, 1, [0]*6)
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0, 0, 0, 5, 0, 0], opp_inventory=[0]*6,
               trees=[], my_trolls=[troll], opp_trolls=[], turn=1)
    assert planting_commands(st, gather_only(), set()) == []
```

(Reuse `gather_only()` from earlier in the file; it returns `plant_enabled=False`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_decide.py -v`
Expected: FAIL — `ImportError: cannot import name 'planting_commands'`.

- [ ] **Step 3: Write minimal implementation**

```python
def _occupied_cells(state):
    return {t.pos for t in state.my_trolls} | {t.pos for t in state.opp_trolls}


def planting_commands(state, params, used_ids):
    if not params.get("plant_enabled") or not params.get("orchard_cells"):
        return []
    seed = params["plant_type"]
    seed_idx = ITEM_INDEX[seed]
    tree_cells = {t.pos for t in state.trees}
    # target cells still needing a tree
    open_cells = [c for c in params["orchard_cells"]
                  if c in state.walkable and c not in tree_cells]
    if not open_cells or len(tree_cells & set(params["orchard_cells"])) >= params["max_orchard"]:
        return []
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.id in used_ids:
            continue
        carrying_seed = troll.carry[seed_idx] > 0
        if not carrying_seed and troll.total_carried > 0:
            continue  # busy carrying real fruit; let it gather/bank
        if carrying_seed:
            if troll.pos in open_cells:
                return [f"PLANT {troll.id} {seed}"]
            dist = bfs_distances(state.walkable, [troll.pos])
            reachable = [c for c in open_cells if c in dist]
            if reachable:
                tgt = min(reachable, key=lambda c: dist[c])
                return [f"MOVE {troll.id} {tgt[0]} {tgt[1]}"]
            return []
        # need a seed: pick one if we have it banked and we're at the shack
        if state.my_inventory[seed_idx] > 0 and _is_adjacent(troll.pos, state.my_shack):
            return [f"PICK {troll.id} {seed}"]
    return []
```

Wire into `decide`: run planting first to claim a troll, then skip that troll in the gather loop:

```python
def decide(state, params):
    commands = []
    used_ids = set()
    plant_cmds = planting_commands(state, params, used_ids)
    for c in plant_cmds:
        used_ids.add(int(c.split()[1]))
    commands.extend(plant_cmds)

    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    return_dist = bfs_distances(state.walkable, shack_adj)
    reserved = set()
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.id in used_ids:
            continue
        dist_t = bfs_distances(state.walkable, [troll.pos])
        cmd, reserved_pos = gather_command(state, troll, reserved, dist_t,
                                           return_dist, params)
        if reserved_pos is not None:
            reserved.add(reserved_pos)
        commands.append(cmd)

    train = training_command(state, params)
    if train is not None:
        commands.append(train)

    if not commands:
        commands = ["WAIT"]
    return commands
```

Add the new keys to the `PARAMS` default dict:

```python
    "plant_type": "BANANA",
    "orchard_cells": [],     # empty => planting effectively off until tuned
    "max_orchard": 4,
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest -q`
Expected: PASS (full suite, including the new planting tests).

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_decide.py
git commit -m "feat(bronze): gated orchard planting (PICK/PLANT) integrated into decide"
```

---

## Task 8: Wire the game loop + end-to-end smoke test

**Files:**
- Modify: `bot/main.py` (`main` calls `decide`, tracks the turn counter, prints `;`-joined commands)
- Modify: `tests/sample_input.txt` (a league-2 turn with 2 own trolls + 1 opponent)
- Create: `tests/test_endtoend.py`

**Interfaces:**
- Consumes: `parse_grid`, `parse_turn`, `decide`, `PARAMS`.
- Produces: `main()` — reads the init block, then each turn parses a `State` (incrementing `turn` from 1) and prints `";".join(decide(state, PARAMS))`.

- [ ] **Step 1: Write the failing test**

Replace `tests/sample_input.txt` with a league-2 turn (own trolls have ids 0 and 2; one sits on the shack at (5,3)):

```
16 8
................
................
................
.....0..........
..........1.....
................
................
................
4 4 4 4 0 0
2 2 2 2 0 0
2
PLUM 5 1 4 4 2 5
BANANA 10 6 4 6 0 2
3
0 0 5 3 1 1 1 0 0 0 0 0 0 0
2 0 6 1 2 4 3 0 0 0 0 0 0 0
1 1 10 4 1 1 1 0 0 0 0 0 0 0
```

```python
# tests/test_endtoend.py
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bot_runs_on_sample_and_emits_commands():
    sample = (ROOT / "tests" / "sample_input.txt").read_text()
    out = subprocess.run([sys.executable, str(ROOT / "bot" / "main.py")],
                         input=sample, capture_output=True, text=True, timeout=10)
    line = out.stdout.strip().splitlines()[0]
    parts = line.split(";")
    # one command per own troll (ids 0 and 2), each a valid verb
    verbs = {p.strip().split()[0] for p in parts}
    assert verbs <= {"MOVE", "HARVEST", "DROP", "WAIT", "PICK", "PLANT", "TRAIN", "MSG"}
    assert any(p.strip().startswith(("MOVE", "HARVEST")) for p in parts)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_endtoend.py -v`
Expected: FAIL — `main()` still uses the old single-troll `choose_action` / `parse_turn` signature, so it raises (wrong arg count) and stdout is empty.

- [ ] **Step 3: Write minimal implementation** (replace `main` in `bot/main.py`)

```python
def main():
    width, height = (int(v) for v in input().split())
    grid_lines = [input() for _ in range(height)]
    walkable, my_shack, opp_shack = parse_grid(grid_lines)

    def line_reader():
        while True:
            yield input()

    lines = line_reader()
    turn = 0
    try:
        while True:
            turn += 1
            state = parse_turn(lines, walkable, my_shack, opp_shack, turn)
            print(";".join(decide(state, PARAMS)), flush=True)
    except EOFError:
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_endtoend.py -v`
Expected: PASS — first output line has two troll commands with valid verbs.

- [ ] **Step 5: Run the full suite + manual smoke**

Run: `uv run pytest -q`
Expected: PASS (all tests).
Run: `uv run python bot/main.py < tests/sample_input.txt`
Expected: a single line like `MOVE 0 5 1;MOVE 2 6 1` (exact targets may differ), optionally with a `TRAIN ...`.

- [ ] **Step 6: Commit**

```bash
git add bot/main.py tests/sample_input.txt tests/test_endtoend.py
git commit -m "feat(bronze): game loop drives multi-troll decide(); e2e smoke test"
```

---

## Self-Review

**Spec coverage:**
- Multi-troll model + parsing → Tasks 1–2. ✓
- Generalized gather (capacity > 1) + reservations → Task 4 (`topup_radius`, reservation set in Task 5). ✓
- Training economy (`n+stat²`, tunable count/spec/timing/reserve) → Tasks 3, 6. ✓
- Planting (PICK/PLANT, gated, tunable) → Task 7. ✓
- Single-file submission + game loop → Task 8. ✓
- Simulator / boss port / mapgen / harness / offline tuning → **out of scope here**, deferred to Plan 2 (this plan ships a bot with hand-set `PARAMS`). Spec build-order steps 4–5 (and re-tuning planting) are Plan 2.

**Placeholder scan:** No TBD/TODO; every code step has full code. ✓

**Type consistency:** `Troll(carry:list)`, `.total_carried`, `.free_capacity`; `State(... my_trolls, opp_trolls, turn)`; `gather_command -> (str, pos|None)`; `best_tree -> Tree|None`; `training_command -> str|None`; `planting_commands -> list[str]`; `decide -> list[str]`; `parse_turn(lines, walkable, my_shack, opp_shack, turn)`. Names/signatures consistent across tasks. ✓

**Note for the implementer:** Between Tasks 1–3 the full suite is intentionally red (old `choose_action`/`State` references). Run the per-task test files named in each command. Task 4 deletes `choose_action` and migrates `tests/test_action.py`; the whole suite is green again from Task 4 onward.
