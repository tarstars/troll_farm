#!/usr/bin/env python3
"""Audit the live secure-orchard mother's lexicographic tie-break.

The control is the exact live slim source.  The alternate exists only in a
temporary directory and reverses one secondary comparator.  The value panel is
restricted to the ten reused seeds where that comparator can matter; sixteen
unique-best seeds serve as dynamic identity sentinels.

This is a deterministic local causal audit, not an Arena predictor or candidate
builder.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import bfs_distances  # noqa: E402
from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from cgauto.offline_policy_league import OPPONENT_SOURCES  # noqa: E402
from sim.engine import has_stalled, stall_reason, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

LIVE_SOURCE = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
LIVE_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
SACRED_SOURCE = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"

CONTROL_SUFFIX = ".then_with(||a.cmp(b))"
ALTERNATE_SUFFIX = ".then_with(||b.cmp(a))"

TIED_SEEDS = (31, 91, 246, 364, 405, 568, 598, 652, 932, 966)
SENTINEL_SEEDS = (
    19,
    28,
    29,
    72,
    86,
    168,
    183,
    200,
    201,
    255,
    266,
    287,
    361,
    382,
    440,
    460,
)
OPPONENT_NAMES = (
    "motion",
    "taskplan",
    "race",
    "yield",
    "ringfix3",
    "chopharvest",
)

VALID_ARITIES = {
    "WAIT": 1,
    "TRAIN": 5,
    "MOVE": 4,
    "HARVEST": 2,
    "DROP": 2,
    "CHOP": 2,
    "MINE": 2,
    "PLANT": 3,
    "PICK": 3,
}
INTEGER_FIELDS = {
    "TRAIN": (1, 2, 3, 4),
    "MOVE": (1, 2, 3),
    "HARVEST": (1,),
    "DROP": (1,),
    "CHOP": (1,),
    "MINE": (1,),
    "PLANT": (1,),
    "PICK": (1,),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def rows_sha256(rows: list[dict]) -> str:
    return sha256_bytes(canonical_bytes(rows))


def transform_source(source: bytes) -> bytes:
    """Reverse exactly the frozen comparator suffix and no other bytes."""

    control = CONTROL_SUFFIX.encode()
    alternate = ALTERNATE_SUFFIX.encode()
    if source.count(control) != 1:
        raise ValueError("live source must contain the control suffix exactly once")
    if source.count(alternate) != 0:
        raise ValueError("live source unexpectedly contains the alternate suffix")
    transformed = source.replace(control, alternate, 1)
    if transformed.count(control) != 0 or transformed.count(alternate) != 1:
        raise ValueError("alternate comparator multiplicity is not exact")
    if transformed.replace(alternate, control, 1) != source:
        raise ValueError("alternate source is not a one-substring transformation")
    return transformed


def ortho_neighbors(cell: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = cell
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def geometry_for(game, seat: int) -> dict:
    """Reproduce the live initializer's static mother calculation."""

    doors = sorted(
        cell for cell in ortho_neighbors(game.shacks[seat]) if cell in game.walkable
    )
    natural = sorted(plant.pos for plant in game.plants if plant.health > 0)
    base = {
        "seat": seat,
        "doors": doors,
        "natural_count": len(natural),
        "eligible": False,
        "reason": None,
        "mothers": [],
        "best_distance": None,
        "best_tie": [],
        "best_tie_size": 0,
        "control_mother": None,
        "alternate_mother": None,
    }
    if len(doors) < 2:
        base["reason"] = "fewer_than_two_home_doors"
        return base
    if not natural:
        base["reason"] = "no_initial_natural"
        return base

    enemy_doors = [
        cell
        for cell in ortho_neighbors(game.shacks[1 - seat])
        if cell in game.walkable
    ]
    home_distance = bfs_distances(game.walkable, doors)
    enemy_distance = bfs_distances(game.walkable, enemy_doors)
    natural_return = [home_distance[cell] for cell in natural if cell in home_distance]
    if len(natural_return) != len(natural):
        base["reason"] = "unreachable_natural"
        return base
    base["median_natural_return"] = statistics.median(natural_return)
    if base["median_natural_return"] < 8:
        base["reason"] = "median_natural_return_below_eight"
        return base

    plant_cells = {plant.pos for plant in game.plants}
    mothers = [
        door
        for door in doors
        if door not in plant_cells
        and any(
            abs(door[0] - water[0]) + abs(door[1] - water[1]) == 1
            for water in game.water
        )
        and enemy_distance.get(door, 10_000) >= 11
    ]
    mothers.sort(key=lambda cell: (-enemy_distance.get(cell, 10_000), cell))
    base["mothers"] = [
        {"cell": cell, "enemy_door_distance": enemy_distance.get(cell, 10_000)}
        for cell in mothers
    ]
    if not mothers:
        base["reason"] = "no_mother"
        return base

    best_distance = enemy_distance.get(mothers[0], 10_000)
    best_tie = sorted(
        cell for cell in mothers if enemy_distance.get(cell, 10_000) == best_distance
    )
    base.update(
        {
            "eligible": True,
            "reason": "eligible",
            "best_distance": best_distance,
            "best_tie": best_tie,
            "best_tie_size": len(best_tie),
            "control_mother": best_tie[0],
            "alternate_mother": best_tie[-1],
        }
    )
    return base


