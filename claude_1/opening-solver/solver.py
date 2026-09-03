"""The opening solver, first form: a randomized greedy dispatcher in the top bots' order, many
rollouts per (second-troll talents, third-troll talents) pair, the best kept.

A rollout: turn 1 the start troll moves off the shack and the shack trains the second troll
from the draw; every free troll then takes the task with the best value per turn -- harvest a
wild tree the bill needs, bank, pick-and-plant a surplus seed next door, mine against the iron
deficit -- and the shack trains the third troll the turn the pre-turn stock clears its bill.
Randomness: the task choice is a softmax over values at temperature `temp`.
"""
from __future__ import annotations

import math
import random

from world import (IDX, ITEMS, IRON, WOOD, MAX_FRUITS, PLANT_COOLDOWN, State, training_cost)

FRUIT_KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")


# ------------------------------------------------------------------ tasks (one troll each)
class Task:
    kind = "?"

    def copy(self):
        t = self.__class__.__new__(self.__class__)
        t.__dict__.update(self.__dict__)
        return t

    def claims(self):
        """Items this task will bring home, for the other trolls' need accounting."""
        return None


class Harvest(Task):
    kind = "harvest"

    def __init__(self, cell, want):
        self.cell, self.want, self.taken = cell, want, 0

    def claims(self):
        return (self.cell, self.want - self.taken)

    def command(self, s: State, u):
        if u.pos != self.cell:
            return ("MOVE", self.cell)
        p = s.plants.get(self.cell)
        if p is None or p.fruits == 0 or u.free <= 0 or self.taken >= self.want:
            return None
        self.taken += min(u.hp, u.free, p.fruits)
        return ("HARVEST", None)


class Drop(Task):
    kind = "drop"

    def __init__(self, door):
        self.door, self.done = door, False

    def command(self, s, u):
        if self.done:
            return None
        if abs(u.x - s.m.shack[0]) + abs(u.y - s.m.shack[1]) > 1 or u.pos == s.m.shack:
            return ("MOVE", self.door)
        self.done = True
        return ("DROP", None)


class PickPlant(Task):
    kind = "plant"

    def __init__(self, seed, door, cell):
        self.seed, self.door, self.cell, self.stage = seed, door, cell, 0   # 0 go door, 1 picked, 2 planted

    def command(self, s, u):
        if self.stage == 0:
            if abs(u.x - s.m.shack[0]) + abs(u.y - s.m.shack[1]) > 1 or u.pos == s.m.shack:
                return ("MOVE", self.door)
            if u.free <= 0 or s.inv[IDX[self.seed]] <= 0:
                return None
            self.stage = 1
            return ("PICK", self.seed)
        if self.stage == 1:
            if u.pos != self.cell:
                return ("MOVE", self.cell)
            if self.cell in s.plants:
                return None
            self.stage = 2
            return ("PLANT", self.seed)
        return None


class Mine(Task):
    kind = "mine"

    def __init__(self, cell, want):
        self.cell, self.want, self.taken = cell, want, 0

    def claims(self):
        return ("IRON", self.want - self.taken)

    def command(self, s, u):
        if u.pos != self.cell:
            return ("MOVE", self.cell)
        if u.free <= 0 or self.taken >= self.want:
            return None
        self.taken += min(u.chop, u.free)
        return ("MINE", None)


class Leave(Task):
    """Step off the shack (a spawned troll stands on it and blocks the next TRAIN)."""
    kind = "leave"

    def __init__(self, cell):
        self.cell = cell

    def command(self, s, u):
        if u.pos == s.m.shack:
            return ("MOVE", self.cell)
        return None


# ------------------------------------------------------------------ the plan and the dispatcher
class Plan:
    def __init__(self, t2, t3, seeds, temp=0.0, seed_turn_limit=12, mine_early=False):
        self.t2 = tuple(t2) if t2 else None     # second troll talents (turn 1 or as soon as affordable)
        self.t3 = tuple(t3) if t3 else None     # third troll talents
        self.seeds = list(seeds)                # kinds to plant, in order
        self.temp = temp
        self.seed_turn_limit = seed_turn_limit
        self.mine_early = mine_early


def fruits_at(p, cd_eff, dt):
    """Fruits on plant `p` after `dt` more ticks with nobody touching it (health>0 assumed)."""
    size, fruits, cd = p.size, p.fruits, p.cd
    for _ in range(dt):
        if cd > 0:
            cd -= 1
        if cd == 0:
            if size < 4:
                size += 1
                cd = cd_eff
            elif fruits < MAX_FRUITS:
                fruits += 1
                cd = cd_eff
    return fruits, size


def next_bill(s: State, plan: Plan):
    """The next troll to buy and its bill, or (None, None) when the roster is complete."""
    n = len(s.units)
    if n == 1 and plan.t2:
        return plan.t2, training_cost(1, plan.t2)
    if n == 2 and plan.t3:
        return plan.t3, training_cost(2, plan.t3)
    if n == 1 and plan.t3:
        return plan.t3, training_cost(1, plan.t3)
    return None, None


def needs(s: State, plan: Plan):
    """Deficit per item toward the next bill after stock, carried and claimed items."""
    talents, bill = next_bill(s, plan)
    if talents is None:
        return None, [0] * 6
    have = list(s.inv)
    for u in s.units:
        for i in range(6):
            have[i] += u.carry[i]
        c = u.task.claims() if u.task is not None else None
        if c is not None:
            what, n = c
            if what == "IRON":
                have[IRON] += n
            else:
                p = s.plants.get(what)
                if p is not None:
                    have[IDX[p.kind]] += n
    pay = (0, 1, 2, 4) if s.m.has_iron else (0, 1, 2)
    return talents, [max(0, bill[i] - have[i]) if i in pay else 0 for i in range(6)]


