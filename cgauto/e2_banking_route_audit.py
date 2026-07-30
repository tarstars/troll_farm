#!/usr/bin/env python3
"""Audit exact-resident bank-return door persistence and hindsight route regret.

This is a behavior-neutral local diagnostic. It observes the current live artifact in the
deterministic simulator on reused seeds; it does not modify the bot, select a candidate, or
estimate Arena rating.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
from dataclasses import asdict, dataclass, field
import hashlib
from itertools import product
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import bfs_distances  # noqa: E402
from cgauto.idle_harvest_study import (  # noqa: E402
    BotSession,
    action_commands,
    compile_source,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

LIVE_SOURCE = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
LIVE_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def ceil_div(value: int, divisor: int) -> int:
    if divisor <= 0:
        raise ValueError("divisor must be positive")
    return (value + divisor - 1) // divisor


def home_doors(game, player: int) -> tuple[tuple[int, int], ...]:
    shack = game.shacks[player]
    return tuple(
        (shack[0] + dx, shack[1] + dy)
        for dx, dy in NEIGHBORS
        if (shack[0] + dx, shack[1] + dy) in game.walkable
    )


@dataclass(frozen=True)
class Action:
    verb: str
    unit_id: int
    raw: str
    target: tuple[int, int] | None = None


def actions_by_unit(commands: list[str], units: list) -> dict[int, Action]:
    """Bind id-less WAIT actions to the resident's sorted unit-action slots."""

    ordered = sorted(units, key=lambda unit: unit.id)
    slot = 0
    result: dict[int, Action] = {}
    for command in commands:
        fields = command.split()
        if not fields:
            continue
        verb = fields[0].upper()
        if verb in {"MSG", "TRAIN"}:
            continue
        if slot >= len(ordered):
            raise ValueError(f"more unit actions than units: {commands}")
        expected = ordered[slot].id
        if verb == "WAIT":
            unit_id = expected
            target = None
        else:
            if len(fields) < 2:
                raise ValueError(f"malformed action: {command}")
            unit_id = int(fields[1])
            if unit_id != expected:
                raise ValueError(
                    f"action order/id mismatch: expected {expected}, saw {unit_id}"
                )
            target = (
                (int(fields[2]), int(fields[3]))
                if verb == "MOVE" and len(fields) == 4
                else None
            )
        result[unit_id] = Action(verb, unit_id, command, target)
        slot += 1
    return result


def semantic_target(action: Action | None, unit) -> tuple[int, int] | None:
    if action is None or action.verb == "WAIT":
        return None
    if action.verb == "MOVE":
        return action.target
    if action.verb in {"DROP", "CHOP", "HARVEST", "MINE", "PICK", "PLANT"}:
        return unit.pos
    return None


def _cell(value: tuple[int, int] | None) -> list[int] | None:
    return list(value) if value is not None else None


@dataclass
class RouteEpisode:
    episode_id: str
    seed: int
    seat: int
    unit_id: int
    start_turn: int
    start_cell: tuple[int, int]
    speed: int
    cargo_start: list[int]
    cargo_total: int
    door_targets: list[tuple[int, int]] = field(default_factory=list)
    target_changes: int = 0
    bank_move_turns: int = 0
    actual_inbound_steps: int = 0
    immediate_checks: int = 0
    immediate_positive_checks: int = 0
    immediate_eta_regret_sum: int = 0
    immediate_eta_regret_max: int = 0
    immediate_unidentified_checks: int = 0
    deposit_turn: int | None = None
    deposit_door: tuple[int, int] | None = None
    deposited_cargo: int | None = None
    post_deposit_wait_turns: int = 0
    next_action_turn: int | None = None
    next_action: str | None = None
    next_target: tuple[int, int] | None = None
    chosen_static_roundtrip_cells: int | None = None
    best_static_roundtrip_cells: int | None = None
    hindsight_cell_regret: int | None = None
    chosen_static_roundtrip_eta: int | None = None
    best_static_roundtrip_eta: int | None = None
    hindsight_eta_regret: int | None = None
    total_hindsight_eta_regret: int | None = None
    total_hindsight_cell_regret: int | None = None
    status: str = "returning"
    note: str | None = None

    def as_json(self) -> dict:
        payload = asdict(self)
        for key in ("start_cell", "deposit_door", "next_target"):
            payload[key] = _cell(getattr(self, key))
        payload["door_targets"] = [list(cell) for cell in self.door_targets]
        return payload


