"""The opening solver, first form: a randomized greedy dispatcher in the top bots' order, many
rollouts per plan (second-troll talents, third-troll talents, the seeds and where they go), the
best kept.  A rollout: turn 1 the start troll moves off the shack and the shack trains the second
troll from the draw; every free troll then takes the task with the best value per turn -- harvest
a wild tree the bill needs, bank, pick-and-plant a seed (next door, or next to water where fruit
comes four times faster), mine against the iron deficit -- and the shack trains the third troll
the turn the pre-turn stock clears its bill.  Randomness: a softmax over task values at `temp`.
"""
from __future__ import annotations

import math

from world import IDX, IRON, MAX_FRUITS, State, training_cost

FRUIT_KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")

#: ablation switches (ablate.py): one item a trip; wild trees beyond this distance off limits
CARRY_ONE = False
NEAR_ONLY = None


# ------------------------------------------------------------------ tasks (one troll each)
class Task:
    kind = "?"

    def copy(self):
        t = self.__class__.__new__(self.__class__)
        t.__dict__.update(self.__dict__)
        return t


class Harvest(Task):
    kind = "harvest"

    def __init__(self, cell, want, wait=False):
        self.cell, self.want, self.taken, self.wait = cell, want, 0, wait

    def command(self, s: State, u):
        if u.pos != self.cell:
            return ("MOVE", self.cell)
        p = s.plants.get(self.cell)
        if p is None or u.free <= 0 or self.taken >= self.want:
            return None
        if p.fruits == 0:
            if self.wait and p.health > 0:
                return ("WAIT", None)
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
        self.seed, self.door, self.cell, self.stage = seed, door, cell, 0   # 0 to the door, 1 picked, 2 planted

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


# ------------------------------------------------------------------ the plan
class Plan:
    """What a rollout is told.  `seeds`: [(kind, mode)] in planting order, mode 'near' (the top
    bots' cell: min distance-to-shack plus distance-to-troll) or 'water' (the nearest free cell
    next to water).  `reserve_t3`: whether seeds may only come from stock beyond the third
    troll's bill.  `surplus_weight`: value of a fruit the bill does not need (a point, a seed)."""

    def __init__(self, t2, t3, seeds=(), temp=0.0, seed_turn_limit=14, reserve_t3=True,
                 surplus_weight=0.25, mine_early=False, wait_cd=4, t2_not_before=1, bottleneck=0.0,
                 reserve_t2=True):
        self.reserve_t2 = reserve_t2            # may a seed delay the second troll's purchase?
        self.t2_not_before = t2_not_before      # ablation: the second troll may not be bought earlier
        self.bottleneck = bottleneck            # 0: every needed item worth 1; 1: worth its fetch cost (bottleneck first)
        self.t2 = tuple(t2) if t2 else None
        self.t3 = tuple(t3) if t3 else None
        self.seeds = [(k, m) for k, m in seeds]
        self.temp = temp
        self.seed_turn_limit = seed_turn_limit
        self.reserve_t3 = reserve_t3
        self.surplus_weight = surplus_weight
        self.mine_early = mine_early
        self.wait_cd = wait_cd

    def args(self):
        return dict(t2=self.t2, t3=self.t3, seeds=list(self.seeds), temp=self.temp,
                    seed_turn_limit=self.seed_turn_limit, reserve_t3=self.reserve_t3,
                    surplus_weight=self.surplus_weight, mine_early=self.mine_early, wait_cd=self.wait_cd,
                    t2_not_before=self.t2_not_before, bottleneck=self.bottleneck, reserve_t2=self.reserve_t2)


def fruits_at(p, cd_eff, dt):
    """Fruits on plant `p` after `dt` more ticks with nobody touching it."""
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
    return fruits, size, cd


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
        t = u.task
        if isinstance(t, Harvest):
            p = s.plants.get(t.cell)
            if p is not None:
                have[IDX[p.kind]] += t.want - t.taken
        elif isinstance(t, Mine):
            have[IRON] += t.want - t.taken
    pay = (0, 1, 2, 4) if s.m.has_iron else (0, 1, 2)
    return talents, [max(0, bill[i] - have[i]) if i in pay else 0 for i in range(6)]


def seed_surplus(s: State, plan: Plan, kind):
    """How many of `kind` the shack can spare for a seed."""
    i = IDX[kind]
    reserve = 0
    n = len(s.units)
    if n <= 1 and plan.t2 and plan.reserve_t2:
        reserve += training_cost(1, plan.t2)[i]
    if n <= 2 and plan.t3 and plan.reserve_t3:
        reserve += training_cost(2, plan.t3)[i]
    return s.inv[i] - reserve