def seed_surplus(s: State, plan: Plan, kind):
    """How many of `kind` the shack can spare for seeds: stock minus what the remaining bills need."""
    i = IDX[kind]
    reserve = 0
    n = len(s.units)
    if n <= 1 and plan.t2:
        reserve += training_cost(1, plan.t2)[i]
    if n <= 2 and plan.t3:
        reserve += training_cost(2, plan.t3)[i]
    return s.inv[i] - reserve


def plant_cell(s: State, u):
    """The free reachable cell minimising distance-to-shack plus distance-to-troll (the top bots'
    rule), never a door (a tree on a door is fine for the referee but costs the door's traffic)."""
    m = s.m
    best, best_c = None, None
    taken = set(s.plants)
    for c in m.reach:
        if c in taken or c in m.doors:
            continue
        v = min(m.d(c, d) for d in m.doors) + 1 + m.d(u.pos, c)
        if best is None or v < best or (v == best and c < best_c):
            best, best_c = v, c
    return best_c


def candidate_tasks(s: State, plan: Plan, u, rng):
    """Score every task the free troll `u` could take now; return [(value, task)]."""
    m = s.m
    talents, need = needs(s, plan)
    roster_done = talents is None
    out = []
    door = m.nearest_door(u.pos)
    d_home = m.d(u.pos, door) if u.pos != m.shack else 1
    carrying = u.total
    # bank what we carry
    if carrying > 0:
        needed_carried = sum(min(u.carry[i], need[i]) for i in range(6)) if not roster_done else 0
        value = (needed_carried * 1.0 + (carrying - needed_carried) * 0.3)
        out.append((value / (d_home + 1) + (2.0 if u.free == 0 else 0.0), Drop(door)))
    if u.free > 0:
        # harvest a tree
        for cell, p in s.plants.items():
            if p.health <= 0 or cell not in m.dist:
                continue
            d = m.d(u.pos, cell)
            if d >= 9999:
                continue
            arrive = -(-d // u.ms)
            fr, _ = fruits_at(p, m.eff_cd(p.kind, cell), arrive)
            # other trolls already heading there
            claimed = sum(v.task.want - v.task.taken for v in s.units
                          if v is not u and isinstance(v.task, Harvest) and v.task.cell == cell)
            avail = max(0, fr - claimed)
            if avail <= 0:
                continue
            k = IDX[p.kind]
            take = min(u.free, avail + (1 if fr >= MAX_FRUITS else 0))
            turns = arrive + -(-take // max(u.hp, 1)) + m.d(cell, m.nearest_door(cell)) / u.ms + 1
            worth = min(take, need[k]) * 1.0 + max(0, take - min(take, need[k])) * 0.25
            if roster_done:
                worth = take * 1.0
            out.append((worth / turns, Harvest(cell, take)))
        # mine against the iron deficit
        if m.has_iron and u.chop > 0 and (need[IRON] > 0 or plan.mine_early):
            cell = m.nearest_mine_cell(u.pos)
            if cell is not None:
                arrive = -(-m.d(u.pos, cell) // u.ms)
                take = min(u.free, max(need[IRON], 1))
                turns = arrive + -(-take // u.chop) + m.d(cell, m.nearest_door(cell)) / u.ms + 1
                out.append((min(take, need[IRON]) * 1.0 / turns, Mine(cell, take)))
        # plant a surplus seed next door
        if plan.seeds and s.turn <= plan.seed_turn_limit and carrying == 0:
            kind = plan.seeds[0]
            if seed_surplus(s, plan, kind) > 0:
                cell = plant_cell(s, u)
                if cell is not None:
                    turns = d_home + 1 + m.d(door, cell) + 1
                    out.append((0.6 / turns * 4, PickPlant(kind, door, cell)))
    if not out:
        out.append((0.0, Leave(door) if u.pos == m.shack else None))
    return out


def choose(cands, temp, rng):
    if temp <= 0 or len(cands) == 1:
        return max(cands, key=lambda c: c[0])[1]
    mx = max(c[0] for c in cands)
    ws = [math.exp((c[0] - mx) / temp) for c in cands]
    r = rng.random() * sum(ws)
    for w, c in zip(ws, cands):
        r -= w
        if r <= 0:
            return c[1]
    return cands[-1][1]


def rollout(s0: State, plan: Plan, rng, horizon=120, stop_when_done=True):
    """Play `plan` from `s0`; return the final state.  The state's `trains` carry the turns."""
    s = s0.copy()
    m = s.m
    while s.turn <= horizon:
        talents, bill = next_bill(s, plan)
        if talents is None and stop_when_done:
            break
        cmds = {}
        picks = [0] * 6
        for u in s.units:
            if u.task is not None:
                c = u.task.command(s, u)
                if c is None:
                    u.task = None
            if u.task is None:
                cands = candidate_tasks(s, plan, u, rng)
                t = choose(cands, plan.temp, rng)
                if t is None:
                    cmds[u.id] = ("WAIT", None)
                    continue
                u.task = t
                if isinstance(t, PickPlant) and plan.seeds:
                    plan.seeds.pop(0)
                c = u.task.command(s, u)
                if c is None:
                    u.task = None
                    cmds[u.id] = ("WAIT", None)
                    continue
            cmds[u.id] = c
            if c[0] == "PICK":
                picks[IDX[c[1]]] += 1
        train = None
        if talents is not None:
            after_picks = [s.inv[i] - picks[i] for i in range(6)]
            if s.affordable(talents, after_picks) and s.shack_free():
                train = talents
        s.step(cmds, train)
    return s
