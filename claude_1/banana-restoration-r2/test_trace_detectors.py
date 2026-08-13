#!/usr/bin/env python3
"""Synthetic self-tests for trace_detectors D-1..D-9.

For each detector: at least one synthetic trace that TRIGGERS it and one
near-miss that must NOT trigger it. Transcripts are built programmatically in
the real stdin protocol format (static map + per-turn blocks) and commands in
the real one-line-per-turn ';'-joined format.

Run: python3 -m unittest test_trace_detectors -v
"""

from __future__ import annotations

import unittest

import trace_detectors as td

# 9x7 map, own tent '0' at (4,3), enemy shack '1' at (8,6). No water, no iron.
# doors(tent) = {(4,2),(5,3),(4,4),(3,3)}; diag(tent) = {(3,2),(5,2),(3,4),(5,4)}
# |Ring| = 8.
MAP_HEADER = "9 7"
MAP_ROWS = [
    ".........",
    ".........",
    ".........",
    "....0....",
    ".........",
    ".........",
    "........1",
]

TENT = (4, 3)
DOOR = (4, 2)
DIAG = (3, 2)


def unit(uid, player, cell, speed=1, cap=2, hp=1, cp=1, carry=None):
    carry = carry or [0] * 6
    return " ".join(str(v) for v in
                    [uid, player, cell[0], cell[1], speed, cap, hp, cp]
                    + list(carry))


def plant(kind, cell, size=1, health=3, fruits=0, cooldown=4):
    return "%s %d %d %d %d %d %d" % (kind, cell[0], cell[1], size, health,
                                     fruits, cooldown)


def turn_block(units, plants=(), inv0=None, inv1=None):
    inv0 = inv0 or [0] * 6
    inv1 = inv1 or [0] * 6
    lines = [" ".join(str(v) for v in inv0),
             " ".join(str(v) for v in inv1),
             str(len(plants))]
    lines.extend(plants)
    lines.append(str(len(units)))
    lines.extend(units)
    return lines


def make_trace(blocks, command_lines):
    body = [MAP_HEADER] + MAP_ROWS
    for block in blocks:
        body.extend(block)
    transcript = "\n".join(body) + "\n"
    commands = "\n".join(command_lines) + "\n"
    return td.build_trace(transcript, commands)


def carry_of(**kw):
    c = [0] * 6
    for name, v in kw.items():
        c[td.ITEM_NAMES.index(name.upper())] = v
    return c


OPP = unit(9, 1, (8, 0))  # inert far-away opponent used as filler


class TestParsers(unittest.TestCase):
    def test_roundtrip(self):
        tr = make_trace(
            [turn_block([unit(0, 0, (1, 1), carry=carry_of(wood=1)), OPP],
                        plants=[plant("BANANA", (2, 2), fruits=1)],
                        inv0=[1, 2, 3, 4, 5, 6])],
            ["MOVE 0 4 2;MSG hello"])
        self.assertEqual(tr.T, 1)
        self.assertEqual(tr.tent, TENT)
        self.assertEqual(tr.doors, frozenset({(4, 2), (5, 3), (4, 4), (3, 3)}))
        self.assertEqual(tr.diag, frozenset({(3, 2), (5, 2), (3, 4), (5, 4)}))
        self.assertEqual(len(tr.ring), 8)
        st = tr.state(1)
        self.assertEqual(st.inventories[0], [1, 2, 3, 4, 5, 6])
        self.assertEqual(st.unit(0).carry[td.WOOD], 1)
        self.assertEqual(st.plant_at((2, 2)).kind, "BANANA")
        cmd = tr.cmd_of(0, 1)
        self.assertEqual(cmd.verb, "MOVE")
        self.assertEqual(cmd.args[0], (4, 2))


def verdict(res):
    return res["verdict"], res["count"]


class TestD1(unittest.TestCase):
    """D-1 A->B->A movement: k >= 3 window, zero progress events."""

    A, B = (1, 1), (2, 1)

    def alternating(self, turns, carry_fn=None):
        blocks, cmds = [], []
        for t in range(1, turns + 1):
            pos = self.A if t % 2 == 1 else self.B
            nxt = self.B if t % 2 == 1 else self.A
            carry = carry_fn(t) if carry_fn else [0] * 6
            blocks.append(turn_block([unit(0, 0, pos, carry=carry), OPP]))
            cmds.append("MOVE 0 %d %d" % nxt)
        return make_trace(blocks, cmds)

    def test_trigger_period2_10_turns(self):
        tr = self.alternating(10)
        res = td.detect_d1(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["unit"], 0)
        self.assertEqual((ep["turn_start"], ep["turn_end"]), (1, 10))
        self.assertGreaterEqual(ep["k"], 3)

    def test_near_miss_progress_event_inside(self):
        # A->B->A->B alternation WITH a progress event (carry delta on the
        # 5->6 transition) inside: D-1 must exempt it.
        tr = self.alternating(
            10, carry_fn=lambda t: carry_of(wood=1) if t >= 6 else [0] * 6)
        self.assertEqual(verdict(td.detect_d1(tr)), ("PASS", 0))

    def test_near_miss_short_window_k2(self):
        # only 5 states (k = 2) -- below the k >= 3 threshold of D-1
        tr = self.alternating(5)
        self.assertEqual(verdict(td.detect_d1(tr)), ("PASS", 0))


class TestD2(unittest.TestCase):
    """D-2 repeated PICK/DROP at doors, net-zero window <= 12 turns."""

    def pick_drop_trace(self, cmds, carries, invs):
        blocks = []
        for carry_b, inv_b in zip(carries, invs):
            blocks.append(turn_block(
                [unit(0, 0, DOOR, carry=carry_of(banana=carry_b)), OPP],
                inv0=carry_of(banana=inv_b)))
        return make_trace(blocks, cmds)

    def test_trigger_two_zero_net_cycles(self):
        tr = self.pick_drop_trace(
            ["PICK 0 BANANA", "DROP 0", "PICK 0 BANANA", "DROP 0", "WAIT"],
            carries=[0, 1, 0, 1, 0], invs=[5, 4, 5, 4, 5])
        res = td.detect_d2(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["unit"], 0)
        self.assertEqual((ep["turn_start"], ep["turn_end"]), (1, 4))

    def test_near_miss_single_pair_is_legit_seed_abort(self):
        tr = self.pick_drop_trace(
            ["PICK 0 BANANA", "DROP 0", "WAIT"],
            carries=[0, 1, 0], invs=[5, 4, 5])
        self.assertEqual(verdict(td.detect_d2(tr)), ("PASS", 0))


