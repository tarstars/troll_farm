#!/usr/bin/env python3
"""Repaired independent probes for the detector bite-test audit (revision r2).

Each class here repairs one probe or claim that review
``chatgpt_1/detector-bitetest-audit-review-2026-08-08.md`` rejected:

  TestD4StallClaim   BAR-6  the "single stall is absent" statement
  TestD6ExactState   BAR-2  oracle checks bound to the exact fixture state
  TestD3Probe        BAR-5  referee-predicted next_cell vs realized landing
  TestD5PayoffOracle BAR-7  first_fruit_delay is not a payoff oracle

METHOD (recorded, not asserted).  Every assertion below was FIRST written to
state the 2026-08-08 audit's original claim and run in that form; 9 of the 10
checks failed.  That transcript is committed verbatim at
``results/probes-red-2026-08-09.txt``
(sha256 aeab241b14bd18431d3879368c451c4f7dc91a72d7e0970ce44bc01dc3fe5448).
The assertions were then replaced by the measured values, each with the
retracted claim retained in a comment.  Nothing here modifies
``trace_detectors.py`` or ``test_trace_detectors.py``; the fixtures are
rebuilt from the committed helper definitions so the probes act on the exact
states the detectors saw.

Run: python3 -m unittest probes
     python3 probes.py --json results/probe-results.json
"""

from __future__ import annotations

import unittest

import conversion_race_oracle as cro
import trace_detectors as td

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


# --- exact mirrors of the committed fixture helpers ------------------------
# Copied verbatim from test_trace_detectors.py so the probes act on the EXACT
# committed fixture states (review BAR-2). The defaults matter: ``plant``
# defaults to cooldown=4.

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
    return td.build_trace("\n".join(body) + "\n",
                          "\n".join(command_lines) + "\n")


def carry_of(**kw):
    c = [0] * 6
    for name, v in kw.items():
        c[td.ITEM_NAMES.index(name.upper())] = v
    return c


OPP = unit(9, 1, (8, 0))


def d6_plant_with_opp(opp_cell):
    """Byte-equivalent rebuild of TestD6.plant_with_opp."""
    blocks, cmds = [], []
    for t in (1, 2):
        carry = carry_of(banana=1) if t == 1 else [0] * 6
        plants = [plant("BANANA", DIAG)] if t == 2 else []
        blocks.append(turn_block(
            [unit(0, 0, DIAG, carry=carry),
             unit(9, 1, opp_cell, hp=1, cp=1)], plants=plants))
        cmds.append("PLANT 0 BANANA" if t == 1 else "WAIT")
    return make_trace(blocks, cmds)


def d4_wood_trace(positions, cmds, wood=1, drop_turn=None):
    """Byte-equivalent rebuild of TestD4.wood_trace."""
    blocks = []
    for t, pos in enumerate(positions, start=1):
        w = wood if (drop_turn is None or t <= drop_turn) else 0
        inv0 = carry_of(wood=1) if (drop_turn is not None
                                    and t > drop_turn) else [0] * 6
        blocks.append(turn_block(
            [unit(0, 0, pos, carry=carry_of(wood=w)), OPP], inv0=inv0))
    return make_trace(blocks, cmds)


def d3_two_movers(dests2):
    """Byte-equivalent rebuild of TestD3.two_movers."""
    blocks, cmds = [], []
    p0 = [(1, 1), (2, 1), (3, 1)]
    p2 = [(1, 5), (2, 5), (3, 5)]
    for t in range(3):
        blocks.append(turn_block([unit(0, 0, p0[t]), unit(2, 0, p2[t]), OPP]))
        d0, d2 = dests2[t]
        cmds.append("MOVE 0 %d %d;MOVE 2 %d %d" % (d0 + d2))
    return make_trace(blocks, cmds)


# ---------------------------------------------------------------------------
# Referee movement mirror (for the repaired D-3 probe)
#
# Mirror of rust/src/game/engine.rs::next_cell (:98-144) --- the authoritative
# engine, byte-sacred, read only. Reproduced here so the probe can compute the
# REFEREE-PREDICTED landing cell instead of comparing the raw MOVE argument to
# the realized position.
# ---------------------------------------------------------------------------

def _bfs(walkable, sources):
    return cro.bfs_distances(walkable, sources)


