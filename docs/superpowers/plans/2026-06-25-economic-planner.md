# Economic Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `bot/main.py`'s hand-tuned greedy economic choices (what to gather, whether to plant, which TRAIN spec) with an analytic economic model that projects candidate build orders to turn 300 and picks the best, re-planned every turn.

**Architecture:** Three pure functions added to `bot/main.py` — `estimate_rates(state)` measures per-map economic rates, `project(state, policy, rates)` is a tiny rate-based forward sim with no positions, `search_policy(state, params)` enumerates build orders and returns a `Plan`. `decide()` calls the planner and feeds the `Plan` into the existing reactive layer. The `sim/` harness validates the projector against the full sim by rank correlation before the model is trusted.

**Tech Stack:** Python 3.11, stdlib only in `bot/main.py`, pytest + the existing `sim/` package. Run tests with `uv run pytest`.

## Global Constraints

- Single-file submission: all in-game code in `bot/main.py`; `sim/` is dev-only.
- stdlib only in `bot/main.py` (no new imports beyond `collections`, `dataclasses`).
- Runtime: projector O(300 × small); per-turn search a few dozen projections.
- v1 is single-agent: the economic model ignores the opponent.
- Reuse existing helpers verbatim: `bfs_distances`, `_ortho_neighbors`, `_is_adjacent`, `training_cost`, `ITEM_INDEX`, `PLANT_COOLDOWN`, `TOTAL_TURNS`, `Tree`, `Troll`, `State`.
- Fidelity gate: projector-vs-sim Spearman rank correlation mean ≥ 0.7 (Task 5) before integration (Task 6).
- Bronze item indices: PLUM 0, LEMON 1, APPLE 2, BANANA 3, IRON 4, WOOD 5. WOOD scores 4 pts; fruit 1 pt.

---

### Task 1: Rate estimator — constants, `Rates`, `estimate_rates`

**Files:**
- Modify: `bot/main.py` (add constants + `Rates` dataclass + `_effective_cooldown` + `estimate_rates` after `training_cost`, before `best_tree`)
- Test: `tests/test_rates.py` (create)

**Interfaces:**
- Consumes: `State`, `Tree`, `bfs_distances`, `_ortho_neighbors`, `_is_adjacent`, `ITEM_INDEX`, `PLANT_COOLDOWN`.
- Produces:
  - `WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}`
  - `WOOD_POINTS = 4`
  - `INF = float("inf")`
  - `@dataclass Rates(fruit_supply: list, mean_dist: float, mean_tree_size: float, mean_tree_health: float, iron_dist: float)` — `fruit_supply` length-4 (fruits/turn per fruit type), `iron_dist` steps to nearest iron approach cell or `INF`.
  - `estimate_rates(state) -> Rates`
  - `_has_iron(rates) -> bool` (== `rates.iron_dist != INF`)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rates.py
from bot.main import State, Tree, estimate_rates, INF, _has_iron, ITEM_INDEX


def _line_map():
    # walkable strip y=0, x=0..5; shack at (0,0)-adjacent gathering from (1,0)
    walkable = {(x, 0) for x in range(6)}
    return walkable


def test_fruit_supply_counts_reachable_trees_by_cooldown():
    walkable = _line_map()
    # PLUM tree (cooldown 8) at (3,0): reachable; APPLE (cooldown 9) at (5,0)
    trees = [Tree("PLUM", 3, 0, 1, 6, 0, 0), Tree("APPLE", 5, 0, 1, 6, 0, 0)]
    st = State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
               my_trolls=[], opp_trolls=[], turn=1)
    r = estimate_rates(st)
    assert abs(r.fruit_supply[ITEM_INDEX["PLUM"]] - 1/8) < 1e-9
    assert abs(r.fruit_supply[ITEM_INDEX["APPLE"]] - 1/9) < 1e-9
    assert r.fruit_supply[ITEM_INDEX["LEMON"]] == 0.0
    assert r.iron_dist == INF
    assert _has_iron(r) is False