def structural_census() -> dict:
    eligible_by_seat = {0: [], 1: []}
    tied_by_seat = {0: [], 1: []}
    geometry = {}
    tie_size_counts = Counter()
    for seed in range(1_000):
        game = generate_bronze(seed)
        for seat in (0, 1):
            result = geometry_for(game, seat)
            if result["eligible"]:
                eligible_by_seat[seat].append(seed)
                tie_size_counts[result["best_tie_size"]] += 1
            if result["best_tie_size"] > 1:
                tied_by_seat[seat].append(seed)
            if seed in TIED_SEEDS or seed in SENTINEL_SEEDS:
                geometry[f"{seed}:{seat}"] = result

    integrity = {
        "eligible_57_each_seat": all(
            len(eligible_by_seat[seat]) == 57 for seat in (0, 1)
        ),
        "eligible_seed_symmetry": eligible_by_seat[0] == eligible_by_seat[1],
        "tied_seed_registry_exact": all(
            tied_by_seat[seat] == list(TIED_SEEDS) for seat in (0, 1)
        ),
        "tie_size_distribution_exact": dict(sorted(tie_size_counts.items()))
        == {1: 94, 2: 20},
        "sentinels_unique_best": all(
            geometry[f"{seed}:{seat}"]["best_tie_size"] == 1
            for seed in SENTINEL_SEEDS
            for seat in (0, 1)
        ),
    }
    if not all(integrity.values()):
        raise RuntimeError(f"structural census integrity failed: {integrity}")
    return {
        "seed_range": [0, 999],
        "eligible_seed_count_by_seat": {
            str(seat): len(values) for seat, values in eligible_by_seat.items()
        },
        "eligible_seeds": eligible_by_seat[0],
        "tied_seeds_by_seat": {
            str(seat): values for seat, values in tied_by_seat.items()
        },
        "eligible_side_best_tie_size_counts": {
            str(size): count for size, count in sorted(tie_size_counts.items())
        },
        "audit_geometry": geometry,
        "integrity": integrity,
    }


def validate_commands(commands: list[str]) -> None:
    for command in commands:
        parts = command.split()
        verb = parts[0].upper() if parts else ""
        if verb not in VALID_ARITIES or len(parts) != VALID_ARITIES[verb]:
            raise ValueError(f"malformed command: {command!r}")
        for index in INTEGER_FIELDS.get(verb, ()):
            try:
                int(parts[index])
            except ValueError as error:
                raise ValueError(f"malformed integer in command: {command!r}") from error