def immediate_door_check(
    game,
    player: int,
    unit,
    chosen: tuple[int, int],
    actions: dict[int, Action],
) -> dict:
    doors = home_doors(game, player)
    distances = bfs_distances(game.walkable, [unit.pos])
    occupied = {
        other.pos
        for other in game.units
        if other.player == player and other.id != unit.id
    }
    reserved = {
        target
        for other in game.units
        if other.player == player and other.id != unit.id
        if (target := semantic_target(actions.get(other.id), other)) is not None
    }
    eligible = [
        door
        for door in doors
        if door in distances
        and (door == unit.pos or door not in occupied)
        and door not in reserved
    ]
    chosen_eta = (
        ceil_div(distances[chosen], unit.ms) if chosen in distances else None
    )
    best_eta = min(
        (ceil_div(distances[door], unit.ms) for door in eligible), default=None
    )
    identifiable = chosen_eta is not None and best_eta is not None and chosen in eligible
    regret = chosen_eta - best_eta if identifiable else None
    return {
        "chosen": list(chosen),
        "eligible": [list(door) for door in eligible],
        "chosen_eta": chosen_eta,
        "best_eta": best_eta,
        "identifiable": identifiable,
        "eta_regret": regret,
    }


def joint_assignment_check(
    game,
    player: int,
    actions: dict[int, Action],
    episode_ids: dict[int, str],
) -> dict | None:
    units = {
        unit.id: unit for unit in game.units if unit.player == player
    }
    movers = [
        units[unit_id]
        for unit_id in sorted(episode_ids)
        if unit_id in units
        and actions.get(unit_id) is not None
        and actions[unit_id].verb == "MOVE"
        and actions[unit_id].target in home_doors(game, player)
    ]
    if len(movers) < 2:
        return None
    doors = home_doors(game, player)
    mover_ids = {unit.id for unit in movers}
    fixed_targets = {
        target
        for unit in units.values()
        if unit.id not in mover_ids
        if (target := semantic_target(actions.get(unit.id), unit)) is not None
    }
    choices: dict[int, list[tuple[tuple[int, int], int]]] = {}
    for unit in movers:
        distances = bfs_distances(game.walkable, [unit.pos])
        occupied = {
            other.pos
            for other in units.values()
            if other.id != unit.id
        }
        choices[unit.id] = [
            (door, ceil_div(distances[door], unit.ms))
            for door in doors
            if door in distances
            and (door == unit.pos or door not in occupied)
            and door not in fixed_targets
        ]
    combinations = []
    for assignment in product(*(choices[unit.id] for unit in movers)):
        selected = [entry[0] for entry in assignment]
        if len(set(selected)) != len(selected):
            continue
        combinations.append((sum(entry[1] for entry in assignment), selected))
    actual = [actions[unit.id].target for unit in movers]
    actual_eta = 0
    actual_identifiable = True
    for unit, chosen in zip(movers, actual):
        match = next((eta for door, eta in choices[unit.id] if door == chosen), None)
        if match is None:
            actual_identifiable = False
            break
        actual_eta += match
    best_eta = min((value for value, _ in combinations), default=None)
    identifiable = (
        actual_identifiable
        and best_eta is not None
        and len(set(actual)) == len(actual)
    )
    return {
        "turn": game.turn,
        "unit_ids": [unit.id for unit in movers],
        "episode_ids": [episode_ids[unit.id] for unit in movers],
        "actual_doors": [list(cell) for cell in actual],
        "actual_eta": actual_eta if actual_identifiable else None,
        "best_eta": best_eta,
        "identifiable": identifiable,
        "eta_regret": actual_eta - best_eta if identifiable else None,
    }