def test_unreachable_tree_excluded_and_iron_distance():
    walkable = _line_map()
    trees = [Tree("PLUM", 3, 0, 1, 6, 0, 0), Tree("LEMON", 9, 9, 1, 6, 0, 0)]
    st = State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
               my_trolls=[], opp_trolls=[], turn=1,
               iron_cells=frozenset({(3, 1)}))   # approached from (3,0), dist 3
    r = estimate_rates(st)
    assert r.fruit_supply[ITEM_INDEX["LEMON"]] == 0.0   # (9,9) unreachable
    assert r.iron_dist == 3
    assert _has_iron(r) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rates.py -v`
Expected: FAIL with `ImportError: cannot import name 'estimate_rates'`

- [ ] **Step 3: Write minimal implementation**

Add to `bot/main.py` (after `training_cost`):

```python
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
WOOD_POINTS = 4
INF = float("inf")


@dataclass
class Rates:
    fruit_supply: list        # length 4: fruits/turn per fruit type
    mean_dist: float          # mean shack->reachable-tree distance (steps)
    mean_tree_size: float     # mean reachable tree size (wood/tree proxy)
    mean_tree_health: float   # mean reachable tree health (fell-time proxy)
    iron_dist: float          # steps to nearest iron approach cell, else INF


def _has_iron(rates):
    return rates.iron_dist != INF


def _effective_cooldown(state, tree):
    cd = PLANT_COOLDOWN[tree.type]
    if any(_is_adjacent(tree.pos, w) for w in state.water_cells):
        cd -= WATER_BOOST[tree.type]
    return max(cd, 1)


def estimate_rates(state):
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    dist = bfs_distances(state.walkable, shack_adj)
    supply = [0.0, 0.0, 0.0, 0.0]
    dsum = size_sum = health_sum = 0.0
    n = 0
    for t in state.trees:
        if t.pos not in dist:
            continue
        ti = ITEM_INDEX[t.type]
        if ti <= 3:
            supply[ti] += 1.0 / _effective_cooldown(state, t)
        dsum += dist[t.pos]
        size_sum += max(t.size, 1)
        health_sum += max(t.health, 1)
        n += 1
    mean_dist = dsum / n if n else 4.0
    mean_size = size_sum / n if n else 1.0
    mean_health = health_sum / n if n else 6.0
    iron_dist = INF
    if state.iron_cells:
        cands = [dist[a] for c in state.iron_cells
                 for a in _ortho_neighbors(c) if a in dist]
        if cands:
            iron_dist = min(cands)
    return Rates(supply, mean_dist, mean_size, mean_health, iron_dist)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rates.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_rates.py
git commit -m "feat: economic rate estimator (per-type fruit supply, distances)"
```

---

### Task 2: Production-rate functions

**Files:**
- Modify: `bot/main.py` (add after `estimate_rates`)
- Test: `tests/test_rates.py` (append)

**Interfaces:**
- Consumes: `Rates`, `_has_iron`, `INF`.
- Produces:
  - `gatherer_rate(rates, stats) -> float` — fruits/turn one gatherer banks. `stats` is `(ms, cc, hp, chop)`.
  - `chopper_wood_rate(rates, stats) -> float` — wood/turn one chopper fells.
  - `chopper_iron_rate(rates, stats) -> float` — iron/turn one chopper mines.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rates.py  (append)
from bot.main import (gatherer_rate, chopper_wood_rate, chopper_iron_rate,
                      Rates, INF)


def test_gatherer_rate_increases_with_capacity_and_speed():
    r = Rates([0.5, 0, 0, 0], mean_dist=4.0, mean_tree_size=2.0,
              mean_tree_health=6.0, iron_dist=INF)
    slow = gatherer_rate(r, (1, 1, 1, 0))
    big = gatherer_rate(r, (1, 3, 1, 0))
    fast = gatherer_rate(r, (2, 1, 1, 0))
    assert big > slow and fast > slow
    # cc=1, ms=1, mean_dist=4 -> cycle = 2*4/1 + 1 = 9 -> 1/9
    assert abs(slow - 1/9) < 1e-9


def test_chopper_rates_zero_without_chop_or_iron():
    r = Rates([0, 0, 0, 0], 4.0, 2.0, 6.0, iron_dist=INF)
    assert chopper_wood_rate(r, (1, 2, 0, 0)) == 0.0       # chop 0
    assert chopper_iron_rate(r, (1, 2, 0, 3)) == 0.0       # no iron on map
    assert chopper_wood_rate(r, (1, 2, 0, 3)) > 0.0
    r2 = Rates([0, 0, 0, 0], 4.0, 2.0, 6.0, iron_dist=2.0)
    assert chopper_iron_rate(r2, (1, 2, 0, 3)) > 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rates.py -v`
