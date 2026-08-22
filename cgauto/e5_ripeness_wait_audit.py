#!/usr/bin/env python3
"""Causally audit the live resident's on-site unripe-fruit wait.

The diagnostic control differs from the exact live source only by stderr
telemetry.  The temporary alternate removes one on-site, zero-fruit candidate
and lets the unchanged resident selector choose its next-best task.

All maps are reused and all bot processes run under the deterministic child
runtime established by E4.  This is not an Arena predictor or candidate.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.e4_orchard_mother_tie_audit import (  # noqa: E402
    canonical_bytes,
    compile_runtime_shim,
    LIVE_SHA256,
    LIVE_SOURCE,
    OPPONENT_NAMES,
    rows_sha256,
    SACRED_SHA256,
    SACRED_SOURCE,
    sha256_bytes,
    sha256_path,
    terminal_state_payload,
    update_stream_hash,
    validate_commands,
)
from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from cgauto.offline_policy_league import OPPONENT_SOURCES  # noqa: E402
from sim.engine import has_stalled, stall_reason, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

SEEDS = tuple(range(60))
SENTINEL_SEEDS = tuple(range(8))

ALTERNATE_FROM = (
    "plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell)"
)
ALTERNATE_TO = (
    "plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell)"
    "||plant.cell==unit.cell&&plant.fruits==0"
)

PROBE_FROM = (
    'for(_,index,current,_,landing)in&projections{if landing==current{'
    'commands[*index]="WAIT".to_string();}}'
)
PROBE_TO = (
    "for(id,index,current,target,landing)in&projections{if landing==current{"
    "if let Some(plant_index)=view.plant_at(*current){"
    "let plant=&view.plants[plant_index];"
    "if plant.health>0&&plant.fruits==0{"
    'eprintln!("@E5_WAIT t={} unit={} cell={},{} item={} size={} cooldown={} '
    'target={},{}",view.turn,id,current.0,current.1,plant.kind.item_index(),'
    "plant.size,plant.cooldown,target.0,target.1);}}"
    'commands[*index]="WAIT".to_string();}}'
)

EVENT_RE = re.compile(
    r"^@E5_WAIT t=(\d+) unit=(\d+) cell=(-?\d+),(-?\d+) "
    r"item=(\d+) size=(\d+) cooldown=(-?\d+) target=(-?\d+),(-?\d+)$"
)


def transform_exact(source: bytes, old: str, new: str, label: str) -> bytes:
    old_bytes = old.encode()
    new_bytes = new.encode()
    if source.count(old_bytes) != 1:
        raise ValueError(f"{label} source anchor must occur exactly once")
    if source.count(new_bytes) != 0:
        raise ValueError(f"{label} transformed anchor already exists")
    transformed = source.replace(old_bytes, new_bytes, 1)
    if transformed.count(new_bytes) != 1:
        raise ValueError(f"{label} replacement multiplicity is not exact")
    if transformed.replace(new_bytes, old_bytes, 1) != source:
        raise ValueError(f"{label} changes bytes outside its declared anchor")
    return transformed


def alternate_source(source: bytes) -> bytes:
    return transform_exact(source, ALTERNATE_FROM, ALTERNATE_TO, "alternate")


def probe_source(source: bytes) -> bytes:
    return transform_exact(source, PROBE_FROM, PROBE_TO, "probe")


def parse_probe_events(stderr: str) -> list[dict]:
    events = []
    unparsed = []
    for line in stderr.splitlines():
        match = EVENT_RE.fullmatch(line.strip())
        if not match:
            if line.strip():
                unparsed.append(line)
            continue
        values = [int(value) for value in match.groups()]
        events.append(
            {
                "turn": values[0],
                "unit": values[1],
                "cell": [values[2], values[3]],
                "item": values[4],
                "size": values[5],
                "cooldown": values[6],
                "target": [values[7], values[8]],
            }
        )
    if unparsed:
        raise RuntimeError(f"unexpected diagnostic stderr: {unparsed[:3]}")
    return events


def commands_by_unit(commands: list[str], unit_ids: list[int]) -> dict[int, str]:
    mapped = {}
    slot = 0
    for command in commands:
        verb = command.split()[0].upper()
        if verb == "TRAIN":
            continue
        if slot >= len(unit_ids):
            raise ValueError(
                f"more unit commands than live units: {commands!r} / {unit_ids!r}"
            )
        mapped[unit_ids[slot]] = command
        slot += 1
    return mapped


def combine_counts(first: dict, second: dict) -> dict:
    combined = Counter(first)
    combined.update(second)
    return dict(sorted(combined.items()))


def outcome(margin: int) -> str:
    if margin > 0:
        return "win"
    if margin < 0:
        return "loss"
    return "tie"


def run_match_trace(
    game,
    binary0: Path,
    binary1: Path,
    diagnostic_seat: int | None = None,
) -> dict:
    sessions = [BotSession(binary0, game, 0), BotSession(binary1, game, 1)]
    stream_hashes = [hashlib.sha256(), hashlib.sha256()]
    traces = [[], []]
    command_counts = [Counter(), Counter()]
    turns_until_end = 0
    ended_by_stall = False
    stderrs = ["", ""]
    try:
        while game.turn <= 300:
            turn = game.turn
            unit_ids = [
                sorted(unit.id for unit in game.units if unit.player == seat)
                for seat in (0, 1)
            ]
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for seat in (0, 1):
                update_stream_hash(stream_hashes[seat], turn, lines[seat])
                validate_commands(commands[seat])
                by_unit = commands_by_unit(commands[seat], unit_ids[seat])
                traces[seat].append(
                    {
                        "turn": turn,
                        "commands": commands[seat],
                        "by_unit": by_unit,
                    }
                )
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

    events = [[], []]
    for seat, stderr in enumerate(stderrs):
        if seat == diagnostic_seat:
            events[seat] = parse_probe_events(stderr)
        elif stderr:
            raise RuntimeError(
                f"unexpected stderr from seat {seat}: {stderr[:300]!r}"
            )
    reason = (
        (stall_reason(game, turns_until_end) or "stalled")
        if ended_by_stall
        else "turn_cap"
    )
    return {
        "scores": list(game.scores),
        "inventories": copy.deepcopy(game.inventories),
        "action_stream_sha256": [hasher.hexdigest() for hasher in stream_hashes],
        "traces": traces,
        "command_counts": [
            dict(sorted(counts.items())) for counts in command_counts
        ],
        "events": events,
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
        "terminal_reason": reason,
        "terminal_state_sha256": sha256_bytes(
            canonical_bytes(terminal_state_payload(game))
        ),
        "malformed_commands": 0,
        "unexpected_stderr_bytes": 0,
    }


def policy_match(
    seed: int,
    policy_binary: Path,
    opponent_binary: Path,
    policy_seat: int,
    diagnostic: bool,
) -> dict:
    initial = generate_bronze(seed)
    if policy_seat == 0:
        match = run_match_trace(
            copy.deepcopy(initial),
            policy_binary,
            opponent_binary,
            diagnostic_seat=0 if diagnostic else None,
        )
        policy_index, opponent_index = 0, 1
    else:
        match = run_match_trace(
            copy.deepcopy(initial),
            opponent_binary,
            policy_binary,
            diagnostic_seat=1 if diagnostic else None,
        )
        policy_index, opponent_index = 1, 0

    margin = match["scores"][policy_index] - match["scores"][opponent_index]
    wood_edge = (
        match["inventories"][policy_index][5]
        - match["inventories"][opponent_index][5]
    )
    return {
        "margin": margin,
        "wood_edge": wood_edge,
        "policy_score": match["scores"][policy_index],
        "opponent_score": match["scores"][opponent_index],
        "policy_wood": match["inventories"][policy_index][5],
        "opponent_wood": match["inventories"][opponent_index][5],
        "outcome": outcome(margin),
        "policy_action_stream_sha256": match["action_stream_sha256"][
            policy_index
        ],
        "opponent_action_stream_sha256": match["action_stream_sha256"][
            opponent_index
        ],
        "policy_trace": match["traces"][policy_index],
        "opponent_trace": match["traces"][opponent_index],
        "events": match["events"][policy_index],
        "policy_command_counts": match["command_counts"][policy_index],
        "opponent_command_counts": match["command_counts"][opponent_index],
        "terminal_turn": match["terminal_turn"],
        "ended_by_stall": match["ended_by_stall"],
        "terminal_reason": match["terminal_reason"],
        "terminal_state_sha256": match["terminal_state_sha256"],
        "malformed_commands": match["malformed_commands"],
        "unexpected_stderr_bytes": match["unexpected_stderr_bytes"],
    }


def first_divergence(control: dict, alternate: dict) -> dict | None:
    control_policy = control["policy_trace"]
    alternate_policy = alternate["policy_trace"]
    control_opponent = control["opponent_trace"]
    alternate_opponent = alternate["opponent_trace"]
    common = min(len(control_policy), len(alternate_policy))
    divergent_index = None
    for index in range(common):
        if (
            control_policy[index]["commands"]
            != alternate_policy[index]["commands"]
        ):
            divergent_index = index
            break
        if (
            control_opponent[index]["commands"]
            != alternate_opponent[index]["commands"]
        ):
            raise RuntimeError("opponent diverged before the policy")
    if divergent_index is None:
        if len(control_policy) != len(alternate_policy):
            raise RuntimeError("trace lengths differ without an action divergence")
        return None

    index = divergent_index
    control_turn = control_policy[index]
    alternate_turn = alternate_policy[index]
    if control_turn["turn"] != alternate_turn["turn"]:
        raise RuntimeError("first divergence turn indices do not align")
    if (
        control_opponent[index]["commands"]
        != alternate_opponent[index]["commands"]
    ):
        raise RuntimeError("opponent action differs on the common divergence state")

    turn = control_turn["turn"]
    events = [event for event in control["events"] if event["turn"] == turn]
    explanations = []
    for event in events:
        unit = event["unit"]
        control_command = control_turn["by_unit"].get(unit)
        alternate_command = alternate_turn["by_unit"].get(unit)
        if control_command == "WAIT" and alternate_command not in (None, "WAIT"):
            explanations.append(
                {
                    "event": event,
                    "control_command": control_command,
                    "alternate_command": alternate_command,
                }
            )
    if not explanations:
        raise RuntimeError(
            f"first policy divergence at turn {turn} lacks an E5 wait explanation"
        )
    return {
        "turn": turn,
        "control_commands": control_turn["commands"],
        "alternate_commands": alternate_turn["commands"],
        "opponent_commands": control_opponent[index]["commands"],
        "explanations": explanations,
        "common_prefix_turns": index,
    }


def compact_match(result: dict) -> dict:
    return {
        key: value
        for key, value in result.items()
        if key not in {"policy_trace", "opponent_trace", "events"}
    }


def value_cell(
    seed: int,
    opponent_name: str,
    probe_binary: Path,
    alternate_binary: Path,
    opponent_binary: Path,
) -> dict:
    seats = []
    all_events = []
    for seat in (0, 1):
        control = policy_match(
            seed, probe_binary, opponent_binary, seat, diagnostic=True
        )
        alternate = policy_match(
            seed, alternate_binary, opponent_binary, seat, diagnostic=False
        )
        divergence = first_divergence(control, alternate)
        if divergence is None:
            fields = (
                "policy_action_stream_sha256",
                "opponent_action_stream_sha256",
                "terminal_state_sha256",
                "margin",
                "wood_edge",
                "policy_score",
                "opponent_score",
                "terminal_turn",
                "ended_by_stall",
                "terminal_reason",
            )
            if any(control[field] != alternate[field] for field in fields):
                raise RuntimeError("inactive policy cell is not terminally exact")
        all_events.extend(
            {"seat": seat, **event} for event in control["events"]
        )
        seats.append(
            {
                "seat": seat,
                "control": compact_match(control),
                "alternate": compact_match(alternate),
                "divergence": divergence,
                "diagnostic_event_count": len(control["events"]),
            }
        )

    control_margins = [row["control"]["margin"] for row in seats]
    alternate_margins = [row["alternate"]["margin"] for row in seats]
    control_wood = [row["control"]["wood_edge"] for row in seats]
    alternate_wood = [row["alternate"]["wood_edge"] for row in seats]
    control_policy_score = [row["control"]["policy_score"] for row in seats]
    alternate_policy_score = [row["alternate"]["policy_score"] for row in seats]
    control_opponent_score = [row["control"]["opponent_score"] for row in seats]
    alternate_opponent_score = [row["alternate"]["opponent_score"] for row in seats]
    return {
        "seed": seed,
        "opponent": opponent_name,
        "activated": any(row["divergence"] is not None for row in seats),
        "seat_activated": [row["divergence"] is not None for row in seats],
        "diagnostic_events": all_events,
        "diagnostic_event_count": len(all_events),
        "control_paired_margin": statistics.mean(control_margins),
        "alternate_paired_margin": statistics.mean(alternate_margins),
        "delta_paired_margin": (
            statistics.mean(alternate_margins)
            - statistics.mean(control_margins)
        ),
        "delta_seat_margins": [
            alternate_margins[seat] - control_margins[seat]
            for seat in (0, 1)
        ],
        "delta_paired_wood_edge": (
            statistics.mean(alternate_wood) - statistics.mean(control_wood)
        ),
        "delta_policy_score": (
            statistics.mean(alternate_policy_score)
            - statistics.mean(control_policy_score)
        ),
        "delta_opponent_score": (
            statistics.mean(alternate_opponent_score)
            - statistics.mean(control_opponent_score)
        ),
        "seats": seats,
    }


def sentinel_cell(
    seed: int,
    raw_binary: Path,
    probe_binary: Path,
    opponent_binary: Path,
) -> dict:
    seats = []
    for seat in (0, 1):
        raw = policy_match(
            seed, raw_binary, opponent_binary, seat, diagnostic=False
        )
        probe = policy_match(
            seed, probe_binary, opponent_binary, seat, diagnostic=True
        )
        fields = (
            "margin",
            "wood_edge",
            "policy_score",
            "opponent_score",
            "outcome",
            "policy_action_stream_sha256",
            "opponent_action_stream_sha256",
            "policy_command_counts",
            "opponent_command_counts",
            "terminal_turn",
            "ended_by_stall",
            "terminal_reason",
            "terminal_state_sha256",
        )
        mismatches = [field for field in fields if raw[field] != probe[field]]
        seats.append(
            {
                "seat": seat,
                "exact": not mismatches,
                "mismatch_fields": mismatches,
                "raw": compact_match(raw),
                "probe": compact_match(probe),
                "probe_event_count": len(probe["events"]),
            }
        )
    return {
        "seed": seed,
        "opponent": "motion",
        "exact": all(row["exact"] for row in seats),
        "seats": seats,
    }


def event_episode_summary(rows: list[dict]) -> dict:
    event_count = 0
    episode_lengths = []
    by_item = Counter()
    by_phase = Counter()
    for row in rows:
        grouped = {}
        for event in row["diagnostic_events"]:
            event_count += 1
            by_item[event["item"]] += 1
            by_phase["opening" if event["turn"] < 80 else "later"] += 1
            grouped.setdefault((event["seat"], event["unit"]), []).append(
                event["turn"]
            )
        for turns in grouped.values():
            ordered = sorted(set(turns))
            length = 0
            previous = None
            for turn in ordered:
                if previous is None or turn == previous + 1:
                    length += 1
                else:
                    episode_lengths.append(length)
                    length = 1
                previous = turn
            if length:
                episode_lengths.append(length)
    return {
        "events": event_count,
        "episodes": len(episode_lengths),
        "episode_length_mean": (
            statistics.mean(episode_lengths) if episode_lengths else None
        ),
        "episode_length_median": (
            statistics.median(episode_lengths) if episode_lengths else None
        ),
        "episode_length_maximum": max(episode_lengths, default=None),
        "events_by_item_index": {
            str(item): count for item, count in sorted(by_item.items())
        },
        "events_by_phase": dict(sorted(by_phase.items())),
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
    }


def mechanism_summary(rows: list[dict]) -> dict:
    activated_cells = [row for row in rows if row["activated"]]
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
        opponent for opponent, count in family_counts.items() if count > 0
    ]
    gates = {
        "at_least_20_cells": len(activated_cells) >= 20,
        "at_least_five_each_seat": all(count >= 5 for count in seat_counts),
        "at_least_four_families": len(active_families) >= 4,
    }
    return {
        "status": "ACTIVE_WAIT" if all(gates.values()) else "WAIT_INERT",
        "gates": gates,
        "activated_cell_count": len(activated_cells),
        "activated_seed_count": len({row["seed"] for row in activated_cells}),
        "seat_game_counts": seat_counts,
        "active_family_count": len(active_families),
        "family_cell_counts": family_counts,
    }


def adjudicate(
    mechanism_status: str,
    mean_margin: float,
    seat_means: list[float],
    family_means: dict[str, float],
) -> tuple[str, dict]:
    positive_families = sum(value > 0 for value in family_means.values())
    worst_family = min(family_means.values())
    gates = {
        "active_wait": mechanism_status == "ACTIVE_WAIT",
        "mean_margin_positive": mean_margin > 0,
        "mean_margin_at_least_one": mean_margin >= 1,
        "both_seats_nonnegative": all(value >= 0 for value in seat_means),
        "at_least_four_positive_families": positive_families >= 4,
        "worst_family_at_least_minus_one": worst_family >= -1,
        "positive_family_count": positive_families,
        "worst_family_mean": worst_family,
    }
    if not gates["active_wait"]:
        verdict = "WAIT_INERT"
    elif (
        not gates["mean_margin_positive"]
        or not gates["both_seats_nonnegative"]
        or not gates["worst_family_at_least_minus_one"]
    ):
        verdict = "KEEP_RIPENESS_WAIT"
    elif (
        not gates["mean_margin_at_least_one"]
        or not gates["at_least_four_positive_families"]
    ):
        verdict = "WAIT_RESIDUAL_NONMATERIAL"
    else:
        verdict = "WAIT_RESIDUAL_MATERIAL_LOCAL"
    return verdict, gates


def aggregate(rows: list[dict]) -> dict:
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
    verdict, gates = adjudicate(
        mechanism["status"],
        metrics["paired_margin"]["mean"],
        seat_means,
        metrics["paired_margin"]["family_means"],
    )
    return {
        "mechanism": mechanism,
        "events": event_episode_summary(rows),
        "metrics": metrics,
        "margin_seat_means": seat_means,
        "verdict": verdict,
        "value_gates": gates,
    }


def run_audit(jobs: int) -> dict:
    source = LIVE_SOURCE.read_bytes()
    source_hash = sha256_bytes(source)
    sacred_hash = sha256_path(SACRED_SOURCE)
    if source_hash != LIVE_SHA256:
        raise RuntimeError(f"live source hash mismatch: {source_hash}")
    if sacred_hash != SACRED_SHA256:
        raise RuntimeError(f"sacred source hash mismatch: {sacred_hash}")
    alternate = alternate_source(source)
    probe = probe_source(source)

    value_rows = []
    sentinel_rows = []
    with tempfile.TemporaryDirectory(prefix="e5-ripeness-wait-") as directory:
        temp = Path(directory)
        probe_path = temp / "probe.rs"
        alternate_path = temp / "alternate.rs"
        probe_path.write_bytes(probe)
        alternate_path.write_bytes(alternate)
        binaries = {}
        compile_source(LIVE_SOURCE, temp / "raw", "e5_raw")
        compile_source(probe_path, temp / "probe", "e5_probe")
        compile_source(alternate_path, temp / "alternate", "e5_alternate")
        binaries["raw"] = temp / "raw"
        binaries["probe"] = temp / "probe"
        binaries["alternate"] = temp / "alternate"
        for index, opponent_name in enumerate(OPPONENT_NAMES):
            compile_source(
                OPPONENT_SOURCES[opponent_name],
                temp / opponent_name,
                f"e5_opponent_{index}_{opponent_name}",
            )
            binaries[opponent_name] = temp / opponent_name
        runtime_shim = compile_runtime_shim(temp)
        print(
            "compiled raw, probe, alternate, six opponents, and deterministic runtime",
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
                        binaries["probe"],
                        binaries["alternate"],
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

            sentinel_tasks = list(SENTINEL_SEEDS)
            with ThreadPoolExecutor(max_workers=jobs) as executor:
                futures = {
                    executor.submit(
                        sentinel_cell,
                        seed,
                        binaries["raw"],
                        binaries["probe"],
                        binaries["motion"],
                    ): seed
                    for seed in sentinel_tasks
                }
                for future in as_completed(futures):
                    sentinel_rows.append(future.result())
        finally:
            if previous_preload is None:
                os.environ.pop("LD_PRELOAD", None)
            else:
                os.environ["LD_PRELOAD"] = previous_preload

    value_rows.sort(key=lambda row: (row["seed"], row["opponent"]))
    sentinel_rows.sort(key=lambda row: row["seed"])
    value_keys = [(row["seed"], row["opponent"]) for row in value_rows]
    coverage = {
        "value_cells": len(value_rows),
        "unique_value_keys": len(set(value_keys)),
        "value_seat_games_per_policy": 2 * len(value_rows),
        "sentinel_cells": len(sentinel_rows),
        "complete": (
            len(value_rows) == 360
            and len(set(value_keys)) == 360
            and len(sentinel_rows) == 8
        ),
    }
    sentinel_integrity = {
        "cells": len(sentinel_rows),
        "seat_games": 2 * len(sentinel_rows),
        "exact_cells": sum(row["exact"] for row in sentinel_rows),
        "all_exact": all(row["exact"] for row in sentinel_rows),
    }
    if not coverage["complete"]:
        raise RuntimeError(f"coverage failed: {coverage}")
    if not sentinel_integrity["all_exact"]:
        raise RuntimeError("raw/probe sentinel identity failed")
    if any(
        seat["control"]["malformed_commands"]
        or seat["alternate"]["malformed_commands"]
        or seat["control"]["unexpected_stderr_bytes"]
        or seat["alternate"]["unexpected_stderr_bytes"]
        for row in value_rows
        for seat in row["seats"]
    ):
        raise RuntimeError("command or stderr integrity failed")

    summary = aggregate(value_rows)
    return {
        "schema": 1,
        "scope": (
            "exact-live one-candidate deterministic local causal audit on reused maps; "
            "not an Arena predictor or candidate"
        ),
        "jobs": jobs,
        "sources": {
            "control": {
                "path": str(LIVE_SOURCE.relative_to(REPO)),
                "sha256": source_hash,
            },
            "probe": {
                "persistent": False,
                "replacement_count": 1,
                "sha256": sha256_bytes(probe),
            },
            "alternate": {
                "persistent": False,
                "replacement_count": 1,
                "from": ALTERNATE_FROM,
                "to": ALTERNATE_TO,
                "sha256": sha256_bytes(alternate),
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
        },
        "coverage": coverage,
        "sentinel_integrity": sentinel_integrity,
        "aggregate": summary,
        "hashes": {
            "value_rows_sha256": rows_sha256(value_rows),
            "sentinel_rows_sha256": rows_sha256(sentinel_rows),
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
        },
        "value_rows": value_rows,
        "sentinel_rows": sentinel_rows,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def self_test() -> None:
    source = (
        b"x"
        + ALTERNATE_FROM.encode()
        + b"y"
        + PROBE_FROM.encode()
        + b"z"
    )
    assert alternate_source(source).count(ALTERNATE_TO.encode()) == 1
    assert probe_source(source).count(PROBE_TO.encode()) == 1
    event = parse_probe_events(
        "@E5_WAIT t=12 unit=3 cell=4,5 item=2 size=4 cooldown=1 target=4,5\n"
    )
    assert event == [
        {
            "turn": 12,
            "unit": 3,
            "cell": [4, 5],
            "item": 2,
            "size": 4,
            "cooldown": 1,
            "target": [4, 5],
        }
    ]
    assert commands_by_unit(
        ["TRAIN 1 1 0 1", "WAIT", "MOVE 7 2 3"], [4, 7]
    ) == {4: "WAIT", 7: "MOVE 7 2 3"}
    families = {name: 1.0 for name in OPPONENT_NAMES}
    assert adjudicate("WAIT_INERT", 2, [1, 1], families)[0] == "WAIT_INERT"
    assert (
        adjudicate("ACTIVE_WAIT", 0.5, [1, 1], families)[0]
        == "WAIT_RESIDUAL_NONMATERIAL"
    )
    assert (
        adjudicate("ACTIVE_WAIT", 1, [0, 1], families)[0]
        == "WAIT_RESIDUAL_MATERIAL_LOCAL"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "e5-ripeness-wait-audit-result-2026-07-30.json",
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
        f"mean margin={summary['metrics']['paired_margin']['mean']:+.6f}",
        flush=True,
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
