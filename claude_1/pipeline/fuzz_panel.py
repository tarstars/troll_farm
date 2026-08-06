#!/usr/bin/env python3
"""fuzz_panel — randomized closed-loop property panel (pipeline final gate).

Motivation (round-4/5 pattern analysis): five hand-constructed scenario
suites in a row were green while broader panels found real defects — the
hand-picked geometries never sampled the state regions where the defects
live (ledger class UNSAMPLED_STATE_SPACE). This tool samples game states
mechanically: a seeded map generator produces varied geometries across
declared classes (open fields, choke/articulation corridors — the round-5
killer class — single/multi-door tents, water-adjacent diagonal cells,
orchard-eligible layouts, dense/sparse forests, iron present/absent), runs
REAL closed-loop games of the candidate and the parent on identical
map+opponent, and asserts machine-checkable properties on every candidate
game:

  P1  detectors D-1..D-9 (trace_detectors.run_all, amended D-8 semantics)
      must report zero episodes.  RAW/ABSOLUTE (owner ruling 2026-08-06):
      EVERY detector episode blocks, inherited-from-parent or not, on every
      map.  The two former parent-comparison exemptions are REMOVED — there
      is no D-1 inherited-report-only downgrade and no D-9
      parent-differential gate (the round-6 ROOT-A exemption is retired).
      The parent run is still computed (for the P3 inertness check and the
      diagnostic report) but never exempts a candidate detector episode.
      trace_detectors is unmodified (the base-detector questions go to the
      integrator).
  P2  R-5 class: no full-cargo two-cell alternation >= 6 turns without a
      cargo change (regression_tests.r5_two_worker_full_cargo_banking
      alternation clause).  The R-5 bounded-banking-horizon clause is
      surfaced as a report-tier flag, not a block.
  P3  on orchard-eligible seat views (mirror of SecureOrchardBot's
      initialize gates) the candidate's command stream must byte-equal the
      parent's (dormancy inertness).
  P4  liveness floor: RAW (owner ruling 2026-08-06) — some progress (own
      inventory or own-unit cargo change) in every rolling 60-turn window,
      with NO exemption.  The former "unless the parent also makes no
      progress in the same window" clause is removed; every stall window
      blocks.
  P0  protocol liveness: the candidate must emit one command line per turn
      for the whole game (a crash/early-close blocks).

Report-tier findings (flagged, never blocking): margin collapse on
banana-activated maps (candidate margin < parent margin - threshold) and
R-5 horizon misses.  (Under the raw gate there are no inherited-parent D-1
or D-9 report-tier downgrades — those episodes block.)

CLI:
  python3 fuzz_panel.py --config <json> --report <md> --json <out.json>
                        [--save-failures <dir>]
Exit codes: 0 = CLEAR, 1 = BLOCK, 2 = tool/config error.

Determinism: every random draw derives from the config-declared seed list
(seed -> per-map PRNG stream; regeneration on invalid geometry advances the
stream deterministically).  No time- or os-based randomness.  Optional
multiprocessing preserves per-game determinism; results are ordered by map
id before the verdict.  Wall time is measured for reporting only.

Reuses (imports, never modifies): the make_banana_traces referee core
(command application, growth, dynamic opponents), trace_detectors D-1..D-9,
regression_tests' R-5 machinery and closed-loop binary runner, and
semantic_harness's map/protocol/compile helpers.  FuzzReferee below is the
thin adapter that binds the referee to generated geometry (instance
walkable set / tent / water) without editing the original module.

Stdlib only (Python 3.12); rustc via semantic_harness (PATH + ~/.cargo/bin).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing
import random
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BR2 = (HERE.parent / "banana-restoration-r2").resolve()
if str(BR2) not in sys.path:
    sys.path.insert(0, str(BR2))

import semantic_harness as sh        # noqa: E402  (compiler + map helpers)
import trace_detectors as td         # noqa: E402  (D-1..D-9)
import make_banana_traces as mbt     # noqa: E402  (referee core)
import regression_tests as rt        # noqa: E402  (R-5 + binary runner)

EXIT_CLEAR, EXIT_BLOCK, EXIT_ERROR = 0, 1, 2

KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")
ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))
DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
WOOD = 5
BIG = 10_000

MAP_CLASSES = ("open_field", "choke_corridor", "single_door_tent",
               "multi_door", "water_diagonal", "orchard_eligible",
               "forest_dense", "forest_sparse")
OPP_PROFILES = ("idle", "harvester", "chopper_aggressor")

DEFAULTS = {
    "maps": 120,
    "turns": 200,
    "processes": 0,               # 0 => min(8, cpu_count)
    "liveness_window": 60,
    "margin_collapse_threshold": 100,
    "max_generation_attempts": 64,
    "class_mix": {
        "choke_corridor": 0.25, "open_field": 0.15, "single_door_tent": 0.10,
        "multi_door": 0.10, "water_diagonal": 0.15, "orchard_eligible": 0.10,
        "forest_dense": 0.08, "forest_sparse": 0.07,
    },
    "opponent_mix": {"idle": 0.30, "harvester": 0.40,
                     "chopper_aggressor": 0.30},
}


class PanelError(Exception):
    """Config / environment / generation error -> exit 2."""


def score(inv) -> int:
    """Mirror of rules::score (research-banana-r2.rs game::rules::score):
    1 point per banked fruit (PLUM/LEMON/APPLE/BANANA), WOOD_POINTS=4 per
    wood, iron worthless."""
    return inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Deterministic mix scheduling
# ---------------------------------------------------------------------------

def schedule(mix: dict, n: int) -> list:
    """Largest-deficit apportionment of a weight mix over n slots.
    Deterministic: sorted keys, deficit-then-name tie-break."""
    items = sorted((k, float(w)) for k, w in mix.items() if w > 0)
    if not items or n <= 0:
        raise PanelError("empty mix or non-positive slot count")
    total = sum(w for _, w in items)
    assigned = {k: 0 for k, _ in items}
    out = []
    for i in range(1, n + 1):
        best = max(items, key=lambda kv: (kv[1] * i / total
                                          - assigned[kv[0]], kv[0]))
        assigned[best[0]] += 1
        out.append(best[0])
    return out


# ---------------------------------------------------------------------------
# Map generation
# ---------------------------------------------------------------------------

def _blank(w, h):
    return [["#"] * w for _ in range(h)]


def _carve(grid, cells):
    for (x, y) in cells:
        grid[y][x] = "."


def _rows(grid):
    return ["".join(r) for r in grid]


def _in(w, h, cell):
    return 0 <= cell[0] < w and 0 <= cell[1] < h


def _orth_neighbors(cell):
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in ORTH]


def median(values):
    """Mirror of SecureOrchardBot::median (sorted; even count -> mean of the
    two middles)."""
    vs = sorted(values)
    n = len(vs)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return float(vs[n // 2])
    return (vs[n // 2 - 1] + vs[n // 2]) / 2.0


def orchard_eligible_view(rows, plants) -> bool:
    """Mirror of the candidate's SecureOrchardBot::initialize gates
    (research-banana-r2.rs): >= 2 own doors; at least one live natural
    plant; all naturals reachable from home doors with median home-door
    distance >= 8; and a free own door that is water-adjacent with
    enemy-door BFS distance >= 11."""
    geo = sh.parse_rows(tuple(rows))
    if 0 not in geo["shacks"] or 1 not in geo["shacks"]:
        return False
    walk = geo["walkable"]
    water = geo["water"]
    doors = sorted(c for c in _orth_neighbors(geo["shacks"][0]) if c in walk)
    if len(doors) < 2:
        return False
    natural = [(p[1], p[2]) for p in plants if p[4] > 0]  # health > 0
    if not natural:
        return False
    home = sh.bfs(walk, doors)
    returns = [home.get(c) for c in natural]
    if any(r is None for r in returns) or median(returns) < 8.0:
        return False
    enemy_doors = [c for c in _orth_neighbors(geo["shacks"][1]) if c in walk]
    edist = sh.bfs(walk, enemy_doors)
    plant_cells = {(p[1], p[2]) for p in plants}
    for door in doors:
        if door in plant_cells:
            continue
        if not any(w in water for w in _orth_neighbors(door)):
            continue
        if edist.get(door, BIG) >= 11:
            return True
    return False


def _mk_plant(rng, cell, kind=None, size=None, fruits=None, cd=None,
              health=None):
    kind = kind or rng.choice(KINDS)
    size = size if size is not None else rng.randint(1, 4)
    full = mbt.HEALTH_BASE[kind] + mbt.HEALTH_SLOPE[kind] * size
    if health is None:
        health = full if rng.random() < 0.8 else rng.randint(1, full)
    if fruits is None:
        fruits = rng.randint(0, 3) if size == 4 else 0
    if cd is None:
        cd = rng.randint(0, mbt.COOLDOWN[kind])
    return [kind, cell[0], cell[1], size, health, fruits, cd]


def _geometry(cls, rng):
    """Class geometry: returns dict(w, h, grid, tents=[A, B],
    forced_plants, meta) or None when the draw is degenerate."""
    forced = []
    meta = {}
    if cls == "choke_corridor":
        w, h = rng.randint(11, 14), rng.randint(4, 8)
        cy = rng.randint(2, h - 2) if h > 4 else 2
        grid = _blank(w, h)
        _carve(grid, [(x, cy) for x in range(1, w - 1)])
        ta = (1, cy - 1)
        _carve(grid, [ta, (2, cy - 1)])          # tent cell + orth door
        if rng.random() < 0.5:
            tb = (w - 2, cy - 1)
            _carve(grid, [tb, (w - 3, cy - 1)])
        else:
            tb = (w - 1, cy)
        # the diagonal ring cell (2, cy) is the single articulation cell of
        # every east->door banking route (the round-5 killer geometry)
        if rng.random() < 0.6:
            forced.append(_mk_plant(
                rng, (2, cy), kind="BANANA", size=4,
                fruits=rng.choice([0, 0, 1]), cd=rng.randint(30, 60),
                health=6))
        meta["second_worker_bias"] = 0.75
        meta["full_wood_bias"] = 0.6
        meta["plant_range"] = (0, 2)
    elif cls == "orchard_eligible":
        w, h = 14, rng.randint(4, 8)
        ay = rng.randint(1, h - 2)
        grid = _blank(w, h)
        _carve(grid, [(x, y) for x in range(w) for y in range(h)])
        ta, tb = (0, ay), (13, rng.randint(1, h - 2))
        if ay - 1 >= 0:
            grid[ay - 1][0] = "#"
            grid[ay - 1][1] = "~"               # water on the door's north
        else:
            return None
        for _ in range(rng.randint(0, 6)):      # obstacles never shorten
            grid[rng.randint(0, h - 1)][rng.randint(4, 9)] = "#"
        used = set()
        for _ in range(rng.randint(1, 3)):      # far naturals: median >= 8
            c = (rng.randint(9, 12), rng.randint(0, h - 1))
            if c in used or c in (ta, tb) or grid[c[1]][c[0]] != ".":
                continue
            used.add(c)
            forced.append(_mk_plant(rng, c, size=4,
                                    fruits=rng.randint(1, 3)))
        if not forced:
            return None
        meta["plant_range"] = (0, 0)
        meta["extra_plant_min_x"] = 9
    else:
        w, h = rng.randint(10, 14), rng.randint(5, 8)
        grid = _blank(w, h)
        _carve(grid, [(x, y) for x in range(w) for y in range(h)])
        ta = (rng.randint(1, 2), rng.randint(1, h - 2))
        tb = (w - 1 - rng.randint(1, 2), rng.randint(1, h - 2))
        keep = {ta, tb} | set(_orth_neighbors(ta)) | set(_orth_neighbors(tb))
        for _ in range(rng.randint(0, (w * h) // 10)):
            c = (rng.randrange(w), rng.randrange(h))
            if c not in keep:
                grid[c[1]][c[0]] = "#"
        if cls == "single_door_tent" or cls == "multi_door":
            doors = [c for c in _orth_neighbors(ta) if _in(w, h, c)]
            n_keep = 1 if cls == "single_door_tent" else rng.randint(2, 4)
            kept = doors[:0]
            order = sorted(doors)
            rng.shuffle(order)
            kept = set(order[:n_keep])
            for c in doors:
                if c not in kept:
                    grid[c[1]][c[0]] = "#"
            for dx, dy in DIAG:                 # tent pocket walls
                c = (ta[0] + dx, ta[1] + dy)
                if _in(w, h, c) and c not in kept and rng.random() < 0.7:
                    grid[c[1]][c[0]] = "#"
            meta["plant_range"] = (1, 4)
        elif cls == "water_diagonal":
            placed = False
            for dx, dy in rng.sample(DIAG, 4):
                d = (ta[0] + dx, ta[1] + dy)
                wc = ((ta[0] + 2 * dx, ta[1] + dy) if rng.random() < 0.5
                      else (ta[0] + dx, ta[1] + 2 * dy))
                if not (_in(w, h, d) and _in(w, h, wc)):
                    continue
                if grid[d[1]][d[0]] != "." or grid[wc[1]][wc[0]] != ".":
                    continue
                # keep water OFF door-adjacency: never orchard-eligible by
                # this cell (banana-eligible wet diagonal instead)
                if any(n in _orth_neighbors(ta) for n in _orth_neighbors(wc)):
                    continue
                grid[wc[1]][wc[0]] = "~"
                placed = True
                break
            if not placed:
                return None
            meta["plant_range"] = (1, 4)
            meta["banana_bank_min"] = 1
        elif cls == "forest_dense":
            meta["plant_range"] = (8, 14)
        elif cls == "forest_sparse":
            meta["plant_range"] = (1, 3)
        else:                                   # open_field
            meta["plant_range"] = (0, 5)
    # iron present/absent (all classes): '+' replaces a wall or field cell
    if rng.random() < 0.3:
        for _ in range(rng.randint(1, 2)):
            c = (rng.randrange(w), rng.randrange(h))
            if c not in (ta, tb) and grid[c[1]][c[0]] in "#.":
                grid[c[1]][c[0]] = "+"
    grid[ta[1]][ta[0]] = "."
    grid[tb[1]][tb[0]] = "."
    return {"w": w, "h": h, "grid": grid, "tents": [list(ta), list(tb)],
            "forced_plants": forced, "meta": meta}


def _roster_template(cls, profile, rng, meta):
    second = None
    if rng.random() < meta.get("second_worker_bias", 0.5):
        second = {
            "speed": rng.choice([1, 1, 1, 2]),
            "cap": rng.choice([1, 2, 2, 3]),
            "harvest": rng.choice([0, 1, 1]),
            "chop": rng.choice([0, 1, 1]),
            "full_wood": rng.random() < meta.get("full_wood_bias", 0.25),
            "frac": round(rng.random(), 4),
        }
    opp = []
    n_opp = 1 if profile == "idle" else rng.choice([1, 1, 2])
    for _ in range(n_opp):
        if profile == "harvester":
            opp.append({"speed": rng.choice([1, 2]), "cap": rng.choice([2, 3]),
                        "harvest": 1, "chop": 0})
        elif profile == "chopper_aggressor":
            opp.append({"speed": 1, "cap": rng.choice([2, 3]),
                        "harvest": 0, "chop": rng.choice([1, 2])})
        else:
            opp.append({"speed": 1, "cap": 2, "harvest": 0, "chop": 0})
    return {"second": second, "opp": opp}


def _inventory(cls, rng, meta):
    inv = [0] * 6
    inv[3] = max(meta.get("banana_bank_min", 0),
                 rng.choice([0, 1, 1, 2]))
    for slot in (0, 1, 2):
        if rng.random() < 0.15:
            inv[slot] = 1
    return inv


def build_skeleton(map_index, cls, profile, cfg):
    """Deterministic skeleton for map #map_index: geometry + plants +
    inventory + roster template. Regenerates on invalid draws by advancing
    the seed stream (attempt counter)."""
    seeds = cfg["seeds"]
    base = seeds[map_index % len(seeds)]
    for attempt in range(cfg["max_generation_attempts"]):
        rng = random.Random(base * 1_000_003 + map_index * 8191
                            + attempt * 7919)
        geo = _geometry(cls, rng)
        if geo is None:
            continue
        rows_plain = _rows(geo["grid"])
        parsed = sh.parse_rows(tuple(rows_plain))
        walk = parsed["walkable"]
        ta = tuple(geo["tents"][0])
        tb = tuple(geo["tents"][1])
        doors_a = sorted(c for c in _orth_neighbors(ta) if c in walk)
        doors_b = sorted(c for c in _orth_neighbors(tb) if c in walk)
        if not doors_a or not doors_b:
            continue
        reach = sh.bfs(walk - {ta, tb}, doors_a)
        if doors_b[0] not in reach:
            continue
        plants = list(geo["forced_plants"])
        taken = {(p[1], p[2]) for p in plants}
        if any(c not in reach and c not in (ta, tb) for c in taken):
            continue
        lo, hi = geo["meta"].get("plant_range", (0, 4))
        min_x = geo["meta"].get("extra_plant_min_x", 0)
        candidates = sorted(c for c in reach
                            if c not in taken and c not in (ta, tb)
                            and c[0] >= min_x)
        n_extra = min(rng.randint(lo, hi), len(candidates))
        for c in (rng.sample(candidates, n_extra) if n_extra else []):
            plants.append(_mk_plant(rng, c))
            taken.add(c)
        skel = {
            "id": "m%03d" % map_index,
            "class": cls,
            "profile": profile,
            "seed": base,
            "attempt": attempt,
            "rows_plain": rows_plain,
            "tents": [list(ta), list(tb)],
            "plants": sorted(plants, key=lambda p: (p[1], p[2])),
            "inventory": _inventory(cls, rng, geo["meta"]),
            "roster": _roster_template(cls, profile, rng, geo["meta"]),
        }
        specs = [materialize(skel, 0), materialize(skel, 1)]
        if any(s is None for s in specs):
            continue
        if cls == "orchard_eligible" and not specs[0]["orchard_eligible"]:
            continue
        return skel, specs
    raise PanelError(
        "map %d (%s): no valid geometry within %d attempts"
        % (map_index, cls, cfg["max_generation_attempts"]))


def materialize(skel, seat):
    """Pure seat-variant instantiation: '0' at the seat's tent, own units
    placed relative to it, opponent units at the other tent's doors."""
    ta = tuple(skel["tents"][seat])
    tb = tuple(skel["tents"][1 - seat])
    rows = []
    for y, row in enumerate(skel["rows_plain"]):
        chars = list(row)
        if y == ta[1]:
            chars[ta[0]] = "0"
        if y == tb[1]:
            chars[tb[0]] = "1"
        rows.append("".join(chars))
    geo = sh.parse_rows(tuple(rows))
    walk = geo["walkable"]
    own_doors = sorted(c for c in _orth_neighbors(ta) if c in walk)
    opp_doors = sorted(c for c in _orth_neighbors(tb) if c in walk)
    if not own_doors or not opp_doors:
        return None
    reach = sh.bfs(walk, own_doors)
    if opp_doors[0] not in reach:
        return None
    if any((p[1], p[2]) not in reach for p in skel["plants"]):
        return None
    units = [[0, 0, own_doors[0][0], own_doors[0][1], 1, 2, 1, 1]
             + [0] * 6]
    second = skel["roster"]["second"]
    if second is not None:
        ordered = sorted(reach.items(), key=lambda kv: (kv[1], kv[0]))
        cell = ordered[int(second["frac"] * (len(ordered) - 1))][0]
        carry = [0] * 6
        if second["full_wood"]:
            carry[WOOD] = second["cap"]
        units.append([2, 0, cell[0], cell[1], second["speed"],
                      second["cap"], second["harvest"], second["chop"]]
                     + carry)
    for i, opp in enumerate(skel["roster"]["opp"]):
        door = opp_doors[min(i, len(opp_doors) - 1)]
        units.append([5 + i, 1, door[0], door[1], opp["speed"], opp["cap"],
                      opp["harvest"], opp["chop"]] + [0] * 6)
    return {
        "map_id": skel["id"],
        "seat": seat,
        "class": skel["class"],
        "profile": skel["profile"],
        "seed": skel["seed"],
        "attempt": skel["attempt"],
        "rows": rows,
        "plants": [list(p) for p in skel["plants"]],
        "inventory": list(skel["inventory"]),
        "units": units,
        "orchard_eligible": orchard_eligible_view(rows, skel["plants"]),
    }