Expected: FAIL with `ImportError: cannot import name 'gatherer_rate'`

- [ ] **Step 3: Write minimal implementation**

```python
def gatherer_rate(rates, stats):
    ms, cc, hp, chop = stats
    cycle = 2.0 * rates.mean_dist / max(ms, 1) + 1.0
    return cc / cycle


def chopper_wood_rate(rates, stats):
    ms, cc, hp, chop = stats
    if chop <= 0:
        return 0.0
    fell = max(1.0, -(-rates.mean_tree_health // chop))   # ceil division
    travel = 2.0 * rates.mean_dist / max(ms, 1)
    wood_per_trip = min(cc, rates.mean_tree_size)
    return wood_per_trip / (fell + travel + 1.0)


def chopper_iron_rate(rates, stats):
    ms, cc, hp, chop = stats
    if chop <= 0 or not _has_iron(rates):
        return 0.0
    travel = 2.0 * rates.iron_dist / max(ms, 1)
    iron_per_trip = min(cc, chop)
    return iron_per_trip / (travel + 1.0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rates.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_rates.py
git commit -m "feat: gatherer/chopper production-rate functions"
```

---

### Task 3: Economic projector

**Files:**
- Modify: `bot/main.py` (add after the rate functions)
- Test: `tests/test_projector.py` (create)

**Interfaces:**
- Consumes: `State`, `Rates`, `training_cost`, `ITEM_INDEX`, `TOTAL_TURNS`, `WOOD_POINTS`, `_has_iron`, the rate functions, `gatherer_rate`, `chopper_wood_rate`, `chopper_iron_rate`.
- Produces:
  - `ROLE_CHOP = "C"`, `ROLE_GATH = "G"`, `RAMP_DELAY_CAP = 8`
  - `_role_of(stats) -> str` (CHOP if `stats[3] >= 2` else GATH)
  - `project(state, policy, rates) -> float` — predicted score@300. `policy` is an ordered list of specs `(ms,cc,hp,chop)` to build from now.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_projector.py
from bot.main import (State, Troll, Rates, project, INF, ITEM_INDEX,
                      estimate_rates, Tree)


def _state(inv, trolls, turn=1, iron=frozenset()):
    walkable = {(x, 0) for x in range(6)}
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=[Tree("PLUM", 3, 0, 1, 6, 0, 0)],
                 my_trolls=list(trolls), opp_trolls=[], turn=turn, iron_cells=iron)


def _g(id, stats):
    return Troll(id=id, x=0, y=0, movement_speed=stats[0], carry_capacity=stats[1],
                 harvest_power=stats[2], carry=[0]*6, chop_power=stats[3])


def test_empty_policy_just_banks_production():
    st = _state([0]*6, [_g(0, (1, 1, 1, 0))])
    r = estimate_rates(st)
    score = project(st, [], r)
    assert score > 0          # one gatherer accrues fruit over the horizon


def test_late_investment_not_worth_it():
    # With few turns left, adding a troll (cost paid, no payback) <= just banking.
    st = _state([20, 20, 20, 0, 20, 0], [_g(0, (1, 1, 1, 0))], turn=295)
    r = estimate_rates(st)
    bank = project(st, [], r)
    invest = project(st, [(2, 2, 2, 0)], r)
    assert bank >= invest


def test_more_gatherers_help_early():
    st = _state([20, 20, 20, 0, 20, 0], [_g(0, (1, 1, 1, 0))], turn=1)
    r = estimate_rates(st)
    bank = project(st, [], r)
    invest = project(st, [(1, 1, 1, 0)], r)
    assert invest >= bank      # early expansion pays back within the horizon
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_projector.py -v`
Expected: FAIL with `ImportError: cannot import name 'project'`

- [ ] **Step 3: Write minimal implementation**

```python
ROLE_CHOP = "C"
ROLE_GATH = "G"
RAMP_DELAY_CAP = 8


def _role_of(stats):
    return ROLE_CHOP if stats[3] >= 2 else ROLE_GATH


def _stats_of(troll):
    return (troll.movement_speed, troll.carry_capacity,
            troll.harvest_power, troll.chop_power)