def referee_next_cell(walkable, current, target, speed):
    """engine.rs::next_cell. Ties among equally-good in-range cells are broken
    by the lexicographically smallest cell (engine.rs:137-143)."""
    walkable = set(walkable)
    src = _bfs(walkable, [current])
    d = src.get(target)
    if d is not None and d <= speed:
        return target
    if target not in src:
        if not src:
            return current
        best = min(abs(target[0] - c[0]) + abs(target[1] - c[1])
                   for c in src)
        goals = [c for c in src
                 if abs(target[0] - c[0]) + abs(target[1] - c[1]) == best]
        tdist = _bfs(walkable, goals)
    else:
        tdist = _bfs(walkable, [target])
    in_range = [c for c, dd in src.items() if dd <= speed and c in tdist]
    if not in_range:
        return current
    best_dist = min(tdist[c] for c in in_range)
    return min(c for c in in_range if tdist[c] == best_dist)


# ===========================================================================
# D-4 --- the "single stall is absent" claim  (review BAR-6)
# ===========================================================================

def d4_door_distance_transitions(tr, uid=0):
    """(turn, d0, d1, relation) for every observable transition of ``uid``."""
    out = []
    for t in range(1, tr.T):
        u0, u1 = tr.unit(uid, t), tr.unit(uid, t + 1)
        if u0 is None or u1 is None:
            continue
        d0 = tr.door_dist.get(u0.cell)
        d1 = tr.door_dist.get(u1.cell)
        if d0 is None or d1 is None:
            continue
        rel = "stall" if d1 == d0 else ("retreat" if d1 > d0 else "progress")
        out.append((t, d0, d1, rel))
    return out


NEAR_MISS_D4 = d4_wood_trace(
    [(2, 2), (2, 2), (3, 2), (4, 2), (4, 2)],
    ["MOVE 0 4 2", "MOVE 0 4 2", "MOVE 0 4 2", "DROP 0", "WAIT"],
    drop_turn=4)

TRIGGER_D4 = d4_wood_trace(
    [(2, 2), (1, 2), (0, 2), (0, 2)],
    ["MOVE 0 4 2", "MOVE 0 0 2", "WAIT", "WAIT"])


def d4_committed_transitions(tr, uid=0):
    """The subset of transitions that lie INSIDE a D-4 wood-commitment
    interval, mirroring the commitment start/end logic of
    ``trace_detectors.detect_d4`` (:769-826) without re-using it."""
    out = []
    committed = False
    for t in range(1, tr.T + 1):
        u = tr.unit(uid, t)
        if u is None:
            committed = False
            continue
        if committed and (u.total_carried() == 0
                          or tr.door_dist.get(u.cell) is None):
            committed = False
        cmd = tr.cmd_of(uid, t)
        if not committed and u.carry[td.WOOD] > 0:
            if (u.free_capacity() == 0
                    or (cmd is not None and cmd.verb == "MOVE"
                        and cmd.args[0] in tr.doors)
                    or (cmd is not None and cmd.verb == "DROP"
                        and u.cell in tr.doors)):
                committed = True
        if not committed:
            continue
        executed_drop = (cmd is not None and cmd.verb == "DROP"
                         and u.cell in tr.doors)
        if t + 1 > tr.T:
            committed = False
            continue
        nu = tr.unit(uid, t + 1)
        if executed_drop or nu is None or nu.total_carried() == 0:
            committed = False
            continue
        d0 = tr.door_dist.get(u.cell)
        d1 = tr.door_dist.get(nu.cell)
        if d0 is None or d1 is None:
            committed = False
            continue
        rel = "stall" if d1 == d0 else ("retreat" if d1 > d0 else "progress")
        out.append((t, d0, d1, rel))
    return out


