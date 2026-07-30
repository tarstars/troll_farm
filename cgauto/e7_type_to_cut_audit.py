#!/usr/bin/env python3
"""Audit the live resident's once-per-game LEMON/PLUM focus choice.

The control is the exact live slim source.  The temporary alternate changes
only the unique initialization of ``type_to_cut`` and selects the other member
of the binary LEMON/PLUM action space.  The exhaustive hindsight calculation
chooses once per seed after averaging all six frozen opponents.

All maps are reused and all bot processes run under E4's deterministic child
runtime.  This is a local causal audit, not a deployable selector, candidate,
or Arena experiment.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import bfs_distances  # noqa: E402
from cgauto.e4_orchard_mother_tie_audit import (  # noqa: E402
    compile_runtime_shim,
    LIVE_SHA256,
    LIVE_SOURCE,
    OPPONENT_NAMES,
    rows_sha256,
    SACRED_SHA256,
    SACRED_SOURCE,
    sha256_bytes,
    sha256_path,
)
from cgauto.e5_ripeness_wait_audit import (  # noqa: E402
    compact_match,
    policy_match,
)
from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import OPPONENT_SOURCES  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

SEEDS = tuple(range(60))

FLIP_FROM = "self.type_to_cut=Some(MoisanBot::focus_type(view));"
FLIP_TO = (
    "self.type_to_cut=Some(match MoisanBot::focus_type(view){"
    "PlantKind::Lemon=>PlantKind::Plum,_=>PlantKind::Lemon});"
)

INACTIVE_FIELDS = (
    "margin",
    "wood_edge",
    "policy_score",
    "opponent_score",
    "policy_wood",
    "opponent_wood",
    "outcome",
    "policy_action_stream_sha256",
    "opponent_action_stream_sha256",
    "policy_command_counts",
    "opponent_command_counts",
    "terminal_turn",
    "ended_by_stall",
    "terminal_reason",
    "terminal_state_sha256",
    "malformed_commands",
    "unexpected_stderr_bytes",
)


def transform_source(source: bytes) -> bytes:
    """Flip exactly the frozen focus initialization and no other bytes."""

    old = FLIP_FROM.encode()
    new = FLIP_TO.encode()
    if source.count(old) != 1:
        raise ValueError("focus initialization anchor must occur exactly once")
    if source.count(new) != 0:
        raise ValueError("flipped focus initialization already exists")
    transformed = source.replace(old, new, 1)
    if transformed.count(old) != 0 or transformed.count(new) != 1:
        raise ValueError("flipped focus multiplicity is not exact")
    if transformed.replace(new, old, 1) != source:
        raise ValueError("flip changes bytes outside its declared anchor")
    return transformed


def ortho_neighbors(cell: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = cell
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def focus_geometry(game, seat: int) -> dict:
    """Independently reproduce the exact static ``focus_type`` calculation."""

    doors = [
        cell
        for cell in ortho_neighbors(game.shacks[seat])
        if cell in game.walkable
    ]
    distances = bfs_distances(game.walkable, doors)
    totals = {}
    counts = {}
    for species in ("LEMON", "PLUM"):
        plants = [plant for plant in game.plants if plant.type == species]
        counts[species] = len(plants)
        totals[species] = sum(
            distances.get(plant.pos, 10_000) for plant in plants
        )
    # The live Rust iterator is [Lemon, Plum], so LEMON wins an exact tie.
    chosen = "LEMON" if totals["LEMON"] <= totals["PLUM"] else "PLUM"
    return {
        "seat": seat,
        "doors": doors,
        "plant_counts": counts,
        "distance_sums": totals,
        "chosen_species": chosen,
        "distance_tie": totals["LEMON"] == totals["PLUM"],
    }


def geometry_census() -> list[dict]:
    rows = []
    for seed in SEEDS:
        game = generate_bronze(seed)
        seats = [focus_geometry(game, seat) for seat in (0, 1)]
        if any(row["chosen_species"] not in {"LEMON", "PLUM"} for row in seats):
            raise RuntimeError(f"seed {seed} did not produce a binary choice")
        if seats[0]["chosen_species"] != seats[1]["chosen_species"]:
            raise RuntimeError(f"seed {seed} has asymmetric focus geometry")
        rows.append(
            {
                "seed": seed,
                "chosen_species": seats[0]["chosen_species"],
                "seats": seats,
            }
        )
    return rows


def command_target_cell(command: str | None) -> tuple[int, int] | None:
    """Return an explicit command target cell where the protocol exposes one."""

    if command is None:
        return None
    fields = command.split()
    if fields[0].upper() not in {"MOVE", "PICK"} or len(fields) != 4:
        return None
    try:
        return int(fields[2]), int(fields[3])
    except ValueError:
        return None


def changed_command_rows(
    control_turn: dict,
    flip_turn: dict,
    initial_species: dict[tuple[int, int], str],
) -> list[dict]:
    units = sorted(set(control_turn["by_unit"]) | set(flip_turn["by_unit"]))
    rows = []
    for unit in units:
        control_command = control_turn["by_unit"].get(unit)
        flip_command = flip_turn["by_unit"].get(unit)
        if control_command == flip_command:
            continue
        control_cell = command_target_cell(control_command)
        flip_cell = command_target_cell(flip_command)
        rows.append(
            {
                "unit": unit,
                "control_command": control_command,
                "flip_command": flip_command,
                "control_initial_target_species": initial_species.get(
                    control_cell
                ),
                "flip_initial_target_species": initial_species.get(flip_cell),
            }
        )
    return rows


def first_divergence(
    control: dict,
    flip: dict,
    initial_species: dict[tuple[int, int], str] | None = None,
) -> dict | None:
    """Locate the first policy action difference on an exact common state."""

    initial_species = initial_species or {}
    control_policy = control["policy_trace"]
    flip_policy = flip["policy_trace"]
    control_opponent = control["opponent_trace"]
    flip_opponent = flip["opponent_trace"]
    common = min(
        len(control_policy),
        len(flip_policy),
        len(control_opponent),
        len(flip_opponent),
    )
    for index in range(common):
        if control_policy[index]["turn"] != flip_policy[index]["turn"]:
            raise RuntimeError("policy trace turns do not align")
        if control_opponent[index]["turn"] != flip_opponent[index]["turn"]:
            raise RuntimeError("opponent trace turns do not align")
        policy_differs = (
            control_policy[index]["commands"]
            != flip_policy[index]["commands"]
        )
        opponent_differs = (
            control_opponent[index]["commands"]
            != flip_opponent[index]["commands"]
        )
        if opponent_differs and not policy_differs:
            raise RuntimeError("opponent diverged before the policy")
        if policy_differs:
            if opponent_differs:
                raise RuntimeError(
                    "opponent differs on the policy's first divergence state"
                )
            changed = changed_command_rows(
                control_policy[index],
                flip_policy[index],
                initial_species,
            )
            if not changed:
                raise RuntimeError("policy divergence has no changed unit command")
            return {
                "turn": control_policy[index]["turn"],
                "common_prefix_turns": index,
                "control_commands": control_policy[index]["commands"],
                "flip_commands": flip_policy[index]["commands"],
                "opponent_commands": control_opponent[index]["commands"],
                "changed_unit_commands": changed,
            }

    lengths = {
        len(control_policy),
        len(flip_policy),
        len(control_opponent),
        len(flip_opponent),
    }
    if len(lengths) != 1:
        raise RuntimeError("trace lengths differ without an action divergence")
    return None


def inactive_mismatches(control: dict, flip: dict) -> list[str]:
    return [
        field for field in INACTIVE_FIELDS if control[field] != flip[field]
    ]


def value_cell(
    seed: int,
    opponent_name: str,
    control_binary: Path,
    flip_binary: Path,
    opponent_binary: Path,
) -> dict:
    initial = generate_bronze(seed)
    species_by_cell = {
        plant.pos: plant.type
        for plant in initial.plants
        if plant.type in {"LEMON", "PLUM"}
    }
    geometry = [focus_geometry(initial, seat) for seat in (0, 1)]
    if geometry[0]["chosen_species"] != geometry[1]["chosen_species"]:
        raise RuntimeError(f"seed {seed} has asymmetric focus geometry")

    seats = []
    for seat in (0, 1):
        control = policy_match(
            seed, control_binary, opponent_binary, seat, diagnostic=False
        )
        flip = policy_match(
            seed, flip_binary, opponent_binary, seat, diagnostic=False
        )
        divergence = first_divergence(control, flip, species_by_cell)
        mismatches = (
            inactive_mismatches(control, flip)
            if divergence is None
            else []
        )
        if mismatches:
            raise RuntimeError(
                f"inactive seed {seed}/{opponent_name}/seat {seat} "
                f"is not exact: {mismatches}"
            )
        seats.append(
            {
                "seat": seat,
                "control": compact_match(control),
                "flip": compact_match(flip),
                "divergence": divergence,
                "inactive_exact": not mismatches,
            }
        )

    control_margins = [row["control"]["margin"] for row in seats]
    flip_margins = [row["flip"]["margin"] for row in seats]
    control_wood = [row["control"]["wood_edge"] for row in seats]
    flip_wood = [row["flip"]["wood_edge"] for row in seats]
    control_policy_score = [row["control"]["policy_score"] for row in seats]
    flip_policy_score = [row["flip"]["policy_score"] for row in seats]
    control_opponent_score = [
        row["control"]["opponent_score"] for row in seats
    ]
    flip_opponent_score = [row["flip"]["opponent_score"] for row in seats]
    return {
        "seed": seed,
        "opponent": opponent_name,
        "control_species": geometry[0]["chosen_species"],
        "flip_species": (
            "PLUM"
            if geometry[0]["chosen_species"] == "LEMON"
            else "LEMON"
        ),
        "activated": any(row["divergence"] is not None for row in seats),
        "seat_activated": [row["divergence"] is not None for row in seats],
        "control_paired_margin": statistics.mean(control_margins),
        "flip_paired_margin": statistics.mean(flip_margins),
        "delta_paired_margin": (
            statistics.mean(flip_margins)
            - statistics.mean(control_margins)
        ),
        "delta_seat_margins": [
            flip_margins[seat] - control_margins[seat] for seat in (0, 1)
        ],
        "delta_paired_wood_edge": (
            statistics.mean(flip_wood) - statistics.mean(control_wood)
        ),
        "delta_policy_score": (
            statistics.mean(flip_policy_score)
            - statistics.mean(control_policy_score)
        ),
        "delta_opponent_score": (
            statistics.mean(flip_opponent_score)
            - statistics.mean(control_opponent_score)
        ),
        "seats": seats,
    }


def metric_summary(rows: list[dict], key: str) -> dict:
    values = [row[key] for row in rows]
    activated = [row[key] for row in rows if row["activated"]]
    family_means = {
        opponent: statistics.mean(
            row[key] for row in rows if row["opponent"] == opponent
        )
        for opponent in OPPONENT_NAMES
    }
    seed_means = {
        str(seed): statistics.mean(
            row[key] for row in rows if row["seed"] == seed
        )
        for seed in SEEDS
    }
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
        "activated_n": len(activated),
        "activated_mean_descriptive": (
            statistics.mean(activated) if activated else None
        ),
        "family_means": family_means,
        "seed_means": seed_means,
    }


def mechanism_summary(rows: list[dict]) -> dict:
    activated = [row for row in rows if row["activated"]]
    seat_counts = [
        sum(row["seat_activated"][seat] for row in rows) for seat in (0, 1)
    ]
    family_counts = {
        opponent: sum(
            row["activated"] for row in rows if row["opponent"] == opponent
        )
        for opponent in OPPONENT_NAMES
    }
    active_families = [
        opponent for opponent, count in family_counts.items() if count
    ]
    gates = {
        "at_least_30_cells": len(activated) >= 30,
        "at_least_10_each_seat": all(count >= 10 for count in seat_counts),
        "at_least_four_families": len(active_families) >= 4,
    }
    return {
        "status": "ACTIVE_FOCUS" if all(gates.values()) else "FOCUS_INERT",
        "gates": gates,
        "activated_cell_count": len(activated),
        "activated_seed_count": len({row["seed"] for row in activated}),
        "seat_game_counts": seat_counts,
        "active_family_count": len(active_families),
        "family_cell_counts": family_counts,
    }


def hindsight_summary(rows: list[dict]) -> tuple[dict, list[dict]]:
    lookup = {(row["seed"], row["opponent"]): row for row in rows}
    oracle_rows = []
    for seed in SEEDS:
        seed_rows = [lookup[(seed, opponent)] for opponent in OPPONENT_NAMES]
        delta = statistics.mean(
            row["delta_paired_margin"] for row in seed_rows
        )
        seat_deltas = [
            statistics.mean(
                row["delta_seat_margins"][seat] for row in seed_rows
            )
            for seat in (0, 1)
        ]
        choose_flip = delta > 0
        oracle_rows.append(
            {
                "seed": seed,
                "control_species": seed_rows[0]["control_species"],
                "selected_policy": "FLIP" if choose_flip else "CONTROL",
                "flip_delta_mean": delta,
                "selected_gain": delta if choose_flip else 0,
                "selected_seat_gains": (
                    seat_deltas if choose_flip else [0, 0]
                ),
                "family_deltas": {
                    opponent: lookup[(seed, opponent)][
                        "delta_paired_margin"
                    ]
                    for opponent in OPPONENT_NAMES
                },
            }
        )

    leave_one_family_out = {}
    for held_out in OPPONENT_NAMES:
        held_values = []
        selected_flip_count = 0
        training_families = [
            opponent for opponent in OPPONENT_NAMES if opponent != held_out
        ]
        for seed in SEEDS:
            training_delta = statistics.mean(
                lookup[(seed, opponent)]["delta_paired_margin"]
                for opponent in training_families
            )
            choose_flip = training_delta > 0
            selected_flip_count += choose_flip
            held_values.append(
                lookup[(seed, held_out)]["delta_paired_margin"]
                if choose_flip
                else 0
            )
        leave_one_family_out[held_out] = {
            "mean_selected_gain": statistics.mean(held_values),
            "selected_flip_seed_count": selected_flip_count,
        }

    selected_seat_means = [
        statistics.mean(row["selected_seat_gains"][seat] for row in oracle_rows)
        for seat in (0, 1)
    ]
    preferred = sum(
        row["selected_policy"] == "FLIP" for row in oracle_rows
    )
    gain = statistics.mean(row["selected_gain"] for row in oracle_rows)
    positive_leave_out = sum(
        row["mean_selected_gain"] > 0
        for row in leave_one_family_out.values()
    )
    gates = {
        "seed_balanced_gain_at_least_one": gain >= 1,
        "at_least_12_seeds_prefer_flip": preferred >= 12,
        "both_selected_policy_seats_nonnegative": all(
            value >= 0 for value in selected_seat_means
        ),
        "at_least_four_positive_leave_one_family_out": (
            positive_leave_out >= 4
        ),
        "preferred_flip_seed_count": preferred,
        "positive_leave_one_family_out_count": positive_leave_out,
    }
    summary = {
        "material": all(
            value
            for key, value in gates.items()
            if key
            not in {
                "preferred_flip_seed_count",
                "positive_leave_one_family_out_count",
            }
        ),
        "gates": gates,
        "seed_balanced_gain": gain,
        "preferred_flip_seed_count": preferred,
        "selected_policy_seat_means": selected_seat_means,
        "leave_one_family_out": leave_one_family_out,
    }
    return summary, oracle_rows


def adjudicate(
    mechanism_status: str,
    mean_margin: float,
    seat_means: list[float],
    family_means: dict[str, float],
    hindsight_material: bool,
) -> tuple[str, dict]:
    positive_families = sum(value > 0 for value in family_means.values())
    worst_family = min(family_means.values())
    direct_gates = {
        "active_focus": mechanism_status == "ACTIVE_FOCUS",
        "mean_margin_at_least_one": mean_margin >= 1,
        "both_seats_nonnegative": all(value >= 0 for value in seat_means),
        "at_least_four_positive_families": positive_families >= 4,
        "worst_family_at_least_minus_one": worst_family >= -1,
        "positive_family_count": positive_families,
        "worst_family_mean": worst_family,
    }
    direct_material = all(
        value
        for key, value in direct_gates.items()
        if key not in {"positive_family_count", "worst_family_mean"}
    )
    if mechanism_status != "ACTIVE_FOCUS":
        verdict = "FOCUS_INERT"
    elif direct_material:
        verdict = "FLIP_MATERIAL_LOCAL"
    elif hindsight_material:
        verdict = "HINDSIGHT_RESIDUAL_ONLY"
    else:
        verdict = "KEEP_TYPE_TO_CUT"
    return verdict, {
        "direct_material": direct_material,
        "direct_gates": direct_gates,
    }


def aggregate(rows: list[dict]) -> tuple[dict, list[dict]]:
    mechanism = mechanism_summary(rows)
    metrics = {
        key.removeprefix("delta_"): metric_summary(rows, key)
        for key in (
            "delta_paired_margin",
            "delta_policy_score",
            "delta_opponent_score",
            "delta_paired_wood_edge",
        )
    }
    seat_means = [
        statistics.mean(row["delta_seat_margins"][seat] for row in rows)
        for seat in (0, 1)
    ]
    hindsight, oracle_rows = hindsight_summary(rows)
    verdict, value_gates = adjudicate(
        mechanism["status"],
        metrics["paired_margin"]["mean"],
        seat_means,
        metrics["paired_margin"]["family_means"],
        hindsight["material"],
    )
    return (
        {
            "mechanism": mechanism,
            "metrics": metrics,
            "margin_seat_means": seat_means,
            "hindsight": hindsight,
            "verdict": verdict,
            "value_gates": value_gates,
        },
        oracle_rows,
    )


def validate_numeric_finiteness(value) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise RuntimeError(f"nonfinite value encountered: {value}")
    if isinstance(value, dict):
        for child in value.values():
            validate_numeric_finiteness(child)
    elif isinstance(value, list):
        for child in value:
            validate_numeric_finiteness(child)


def run_audit(jobs: int) -> dict:
    source = LIVE_SOURCE.read_bytes()
    source_hash = sha256_bytes(source)
    sacred_hash = sha256_path(SACRED_SOURCE)
    if source_hash != LIVE_SHA256:
        raise RuntimeError(f"live source hash mismatch: {source_hash}")
    if sacred_hash != SACRED_SHA256:
        raise RuntimeError(f"sacred source hash mismatch: {sacred_hash}")
    flipped = transform_source(source)
    geometry_rows = geometry_census()

    value_rows = []
    with tempfile.TemporaryDirectory(prefix="e7-type-to-cut-") as directory:
        temp = Path(directory)
        flip_path = temp / "flip.rs"
        flip_path.write_bytes(flipped)
        binaries = {}
        compile_source(LIVE_SOURCE, temp / "control", "e7_control")
        compile_source(flip_path, temp / "flip", "e7_flip")
        binaries["control"] = temp / "control"
        binaries["flip"] = temp / "flip"
        for index, opponent_name in enumerate(OPPONENT_NAMES):
            compile_source(
                OPPONENT_SOURCES[opponent_name],
                temp / opponent_name,
                f"e7_opponent_{index}_{opponent_name}",
            )
            binaries[opponent_name] = temp / opponent_name
        runtime_shim = compile_runtime_shim(temp)
        print(
            "compiled control, flip, six opponents, and deterministic runtime",
            flush=True,
        )

        previous_preload = os.environ.get("LD_PRELOAD")
        os.environ["LD_PRELOAD"] = (
            str(runtime_shim)
            if not previous_preload
            else f"{runtime_shim}:{previous_preload}"
        )
        try:
            tasks = [
                (seed, opponent)
                for seed in SEEDS
                for opponent in OPPONENT_NAMES
            ]
            with ThreadPoolExecutor(max_workers=jobs) as executor:
                futures = {
                    executor.submit(
                        value_cell,
                        seed,
                        opponent,
                        binaries["control"],
                        binaries["flip"],
                        binaries[opponent],
                    ): (seed, opponent)
                    for seed, opponent in tasks
                }
                for completed, future in enumerate(as_completed(futures), 1):
                    value_rows.append(future.result())
                    if completed % 30 == 0 or completed == len(tasks):
                        print(
                            f"completed {completed}/{len(tasks)} value cells",
                            flush=True,
                        )
        finally:
            if previous_preload is None:
                os.environ.pop("LD_PRELOAD", None)
            else:
                os.environ["LD_PRELOAD"] = previous_preload

    value_rows.sort(key=lambda row: (row["seed"], row["opponent"]))
    keys = [(row["seed"], row["opponent"]) for row in value_rows]
    coverage = {
        "value_cells": len(value_rows),
        "unique_value_keys": len(set(keys)),
        "seat_games_per_policy": 2 * len(value_rows),
        "total_games": 4 * len(value_rows),
        "complete": len(value_rows) == 360 and len(set(keys)) == 360,
    }
    if not coverage["complete"]:
        raise RuntimeError(f"coverage failed: {coverage}")
    if any(
        seat[policy]["malformed_commands"]
        or seat[policy]["unexpected_stderr_bytes"]
        for row in value_rows
        for seat in row["seats"]
        for policy in ("control", "flip")
    ):
        raise RuntimeError("command or stderr integrity failed")

    summary, oracle_rows = aggregate(value_rows)
    payload = {
        "schema": 1,
        "scope": (
            "exact-live binary focus-species causal audit and seed-level "
            "hindsight ceiling on reused maps; not a selector, candidate, "
            "or Arena predictor"
        ),
        "jobs": jobs,
        "sources": {
            "control": {
                "path": str(LIVE_SOURCE.relative_to(REPO)),
                "sha256": source_hash,
            },
            "flip": {
                "persistent": False,
                "replacement_count": 1,
                "from": FLIP_FROM,
                "to": FLIP_TO,
                "sha256": sha256_bytes(flipped),
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
        "panel": {
            "seeds": list(SEEDS),
            "opponents": list(OPPONENT_NAMES),
            "policies": ["control", "flip"],
            "seats": [0, 1],
        },
        "coverage": coverage,
        "geometry": {
            "choice_counts": dict(
                sorted(
                    Counter(
                        row["chosen_species"] for row in geometry_rows
                    ).items()
                )
            ),
            "symmetric_seed_count": sum(
                row["seats"][0]["chosen_species"]
                == row["seats"][1]["chosen_species"]
                for row in geometry_rows
            ),
            "rows": geometry_rows,
        },
        "aggregate": summary,
        "hashes": {
            "value_rows_sha256": rows_sha256(value_rows),
            "geometry_rows_sha256": rows_sha256(geometry_rows),
            "divergence_rows_sha256": rows_sha256(
                [
                    {
                        "seed": row["seed"],
                        "opponent": row["opponent"],
                        "seat_activated": row["seat_activated"],
                        "divergences": [
                            seat["divergence"] for seat in row["seats"]
                        ],
                    }
                    for row in value_rows
                ]
            ),
            "oracle_rows_sha256": rows_sha256(oracle_rows),
        },
        "value_rows": value_rows,
        "oracle_rows": oracle_rows,
    }
    validate_numeric_finiteness(payload)
    return payload


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def self_test() -> None:
    source = b"x" + FLIP_FROM.encode() + b"y"
    transformed = transform_source(source)
    assert transformed.count(FLIP_TO.encode()) == 1
    assert transformed.replace(
        FLIP_TO.encode(), FLIP_FROM.encode(), 1
    ) == source
    assert command_target_cell("MOVE 3 4 5") == (4, 5)
    assert command_target_cell("WAIT") is None
    positive = {name: 1.0 for name in OPPONENT_NAMES}
    assert (
        adjudicate("FOCUS_INERT", 2, [1, 1], positive, True)[0]
        == "FOCUS_INERT"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 0, [0, 0], positive, False)[0]
        == "KEEP_TYPE_TO_CUT"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 0, [0, 0], positive, True)[0]
        == "HINDSIGHT_RESIDUAL_ONLY"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 1, [0, 0], positive, False)[0]
        == "FLIP_MATERIAL_LOCAL"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "e7-type-to-cut-audit-result-2026-07-31.json",
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
        f"direct mean={summary['metrics']['paired_margin']['mean']:+.6f}; "
        f"hindsight={summary['hindsight']['seed_balanced_gain']:+.6f}",
        flush=True,
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