def project(state, policy, rates):
    banked = [float(v) for v in state.my_inventory]
    roster = [(_role_of(_stats_of(t)), _stats_of(t)) for t in state.my_trolls]
    pending = []                         # (ready_at, role, stats)
    bi = 0
    ramp = min(int(rates.mean_dist) + 1, RAMP_DELAY_CAP)
    iron_i = ITEM_INDEX["IRON"]
    wood_i = ITEM_INDEX["WOOD"]
    pay = (0, 1, 2, 4) if _has_iron(rates) else (0, 1, 2)
    for t in range(state.turn, TOTAL_TURNS + 1):
        for p in [p for p in pending if p[0] <= t]:
            roster.append((p[1], p[2]))
            pending.remove(p)
        n_now = len(roster) + len(pending)
        need = [0.0] * 6
        if bi < len(policy):
            cost = training_cost(n_now, policy[bi])
            for i in range(6):
                need[i] = max(cost[i] - banked[i], 0.0)
        # gatherers: needed fruit types first, then highest supply for score
        remaining = sum(gatherer_rate(rates, s) for (r, s) in roster if r == ROLE_GATH)
        for i in sorted(range(4), key=lambda j: (-need[j], -rates.fruit_supply[j])):
            if remaining <= 0:
                break
            take = min(remaining, rates.fruit_supply[i])
            banked[i] += take
            remaining -= take
        # choppers: mine while the next investment still needs iron, else chop
        for (r, s) in roster:
            if r != ROLE_CHOP:
                continue
            if need[iron_i] > 0:
                banked[iron_i] += chopper_iron_rate(rates, s)
            else:
                banked[wood_i] += chopper_wood_rate(rates, s)
        # investment (earliest-affordable)
        if bi < len(policy):
            spec = policy[bi]
            cost = training_cost(n_now, spec)
            if all(banked[i] >= cost[i] for i in pay):
                for i in pay:
                    banked[i] -= cost[i]
                pending.append((t + ramp, _role_of(spec), spec))
                bi += 1
    return sum(banked[0:4]) + WOOD_POINTS * banked[wood_i]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_projector.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_projector.py
git commit -m "feat: rate-based economic projector (finite-horizon score@300)"
```

---

### Task 4: Policy search and `Plan`

**Files:**
- Modify: `bot/main.py` (add after `project`)
- Test: `tests/test_search.py` (create)

**Interfaces:**
- Consumes: `State`, `estimate_rates`, `project`, `training_cost`, `ITEM_INDEX`.
- Produces:
  - `GATHERER_SPECS = [(1, 1, 1, 0), (1, 2, 1, 0), (2, 2, 2, 0)]`
  - `CHOPPER_SPECS = [(1, 3, 0, 2), (2, 4, 0, 3), (2, 4, 0, 4)]`
  - `candidate_policies() -> list[list[tuple]]`
  - `@dataclass Plan(train: tuple, gather_types: list, plant: str)` — `train` is the spec to TRAIN now or `None`; `gather_types` ordered fruit-type indices to prioritize; `plant` a type name or `None`.
  - `search_policy(state, params=None) -> Plan` — honours `params["forced_policy"]` (a policy list) when present, else searches.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_search.py
from bot.main import (State, Troll, Tree, search_policy, candidate_policies,
                      ITEM_INDEX)


def _state(inv, turn=1, trees=None, iron=frozenset(), walkable=None):
    walkable = walkable or {(x, 0) for x in range(6)}
    troll = Troll(id=0, x=0, y=0, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carry=[0]*6, chop_power=1)
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=trees if trees is not None else [Tree("LEMON", 3, 0, 1, 6, 0, 0)],
                 my_trolls=[troll], opp_trolls=[], turn=turn, iron_cells=iron)


def test_no_plum_supply_means_no_movement_training():
    # Only LEMON trees reachable -> PLUM supply 0 -> any movement-stat (ms>1)
    # spec is unfundable; the chosen plan's training must not demand PLUM we
    # cannot supply. We assert: no scheduled spec needs ms>1.
    st = _state([5, 5, 5, 0, 5, 0], trees=[Tree("LEMON", 3, 0, 1, 6, 0, 0)])
    plan = search_policy(st)
    if plan.train is not None:
        assert plan.train[0] == 1      # movement speed stays 1 (no PLUM needed beyond n)


def test_late_game_stops_investing():
    st = _state([20, 20, 20, 0, 20, 0], turn=296)
    plan = search_policy(st)
    assert plan.train is None


def test_forced_policy_is_obeyed():
    st = _state([20, 20, 20, 0, 20, 0])
    plan = search_policy(st, {"forced_policy": [(2, 2, 2, 0)]})
    assert plan.train == (2, 2, 2, 0)


def test_candidates_include_empty_and_chopper():
    cands = candidate_policies()
    assert [] in cands
    assert any(spec[3] >= 2 for pol in cands for spec in pol)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_search.py -v`
