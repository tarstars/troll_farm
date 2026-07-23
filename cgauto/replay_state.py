"""Decode exact logical Troll Farm state from CodinGame replay ``frame.diff`` fields."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from sim.engine import recompute_scores
from sim.state import GameState, SimPlant, SimUnit

PLANT_TYPES = ("PLUM", "LEMON", "APPLE", "BANANA")
PLANT_HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}


def b36(value: str) -> int:
    return int(value, 36)


def view_payload(view: str) -> dict | None:
    if "{" not in view:
        return None
    return json.loads(view.split("\n", 1)[1])


class DiffDecoder:
    def __init__(self) -> None:
        self.units: dict[int, dict] = {}
        self.plants: dict[int, dict] = {}
        self.unknown_updates: list[dict] = []

    def apply(self, diff: str, frame: int) -> None:
        for raw in diff.split(";"):
            fields = raw.strip().split()
            if len(fields) < 2:
                continue
            entity = int(fields[0])
            if fields[1] == "W":
                self.units[entity] = self._new_unit(fields[2])
            elif fields[1] == "P":
                self.plants[entity] = self._new_plant(fields[2])
            elif entity in self.units:
                self._update_unit(entity, fields[1:], frame)
            elif entity in self.plants:
                self._update_plant(entity, fields[1:], frame)
            else:
                self.unknown_updates.append(
                    {"frame": frame, "entity": entity, "fields": fields[1:]}
                )

    def tick_existing_plants(self) -> None:
        """Advance clocks that the visual diff deliberately leaves implicit.

        Replay diffs report the initial and reset cooldowns, but omit ordinary
        countdown and growth updates.  Existing plants tick after actions each
        turn.  Advancing first and then applying the frame diff lets explicit
        post-turn harvest/reset values override the inferred clock state.
        Newly-created plants are added by the subsequent diff with their exact
        post-tick encoding, so they are not advanced twice.
        """

        for plant in self.plants.values():
            if not plant["active"]:
                continue
            if plant["cooldown"] > 0:
                plant["cooldown"] -= 1
            if plant["cooldown"] == 0 and plant["health"] > 0 and plant["stage"] < 7:
                if plant["stage"] < 4:
                    plant["health"] += PLANT_HEALTH_SLOPE[plant["type"]]
                plant["stage"] += 1
                plant["size"] = min(plant["stage"], 4)
                plant["fruits"] = max(plant["stage"] - 4, 0)
                plant["cooldown"] = plant["cooldown_effective"]

    def apply_known_chops(self, unit_ids: list[int]) -> None:
        """Apply recorded CHOP damage before inferring an implicit plant tick.

        The visual diff stores absolute changes from one displayed state to the
        next.  When chop damage exactly cancels health added by same-turn growth,
        it emits no ``h`` token.  Command context is therefore required to
        reconstruct that transition without inventing health.
        """

        units_by_id = {
            unit["id"]: unit for unit in self.units.values() if unit["active"]
        }
        plants_by_cell = {
            (plant["x"], plant["y"]): plant
            for plant in self.plants.values()
            if plant["active"]
        }
        for unit_id in unit_ids:
            unit = units_by_id.get(unit_id)
            if unit is None or unit["chop"] <= 0:
                continue
            plant = plants_by_cell.get((unit["x"], unit["y"]))
            if plant is None or not plant["active"]:
                continue
            plant["health"] = max(plant["health"] - unit["chop"], 0)
            if plant["health"] == 0:
                plant["active"] = False

    @staticmethod
    def _new_unit(encoded: str) -> dict:
        if len(encoded) != 8:
            raise ValueError(f"bad unit encoding: {encoded!r}")
        values = [b36(char) for char in encoded]
        return {
            "id": values[0],
            "x": values[1],
            "y": values[2],
            "player": values[3],
            "ms": values[4],
            "cc": values[5],
            "hp": values[6],
            "chop": values[7],
            "carry": [0] * 6,
            "active": True,
        }

    @staticmethod
    def _new_plant(encoded: str) -> dict:
        if len(encoded) != 7:
            raise ValueError(f"bad plant encoding: {encoded!r}")
        x, y, kind, stage, cooldown, health, cooldown_effective = (
            b36(char) for char in encoded
        )
        return {
            "type": PLANT_TYPES[kind],
            "x": x,
            "y": y,
            "stage": stage,
            "size": min(stage, 4),
            "fruits": max(stage - 4, 0),
            "cooldown": cooldown,
            "health": health,
            "cooldown_effective": cooldown_effective,
            "active": health > 0,
        }

    def _update_unit(self, entity: int, tokens: list[str], frame: int) -> None:
        unit = self.units[entity]
        for token in tokens:
            if token == "D":
                unit["active"] = False
            elif token.startswith("x") and len(token) > 1:
                unit["x"] = b36(token[1:])
            elif token.startswith("y") and len(token) > 1:
                unit["y"] = b36(token[1:])
            elif token[0] in "012345" and len(token) > 1:
                unit["carry"][int(token[0])] = b36(token[1:])
            else:
                self.unknown_updates.append(
                    {"frame": frame, "entity": entity, "fields": [token]}
                )

    def _update_plant(self, entity: int, tokens: list[str], frame: int) -> None:
        plant = self.plants[entity]
        for token in tokens:
            if token == "D":
                plant["active"] = False
            elif token.startswith("h") and len(token) > 1:
                plant["health"] = b36(token[1:])
                plant["active"] = plant["health"] > 0
            elif token.startswith("s") and len(token) > 1:
                plant["stage"] = b36(token[1:])
                plant["size"] = min(plant["stage"], 4)
                plant["fruits"] = max(plant["stage"] - 4, 0)
            elif token.startswith("c") and len(token) > 1:
                plant["cooldown"] = b36(token[1:])
            else:
                self.unknown_updates.append(
                    {"frame": frame, "entity": entity, "fields": [token]}
                )

    def snapshot(self, resolved_turn: int, inventories: list[list[int]]) -> dict:
        units = [copy.deepcopy(unit) for unit in self.units.values() if unit["active"]]
        plants = [copy.deepcopy(plant) for plant in self.plants.values() if plant["active"]]
        for row in units:
            row.pop("active", None)
        for row in plants:
            row.pop("active", None)
        units.sort(key=lambda unit: unit["id"])
        # Dict insertion order is the referee's entity-creation/input order.
        # Preserve it: the live bot intentionally lets input order break a few
        # otherwise exact candidate ties.
        return {
            "resolved_turn": resolved_turn,
            "inventories": copy.deepcopy(inventories),
            "units": units,
            "plants": plants,
        }


def decode_replay(
    path: Path, *, chop_unit_ids_by_turn: list[list[int]] | None = None
) -> dict:
    replay = json.loads(path.read_text())
    initial = view_payload(replay["frames"][0]["view"])
    if initial is None:
        raise ValueError(f"missing initial replay payload: {path}")
    header, *rows = initial["global"]["inputmodule"].splitlines()
    width, height = (int(value) for value in header.split())
    decoder = DiffDecoder()
    decoder.apply(initial["frame"].get("diff", ""), 0)
    inventories = [
        [int(value) for value in line.split()]
        for line in initial["frame"]["inputmodule"].splitlines()
    ]
    states = [decoder.snapshot(0, inventories)]
    resolved_turn = 0
    for frame_index, frame in enumerate(replay["frames"][1:], 1):
        if not frame.get("keyframe"):
            continue
        payload = view_payload(frame.get("view") or "")
        if payload is None:
            continue
        if chop_unit_ids_by_turn is not None and resolved_turn < len(
            chop_unit_ids_by_turn
        ):
            decoder.apply_known_chops(chop_unit_ids_by_turn[resolved_turn])
        decoder.tick_existing_plants()
        decoder.apply(payload.get("diff", ""), frame_index)
        if payload.get("inputmodule"):
            inventories = [
                [int(value) for value in line.split()]
                for line in payload["inputmodule"].splitlines()
            ]
        resolved_turn += 1
        states.append(decoder.snapshot(resolved_turn, inventories))
    return {
        "game_id": replay["gameId"],
        "scores": [int(score) for score in replay["scores"]],
        "ranks": replay["ranks"],
        "map": {"width": width, "height": height, "rows": rows},
        "states": states,
        "unknown_updates": decoder.unknown_updates,
    }


def to_game_state(map_data: dict, state: dict) -> GameState:
    walkable = set()
    iron = set()
    water = set()
    shacks = [None, None]
    for y, row in enumerate(map_data["rows"]):
        for x, char in enumerate(row):
            cell = (x, y)
            if char == "0":
                shacks[0] = cell
            elif char == "1":
                shacks[1] = cell
            elif char == ".":
                walkable.add(cell)
            elif char == "+":
                iron.add(cell)
            elif char == "~":
                water.add(cell)
    units = [
        SimUnit(
            unit["id"],
            unit["player"],
            unit["x"],
            unit["y"],
            unit["ms"],
            unit["cc"],
            unit["hp"],
            unit["chop"],
            list(unit["carry"]),
        )
        for unit in state["units"]
    ]
    plants = [
        SimPlant(
            plant["type"],
            plant["x"],
            plant["y"],
            plant["size"],
            plant["health"],
            plant["fruits"],
            plant["cooldown"],
        )
        for plant in state["plants"]
    ]
    game = GameState(
        width=map_data["width"],
        height=map_data["height"],
        walkable=walkable,
        shacks=shacks,
        inventories=copy.deepcopy(state["inventories"]),
        units=units,
        plants=plants,
        scores=[0, 0],
        turn=state["resolved_turn"] + 1,
        next_id=max((unit.id for unit in units), default=-1) + 1,
        iron=iron,
        water=water,
    )
    recompute_scores(game)
    return game