# ---------------------------------------------------------------------------
# Referee adapter (thin adapter over the make_banana_traces referee core)
# ---------------------------------------------------------------------------

class FuzzReferee(mbt.Referee):
    """make_banana_traces.Referee bound to generated geometry.

    The inherited command application (MOVE/HARVEST/CHOP/PLANT/PICK/DROP)
    and growth are reused verbatim; this adapter only (a) supplies the
    instance walkable set / tent for the module-global lookups the original
    referee performs (bound before every apply), (b) evaluates water
    adjacency on the instance map so wet-cell cooldown boosts are real, and
    (c) steps the deterministic opponent policy after own commands and
    before growth, exactly like DynamicOpponentReferee."""

    def __init__(self, rows, inventory, plants, units, profile):
        super().__init__(list(inventory), plants, units)
        self.rows = tuple(rows)
        geo = sh.parse_rows(self.rows)
        self.walk = set(geo["walkable"])
        self.tent = geo["shacks"][0]
        self.opp_tent = geo["shacks"][1]
        self.waters = set(geo["water"])
        self.profile = profile
        self.opp_doors = sorted(c for c in _orth_neighbors(self.opp_tent)
                                if c in self.walk)

    def map_header(self):
        return ("%d %d\n" % (len(self.rows[0]), len(self.rows))
                + "\n".join(self.rows) + "\n")

    def near_water(self, cell):
        return any(n in self.waters for n in _orth_neighbors(cell))

    def _nbrs(self, cell):
        return [n for n in _orth_neighbors(cell) if n in self.walk]

    def _bfs_from(self, sources):
        from collections import deque
        dist = {}
        queue = deque()
        for c in sources:
            if c not in dist:
                dist[c] = 0
                queue.append(c)
        while queue:
            cell = queue.popleft()
            for n in self._nbrs(cell):
                if n not in dist:
                    dist[n] = dist[cell] + 1
                    queue.append(n)
        return dist

    def step_toward(self, current, target, speed):
        """Same nav::next_cell mirror as Referee.step_toward, evaluated on
        the instance walkable set (pattern of mbt.CustomMapReferee)."""
        if target == current:
            return current
        dist = self._bfs_from([target])
        if current not in dist:
            return current
        if dist[current] <= speed:
            return target
        cell = current
        for _ in range(speed):
            options = [n for n in self._nbrs(cell) if n in dist]
            if not options:
                break
            cell = min(options, key=lambda n: (dist[n], n))
        return cell

    def _bind(self):
        # The inherited apply() resolves PICK/DROP door adjacency against
        # the module-level TENT and movement against WALKABLE; bind them to
        # this instance's geometry for the duration of the call.
        mbt.TENT = self.tent
        mbt.WALKABLE = self.walk

    def apply(self, command_line):
        saved = (mbt.TENT, mbt.WALKABLE)
        self._bind()
        try:
            mbt.Referee.apply(self, command_line)
            OPP_POLICIES[self.profile](self)
        finally:
            mbt.TENT, mbt.WALKABLE = saved