Expected: FAIL with `ImportError: cannot import name 'search_policy'`

- [ ] **Step 3: Write minimal implementation**

```python
GATHERER_SPECS = [(1, 1, 1, 0), (1, 2, 1, 0), (2, 2, 2, 0)]
CHOPPER_SPECS = [(1, 3, 0, 2), (2, 4, 0, 3), (2, 4, 0, 4)]


@dataclass
class Plan:
    train: tuple        # spec to TRAIN now, or None
    gather_types: list  # ordered fruit-type indices to prioritize
    plant: str          # plant type name, or None


def candidate_policies():
    cands = [[]]
    for g in GATHERER_SPECS:
        cands.append([g])
        cands.append([g, g])
    for c in CHOPPER_SPECS:
        cands.append([c])
        for g in GATHERER_SPECS:
            cands.append([c, g])
            cands.append([c, g, g])
    return cands


def _plan_from_policy(state, policy):
    n = len(state.my_trolls)
    league3 = bool(state.iron_cells)
    pay = (0, 1, 2, 4) if league3 else (0, 1, 2)
    if not policy:
        return Plan(None, [], None)
    first = policy[0]
    cost = training_cost(n, first)
    affordable = all(state.my_inventory[i] >= cost[i] for i in pay)
    gather_types = sorted((i for i in range(4) if state.my_inventory[i] < cost[i]),
                          key=lambda i: state.my_inventory[i] - cost[i])
    return Plan(first if affordable else None, gather_types, None)


def search_policy(state, params=None):
    if params and params.get("forced_policy") is not None:
        return _plan_from_policy(state, params["forced_policy"])
    rates = estimate_rates(state)
    best, best_score = [], None
    for pol in candidate_policies():
        s = project(state, pol, rates)
        if best_score is None or s > best_score:
            best_score, best = s, pol
    return _plan_from_policy(state, best)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_search.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_search.py
git commit -m "feat: policy search + Plan (build-order enumeration over rate model)"
```

---

### Task 5: Projector-vs-sim rank-correlation gate (GO/NO-GO)

**Files:**
- Create: `tests/test_projector_corr.py`
- Modify: `bot/main.py` `decide()` minimally (Step 3): when `params["forced_policy"]` is set, training follows that policy; when absent, `decide()` behaves exactly as v0.6.1 (still uses `training_command`). This is the only `decide()` change in this task and keeps the existing suite green.

**Interfaces:**
- Consumes: `bot.main.project`, `bot.main.estimate_rates`, `bot.main.search_policy`, `bot.main.decide`, `sim.mapgen.generate_bronze`, `sim.views.build_view`, `sim.engine.step`, `bot.main.training_command` (still present until Task 6).
- Produces: a test asserting mean Spearman ≥ 0.7.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_projector_corr.py
from bot.main import (project, estimate_rates, CHOPPER_SPECS, GATHERER_SPECS,
                      decide)
from sim.mapgen import generate_bronze
from sim.views import build_view
from sim.engine import step


POLICIES = [
    [],
    [GATHERER_SPECS[0]],
    [GATHERER_SPECS[0], GATHERER_SPECS[0]],
    [CHOPPER_SPECS[0]],
    [CHOPPER_SPECS[1], GATHERER_SPECS[0]],
    [CHOPPER_SPECS[2], GATHERER_SPECS[2], GATHERER_SPECS[2]],
]


def _spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0] * len(v)
        for pos, i in enumerate(order):
            rk[i] = pos
        return rk
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    vx = sum((rx[i]-mx)**2 for i in range(n)) ** 0.5
    vy = sum((ry[i]-my)**2 for i in range(n)) ** 0.5
    return cov / (vx*vy) if vx and vy else 0.0


def _policy_decide(state, policy, params):
    # Train this policy's specs in order (earliest-affordable), otherwise act
    # exactly like the shipped bot. Implemented via forced_policy in params.
    p = dict(params)
    p["forced_policy"] = policy
    return decide(state, p)