def plant_cell(s: State, u, mode):
    """'near': the free reachable cell minimising distance-to-shack plus distance-to-troll (the top
    bots' rule); 'water': the same among cells next to water.  Doors are never used."""
    m = s.m
    best, best_c = None, None
    for c in m.reach:
        if c in s.plants or c in m.doors:
            continue
        if mode == "water" and not m.near_water[c]:
            continue
        v = min(m.d(c, d) for d in m.doors) + 1 + m.d(u.pos, c)
        if best is None or v < best or (v == best and c < best_c):
            best, best_c = v, c
    return best_c


def fetch_cost(s: State, u, item):
    """Turns per unit of `item` for troll `u` from the cheapest source now (a rough, monotone
    number: walking there and back, the taking, per unit carried)."""
    m = s.m
    door = m.nearest_door(u.pos)
    best = None
    if item == IRON:
        cell = m.nearest_mine_cell(u.pos)
        if cell is None or u.chop == 0:
            return None
        take = min(u.free, u.chop) if u.free > 0 else 1
        d = m.d(door, cell)
        return (2 * d + -(-take // u.chop) + 1) / max(take, 1)
    for cell, p in s.plants.items():
        if IDX[p.kind] != item or p.health <= 0 or cell not in m.dist:
            continue
        d = m.d(door, cell)
        fr = p.fruits if p.fruits > 0 else (1 if p.size >= 4 else 0)
        if fr <= 0:
            continue
        take = min(max(u.cc, 1), fr)
        cost = (2 * d + -(-take // max(u.hp, 1)) + 1) / take
        if best is None or cost < best:
            best = cost
    return best


def item_weights(s: State, plan: Plan, u, need):
    """Weight of one needed unit of each item: its fetch cost relative to the mean over the items
    still needed, so the bottleneck is fetched first; unknown sources count as expensive."""
    costs = {}
    for i in range(6):
        if need[i] > 0:
            c = fetch_cost(s, u, i)
            costs[i] = c if c is not None else 40.0
    if not costs:
        return (1.0,) * 6
    mean = sum(costs.values()) / len(costs)
    w = [1.0] * 6
    for i, c in costs.items():
        w[i] = 1.0 + plan.bottleneck * (c / mean - 1.0)
        w[i] = max(0.3, min(w[i], 4.0))
    return tuple(w)


def best_door(s: State, u, need):
    """The door to bank at: the one minimising the walk to it plus the walk from it to the next
    job (the closest tree with fruit the bill needs, or the mine when iron is short).  The
    funding read blamed our bot for walking to a far door; this is the rule that avoids it."""
    m = s.m
    if len(m.doors) == 1:
        return m.doors[0]
    targets = []
    for cell, p in s.plants.items():
        if p.health > 0 and cell in m.dist and (p.fruits > 0 or p.size >= 4) and need[IDX[p.kind]] > 0:
            targets.append(cell)
    if need[IRON] > 0 and m.mine_cells:
        targets.extend(m.mine_cells[:2])
    best, best_door_cell = None, None
    for door in m.doors:
        d0 = m.d(u.pos, door) if u.pos != m.shack else 1
        d1 = min((m.d(door, c) for c in targets), default=0)
        v = (d0 + d1, d0, door)
        if best is None or v < best:
            best, best_door_cell = v, door
    return best_door_cell


def candidate_tasks(s: State, plan: Plan, u):
    """Score every task the free troll `u` could take now; return [(value, task)]."""
    m = s.m
    talents, need = needs(s, plan)
    roster_done = talents is None
    out = []
    door = best_door(s, u, need)
    d_home = m.d(u.pos, door) if u.pos != m.shack else 1
    carrying = u.total
    sw = plan.surplus_weight
    w = item_weights(s, plan, u, need) if (plan.bottleneck and not roster_done) else (1.0,) * 6
    if carrying > 0:
        needed_carried = 0 if roster_done else sum(min(u.carry[i], need[i]) * w[i] for i in range(6))
        plain = 0 if roster_done else sum(min(u.carry[i], need[i]) for i in range(6))
        value = needed_carried + (carrying - plain) * sw
        out.append((value / (d_home + 1) + (2.0 if u.free == 0 else 0.0), Drop(door)))
    if u.free > 0:
        for cell, p in s.plants.items():
            if p.health <= 0 or cell not in m.dist:
                continue
            d = m.d(u.pos, cell)
            if d >= 9999:
                continue
            if NEAR_ONLY is not None and not p.own and min(m.d(cell, dd) for dd in m.doors) > NEAR_ONLY:
                continue
            arrive = -(-d // u.ms)
            cd_eff = m.eff_cd(p.kind, cell)
            fr, size, cd = fruits_at(p, cd_eff, arrive)
            claimed = sum(v.task.want - v.task.taken for v in s.units
                          if v is not u and isinstance(v.task, Harvest) and v.task.cell == cell)
            k = IDX[p.kind]
            worth_each = w[k] if need[k] > 0 else sw
            back = m.d(cell, m.nearest_door(cell)) / u.ms + 1
            # take what is there (a full tree regrows one the same turn it is harvested)
            avail = max(0, fr - claimed)
            if avail > 0:
                take = min(u.free, avail + (1 if fr >= MAX_FRUITS and cd == 0 else 0))
                if CARRY_ONE:
                    take = 1
                turns = arrive + -(-take // max(u.hp, 1)) + back
                worth = min(take, need[k]) * w[k] + max(0, take - need[k]) * sw
                if roster_done:
                    worth = take
                out.append((worth / turns, Harvest(cell, take)))
            # or stay and let a fast tree refill the carry
            if size >= 4 and cd_eff <= plan.wait_cd and u.free > avail and claimed == 0 and not CARRY_ONE:
                take = u.free
                extra = take - avail
                turns = arrive + max(1, -(-avail // max(u.hp, 1))) + extra * cd_eff + back
                worth = min(take, need[k]) * w[k] + max(0, take - need[k]) * sw
                if roster_done:
                    worth = take
                out.append((worth / turns * 0.98, Harvest(cell, take, wait=True)))
            if arrive < 20 and fr == 0 and size >= 4 and cd > 0 and cd + arrive <= 12 and need[k] > 0 and claimed == 0:
                # a tree about to bear: go and wait for it
                take = min(u.free, 1)
                turns = arrive + (cd - arrive if cd > arrive else 0) + 1 + back
                out.append((worth_each / turns * 0.9, Harvest(cell, take, wait=True)))
        if m.has_iron and u.chop > 0 and (need[IRON] > 0 or plan.mine_early):
            cell = m.nearest_mine_cell(u.pos)
            if cell is not None:
                arrive = -(-m.d(u.pos, cell) // u.ms)
                take = min(u.free, max(need[IRON], 1))
                if CARRY_ONE:
                    take = 1
                turns = arrive + -(-take // u.chop) + m.d(cell, m.nearest_door(cell)) / u.ms + 1
                out.append((min(take, need[IRON]) * w[IRON] / turns, Mine(cell, take)))
        if plan.seeds and s.turn <= plan.seed_turn_limit and carrying == 0:
            kind, mode = plan.seeds[0]
            if seed_surplus(s, plan, kind) > 0:
                cell = plant_cell(s, u, mode)
                if cell is not None:
                    turns = d_home + 1 + m.d(door, cell) + 1
                    out.append((3.0 / turns, PickPlant(kind, door, cell)))
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


def shack_free_after_moves(s: State, cmds):
    """TRAIN resolves after MOVE: the shack must be empty once this turn's moves have happened.
    A troll standing on the shack with a MOVE order leaves it unless another own troll blocks."""
    if s.shack_free():
        return True
    probe = s.copy()
    probe._apply_moves({uid: arg for uid, (verb, arg) in cmds.items() if verb == "MOVE"})
    return probe.shack_free()


def rollout(s0: State, plan: Plan, rng, horizon=160, stop_when_done=True):
    """Play `plan` from `s0`; return the final state (its `trains` carry the turns, its `log` the
    referee command lines).  The plan's seed list is consumed, so pass a fresh Plan each time."""
    s = s0.copy()
    while s.turn <= horizon:
        talents, bill = next_bill(s, plan)
        if talents is None and stop_when_done:
            break
        cmds = {}
        picks = [0] * 6
        for u in s.units:
            c = None
            if u.task is not None:
                c = u.task.command(s, u)
                if c is None:
                    u.task = None
            if u.task is None:
                t = choose(candidate_tasks(s, plan, u), plan.temp, rng)
                if t is None:
                    cmds[u.id] = ("WAIT", None)
                    continue
                if isinstance(t, PickPlant):
                    plan.seeds.pop(0)
                u.task = t
                c = t.command(s, u)
                if c is None:
                    u.task = None
                    cmds[u.id] = ("WAIT", None)
                    continue
            cmds[u.id] = c
            if c[0] == "PICK":
                picks[IDX[c[1]]] += 1
        train = None
        if talents is not None and not (len(s.units) == 1 and s.turn < plan.t2_not_before):
            after_picks = [s.inv[i] - picks[i] for i in range(6)]
            if s.affordable(talents, after_picks) and shack_free_after_moves(s, cmds):
                train = talents
        s.step(cmds, train)
    return s
