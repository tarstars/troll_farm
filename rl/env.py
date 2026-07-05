"""Troll Farm RL environment (framework-agnostic, numpy-only core).

Wraps the EXISTING reference sim (`sim/engine.py`) — the code the Rust engine
(`rust/src/game/engine.rs`) was ported from and which `tests/test_rust_parity.py`
keeps byte-parity with. So the dynamics here match `engine.rs` by construction;
there is no reimplementation to drift.

We control player 0; a fixed scripted opponent (default `sim.boss.boss_decide`)
plays player 1. The env exposes a Gym-style API:

    obs = env.reset(seed=...)                       # -> np.float32[obs_dim]
    obs, reward, terminated, truncated, info = env.step(action)

`action` is a length-(K+1) integer vector (a MultiDiscrete):
    action[0..K-1]  per-troll MACRO in {0..NUM_MACROS-1}
    action[K]       TRAIN head in {0..NUM_TRAIN-1}  (0 = don't train)

MACROS are high-level intents the env compiles into concrete engine commands
(pathing/targeting handled here) so the policy needn't emit raw 128-cell MOVE
targets:
    0 WAIT   1 CHOP-nearest-tree   2 HARVEST-nearest-fruited-tree
    3 BANK (go to shack, DROP)     4 MINE-nearest-iron    5 PLANT/seed a banana

REWARD (per turn):
    r = Δ(my_score - opp_score) + carry_coef * Δ(value of my carried fruit+wood)
    scaled by 1/reward_scale.
The margin term telescopes to the final win margin; the carry term is a small
potential-style shaping that densifies the early "gather wood" signal.
"""

import copy
import os
import sys

import numpy as np

# Make the repo root importable (sim/, bot/) regardless of caller cwd.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from sim.mapgen import generate_bronze
from sim.engine import step as engine_step
from bot.main import training_cost
from rl.opponents import get_opponent

# item indices (mirror engine.rs constants)
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = 0, 1, 2, 3, 4, 5
WOOD_POINTS = 4

# fixed map size produced by sim.mapgen.generate_bronze
MAP_W, MAP_H = 16, 8
# number of own-troll slots we model (in obs and in the action vector)
K = 4

# macro action set
NUM_MACROS = 6
M_WAIT, M_CHOP, M_HARVEST, M_BANK, M_MINE, M_PLANT = range(NUM_MACROS)

# TRAIN head: index 0 = no train; others are (ms, cc, hp, chop) specs.
# cc2 chopper is the proven strong early unit; cc3 chopper and a balanced troll
# give the policy richer economic options.
TRAIN_SPECS = [None, (2, 2, 0, 2), (2, 3, 0, 2), (2, 2, 2, 2)]
NUM_TRAIN = len(TRAIN_SPECS)

_ACTION_NVEC = np.array([NUM_MACROS] * K + [NUM_TRAIN], dtype=np.int64)


# ── small map generation cache (templates are deep-copied per episode) ────────
_TEMPLATE_CACHE = {}


def _template(seed):
    g = _TEMPLATE_CACHE.get(seed)
    if g is None:
        g = generate_bronze(seed)
        _TEMPLATE_CACHE[seed] = g
    return g


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _plant_at(game, cell):
    for p in game.plants:
        if p.pos == cell:
            return p
    return None


def _nearest(items, pos, key=lambda it: it.pos):
    best, bestd = None, 1 << 30
    for it in items:
        d = _manhattan(pos, key(it))
        if d < bestd:
            best, bestd = it, d
    return best, bestd


