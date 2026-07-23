"""Read-only terminal and completion-race telemetry for simulator studies."""

from __future__ import annotations

from bot.main import bfs_distances
from sim.engine import ITEM_INDEX, stall_reason, stuck_players

FRUIT_KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")


def ceil_div(value: int, divisor: int) -> int:
    if divisor <= 0:
        return 10_000
    return (value + divisor - 1) // divisor


def scoring_value(stock: list[int]) -> int:
    return sum(stock[:4]) + 4 * stock[ITEM_INDEX["WOOD"]]


def cashout_eta(game, unit) -> int | None:
    """Commands needed to reach a home door and DROP the current cargo."""

    distance = bfs_distances(game.walkable, [game.shacks[unit.player]]).get(unit.pos)
    if distance is None:
        return None
    travel = ceil_div(max(distance - 1, 0), unit.ms)
    return travel + 1


def focus_kind(game, player: int) -> str:
    """Reproduce the live bot's immutable LEMON/PLUM opening focus choice."""

    sx, sy = game.shacks[player]
    doors = [
        cell
        for cell in ((sx, sy + 1), (sx + 1, sy), (sx, sy - 1), (sx - 1, sy))
        if cell in game.walkable
    ]
    distance = bfs_distances(game.walkable, doors)

    def total(kind: str) -> int:
        return sum(
            distance.get(plant.pos, 10_000)
            for plant in game.plants
            if plant.type == kind
        )

    return min(("LEMON", "PLUM"), key=total)


def static_completion(game, unit, plant) -> dict | None:
    """Single-worker, no-growth arrival/fell/bank estimate for one tree."""

    if unit.chop <= 0 or unit.free <= 0:
        return None
    arrival_distance = bfs_distances(game.walkable, [unit.pos]).get(plant.pos)
    if arrival_distance is None:
        return None
    sx, sy = game.shacks[unit.player]
    doors = [
        cell
        for cell in ((sx, sy + 1), (sx + 1, sy), (sx, sy - 1), (sx - 1, sy))
        if cell in game.walkable
    ]
    return_distance = bfs_distances(game.walkable, doors).get(plant.pos)
    if return_distance is None:
        return None
    arrival_eta = ceil_div(arrival_distance, unit.ms)
    fell_eta = arrival_eta + ceil_div(max(plant.health, 1), unit.chop)
    bank_eta = fell_eta + ceil_div(return_distance, unit.ms) + 1
    wood = min(plant.size, unit.free)
    return {
        "unit": unit.id,
        "player": unit.player,
        "arrival_eta": arrival_eta,
        "fell_eta": fell_eta,
        "bank_eta": bank_eta,
        "wood": wood,
        "value": 4 * wood,
    }


def selected_tree_races(
    game,
    player: int,
    commands: list[str],
    selected_focus_kind: str,
) -> list[dict]:
    """Describe completion races for selected MOVE-to-tree and CHOP actions."""

    units = {unit.id: unit for unit in game.units}
    plants = {plant.pos: plant for plant in game.plants}
    opponent_units = [unit for unit in game.units if unit.player == 1 - player]
    opponent_count = len(opponent_units)
    races = []
    for command in commands:
        fields = command.split()
        if len(fields) < 2 or fields[0].upper() not in ("MOVE", "CHOP"):
            continue
        try:
            unit_id = int(fields[1])
        except ValueError:
            continue
        unit = units.get(unit_id)
        if unit is None or unit.player != player:
            continue
        if fields[0].upper() == "CHOP":
            target = unit.pos
        elif len(fields) >= 4:
            try:
                target = (int(fields[2]), int(fields[3]))
            except ValueError:
                continue
        else:
            continue
        plant = plants.get(target)
        if plant is None:
            continue
        selected = static_completion(game, unit, plant)
        opponents = [
            completion
            for other in opponent_units
            if (completion := static_completion(game, other, plant)) is not None
        ]
        opponent = min(opponents, key=lambda item: (item["bank_eta"], item["fell_eta"])) if opponents else None
        races.append(
            {
                "command": command,
                "tree": {
                    "type": plant.type,
                    "x": plant.x,
                    "y": plant.y,
                    "size": plant.size,
                    "health": plant.health,
                    "fruits": plant.fruits,
                },
                "focus_kind": selected_focus_kind,
                "focus_gate_active": (
                    plant.type == selected_focus_kind and opponent_count <= 2
                ),
                "opponent_units": opponent_count,
                "selected": selected,
                "opponent_fastest": opponent,
                "opponent_beats_selected_fell": bool(
                    selected and opponent and opponent["fell_eta"] < selected["fell_eta"]
                ),
                "opponent_beats_selected_bank": bool(
                    selected and opponent and opponent["bank_eta"] < selected["bank_eta"]
                ),
            }
        )
    return races


def terminal_snapshot(game, turns_until_end: int) -> dict:
    """Summarize score, seed, cargo, cash-out, and end-rule state without mutation."""

    players = []
    for player in (0, 1):
        carriers = []
        for unit in game.units:
            if unit.player != player or scoring_value(unit.carry) <= 0:
                continue
            eta = cashout_eta(game, unit)
            value = scoring_value(unit.carry)
            carriers.append(
                {
                    "unit": unit.id,
                    "pos": [unit.x, unit.y],
                    "ms": unit.ms,
                    "carry": list(unit.carry),
                    "value": value,
                    "cashout_eta": eta,
                    "within_implied_grace": eta is not None and eta <= turns_until_end,
                }
            )
        inventory = game.inventories[player]
        carried_value = sum(carrier["value"] for carrier in carriers)
        players.append(
            {
                "score": game.scores[player],
                "banked_fruit": sum(inventory[:4]),
                "banked_fruit_by_kind": dict(zip(FRUIT_KINDS, inventory[:4])),
                "banked_wood": inventory[ITEM_INDEX["WOOD"]],
                "carried_value": carried_value,
                "carried_seed": sum(unit.carry[index] for unit in game.units if unit.player == player for index in range(4)),
                "projected_score": game.scores[player] + carried_value,
                "value_within_implied_grace": sum(
                    carrier["value"]
                    for carrier in carriers
                    if carrier["within_implied_grace"]
                ),
                "carriers": carriers,
            }
        )
    stuck = stuck_players(game)
    return {
        "resolved_turn": game.turn - 1,
        "scores": list(game.scores),
        "margin_player_0": game.scores[0] - game.scores[1],
        "projected_margin_player_0": players[0]["projected_score"]
        - players[1]["projected_score"],
        "plants": len(game.plants),
        "ripe_plants": sum(plant.fruits > 0 for plant in game.plants),
        "implied_grace": turns_until_end,
        "stuck": list(stuck),
        "stall_reason": stall_reason(game, turns_until_end),
        "players": players,
    }