class TestD3(unittest.TestCase):
    """D-3 same-target contention >= 2 consecutive turns."""

    def two_movers(self, dests2):
        blocks, cmds = [], []
        p0 = [(1, 1), (2, 1), (3, 1)]
        p2 = [(1, 5), (2, 5), (3, 5)]
        for t in range(3):
            blocks.append(turn_block(
                [unit(0, 0, p0[t]), unit(2, 0, p2[t]), OPP]))
            d0, d2 = dests2[t]
            cmds.append("MOVE 0 %d %d;MOVE 2 %d %d" % (d0 + d2))
        return make_trace(blocks, cmds)

    def test_trigger_shared_move_target_2_turns(self):
        tr = self.two_movers([((6, 1), (6, 1)), ((6, 1), (6, 1)),
                              ((6, 1), (6, 5))])
        res = td.detect_d3(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["units"], [0, 2])
        self.assertEqual((ep["turn_start"], ep["turn_end"]), (1, 2))

    def test_near_miss_one_turn_transient(self):
        # single-turn shared target is the conflict resolver's to fix (D-3)
        tr = self.two_movers([((6, 1), (6, 1)), ((6, 1), (6, 5)),
                              ((6, 1), (6, 5))])
        self.assertEqual(verdict(td.detect_d3(tr)), ("PASS", 0))


class TestD4(unittest.TestCase):
    """D-4 abandoned carried-wood return."""

    def wood_trace(self, positions, cmds, wood=1, drop_turn=None):
        blocks = []
        for t, pos in enumerate(positions, start=1):
            w = wood if (drop_turn is None or t <= drop_turn) else 0
            inv0 = carry_of(wood=1) if (drop_turn is not None
                                        and t > drop_turn) else [0] * 6
            blocks.append(turn_block(
                [unit(0, 0, pos, carry=carry_of(wood=w)), OPP], inv0=inv0))
        return make_trace(blocks, cmds)

    def test_trigger_non_bank_verb_during_commitment(self):
        tr = self.wood_trace([(1, 1), (2, 1), (2, 2)],
                             ["MOVE 0 4 2", "CHOP 0", "WAIT"])
        res = td.detect_d4(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["episodes"][0]["kind"], "non_bank_verb")
        self.assertEqual(res["episodes"][0]["verb"], "CHOP")

    def test_trigger_two_turns_without_progress(self):
        # committed at t1, then door_dist increases on two consecutive
        # transitions (2, 3, 4) -> violation (I-20 tolerates only 1)
        tr = self.wood_trace([(2, 2), (1, 2), (0, 2), (0, 2)],
                             ["MOVE 0 4 2", "MOVE 0 0 2", "WAIT", "WAIT"])
        res = td.detect_d4(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["episodes"][0]["kind"], "no_progress")

    def test_near_miss_monotone_return_and_drop(self):
        tr = self.wood_trace([(2, 2), (3, 2), (4, 2), (4, 2), (4, 2)],
                             ["MOVE 0 4 2", "MOVE 0 4 2", "DROP 0",
                              "WAIT", "WAIT"],
                             drop_turn=3)
        self.assertEqual(verdict(td.detect_d4(tr)), ("PASS", 0))

    def test_near_miss_single_stall_is_tolerated(self):
        # one non-decrease turn (resolver displacement) then progress + DROP
        tr = self.wood_trace([(2, 2), (2, 2), (3, 2), (4, 2), (4, 2)],
                             ["MOVE 0 4 2", "MOVE 0 4 2", "MOVE 0 4 2",
                              "DROP 0", "WAIT"],
                             drop_turn=4)
        self.assertEqual(verdict(td.detect_d4(tr)), ("PASS", 0))


class TestD5(unittest.TestCase):
    """D-5 unbounded planting."""

    def plant_trace(self, cell, plant_turn, total_turns):
        blocks, cmds = [], []
        for t in range(1, total_turns + 1):
            carry = carry_of(banana=1) if t <= plant_turn else [0] * 6
            plants = [plant("BANANA", cell)] if t > plant_turn else []
            blocks.append(turn_block([unit(0, 0, cell, carry=carry), OPP],
                                     plants=plants))
            cmds.append("PLANT 0 BANANA" if t == plant_turn else "WAIT")
        return make_trace(blocks, cmds)

    def test_trigger_plant_outside_ring(self):
        tr = self.plant_trace((6, 3), plant_turn=1, total_turns=2)
        res = td.detect_d5(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["episodes"][0]["kind"], "outside_ring")
        self.assertEqual(res["episodes"][0]["cell"], [6, 3])

    def test_trigger_plant_after_cutoff(self):
        # orth slot, no water => CD_dry = 6, chop = 1:
        # T_late = 300 - (2*6 + 4 + 2) = 282 < 299 (I-5 cutoff, D-5)
        tr = self.plant_trace(DOOR, plant_turn=299, total_turns=300)
        res = td.detect_d5(tr)
        self.assertEqual(res["verdict"], "FAIL")
        kinds = {ep["kind"] for ep in res["episodes"]}
        self.assertIn("orth_cutoff", kinds)

    def test_near_miss_early_ring_plant(self):
        tr = self.plant_trace(DIAG, plant_turn=1, total_turns=2)
        self.assertEqual(verdict(td.detect_d5(tr)), ("PASS", 0))


# The Ring is the 8 cells at Chebyshev distance 1 from the tent — the only legal
# banana slots (I-12). |Ring| = 8 is the bound both I-13 clauses are written against.
RING = [(x, y) for x in range(3, 6) for y in range(2, 5) if (x, y) != TENT]

# Same 9x7 map, but with water at (4,1) — orthogonally adjacent to the DOOR slot
# (4,2), so `near_water(DOOR)` is True and the planting cooldown is CD_wet = 4.
MAP_ROWS_WATER = [
    ".........",
    "....~....",
    ".........",
    "....0....",
    ".........",
    ".........",
    "........1",
]


def make_trace_on(map_rows, blocks, command_lines):
    """make_trace, but on a caller-supplied map (needed to exercise water)."""
    body = [MAP_HEADER] + map_rows
    for block in blocks:
        body.extend(block)
    return td.build_trace("\n".join(body) + "\n", "\n".join(command_lines) + "\n")