class TestD4StallClaim(unittest.TestCase):
    """BAR-6.  RETRACTED CLAIM (audit 2026-08-08 sec. 2, D-4): "in both
    trigger and near-miss the distance strictly increases rather than merely
    stalling -- so the very distinction the near-miss is named after ('single
    stall') is not actually present in the data".  That statement is FALSE."""

    def test_near_miss_contains_exactly_one_committed_stall(self):
        rels = [r for (_, _, _, r) in
                d4_committed_transitions(NEAR_MISS_D4)]
        # door_dist sequence 2,2,1,0 inside the commitment interval:
        # transition 1 is a genuine equality stall at door_dist 2.
        self.assertEqual(rels.count("stall"), 1)
        self.assertEqual(rels, ["stall", "progress", "progress"])

    def test_near_miss_raw_scan_shows_a_second_post_drop_stall(self):
        # The raw geometric scan finds two equalities; the second (turn 4,
        # 0 -> 0) is AFTER the executed DROP at a door, so it is outside the
        # commitment interval and D-4 never sees it.
        rels = [r for (_, _, _, r) in
                d4_door_distance_transitions(NEAR_MISS_D4)]
        self.assertEqual(rels, ["stall", "progress", "progress", "stall"])

    def test_trigger_violating_run_is_two_strict_retreats(self):
        # The no_progress trigger reaches nd_run == 2 on two strict RETREATS
        # (2->3, 3->4); its single equality (4->4) comes after the episode has
        # already been emitted. This -- not the absence of a stall in the
        # near-miss -- is why D4-M3 (`d1 >= d0` -> `d1 > d0`) survives.
        rels = [r for (_, _, _, r) in d4_committed_transitions(TRIGGER_D4)]
        self.assertEqual(rels[:2], ["retreat", "retreat"])
        self.assertEqual(rels.count("stall"), 1)

    def test_no_fixture_has_two_consecutive_equality_transitions(self):
        # The surviving-mutant explanation that DOES hold: under both `>=` and
        # `>` every committed fixture stays below the violation horizon,
        # because no fixture contains two CONSECUTIVE equality transitions.
        for tr in (NEAR_MISS_D4, TRIGGER_D4):
            rels = [r for (_, _, _, r) in d4_committed_transitions(tr)]
            pairs = list(zip(rels, rels[1:]))
            self.assertNotIn(("stall", "stall"), pairs)


# ===========================================================================
# D-6 --- oracle checks bound to the EXACT serialized fixture state
#         (review BAR-2)
# ===========================================================================

def d6_serialized_state(tr, turn):
    """The exact ``Trace.state(turn)`` plant and unit tuples."""
    st = tr.state(turn)
    return {
        "turn": turn,
        "plants": sorted((p.kind, p.cell, p.size, p.health, p.fruits,
                          p.cooldown) for p in st.plants),
        "units": sorted((u.id, u.player, u.cell, u.speed, u.capacity,
                         u.harvest_power, u.chop_power, tuple(u.carry))
                        for u in st.units),
    }


def d6_founding_oracle_on_exact_state(tr, plant_turn=1):
    """Feed the exact post-PLANT serialized state at ``plant_turn + 1`` into
    FOUNDING_SAFETY_ORACLE. The oracle's anchor is t+1 by construction
    (conversion_race_oracle.py:391-403), which is exactly the trace state in
    which the fixture's sapling first exists, so no state is reconstructed."""
    anchor = plant_turn + 1
    st = tr.state(anchor)
    p = st.plant_at(DIAG)
    res = st.unit(0)
    return cro.founding_safety_oracle(
        plant_turn=plant_turn,
        walkable=set(tr.smap.walkable),
        ring_cell=DIAG,
        sapling=(p.size, p.health, p.fruits, p.cooldown),
        resident_speed=res.speed,
        resident_chop_power=res.chop_power,
        opponents=[(u.cell, u.speed, u.harvest_power, u.chop_power)
                   for u in st.opp_units()],
        near_water=tr.near_water(DIAG))


D6_TRIGGER = d6_plant_with_opp((3, 0))
D6_NEAR_MISS = d6_plant_with_opp((0, 6))