def _opp_ids(ref):
    return sorted(uid for uid, u in ref.units.items() if u["player"] == 1)


def _opp_seek_and_act(ref, want_fruits, act):
    """Shared deterministic opponent loop: full units bank at the opponent
    tent; otherwise walk to the nearest qualifying plant (BFS from the
    unit, ties by cell) and act on it."""
    for uid in _opp_ids(ref):
        u = ref.units[uid]
        free = u["cap"] - sum(u["carry"])
        if free <= 0:
            x, y = u["cell"]
            if abs(x - ref.opp_tent[0]) + abs(y - ref.opp_tent[1]) == 1:
                for i in range(6):
                    ref.opp_inv[i] += u["carry"][i]
                    u["carry"][i] = 0
                continue
            if not ref.opp_doors:
                continue
            dmap = ref._bfs_from([u["cell"]])
            door = min(ref.opp_doors, key=lambda d: (dmap.get(d, BIG), d))
            u["cell"] = ref.step_toward(u["cell"], door, u["speed"])
            continue
        targets = sorted(
            c for c, p in ref.plants.items()
            if (p["fruits"] > 0 if want_fruits else True))
        if not targets:
            continue
        dmap = ref._bfs_from([u["cell"]])
        targets = [c for c in targets if c in dmap]
        if not targets:
            continue
        tgt = min(targets, key=lambda c: (dmap[c], c))
        if u["cell"] != tgt:
            u["cell"] = ref.step_toward(u["cell"], tgt, u["speed"])
        if u["cell"] == tgt:
            plant = ref.plants.get(tgt)
            if plant is not None:
                act(ref, u, tgt, plant)


