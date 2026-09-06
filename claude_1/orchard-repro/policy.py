#!/usr/bin/env python3
"""The planting policies -- the macro layer's alphabet, and nothing else.

A policy rewrites the command of ONE designated planter troll (the second troll, from
the branch turn onward) and never touches any other fragment. Its whole vocabulary is
the six actions published in PREREGISTRATION sec 4 and corrected for arity in
ADDENDUM sec 1:

    NO_PLANT   -- no rewrite; the champion's own fragment passes through. Always legal.
    MOVE uid x y
    PICK uid KIND      (troll within 1 of the shack; takes a seed from the bank)
    PLANT uid KIND     (the tree appears at the TROLL'S OWN cell)
    CHOP uid           (the troll must be standing ON the tree's cell)
    DROP uid           (within 1 of the shack; banks the whole carry)

There is NO planting model here either: growth, self-occupancy, raid, felling, carry
and banking are whatever the referee does. This file only decides which of the six
strings to emit.
"""
from __future__ import annotations

import itertools

from harness import PassThrough, rewrite_line, split_fragments, fragment_uid

SPECIES = ("BANANA", "PLUM", "LEMON", "APPLE")
N_TREES = (1, 2, 3)
RADII = (2, 4)
TRIGGERS = ("maturity", "forest_gone")

MATURE_SIZE = 4
FOREST_RADIUS = 4          # "no wild tree stands within 4 steps of the shack"