class TestD5Uncovered(unittest.TestCase):
    """G6 fixtures for the three D-5 branches the bite-test audit found with NO_FIXTURE.

    Task `20260810-guards-that-cannot-fail`, sub-item G6. Fixtures only — no predicate is
    touched. Each branch gets both halves: the innocent case that must stay silent, and a
    deliberately violating subject observed firing.

    Branch -> mutant these are written to kill:
      (b) I-13 cumulative bound `:850`   -> D5-M4 (`len(cumulative) > ring_size` -> False)
      (c) I-13 concurrent bound `:876`   -> D5-M5 (`len(alive) > ring_size` -> False)
      (f) water-boost CD selection `:857`-> D5-M8 (cooldown always CD_wet)
    """

    def sequential_plant(self, cells, keep_alive):
        """One PLANT per turn, walking the unit onto each cell in turn.

        `keep_alive` controls whether the planted trees are still present in later states:
        the cumulative bound counts PLANT events and does not care, the concurrent bound
        counts living trees and cares entirely.
        """
        blocks, cmds = [], []
        for i in range(len(cells) + 1):
            planted = cells[:i] if keep_alive else []
            here = cells[i] if i < len(cells) else cells[-1]
            blocks.append(turn_block(
                [unit(0, 0, here, carry=carry_of(banana=1)), OPP],
                plants=[plant("BANANA", c) for c in planted]))
            cmds.append("PLANT 0 BANANA" if i < len(cells) else "WAIT")
        return make_trace(blocks, cmds)

    def kinds(self, tr):
        return {e["kind"] for e in td.detect_d5(tr)["episodes"]}

    # --- (b) I-13 cumulative bound ------------------------------------------------

    def test_eight_distinct_ring_cells_is_within_the_cumulative_bound(self):
        """The innocent case: every Ring slot used once is exactly |Ring|, not over it."""
        self.assertEqual(len(RING), 8)
        self.assertEqual(verdict(td.detect_d5(self.sequential_plant(RING, False))), ("PASS", 0))

    def test_a_ninth_distinct_cell_breaks_the_cumulative_bound(self):
        """The violation: a 9th distinct planting site exceeds |Ring| over the game.

        The 9th cell is necessarily outside the Ring — there is no 9th Ring cell — so this
        trace also trips `outside_ring`. The assertion names `cumulative_over_ring`
        specifically so the two clauses cannot stand in for one another."""
        kinds = self.kinds(self.sequential_plant(RING + [(6, 3)], False))
        self.assertIn("cumulative_over_ring", kinds)

    def test_replanting_the_same_cell_does_not_grow_the_cumulative_count(self):
        """Cumulative counts DISTINCT sites: nine plants on eight cells stays legal."""
        self.assertEqual(verdict(td.detect_d5(self.sequential_plant(RING + [RING[0]], False))),
                         ("PASS", 0))

    # --- (c) I-13 concurrent bound -------------------------------------------------

    def test_eight_trees_alive_at_once_is_within_the_concurrent_bound(self):
        """The innocent case: eight living trees is exactly |Ring|."""
        self.assertNotIn("concurrent_over_ring", self.kinds(self.sequential_plant(RING, True)))

    def test_nine_trees_alive_at_once_breaks_the_concurrent_bound(self):
        """The violation: a 9th simultaneously living tree.

        Distinct from (b): the cumulative clause counts sites ever used, this one counts
        trees standing at the same moment. The two are only equal when nothing is felled."""
        kinds = self.kinds(self.sequential_plant(RING + [(6, 3)], True))
        self.assertIn("concurrent_over_ring", kinds)

    # --- (f) water-boost cooldown selection ---------------------------------------
    #
    # The orthogonal-slot planting deadline is T_late = 300 - (2*CD + ceil(4/chop) + 2),
    # so the cooldown chosen by this branch moves the deadline: CD_dry = 6 gives 282,
    # CD_wet = 4 gives 286. Planting at turn 284 falls between them, which is the only
    # window where the branch's choice is observable. The global cutoff (296) is not
    # reached at 284, so nothing else can account for the verdict.

    def late_plant(self, map_rows, cell, turn, total=300):
        blocks, cmds = [], []
        for t in range(1, total + 1):
            carry = carry_of(banana=1) if t <= turn else [0] * 6
            blocks.append(turn_block([unit(0, 0, cell, carry=carry), OPP],
                                     plants=[plant("BANANA", cell)] if t > turn else []))
            cmds.append("PLANT 0 BANANA" if t == turn else "WAIT")
        return make_trace_on(map_rows, blocks, cmds)

    def test_dry_slot_planted_after_its_deadline_is_flagged(self):
        """The violation: no water, so CD_dry = 6 and the deadline is 282 — 284 is late."""
        tr = self.late_plant(MAP_ROWS, DOOR, 284)
        self.assertFalse(tr.near_water(DOOR), "precondition: the default map has no water")
        self.assertIn("orth_cutoff", self.kinds(tr))

    def test_the_same_turn_is_legal_next_to_water(self):
        """The innocent case: water adjacent, so CD_wet = 4 and the deadline moves to 286.

        Identical cell, identical turn, identical everything except one water tile. The
        PASS is itself the evidence that the water branch was taken — a dry cell planted at
        284 fails the test above."""
        tr = self.late_plant(MAP_ROWS_WATER, DOOR, 284)
        self.assertTrue(tr.near_water(DOOR), "precondition: water must be adjacent to the slot")
        self.assertEqual(verdict(td.detect_d5(tr)), ("PASS", 0))


class TestD6(unittest.TestCase):
    """D-6 opponent-favored fruit creation."""

    def plant_with_opp(self, opp_cell):
        blocks, cmds = [], []
        for t in (1, 2):
            carry = carry_of(banana=1) if t == 1 else [0] * 6
            plants = [plant("BANANA", DIAG)] if t == 2 else []
            blocks.append(turn_block(
                [unit(0, 0, DIAG, carry=carry),
                 unit(9, 1, opp_cell, hp=1, cp=1)], plants=plants))
            cmds.append("PLANT 0 BANANA" if t == 1 else "WAIT")
        return make_trace(blocks, cmds)

    def test_trigger_opponent_chopper_within_2(self):
        # opp chopper at BFS distance 2 from the plant cell: eta_opp_x = 2
        # <= 2 (D-6 clause a)
        tr = self.plant_with_opp((3, 0))
        res = td.detect_d6(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["episodes"][0]["kind"], "opp_chop_eta")

    def test_near_miss_opponent_far_away(self):
        tr = self.plant_with_opp((0, 6))   # BFS distance 7 > 2
        self.assertEqual(verdict(td.detect_d6(tr)), ("PASS", 0))