def _act_harvest(ref, u, cell, plant):
    free = u["cap"] - sum(u["carry"])
    if plant["fruits"] > 0 and u["harvest"] > 0 and free > 0:
        plant["fruits"] -= 1
        u["carry"][mbt.ITEM[plant["kind"]]] += 1


def _act_chop(ref, u, cell, plant):
    if u["chop"] > 0:
        plant["health"] -= u["chop"]
        if plant["health"] <= 0:
            free = u["cap"] - sum(u["carry"])
            u["carry"][WOOD] += min(plant["size"], max(free, 0))
            del ref.plants[cell]


OPP_POLICIES = {
    "idle": lambda ref: None,
    "harvester": lambda ref: _opp_seek_and_act(ref, True, _act_harvest),
    "chopper_aggressor": lambda ref: _opp_seek_and_act(ref, False, _act_chop),
}


def make_referee(spec) -> FuzzReferee:
    plants = {}
    for k, x, y, size, health, fruits, cd in spec["plants"]:
        plants[(x, y)] = {"kind": k, "size": size, "health": health,
                          "fruits": fruits, "cd": cd}
    units = {}
    for row in spec["units"]:
        uid, player, x, y, speed, cap, harvest, chop = row[:8]
        units[uid] = {"player": player, "cell": (x, y), "speed": speed,
                      "cap": cap, "harvest": harvest, "chop": chop,
                      "carry": list(row[8:14])}
    return FuzzReferee(spec["rows"], spec["inventory"], plants, units,
                       spec["profile"])


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def progress_turns(tr) -> set:
    """Turns t (1..T-1) whose S_t -> S_{t+1} transition changes the own
    inventory or any own unit's cargo (P4 'score credit or cargo change')."""
    out = set()
    for t in range(1, tr.T):
        s0, s1 = tr.state(t), tr.state(t + 1)
        if s0.inventories[0] != s1.inventories[0]:
            out.add(t)
            continue
        if ({u.id: tuple(u.carry) for u in s0.own_units()}
                != {u.id: tuple(u.carry) for u in s1.own_units()}):
            out.add(t)
    return out