class SideAudit:
    def __init__(self, seed: int, seat: int, walkable: set, shack) -> None:
        self.seed = seed
        self.seat = seat
        self.walkable = set(walkable)
        self.shack = shack
        self.episodes: list[RouteEpisode] = []
        self.active: dict[int, RouteEpisode] = {}
        self.awaiting: dict[int, RouteEpisode] = {}
        self.joint_checks: list[dict] = []
        self.ambiguous_carrying_door_moves = 0
        self._sequence = 0

    def _new_episode(self, unit, turn: int) -> RouteEpisode:
        episode = RouteEpisode(
            episode_id=f"{self.seed}:{self.seat}:{self._sequence}",
            seed=self.seed,
            seat=self.seat,
            unit_id=unit.id,
            start_turn=turn,
            start_cell=unit.pos,
            speed=unit.ms,
            cargo_start=list(unit.carry),
            cargo_total=unit.total,
        )
        self._sequence += 1
        self.episodes.append(episode)
        self.active[unit.id] = episode
        return episode

    def _record_move(
        self,
        episode: RouteEpisode,
        before,
        after,
        unit,
        action: Action,
        actions: dict[int, Action],
    ) -> None:
        assert action.target is not None
        if episode.door_targets and episode.door_targets[-1] != action.target:
            episode.target_changes += 1
        episode.door_targets.append(action.target)
        episode.bank_move_turns += 1
        after_unit = next(
            (
                candidate
                for candidate in after.units
                if candidate.player == self.seat and candidate.id == unit.id
            ),
            None,
        )
        if after_unit is not None:
            episode.actual_inbound_steps += abs(after_unit.x - unit.x) + abs(
                after_unit.y - unit.y
            )
        check = immediate_door_check(before, self.seat, unit, action.target, actions)
        episode.immediate_checks += 1
        if not check["identifiable"]:
            episode.immediate_unidentified_checks += 1
        else:
            regret = int(check["eta_regret"])
            episode.immediate_eta_regret_sum += regret
            episode.immediate_eta_regret_max = max(
                episode.immediate_eta_regret_max, regret
            )
            if regret > 0:
                episode.immediate_positive_checks += 1

    def _record_drop(
        self, episode: RouteEpisode, before, after, unit, action: Action
    ) -> None:
        doors = home_doors(before, self.seat)
        after_unit = next(
            (
                candidate
                for candidate in after.units
                if candidate.player == self.seat and candidate.id == unit.id
            ),
            None,
        )
        if unit.pos not in doors or after_unit is None or after_unit.total >= unit.total:
            episode.status = "unidentified_drop"
            episode.note = "DROP did not bind a positive cargo deposit at a home door"
            self.active.pop(unit.id, None)
            return
        episode.deposit_turn = before.turn
        episode.deposit_door = unit.pos
        episode.deposited_cargo = unit.total - after_unit.total
        episode.status = "deposited_awaiting_outbound"
        self.active.pop(unit.id, None)
        self.awaiting[unit.id] = episode

    def _bind_outbound(self, episode: RouteEpisode, game, unit, action: Action) -> None:
        if action.verb == "WAIT":
            episode.post_deposit_wait_turns += 1
            return
        if action.verb == "DROP":
            episode.post_deposit_wait_turns += 1
            return
        if action.verb == "MOVE" and (
            action.target in home_doors(game, self.seat)
            or action.target == game.shacks[self.seat]
        ):
            episode.post_deposit_wait_turns += 1
            return
        target = semantic_target(action, unit)
        if target is None:
            episode.post_deposit_wait_turns += 1
            return
        assert episode.deposit_door is not None
        from_start = bfs_distances(self.walkable, [episode.start_cell])
        to_target = bfs_distances(self.walkable, [target])
        doors = tuple(
            (self.shack[0] + dx, self.shack[1] + dy)
            for dx, dy in NEIGHBORS
            if (self.shack[0] + dx, self.shack[1] + dy) in self.walkable
        )
        feasible = [
            door for door in doors if door in from_start and door in to_target
        ]
        if episode.deposit_door not in feasible or not feasible:
            episode.status = "deposited_unidentified_outbound"
            episode.note = "deposit door or next target is not connected in the static board"
            self.awaiting.pop(unit.id, None)
            return
        chosen_cells = (
            from_start[episode.deposit_door] + to_target[episode.deposit_door]
        )
        best_cells = min(from_start[door] + to_target[door] for door in feasible)
        chosen_eta = ceil_div(
            from_start[episode.deposit_door], episode.speed
        ) + ceil_div(to_target[episode.deposit_door], episode.speed)
        best_eta = min(
            ceil_div(from_start[door], episode.speed)
            + ceil_div(to_target[door], episode.speed)
            for door in feasible
        )
        actual_total_eta = episode.bank_move_turns + ceil_div(
            to_target[episode.deposit_door], episode.speed
        )
        actual_total_cells = (
            episode.actual_inbound_steps + to_target[episode.deposit_door]
        )
        episode.next_action_turn = game.turn
        episode.next_action = action.raw
        episode.next_target = target
        episode.chosen_static_roundtrip_cells = chosen_cells
        episode.best_static_roundtrip_cells = best_cells
        episode.hindsight_cell_regret = chosen_cells - best_cells
        episode.chosen_static_roundtrip_eta = chosen_eta
        episode.best_static_roundtrip_eta = best_eta
        episode.hindsight_eta_regret = chosen_eta - best_eta
        episode.total_hindsight_eta_regret = max(0, actual_total_eta - best_eta)
        episode.total_hindsight_cell_regret = max(0, actual_total_cells - best_cells)
        episode.status = "deposited_bound"
        self.awaiting.pop(unit.id, None)

    def observe_transition(
        self, before, after, commands: list[str]
    ) -> None:
        units = [unit for unit in before.units if unit.player == self.seat]
        actions = actions_by_unit(commands, units)
        by_id = {unit.id: unit for unit in units}

        for unit_id, episode in list(self.awaiting.items()):
            unit = by_id.get(unit_id)
            if unit is None:
                episode.status = "deposited_unidentified_outbound"
                episode.note = "unit disappeared before a post-deposit action"
                self.awaiting.pop(unit_id, None)
                continue
            action = actions.get(unit_id, Action("WAIT", unit_id, "WAIT"))
            self._bind_outbound(episode, before, unit, action)

        returning_ids: dict[int, str] = {}
        doors = set(home_doors(before, self.seat))
        for unit in units:
            action = actions.get(unit.id, Action("WAIT", unit.id, "WAIT"))
            is_door_move = (
                unit.total > 0
                and action.verb == "MOVE"
                and action.target in doors
            )
            is_drop = unit.total > 0 and action.verb == "DROP" and unit.pos in doors
            episode = self.active.get(unit.id)
            if episode is not None and unit.total != episode.cargo_total:
                episode.status = "unidentified_interrupted"
                episode.note = "cargo changed before a bound deposit"
                self.active.pop(unit.id, None)
                episode = None
            if episode is None and (is_door_move or is_drop):
                episode = self._new_episode(unit, before.turn)
            if episode is None:
                continue
            if is_door_move:
                self._record_move(episode, before, after, unit, action, actions)
                returning_ids[unit.id] = episode.episode_id
            elif is_drop:
                self._record_drop(episode, before, after, unit, action)
            else:
                episode.status = "unidentified_interrupted"
                episode.note = f"non-bank action before deposit: {action.raw}"
                self.ambiguous_carrying_door_moves += episode.bank_move_turns
                self.active.pop(unit.id, None)

        joint = joint_assignment_check(before, self.seat, actions, returning_ids)
        if joint is not None:
            joint.update({"seed": self.seed, "seat": self.seat})
            self.joint_checks.append(joint)

    def finalize(self) -> None:
        for episode in self.active.values():
            episode.status = "unidentified_unterminated_return"
            episode.note = "game ended before a bound deposit"
            self.ambiguous_carrying_door_moves += episode.bank_move_turns
        self.active.clear()
        for episode in self.awaiting.values():
            episode.status = "deposited_unbound"
            episode.note = "game ended before a post-deposit productive target"
        self.awaiting.clear()