def update_stream_hash(hasher, turn: int, line: str) -> None:
    encoded = line.encode("utf-8")
    hasher.update(f"{turn}:{len(encoded)}:".encode("ascii"))
    hasher.update(encoded)
    hasher.update(b"\n")


def terminal_state_payload(game) -> dict:
    return {
        "width": game.width,
        "height": game.height,
        "walkable": sorted(game.walkable),
        "iron": sorted(game.iron),
        "water": sorted(game.water),
        "shacks": game.shacks,
        "inventories": game.inventories,
        "scores": game.scores,
        "turn": game.turn,
        "next_id": game.next_id,
        "units": [
            {
                "id": unit.id,
                "player": unit.player,
                "x": unit.x,
                "y": unit.y,
                "ms": unit.ms,
                "cc": unit.cc,
                "hp": unit.hp,
                "chop": unit.chop,
                "carry": unit.carry,
            }
            for unit in sorted(game.units, key=lambda value: value.id)
        ],
        "plants": [
            {
                "type": plant.type,
                "x": plant.x,
                "y": plant.y,
                "size": plant.size,
                "health": plant.health,
                "fruits": plant.fruits,
                "cooldown": plant.cooldown,
            }
            for plant in sorted(
                game.plants,
                key=lambda value: (
                    value.x,
                    value.y,
                    value.type,
                    value.size,
                    value.health,
                    value.fruits,
                    value.cooldown,
                ),
            )
        ],
    }


def run_match_telemetry(game, binary0: Path, binary1: Path) -> dict:
    sessions = [BotSession(binary0, game, 0), BotSession(binary1, game, 1)]
    stream_hashes = [hashlib.sha256(), hashlib.sha256()]
    command_counts = [Counter(), Counter()]
    turns_until_end = 0
    ended_by_stall = False
    stderrs = ["", ""]
    try:
        while game.turn <= 300:
            turn = game.turn
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for seat in (0, 1):
                update_stream_hash(stream_hashes[seat], turn, lines[seat])
                validate_commands(commands[seat])
                command_counts[seat].update(
                    command.split()[0].upper() for command in commands[seat]
                )
            step(game, commands[0], commands[1])
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        for seat, session in enumerate(sessions):
            stderrs[seat] = session.close()

    if any(stderrs):
        lengths = [len(stderr) for stderr in stderrs]
        raise RuntimeError(f"unexpected bot stderr bytes: {lengths}")
    reason = (
        stall_reason(game, turns_until_end) or "stalled"
        if ended_by_stall
        else "turn_cap"
    )
    terminal = terminal_state_payload(game)
    return {
        "scores": list(game.scores),
        "inventories": copy.deepcopy(game.inventories),
        "action_stream_sha256": [hasher.hexdigest() for hasher in stream_hashes],
        "command_counts": [
            dict(sorted(counts.items())) for counts in command_counts
        ],
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
        "terminal_reason": reason,
        "terminal_state_sha256": sha256_bytes(canonical_bytes(terminal)),
        "malformed_commands": 0,
        "stderr_bytes": [0, 0],
    }


def outcome(margin: int) -> str:
    if margin > 0:
        return "win"
    if margin < 0:
        return "loss"
    return "tie"


def combine_counts(first: dict, second: dict) -> dict:
    combined = Counter(first)
    combined.update(second)
    return dict(sorted(combined.items()))