def stall_windows(prog: set, T: int, window: int) -> list:
    """Maximal runs of >= window consecutive progress-free turns in
    1..T-1."""
    runs = []
    start = None
    for t in range(1, T):
        if t in prog:
            if start is not None and t - start >= window:
                runs.append((start, t - 1))
            start = None
        elif start is None:
            start = t
    if start is not None and T - start >= window:
        runs.append((start, T - 1))
    return runs


def eval_p1(tr_c, tr_p, parent_cmds, parent_d1_failed: bool):
    """RAW detector gate (owner ruling 2026-08-06): every FAIL among
    D-1..D-9 blocks the candidate, inherited-from-parent or not, on every
    map.  Both former parent-comparison exemptions are REMOVED:
      * the D-9 parent-differential gate (round-6 ROOT-A) -- a D-9 episode
        the parent reproduced byte-for-byte used to be downgraded to a
        report-tier flag; under raw it blocks;
      * the D-1 inherited-report-only downgrade -- a D-1 episode on a map
        where the parent also oscillates used to be report-only; under raw
        it blocks.
    tr_p and parent_d1_failed are retained only for signature/diagnostic
    parity and never exempt an episode.  parent_cmds is still forwarded to
    td.run_all because detect_d9's base semantics consume it (the detector
    itself is unmodified).  The returned `inherited`/`d9_dropped` are always
    empty/0 now -- kept so the caller's shape is unchanged."""
    results = td.run_all(tr_c, parent_cmds)
    violations = [r for r in results if r["verdict"] == "FAIL"]
    return results, violations, [], 0


