#!/usr/bin/env python3
"""Closed-loop banana-active fixture traces for the D-1..D-9 detector gate.

The semantic harness is open-loop (commands never applied); the trace
detectors quantify over executed effects (carry deltas, inventory responses,
plant lifecycles). This driver closes the loop with a Python mini-referee:
each turn the compiled candidate reads the serialized state and the referee
applies its own-side commands (MOVE/HARVEST/CHOP/PLANT/PICK/DROP) plus plant
growth to produce the next state. Opponent units are static. The referee is
a plausible mechanics mirror (game::rules constants), sufficient for the
detectors' consistency predicates; it is not the platform engine.

Scenarios (banana-active per I-28: ring map, no water, orchard-ineligible):
  t1_lifecycle : 300 turns. Bank BANANA=2, empty ring, resident on a door,
                 inert trained peer, far opponent. Exercises bootstrap PICK,
                 orthogonal plant->grow->chop->bank wood cycle, diagonal
                 mother plant + harvest service, late cutoffs, banking.
  t2_contested : 60 turns. Pre-grown fruited mother, opponent harvester at
                 ETA <= resident ETA (I-10a ownership-loss response:
                 harvest-now), replant + surplus banking under threat.

Outputs per scenario, under traces/: <name>-transcript.txt,
<name>-commands.txt, <name>-detectors.json (via trace_detectors.run_all).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import semantic_harness as sh          # noqa: E402  (builders + compiler)
import trace_detectors as td           # noqa: E402  (detector library)

CANDIDATE = HERE / "candidate-banana-r2.min.rs"
TRACES = HERE / "traces"

MAP = (
    "..............",
    ".0...........1",
    "..............",
    "..............",
    "..............",
)
GEO = sh.parse_rows(MAP)
WALKABLE = GEO["walkable"]
TENT = GEO["shacks"][0]

HEALTH_BASE = {"PLUM": 4, "LEMON": 4, "APPLE": 8, "BANANA": 2}
HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}
COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
ITEM = {"PLUM": 0, "LEMON": 1, "APPLE": 2, "BANANA": 3, "IRON": 4, "WOOD": 5}
KIND_OF_ITEM = {0: "PLUM", 1: "LEMON", 2: "APPLE", 3: "BANANA"}


class Referee:
    def __init__(self, inventory, plants, units):
        # units: dict id -> dict(player,cell,speed,cap,harvest,chop,carry[6])
        self.inv = list(inventory)
        self.opp_inv = [0] * 6
        self.plants = plants           # dict cell -> dict(kind,size,health,fruits,cd)
        self.units = units

    def near_water(self, cell):
        return False                   # the trace map has no water

    def effective_cd(self, kind, cell):
        return COOLDOWN[kind] - (WATER_BOOST[kind] if self.near_water(cell) else 0)

    def turn_text(self):
        plant_rows = tuple(
            (p["kind"], c[0], c[1], p["size"], p["health"], p["fruits"], p["cd"])
            for c, p in sorted(self.plants.items())
        )
        unit_rows = tuple(
            (uid, u["player"], u["cell"][0], u["cell"][1], u["speed"], u["cap"],
             u["harvest"], u["chop"], *u["carry"])
            for uid, u in sorted(self.units.items())
        )
        return sh.turn_text(
            inventory=tuple(self.inv),
            opponent_inventory=tuple(self.opp_inv),
            plants=plant_rows,
            units=unit_rows,
        )

    def step_toward(self, current, target, speed):
        """Mirror of nav::next_cell, adequate for speed >= 1 on this map."""
        if target == current:
            return current
        dist = self._bfs([target])
        if current not in dist:
            return current
        if dist[current] <= speed:
            return target
        cell = current
        for _ in range(speed):
            options = [n for n in self._neighbors(cell) if n in dist]
            if not options:
                break
            cell = min(options, key=lambda n: (dist[n], n))
        return cell

    @staticmethod
    def _neighbors(cell):
        x, y = cell
        return [n for n in ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y))
                if n in WALKABLE]

    @staticmethod
    def _bfs(sources):
        dist = {}
        queue = deque()
        for c in sources:
            if c in WALKABLE or True:  # allow plant-target cells (walkable anyway)
                if c not in dist:
                    dist[c] = 0
                    queue.append(c)
        while queue:
            cell = queue.popleft()
            for n in Referee._neighbors(cell):
                if n not in dist:
                    dist[n] = dist[cell] + 1
                    queue.append(n)
        return dist

    def apply(self, command_line):
        for raw in command_line.split(";"):
            raw = raw.strip()
            if not raw:
                continue
            tok = raw.split()
            verb = tok[0].upper()
            if verb in ("MSG", "WAIT", "TRAIN"):
                continue
            uid = int(tok[1])
            unit = self.units.get(uid)
            if unit is None or unit["player"] != 0:
                continue
            cell = unit["cell"]
            free = unit["cap"] - sum(unit["carry"])
            if verb == "MOVE":
                target = (int(tok[2]), int(tok[3]))
                unit["cell"] = self.step_toward(cell, target, unit["speed"])
            elif verb == "HARVEST":
                plant = self.plants.get(cell)
                if plant and plant["fruits"] > 0 and unit["harvest"] > 0 and free > 0:
                    plant["fruits"] -= 1
                    unit["carry"][ITEM[plant["kind"]]] += 1
            elif verb == "CHOP":
                plant = self.plants.get(cell)
                if plant and unit["chop"] > 0:
                    plant["health"] -= unit["chop"]
                    if plant["health"] <= 0:
                        unit["carry"][5] += min(plant["size"], max(free, 0))
                        del self.plants[cell]
            elif verb == "PLANT" and len(tok) == 3:
                kind = tok[2].upper()
                item = ITEM.get(kind)
                if (item is not None and item <= 3 and unit["carry"][item] > 0
                        and cell not in self.plants):
                    unit["carry"][item] -= 1
                    self.plants[cell] = {
                        "kind": kind, "size": 1,
                        "health": HEALTH_BASE[kind] + HEALTH_SLOPE[kind],
                        "fruits": 0, "cd": self.effective_cd(kind, cell),
                    }
            elif verb == "PICK" and len(tok) == 3:
                item = ITEM.get(tok[2].upper())
                adjacent = abs(cell[0] - TENT[0]) + abs(cell[1] - TENT[1]) == 1
                if item is not None and adjacent and self.inv[item] > 0 and free > 0:
                    self.inv[item] -= 1
                    unit["carry"][item] += 1
            elif verb == "DROP":
                adjacent = abs(cell[0] - TENT[0]) + abs(cell[1] - TENT[1]) == 1
                if adjacent:
                    for i in range(6):
                        self.inv[i] += unit["carry"][i]
                        unit["carry"][i] = 0

    def grow(self):
        for cell, plant in self.plants.items():
            if plant["cd"] > 0:
                plant["cd"] -= 1
            if plant["cd"] == 0:
                if plant["size"] < 4:
                    plant["size"] += 1
                    plant["health"] += HEALTH_SLOPE[plant["kind"]]
                    plant["cd"] = self.effective_cd(plant["kind"], cell)
                elif plant["fruits"] < 3:
                    plant["fruits"] += 1
                    plant["cd"] = self.effective_cd(plant["kind"], cell)


def unit_row(uid, player, cell, speed=1, cap=2, harvest=0, chop=1, carry=None):
    return {
        "player": player, "cell": cell, "speed": speed, "cap": cap,
        "harvest": harvest, "chop": chop, "carry": list(carry or [0] * 6),
    }


def run_scenario(name, binary, referee, turns):
    header = f"{len(MAP[0])} {len(MAP)}\n" + "\n".join(MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    with subprocess.Popen(
        [str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    ) as proc:
        proc.stdin.write(header)
        proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            transcript_parts.append(block)
            proc.stdin.write(block)
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError(f"{name}: bot closed stdout early")
            line = line.rstrip("\n")
            command_lines.append(line)
            referee.apply(line)
            referee.grow()
        proc.stdin.close()
    transcript = "".join(transcript_parts)
    commands = "\n".join(command_lines) + "\n"
    TRACES.mkdir(exist_ok=True)
    (TRACES / f"{name}-transcript.txt").write_text(transcript)
    (TRACES / f"{name}-commands.txt").write_text(commands)
    trace = td.build_trace(transcript, commands)
    results = td.run_all(trace)
    report = {
        "scenario": name,
        "turns": trace.T,
        "notes": trace.notes,
        "detectors": results,
        "overall": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL",
    }
    (TRACES / f"{name}-detectors.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n"
    )
    return report


def scenario_t1():
    # Bootstrap + full ring lifecycle: bank seeds, empty ring, resident on
    # the (2,1) door, inert trained peer, far opponent (harvester+chopper).
    return Referee(
        inventory=[0, 0, 0, 2, 0, 0],
        plants={},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
        },
    )


def scenario_t2():
    # Contested mother (I-10a): opponent harvester at ETA <= resident ETA.
    return Referee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={(2, 2): {"kind": "BANANA", "size": 4, "health": 6,
                         "fruits": 2, "cd": 4}},
        units={
            0: unit_row(0, 0, (0, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (3, 3), cap=2, harvest=1, chop=0),
        },
    )


# ---------------------------------------------------------------------------
# Additive dynamic-opponent support (RED-phase regression scenarios).
# Nothing below is reachable from the original t1/t2 path: scenario_t1/
# scenario_t2 still build the plain static-opponent Referee and the default
# CLI (no arguments) runs exactly the original main body, so t1/t2 output
# stays byte-identical.
# ---------------------------------------------------------------------------

class DynamicOpponentReferee(Referee):
    """Referee with a deterministic moving opponent harvester.

    Every opponent unit listed in ``opp_targets`` (uid -> target cell) MOVEs
    toward its target at its own movement speed each turn, using the same
    ``step_toward`` mirror as own-side moves, and once standing on the target
    cell harvests one ripe fruit per turn (subject to harvest power and free
    capacity), exactly like an own-side HARVEST. The opponent acts after the
    own-side commands of the turn are applied and before growth, so the
    resulting states are a deterministic pure function of the command stream.
    Existing Referee behavior paths are untouched.
    """

    def __init__(self, inventory, plants, units, opp_targets):
        super().__init__(inventory, plants, units)
        self.opp_targets = dict(opp_targets)

    def opponent_step(self):
        for uid in sorted(self.opp_targets):
            unit = self.units.get(uid)
            if unit is None or unit["player"] != 1:
                continue
            target = self.opp_targets[uid]
            if unit["cell"] != target:
                unit["cell"] = self.step_toward(
                    unit["cell"], target, unit["speed"])
            if unit["cell"] == target:
                plant = self.plants.get(target)
                free = unit["cap"] - sum(unit["carry"])
                if (plant is not None and plant["fruits"] > 0
                        and unit["harvest"] > 0 and free > 0):
                    plant["fruits"] -= 1
                    unit["carry"][ITEM[plant["kind"]]] += 1

    def apply(self, command_line):
        super().apply(command_line)
        self.opponent_step()


MOTHER_CELL = (2, 2)   # diagonal ring cell of the (1,1) tent on the trace map


def scenario_t3_abandon():
    # I-10a abandon branch. Unripe mother (size 4, health 6, fruits 0,
    # cd 6 -> ripens around turn 7-9), resident (speed 1, chop 1) starts at
    # (5,3), BFS distance 4 to the mother. Opponent harvester (speed 2,
    # chop 0) starts at (11,2), distance 9, eta ceil(9/2)=5 > 4, so the
    # mother is owned (I-7) at turn 1 and ownership is LOST a few turns
    # later as the faster opponent closes in. At the flip the conversion
    # (travel + 6 chops) cannot complete strictly before the opponent's
    # earliest harvest, so I-10a requires Abandoned: no further investment.
    return DynamicOpponentReferee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={MOTHER_CELL: {"kind": "BANANA", "size": 4, "health": 6,
                              "fruits": 0, "cd": 6}},
        units={
            0: unit_row(0, 0, (5, 3), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (11, 2), speed=2, cap=2, harvest=1, chop=0),
        },
        opp_targets={5: MOTHER_CELL},
    )


def scenario_t4_convert():
    # I-10a convert branch. Unripe pre-damaged mother (size 4, health 2,
    # fruits 0, cd 30 -> stays unripe for the whole 20-turn trace), resident
    # at the (2,1) door, distance 1, chop 1: conversion completes within
    # ~3 turns. Opponent harvester (speed 2, chop 0) approaches from (10,2)
    # (distance 8, eta 4) and camps on the mother; its earliest possible
    # harvest is bounded below by the 30-turn ripening, so the chop
    # completes strictly before eta_opp and I-10a requires CHOP (convert).
    return DynamicOpponentReferee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={MOTHER_CELL: {"kind": "BANANA", "size": 4, "health": 2,
                              "fruits": 0, "cd": 30}},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (10, 2), speed=2, cap=2, harvest=1, chop=0),
        },
        opp_targets={5: MOTHER_CELL},
    )


DYNAMIC_SCENARIOS = (
    ("t3_abandon", scenario_t3_abandon, 20),
    ("t4_convert", scenario_t4_convert, 20),
)


def scenario_r3_growth():
    # R-3 "growth-aware-conversion" (RED round 3; successor host review
    # 2026-08-05, terminal failure 1). Unripe pre-existing mother (size 2,
    # health 4 = 2 + size, fruits 0, cd 10). Resident (speed 1, chop 1) at
    # (7,2), BFS distance 5; opponent harvester (speed 1, chop 0) at (6,3),
    # BFS distance 5: I-7 ownership is lost at turn 1 (tie, eta_res 5 >=
    # eta_opp 5, ties conceded). Exact growth-aware conversion needs travel
    # 5 + 4 chops = completion turn 9, while the opponent ARRIVES on the
    # mother at turn 6 -- the conversion cannot complete strictly before
    # opponent arrival, so I-10a requires abandon. The rejected candidate's
    # static arithmetic instead accepts (at the on-tree decision it compares
    # ceil(health 4 / chop 1) = 4 against max(eta_opp 0, cooldown-as-ripen
    # 5) = 5, the review's literal "4 < 5") and starts the doomed chop.
    return DynamicOpponentReferee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={MOTHER_CELL: {"kind": "BANANA", "size": 2, "health": 4,
                              "fruits": 0, "cd": 10}},
        units={
            0: unit_row(0, 0, (7, 2), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (6, 3), speed=1, cap=2, harvest=1, chop=0),
        },
        opp_targets={5: MOTHER_CELL},
    )


# ---------------------------------------------------------------------------
# Round-4 additive support: CONVERSION_RACE_ORACLE regression scenarios
# (spec Revision 2026-08-05). Nothing below is reachable from the t1-t6
# paths; their output stays byte-identical.
# ---------------------------------------------------------------------------


def scenario_r4_flip_reach():
    # R-4 "flip-response-reachability" (round 4). The CANDIDATE ITSELF
    # bootstraps (PICK), plants the diagonal mother at (2,2), then leaves it
    # during its normal lifecycle: a pre-grown orthogonal wood banana at the
    # (0,1) door (size 2, inert cooldown 40) pulls the resident away for the
    # I-4 wood cycle (chop turns 7-10, bank DROP at turn 11). Meanwhile the
    # opponent harvester walks in from (13,0) (distance 13) toward a camp
    # cell adjacent to the mother: at turn 11 the resident (at (0,1), eta 3)
    # ties the opponent (distance 3) -> I-7 ownership flips. The mother is
    # size 2, unripe, first fruit ~16 growth turns out, so
    # CONVERSION_RACE_ORACLE says the conversion is FEASIBLE
    # (completion_turn 18 < opponent_harvest_turn 27) and I-10a requires the
    # convert response to begin by turn 12 (flip turn + 1).
    return DynamicOpponentReferee(
        inventory=[0, 0, 0, 1, 0, 0],
        plants={(0, 1): {"kind": "BANANA", "size": 2, "health": 4,
                         "fruits": 0, "cd": 40}},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (13, 0), speed=1, cap=2, harvest=1, chop=0),
        },
        opp_targets={5: (2, 3)},
    )


def _scenario_r3_boundary(health):
    # Shared geometry of the R-3 boundary pair (spec Revision 2026-08-05,
    # normative examples): near-ripe size-4 mother at (2,2) (fruits 0,
    # cd 6 -> first fruit in state 7), resident on the ring at (2,0)
    # (BFS distance 2, chop 1), opponent harvester at (4,2) (distance 2,
    # speed 1) walking in and camping on the mother. I-7 ownership is lost
    # at turn 1 (tie, eta 2 vs 2).
    return DynamicOpponentReferee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={MOTHER_CELL: {"kind": "BANANA", "size": 4, "health": health,
                              "fruits": 0, "cd": 6}},
        units={
            0: unit_row(0, 0, (2, 0), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (4, 2), speed=1, cap=2, harvest=1, chop=0),
        },
        opp_targets={5: MOTHER_CELL},
    )


def scenario_r3a_boundary():
    # R-3a: INFEASIBLE by exactly the strict tie. Health 5 -> exact chops 5,
    # completion_turn 1 + 2 + 5 - 1 = 7 == opponent_harvest_turn
    # max(1 + 2, 1 + 6) = 7. I-10a requires abandon; any chop-start here is
    # the doomed chop.
    return _scenario_r3_boundary(5)


def scenario_r3b_boundary():
    # R-3b: FEASIBLE by exactly one turn. Health 4 -> exact chops 4,
    # completion_turn 6 < opponent_harvest_turn 7. I-10a requires convert.
    # Every voided legacy deadline (spec-old "< eta_opp", candidate
    # "< max(eta_opp, predicted.cooldown)", D-8-old arrival-only) answers
    # infeasible here -- the discriminating geometry of the unification.
    return _scenario_r3_boundary(4)


# ---------------------------------------------------------------------------
# Round-3 additive support: t5 / t6 traces for the amended D-8 (integrator's
# narrow I-10a/D-8 ruling, successor host review 2026-08-05). Nothing below
# is reachable from the t1-t4 paths; their output stays byte-identical.
# ---------------------------------------------------------------------------

class WaypointOpponentReferee(DynamicOpponentReferee):
    """DynamicOpponentReferee whose opponents follow a waypoint list: when a
    unit stands on its current waypoint the next one becomes the target
    (allowing pass-by geometries: approach, flip I-7 ownership, depart).
    Movement/harvest semantics are inherited unchanged."""

    def __init__(self, inventory, plants, units, opp_waypoints):
        first = {uid: wps[0] for uid, wps in opp_waypoints.items() if wps}
        super().__init__(inventory, plants, units, first)
        self.opp_waypoints = {uid: list(wps)
                              for uid, wps in opp_waypoints.items()}

    def opponent_step(self):
        for uid in sorted(self.opp_waypoints):
            unit = self.units.get(uid)
            wps = self.opp_waypoints[uid]
            if unit is None or not wps:
                continue
            while len(wps) > 1 and unit["cell"] == wps[0]:
                wps.pop(0)
            self.opp_targets[uid] = wps[0]
        super().opponent_step()


def scenario_t5_flip_convert():
    # t5: own-PLANT -> opponent movement -> I-7 ownership flip -> FEASIBLE
    # exact conversion (D-8 amendment positive case). The opponent harvester
    # transits: it approaches the mother to BFS distance 1 (turn-6 state:
    # opponent at (2,3), resident at the (2,1) door, eta_res 1 >= eta_opp 1,
    # tie conceded -> ownership flips), then departs toward (12,4). At the
    # scripted chop-start (turn 12: plant size 2, health 4, cd 3) the exact
    # growth-aware chop count is 5 (the tree grows mid-sequence) < opponent
    # ETA 7: the strict exact race is won and the amended D-8 must exempt
    # the conversion.
    return WaypointOpponentReferee(
        inventory=[0, 0, 0, 1, 0, 0],
        plants={},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (7, 3), speed=1, cap=2, harvest=1, chop=0),
        },
        opp_waypoints={5: [(2, 3), (12, 4)]},
    )


T5_SCRIPT = {
    1: "PICK 0 BANANA;WAIT",
    2: "MOVE 0 2 2;WAIT",
    3: "PLANT 0 BANANA;WAIT",
    4: "MOVE 0 2 1;WAIT",
    11: "MOVE 0 2 2;WAIT",
    12: "CHOP 0;WAIT", 13: "CHOP 0;WAIT", 14: "CHOP 0;WAIT",
    15: "CHOP 0;WAIT", 16: "CHOP 0;WAIT",
    17: "MOVE 0 2 1;WAIT",
    18: "DROP 0;WAIT",
}


def scenario_t6_owned_chop():
    # t6: negative control -- discretionary chop of an OWNED own-planted
    # diagonal mother. The opponent harvester stays far (BFS distance 13,
    # eta 13): I-7 ownership never flips, so the scripted chops at turns
    # 6..9 are the forbidden discretionary case and the amended D-8 must
    # still flag them (reason discretionary_owned).
    return Referee(
        inventory=[0, 0, 0, 1, 0, 0],
        plants={},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=0),
        },
    )


T6_SCRIPT = {
    1: "PICK 0 BANANA;WAIT",
    2: "MOVE 0 2 2;WAIT",
    3: "PLANT 0 BANANA;WAIT",
    6: "CHOP 0;WAIT", 7: "CHOP 0;WAIT", 8: "CHOP 0;WAIT", 9: "CHOP 0;WAIT",
    10: "MOVE 0 2 1;WAIT",
    11: "DROP 0;WAIT",
}


def run_scripted_scenario(name, referee, script, turns):
    """Closed-loop run of a scripted per-turn policy (dict turn -> command
    line, default WAIT) through the referee; writes the same trace triple
    as run_scenario (transcript, commands, detectors.json). Used for the
    synthetic t5/t6 D-8-amendment traces, which document required successor
    behavior rather than current-candidate behavior."""
    header = f"{len(MAP[0])} {len(MAP)}\n" + "\n".join(MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    for turn in range(1, turns + 1):
        transcript_parts.append(referee.turn_text())
        line = script.get(turn, "WAIT")
        command_lines.append(line)
        referee.apply(line)
        referee.grow()
    transcript = "".join(transcript_parts)
    commands = "\n".join(command_lines) + "\n"
    TRACES.mkdir(exist_ok=True)
    (TRACES / f"{name}-transcript.txt").write_text(transcript)
    (TRACES / f"{name}-commands.txt").write_text(commands)
    trace = td.build_trace(transcript, commands)
    results = td.run_all(trace)
    report = {
        "scenario": name,
        "turns": trace.T,
        "notes": trace.notes,
        "detectors": results,
        "overall": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL",
    }
    (TRACES / f"{name}-detectors.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n"
    )
    return report


ROUND3_SCENARIOS = (
    ("t5_flip_convert", scenario_t5_flip_convert, T5_SCRIPT, 20),
    ("t6_owned_chop", scenario_t6_owned_chop, T6_SCRIPT, 14),
)


# ---------------------------------------------------------------------------
# Round-5 additive support: R-5 "two-worker-full-cargo-banking" reproduction
# scenario (round-4 host review 2026-08-05, terminal failure: on map seed
# 9,854,000 seat 0 the candidate's FULL second worker -- carry [0,0,0,0,0,2]
# -- oscillates (8,4)<->(8,3) for 225 turns, turns 34-258, emitting
# MOVE 2 8 3 / MOVE 2 8 4 with no DROP, instead of banking; margin +68 -> -93).
# Nothing below is reachable from the t1-t6 paths; their output stays
# byte-identical (the default CLI, --dynamic and --round3 never construct
# CustomMapReferee).
# ---------------------------------------------------------------------------

# R-5 map: banana-eligible (no water -> orchard geometry None), own tent at
# the module TENT cell (1,1) with exactly TWO walkable doors, (2,1) and
# (1,2), and the diagonal ring cell (2,2) as the SINGLE ARTICULATION CELL of
# the walkable graph between the east corridor (row 2) and both doors:
# every banking route of a carrier coming from the east passes through
# (2,2). A live diagonal banana on (2,2) is then the protected mother, so
# the candidate's C5 third protection layer (block-i1: banana_forbidden =
# {mother} in resolve_move_conflicts_with_priority_and_forbidden) makes the
# carrier's one-step landing onto (2,2) forbidden -- the local reproduction
# of the host counterexample's ring/banking interaction.
R5_MAP = (
    "##############",
    "#0.###########",
    "#............1",
    "##############",
    "##############",
)


class CustomMapReferee(Referee):
    """Referee bound to an INSTANCE static map instead of the module-level
    MAP/WALKABLE globals. Movement (``step_toward``) and its BFS run on the
    instance walkable set; everything else (HARVEST/CHOP/PLANT/PICK/DROP,
    growth) is inherited unchanged. The own tent must stay on the module
    TENT cell (1,1) because the inherited PICK/DROP door-adjacency
    arithmetic reads that module constant; the constructor enforces it."""

    def __init__(self, map_rows, inventory, plants, units):
        super().__init__(inventory, plants, units)
        self.map_rows = tuple(map_rows)
        geo = sh.parse_rows(self.map_rows)
        if geo["shacks"].get(0) != TENT:
            raise ValueError(
                "CustomMapReferee requires the own tent at %r" % (TENT,))
        self.walk = set(geo["walkable"])

    def map_header(self):
        return (f"{len(self.map_rows[0])} {len(self.map_rows)}\n"
                + "\n".join(self.map_rows) + "\n")

    def _map_neighbors(self, cell):
        x, y = cell
        return [n for n in ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y))
                if n in self.walk]

    def _map_bfs(self, sources):
        dist = {}
        queue = deque()
        for c in sources:
            if c not in dist:
                dist[c] = 0
                queue.append(c)
        while queue:
            cell = queue.popleft()
            for n in self._map_neighbors(cell):
                if n not in dist:
                    dist[n] = dist[cell] + 1
                    queue.append(n)
        return dist

    def step_toward(self, current, target, speed):
        """Same nav::next_cell mirror as Referee.step_toward, evaluated on
        the instance walkable set."""
        if target == current:
            return current
        dist = self._map_bfs([target])
        if current not in dist:
            return current
        if dist[current] <= speed:
            return target
        cell = current
        for _ in range(speed):
            options = [n for n in self._map_neighbors(cell) if n in dist]
            if not options:
                break
            cell = min(options, key=lambda n: (dist[n], n))
        return cell


def scenario_r5_two_worker_banking():
    # R-5 "two-worker-full-cargo-banking". Both own workers present from
    # turn 1 (mirrors the host counterexample's turn-1 training):
    #   unit 0 -- the resident starter, on the (2,1) door (on-ring, so the
    #            banana phase activates at turn 1: 2 workers + live ring
    #            banana as the seed source); it has nothing to do (mother
    #            unripe, no vacancies plantable without a seed) and WAITs;
    #   unit 2 -- the second economy worker, cap 2 carrying 2 wood
    #            (carry [0,0,0,0,0,2], free_capacity 0), in the east
    #            corridor at (6,2); its ONLY task is banking, and every
    #            route to a door crosses the protected mother cell (2,2);
    #   unit 5 -- far opponent harvester at (12,2) (eta to the mother 10 >>
    #            resident eta 1, so I-7 ownership never flips and the C5
    #            protection stays engaged for the whole trace).
    # The mother is size 4, fruits 0, cooldown 60: unripe for the whole
    # 40-turn scenario, so the resident never gets a harvest task and the
    # protected cell never changes.
    return CustomMapReferee(
        R5_MAP,
        inventory=[0, 0, 0, 0, 0, 0],
        plants={(2, 2): {"kind": "BANANA", "size": 4, "health": 6,
                         "fruits": 0, "cd": 60}},
        units={
            0: unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            2: unit_row(2, 0, (6, 2), cap=2, harvest=0, chop=1,
                        carry=[0, 0, 0, 0, 0, 2]),
            5: unit_row(5, 1, (12, 2), cap=2, harvest=1, chop=0),
        },
    )


def main_round3() -> int:
    """`--round3` flag: emit the scripted t5/t6 D-8-amendment traces.

    t5 (flip + feasible exact conversion) must be overall PASS under the
    amended D-8; t6 (owned-mother discretionary chop) is REQUIRED to show a
    D-8 FAIL -- it is the negative control. Exit 0 iff both behave as
    designed.
    """
    ok = True
    for name, factory, script, turns in ROUND3_SCENARIOS:
        report = run_scripted_scenario(name, factory(), script, turns)
        verdicts = {r["detector"]: r["verdict"] for r in report["detectors"]}
        print(name, report["overall"], json.dumps(verdicts))
        d8 = verdicts.get("D-8")
        if name == "t5_flip_convert":
            ok = ok and report["overall"] == "PASS"
        else:
            ok = ok and d8 == "FAIL" and all(
                v == "PASS" for k, v in verdicts.items() if k != "D-8")
    return 0 if ok else 1


def main_dynamic() -> int:
    """`--dynamic` flag: emit only the dynamic-opponent scenarios t3/t4.

    Detector verdicts are printed as information; the exit code only
    reflects that the traces were produced (these RED scenarios are allowed
    to show detector failures on a rejected candidate).
    """
    source = CANDIDATE.read_text()
    with tempfile.TemporaryDirectory(prefix="banana-r2-traces-") as directory:
        binary = Path(directory) / "candidate"
        sh.compile_text(source, binary, "banana_r2_traces")
        for name, factory, turns in DYNAMIC_SCENARIOS:
            report = run_scenario(name, binary, factory(), turns)
            verdicts = {r["detector"]: r["verdict"] for r in report["detectors"]}
            print(name, report["overall"], json.dumps(verdicts))
    return 0


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    if args and args[0] == "--dynamic":
        return main_dynamic()
    if args and args[0] == "--round3":
        return main_round3()
    source = CANDIDATE.read_text()
    overall_ok = True
    with tempfile.TemporaryDirectory(prefix="banana-r2-traces-") as directory:
        binary = Path(directory) / "candidate"
        sh.compile_text(source, binary, "banana_r2_traces")
        for name, factory, turns in (
            ("t1_lifecycle", scenario_t1, 300),
            ("t2_contested", scenario_t2, 60),
        ):
            report = run_scenario(name, binary, factory(), turns)
            verdicts = {r["detector"]: r["verdict"] for r in report["detectors"]}
            print(name, report["overall"], json.dumps(verdicts))
            overall_ok = overall_ok and report["overall"] == "PASS"
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