def paired_cell(
    seed: int,
    map_class: str,
    policy_name: str,
    opponent_name: str,
    policy_binary: Path,
    opponent_binary: Path,
) -> dict:
    initial = generate_bronze(seed)
    first = run_match_telemetry(
        copy.deepcopy(initial), policy_binary, opponent_binary
    )
    second = run_match_telemetry(
        copy.deepcopy(initial), opponent_binary, policy_binary
    )
    seat_margins = [
        first["scores"][0] - first["scores"][1],
        second["scores"][1] - second["scores"][0],
    ]
    seat_wood_edges = [
        first["inventories"][0][5] - first["inventories"][1][5],
        second["inventories"][1][5] - second["inventories"][0][5],
    ]
    return {
        "seed": seed,
        "map_class": map_class,
        "policy": policy_name,
        "opponent": opponent_name,
        "seat_margins": seat_margins,
        "paired_margin": statistics.mean(seat_margins),
        "seat_wood_edges": seat_wood_edges,
        "paired_wood_edge": statistics.mean(seat_wood_edges),
        "policy_scores": [first["scores"][0], second["scores"][1]],
        "opponent_scores": [first["scores"][1], second["scores"][0]],
        "policy_wood": [
            first["inventories"][0][5],
            second["inventories"][1][5],
        ],
        "opponent_wood": [
            first["inventories"][1][5],
            second["inventories"][0][5],
        ],
        "policy_action_stream_sha256": [
            first["action_stream_sha256"][0],
            second["action_stream_sha256"][1],
        ],
        "opponent_action_stream_sha256": [
            first["action_stream_sha256"][1],
            second["action_stream_sha256"][0],
        ],
        "terminal_state_sha256": [
            first["terminal_state_sha256"],
            second["terminal_state_sha256"],
        ],
        "outcomes": [outcome(value) for value in seat_margins],
        "terminal_turns": [first["terminal_turn"], second["terminal_turn"]],
        "ended_by_stall": [
            first["ended_by_stall"],
            second["ended_by_stall"],
        ],
        "terminal_reasons": [
            first["terminal_reason"],
            second["terminal_reason"],
        ],
        "policy_command_counts": combine_counts(
            first["command_counts"][0], second["command_counts"][1]
        ),
        "opponent_command_counts": combine_counts(
            first["command_counts"][1], second["command_counts"][0]
        ),
        "malformed_commands": 0,
        "stderr_bytes": 0,
    }


def mean(values) -> float:
    values = list(values)
    if not values:
        raise ValueError("mean requires at least one value")
    return statistics.mean(values)


def delta_records(tied_rows: list[dict]) -> list[dict]:
    lookup = {
        (row["seed"], row["opponent"], row["policy"]): row for row in tied_rows
    }
    records = []
    for seed in TIED_SEEDS:
        for opponent_name in OPPONENT_NAMES:
            control = lookup[(seed, opponent_name, "control")]
            alternate = lookup[(seed, opponent_name, "alternate")]
            records.append(
                {
                    "seed": seed,
                    "opponent": opponent_name,
                    "policy_action_diverged_by_seat": [
                        alternate["policy_action_stream_sha256"][seat]
                        != control["policy_action_stream_sha256"][seat]
                        for seat in (0, 1)
                    ],
                    "opponent_action_diverged_by_seat": [
                        alternate["opponent_action_stream_sha256"][seat]
                        != control["opponent_action_stream_sha256"][seat]
                        for seat in (0, 1)
                    ],
                    "terminal_state_diverged_by_seat": [
                        alternate["terminal_state_sha256"][seat]
                        != control["terminal_state_sha256"][seat]
                        for seat in (0, 1)
                    ],
                    "control_paired_margin": control["paired_margin"],
                    "alternate_paired_margin": alternate["paired_margin"],
                    "delta_paired_margin": (
                        alternate["paired_margin"] - control["paired_margin"]
                    ),
                    "delta_seat_margins": [
                        alternate["seat_margins"][seat]
                        - control["seat_margins"][seat]
                        for seat in (0, 1)
                    ],
                    "delta_paired_wood_edge": (
                        alternate["paired_wood_edge"]
                        - control["paired_wood_edge"]
                    ),
                    "delta_policy_score": (
                        mean(alternate["policy_scores"])
                        - mean(control["policy_scores"])
                    ),
                    "delta_opponent_score": (
                        mean(alternate["opponent_scores"])
                        - mean(control["opponent_scores"])
                    ),
                    "delta_policy_wood": (
                        mean(alternate["policy_wood"])
                        - mean(control["policy_wood"])
                    ),
                    "delta_opponent_wood": (
                        mean(alternate["opponent_wood"])
                        - mean(control["opponent_wood"])
                    ),
                }
            )
    return records