class TrollFarmEnv:
    """Single-agent env: policy plays player 0 vs a scripted player 1."""

    def __init__(self, opponent="boss", seed_pool=None, max_turns=300,
                 carry_coef=0.5, reward_scale=4.0, seed=0):
        self.opponent_name = opponent
        self.opponent = get_opponent(opponent)
        # seed_pool: None -> a fresh random map every episode; else an iterable of
        # map seeds to sample from (use a small pool for a lower-variance curve).
        self.seed_pool = list(seed_pool) if seed_pool is not None else None
        self.max_turns = max_turns
        self.carry_coef = carry_coef
        self.reward_scale = reward_scale
        self.rng = np.random.RandomState(seed)

        self.action_nvec = _ACTION_NVEC.copy()
        self.num_heads = len(self.action_nvec)
        self.game = None
        self.t = 0
        self.obs_dim = len(self._encode(_template(0)))  # probe length once

    # ── carried-item value (shaping potential) ────────────────────────────────
    def _carry_value(self, player):
        v = 0
        for u in self.game.units:
            if u.player != player:
                continue
            v += u.carry[PLUM] + u.carry[LEMON] + u.carry[APPLE] + u.carry[BANANA]
            v += WOOD_POINTS * u.carry[WOOD]
        return v

    # ── reset ─────────────────────────────────────────────────────────────────
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.RandomState(seed)
        if self.seed_pool is not None:
            map_seed = int(self.rng.choice(self.seed_pool))
        else:
            map_seed = int(self.rng.randint(0, 2**31 - 1))
        self.map_seed = map_seed
        self.game = copy.deepcopy(_template(map_seed))
        self.t = 0
        return self._encode(self.game)

    # ── macro -> concrete command for one troll ───────────────────────────────
    def _macro_cmd(self, game, u, m):
        if m == M_WAIT:
            return None

        if m == M_CHOP:
            if u.chop == 0 or not game.plants:
                return None
            t, _ = _nearest(game.plants, u.pos)
            if u.pos == t.pos:
                return f"CHOP {u.id}"
            return f"MOVE {u.id} {t.x} {t.y}"

        if m == M_HARVEST:
            if u.hp == 0:
                return None
            fruited = [p for p in game.plants if p.fruits > 0]
            if not fruited:
                return None
            t, _ = _nearest(fruited, u.pos)
            if u.pos == t.pos and u.free > 0:
                return f"HARVEST {u.id}"
            return f"MOVE {u.id} {t.x} {t.y}"

        if m == M_BANK:
            sx, sy = game.shacks[0]
            if _manhattan(u.pos, (sx, sy)) <= 1:
                return f"DROP {u.id}"
            return f"MOVE {u.id} {sx} {sy}"

        if m == M_MINE:
            if u.chop == 0 or not game.iron:
                return None
            if any(_manhattan(u.pos, c) == 1 for c in game.iron):
                return f"MINE {u.id}"
            t, _ = _nearest(list(game.iron), u.pos, key=lambda c: c)
            return f"MOVE {u.id} {t[0]} {t[1]}"

        if m == M_PLANT:
            sx, sy = game.shacks[0]
            near_shack = _manhattan(u.pos, (sx, sy)) <= 1
            if u.carry[BANANA] > 0:
                # plant underfoot if the cell is a free walkable tile
                if u.pos in game.walkable and _plant_at(game, u.pos) is None:
                    return f"PLANT {u.id} BANANA"
                # otherwise walk to the nearest empty walkable tile and plant there
                best, bestd = None, 1 << 30
                for c in game.walkable:
                    if _plant_at(game, c) is None:
                        d = _manhattan(u.pos, c)
                        if d < bestd:
                            best, bestd = c, d
                if best is not None:
                    return f"MOVE {u.id} {best[0]} {best[1]}"
                return None
            # no seed carried: fetch one banana from inventory at the shack
            if game.inventories[0][BANANA] > 0 and u.free > 0:
                if near_shack:
                    return f"PICK {u.id} BANANA"
                return f"MOVE {u.id} {sx} {sy}"
            return None

        return None

    def _compile_commands(self, game, action):
        mine = sorted((u for u in game.units if u.player == 0), key=lambda u: u.id)
        cmds = []
        for slot, u in enumerate(mine[:K]):
            c = self._macro_cmd(game, u, int(action[slot]))
            if c is not None:
                cmds.append(c)
        train_idx = int(action[K])
        # only train while we still have a free controllable slot
        if train_idx > 0 and len(mine) < K:
            ms, cc, hp, chop = TRAIN_SPECS[train_idx]
            cmds.append(f"TRAIN {ms} {cc} {hp} {chop}")
        if not cmds:
            cmds = ["WAIT"]
        return cmds

    # ── step ──────────────────────────────────────────────────────────────────
    def step(self, action):
        game = self.game
        prev_margin = game.scores[0] - game.scores[1]
        prev_carry = self._carry_value(0)

        ours = self._compile_commands(game, action)
        theirs = self.opponent(game, 1)
        engine_step(game, ours, theirs)  # ticks plants, recomputes scores, turn++

        new_margin = game.scores[0] - game.scores[1]
        new_carry = self._carry_value(0)
        reward = (new_margin - prev_margin) + self.carry_coef * (new_carry - prev_carry)
        reward /= self.reward_scale

        self.t += 1
        truncated = self.t >= self.max_turns
        terminated = False
        obs = self._encode(game)
        info = {}
        if truncated:
            info = {
                "my_score": game.scores[0],
                "opp_score": game.scores[1],
                "margin": new_margin,
                "win": float(game.scores[0] > game.scores[1]),
                "my_wood": game.inventories[0][WOOD],
                "opp_wood": game.inventories[1][WOOD],
                "n_trolls": sum(1 for u in game.units if u.player == 0),
                "map_seed": self.map_seed,
            }
        return obs, float(reward), terminated, truncated, info

    # ── observation encoding ──────────────────────────────────────────────────
    def _encode(self, game):
        f = []
        s0, s1 = game.scores
        inv0, inv1 = game.inventories
        mine = sorted((u for u in game.units if u.player == 0), key=lambda u: u.id)
        opp = [u for u in game.units if u.player == 1]
        n_my, n_opp = len(mine), len(opp)

        # ── global ──
        f.append(game.turn / 300.0)
        f.append((s0 - s1) / 100.0)
        f.append(s0 / 100.0)
        f.append(s1 / 100.0)
        f.extend(v / 15.0 for v in inv0)          # 6
        f.extend(v / 15.0 for v in inv1)          # 6
        f.append(n_my / K)
        f.append(n_opp / K)
        # train affordability flags for each real spec
        iron_present = bool(game.iron)
        pay = (0, 1, 2, 3, 4, 5) if iron_present else (0, 1, 2, 3, 5)
        for spec in TRAIN_SPECS[1:]:
            cost = training_cost(n_my, spec)
            f.append(1.0 if all(inv0[i] >= cost[i] for i in pay) else 0.0)
        # map summary
        trees = game.plants
        fruited = [p for p in trees if p.fruits > 0]
        n_trees = len(trees)
        f.append(n_trees / 22.0)
        f.append(len(fruited) / 22.0)
        f.append(sum(p.fruits for p in trees) / 50.0)
        f.append((sum(p.size for p in trees) / n_trees / 4.0) if n_trees else 0.0)
        f.append((sum(p.health for p in trees) / n_trees / 18.0) if n_trees else 0.0)
        f.append(len(game.iron) / 8.0)
        f.append(len(game.water) / 8.0)

        # ── per-troll slots ──
        sx, sy = game.shacks[0]
        for slot in range(K):
            if slot < n_my:
                u = mine[slot]
                f.append(1.0)                                    # present
                f.append(u.x / MAP_W)
                f.append(u.y / MAP_H)
                f.append(u.ms / 4.0)
                f.append(u.cc / 6.0)
                f.append(u.hp / 4.0)
                f.append(u.chop / 4.0)
                f.append(u.total / max(u.cc, 1))
                f.append(u.carry[WOOD] / 6.0)
                f.append((u.carry[PLUM] + u.carry[LEMON] + u.carry[APPLE] + u.carry[BANANA]) / 6.0)
                f.append(u.free / 6.0)
                f.append(_manhattan(u.pos, (sx, sy)) / (MAP_W + MAP_H))
                f.append(1.0 if _manhattan(u.pos, (sx, sy)) <= 1 else 0.0)
                tt, td = _nearest(trees, u.pos)
                if tt is not None:
                    f.append(td / (MAP_W + MAP_H))
                    f.append(1.0 if u.pos == tt.pos else 0.0)
                    f.append(tt.size / 4.0)
                    f.append(tt.health / 18.0)
                    f.append(tt.fruits / 3.0)
                else:
                    f.extend((1.0, 0.0, 0.0, 0.0, 0.0))
                ft, fd = _nearest(fruited, u.pos)
                if ft is not None:
                    f.append(fd / (MAP_W + MAP_H))
                    f.append(1.0)
                else:
                    f.extend((1.0, 0.0))
            else:
                f.extend([0.0] * 20)

        return np.asarray(f, dtype=np.float32)


# convenience: expose action-space sizes for trainers
def action_nvec():
    return _ACTION_NVEC.copy()