def _sim_score(seed, policy):
    g = generate_bronze(seed)
    from bot.main import PARAMS
    opp = dict(PARAMS)
    opp["forced_policy"] = []          # fixed, non-expanding opponent (stable gate)
    for _ in range(300):
        cmds0 = _policy_decide(build_view(g, 0), policy, PARAMS)
        cmds1 = decide(build_view(g, 1), opp)
        step(g, cmds0, cmds1)
    return g.scores[0]


def test_projector_ranks_policies_like_the_sim():
    from sim.views import build_view as bv
    corrs = []
    for seed in range(6):
        g = generate_bronze(seed)
        st = bv(g, 0)
        r = estimate_rates(st)
        predicted = [project(st, pol, r) for pol in POLICIES]
        actual = [_sim_score(seed, pol) for pol in POLICIES]
        corrs.append(_spearman(predicted, actual))
    mean = sum(corrs) / len(corrs)
    assert mean >= 0.7, f"projector rank-correlation too low: {mean:.2f} ({corrs})"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_projector_corr.py -v`
Expected: FAIL — either `ImportError` (if `decide` doesn't yet accept `forced_policy`) or an assertion if correlation is low.

- [ ] **Step 3: Make `decide()` honour `forced_policy` for training only**

In `bot/main.py` `decide()`, locate the training emission:

```python
    train = training_command(state, params)
    if train is not None:
        commands.append(train)
```

Replace with:

```python
    if params.get("forced_policy") is not None:
        plan = search_policy(state, params)
        if (plan.train is not None
                and TOTAL_TURNS - state.turn > params["min_turns_left_to_train"]
                and not any(t.pos == state.my_shack for t in state.my_trolls)
                and len(state.my_trolls) < params["max_trolls"]):
            commands.append(f"TRAIN {plan.train[0]} {plan.train[1]} "
                            f"{plan.train[2]} {plan.train[3]}")
    else:
        train = training_command(state, params)
        if train is not None:
            commands.append(train)
```

This leaves v0.6.1 behavior untouched when `forced_policy` is absent, so the existing suite stays green, and lets the sim play a forced build order.

- [ ] **Step 4: Run the gate**

Run: `uv run pytest tests/test_projector_corr.py -v`
Expected: PASS (mean ≥ 0.7).

**If it FAILS the threshold:** STOP and report. The model is not yet faithful enough to trust. Likely fixes, in order: (a) make `ramp` depend on actual shack→tree distance per role; (b) cap aggregate gatherer collection per type at `fruit_supply` (already done) but also split chopper time between mine and chop instead of all-or-nothing; (c) include carried-but-unbanked at horizon end. Apply ONE fix, re-run, and record what moved the correlation. Do not proceed to Task 6 until the gate passes.

- [ ] **Step 5: Commit**

```bash
git add bot/main.py tests/test_projector_corr.py
git commit -m "test: projector-vs-sim rank-correlation gate (>=0.7); decide honours forced_policy"
```

---

### Task 6: Wire the planner into `decide()` (shippable v0.7.0)

**Files:**
- Modify: `bot/main.py` — `decide()`, `best_tree`, `PARAMS`, `VERSION`; remove `training_command`.
- Modify: `tests/test_decide.py` — update expectations for planner-driven training/gathering.
- Delete: `tests/test_training.py` (its subject, `training_command`, is removed; the planner replaces it and is covered by `tests/test_search.py`).
- Test: `tests/test_planner_integration.py` (create)

**Interfaces:**
- Consumes: `search_policy`, `Plan`, `estimate_rates`.
- Produces: planner-driven `decide()`; `best_tree` honours `params["gather_types"]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_planner_integration.py
from bot.main import decide, PARAMS, State, Troll, Tree


def _bronze_state(inv, turn=1):
    walkable = {(x, 0) for x in range(8)} | {(x, 1) for x in range(8)}
    troll = Troll(id=0, x=0, y=1, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carry=[0]*6, chop_power=1)
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(7, 0),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=[Tree("PLUM", 3, 1, 1, 6, 0, 0),
                        Tree("APPLE", 5, 1, 1, 6, 0, 0)],
                 my_trolls=[troll], opp_trolls=[], turn=turn,
                 iron_cells=frozenset({(2, 0)}))


def test_decide_runs_and_emits_commands_without_forced_policy():
    cmds = decide(_bronze_state([5, 5, 5, 0, 5, 0]), PARAMS)
    assert isinstance(cmds, list) and cmds            # non-empty, no crash