def eval_p2(tr_c):
    rep = rt.r5_two_worker_full_cargo_banking(tr_c)
    alternations = [v for v in rep["violations"] if "alternation" in v["why"]]
    horizon = [v for v in rep["violations"]
               if "banking horizon" in v["why"]]
    return rep, alternations, horizon


def eval_p3(orchard_eligible: bool, commands_c: str, commands_p: str):
    if not orchard_eligible or commands_c == commands_p:
        return []
    lc, lp = commands_c.splitlines(), commands_p.splitlines()
    for i in range(max(len(lc), len(lp))):
        a = lc[i] if i < len(lc) else "<absent>"
        b = lp[i] if i < len(lp) else "<absent>"
        if a != b:
            return [{"first_divergence_turn": i + 1,
                     "candidate": a, "parent": b}]
    return [{"first_divergence_turn": None,
             "candidate": "<trailing bytes differ>", "parent": ""}]


def eval_p4(tr_c, tr_p, window: int):
    """RAW liveness (owner ruling 2026-08-06): the candidate must make
    progress (own inventory or own-unit cargo change) in every rolling
    window; EVERY stall window blocks.  The former 'unless the parent also
    makes no progress in the same window' exemption is REMOVED -- it was the
    property's ONLY exemption and it was purely parent-based (no absolute
    all-WAIT terminal state was ever recognised), so nothing parent-free
    survives.  tr_p is accepted for signature/diagnostic parity but is NOT
    consulted for blocking."""
    pc = progress_turns(tr_c)
    violations = []
    for (a, b) in stall_windows(pc, tr_c.T, window):
        violations.append({
            "window_start": a, "window_end": b,
            "why": "candidate makes no own-inventory/own-cargo progress over "
                   "turns %d-%d (>= %d turns) [RAW liveness: every stall "
                   "window blocks, no parent exemption]" % (a, b, window)})
    return violations


# ---------------------------------------------------------------------------
# Per-game job
# ---------------------------------------------------------------------------

def run_pair(job):
    """One (map, seat): candidate + parent closed-loop games on the
    identical spec, then all properties. Pure function of the job dict."""
    spec = job["spec"]
    turns = job["turns"]
    row = {
        "map_id": spec["map_id"], "seat": spec["seat"],
        "class": spec["class"], "profile": spec["profile"],
        "seed": spec["seed"], "attempt": spec["attempt"],
        "orchard_eligible": spec["orchard_eligible"],
        "violations": [], "flags": [],
    }
    try:
        ref_c = make_referee(spec)
        t_c, c_c = rt.run_binary_custom(Path(job["candidate"]), ref_c, turns)
    except (RuntimeError, OSError) as exc:
        row["violations"].append({
            "property": "P0", "detail": "candidate crashed / closed stdout "
            "early: %s" % exc})
        row.update({"block": True, "banana_active": False, "turns": 0,
                    "detector_counts": {}, "candidate": None,
                    "parent": None, "artifacts": {}})
        return row
    try:
        ref_p = make_referee(spec)
        t_p, c_p = rt.run_binary_custom(Path(job["parent"]), ref_p, turns)
    except (RuntimeError, OSError) as exc:
        raise PanelError("parent crashed on %s seat %d: %s"
                         % (spec["map_id"], spec["seat"], exc))
    tr_c = td.build_trace(t_c, c_c)
    tr_p = td.build_trace(t_p, c_p)
    parent_cmds = td.CommandParser().parse(c_p)
    parent_d1 = td.detect_d1(tr_p)

    detectors, p1_viol, inherited, d9_dropped = eval_p1(
        tr_c, tr_p, parent_cmds, parent_d1["verdict"] == "FAIL")
    _, p2_alt, p2_horizon = eval_p2(tr_c)
    p3_viol = eval_p3(spec["orchard_eligible"], c_c, c_p)
    p4_viol = eval_p4(tr_c, tr_p, job["liveness_window"])

    margin_c = score(ref_c.inv) - score(ref_c.opp_inv)
    margin_p = score(ref_p.inv) - score(ref_p.opp_inv)
    banana_active = "BANANA" in c_c.upper()

    for r in p1_viol:
        row["violations"].append({
            "property": "P1", "detector": r["detector"],
            "count": r["count"], "episodes": r["episodes"][:5]})
    for v in p2_alt:
        row["violations"].append({"property": "P2", "detail": v["why"],
                                  "unit": v["unit"]})
    for v in p3_viol:
        row["violations"].append({"property": "P3", "detail": v})
    for v in p4_viol:
        row["violations"].append({"property": "P4", "detail": v})

    # RAW gate (owner ruling 2026-08-06): no inherited-parent-D1 /
    # inherited-parent-D9 downgrades exist any more -- eval_p1 returns those
    # channels empty and every detector episode is already a blocking P1
    # violation above.
    assert not inherited and not d9_dropped
    for v in p2_horizon:
        row["flags"].append({"flag": "r5-horizon", "detail": v["why"],
                             "unit": v["unit"]})
    if banana_active and margin_c < margin_p - job["margin_threshold"]:
        row["flags"].append({
            "flag": "margin-collapse",
            "detail": "banana-activated map: candidate margin %d < parent "
                      "margin %d - %d" % (margin_c, margin_p,
                                          job["margin_threshold"])})

    row.update({
        "turns": tr_c.T,
        "banana_active": banana_active,
        "candidate": {"inventory": list(ref_c.inv),
                      "opp_inventory": list(ref_c.opp_inv),
                      "score": score(ref_c.inv),
                      "opp_score": score(ref_c.opp_inv),
                      "margin": margin_c},
        "parent": {"inventory": list(ref_p.inv),
                   "opp_inventory": list(ref_p.opp_inv),
                   "score": score(ref_p.inv),
                   "opp_score": score(ref_p.opp_inv),
                   "margin": margin_p},
        "detector_counts": {r["detector"]: r["count"] for r in detectors},
        "block": bool(row["violations"]),
        "artifacts": {
            "candidate_transcript": t_c, "candidate_commands": c_c,
            "parent_transcript": t_p, "parent_commands": c_p,
            "detectors": detectors,
        },
    })
    return row