class TestD6ExactState(unittest.TestCase):
    """BAR-2.  Every number below is bound to the exact serialized
    ``Trace.state(2)`` of the committed D-6 fixtures.  The 2026-08-08 audit
    instead hand-reconstructed a nearby state with ``cooldown = CD_dry = 6``;
    the committed helper ``plant()`` defaults to ``cooldown=4`` and
    ``TestD6.plant_with_opp`` does not override it, so every turn the audit
    published was computed on a state ``detect_d6`` never saw."""

    def test_fixture_sapling_is_cooldown_4_not_6(self):
        # RETRACTED: "the referee's post-PLANT banana sapling is
        # (size 1, health 3, fruits 0, cooldown CD_dry = 6)".
        p = D6_NEAR_MISS.state(2).plant_at(DIAG)
        self.assertEqual((p.size, p.health, p.fruits, p.cooldown),
                         (1, 3, 0, 4))
        self.assertEqual(D6_TRIGGER.state(2).plant_at(DIAG).cooldown, 4)

    def test_serialized_states_are_identical_apart_from_the_opponent_cell(self):
        a = d6_serialized_state(D6_TRIGGER, 2)
        b = d6_serialized_state(D6_NEAR_MISS, 2)
        self.assertEqual(a["plants"], b["plants"])
        self.assertEqual([u for u in a["units"] if u[1] == 0],
                         [u for u in b["units"] if u[1] == 0])
        self.assertEqual([u[2] for u in a["units"] if u[1] == 1], [(3, 0)])
        self.assertEqual([u[2] for u in b["units"] if u[1] == 1], [(0, 6)])

    def test_first_fruit_delay_on_the_exact_sapling(self):
        # RETRACTED: first_fruit_delay(1, 3, 0, 6) = 24.
        p = D6_NEAR_MISS.state(2).plant_at(DIAG)
        self.assertEqual(
            cro.first_fruit_delay(p.size, p.health, p.fruits, p.cooldown), 22)
        # the audit's hypothetical cooldown-6 sapling would have given 24
        self.assertEqual(cro.first_fruit_delay(1, 3, 0, 6), 24)

    def test_trigger_oracle_turns_on_the_exact_state(self):
        # RETRACTED: our_h=26 opp_h=26 opp_destroy=6.
        out = d6_founding_oracle_on_exact_state(D6_TRIGGER)
        self.assertEqual(out["anchor_turn"], 2)
        self.assertEqual((out["our_harvest_turn"], out["opp_harvest_turn"],
                          out["opp_destroy_turn"]), (24, 24, 7))

    def test_near_miss_oracle_turns_on_the_exact_state(self):
        # RETRACTED: our_h=26 opp_h=26 opp_destroy=12.
        out = d6_founding_oracle_on_exact_state(D6_NEAR_MISS)
        self.assertEqual(out["anchor_turn"], 2)
        self.assertEqual((out["our_harvest_turn"], out["opp_harvest_turn"],
                          out["opp_destroy_turn"]), (24, 24, 13))

    def test_both_geometries_are_founding_unsafe(self):
        # The qualitative conclusion that DOES survive the state correction:
        # on this fixture map ripeness dominates travel for every opponent
        # cell, so our and the opponent's executable-harvest turns TIE at 24
        # and the tie is conceded; the chopper additionally fells the sapling
        # (turn 7 / turn 13) long before turn 24.
        for tr in (D6_TRIGGER, D6_NEAR_MISS):
            out = d6_founding_oracle_on_exact_state(tr)
            self.assertFalse(out["feasible_found"])
            self.assertEqual(out["our_harvest_turn"], out["opp_harvest_turn"])
            self.assertLess(out["opp_destroy_turn"], out["our_harvest_turn"])

    def test_detector_verdicts_on_the_same_two_fixtures(self):
        self.assertEqual(td.detect_d6(D6_TRIGGER)["verdict"], "FAIL")
        self.assertEqual(td.detect_d6(D6_NEAR_MISS)["verdict"], "PASS")


# ===========================================================================
# D-3 --- referee-predicted landing vs realized landing  (review BAR-5)
# ===========================================================================

D3_TRIGGER = d3_two_movers([((6, 1), (6, 1)), ((6, 1), (6, 1)),
                            ((6, 1), (6, 5))])


def d3_old_probe(tr):
    """The 2026-08-08 audit's proposed label: commanded MOVE destination !=
    realized next-state position => 'referee displaced the unit'."""
    out = []
    for t in range(1, tr.T):
        for uid in tr.own_ids:
            cmd = tr.cmd_of(uid, t)
            if cmd is None or cmd.verb != "MOVE":
                continue
            realized = tr.pos(uid, t + 1)
            if realized is None:
                continue
            out.append((t, uid, cmd.args[0], realized,
                        cmd.args[0] != realized))
    return out


def d3_repaired_probe(tr):
    """The repaired label: referee-predicted next_cell (engine.rs::next_cell
    on the exact pre-state map, position, speed and target) vs the realized
    next-state position."""
    out = []
    walkable = set(tr.smap.walkable)
    for t in range(1, tr.T):
        for uid in tr.own_ids:
            cmd = tr.cmd_of(uid, t)
            if cmd is None or cmd.verb != "MOVE":
                continue
            u = tr.unit(uid, t)
            realized = tr.pos(uid, t + 1)
            if u is None or realized is None:
                continue
            pred = referee_next_cell(walkable, u.cell, cmd.args[0],
                                     max(u.speed, 1))
            out.append((t, uid, cmd.args[0], pred, realized, pred != realized))
    return out