class TestD6Uncovered(unittest.TestCase):
    """G6 fixtures for the three D-6 branches the bite-test audit found with NO_FIXTURE.

    Task `20260810-guards-that-cannot-fail`, sub-item G6. Fixtures only — no predicate is
    touched.

    Branch -> mutant these are written to kill:
      (a1) arrival-order harvest race `:920` -> D6-M4 (clause deleted), D6-M3 (tie not
           conceded), D6-M6 (A7 min taken over harvest-capable own units only)
      (a3) ETA formula `ceil(bfs/speed)` `:911` -> D6-M7 (speed division dropped)
      (b)  replay ground truth `:928-941`      -> D6-M5 (clause deleted)

    **Structural note on (a1), which shapes every fixture below.** The clause is
    `opp_h <= min_own`, and `min_own` is the minimum ETA over ALL own units at the planting
    turn. The planting unit is by definition standing ON the cell it plants, so its ETA is 0
    and `min_own` is **always 0** at a PLANT event. The clause can therefore only fire when
    `opp_h == 0` — an opponent harvester sharing that exact cell. That is not a defect this
    sub-item may repair (G6 changes no predicate) but it does mean the branch is close to
    inert in ordinary play, and it is reported to the coordinator rather than papered over.
    """

    def plant_trace(self, own_line, opp_line):
        """One PLANT of a banana on DIAG at t1, with the given own/opponent units."""
        blocks = [turn_block([own_line, opp_line]),
                  turn_block([own_line, opp_line], plants=[plant("BANANA", DIAG)])]
        return make_trace(blocks, ["PLANT 0 BANANA", "WAIT"])

    def kinds(self, tr):
        return {e["kind"] for e in td.detect_d6(tr)["episodes"]}

    # --- (a1) arrival-order harvest race -------------------------------------------

    def test_arrival_tie_is_conceded_to_the_opponent(self):
        """The violation: an opponent harvester on the planting cell ties our own ETA.

        Both ETAs are 0, and the spec concedes ties to the opponent (`<=`), so planting into
        that square is flagged. This is the only geometry in which the clause can fire; see
        the class docstring."""
        tr = self.plant_trace(unit(0, 0, DIAG, carry=carry_of(banana=1)),
                              unit(9, 1, DIAG, hp=1, cp=0))
        res = td.detect_d6(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = next(e for e in res["episodes"] if e["kind"] == "opp_harvest_eta")
        self.assertEqual(ep["eta_opp_h"], 0)
        self.assertEqual(ep["min_own_eta"], 0)

    def test_opponent_harvester_one_step_away_does_not_tie(self):
        """The innocent case: the same plant with the harvester one step off the cell.
        Its ETA is 1 against our 0, so we win the race and nothing is flagged."""
        tr = self.plant_trace(unit(0, 0, DIAG, carry=carry_of(banana=1)),
                              unit(9, 1, (3, 3), hp=1, cp=0))
        self.assertNotIn("opp_harvest_eta", self.kinds(tr))

    def test_min_own_eta_is_taken_over_all_own_units_not_just_harvesters(self):
        """A7: the minimum is over EVERY own unit, harvest-capable or not.

        The planter here has `harvest_power = 0`. Under A7 it still counts, so `min_own` is 0
        and a harvester three steps away loses the race — nothing is flagged. Restricting the
        minimum to harvest-capable units would leave the set empty, make `min_own`
        unreachable, and flag this innocent plant."""
        tr = self.plant_trace(unit(0, 0, DIAG, hp=0, cp=1, carry=carry_of(banana=1)),
                              unit(9, 1, (3, 5), hp=1, cp=0))
        self.assertEqual(verdict(td.detect_d6(tr)), ("PASS", 0))

    # --- (a3) ETA formula: ceil(bfs distance / speed) --------------------------------
    #
    # Speed is what makes this branch observable: at speed 1 the ETA and the raw distance
    # coincide, so every existing fixture — all of which use speed-1 units — cannot tell the
    # formula from the bare distance. Both cases below use a speed-2 chopper.

    def test_a_fast_chopper_is_within_reach_although_its_distance_is_not(self):
        """The violation: distance 4 at speed 2 is an ETA of 2, inside the `<= 2` bound.
        Reading the raw distance instead would call it 4 and wave the plant through."""
        tr = self.plant_trace(unit(0, 0, DIAG, carry=carry_of(banana=1)),
                              unit(9, 1, (3, 6), speed=2, hp=0, cp=1))
        ep = next(e for e in td.detect_d6(tr)["episodes"] if e["kind"] == "opp_chop_eta")
        self.assertEqual(ep["eta_opp_x"], 2)

    def test_the_same_speed_at_a_greater_distance_stays_outside_the_bound(self):
        """The innocent case: distance 5 at speed 2 is an ETA of 3, outside `<= 2`.
        Same unit, same speed — only the distance moved, so the pair isolates the division."""
        tr = self.plant_trace(unit(0, 0, DIAG, carry=carry_of(banana=1)),
                              unit(9, 1, (8, 2), speed=2, hp=0, cp=1))
        self.assertEqual(verdict(td.detect_d6(tr)), ("PASS", 0))

    # --- (b) replay ground truth: the opponent actually took our fruit ----------------

    def replay_trace(self, fruits_after, carry_after):
        """We plant on DIAG and walk away; an opponent stands on the tree for two turns."""
        blocks = [
            turn_block([unit(0, 0, DIAG, carry=carry_of(banana=1)),
                        unit(9, 1, (8, 0), hp=1, cp=0)]),
            turn_block([unit(0, 0, (4, 4)), unit(9, 1, DIAG, hp=1, cp=0)],
                       plants=[plant("BANANA", DIAG, size=4, health=6, fruits=2)]),
            turn_block([unit(0, 0, (4, 4)),
                        unit(9, 1, DIAG, hp=1, cp=0,
                             carry=carry_of(banana=carry_after))],
                       plants=[plant("BANANA", DIAG, size=4, health=6,
                                     fruits=fruits_after)]),
        ]
        return make_trace(blocks, ["PLANT 0 BANANA", "WAIT", "WAIT"])

    def test_opponent_harvesting_our_tree_is_recorded(self):
        """The violation: the tree loses a fruit and that same opponent gains a banana.

        Both halves are required — a fruit count falling on its own proves nothing, since
        fruit can be lost other ways."""
        kinds = self.kinds(self.replay_trace(fruits_after=1, carry_after=1))
        self.assertIn("opp_harvested_ours", kinds)

    def test_an_opponent_standing_on_our_tree_is_not_enough(self):
        """The innocent case: same opponent, same cell, same carry increase — but the tree
        keeps its fruit, so no harvest of ours is recorded."""
        kinds = self.kinds(self.replay_trace(fruits_after=2, carry_after=1))
        self.assertNotIn("opp_harvested_ours", kinds)


class TestD7(unittest.TestCase):
    """D-7 lost harvested fruit ledger."""

    def harvest_trace(self, cell, drop_bank):
        blocks = []
        invs = [0, 0, 1 if drop_bank else 0]
        carries = [0, 1, 0]
        fruits = [1, 0, 0]
        for t in range(3):
            blocks.append(turn_block(
                [unit(0, 0, cell, carry=carry_of(banana=carries[t])), OPP],
                plants=[plant("BANANA", cell, size=4, health=6,
                              fruits=fruits[t])],
                inv0=carry_of(banana=invs[t])))
        return make_trace(blocks, ["HARVEST 0", "DROP 0", "WAIT"])

    def test_trigger_dropped_outside_door_is_lost(self):
        tr = self.harvest_trace((2, 2), drop_bank=False)
        res = td.detect_d7(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["episodes"][0]["kind"], "lost_bananas")

    def test_near_miss_banked_at_door(self):
        tr = self.harvest_trace(DOOR, drop_bank=True)
        self.assertEqual(verdict(td.detect_d7(tr)), ("PASS", 0))


class TestD7Uncovered(unittest.TestCase):
    """G6 fixtures for the four D-7 branches the bite-test audit found with NO_FIXTURE.

    Task `20260810-guards-that-cannot-fail`, sub-item G6. Fixtures only — no predicate is
    touched. Each branch gets BOTH halves of the standing rule: the exempting/limiting case
    must pass, AND a deliberately violating subject must be observed firing. A test that only
    shows the clean case cannot tell whether the branch still works.

    Branch -> mutant these are written to kill:
      (d) PLANT sink exemption `:1002`        -> D7-M5 (`planted = False`)
      (e) carried overage `age > 12` `:973`   -> D7-M1 (`> 12` becomes `> 0`)
      (f) end-of-game grace `T-6` `:1012`     -> D7-M2 (`T - 6` becomes `T - 600`)
      (g) harvest provenance `:987`           -> D7-M6 (harvest label deleted)
    """

    CELL = (2, 2)

    def carry_trace(self, turns, *, acquire_turn=1, final_verb="WAIT",
                    acquire_verb="HARVEST", at_door=False):
        """A unit that acquires one banana and then holds it for the rest of the trace.

        `acquire_verb` drives provenance; `final_verb` lets the last turn dispose of the
        banana (PLANT/DROP) so the sink branches can be exercised.
        """
        cell = DOOR if at_door else self.CELL
        blocks, commands = [], []
        for t in range(turns):
            carried = 1 if (t >= acquire_turn and t < turns - 1) else 0
            if t == turns - 1 and final_verb == "WAIT":
                carried = 1            # still holding at the end
            blocks.append(turn_block(
                [unit(0, 0, cell, carry=carry_of(banana=carried)), OPP],
                plants=[plant("BANANA", cell, size=4, health=6,
                              fruits=1 if t < acquire_turn else 0)],
                inv0=carry_of(banana=0)))
            if t == acquire_turn - 1:
                # Token counts are load-bearing in the parser: CHOP/HARVEST/DROP take
                # `VERB <uid>`, PICK/PLANT take `VERB <uid> <KIND>`, MOVE takes
                # `MOVE <uid> <x> <y>`. A line with the wrong arity parses to no command
                # at all, which silently changes what the fixture is testing.
                commands.append("PICK 0 BANANA" if acquire_verb == "PICK"
                                else f"{acquire_verb} 0")
            elif t == turns - 2 and final_verb != "WAIT":
                commands.append(final_verb)
            else:
                commands.append("WAIT")
        return make_trace(blocks, commands)

    # --- (d) PLANT sink exemption -------------------------------------------------

    def test_plant_is_a_legitimate_sink_not_a_loss(self):
        """Branch (d): carried banana disappearing via PLANT BANANA is not a loss."""
        tr = self.carry_trace(4, final_verb="PLANT 0 BANANA")
        episodes = td.detect_d7(tr)["episodes"]
        self.assertEqual([e for e in episodes if e["kind"] == "lost_bananas"], [])

    def test_plant_exemption_observed_firing_when_the_verb_is_not_plant(self):
        """The deliberate violation: same disappearance, no legitimate sink -> loss."""
        tr = self.carry_trace(4, final_verb="MOVE 0 3 3")
        episodes = td.detect_d7(tr)["episodes"]
        self.assertTrue([e for e in episodes if e["kind"] == "lost_bananas"],
                        "a banana vanishing without PLANT/DROP must be reported lost")

    # --- (e) carried overage age > 12 ---------------------------------------------

    def test_carrying_within_twelve_turns_is_not_an_overage(self):
        """Branch (e), limiting side: held for exactly 12 turns is still inside the bound."""
        tr = self.carry_trace(14, acquire_turn=1)
        overage = [e for e in td.detect_d7(tr)["episodes"]
                   if e["kind"] == "carried_overage"]
        self.assertEqual(overage, [], "age == 12 is not > 12")

    def test_carrying_beyond_twelve_turns_is_observed_firing(self):
        """The deliberate violation: one turn past the bound must report carried_overage."""
        tr = self.carry_trace(15, acquire_turn=1)
        overage = [e for e in td.detect_d7(tr)["episodes"]
                   if e["kind"] == "carried_overage"]
        self.assertTrue(overage, "age 13 > 12 must be reported")
        self.assertEqual(overage[0]["provenance"], "harvest")

    # --- (f) end-of-game grace T-6 -------------------------------------------------

    def test_harvest_inside_the_final_six_turns_is_excused_at_end(self):
        """Branch (f): a late harvest still carried at T is excused."""
        tr = self.carry_trace(8, acquire_turn=6)
        unbanked = [e for e in td.detect_d7(tr)["episodes"]
                    if e["kind"] == "unbanked_at_end"]
        self.assertEqual(unbanked, [], "harvested inside the grace window")

    def test_harvest_before_the_grace_window_is_observed_firing(self):
        """The deliberate violation: harvested early, still carried at the end."""
        tr = self.carry_trace(12, acquire_turn=1)
        unbanked = [e for e in td.detect_d7(tr)["episodes"]
                    if e["kind"] == "unbanked_at_end"]
        self.assertTrue(unbanked, "harvest outside the grace window is not excused")

    # --- (g) harvest provenance labelling ------------------------------------------

    def test_provenance_distinguishes_harvest_from_bank_pick(self):
        """Branch (g): the label is what the grace window keys on, so it must be real.

        A PICK-acquired banana is never excused by the T-6 grace, because that grace is for
        harvest only — which is exactly what makes the label load-bearing rather than
        decorative.
        """
        harvested = self.carry_trace(8, acquire_turn=6, acquire_verb="HARVEST")
        picked = self.carry_trace(8, acquire_turn=6, acquire_verb="PICK")

        self.assertEqual(
            [e for e in td.detect_d7(harvested)["episodes"]
             if e["kind"] == "unbanked_at_end"], [],
            "a late HARVEST is excused")
        picked_unbanked = [e for e in td.detect_d7(picked)["episodes"]
                           if e["kind"] == "unbanked_at_end"]
        self.assertTrue(picked_unbanked,
                        "a late PICK is NOT excused — the grace is harvest-only")
        self.assertEqual(picked_unbanked[0]["provenance"], "bank_pick")


class TestD8(unittest.TestCase):
    """D-8 diagonal-mother chop."""

    def plant_then_chop(self, cell):
        blocks, cmds = [], []
        for t in (1, 2, 3):
            carry = carry_of(banana=1) if t == 1 else [0] * 6
            plants = [plant("BANANA", cell, size=2, health=4)] if t > 1 else []
            blocks.append(turn_block([unit(0, 0, cell, carry=carry), OPP],
                                     plants=plants))
        cmds = ["PLANT 0 BANANA", "WAIT", "CHOP 0"]
        return make_trace(blocks, cmds)

    def test_trigger_chop_diagonal_mother(self):
        tr = self.plant_then_chop(DIAG)
        res = td.detect_d8(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["kind"], "diag_mother_chop")
        self.assertEqual(ep["cell"], list(DIAG))
        self.assertEqual(ep["turn_start"], 3)

    def test_near_miss_orthogonal_wood_slot_chop_is_legal(self):
        # orth(tent) slots are the wood-conversion channel (I-4): not D-8
        tr = self.plant_then_chop(DOOR)
        self.assertEqual(verdict(td.detect_d8(tr)), ("PASS", 0))


class TestD8Amended(unittest.TestCase):
    """D-8 with the CONVERSION_RACE_ORACLE exemption (spec Revision
    2026-08-05): an own-chop of an own-planted diagonal mother is exempt IFF
    (a) I-7 ownership had flipped to lost at or before the chop-start turn
    (committed-harvester ETA, ties conceded) AND (b) CONVERSION_RACE_ORACLE
    at the chop-start state reports feasible — the absolute final-chop turn
    is strictly before the opponent's absolute earliest EXECUTABLE HARVEST
    turn (travel AND ripeness; arrival alone is not loss).
    """

    # Timeline builder: resident u0 plants the DIAG mother at t1 while ON
    # it, then per-turn (res_cell, opp_cell, plant_row_or_None, command).
    def flip_trace(self, steps):
        blocks = [turn_block(
            [unit(0, 0, DIAG, carry=carry_of(banana=1)),
             unit(9, 1, (3, 6), hp=1, cp=0)])]
        cmds = ["PLANT 0 BANANA"]
        for res_cell, opp_cell, plant_row, cmd in steps:
            plants = [plant_row] if plant_row else []
            blocks.append(turn_block(
                [unit(0, 0, res_cell), unit(9, 1, opp_cell, hp=1, cp=0)],
                plants=plants))
            cmds.append(cmd)
        return make_trace(blocks, cmds)

    def test_oracle_matches_review_counterexample(self):
        # Terminal failure 1 boundary (host review 2026-08-05): size 2,
        # health 4, cooldown 1, chop 1 -> the tree grows after chop 1 and
        # needs FIVE exact chops; the static arithmetic claims four.
        self.assertEqual(td.banana_exact_chop_turns(2, 4, 1, 1), 5)
        self.assertEqual(td.ceil_div(4, 1), 4)
        # No growth interference: cooldown outlasts the chop sequence.
        self.assertEqual(td.banana_exact_chop_turns(2, 4, 5, 1), 4)
        # Growth-only prediction: cd 1 grows next turn (+1 size/health).
        self.assertEqual(td.banana_predict_tree(2, 4, 0, 1, 1), (3, 5, 0, 6))

    def test_exempt_flip_then_feasible_conversion(self):
        # t2: resident at (1,2) (eta 2), opponent at (3,4) (eta 2): I-7 tie
        # -> ownership flips (lost). Opponent then departs; at chop-start t4
        # the plant is size 1 health 3 cd 3 (exact chops 3): oracle
        # completion_turn 4+3-1 = 6, opponent_harvest_turn max(arrival 8,
        # first fruit 25) = 25 -> feasible, exempt.
        p = lambda h, cd: plant("BANANA", DIAG, size=1, health=h, cooldown=cd)
        tr = self.flip_trace([
            ((1, 2), (3, 4), p(3, 5), "WAIT"),          # t2: flip (2 >= 2)
            ((2, 2), (3, 5), p(3, 4), "MOVE 0 3 2"),    # t3: opp departing
            (DIAG,   (3, 6), p(3, 3), "CHOP 0"),        # t4: chop-start
            (DIAG,   (3, 6), p(2, 2), "CHOP 0"),        # t5
            (DIAG,   (3, 6), p(1, 1), "CHOP 0"),        # t6
            (DIAG,   (3, 6), None,    "WAIT"),          # t7: felled
        ])
        self.assertEqual(verdict(td.detect_d8(tr)), ("PASS", 0))

    def test_flagged_discretionary_owned_chop(self):
        # Opponent harvester stays far (eta >= 4 always): ownership never
        # flips, so the chop of the own-planted diagonal mother is the
        # forbidden discretionary case (I-14 unchanged while owned).
        p = lambda h, cd: plant("BANANA", DIAG, size=1, health=h, cooldown=cd)
        tr = self.flip_trace([
            (DIAG, (3, 6), p(3, 5), "WAIT"),
            (DIAG, (3, 6), p(3, 4), "CHOP 0"),
            (DIAG, (3, 6), p(2, 3), "CHOP 0"),
            (DIAG, (3, 6), p(1, 2), "CHOP 0"),
            (DIAG, (3, 6), None,    "WAIT"),
        ])
        res = td.detect_d8(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["count"], 3)
        self.assertEqual(res["episodes"][0]["reason"], "discretionary_owned")
        self.assertEqual(res["episodes"][0]["turn_start"], 3)

    def test_flagged_flip_but_infeasible_chop(self):
        # Re-based on CONVERSION_RACE_ORACLE (spec Revision 2026-08-05,
        # documented expected-value change 1): the old scenario's doom was
        # arrival-only (unripe size-1 mother, opponent adjacent), which the
        # oracle correctly calls FEASIBLE (first fruit ~21 turns out).
        # Genuinely infeasible geometry: NEAR-RIPE size-4 mother (fruits 0,
        # cd 1 at chop-start t4 -> first executable harvest turn 5 with the
        # opponent adjacent) while the conversion needs 3 chops ->
        # completion_turn 6 >= opponent_harvest_turn 5 -> race lost ->
        # flagged (I-10a says abandon, not convert).
        p = lambda h, cd, f=0: plant("BANANA", DIAG, size=4, health=h,
                                     fruits=f, cooldown=cd)
        tr = self.flip_trace([
            ((1, 2), (3, 4), p(3, 3), "WAIT"),          # t2: flip (2 >= 2)
            ((2, 2), (3, 3), p(3, 2), "MOVE 0 3 2"),    # t3: opp closing
            (DIAG,   (3, 3), p(3, 1), "CHOP 0"),        # t4: chop-start
            (DIAG,   (3, 3), p(2, 6, 1), "CHOP 0"),     # t5: fruit ripened
            (DIAG,   (3, 3), p(1, 5, 1), "CHOP 0"),     # t6
            (DIAG,   (3, 3), None,    "WAIT"),          # t7
        ])
        res = td.detect_d8(tr)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["count"], 3)
        ep = res["episodes"][0]
        self.assertEqual(ep["reason"], "flip_but_infeasible")
        self.assertEqual(ep["flip_turn"], 2)
        self.assertEqual(ep["exact_chop_turns"], 3)
        self.assertEqual(ep["eta_opp_at_chop_start"], 1)
        self.assertEqual(ep["completion_turn"], 6)
        self.assertEqual(ep["opponent_harvest_turn"], 5)

    def test_exempt_arrival_is_not_loss(self):
        # The discriminating direction of the unification: opponent ADJACENT
        # at chop start (old arrival-only D-8 would flag), but the mother is
        # young and unripe -> earliest executable harvest is the far-future
        # first-fruit turn -> oracle feasible -> exempt.
        p = lambda h, cd: plant("BANANA", DIAG, size=1, health=h, cooldown=cd)
        tr = self.flip_trace([
            ((1, 2), (3, 4), p(3, 5), "WAIT"),          # t2: flip (2 >= 2)
            ((2, 2), (3, 3), p(3, 4), "MOVE 0 3 2"),    # t3: opp closing
            (DIAG,   (2, 2), p(3, 3), "CHOP 0"),        # t4: eta_opp 1
            (DIAG,   (2, 2), p(2, 2), "CHOP 0"),        # t5
            (DIAG,   (2, 2), p(1, 1), "CHOP 0"),        # t6
            (DIAG,   (2, 2), None,    "WAIT"),          # t7
        ])
        self.assertEqual(verdict(td.detect_d8(tr)), ("PASS", 0))