def metric_summary(records: list[dict], key: str) -> dict:
    values = [record[key] for record in records]
    seed_means = {
        seed: mean(record[key] for record in records if record["seed"] == seed)
        for seed in TIED_SEEDS
    }
    family_means = {
        opponent: mean(
            record[key] for record in records if record["opponent"] == opponent
        )
        for opponent in OPPONENT_NAMES
    }
    return {
        "tied_cell_mean": mean(values),
        "seed_balanced_tied_mean": mean(seed_means.values()),
        "exact_1000_map_weighted_mean": sum(values) / (1_000 * len(OPPONENT_NAMES)),
        "minimum_cell": min(values),
        "maximum_cell": max(values),
        "seed_means": {str(seed): value for seed, value in seed_means.items()},
        "family_means": family_means,
    }


def mechanism_summary(records: list[dict]) -> dict:
    divergent_seeds = sorted(
        {
            record["seed"]
            for record in records
            if any(record["policy_action_diverged_by_seat"])
        }
    )
    seat_divergent_cells = {
        str(seat): sum(
            record["policy_action_diverged_by_seat"][seat] for record in records
        )
        for seat in (0, 1)
    }
    family_divergent_seeds = {
        opponent: sorted(
            {
                record["seed"]
                for record in records
                if record["opponent"] == opponent
                and any(record["policy_action_diverged_by_seat"])
            }
        )
        for opponent in OPPONENT_NAMES
    }
    divergent_families = [
        opponent for opponent, seeds in family_divergent_seeds.items() if seeds
    ]
    gates = {
        "at_least_six_tied_seeds": len(divergent_seeds) >= 6,
        "both_seats": all(seat_divergent_cells[str(seat)] > 0 for seat in (0, 1)),
        "at_least_four_families": len(divergent_families) >= 4,
    }
    return {
        "status": "ACTIVE_TIE" if all(gates.values()) else "TIE_INERT",
        "gates": gates,
        "divergent_seed_count": len(divergent_seeds),
        "divergent_seeds": divergent_seeds,
        "seat_divergent_cell_counts": seat_divergent_cells,
        "divergent_family_count": len(divergent_families),
        "divergent_families": divergent_families,
        "family_divergent_seeds": family_divergent_seeds,
    }


def adjudicate(
    mechanism_status: str,
    weighted_margin: float,
    seat_means: list[float],
    family_means: dict[str, float],
) -> tuple[str, dict]:
    positive_families = sum(value > 0 for value in family_means.values())
    worst_family = min(family_means.values())
    gates = {
        "active_tie": mechanism_status == "ACTIVE_TIE",
        "weighted_margin_positive": weighted_margin > 0,
        "weighted_margin_at_least_one": weighted_margin >= 1,
        "both_seats_nonnegative": all(value >= 0 for value in seat_means),
        "at_least_four_positive_families": positive_families >= 4,
        "worst_family_at_least_minus_one": worst_family >= -1,
    }
    if not gates["active_tie"]:
        verdict = "TIE_INERT"
    elif (
        not gates["weighted_margin_positive"]
        or not gates["both_seats_nonnegative"]
        or not gates["worst_family_at_least_minus_one"]
    ):
        verdict = "KEEP_LEXICOGRAPHIC"
    elif (
        not gates["weighted_margin_at_least_one"]
        or not gates["at_least_four_positive_families"]
    ):
        verdict = "TIE_RESIDUAL_NONMATERIAL"
    else:
        verdict = "TIE_RESIDUAL_MATERIAL_LOCAL"
    gates["positive_family_count"] = positive_families
    gates["worst_family_mean"] = worst_family
    return verdict, gates