class TestD3Probe(unittest.TestCase):
    """BAR-5.  RETRACTED CLAIM (audit sec. 2, D-3 falsification probe):
    referee displacement is "observable as commanded MOVE destination !=
    realized next-state position".  A ``MOVE id x y`` names a target many
    cells away; under a speed limit the next state is NOT expected to equal
    that target."""

    def test_old_probe_mislabels_every_ordinary_travel_turn(self):
        rows = d3_old_probe(D3_TRIGGER)
        self.assertEqual(len(rows), 4)
        # all four ordinary one-step travels are labelled "displaced"
        self.assertEqual(sum(1 for r in rows if r[4]), 4)

    def test_repaired_probe_clears_the_speed_limited_travel_turns(self):
        # unit 0 walks (1,1) -> (2,1) -> (3,1) toward (6,1); engine.rs's
        # next_cell predicts exactly those landings, so the repaired label
        # reports NO displacement where the old one reported two.
        rows = {(t, uid): (pred, real, bad)
                for (t, uid, _tg, pred, real, bad) in
                d3_repaired_probe(D3_TRIGGER)}
        self.assertEqual(rows[(1, 0)], ((2, 1), (2, 1), False))
        self.assertEqual(rows[(2, 0)], ((3, 1), (3, 1), False))

    def test_repaired_probe_finds_the_fixture_itself_referee_inconsistent(self):
        # A second, unplanned result: unit 2's authored landings are NOT what
        # the referee would produce.  From (1,5) toward (6,1) the tie between
        # (1,4) and (2,5) (both at tdist 8) is broken lexicographically to
        # (1,4); the fixture asserts (2,5).  The committed D-3 fixture
        # therefore cannot serve as referee ground truth for this probe --
        # the probe must be run on refereed transcripts, not on the fixtures.
        rows = {(t, uid): (pred, real, bad)
                for (t, uid, _tg, pred, real, bad) in
                d3_repaired_probe(D3_TRIGGER)}
        self.assertEqual(rows[(1, 2)], ((1, 4), (2, 5), True))
        self.assertEqual(rows[(2, 2)], ((2, 4), (3, 5), True))

    def test_referee_next_cell_returns_the_target_when_within_speed(self):
        walkable = set(D3_TRIGGER.smap.walkable)
        self.assertEqual(referee_next_cell(walkable, (1, 1), (2, 1), 1),
                         (2, 1))
        self.assertEqual(referee_next_cell(walkable, (1, 1), (3, 1), 2),
                         (3, 1))


# ===========================================================================
# D-5 --- first_fruit_delay is not a payoff oracle  (review BAR-7)
# ===========================================================================

def orth_wood_cycle_turns(sapling, chop_power, near_water=False,
                          travel_bank=2):
    """Turns from the sapling's first existence to banked wood on the
    orthogonal grow-chop-bank path: grow to the intended chop size, fell it
    under growth-aware health, then travel and bank."""
    size, health, fruits, cooldown = sapling
    grow = 0
    while size < 2:
        size, health, fruits, cooldown = cro.predict_tree(
            size, health, fruits, cooldown, 1, near_water)
        grow += 1
    chops = cro.exact_chop_turns(size, health, cooldown, chop_power,
                                 near_water)
    return grow + chops + travel_bank