class TestD8Uncovered(unittest.TestCase):
    """G6 fixtures for the D-8 branches the bite-test audit found with NO_FIXTURE.

    Task `20260810-guards-that-cannot-fail`, sub-item G6. Fixtures only — no predicate is
    touched. Each branch gets BOTH halves of the standing rule: the limiting case that must
    stay silent, AND a deliberately violating subject observed firing.

    Branch -> mutant these are written to kill:
      (f) oracle growth-aware chop count -> D8-M9  (exact_chop_turns -> ceil(health/chop))
      (g) oracle strict-tie `<`          -> D8-M3  (`<` becomes `<=`)
      (h) health-decrease confirmation   -> D8-M11 (`health_drop = True`)

    Branch (b) `plant kind == BANANA` is NOT fixtured here and D8-M8 is NOT killed. It is an
    equivalent mutant; see `test_alive_set_already_guarantees_the_plant_kind` below for the
    demonstration and the audit note for the disposition.

    Every exemption below requires ownership to have FLIPPED first — `exempt = lost and
    race_won`. Without the flip, `lost` is False and the chop is flagged as
    `discretionary_owned` whatever the oracle says, so an oracle mutant would survive: the
    fixture would be testing the ownership clause instead of the clause it names.
    """

    # Resident plants the DIAG mother at t1 while standing on it, then per-turn
    # (resident_cell, opponent_cell, plant_row_or_None, command). Mirrors TestD8Amended.
    def flip_trace(self, steps):
        blocks = [turn_block(
            [unit(0, 0, DIAG, carry=carry_of(banana=1)),
             unit(9, 1, (3, 6), hp=1, cp=0)])]
        cmds = ["PLANT 0 BANANA"]
        for res_cell, opp_cell, plant_row, cmd in steps:
            blocks.append(turn_block(
                [unit(0, 0, res_cell), unit(9, 1, opp_cell, hp=1, cp=0)],
                plants=[plant_row] if plant_row else []))
            cmds.append(cmd)
        return make_trace(blocks, cmds)

    # --- (g) strict tie: completion_turn < opponent_harvest_turn ---------------------
    #
    # The mother is size 4 / health 3 / cd 1 with the resident standing on it at chop-start
    # t4: eta_res 0, exact chops 3, so completion_turn = 4 + 0 + 3 - 1 = 6. The opponent sits
    # at BFS distance 2 and the mother is within 2 turns of fruit, so
    # opponent_harvest_turn = 6 as well. A dead heat is NOT a win: the spec requires the final
    # chop STRICTLY before the opponent's earliest executable harvest.

    TIE_PLANT = dict(size=4, cooldown=1)

    def tie_trace(self, opp_cell):
        p = lambda h: plant("BANANA", DIAG, health=h, **self.TIE_PLANT)
        return self.flip_trace([
            ((1, 2), (3, 4), p(3), "WAIT"),          # t2: flip, eta_res 2 == eta_opp 2
            ((2, 2), opp_cell, p(3), "MOVE 0 3 2"),  # t3
            (DIAG,   opp_cell, p(3), "CHOP 0"),      # t4: chop-start
            (DIAG,   opp_cell, p(2), "CHOP 0"),      # t5
            (DIAG,   opp_cell, p(1), "CHOP 0"),      # t6
            (DIAG,   opp_cell, None, "WAIT"),        # t7
        ])

    def test_tie_on_the_conversion_race_is_flagged_not_exempt(self):
        """Branch (g), the violation: completion_turn == opponent_harvest_turn == 6."""
        res = td.detect_d8(self.tie_trace((3, 4)))
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["reason"], "flip_but_infeasible")
        self.assertEqual(ep["completion_turn"], 6)
        self.assertEqual(ep["opponent_harvest_turn"], 6)
        self.assertEqual(ep["completion_turn"], ep["opponent_harvest_turn"])

    def test_one_turn_of_margin_is_exempt(self):
        """Branch (g), the silent half: the SAME geometry with the opponent one step
        further is completion 6 < harvest 7 — a real win, and exempt. The pair localises
        the boundary to the tie itself rather than to the surrounding scenario."""
        self.assertEqual(verdict(td.detect_d8(self.tie_trace((3, 5)))), ("PASS", 0))

    # --- (f) oracle growth-aware chop count ------------------------------------------
    #
    # size 2 / health 7 / fruits 1, resident on the cell, opponent at BFS distance 7.
    # Growth-aware: the tree grows mid-sequence, so it takes NINE chops, not
    # ceil(7/1) = 7 -> completion 12 against an opponent harvest of 11 -> race lost.
    # The static arithmetic would claim 7 chops, completion 10, and wrongly exempt it.
    # The margin is deliberately 2 turns, so this fixture does NOT also depend on the
    # tie semantics of branch (g) — under the `<=` mutant 12 <= 11 is still false.

    def growth_trace(self, cooldown):
        p = lambda h: plant("BANANA", DIAG, size=2, health=h, fruits=1, cooldown=cooldown)
        return self.flip_trace([
            ((1, 2), (3, 4), p(7), "WAIT"),          # t2: flip
            ((2, 2), (6, 1), p(7), "MOVE 0 3 2"),    # t3: opponent withdrawing
            (DIAG,   (8, 0), p(7), "CHOP 0"),        # t4: chop-start, distance 7
            (DIAG,   (8, 0), p(6), "WAIT"),
        ])

    def test_growth_during_the_chop_sequence_loses_the_race(self):
        """Branch (f), the violation: cooldown 1 lets the tree grow mid-sequence."""
        res = td.detect_d8(self.growth_trace(cooldown=1))
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["reason"], "flip_but_infeasible")
        self.assertEqual(ep["exact_chop_turns"], 9)       # NOT ceil(7/1) = 7
        self.assertEqual(ep["completion_turn"], 12)
        self.assertEqual(ep["opponent_harvest_turn"], 11)

    def test_without_growth_interference_the_same_race_is_won(self):
        """Branch (f), the silent half: identical geometry, cooldown 7 so the tree cannot
        grow before the sequence ends. Then exact == static == 7, completion 10 < 11, and
        the conversion is exempt. The only thing that changed is the growth."""
        self.assertEqual(verdict(td.detect_d8(self.growth_trace(cooldown=7))), ("PASS", 0))

    # --- (h) health-decrease confirmation ---------------------------------------------
    #
    # `health_decreased` records whether the chop actually landed. It is a reporting field,
    # so nothing downstream forces it to be right — which is exactly why it needs a fixture.

    def health_trace(self, health_after):
        p = lambda h: plant("BANANA", DIAG, size=1, health=h, cooldown=5)
        return self.flip_trace([
            (DIAG, (3, 6), p(3), "WAIT"),
            (DIAG, (3, 6), p(3), "CHOP 0"),          # t3: the chop under test
            (DIAG, (3, 6), p(health_after), "WAIT"),  # t4: state after it
        ])

    def test_health_decrease_is_reported_false_when_the_chop_does_not_land(self):
        """Branch (h), the discriminating case: health unchanged at t+1 -> False.

        A mutant that hard-codes the field True still produces the right episode, the right
        count and the right reason; only this field distinguishes it."""
        res = td.detect_d8(self.health_trace(health_after=3))
        self.assertEqual(res["verdict"], "FAIL")
        self.assertIs(res["episodes"][0]["health_decreased"], False)

    def test_health_decrease_is_reported_true_when_the_chop_lands(self):
        """Branch (h), the other half: health drops by the chop power -> True."""
        res = td.detect_d8(self.health_trace(health_after=2))
        self.assertIs(res["episodes"][0]["health_decreased"], True)

    # --- (b) plant kind == BANANA: equivalent mutant, documented not pinned -------------

    def test_alive_set_already_guarantees_the_plant_kind(self):
        """Branch (b) `p.kind == "BANANA"` (`:1115`) cannot be observed failing.

        `detect_d8` only reaches that test when `c in alive_per_turn[t]`, and
        `own_banana_history` builds that set from the SAME `state(t)` while filtering
        `plant_at(c).kind == "BANANA"`. So the kind test is true whenever it is evaluated and
        D8-M8 (which deletes it) is an EQUIVALENT MUTANT — no fixture can kill it, and its
        survival is not evidence of weak coverage.

        This test pins the coupling that makes it equivalent rather than pretending to pin the
        branch: if `own_banana_history` ever stops filtering on kind, the redundancy
        disappears, the branch becomes load-bearing, and this test fails to say so.
        """
        blocks, rows = [], {
            1: [plant("BANANA", DIAG, size=2, health=4)],
            2: [plant("BANANA", DIAG, size=2, health=4)],
            3: [plant("WOOD", DIAG, size=2, health=4)],
            4: [plant("WOOD", DIAG, size=2, health=4)],
        }
        for t in (1, 2, 3, 4):
            carry = carry_of(banana=1) if t == 1 else [0] * 6
            blocks.append(turn_block([unit(0, 0, DIAG, carry=carry), OPP], plants=rows[t]))
        tr = make_trace(blocks, ["PLANT 0 BANANA", "WAIT", "CHOP 0", "WAIT"])

        _events, alive = tr.own_banana_history()
        for t in range(1, tr.T + 1):
            p = tr.state(t).plant_at(DIAG)
            if DIAG in alive[t]:
                self.assertIsNotNone(p)
                self.assertEqual(p.kind, "BANANA",
                                 f"t{t}: a cell in the alive set held a non-banana plant, so "
                                 f"the kind test at :1115 is no longer redundant")
        # The CHOP at t3 targets a WOOD plant on a diagonal cell: the cell has already left
        # the alive set, so the kind test is never reached and no episode is produced.
        self.assertEqual(tr.state(3).plant_at(DIAG).kind, "WOOD")
        self.assertNotIn(DIAG, alive[3])
        self.assertEqual(verdict(td.detect_d8(tr)), ("PASS", 0))