def test_no_planting_command_by_default():
    # v1 core: planning replaces the orchard churn -> no PLANT emitted.
    cmds = decide(_bronze_state([5, 5, 5, 5, 5, 0]), PARAMS)
    assert not any(c.startswith("PLANT") for c in cmds)


def test_late_game_emits_no_train():
    cmds = decide(_bronze_state([30, 30, 30, 0, 30, 0], turn=296), PARAMS)
    assert not any(c.startswith("TRAIN") for c in cmds)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_planner_integration.py -v`
Expected: FAIL (`test_no_planting_command_by_default` fails — v0.6.1 still plants).

- [ ] **Step 3: Implement planner-driven `decide()`**

3a. Add `gather_types` support to `best_tree`. Replace its key block:

```python
        wait = ripe - walk
        key = (wait, ripe + return_dist[tree.pos], walk)
```

with:

```python
        gather_types = params.get("gather_types", [])
        ti = ITEM_INDEX[tree.type]
        short = 0 if ti in gather_types else 1
        wait = ripe - walk
        key = (short, wait, ripe + return_dist[tree.pos], walk)
```

3b. In `decide()`, immediately after `return_dist = bfs_distances(...)` add:

```python
    plan = search_policy(state, params)
    params = dict(params)
    params["gather_types"] = plan.gather_types
```

3c. Gate planting on the plan. Change:

```python
    if params.get("plant_enabled"):
```

to:

```python
    if params.get("plant_enabled") and plan.plant is not None:
```

3d. Replace the whole training-emission block (the `forced_policy`/`else` block from Task 5) with:

```python
    if (plan.train is not None
            and TOTAL_TURNS - state.turn > params["min_turns_left_to_train"]
            and not any(t.pos == state.my_shack for t in state.my_trolls)
            and len(state.my_trolls) < params["max_trolls"]):
        commands.append(f"TRAIN {plan.train[0]} {plan.train[1]} "
                        f"{plan.train[2]} {plan.train[3]}")
```

3e. Delete the `training_command` function entirely.

3f. Bump `VERSION = "0.7.0"`.

3g. In `PARAMS`, leave `plant_enabled: True` but note `plant` is plan-gated; remove `train_specs`, `chopper_specs`, `max_choppers`, `chopper_after`/`fruit_target` if present (the planner supersedes them). Keep `topup_radius`, `max_trolls`, `iron_target`, `min_turns_left_to_train`, `score_reserve`, `plant_type`, `max_orchard`.

- [ ] **Step 4: Update affected tests and run the full suite**

Delete `tests/test_training.py`:

```bash
git rm tests/test_training.py
```

Run `uv run pytest -q`. For each failure in `tests/test_decide.py` caused by the removed `train_specs`/`training_command` or the new no-planting default, update the expectation to match planner-driven behavior (training now comes from `search_policy`; planting only when `plan.plant`). Do not weaken assertions about pathing/banking/deconfliction — those are unchanged.

Run: `uv run pytest -q`
Expected: PASS (all tests green, including the new integration + correlation tests).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: planner-driven decide() — model picks training, gathering, planting (v0.7.0)"
```

---

### Task 7 (after Task 6 ships): planting-as-investment

**Files:**
- Modify: `bot/main.py` — `project`, `candidate_policies`, `_plan_from_policy`, executor planting.
- Test: `tests/test_planting_investment.py` (create)

**Interfaces:**
- Consumes: `project`, `Rates`, `PLANT_COOLDOWN`, `Plan`.
- Produces: policies may contain a plant marker `("PLANT", type_name)`; the projector adds delayed supply; `Plan.plant` is set when the chosen policy's next step is a plant.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_planting_investment.py
from bot.main import project, estimate_rates, State, Troll, Tree, ITEM_INDEX


def _state_no_plum():
    walkable = {(x, 0) for x in range(6)}
    troll = Troll(id=0, x=0, y=0, movement_speed=1, carry_capacity=2,
                  harvest_power=1, carry=[0]*6, chop_power=0)
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
                 my_inventory=[0, 0, 0, 6, 0, 0],   # only BANANA seeds in hand
                 opp_inventory=[0]*6,
                 trees=[Tree("LEMON", 3, 0, 1, 6, 0, 0)], my_trolls=[troll],
                 opp_trolls=[], turn=1)