def run_seed(seed: int, binary: Path) -> dict:
    game = generate_bronze(seed)
    sessions = [BotSession(binary, game, player) for player in (0, 1)]
    audits = [
        SideAudit(seed, player, game.walkable, game.shacks[player])
        for player in (0, 1)
    ]
    turns_until_end = 0
    ended_by_stall = False
    try:
        while game.turn <= 300:
            before = copy.deepcopy(game)
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            step(game, commands[0], commands[1])
            for player in (0, 1):
                audits[player].observe_transition(
                    before, game, commands[player]
                )
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("the exact live artifact unexpectedly wrote to stderr")
    for audit in audits:
        audit.finalize()
    return {
        "seed": seed,
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
        "sides": [
            {
                "seat": audit.seat,
                "episodes": [episode.as_json() for episode in audit.episodes],
                "joint_checks": audit.joint_checks,
                "ambiguous_carrying_door_moves": audit.ambiguous_carrying_door_moves,
            }
            for audit in audits
        ],
    }


def aggregate(rows: list[dict]) -> dict:
    episodes = [
        episode
        for row in rows
        for side in row["sides"]
        for episode in side["episodes"]
    ]
    confirmed = [
        episode
        for episode in episodes
        if episode["status"].startswith("deposited")
    ]
    bound = [
        episode for episode in confirmed if episode["status"] == "deposited_bound"
    ]
    confirmed_ids = {episode["episode_id"] for episode in confirmed}
    joint = [
        check
        for row in rows
        for side in row["sides"]
        for check in side["joint_checks"]
        if all(value in confirmed_ids for value in check["episode_ids"])
    ]
    statuses = Counter(episode["status"] for episode in episodes)
    immediate_checks = sum(episode["immediate_checks"] for episode in confirmed)
    immediate_positive = sum(
        episode["immediate_positive_checks"] for episode in confirmed
    )
    immediate_unidentified = sum(
        episode["immediate_unidentified_checks"] for episode in confirmed
    )
    joint_identified = [check for check in joint if check["identifiable"]]
    joint_positive = [
        check for check in joint_identified if check["eta_regret"] > 0
    ]
    switchers = [episode for episode in confirmed if episode["target_changes"] > 0]
    hindsight_positive = [
        episode
        for episode in bound
        if episode["hindsight_eta_regret"] is not None
        and episode["hindsight_eta_regret"] > 0
    ]
    total_positive = [
        episode
        for episode in bound
        if episode["total_hindsight_eta_regret"] is not None
        and episode["total_hindsight_eta_regret"] > 0
    ]
    side_games_with_confirmed = {
        (episode["seed"], episode["seat"]) for episode in confirmed
    }
    side_games_with_positive = {
        (episode["seed"], episode["seat"]) for episode in total_positive
    }
    positive_mechanism = (
        immediate_positive > 0
        or bool(joint_positive)
        or bool(switchers)
        or bool(total_positive)
    )
    verdict = (
        "UNIDENTIFIABLE"
        if not confirmed
        else "ROUTE_RESIDUAL_OBSERVED"
        if positive_mechanism
        else "NO_ROUTE_RESIDUAL"
    )
    return {
        "verdict": verdict,
        "games": len(rows),
        "side_games": 2 * len(rows),
        "ended_by_stall": sum(row["ended_by_stall"] for row in rows),
        "median_terminal_turn": statistics.median(
            row["terminal_turn"] for row in rows
        )
        if rows
        else None,
        "episodes": len(episodes),
        "confirmed_deposits": len(confirmed),
        "bound_next_targets": len(bound),
        "status_counts": dict(sorted(statuses.items())),
        "side_games_with_confirmed_deposit": len(side_games_with_confirmed),
        "cargo_units_confirmed": sum(
            episode["deposited_cargo"] or 0 for episode in confirmed
        ),
        "ambiguous_carrying_door_moves": sum(
            side["ambiguous_carrying_door_moves"]
            for row in rows
            for side in row["sides"]
        ),
        "immediate": {
            "checks": immediate_checks,
            "identified_checks": immediate_checks - immediate_unidentified,
            "unidentified_checks": immediate_unidentified,
            "positive_checks": immediate_positive,
            "eta_regret_sum": sum(
                episode["immediate_eta_regret_sum"] for episode in confirmed
            ),
            "eta_regret_max": max(
                (
                    episode["immediate_eta_regret_max"]
                    for episode in confirmed
                ),
                default=0,
            ),
        },
        "joint_assignment": {
            "confirmed_checks": len(joint),
            "identified_checks": len(joint_identified),
            "positive_checks": len(joint_positive),
            "eta_regret_sum": sum(
                check["eta_regret"] for check in joint_identified
            ),
            "eta_regret_max": max(
                (check["eta_regret"] for check in joint_identified), default=0
            ),
        },
        "persistence": {
            "episodes_with_target_change": len(switchers),
            "target_changes": sum(
                episode["target_changes"] for episode in confirmed
            ),
            "max_target_changes": max(
                (episode["target_changes"] for episode in confirmed), default=0
            ),
        },
        "hindsight_static": {
            "bound_episodes": len(bound),
            "positive_eta_episodes": len(hindsight_positive),
            "eta_regret_sum": sum(
                episode["hindsight_eta_regret"] or 0 for episode in bound
            ),
            "eta_regret_max": max(
                (episode["hindsight_eta_regret"] or 0 for episode in bound),
                default=0,
            ),
            "cell_regret_sum": sum(
                episode["hindsight_cell_regret"] or 0 for episode in bound
            ),
        },
        "total_hindsight_ceiling": {
            "positive_episodes": len(total_positive),
            "positive_side_games": len(side_games_with_positive),
            "avoidable_movement_turns": sum(
                episode["total_hindsight_eta_regret"] or 0 for episode in bound
            ),
            "max_episode_turns": max(
                (
                    episode["total_hindsight_eta_regret"] or 0
                    for episode in bound
                ),
                default=0,
            ),
            "avoidable_cells": sum(
                episode["total_hindsight_cell_regret"] or 0
                for episode in bound
            ),
            "note": (
                "Hindsight/static upper bound conditioned on the observed next target; "
                "not causal value and not rating."
            ),
        },
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    temporary.replace(path)


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_examples(rows: list[dict], limit: int = 16) -> dict:
    episodes = [
        episode
        for row in rows
        for side in row["sides"]
        for episode in side["episodes"]
    ]
    selected = []
    seen = set()
    for episode in episodes:
        interesting = (
            (episode["immediate_positive_checks"] or 0) > 0
            or (episode["target_changes"] or 0) > 0
            or (episode["total_hindsight_eta_regret"] or 0) > 0
            or episode["status"]
            not in {"deposited_bound", "deposited_unbound"}
        )
        if interesting and episode["episode_id"] not in seen:
            selected.append(episode)
            seen.add(episode["episode_id"])
        if len(selected) >= limit:
            break
    joint = [
        check
        for row in rows
        for side in row["sides"]
        for check in side["joint_checks"]
        if check["identifiable"] and (check["eta_regret"] or 0) > 0
    ][:limit]
    return {"episodes": selected, "positive_joint_assignments": joint}


def self_test() -> None:
    assert ceil_div(5, 2) == 3
    assert ceil_div(4, 2) == 2

    class Unit:
        def __init__(self, unit_id):
            self.id = unit_id

    actions = actions_by_unit(
        ["WAIT", "MOVE 4 2 3"], [Unit(3), Unit(4)]
    )
    assert actions[3].verb == "WAIT"
    assert actions[4].target == (2, 3)
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--source", type=Path, default=LIVE_SOURCE)
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            REPO
            / "data/analysis/live-agent-6553250/"
            "e2-banking-route-efficiency-result-2026-07-30.json"
        ),
    )
    parser.add_argument(
        "--details-output",
        type=Path,
        help=(
            "full episode bundle; defaults beneath the external-backed outputs root "
            "with the audited seed interval in its name"
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.seeds <= 0:
        raise SystemExit("--seeds must be positive")
    if args.seed_start < 0:
        raise SystemExit("--seed-start cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    digest = source_sha256(args.source)
    if args.source.resolve() == LIVE_SOURCE.resolve() and digest != LIVE_SHA256:
        raise SystemExit(
            f"live source hash mismatch: expected {LIVE_SHA256}, observed {digest}"
        )

    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    with tempfile.TemporaryDirectory(prefix="e2-bank-route-") as directory:
        binary = Path(directory) / "resident"
        compile_source(args.source, binary, "e2_bank_route_resident")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary): seed for seed in seeds
            }
            for future in as_completed(futures):
                rows.append(future.result())
        rows.sort(key=lambda row: row["seed"])

    details_output = args.details_output or (
        REPO
        / "outputs/local_codex_1/e2-banking-route-efficiency/"
        f"e2-episode-details-{seeds[0]}-{seeds[-1]}.json"
    )
    details = {
        "schema": 1,
        "scope": (
            "behavior-neutral exact-live local audit on reused deterministic seeds; "
            "no source change, protected range, candidate, or Arena inference"
        ),
        "source": str(args.source.resolve().relative_to(REPO)),
        "source_sha256": digest,
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(details_output, details)
    details_digest = source_sha256(details_output)
    try:
        details_path = str(details_output.absolute().relative_to(REPO))
    except ValueError:
        details_path = str(details_output)
    payload = {
        key: details[key]
        for key in (
            "schema",
            "scope",
            "source",
            "source_sha256",
            "seed_start",
            "seeds",
            "aggregate",
        )
    }
    payload["examples"] = compact_examples(rows)
    payload["details"] = {
        "path": details_path,
        "sha256": details_digest,
        "bytes": details_output.stat().st_size,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1, sort_keys=True))
    print(f"saved {args.output}")
    print(
        f"details {details_path} ({details_output.stat().st_size} bytes, "
        f"sha256 {details_digest})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