def aggregate(records: list[dict]) -> dict:
    mechanism = mechanism_summary(records)
    metrics = {
        key.removeprefix("delta_"): metric_summary(records, key)
        for key in (
            "delta_paired_margin",
            "delta_policy_score",
            "delta_opponent_score",
            "delta_paired_wood_edge",
            "delta_policy_wood",
            "delta_opponent_wood",
        )
    }
    seat_means = [
        mean(record["delta_seat_margins"][seat] for record in records)
        for seat in (0, 1)
    ]
    margin = metrics["paired_margin"]
    verdict, value_gates = adjudicate(
        mechanism["status"],
        margin["exact_1000_map_weighted_mean"],
        seat_means,
        margin["family_means"],
    )
    return {
        "mechanism": mechanism,
        "metrics": metrics,
        "margin_seat_means": seat_means,
        "verdict": verdict,
        "value_gates": value_gates,
    }


def sentinel_signature(row: dict) -> dict:
    return {
        key: value
        for key, value in row.items()
        if key not in {"policy"}
    }


def validate_sentinels(rows: list[dict]) -> dict:
    lookup = {(row["seed"], row["policy"]): row for row in rows}
    mismatches = []
    for seed in SENTINEL_SEEDS:
        control = sentinel_signature(lookup[(seed, "control")])
        alternate = sentinel_signature(lookup[(seed, "alternate")])
        if control != alternate:
            mismatches.append(seed)
    if mismatches:
        raise RuntimeError(f"sentinel identity failed for seeds {mismatches}")
    return {
        "sentinel_count": len(SENTINEL_SEEDS),
        "exact_count": len(SENTINEL_SEEDS) - len(mismatches),
        "mismatch_seeds": mismatches,
        "all_exact": not mismatches,
    }


