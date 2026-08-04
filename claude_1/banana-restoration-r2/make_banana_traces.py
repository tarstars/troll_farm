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


def main() -> int:
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
