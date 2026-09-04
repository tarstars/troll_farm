#!/usr/bin/env python3
"""Offline champion-prefix orchard oracle.

The candidate process is the unchanged champion binary.  Until the champion's
own second TRAIN resolves, its stdout is forwarded byte-for-byte.  Afterwards
a Python controller may replace commands for one planter and one feller while
the same champion process keeps receiving the resulting live states.  It is
therefore a continuously advanced shadow champion, not a restarted or guessed
continuation.

This is an offline mechanism experiment.  It searches a small, published
policy vocabulary on development maps, includes NO_PLANT, uses exact paired
referee replay, and never submits a bot.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for rel in (
    "claude_1/t1",
    "claude_1/pipeline",
    "claude_1/banana-restoration-r2",
    "claude_1/narrate6",
    "claude_1/cure3",
):
    path = str(REPO / rel)
    if path not in sys.path:
        sys.path.insert(0, path)

import fuzz_panel as fp  # noqa: E402
import semantic_harness as sh  # noqa: E402

# Import the exact real-map smoke adapter without relying on the ambiguous
# module name "smoke".
_smoke_spec = importlib.util.spec_from_file_location(
    "third_troll_smoke", REPO / "local_claude_1" / "third-troll" / "smoke.py"
)
if _smoke_spec is None or _smoke_spec.loader is None:
    raise RuntimeError("cannot import third-troll smoke adapter")
smoke = importlib.util.module_from_spec(_smoke_spec)
_smoke_spec.loader.exec_module(smoke)

PLUM, LEMON, APPLE, BANANA, IRON, WOOD = range(6)
ITEM_INDEX = {"PLUM": PLUM, "LEMON": LEMON, "APPLE": APPLE, "BANANA": BANANA}
UNIT_VERBS = {"MOVE", "HARVEST", "CHOP", "MINE", "PLANT", "DROP", "PICK"}
BIG = 10**9
TURNS = 300


class ExperimentError(RuntimeError):
    pass


class DeadCondition(ExperimentError):
    pass


@dataclass(frozen=True)
class Policy:
    name: str
    enabled: bool
    species: str = "BANANA"
    start_turn: int = 70
    plant_count: int = 0
    max_door_distance: int = 2
    latest_plant_turn: int = 150
    fell_size: int = 4

    @property
    def no_plant(self) -> bool:
        return not self.enabled or self.plant_count <= 0


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(inv: list[int]) -> int:
    return sum(inv[:4]) + 4 * inv[WOOD]


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def orth(cell: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = cell
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def own_units(ref) -> dict[int, dict[str, Any]]:
    return {uid: unit for uid, unit in ref.units.items() if unit["player"] == 0}


def own_doors(ref) -> list[tuple[int, int]]:
    return sorted(cell for cell in orth(ref.shacks[0]) if cell in ref.walk)


def nearest_door(ref, unit: dict[str, Any]) -> tuple[int, int] | None:
    doors = own_doors(ref)
    if not doors:
        return None
    dist = ref._bfs_from([unit["cell"]])
    return min(doors, key=lambda cell: (dist.get(cell, BIG), cell))


def command_fragments(line: str) -> list[str]:
    return [fragment.strip() for fragment in line.split(";") if fragment.strip()]


def fragment_unit(fragment: str) -> int | None:
    fields = fragment.split()
    if len(fields) < 2 or fields[0].upper() not in UNIT_VERBS:
        return None
    try:
        return int(fields[1])
    except ValueError:
        return None


def fragment_target(fragment: str, ref) -> tuple[int, int] | None:
    fields = fragment.split()
    if not fields:
        return None
    verb = fields[0].upper()
    uid = fragment_unit(fragment)
    if verb == "MOVE" and len(fields) == 4:
        try:
            return int(fields[2]), int(fields[3])
        except ValueError:
            return None
    if uid is not None and verb in {"HARVEST", "CHOP", "PLANT"}:
        unit = ref.units.get(uid)
        return None if unit is None else tuple(unit["cell"])
    return None


def training_fragments(lines: Iterable[str]) -> list[dict[str, Any]]:
    rows = []
    for turn, line in enumerate(lines, 1):
        for fragment in command_fragments(line):
            fields = fragment.split()
            if fields and fields[0].upper() == "TRAIN" and len(fields) == 5:
                rows.append(
                    {
                        "turn": turn,
                        "spec": " ".join(fields[1:5]),
                        "stats": [int(value) for value in fields[1:5]],
                    }
                )
    return rows


def acting_ids(line: str) -> set[int]:
    return {
        uid
        for fragment in command_fragments(line)
        if (uid := fragment_unit(fragment)) is not None
    }


def idle_max(lines: list[str], unit_ids: Iterable[int], first: int, last: int) -> dict[str, int]:
    ids = list(unit_ids)
    run = {uid: 0 for uid in ids}
    best = {uid: 0 for uid in ids}
    for turn in range(max(1, first), min(last, len(lines)) + 1):
        active = acting_ids(lines[turn - 1])
        for uid in ids:
            if uid in active:
                run[uid] = 0
            else:
                run[uid] += 1
                best[uid] = max(best[uid], run[uid])
    return {str(uid): value for uid, value in best.items()}


def bootstrap_ci(values: list[float], *, seed: int = 20260904, draws: int = 10000) -> dict[str, Any]:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "lower95": None, "upper95": None}
    mean = statistics.fmean(values)
    if n == 1:
        return {"n": 1, "mean": mean, "lower95": mean, "upper95": mean}
    rng = random.Random(seed)
    means = []
    for _ in range(draws):
        means.append(statistics.fmean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    lo = means[int(0.025 * (draws - 1))]
    hi = means[int(0.975 * (draws - 1))]
    return {"n": n, "mean": mean, "lower95": lo, "upper95": hi}


def policy_key(row: dict[str, Any]) -> tuple[float, float, int, str]:
    # Higher paired margin, then own score; fewer irreversible plants wins ties.
    return (
        float(row["delta_margin"]),
        float(row["delta_own"]),
        -int(row.get("plants_successful", 0)),
        str(row["policy"]),
    )


class OrchardController:
    """Small explicit macro controller used only after the champion prefix."""

    def __init__(self, policy: Policy):
        self.policy = policy
        self.branch_turn: int | None = None
        self.second_event: dict[str, Any] | None = None
        self.planter_id: int | None = None
        self.feller_id: int | None = None
        self.candidate_cells: list[tuple[int, int]] = []
        self.skipped_cells: set[tuple[int, int]] = set()
        self.orchard_cells: set[tuple[int, int]] = set()
        self.pending_cells: dict[tuple[int, int], int] = {}
        self.resolved_cells: set[tuple[int, int]] = set()
        self.plants_issued = 0
        self.plants_successful = 0
        self.fells_completed = 0
        self.realized_orchard_wood = 0
        self.predicted_orchard_wood = 0.0
        self.banked_by_overrides = 0
        self.overrides = 0
        self.suppressed_trains = 0
        self.abandoned = False
        self.abandon_reason: str | None = None
        self.failed_effect_streak = 0
        self.last_effects: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    def _choose_workers(self, ref) -> None:
        units = own_units(ref)
        if len(units) < 2:
            return
        self.planter_id = min(units)
        alternatives = [
            (uid, unit)
            for uid, unit in units.items()
            if uid != self.planter_id and unit["chop"] > 0
        ]
        if not alternatives:
            alternatives = [(uid, unit) for uid, unit in units.items() if unit["chop"] > 0]
        if not alternatives:
            self.abandoned = True
            self.abandon_reason = "no own chopper after the champion prefix"
            return
        self.feller_id = max(
            alternatives,
            key=lambda item: (
                item[1]["chop"] * item[1]["cap"],
                item[1]["cap"],
                item[1]["chop"],
                item[1]["speed"],
                -item[0],
            ),
        )[0]

    def _choose_cells(self, ref) -> None:
        doors = own_doors(ref)
        if not doors:
            self.abandoned = True
            self.abandon_reason = "no reachable own door"
            return
        dist = ref._bfs_from(doors)
        enemy_dist = ref._bfs_from(ref.opp_doors) if ref.opp_doors else {}
        occupied = set(ref.plants) | {tuple(unit["cell"]) for unit in ref.units.values()}
        door_set = set(doors)
        cells = [
            cell
            for cell in ref.walk
            if cell not in occupied
            and cell not in door_set
            and cell not in ref.shacks
            and 1 <= dist.get(cell, BIG) <= self.policy.max_door_distance
        ]
        cells.sort(
            key=lambda cell: (
                not ref.near_water(cell),
                dist.get(cell, BIG),
                -enemy_dist.get(cell, -BIG),
                cell,
            )
        )
        # Keep deterministic backups because an opponent can occupy a planned cell.
        self.candidate_cells = cells[: max(self.policy.plant_count * 3, 8)]

    def _observe_previous(self, ref, turn: int) -> None:
        if not self.last_effects:
            return
        successes = 0
        failures = 0
        for effect in self.last_effects:
            uid = effect["uid"]
            unit = ref.units.get(uid)
            verb = effect["verb"]
            target = effect.get("target")
            ok = False
            if verb == "MOVE":
                ok = unit is not None and (
                    tuple(unit["cell"]) != tuple(effect["before_cell"])
                    or tuple(unit["cell"]) == tuple(target)
                )
            elif verb == "PICK":
                idx = effect["item"]
                ok = (
                    unit is not None
                    and unit["carry"][idx] > effect["before_carry"]
                )
            elif verb == "PLANT":
                plant = ref.plants.get(tuple(target))
                ok = plant is not None and plant["kind"] == effect["species"]
                if ok:
                    cell = tuple(target)
                    if cell not in self.orchard_cells:
                        self.orchard_cells.add(cell)
                        self.pending_cells.pop(cell, None)
                        self.plants_successful += 1
                        feller = ref.units.get(self.feller_id) if self.feller_id is not None else None
                        convertible = min(4, max(0, feller["cap"])) if feller else 0
                        wet = ref.near_water(cell)
                        growth = 12 if wet else 18
                        maturity_turn = effect["turn"] + growth
                        pre = max(0, min(maturity_turn, 100) - effect["turn"])
                        post = max(0, maturity_turn - max(effect["turn"], 100))
                        survival = math.exp(-(0.0019 * pre + 0.008 * post))
                        self.predicted_orchard_wood += convertible * survival
                        self.events.append(
                            {
                                "turn": turn,
                                "event": "plant_confirmed",
                                "cell": list(cell),
                                "species": effect["species"],
                                "predicted_convertible_wood": convertible * survival,
                            }
                        )
            elif verb == "CHOP":
                before_health = effect["before_health"]
                plant = ref.plants.get(tuple(target))
                wood_now = 0 if unit is None else unit["carry"][WOOD]
                ok = (
                    plant is None
                    or plant["health"] != before_health
                    or wood_now > effect["before_wood"]
                )
                if plant is None and tuple(target) in self.orchard_cells:
                    gained = max(0, wood_now - effect["before_wood"])
                    if tuple(target) not in self.resolved_cells:
                        self.resolved_cells.add(tuple(target))
                        self.fells_completed += 1
                        self.realized_orchard_wood += gained
                        self.events.append(
                            {
                                "turn": turn,
                                "event": "orchard_tree_removed",
                                "cell": list(target),
                                "wood_gained": gained,
                            }
                        )
            elif verb == "DROP":
                carry_now = 0 if unit is None else sum(unit["carry"])
                ok = carry_now < effect["before_total"]
                if ok:
                    delta = max(0, ref.inv[WOOD] - effect["before_bank_wood"])
                    self.banked_by_overrides += delta
            if ok:
                successes += 1
            else:
                failures += 1
                self.events.append(
                    {
                        "turn": turn,
                        "event": "missed_progress",
                        "verb": verb,
                        "uid": uid,
                        "target": list(target) if isinstance(target, tuple) else target,
                    }
                )
        if failures and not successes:
            self.failed_effect_streak += 1
        else:
            self.failed_effect_streak = 0
        if self.failed_effect_streak >= 3:
            self.abandoned = True
            self.abandon_reason = "three consecutive override turns missed their progress event"
            self.events.append(
                {"turn": turn, "event": "hand_back", "reason": self.abandon_reason}
            )
        self.last_effects = []

    def _next_empty_cell(self, ref) -> tuple[int, int] | None:
        for cell in self.candidate_cells:
            if cell in self.orchard_cells or cell in self.pending_cells or cell in self.skipped_cells:
                continue
            if cell in ref.plants or any(tuple(unit["cell"]) == cell for unit in ref.units.values()):
                self.skipped_cells.add(cell)
                continue
            return cell
        return None

    def _bank_command(self, ref, uid: int) -> tuple[str, tuple[int, int] | None] | None:
        unit = ref.units.get(uid)
        if unit is None or sum(unit["carry"]) <= 0:
            return None
        if manhattan(tuple(unit["cell"]), tuple(ref.shacks[0])) <= 1:
            return f"DROP {uid}", tuple(unit["cell"])
        door = nearest_door(ref, unit)
        if door is None:
            return None
        return f"MOVE {uid} {door[0]} {door[1]}", door

    def _desired(self, ref, turn: int) -> tuple[dict[int, str], set[tuple[int, int]]]:
        if self.abandoned or self.policy.no_plant or turn < self.policy.start_turn:
            return {}, set()
        if self.planter_id is None or self.feller_id is None:
            return {}, set()
        units = own_units(ref)
        if self.planter_id not in units or self.feller_id not in units:
            self.abandoned = True
            self.abandon_reason = "selected orchard worker disappeared"
            return {}, set()

        desired: dict[int, str] = {}
        reserved: set[tuple[int, int]] = set()

        # First, finish any orchard wood already carried by the feller.
        feller = units[self.feller_id]
        if sum(feller["carry"]) > 0:
            command = self._bank_command(ref, self.feller_id)
            if command is not None:
                desired[self.feller_id] = command[0]
                if command[1] is not None:
                    reserved.add(command[1])
        else:
            mature = [
                cell
                for cell in self.orchard_cells
                if cell not in self.resolved_cells
                and (plant := ref.plants.get(cell)) is not None
                and plant["kind"] == self.policy.species
                and plant["size"] >= self.policy.fell_size
                and plant["health"] > 0
            ]
            if mature:
                dist = ref._bfs_from([tuple(feller["cell"])])
                target = min(mature, key=lambda cell: (dist.get(cell, BIG), cell))
                if tuple(feller["cell"]) == target:
                    desired[self.feller_id] = f"CHOP {self.feller_id}"
                else:
                    desired[self.feller_id] = (
                        f"MOVE {self.feller_id} {target[0]} {target[1]}"
                    )
                reserved.add(target)

        outstanding = self.plants_successful + len(self.pending_cells)
        if (
            outstanding < self.policy.plant_count
            and turn <= self.policy.latest_plant_turn
        ):
            target = self._next_empty_cell(ref)
            planter = units[self.planter_id]
            idx = ITEM_INDEX[self.policy.species]
            if target is not None and self.planter_id not in desired:
                if planter["carry"][idx] > 0:
                    if tuple(planter["cell"]) == target:
                        desired[self.planter_id] = (
                            f"PLANT {self.planter_id} {self.policy.species}"
                        )
                    else:
                        desired[self.planter_id] = (
                            f"MOVE {self.planter_id} {target[0]} {target[1]}"
                        )
                    reserved.add(target)
                elif sum(planter["carry"]) > 0:
                    command = self._bank_command(ref, self.planter_id)
                    if command is not None:
                        desired[self.planter_id] = command[0]
                        if command[1] is not None:
                            reserved.add(command[1])
                elif ref.inv[idx] > 0:
                    if manhattan(tuple(planter["cell"]), tuple(ref.shacks[0])) <= 1:
                        desired[self.planter_id] = (
                            f"PICK {self.planter_id} {self.policy.species}"
                        )
                    else:
                        door = nearest_door(ref, planter)
                        if door is not None:
                            desired[self.planter_id] = (
                                f"MOVE {self.planter_id} {door[0]} {door[1]}"
                            )
                            reserved.add(door)

        # If one unit has both roles, felling/banking takes precedence.
        if self.planter_id == self.feller_id and self.feller_id in desired:
            desired = {self.feller_id: desired[self.feller_id]}
        return desired, reserved

    def _make_effect(self, ref, turn: int, uid: int, command: str) -> dict[str, Any]:
        fields = command.split()
        verb = fields[0]
        unit = ref.units[uid]
        effect: dict[str, Any] = {
            "turn": turn,
            "uid": uid,
            "verb": verb,
            "before_cell": tuple(unit["cell"]),
        }
        if verb == "MOVE":
            effect["target"] = (int(fields[2]), int(fields[3]))
        elif verb == "PICK":
            idx = ITEM_INDEX[fields[2]]
            effect["item"] = idx
            effect["before_carry"] = unit["carry"][idx]
        elif verb == "PLANT":
            effect["target"] = tuple(unit["cell"])
            effect["species"] = fields[2]
            self.pending_cells[tuple(unit["cell"])] = turn
            self.plants_issued += 1
        elif verb == "CHOP":
            target = tuple(unit["cell"])
            effect["target"] = target
            plant = ref.plants.get(target)
            effect["before_health"] = None if plant is None else plant["health"]
            effect["before_wood"] = unit["carry"][WOOD]
        elif verb == "DROP":
            effect["before_total"] = sum(unit["carry"])
            effect["before_bank_wood"] = ref.inv[WOOD]
        return effect

    def rewrite(self, turn: int, ref, champion_line: str) -> str:
        self._observe_previous(ref, turn)
        units = own_units(ref)
        if len(units) < 2:
            return champion_line

        if self.branch_turn is None:
            self.branch_turn = turn
            events = ref.spawn_events()
            self.second_event = dict(events[0]) if events else None
            self._choose_workers(ref)
            self._choose_cells(ref)
            self.events.append(
                {
                    "turn": turn,
                    "event": "branch",
                    "planter": self.planter_id,
                    "feller": self.feller_id,
                    "candidate_cells": [list(cell) for cell in self.candidate_cells],
                }
            )

        desired, reserved = self._desired(ref, turn)
        if not desired:
            # Enforce the experiment's no-third-troll boundary without changing
            # the ordinary champion stream (the champion presently emits none).
            fragments = command_fragments(champion_line)
            kept = []
            for fragment in fragments:
                if fragment.split()[0].upper() == "TRAIN":
                    self.suppressed_trains += 1
                    continue
                kept.append(fragment)
            return ";".join(kept) if kept else "WAIT"

        kept = []
        for fragment in command_fragments(champion_line):
            fields = fragment.split()
            verb = fields[0].upper()
            if verb == "TRAIN":
                self.suppressed_trains += 1
                continue
            uid = fragment_unit(fragment)
            if uid is not None and uid in desired:
                continue
            target = fragment_target(fragment, ref)
            if target is not None and target in reserved:
                continue
            kept.append(fragment)

        effects = []
        for uid in sorted(desired):
            command = desired[uid]
            kept.append(command)
            effects.append(self._make_effect(ref, turn, uid, command))
        self.last_effects = effects
        self.overrides += len(desired)
        return ";".join(kept) if kept else "WAIT"

    def summary(self) -> dict[str, Any]:
        return {
            "branch_turn": self.branch_turn,
            "second_event": self.second_event,
            "planter_id": self.planter_id,
            "feller_id": self.feller_id,
            "candidate_cells": [list(cell) for cell in self.candidate_cells],
            "orchard_cells": [list(cell) for cell in sorted(self.orchard_cells)],
            "plants_issued": self.plants_issued,
            "plants_successful": self.plants_successful,
            "fells_completed": self.fells_completed,
            "predicted_orchard_wood": self.predicted_orchard_wood,
            "realized_orchard_wood": self.realized_orchard_wood,
            "banked_by_overrides": self.banked_by_overrides,
            "overrides": self.overrides,
            "suppressed_trains": self.suppressed_trains,
            "abandoned": self.abandoned,
            "abandon_reason": self.abandon_reason,
            "events": self.events,
        }


def rewrite_for_test(
    champion_line: str,
    desired: dict[int, str],
    reserved: set[tuple[int, int]],
    ref,
) -> str:
    """Small pure seam used by regression tests."""
    kept = []
    for fragment in command_fragments(champion_line):
        uid = fragment_unit(fragment)
        if uid is not None and uid in desired:
            continue
        target = fragment_target(fragment, ref)
        if target is not None and target in reserved:
            continue
        kept.append(fragment)
    kept.extend(desired[uid] for uid in sorted(desired))
    return ";".join(kept) if kept else "WAIT"


def run_game(
    binary: Path,
    rec: dict[str, Any],
    draw: list[int],
    profile: str,
    policy: Policy | None,
    *,
    turns: int = TURNS,
    high_raid: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    ref = smoke.make_referee(rec, draw, profile)
    if high_raid:
        ref.profile = "chopper_aggressor"
        for unit in ref.units.values():
            if unit["player"] == 1:
                unit["speed"] = max(2, unit["speed"])
                unit["chop"] = max(2, unit["chop"])
                unit["cap"] = max(3, unit["cap"])
    controller = OrchardController(policy) if policy is not None else None
    header = ref.map_header()
    lines: list[str] = []
    with subprocess.Popen(
        [str(binary)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    ) as proc:
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write(header)
        proc.stdin.flush()
        for turn in range(1, turns + 1):
            proc.stdin.write(ref.turn_text())
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise ExperimentError(f"champion closed stdout at turn {turn}")
            champion_line = line.rstrip("\n")
            actual = (
                champion_line
                if controller is None
                else controller.rewrite(turn, ref, champion_line)
            )
            lines.append(actual)
            ref.apply(actual)
            ref.grow()
        proc.stdin.close()
        proc.wait(timeout=10)
        if proc.returncode not in (0, None):
            raise ExperimentError(f"champion process exited {proc.returncode}")

    spawns = ref.spawn_events()
    own = own_units(ref)
    result = {
        "turns_answered": len(lines),
        "execution_status": ref.execution_status,
        "referee_errors": dict(ref.error_counts),
        "own_score": score(ref.inv),
        "opp_score": score(ref.opp_inv),
        "margin": score(ref.inv) - score(ref.opp_inv),
        "own_inventory": list(ref.inv),
        "opp_inventory": list(ref.opp_inv),
        "own_units": len(own),
        "own_unit_stats": {
            str(uid): [
                unit["speed"],
                unit["cap"],
                unit["harvest"],
                unit["chop"],
            ]
            for uid, unit in sorted(own.items())
        },
        "spawn_events": spawns,
        "trains": training_fragments(lines),
        "command_sha256": sha_text("\n".join(lines) + "\n"),
        "high_raid": high_raid,
    }
    if controller is not None:
        result.update(controller.summary())
    second_turn = spawns[0]["turn"] if spawns else turns
    result["idle_max_post_second"] = idle_max(
        lines, sorted(own), second_turn + 1, min(turns, 280)
    )
    return result, lines


def load_policies(path: Path) -> list[Policy]:
    payload = json.loads(path.read_text())
    policies = [Policy(**item) for item in payload["policies"]]
    names = [policy.name for policy in policies]
    if len(names) != len(set(names)):
        raise ExperimentError("duplicate policy names")
    if not any(policy.no_plant for policy in policies):
        raise ExperimentError("NO_PLANT is missing")
    for policy in policies:
        if policy.species not in ITEM_INDEX:
            raise ExperimentError(f"unknown species in policy {policy.name}")
        if policy.plant_count < 0 or policy.plant_count > 8:
            raise ExperimentError(f"plant_count outside bounded vocabulary: {policy.name}")
        if policy.max_door_distance not in (2, 4):
            raise ExperimentError(f"distance outside geometry vocabulary: {policy.name}")
    return policies


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        rec = item["rec"]
        cases.append(
            {
                "index": len(cases),
                "map_hash": rec.get("map_hash", f"case-{len(cases)}"),
                "rec": rec,
                "draw": item["draw"],
                "profile": item["profile"],
            }
        )
    if not cases:
        raise ExperimentError("no cases")
    return cases


def mechanics_ok(result: dict[str, Any], turns: int) -> bool:
    return (
        result["turns_answered"] == turns
        and result["execution_status"] == "ok"
        and not result["referee_errors"]
        and result["own_units"] <= 2
        and len(result["spawn_events"]) <= 1
    )


def compare_candidate(
    case: dict[str, Any],
    policy: Policy,
    baseline: dict[str, Any],
    baseline_lines: list[str],
    result: dict[str, Any],
    lines: list[str],
) -> dict[str, Any]:
    b_spawns = baseline["spawn_events"]
    c_spawns = result["spawn_events"]
    same_second = b_spawns[:1] == c_spawns[:1]
    prefix_end = b_spawns[0]["turn"] if b_spawns else TURNS
    prefix_same = lines[:prefix_end] == baseline_lines[:prefix_end]
    idle_excess = {}
    for uid, value in result["idle_max_post_second"].items():
        base = baseline["idle_max_post_second"].get(uid, 0)
        if value > base + 20:
            idle_excess[uid] = {"candidate": value, "baseline": base}
    return {
        "case_index": case["index"],
        "map_hash": case["map_hash"],
        "profile": case["profile"],
        "policy": policy.name,
        "delta_own": result["own_score"] - baseline["own_score"],
        "delta_opp": result["opp_score"] - baseline["opp_score"],
        "delta_margin": result["margin"] - baseline["margin"],
        "baseline_own": baseline["own_score"],
        "candidate_own": result["own_score"],
        "baseline_margin": baseline["margin"],
        "candidate_margin": result["margin"],
        "prefix_end_turn": prefix_end,
        "prefix_same": prefix_same,
        "same_second_event": same_second,
        "mechanics_ok": mechanics_ok(result, TURNS),
        "idle_excess": idle_excess,
        "plants_successful": result.get("plants_successful", 0),
        "plants_issued": result.get("plants_issued", 0),
        "fells_completed": result.get("fells_completed", 0),
        "predicted_orchard_wood": result.get("predicted_orchard_wood", 0.0),
        "realized_orchard_wood": result.get("realized_orchard_wood", 0),
        "overrides": result.get("overrides", 0),
        "abandoned": result.get("abandoned", False),
        "abandon_reason": result.get("abandon_reason"),
        "candidate_command_sha256": result["command_sha256"],
        "baseline_command_sha256": baseline["command_sha256"],
    }


def summarize_policy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "delta_margin": bootstrap_ci([row["delta_margin"] for row in rows]),
        "delta_own": bootstrap_ci([row["delta_own"] for row in rows], seed=20260905),
        "plants_mean": statistics.fmean(row["plants_successful"] for row in rows),
        "fells_mean": statistics.fmean(row["fells_completed"] for row in rows),
        "mechanics_all": all(row["mechanics_ok"] and not row["idle_excess"] for row in rows),
        "prefix_all": all(row["prefix_same"] and row["same_second_event"] for row in rows),
    }


def choose_policy(
    names: list[str],
    rows_by_policy: dict[str, list[dict[str, Any]]],
    exclude_index: int | None = None,
) -> str:
    candidates = []
    for name in names:
        rows = [
            row
            for row in rows_by_policy[name]
            if exclude_index is None or row["case_index"] != exclude_index
        ]
        candidates.append(
            (
                statistics.fmean(row["delta_margin"] for row in rows),
                statistics.fmean(row["delta_own"] for row in rows),
                -statistics.fmean(row["plants_successful"] for row in rows),
                name,
            )
        )
    return max(candidates)[3]


def calibration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    predicted = sum(row["predicted_orchard_wood"] for row in rows)
    realized = sum(row["realized_orchard_wood"] for row in rows)
    ratios = []
    zero_realized = 0
    for row in rows:
        p = row["predicted_orchard_wood"]
        a = row["realized_orchard_wood"]
        if p <= 0:
            continue
        if a <= 0:
            zero_realized += 1
            ratios.append(1e9)
        else:
            ratios.append(p / a)
    ratios.sort()
    p90 = None if not ratios else ratios[min(len(ratios) - 1, math.ceil(0.9 * len(ratios)) - 1)]
    return {
        "predicted_total": predicted,
        "realized_total": realized,
        "aggregate_overstatement": None if realized <= 0 else predicted / realized,
        "p90_overstatement": p90,
        "predicted_games": len(ratios),
        "predicted_but_zero_realized_games": zero_realized,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    policies = load_policies(args.policies)
    cases = load_cases(args.records)
    champion_text = args.champion.read_text()
    champion_sha = sha_text(champion_text)

    with tempfile.TemporaryDirectory(prefix="champion-prefix-orchard-") as temp:
        binary = Path(temp) / "champion.bin"
        sh.compile_text(champion_text, binary, crate="champion_prefix_orchard")

        baselines: list[dict[str, Any]] = []
        baseline_lines: list[list[str]] = []
        for case in cases:
            result, lines = run_game(
                binary,
                case["rec"],
                case["draw"],
                case["profile"],
                None,
                turns=args.turns,
            )
            if not mechanics_ok(result, args.turns):
                raise DeadCondition(
                    f"unchanged champion mechanics failed on {case['map_hash']}: {result}"
                )
            baselines.append(result)
            baseline_lines.append(lines)

        rows_by_policy: dict[str, list[dict[str, Any]]] = {}
        invalid_policies: dict[str, list[str]] = {}
        for policy in policies:
            rows = []
            if policy.no_plant:
                for case, baseline in zip(cases, baselines):
                    rows.append(
                        {
                            "case_index": case["index"],
                            "map_hash": case["map_hash"],
                            "profile": case["profile"],
                            "policy": policy.name,
                            "delta_own": 0,
                            "delta_opp": 0,
                            "delta_margin": 0,
                            "baseline_own": baseline["own_score"],
                            "candidate_own": baseline["own_score"],
                            "baseline_margin": baseline["margin"],
                            "candidate_margin": baseline["margin"],
                            "prefix_end_turn": baseline["spawn_events"][0]["turn"]
                            if baseline["spawn_events"]
                            else args.turns,
                            "prefix_same": True,
                            "same_second_event": True,
                            "mechanics_ok": True,
                            "idle_excess": {},
                            "plants_successful": 0,
                            "plants_issued": 0,
                            "fells_completed": 0,
                            "predicted_orchard_wood": 0.0,
                            "realized_orchard_wood": 0,
                            "overrides": 0,
                            "abandoned": False,
                            "abandon_reason": None,
                            "candidate_command_sha256": baseline["command_sha256"],
                            "baseline_command_sha256": baseline["command_sha256"],
                        }
                    )
                rows_by_policy[policy.name] = rows
                continue

            reasons = []
            for case, baseline, b_lines in zip(cases, baselines, baseline_lines):
                result, lines = run_game(
                    binary,
                    case["rec"],
                    case["draw"],
                    case["profile"],
                    policy,
                    turns=args.turns,
                )
                row = compare_candidate(case, policy, baseline, b_lines, result, lines)
                if not row["prefix_same"] or not row["same_second_event"]:
                    raise DeadCondition(
                        f"prefix or second TRAIN changed under {policy.name} on "
                        f"{case['map_hash']}"
                    )
                if not row["mechanics_ok"]:
                    raise DeadCondition(
                        f"protocol/referee mechanics failed under {policy.name} on "
                        f"{case['map_hash']}"
                    )
                if row["idle_excess"]:
                    reasons.append(
                        f"{case['map_hash']}: new inactivity {row['idle_excess']}"
                    )
                rows.append(row)
            rows_by_policy[policy.name] = rows
            if reasons:
                invalid_policies[policy.name] = reasons

        valid_names = [
            policy.name
            for policy in policies
            if policy.name not in invalid_policies
        ]
        if not valid_names:
            raise DeadCondition("no policy, including NO_PLANT, survived mechanics")
        no_plant_name = next(policy.name for policy in policies if policy.no_plant)
        if no_plant_name not in valid_names:
            raise DeadCondition("NO_PLANT did not survive mechanics")

        policy_summaries = {
            name: summarize_policy(rows_by_policy[name]) for name in valid_names
        }
        global_choice = choose_policy(valid_names, rows_by_policy)

        loo_rows = []
        loo_choices = []
        for case in cases:
            chosen = choose_policy(valid_names, rows_by_policy, case["index"])
            row = rows_by_policy[chosen][case["index"]]
            loo_rows.append(row)
            loo_choices.append(chosen)

        primary_margin = bootstrap_ci(
            [row["delta_margin"] for row in loo_rows], seed=20260906
        )
        primary_own = bootstrap_ci(
            [row["delta_own"] for row in loo_rows], seed=20260907
        )

        per_map_choices = []
        for case in cases:
            options = [rows_by_policy[name][case["index"]] for name in valid_names]
            best = max(options, key=policy_key)
            per_map_choices.append(best["policy"])
        no_plant_count = sum(name == no_plant_name for name in per_map_choices)
        calib = calibration(loo_rows)

        dead_reasons = []
        if primary_margin["lower95"] is None or primary_margin["lower95"] <= 0:
            dead_reasons.append("paired final-margin lower 95% bound is not above zero")
        if primary_own["lower95"] is None or primary_own["lower95"] < 0:
            dead_reasons.append("paired own-score lower 95% bound is negative")
        if no_plant_count > len(cases) / 2:
            dead_reasons.append("NO_PLANT is the per-map oracle choice on most maps")
        p90 = calib["p90_overstatement"]
        if p90 is not None and p90 > 1.5:
            dead_reasons.append("90th-percentile wood overstatement exceeds 1.5x")

        result: dict[str, Any] = {
            "schema": "champion-prefix-orchard-v1",
            "task": "20260904-champion-prefix-orchard",
            "champion": {
                "path": str(args.champion.relative_to(REPO)),
                "sha256": champion_sha,
            },
            "records": {
                "path": str(args.records.relative_to(REPO)),
                "sha256": sha_file(args.records),
                "n": len(cases),
            },
            "policy_manifest": {
                "path": str(args.policies.relative_to(REPO)),
                "sha256": sha_file(args.policies),
            },
            "prefix": {
                "all_byte_identical_through_second_train": True,
                "second_train_events_unchanged": True,
            },
            "mechanics": {
                "baseline_all_clean": True,
                "invalid_policies": invalid_policies,
                "globally_valid_policies": valid_names,
            },
            "normal": {
                "policy_summaries": policy_summaries,
                "global_in_sample_choice": global_choice,
                "leave_one_map_out_choices": loo_choices,
                "leave_one_map_out_delta_margin": primary_margin,
                "leave_one_map_out_delta_own": primary_own,
                "per_map_oracle_choices": per_map_choices,
                "no_plant_count": no_plant_count,
                "no_plant_fraction": no_plant_count / len(cases),
                "calibration": calib,
                "rows": loo_rows,
                "all_policy_rows": rows_by_policy,
            },
            "high_raid": None,
            "dead_reasons_before_high_raid": dead_reasons,
        }

        # The card says stop immediately on a registered dead condition.
        if dead_reasons:
            result["verdict"] = "DEAD_ON_NORMAL_PAIRED_REPLAY"
            return result

        # High-raid stress: freeze each leave-one-map-out policy choice and
        # rerun against a faster chop-2/carry-3 aggressor.  No retuning.
        high_rows = []
        stress_baselines = []
        for case in cases:
            base, b_lines = run_game(
                binary,
                case["rec"],
                case["draw"],
                "chopper_aggressor",
                None,
                turns=args.turns,
                high_raid=True,
            )
            if not mechanics_ok(base, args.turns):
                raise DeadCondition(
                    f"high-raid baseline mechanics failed on {case['map_hash']}"
                )
            stress_baselines.append((base, b_lines))

        by_name = {policy.name: policy for policy in policies}
        for case, chosen, (base, b_lines) in zip(cases, loo_choices, stress_baselines):
            policy = by_name[chosen]
            if policy.no_plant:
                row = {
                    "case_index": case["index"],
                    "map_hash": case["map_hash"],
                    "profile": "high_raid",
                    "policy": chosen,
                    "delta_own": 0,
                    "delta_opp": 0,
                    "delta_margin": 0,
                    "plants_successful": 0,
                    "fells_completed": 0,
                    "predicted_orchard_wood": 0.0,
                    "realized_orchard_wood": 0,
                    "prefix_same": True,
                    "same_second_event": True,
                    "mechanics_ok": True,
                    "idle_excess": {},
                }
            else:
                candidate, lines = run_game(
                    binary,
                    case["rec"],
                    case["draw"],
                    "chopper_aggressor",
                    policy,
                    turns=args.turns,
                    high_raid=True,
                )
                row = compare_candidate(case, policy, base, b_lines, candidate, lines)
                if (
                    not row["prefix_same"]
                    or not row["same_second_event"]
                    or not row["mechanics_ok"]
                    or row["idle_excess"]
                ):
                    raise DeadCondition(
                        f"high-raid mechanics/prefix failed on {case['map_hash']}"
                    )
            high_rows.append(row)

        high_margin = bootstrap_ci(
            [row["delta_margin"] for row in high_rows], seed=20260908
        )
        high_own = bootstrap_ci(
            [row["delta_own"] for row in high_rows], seed=20260909
        )
        high_calib = calibration(high_rows)
        high_dead = []
        if high_margin["mean"] is None or high_margin["mean"] <= 0:
            high_dead.append("mean paired margin disappears under high raid")
        if high_own["mean"] is None or high_own["mean"] < 0:
            high_dead.append("mean paired own score is negative under high raid")
        hp90 = high_calib["p90_overstatement"]
        if hp90 is not None and hp90 > 1.5:
            high_dead.append("high-raid p90 wood overstatement exceeds 1.5x")
        result["high_raid"] = {
            "opponent": "chopper_aggressor with speed>=2, chop>=2, carry>=3",
            "delta_margin": high_margin,
            "delta_own": high_own,
            "calibration": high_calib,
            "rows": high_rows,
            "dead_reasons": high_dead,
        }
        if high_dead:
            result["verdict"] = "DEAD_UNDER_HIGH_RAID"
        else:
            result["verdict"] = (
                "MECHANISM_POSITIVE_SOFT_STOP"
                if primary_margin["mean"] < 15
                else "MECHANISM_POSITIVE_WORTH_FRESH_HOLDOUT"
            )
        return result


def render_markdown(result: dict[str, Any]) -> str:
    normal = result.get("normal", {})
    margin = normal.get("leave_one_map_out_delta_margin", {})
    own = normal.get("leave_one_map_out_delta_own", {})
    lines = [
        "# Champion-prefix orchard experiment",
        "",
        f"**Verdict: `{result.get('verdict', 'ERROR')}`**",
        "",
        "The unchanged champion was the executable in both worlds. The candidate",
        "forwarded its stdout byte-for-byte through the champion's own second",
        "`TRAIN`; only the post-prefix orchard macros could be overridden. Third",
        "training was disabled and `NO_PLANT` was always legal.",
        "",
        "## Registered gates",
        "",
        f"- Prefix byte-identical: **{result.get('prefix', {}).get('all_byte_identical_through_second_train')}**",
        f"- Second TRAIN unchanged: **{result.get('prefix', {}).get('second_train_events_unchanged')}**",
        f"- Baseline mechanics clean: **{result.get('mechanics', {}).get('baseline_all_clean')}**",
        f"- Globally valid policies: `{', '.join(result.get('mechanics', {}).get('globally_valid_policies', []))}`",
        "",
        "## Primary result: leave-one-map-out policy choice",
        "",
        f"- paired final margin: mean **{margin.get('mean')}**, 95% bootstrap interval "
        f"**[{margin.get('lower95')}, {margin.get('upper95')}]**, n={margin.get('n')};",
        f"- paired own score: mean **{own.get('mean')}**, 95% bootstrap interval "
        f"**[{own.get('lower95')}, {own.get('upper95')}]**, n={own.get('n')};",
        f"- `NO_PLANT` was the per-map oracle choice on "
        f"**{normal.get('no_plant_count')}/{result.get('records', {}).get('n')}** maps;",
        f"- in-sample global policy: `{normal.get('global_in_sample_choice')}`.",
        "",
        "The leave-one-map-out number, rather than the per-map oracle upper bound,",
        "is the primary mechanism estimate. All maps are still development data.",
        "",
        "## Wood calibration",
        "",
        "```json",
        json.dumps(normal.get("calibration"), indent=2, sort_keys=True),
        "```",
        "",
    ]
    if result.get("high_raid") is not None:
        high = result["high_raid"]
        lines += [
            "## High-raid stress",
            "",
            f"- paired margin: `{high['delta_margin']}`",
            f"- paired own score: `{high['delta_own']}`",
            f"- calibration: `{high['calibration']}`",
            f"- dead reasons: `{high['dead_reasons']}`",
            "",
        ]
    reasons = result.get("dead_reasons_before_high_raid", [])
    if reasons:
        lines += [
            "## Why execution stopped",
            "",
            *[f"- {reason}" for reason in reasons],
            "",
            "The card requires an immediate stop on any of these conditions, so no",
            "high-raid rerun, panel, holdout, ladder, platform, Arena or cluster work",
            "followed.",
            "",
        ]
    lines += [
        "## Reproduction",
        "",
        "```bash",
        "bash chatgpt_1/champion-prefix-orchard/run.sh",
        "```",
        "",
        "Machine-readable rows and every policy summary are in `results/result.json`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--champion",
        type=Path,
        default=REPO
        / "local_claude_1"
        / "denial-ablation"
        / "champion-denial-off-v6-instrument.rs",
    )
    parser.add_argument(
        "--records",
        type=Path,
        default=REPO
        / "local_claude_1"
        / "third-troll"
        / "smoke-maps-seed0.jsonl",
    )
    parser.add_argument("--policies", type=Path, default=HERE / "policies.json")
    parser.add_argument("--turns", type=int, default=TURNS)
    parser.add_argument("--out", type=Path, default=HERE / "results" / "result.json")
    parser.add_argument("--report", type=Path, default=HERE / "RESULTS.md")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = run(args)
    except Exception as exc:
        payload = {
            "schema": "champion-prefix-orchard-v1",
            "task": "20260904-champion-prefix-orchard",
            "verdict": "EXECUTION_ERROR",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        args.report.write_text(render_markdown(payload))
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.report.write_text(render_markdown(result))
    print(json.dumps({k: result[k] for k in ("verdict", "prefix", "mechanics")}, indent=2))
    print(json.dumps(result["normal"]["leave_one_map_out_delta_margin"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