def run_audit(jobs: int) -> dict:
    live_source = LIVE_SOURCE.read_bytes()
    source_hash = sha256_bytes(live_source)
    sacred_hash = sha256_path(SACRED_SOURCE)
    if source_hash != LIVE_SHA256:
        raise RuntimeError(f"live source hash mismatch: {source_hash}")
    if sacred_hash != SACRED_SHA256:
        raise RuntimeError(f"sacred source hash mismatch: {sacred_hash}")
    alternate_source = transform_source(live_source)
    census = structural_census()

    rows = []
    with tempfile.TemporaryDirectory(prefix="e4-orchard-mother-tie-") as directory:
        temp = Path(directory)
        alternate_path = temp / "alternate.rs"
        alternate_path.write_bytes(alternate_source)
        binaries = {}
        compile_source(LIVE_SOURCE, temp / "control", "e4_control")
        binaries["control"] = temp / "control"
        compile_source(alternate_path, temp / "alternate", "e4_alternate")
        binaries["alternate"] = temp / "alternate"
        for index, opponent_name in enumerate(OPPONENT_NAMES):
            compile_source(
                OPPONENT_SOURCES[opponent_name],
                temp / opponent_name,
                f"e4_opponent_{index}_{opponent_name}",
            )
            binaries[opponent_name] = temp / opponent_name
        print("compiled control, temporary alternate, and six opponents", flush=True)

        tasks = [
            (seed, "tied", policy, opponent)
            for seed in TIED_SEEDS
            for policy in ("control", "alternate")
            for opponent in OPPONENT_NAMES
        ] + [
            (seed, "sentinel", policy, "motion")
            for seed in SENTINEL_SEEDS
            for policy in ("control", "alternate")
        ]
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = {
                executor.submit(
                    paired_cell,
                    seed,
                    map_class,
                    policy,
                    opponent,
                    binaries[policy],
                    binaries[opponent],
                ): (seed, map_class, policy, opponent)
                for seed, map_class, policy, opponent in tasks
            }
            for completed, future in enumerate(as_completed(futures), 1):
                rows.append(future.result())
                if completed % 16 == 0 or completed == len(tasks):
                    print(f"completed {completed}/{len(tasks)} paired cells", flush=True)

    rows.sort(
        key=lambda row: (
            row["map_class"],
            row["seed"],
            row["policy"],
            row["opponent"],
        )
    )
    tied_rows = [row for row in rows if row["map_class"] == "tied"]
    sentinel_rows = [row for row in rows if row["map_class"] == "sentinel"]
    keys = [
        (row["map_class"], row["seed"], row["policy"], row["opponent"])
        for row in rows
    ]
    coverage = {
        "row_count": len(rows),
        "unique_key_count": len(set(keys)),
        "tied_row_count": len(tied_rows),
        "sentinel_row_count": len(sentinel_rows),
        "complete": (
            len(rows) == 152
            and len(set(keys)) == 152
            and len(tied_rows) == 120
            and len(sentinel_rows) == 32
        ),
    }
    if not coverage["complete"]:
        raise RuntimeError(f"panel coverage failed: {coverage}")
    if any(row["malformed_commands"] or row["stderr_bytes"] for row in rows):
        raise RuntimeError("command/stderr integrity failed")

    sentinel_integrity = validate_sentinels(sentinel_rows)
    deltas = delta_records(tied_rows)
    summary = aggregate(deltas)
    return {
        "schema": 1,
        "scope": (
            "exact-live comparator-only deterministic local audit on reused maps; "
            "not an Arena predictor or candidate"
        ),
        "jobs": jobs,
        "sources": {
            "control": {
                "path": str(LIVE_SOURCE.relative_to(REPO)),
                "sha256": source_hash,
            },
            "alternate": {
                "persistent": False,
                "replacement_count": 1,
                "control_suffix": CONTROL_SUFFIX,
                "alternate_suffix": ALTERNATE_SUFFIX,
                "sha256": sha256_bytes(alternate_source),
            },
            "sacred_resident": {
                "path": str(SACRED_SOURCE.relative_to(REPO)),
                "sha256": sacred_hash,
            },
            "opponents": {
                name: {
                    "path": str(OPPONENT_SOURCES[name].relative_to(REPO)),
                    "sha256": sha256_path(OPPONENT_SOURCES[name]),
                }
                for name in OPPONENT_NAMES
            },
        },
        "census": census,
        "coverage": coverage,
        "sentinel_integrity": sentinel_integrity,
        "aggregate": summary,
        "hashes": {
            "tied_rows_sha256": rows_sha256(tied_rows),
            "sentinel_rows_sha256": rows_sha256(sentinel_rows),
            "delta_records_sha256": rows_sha256(deltas),
        },
        "delta_records": deltas,
        "rows": rows,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def self_test() -> None:
    source = b"prefix" + CONTROL_SUFFIX.encode() + b"suffix"
    alternate = transform_source(source)
    assert alternate == b"prefix" + ALTERNATE_SUFFIX.encode() + b"suffix"
    assert rows_sha256([{"b": 2, "a": 1}]) == rows_sha256([{"a": 1, "b": 2}])

    families = {name: 1.0 for name in OPPONENT_NAMES}
    verdict, _ = adjudicate("TIE_INERT", 2.0, [1.0, 1.0], families)
    assert verdict == "TIE_INERT"
    verdict, _ = adjudicate("ACTIVE_TIE", 0.5, [1.0, 1.0], families)
    assert verdict == "TIE_RESIDUAL_NONMATERIAL"
    verdict, _ = adjudicate("ACTIVE_TIE", 1.0, [0.0, 1.0], families)
    assert verdict == "TIE_RESIDUAL_MATERIAL_LOCAL"
    verdict, _ = adjudicate("ACTIVE_TIE", 2.0, [-0.01, 1.0], families)
    assert verdict == "KEEP_LEXICOGRAPHIC"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "e4-orchard-mother-tie-audit-result-2026-07-30.json",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    if args.self_test:
        self_test()
        print("self-test: ok")
        return 0

    payload = run_audit(args.jobs)
    save(args.output, payload)
    summary = payload["aggregate"]
    print(
        f"verdict: {summary['verdict']}; "
        f"mechanism={summary['mechanism']['status']}; "
        "weighted margin="
        f"{summary['metrics']['paired_margin']['exact_1000_map_weighted_mean']:+.6f}",
        flush=True,
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