class TestD9(unittest.TestCase):
    """D-9 second-worker TRAIN displacement (single-trace clause)."""

    def test_trigger_banana_command_before_train_single_worker(self):
        blocks = [
            turn_block([unit(0, 0, DOOR)], inv0=carry_of(banana=2)),
            turn_block([unit(0, 0, DOOR, carry=carry_of(banana=1))],
                       inv0=carry_of(banana=1)),
        ]
        tr = make_trace(blocks, ["PICK 0 BANANA", "WAIT"])
        res = td.detect_d9(tr)
        self.assertEqual(res["verdict"], "FAIL")
        ep = res["episodes"][0]
        self.assertEqual(ep["kind"], "banana_before_train")
        self.assertEqual(ep["turn_start"], 1)

    # ---- pinning tests for the branch the owner made binding 2026-08-10 ----
    # "No banana manipulation before training the second troll" is a STRICT
    # rule with threshold 0, and it is policed by this branch alone. Three
    # mutations of this branch's own implementation survived the suite
    # (D9-M1, D9-M2, D9-M3), so the rule was enforced by a detector nobody had
    # shown could tell right from wrong. Each test below is a NEGATIVE case:
    # the detector must stay silent, and each corresponding mutation makes it
    # speak. Verified by applying each manifest mutation and confirming the
    # fixture flips to FAIL.

    def test_no_episode_when_more_than_one_own_unit_holds_a_banana(self):
        """Kills D9-M1 (`|own units| == 1` guard deleted).

        The rule is about the FIRST worker: once a second troll exists there is
        nothing left to displace. Without the guard the detector would flag
        banana handling for the whole game.
        """
        blocks = [
            turn_block([unit(0, 0, DOOR), unit(2, 0, (4, 4))],
                       inv0=carry_of(banana=2)),
            turn_block([unit(0, 0, DOOR, carry=carry_of(banana=1)),
                        unit(2, 0, (4, 4))], inv0=carry_of(banana=1)),
        ]
        tr = make_trace(blocks, ["PICK 0 BANANA;WAIT", "WAIT"])
        res = td.detect_d9(tr)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["episodes"], [])

    def test_no_episode_for_a_non_banana_resource_before_train(self):
        """Kills D9-M2 (banana restriction widened to any resource argument).

        The owner's rule names bananas. A single worker picking WOOD before
        TRAIN violates nothing, and a detector that flagged it would make the
        strict rule unmeetable rather than strict.
        """
        blocks = [
            turn_block([unit(0, 0, DOOR)], inv0=carry_of(wood=2)),
            turn_block([unit(0, 0, DOOR, carry=carry_of(wood=1))],
                       inv0=carry_of(wood=1)),
        ]
        tr = make_trace(blocks, ["PICK 0 WOOD", "WAIT"])
        res = td.detect_d9(tr)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["episodes"], [])

    def test_no_episode_when_the_banana_command_shares_the_train_turn(self):
        """Kills D9-M3 (ordering boundary `t >= first_train` -> `t > first_train`).

        "Before TRAIN" excludes the TRAIN turn itself: a banana command issued
        on the same turn the second troll is trained is not *before* it. The
        mutation shifts that boundary by one turn, which is the single most
        likely way for this branch to be silently wrong -- and exactly the
        games-vs-episodes class of boundary error this programme keeps hitting.
        """
        blocks = [
            turn_block([unit(0, 0, DOOR)], inv0=carry_of(banana=2)),
            turn_block([unit(0, 0, DOOR, carry=carry_of(banana=1)),
                        unit(2, 0, (4, 4))], inv0=carry_of(banana=1)),
        ]
        tr = make_trace(blocks, ["TRAIN 1 1 1 1;PICK 0 BANANA", "WAIT"])
        res = td.detect_d9(tr)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["episodes"], [])

    def test_near_miss_train_issued_first(self):
        blocks = [
            turn_block([unit(0, 0, DOOR)], inv0=carry_of(banana=2)),
            turn_block([unit(0, 0, DOOR), unit(2, 0, TENT and (4, 4))],
                       inv0=carry_of(banana=2)),
            turn_block([unit(0, 0, DOOR, carry=carry_of(banana=1)),
                        unit(2, 0, (4, 4))],
                       inv0=carry_of(banana=1)),
        ]
        tr = make_trace(blocks,
                        ["TRAIN 1 1 1 1;WAIT", "WAIT", "PICK 0 BANANA"])
        self.assertEqual(verdict(td.detect_d9(tr)), ("PASS", 0))


if __name__ == "__main__":
    unittest.main()
