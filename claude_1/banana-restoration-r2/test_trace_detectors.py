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
