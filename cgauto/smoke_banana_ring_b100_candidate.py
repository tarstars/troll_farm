#!/usr/bin/env python3
"""Paired consumed-seed value and behavior smoke for the banana-ring candidate."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile
from collections import deque


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import action_commands, BotSession, compile_source
from sim.engine import has_stalled, step
from sim.mapgen import generate_bronze


ARMS = {
    "fallback_b100_e6": REPO / "cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs",
    "live_unbounded_factory": REPO / "local_codex_1/banana-factory-b100-owner-override/banana-factory-b100-e6.arena.rs",
    "bounded_ring": REPO / "local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.arena.rs",
}
OPPONENTS = {
    "ringfix3": REPO / "cgauto/submissions/v1.59.0-ringfix3.min.rs",
    "taskplan": REPO / "cgauto/submissions/v1.27.0-taskplan.min.rs",
}


def ortho(cell: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    x, y = cell
    return ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y))


def distances(walkable: set[tuple[int, int]], sources) -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = {}
    queue = deque()
    for cell in sources:
        if cell not in out:
            out[cell] = 0
            queue.append(cell)
    while queue:
        cell = queue.popleft()
        for nxt in ortho(cell):
            if nxt in walkable and nxt not in out:
                out[nxt] = out[cell] + 1
                queue.append(nxt)
    return out


def ring_cells(game, seat: int) -> set[tuple[int, int]]:
    shack = game.shacks[seat]
    gates = sorted(cell for cell in ortho(shack) if cell in game.walkable)
    frontdoor = None
    if len(gates) >= 2:
        gate_maps = [(gate, distances(game.walkable, [gate])) for gate in gates]
        max_pair = max(
            mapping.get(right, 10**9)
            for index, (_, mapping) in enumerate(gate_maps)
            for right, _ in gate_maps[index + 1 :]
        )
        if max_pair > 8:
            enemy = distances(game.walkable, [game.shacks[1 - seat]])
            viable = [
                (gate, enemy.get(gate, 0))
                for gate, mapping in gate_maps
                if sum(mapping.get(cell, 10**9) <= 2 for cell in game.walkable) >= 4
            ]
            if viable:
                viable.sort(key=lambda pair: (-pair[1], pair[0]))
                frontdoor = viable[0][0]
    home = distances(game.walkable, gates)
    front = distances(game.walkable, [frontdoor]) if frontdoor is not None else None
    sx, sy = shack
    return {
        (sx + dx, sy + dy)
        for dy in range(-1, 2)
        for dx in range(-1, 2)
        if (dx or dy)
        and (sx + dx, sy + dy) in game.walkable
        and (sx + dx, sy + dy) in home
        and (front is None or front.get((sx + dx, sy + dy), 10**9) <= 2)
    }


def live_plant(game, cell):
    return next((plant for plant in game.plants if (plant.x, plant.y) == cell and plant.health > 0), None)


def run_match(binary: Path, opponent: Path, seed: int, seat: int, observe: bool) -> dict:
    game = generate_bronze(seed)
    binaries = [binary, opponent] if seat == 0 else [opponent, binary]
    sessions = [BotSession(binaries[index], game, index) for index in (0, 1)]
    metrics = {
        "plants_outside_ring": 0,
        "max_own_banana_chebyshev_from_tent": 0,
        "max_concurrent_own_ring_bananas": 0,
        "orthogonal_chop_actions": 0,
        "diagonal_ordinary_chops": 0,
        "banana_drops_after_full_ring": 0,
        "full_ring_bank_picks": 0,
        "wood_deposit_increase": 0,
    }
    owned_cells: set[tuple[int, int]] = set()
    turns_until_end = 0
    try:
        while game.turn <= 300:
            ring = ring_cells(game, seat)
            shack = game.shacks[seat]
            units = {unit.id: unit for unit in game.units if unit.player == seat}
            ring_full = bool(ring) and all(live_plant(game, cell) is not None for cell in ring)
            before_wood = game.inventories[seat][5]
            raw = [session.command(game) for session in sessions]
            candidate_commands = action_commands(raw[seat])
            if observe:
                for command in candidate_commands:
                    fields = command.split()
                    if len(fields) < 2 or not fields[1].lstrip("-").isdigit():
                        continue
                    unit = units.get(int(fields[1]))
                    if unit is None:
                        continue
                    cell = (unit.x, unit.y)
                    if fields[0] == "PLANT" and len(fields) == 3 and fields[2] == "BANANA":
                        distance = max(abs(cell[0] - shack[0]), abs(cell[1] - shack[1]))
                        metrics["max_own_banana_chebyshev_from_tent"] = max(
                            metrics["max_own_banana_chebyshev_from_tent"], distance
                        )
                        if cell not in ring:
                            metrics["plants_outside_ring"] += 1
                        else:
                            owned_cells.add(cell)
                    elif fields[0] == "PICK" and len(fields) == 3 and fields[2] == "BANANA":
                        if ring_full:
                            metrics["full_ring_bank_picks"] += 1
                    elif fields[0] == "DROP" and unit.carry[3] > 0 and ring_full:
                        metrics["banana_drops_after_full_ring"] += 1
                    elif fields[0] == "CHOP":
                        plant = live_plant(game, cell)
                        if plant is not None and plant.type == "BANANA" and cell in ring:
                            diagonal = abs(cell[0] - shack[0]) == abs(cell[1] - shack[1]) == 1
                            if diagonal:
                                home = distances(game.walkable, [shack])
                                raid = any(
                                    other.player != seat and home.get((other.x, other.y), 10**9) <= 4
                                    for other in game.units
                                )
                                if game.turn < 266 and not raid:
                                    metrics["diagonal_ordinary_chops"] += 1
                            else:
                                metrics["orthogonal_chop_actions"] += 1
            commands = [action_commands(line) for line in raw]
            step(game, commands[0], commands[1])
            if observe:
                metrics["wood_deposit_increase"] += max(
                    0, game.inventories[seat][5] - before_wood
                )
                owned_cells = {cell for cell in owned_cells if live_plant(game, cell) is not None}
                metrics["max_concurrent_own_ring_bananas"] = max(
                    metrics["max_concurrent_own_ring_bananas"], len(owned_cells)
                )
            ended, turns_until_end = has_stalled(game, turns_until_end)
            if ended:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError(f"runtime stderr: {stderrs}")
    margin = game.scores[seat] - game.scores[1 - seat]
    return {
        "seed": seed,
        "seat": seat,
        "score": game.scores[seat],
        "opponent_score": game.scores[1 - seat],
        "margin": margin,
        "metrics": metrics,
    }


def aggregate(rows: list[dict]) -> dict:
    margins = [row["margin"] for row in rows]
    return {
        "games": len(rows),
        "wins": sum(margin > 0 for margin in margins),
        "ties": sum(margin == 0 for margin in margins),
        "mean_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "catastrophes_le_minus_40": sum(margin <= -40 for margin in margins),
        "negative_margin_mass": -sum(min(0, margin) for margin in margins),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="banana-ring-smoke-") as raw:
        directory = Path(raw)
        binaries = {}
        for name, source in {**ARMS, **OPPONENTS}.items():
            binary = directory / name
            compile_source(source, binary, f"banana_ring_smoke_{name}")
            binaries[name] = binary
        arm_rows = {name: [] for name in ARMS}
        behavior = {key: 0 for key in (
            "plants_outside_ring", "max_own_banana_chebyshev_from_tent",
            "max_concurrent_own_ring_bananas", "orthogonal_chop_actions",
            "diagonal_ordinary_chops", "banana_drops_after_full_ring",
            "full_ring_bank_picks", "wood_deposit_increase",
        )}
        for seed in range(1300, 1308):
            for seat in (0, 1):
                opponent = "ringfix3" if seat == 0 else "taskplan"
                for arm in ARMS:
                    row = run_match(
                        binaries[arm], binaries[opponent], seed, seat, arm == "bounded_ring"
                    )
                    arm_rows[arm].append(row)
                    if arm == "bounded_ring":
                        for key, value in row["metrics"].items():
                            if key.startswith("max_"):
                                behavior[key] = max(behavior[key], value)
                            else:
                                behavior[key] += value
    aggregates = {name: aggregate(rows) for name, rows in arm_rows.items()}
    candidate = aggregates["bounded_ring"]
    live = aggregates["live_unbounded_factory"]
    invariant_pass = (
        behavior["plants_outside_ring"] == 0
        and behavior["max_own_banana_chebyshev_from_tent"] <= 1
        and behavior["diagonal_ordinary_chops"] == 0
        and behavior["full_ring_bank_picks"] == 0
        and behavior["orthogonal_chop_actions"] > 0
        and behavior["wood_deposit_increase"] > 0
    )
    no_severe_tail_regression = (
        candidate["catastrophes_le_minus_40"] <= live["catastrophes_le_minus_40"] + 2
        and candidate["negative_margin_mass"] <= live["negative_margin_mass"] + 200
    )
    payload = {
        "schema": 1,
        "scope": "consumed seeds 1300..1307, both seats; paired smoke, not a fitted estimate",
        "status": "SMOKE_QUALIFIED" if invariant_pass and no_severe_tail_regression else "CLOSED",
        "behavior": behavior,
        "behavior_invariants_pass": invariant_pass,
        "no_severe_tail_regression": no_severe_tail_regression,
        "arms": aggregates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"{payload['status']}: ring mean={candidate['mean_margin']:.2f}, "
        f"live mean={live['mean_margin']:.2f}, behavior={behavior}"
    )
    return 0 if payload["status"] == "SMOKE_QUALIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