class TestD5PayoffOracle(unittest.TestCase):
    """BAR-7.  RETRACTED CLAIM (audit sec. 2 and sec. 5, D-5): "A cutoff
    derived from first_fruit_delay would be an oracle-grounded label" for the
    I-5 cutoff.  D-5's ``orth_cutoff`` branch governs the ORTHOGONAL slot,
    whose payoff is WOOD via grow-chop-bank, not fruit."""

    def test_fruit_deadline_is_strictly_later_than_the_wood_cycle(self):
        for cd in (4, 6):
            sapling = (1, 3, 0, cd)
            fruit = cro.first_fruit_delay(*sapling)
            wood = orth_wood_cycle_turns(sapling, chop_power=1)
            self.assertGreater(fruit, wood)
        self.assertEqual(cro.first_fruit_delay(1, 3, 0, 6), 24)
        self.assertEqual(orth_wood_cycle_turns((1, 3, 0, 6), 1), 12)

    def test_a_fruit_only_cutoff_rejects_profitable_wood_plants(self):
        # Dry orthogonal slot, chop power 1, sapling first exists at t+1.
        sapling = (1, 3, 0, 6)
        wood_deadline = (td.TOTAL_TURNS - 1
                         - orth_wood_cycle_turns(sapling, 1))      # 287
        fruit_deadline = (td.TOTAL_TURNS - 1
                          - cro.first_fruit_delay(*sapling))       # 275
        self.assertEqual((wood_deadline, fruit_deadline), (287, 275))
        # D-5's own committed orth cutoff sits between the two.
        d5_cutoff = td.TOTAL_TURNS - (2 * 6 + td.ceil_div(4, 1) + 2)
        self.assertEqual(d5_cutoff, 282)
        self.assertLess(fruit_deadline, d5_cutoff)
        self.assertLess(d5_cutoff, wood_deadline)
        # 12 turns of profitable orthogonal wood plants (276..287) would be
        # rejected by a first_fruit_delay-derived cutoff.
        self.assertEqual(wood_deadline - fruit_deadline, 12)

    def test_the_gap_is_not_a_fixed_offset(self):
        # The fruit/wood gap depends on chop power, which first_fruit_delay
        # does not take as an input at all.  No constant correction turns a
        # fruit deadline into the wood-cycle deadline.
        gaps = {}
        for chop in (1, 2, 3):
            sapling = (1, 3, 0, 6)
            gaps[chop] = (cro.first_fruit_delay(*sapling)
                          - orth_wood_cycle_turns(sapling, chop))
        self.assertEqual(gaps, {1: 12, 2: 14, 3: 14})
        self.assertGreater(len(set(gaps.values())), 1)


# ---------------------------------------------------------------------------
# Machine-readable dump
# ---------------------------------------------------------------------------

def collect():
    return {
        "schema": "detector-bitetest-probe-results/1",
        "red_transcript": "results/probes-red-2026-08-09.txt",
        "D-4": {
            "near_miss_raw_transitions":
                d4_door_distance_transitions(NEAR_MISS_D4),
            "near_miss_committed_transitions":
                d4_committed_transitions(NEAR_MISS_D4),
            "trigger_raw_transitions":
                d4_door_distance_transitions(TRIGGER_D4),
            "trigger_committed_transitions":
                d4_committed_transitions(TRIGGER_D4),
        },
        "D-6": {
            "trigger_state_2": d6_serialized_state(D6_TRIGGER, 2),
            "near_miss_state_2": d6_serialized_state(D6_NEAR_MISS, 2),
            "trigger_founding_oracle":
                d6_founding_oracle_on_exact_state(D6_TRIGGER),
            "near_miss_founding_oracle":
                d6_founding_oracle_on_exact_state(D6_NEAR_MISS),
            "first_fruit_delay_exact": cro.first_fruit_delay(1, 3, 0, 4),
            "first_fruit_delay_published_state": cro.first_fruit_delay(
                1, 3, 0, 6),
            "detector_verdicts": {
                "trigger": td.detect_d6(D6_TRIGGER)["verdict"],
                "near_miss": td.detect_d6(D6_NEAR_MISS)["verdict"],
            },
        },
        "D-3": {
            "old_probe_rows": d3_old_probe(D3_TRIGGER),
            "repaired_probe_rows": d3_repaired_probe(D3_TRIGGER),
        },
        "D-5": {
            "first_fruit_delay_cd6": cro.first_fruit_delay(1, 3, 0, 6),
            "orth_wood_cycle_cd6_chop1": orth_wood_cycle_turns((1, 3, 0, 6),
                                                               1),
            "wood_deadline": td.TOTAL_TURNS - 1 - orth_wood_cycle_turns(
                (1, 3, 0, 6), 1),
            "fruit_deadline": td.TOTAL_TURNS - 1 - cro.first_fruit_delay(
                1, 3, 0, 6),
            "d5_committed_orth_cutoff":
                td.TOTAL_TURNS - (2 * 6 + td.ceil_div(4, 1) + 2),
        },
    }


def _main(argv):
    import json
    import sys
    if len(argv) >= 2 and argv[0] == "--json":
        with open(argv[1], "w", encoding="utf-8") as fh:
            json.dump(collect(), fh, indent=1, sort_keys=False, default=str)
            fh.write("\n")
        sys.stderr.write("wrote %s\n" % argv[1])
        return 0
    json.dump(collect(), sys.stdout, indent=1, sort_keys=False, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    import sys
    if "--json" in sys.argv or "--dump" in sys.argv:
        raise SystemExit(_main(sys.argv[1:]))
    unittest.main()