def test_planting_adds_delayed_supply():
    st = _state_no_plum()
    r = estimate_rates(st)
    no_plant = project(st, [], r)
    with_plant = project(st, [("PLANT", "PLUM")], r)
    # planting a PLUM tree creates PLUM supply that a no-PLUM map otherwise lacks,
    # so end score with the plant must strictly exceed the no-plant baseline.
    assert with_plant > no_plant
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_planting_investment.py -v`
Expected: FAIL (projector ignores `("PLANT", ...)` markers).

- [ ] **Step 3: Implement plant markers in `project`**

In `project`, detect a plant marker before the training branch. Maintain a local mutable copy of supply so a planted tree contributes after maturation:

```python
    supply = list(rates.fruit_supply)            # mutable copy near the top
    extra_supply = []                            # (ready_at, type_index, rate)
```

In the per-turn loop, before the investment branch, promote matured plants:

```python
        for e in [e for e in extra_supply if e[0] <= t]:
            supply[e[1]] += e[2]
            extra_supply.remove(e)
```

and make the gatherer-allocation loop read `supply[i]` instead of `rates.fruit_supply[i]`. Then in the investment branch, handle the marker:

```python
        if bi < len(policy):
            step_item = policy[bi]
            if isinstance(step_item, tuple) and step_item and step_item[0] == "PLANT":
                ptype = step_item[1]
                # cost: one seed of ptype from BANANA-or-own hand; model as 1 unit
                seed_i = ITEM_INDEX[ptype]
                # a planted tree matures, then yields 1/cooldown forever
                mature = PLANT_COOLDOWN[ptype] * 4      # ~size growth to fruiting
                extra_supply.append((t + mature, seed_i, 1.0 / PLANT_COOLDOWN[ptype]))
                bi += 1
            else:
                spec = step_item
                cost = training_cost(n_now, spec)
                if all(banked[i] >= cost[i] for i in pay):
                    for i in pay:
                        banked[i] -= cost[i]
                    pending.append((t + ramp, _role_of(spec), spec))
                    bi += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_planting_investment.py -v`
Expected: PASS.

- [ ] **Step 5: Add plant candidates + executor wiring, then commit**

Extend `candidate_policies()` with a few plant-led options, e.g. append `[("PLANT", "PLUM")], [("PLANT", "APPLE")], [("PLANT", "PLUM"), GATHERER_SPECS[0]]`. In `_plan_from_policy`, if the first step is a `("PLANT", type)` marker, return `Plan(None, [], type)` (planting, not training). The executor's plant block (Task 6, step 3c) already honours `plan.plant`. Run `uv run pytest -q` (all green), then:

```bash
git add -A
git commit -m "feat: planting-as-investment — model the plant->supply->train chain"
```

---

## Self-Review

**Spec coverage:**
- Rate estimator (per-type supply, distances, iron) → Task 1, 2. ✓
- Economic projector (finite-horizon, ramp, mine-vs-chop) → Task 3. ✓
- Policy search (build orders, earliest-affordable, single-agent) → Task 4. ✓
- Executor integration (gather_types, plant gating, train) → Task 6. ✓
- Validation: projector-vs-sim rank correlation (≥0.7 gate) → Task 5. ✓
- Regression: no-PLUM → no movement training → Task 4 (`test_no_plum_supply_means_no_movement_training`). ✓
- Single-file constraint (all in `bot/main.py`) → every task. ✓
- Planting-as-investment (the plant→resources→chopper chain) → Task 7. ✓

**Placeholder scan:** No TBD/TODO. Task 5's failure branch lists concrete fixes, not placeholders. The `if False else` shim in Task 3's test is intentional (documented inline).

**Type consistency:** `project(state, policy, rates)`, `estimate_rates(state)`, `search_policy(state, params=None)`, `Plan(train, gather_types, plant)`, `Rates(fruit_supply, mean_dist, mean_tree_size, mean_tree_health, iron_dist)`, `_role_of(stats)` used consistently across tasks. `ITEM_INDEX["IRON"]==4`, `["WOOD"]==5` used consistently. `candidate_policies` returns lists of specs (Tasks 4) and, after Task 7, possibly `("PLANT", type)` markers — `project` (Task 3) only iterates specs until Task 7 extends it; `_plan_from_policy` handles the marker only after Task 7. Consistent.

**Ordering note:** Tasks 1→6 deliver the shippable core (v0.7.0); Task 5 is the go/no-go gate before integration; Task 7 is an independent follow-up.