# ---------------------------------------------------------------------------
# Panel driver
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PanelError("cannot load config %s: %s" % (path, exc))
    cfg = dict(DEFAULTS)
    cfg.update(raw)
    cfg["config_dir"] = path.resolve().parent
    if not cfg.get("seeds"):
        raise PanelError("config must declare a non-empty seed list")
    for key in ("candidate", "parent"):
        if key not in cfg or "source" not in cfg[key]:
            raise PanelError("config must declare %s.source" % key)
    unknown = set(cfg["class_mix"]) - set(MAP_CLASSES)
    if unknown:
        raise PanelError("unknown map classes in class_mix: %s"
                         % sorted(unknown))
    unknown = set(cfg["opponent_mix"]) - set(OPP_PROFILES)
    if unknown:
        raise PanelError("unknown opponent profiles: %s" % sorted(unknown))
    return cfg


def resolve(cfg, path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (cfg["config_dir"] / p).resolve()


def compile_bot(cfg, key: str, workdir: Path) -> Path:
    entry = cfg[key]
    source = resolve(cfg, entry["source"])
    if not source.exists():
        raise PanelError("%s source missing: %s" % (key, source))
    digest = sha256_path(source)
    declared = entry.get("sha256")
    if declared and not digest.startswith(declared.rstrip(".")):
        raise PanelError(
            "%s sha256 mismatch: declared %s, actual %s (%s)"
            % (key, declared, digest, source))
    cache_dir = cfg.get("bin_cache_dir")
    if cache_dir:
        cache = resolve(cfg, cache_dir)
        cache.mkdir(parents=True, exist_ok=True)
        out = cache / ("bot-%s" % digest[:16])
        if not out.exists():
            sh.compile_text(source.read_text(), out,
                            entry.get("crate", "fuzz_bot_" + key))
        return out
    out = workdir / ("bot-%s" % digest[:16])
    if not out.exists():
        sh.compile_text(source.read_text(), out,
                        entry.get("crate", "fuzz_bot_" + key))
    return out


def build_jobs(cfg, candidate: Path, parent: Path):
    n = int(cfg["maps"])
    classes = schedule(cfg["class_mix"], n)
    profiles = schedule(cfg["opponent_mix"], n)
    jobs = []
    for i in range(n):
        skel, specs = build_skeleton(i, classes[i], profiles[i], cfg)
        for spec in specs:
            jobs.append({
                "spec": spec,
                "turns": int(cfg["turns"]),
                "liveness_window": int(cfg["liveness_window"]),
                "margin_threshold": int(cfg["margin_collapse_threshold"]),
                "candidate": str(candidate),
                "parent": str(parent),
            })
    return jobs


def save_failure(base: Path, row: dict):
    d = base / ("%s-s%d" % (row["map_id"], row["seat"]))
    d.mkdir(parents=True, exist_ok=True)
    art = row.get("artifacts", {})
    spec = dict(row)
    spec.pop("artifacts", None)
    (d / "properties.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")
    for name, key in (("candidate-transcript.txt", "candidate_transcript"),
                      ("candidate-commands.txt", "candidate_commands"),
                      ("parent-transcript.txt", "parent_transcript"),
                      ("parent-commands.txt", "parent_commands")):
        if key in art:
            (d / name).write_text(art[key])
    if "detectors" in art:
        (d / "detectors.json").write_text(
            json.dumps(art["detectors"], indent=1, sort_keys=True) + "\n")


def write_games_archive(cfg, rows):
    games_dir = cfg.get("games_dir")
    if not games_dir:
        return None
    out_dir = resolve(cfg, games_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "games.jsonl.gz"
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return out


def summarize(cfg, rows, wall_time):
    stats = {
        "maps": int(cfg["maps"]),
        "games": len(rows),
        "turns_per_game": int(cfg["turns"]),
        "by_class": {},
        "by_profile": {},
        "banana_activated_games": sum(1 for r in rows if r["banana_active"]),
        "orchard_eligible_games": sum(1 for r in rows
                                      if r["orchard_eligible"]),
        "orchard_inertness_checks_passed": sum(
            1 for r in rows if r["orchard_eligible"]
            and not any(v["property"] == "P3" for v in r["violations"])),
        "blocking_games": sum(1 for r in rows if r["block"]),
        "flagged_games": sum(1 for r in rows if r["flags"]),
        "wall_time_seconds": round(wall_time, 2),
    }
    for r in rows:
        stats["by_class"][r["class"]] = stats["by_class"].get(
            r["class"], 0) + 1
        stats["by_profile"][r["profile"]] = stats["by_profile"].get(
            r["profile"], 0) + 1
    return stats


def write_report(path: Path, cfg, rows, stats, verdict):
    lines = []
    lines.append("# fuzz panel report - %s" % cfg.get("task", "<unnamed>"))
    lines.append("")
    lines.append("- candidate: `%s` (sha256 %s)"
                 % (cfg["candidate"]["source"],
                    cfg["candidate"].get("sha256", "?")))
    lines.append("- parent: `%s` (sha256 %s)"
                 % (cfg["parent"]["source"], cfg["parent"].get("sha256", "?")))
    lines.append("- seeds: %s" % cfg["seeds"])
    lines.append("- maps: %d (x2 seats = %d candidate games + %d parent "
                 "games), %d turns each"
                 % (stats["maps"], stats["games"], stats["games"],
                    stats["turns_per_game"]))
    lines.append("- wall time: %.1f s" % stats["wall_time_seconds"])
    lines.append("")
    lines.append("## Verdict: %s" % verdict)
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    for k in ("games", "banana_activated_games", "orchard_eligible_games",
              "orchard_inertness_checks_passed", "blocking_games",
              "flagged_games"):
        lines.append("| %s | %s |" % (k, stats[k]))
    lines.append("")
    lines.append("| class | games |")
    lines.append("|---|---|")
    for k, v in sorted(stats["by_class"].items()):
        lines.append("| %s | %d |" % (k, v))
    lines.append("")
    lines.append("| opponent profile | games |")
    lines.append("|---|---|")
    for k, v in sorted(stats["by_profile"].items()):
        lines.append("| %s | %d |" % (k, v))
    lines.append("")
    blocking = [r for r in rows if r["block"]]
    if blocking:
        lines.append("## Blocking violations")
        lines.append("")
        for r in blocking:
            lines.append("### %s seat %d (%s, %s, seed %d)"
                         % (r["map_id"], r["seat"], r["class"], r["profile"],
                            r["seed"]))
            lines.append("")
            for v in r["violations"]:
                lines.append("- **%s**: %s" % (
                    v["property"],
                    json.dumps({k: vv for k, vv in v.items()
                                if k != "property"}, sort_keys=True)[:600]))
            lines.append("")
    flagged = [r for r in rows if r["flags"]]
    if flagged:
        lines.append("## Report-tier flags (non-blocking)")
        lines.append("")
        for r in flagged:
            for f in r["flags"]:
                lines.append("- %s seat %d [%s]: %s"
                             % (r["map_id"], r["seat"], f["flag"],
                                f["detail"]))
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**VERDICT: %s**" % verdict)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def run_panel(cfg, report_path: Path, json_path: Path | None,
              save_failures: Path | None) -> int:
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="fuzz-panel-") as workdir:
        candidate = compile_bot(cfg, "candidate", Path(workdir))
        parent = compile_bot(cfg, "parent", Path(workdir))
        jobs = build_jobs(cfg, candidate, parent)
        procs = int(cfg["processes"]) or min(
            8, multiprocessing.cpu_count())
        if procs > 1 and len(jobs) > 1:
            with multiprocessing.get_context("fork").Pool(procs) as pool:
                rows = pool.map(run_pair, jobs)
        else:
            rows = [run_pair(job) for job in jobs]
    rows.sort(key=lambda r: (r["map_id"], r["seat"]))
    wall_time = time.monotonic() - started

    if save_failures is not None:
        for row in rows:
            if row["block"] or row["flags"]:
                save_failure(save_failures, row)
    write_games_archive(cfg, rows)

    stats = summarize(cfg, rows, wall_time)
    verdict = "BLOCK" if any(r["block"] for r in rows) else "CLEAR"
    write_report(report_path, cfg, rows, stats, verdict)
    if json_path is not None:
        slim = []
        for row in rows:
            r = dict(row)
            r.pop("artifacts", None)
            slim.append(r)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(
            {"task": cfg.get("task"), "verdict": verdict, "stats": stats,
             "games": slim}, indent=1, sort_keys=True) + "\n")
    print("fuzz_panel: %s (%d games, %d blocking, %d flagged, %.1f s; "
          "report: %s)"
          % (verdict, stats["games"], stats["blocking_games"],
             stats["flagged_games"], wall_time, report_path))
    return EXIT_CLEAR if verdict == "CLEAR" else EXIT_BLOCK


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fuzz_panel",
        description="randomized closed-loop property panel (final gate)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json", dest="json_out")
    parser.add_argument("--save-failures", dest="save_failures")
    args = parser.parse_args(argv)
    try:
        cfg = load_config(Path(args.config))
        return run_panel(
            cfg, Path(args.report),
            Path(args.json_out) if args.json_out else None,
            Path(args.save_failures) if args.save_failures else None)
    except PanelError as exc:
        print("fuzz_panel: tool/config error: %s" % exc, file=sys.stderr)
        return EXIT_ERROR
    except Exception as exc:                        # noqa: BLE001
        print("fuzz_panel: unexpected error: %r" % exc, file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