def _man(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Policy(PassThrough):
    """(species, n_trees, radius, fell_trigger). Deterministic in every choice.

    The state machine, in priority order, evaluated fresh from the referee each turn:

      1. carrying wood            -> walk to the shack and DROP
      2. a felling trigger is met -> walk onto that own tree and CHOP
      3. fewer than n_trees own trees alive, and a free target cell exists:
             carrying the seed  -> walk to the target; PLANT when standing on it
             not carrying it    -> walk to the shack; PICK when within 1
      4. otherwise                -> NO_PLANT (the champion's own command)

    Target cells are the free walkable cells within `radius` of our shack, ordered
    deterministically: water-adjacent first (they fruit 2-3x sooner), then nearer,
    then by (x, y). The shack cell and its immediate door are never used as targets --
    a tree there would wall the champion's own banking in.
    """

    def __init__(self, species, n_trees, radius, trigger):
        super().__init__()
        self.species = species
        self.n_trees = n_trees
        self.radius = radius
        self.trigger = trigger
        self.name = "%s/%d/r%d/%s" % (species.lower(), n_trees, radius, trigger)
        self.mine = set()               # cells this policy planted
        self.targets = None
        self.emitted = {"MOVE": 0, "PICK": 0, "PLANT": 0, "CHOP": 0, "DROP": 0}
        self.plant_attempts = []        # (turn, cell, plants_before, carry_before)
        self.plant_accounting = []      # filled by the runner after each turn
        # why a turn ended in NO_PLANT: the diagnostic that tells "the policy declined"
        # apart from "the policy could not act"
        self.passed = {"satisfied": 0, "no_free_cell": 0, "bank_empty": 0,
                       "hands_full": 0}

    # -- geometry ------------------------------------------------------------
    def _build_targets(self, ref):
        shack = ref.tent
        cand = []
        for cell in ref.walk:
            d = _man(cell, shack)
            if d == 0 or d > self.radius:
                continue
            if d == 1:                      # the door: never block our own banking
                continue
            cand.append((0 if ref.near_water(cell) else 1, d, cell[0], cell[1], cell))
        cand.sort()
        self.targets = [c[4] for c in cand]

    def _alive(self, ref):
        return [c for c in self.mine if c in ref.plants]

    def _free_target(self, ref):
        for cell in self.targets:
            if cell not in ref.plants:
                return cell
        return None

    def _forest_gone(self, ref):
        for cell, p in ref.plants.items():
            if cell in self.mine:
                continue
            if _man(cell, ref.tent) <= FOREST_RADIUS:
                return False
        return True

    def _fellable(self, ref):
        alive = self._alive(ref)
        if not alive:
            return None
        if self.trigger == "maturity":
            ripe = [c for c in alive if ref.plants[c]["size"] >= MATURE_SIZE]
        else:
            ripe = alive if self._forest_gone(ref) else []
        if not ripe:
            return None
        return sorted(ripe, key=lambda c: (_man(c, ref.tent), c))[0]

    # -- the macro -----------------------------------------------------------
    def __call__(self, turn, ref, line):
        # the branch bookkeeping is the pass-through's, unchanged
        base = PassThrough.__call__(self, turn, ref, line)
        if self.branch_turn is None or self.branch_turn == turn:
            return base
        u = ref.units.get(self.planter)
        if u is None:
            return base
        if self.targets is None:
            self._build_targets(ref)

        act = self._decide(turn, ref, u)
        if act is None:
            return base                                    # NO_PLANT
        verb = act.split()[0]
        self.emitted[verb] += 1
        return rewrite_line(line, self.planter, act)

    def _decide(self, turn, ref, u):
        if self.n_trees == 0:
            # BANK_ONLY control: rule 1 alone. It exists because rule 1 fires on turns
            # where the policy is otherwise inactive -- the macro overrides the
            # champion's own banking decision even when it never plants -- so the
            # overlay is NOT a pure superset of NO_PLANT and that has to be priced
            # separately from planting. Found by tracing the run, reported as such.
            WOOD = 5
            if u["carry"][WOOD] > 0:
                if _man(u["cell"], ref.tent) <= 1:
                    return "DROP %d" % self.planter
                return "MOVE %d %d %d" % (self.planter, ref.tent[0], ref.tent[1])
            self.passed["satisfied"] += 1
            return None
        uid = self.planter
        carry = u["carry"]
        shack = ref.tent
        WOOD = 5
        sidx = {"PLUM": 0, "LEMON": 1, "APPLE": 2, "BANANA": 3}[self.species]

        # 1. bank wood we are holding
        if carry[WOOD] > 0:
            if _man(u["cell"], shack) <= 1:
                return "DROP %d" % uid
            return "MOVE %d %d %d" % (uid, shack[0], shack[1])

        # 2. fell
        tree = self._fellable(ref)
        if tree is not None:
            if u["cell"] == tree:
                return "CHOP %d" % uid
            return "MOVE %d %d %d" % (uid, tree[0], tree[1])

        # 3. plant up to n_trees
        if len(self._alive(ref)) < self.n_trees:
            target = self._free_target(ref)
            if target is None:
                self.passed["no_free_cell"] += 1
            else:
                if carry[sidx] > 0:
                    if u["cell"] == target:
                        self.plant_attempts.append(
                            (turn, target, len(ref.plants), list(carry)))
                        return "PLANT %d %s" % (uid, self.species)
                    return "MOVE %d %d %d" % (uid, target[0], target[1])
                # need a seed; only fetchable at the shack, and only if in stock
                if sum(carry) >= u["cap"]:
                    self.passed["hands_full"] += 1
                    return None                       # hands full of something else
                if ref.inv[sidx] <= 0:
                    self.passed["bank_empty"] += 1
                    return None                       # bank is empty: NO_PLANT
                if _man(u["cell"], shack) <= 1:
                    return "PICK %d %s" % (uid, self.species)
                return "MOVE %d %d %d" % (uid, shack[0], shack[1])
        else:
            self.passed["satisfied"] += 1
        return None

    def note_planted(self, ref):
        """Called by the runner AFTER the referee applied the turn: every cell we
        planted becomes ours, so `_alive` counts our own orchard and `_forest_gone`
        does not count our own trees as wild forest."""
        while self.plant_attempts:
            turn, cell, before, carry = self.plant_attempts.pop(0)
            landed = cell in ref.plants
            self.plant_accounting.append(
                {"turn": turn, "cell": list(cell), "landed": bool(landed)})
            if landed:
                self.mine.add(cell)


def bank_only():
    """The control that prices rule 1 on its own: never plants, only banks wood."""
    pol = Policy("BANANA", 0, 2, "maturity")
    pol.name = "BANK_ONLY"
    return pol


def grid():
    """49 policies: 4 x 3 x 2 x 2 planting policies plus NO_PLANT, plus the BANK_ONLY
    control (50 arms in all)."""
    out = [PassThrough(), bank_only()]
    for sp, n, r, t in itertools.product(SPECIES, N_TREES, RADII, TRIGGERS):
        out.append(Policy(sp, n, r, t))
    return out


def fresh(name):
    if name == "NO_PLANT":
        return PassThrough()
    if name == "BANK_ONLY":
        return bank_only()
    sp, n, r, t = name.split("/")
    return Policy(sp.upper(), int(n), int(r[1:]), t)
