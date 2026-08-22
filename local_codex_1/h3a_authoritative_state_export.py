#!/usr/bin/env python3
"""Replay the exact 17 open H3a games into outcome-blind authoritative decision states."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_SOURCE_PACKAGE_SHA256 = (
    "e3029c7e506e3da23c7d2dba5547cbb219df435b9924208db0c3a01701d2c49b"
)
EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "f3b28d735fe69a5b84ff005b718ec841167d75ba2c767f14c75bfde5583d053c"
)
EXPECTED_REFEREE_SHA256 = (
    "518c222881ac23f8548cc13c858bacc93577ea920ecfbdbf0fd0e588cad1bf83"
)
EXPECTED_LOCKED_RUNNER_SHA256 = (
    "1054a047a410b23ca952e3ed6b96df12662615bb630597f68b1d551b9b056a3f"
)
EXPECTED_SACRED_SHA256 = (
    "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
)
EXPECTED_IDS = (
    897780891,
    897781216,
    897781413,
    897781719,
    897781840,
    897781987,
    897782076,
    897782213,
    897782302,
    897782366,
    897782128,
    897782246,
    897781650,
    897781674,
    897782379,
    897782201,
    897782068,
)
MOVE_RE = re.compile(
    r"^\$(?P<player>\d+): troll (?P<unit>\d+) moved to "
    r"\((?P<x>-?\d+), (?P<y>-?\d+)\)$"
)
TRAIN_RE = re.compile(r"^\$(?P<player>\d+): trained a troll$")
PLANT_RE = re.compile(
    r"^\$(?P<player>\d+): troll (?P<unit>\d+) planted a (?P<species>[A-Z]+)$"
)
NUMERIC_ALIAS_RE = re.compile(r"^(PICK|PLANT)\s+\d+\s+([0-3])$", re.IGNORECASE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def parse_view(frame: dict[str, Any]) -> dict[str, Any]:
    view = frame["view"]
    _, separator, payload = view.partition("\n")
    if not separator or not payload.strip():
        raise ValueError("frame lacks a viewer payload")
    return json.loads(payload)


def parse_inventories(text: str) -> list[list[int]]:
    rows = [[int(value) for value in row.split()] for row in text.splitlines()]
    if len(rows) != 2 or any(len(row) != 6 for row in rows):
        raise ValueError(f"unexpected inventory shape: {rows}")
    return rows


def split_commands(raw: str) -> list[str]:
    return [command.strip() for command in raw.split(";") if command.strip()]


def source_rows(package_path: Path) -> list[dict[str, Any]]:
    if sha256_file(package_path) != EXPECTED_SOURCE_PACKAGE_SHA256:
        raise ValueError("source public-frame package hash mismatch")
    with gzip.open(package_path, "rt", encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream]
    ids = tuple(row["game_id"] for row in rows)
    if ids != EXPECTED_IDS:
        raise ValueError(f"source game order mismatch: {ids}")
    return rows


def force_movement_outcomes(
    raw: str, landed: dict[int, tuple[int, int]]
) -> tuple[str, int, int, int]:
    commands = []
    forced_moves = 0
    stopped_moves = 0
    empty_messages = 0
    for command in split_commands(raw):
        fields = command.split()
        if len(fields) == 1 and fields[0].upper() == "MSG":
            commands.append("MSG replay-empty")
            empty_messages += 1
        elif len(fields) == 4 and fields[0].upper() == "MOVE":
            unit_id = int(fields[1])
            if unit_id in landed:
                x, y = landed[unit_id]
                commands.append(f"MOVE {unit_id} {x} {y}")
                forced_moves += 1
            else:
                commands.append("WAIT")
                stopped_moves += 1
        else:
            commands.append(command)
    return ";".join(commands), forced_moves, stopped_moves, empty_messages


def command_input(
    row: dict[str, Any]
) -> tuple[str, Counter[tuple[str, str]], Counter[str], Counter[str]]:
    seed_text = row["referee_input"].strip()
    if not seed_text.startswith("seed="):
        raise ValueError(f"game {row['game_id']} has unexpected referee input")
    seed = int(seed_text.split("=", 1)[1])
    lines = [f"{row['game_id']}\t{seed}\t{row['current_seat']}\t300"]
    aliases: Counter[tuple[str, str]] = Counter()
    movement: Counter[str] = Counter()
    syntax: Counter[str] = Counter()
    for turn in range(1, 301):
        frame0 = row["frames"][2 * turn - 1]
        frame1 = row["frames"][2 * turn]
        if (frame0["agentId"], frame1["agentId"]) != (0, 1):
            raise ValueError(f"game {row['game_id']} turn {turn} frame order mismatch")
        commands = [frame0["stdout"], frame1["stdout"]]
        move_facts, _, _ = summary_facts(frame1.get("summary") or "")
        landed = {unit_id: (x, y) for _, unit_id, x, y in move_facts}
        if len(landed) != len(move_facts):
            raise ValueError(f"game {row['game_id']} turn {turn} duplicate move summary")
        forced = []
        for raw in commands:
            for command in split_commands(raw):
                match = NUMERIC_ALIAS_RE.fullmatch(command)
                if match:
                    aliases[(match.group(1).upper(), match.group(2))] += 1
            rewritten, forced_count, stopped_count, empty_messages = force_movement_outcomes(
                raw, landed
            )
            forced.append(rewritten)
            movement["forced_to_public_landing"] += forced_count
            movement["replaced_with_wait"] += stopped_count
            syntax["empty_msg_normalized"] += empty_messages
        lines.append(
            f"{turn}\t{commands[0].encode('utf-8').hex()}\t"
            f"{commands[1].encode('utf-8').hex()}\t"
            f"{forced[0].encode('utf-8').hex()}\t{forced[1].encode('utf-8').hex()}"
        )
    return "\n".join(lines) + "\n", aliases, movement, syntax


def platform_map(row: dict[str, Any]) -> tuple[int, int, list[str], list[list[int]]]:
    initial = parse_view(row["frames"][0])
    map_lines = initial["global"]["inputmodule"].splitlines()
    width, height = (int(value) for value in map_lines[0].split())
    rows = map_lines[1:]
    if len(rows) != height or any(len(line) != width for line in rows):
        raise ValueError(f"game {row['game_id']} initial map shape mismatch")
    inventories = parse_inventories(initial["frame"]["inputmodule"])
    return width, height, rows, inventories


def regenerated_map_rows(map_record: dict[str, Any], resident_seat: int) -> list[str]:
    width = map_record["width"]
    height = map_record["height"]
    walkable = {tuple(cell) for cell in map_record["walkable"]}
    iron = {tuple(cell) for cell in map_record["iron"]}
    water = {tuple(cell) for cell in map_record["water"]}
    shacks: list[tuple[int, int] | None] = [None, None]
    shacks[resident_seat] = tuple(map_record["shacks"][0])
    shacks[1 - resident_seat] = tuple(map_record["shacks"][1])
    rows = []
    for y in range(height):
        values = []
        for x in range(width):
            cell = (x, y)
            if cell == shacks[0]:
                values.append("0")
            elif cell == shacks[1]:
                values.append("1")
            elif cell in iron:
                values.append("+")
            elif cell in water:
                values.append("~")
            elif cell in walkable:
                values.append(".")
            else:
                values.append("#")
        rows.append("".join(values))
    return rows


def normalized_to_global(values: list[Any], resident_seat: int) -> list[Any]:
    global_values: list[Any] = [None, None]
    global_values[resident_seat] = values[0]
    global_values[1 - resident_seat] = values[1]
    return global_values


def summary_facts(summary: str) -> tuple[list[tuple[int, int, int, int]], Counter[int], Counter[tuple[int, int, str]]]:
    moves = []
    trains: Counter[int] = Counter()
    plants: Counter[tuple[int, int, str]] = Counter()
    for line in summary.splitlines():
        move = MOVE_RE.fullmatch(line)
        if move:
            moves.append(tuple(int(move.group(key)) for key in ("player", "unit", "x", "y")))
            continue
        train = TRAIN_RE.fullmatch(line)
        if train:
            trains[int(train.group("player"))] += 1
            continue
        plant = PLANT_RE.fullmatch(line)
        if plant:
            plants[(
                int(plant.group("player")),
                int(plant.group("unit")),
                plant.group("species"),
            )] += 1
    return moves, trains, plants


def score(inventory: list[int]) -> int:
    return sum(inventory[:4]) + 4 * inventory[5]


def replay_one(
    row: dict[str, Any], binary: Path
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
    Counter[tuple[str, str]],
    Counter[str],
    Counter[str],
]:
    replay_input, aliases, movement, syntax = command_input(row)
    completed = subprocess.run(
        [str(binary)],
        input=replay_input,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"game {row['game_id']} replay failed ({completed.returncode}): "
            f"{completed.stderr[-2000:]}"
        )
    records = [json.loads(line) for line in completed.stdout.splitlines()]
    maps = [record for record in records if record["kind"] == "map"]
    decisions = [record for record in records if record["kind"] == "decision"]
    validations = [record for record in records if record["kind"] == "validation"]
    if (len(maps), len(decisions), len(validations)) != (1, 300, 300):
        raise ValueError(f"game {row['game_id']} replay record cardinality mismatch")
    map_record = maps[0]
    seat = row["current_seat"]
    width, height, expected_map, expected_initial_inventories = platform_map(row)
    if (map_record["width"], map_record["height"]) != (width, height):
        raise ValueError(f"game {row['game_id']} generated dimensions mismatch")
    if regenerated_map_rows(map_record, seat) != expected_map:
        raise ValueError(f"game {row['game_id']} generated terrain mismatch")
    if normalized_to_global(map_record["initial_inventories"], seat) != expected_initial_inventories:
        raise ValueError(f"game {row['game_id']} starting inventory mismatch")

    movement_facts = 0
    train_facts = 0
    plant_facts = 0
    prior_roster = Counter({0: 1, 1: 1})
    for turn, (decision, validation) in enumerate(zip(decisions, validations), 1):
        if decision["turn"] != turn or validation["turn"] != turn:
            raise ValueError(f"game {row['game_id']} turn sequence mismatch at {turn}")
        resident_frame = row["frames"][2 * turn - 1 + seat]
        if decision["issued_commands"] != split_commands(resident_frame["stdout"]):
            raise ValueError(f"game {row['game_id']} resident command mismatch at {turn}")
        viewer = parse_view(row["frames"][2 * turn])
        expected_inventories = parse_inventories(viewer["inputmodule"])
        if validation["inventories"] != expected_inventories:
            raise ValueError(f"game {row['game_id']} inventory mismatch at turn {turn}")

        units = {unit[0]: (unit[1], unit[2], unit[3]) for unit in validation["units"]}
        roster = Counter(unit[0] for unit in units.values())
        moves, trains, planted = summary_facts(row["frames"][2 * turn].get("summary") or "")
        for player, unit_id, x, y in moves:
            if units.get(unit_id) != (player, x, y):
                raise ValueError(
                    f"game {row['game_id']} move mismatch at turn {turn}: "
                    f"unit {unit_id} expected {(player, x, y)} got {units.get(unit_id)}"
                )
        movement_facts += len(moves)
        landed_trains = Counter(
            {player: roster[player] - prior_roster[player] for player in (0, 1)}
        )
        landed_trains += Counter()
        if trains != landed_trains:
            raise ValueError(
                f"game {row['game_id']} train mismatch at turn {turn}: "
                f"summary={trains}, replay={landed_trains}"
            )
        train_facts += sum(trains.values())
        prior_roster = roster

        created: Counter[tuple[int, int, str]] = Counter()
        for plant in validation["created"]:
            player = int(plant["created_by"].removeprefix("seat"))
            for planter_id in plant["planter_ids"]:
                created[(player, planter_id, plant["species"])] += 1
        if planted != created:
            raise ValueError(
                f"game {row['game_id']} plant mismatch at turn {turn}: "
                f"summary={planted}, replay={created}"
            )
        plant_facts += sum(planted.values())

    final_inventories = validations[-1]["inventories"]
    final_scores = [score(inventory) for inventory in final_inventories]
    if final_scores != row["scores"]:
        raise ValueError(
            f"game {row['game_id']} final score mismatch: replay={final_scores}, "
            f"source={row['scores']}"
        )
    diagnostics = {
        "critical_issues": validations[-1]["critical_issue_count"],
        "final_scores": final_scores,
        "inventory_snapshots_checked": 301,
        "issue_reasons": validations[-1]["issue_reasons"],
        "movement_facts_checked": movement_facts,
        "plant_facts_checked": plant_facts,
        "train_facts_checked": train_facts,
        "unclassified_issues": validations[-1]["unclassified_issue_count"],
        "legality_issues": validations[-1]["legality_issue_count"],
    }
    if diagnostics["critical_issues"] or diagnostics["unclassified_issues"]:
        raise ValueError(f"game {row['game_id']} has critical/unclassified replay issues")
    return map_record, decisions, diagnostics, aliases, movement, syntax


def gzip_deterministic(data: bytes) -> bytes:
    return gzip.compress(data, compresslevel=9, mtime=0)


def export(
    package_path: Path,
    source_manifest_path: Path,
    binary: Path,
    output_prefix: Path,
    created_utc: str,
    repo_root: Path,
) -> tuple[Path, Path, Path]:
    if sha256_file(source_manifest_path) != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise ValueError("source public-frame manifest hash mismatch")
    locked_paths = {
        "rust/src/game/a2_referee_parity.rs": EXPECTED_REFEREE_SHA256,
        "rust/src/bin/a2_0b_referee_parity.rs": EXPECTED_LOCKED_RUNNER_SHA256,
        "rust/src/bin/yamo_orchard_live.rs": EXPECTED_SACRED_SHA256,
    }
    for logical_path, expected_hash in locked_paths.items():
        if sha256_file(repo_root / logical_path) != expected_hash:
            raise ValueError(f"locked source hash mismatch: {logical_path}")
    if not binary.is_file():
        raise FileNotFoundError(binary)

    rows = source_rows(package_path)
    map_lines = []
    decision_lines = []
    game_manifest = []
    aliases_total: Counter[tuple[str, str]] = Counter()
    movement_total: Counter[str] = Counter()
    syntax_total: Counter[str] = Counter()
    validation_totals: Counter[str] = Counter()
    issue_reason_totals: Counter[str] = Counter()
    affected_alias_games = []
    for row in rows:
        map_record, decisions, diagnostics, aliases, movement, syntax = replay_one(row, binary)
        map_line = compact_json(map_record)
        encoded_decisions = [compact_json(decision) for decision in decisions]
        map_lines.append(map_line)
        decision_lines.extend(encoded_decisions)
        aliases_total.update(aliases)
        movement_total.update(movement)
        syntax_total.update(syntax)
        if aliases:
            affected_alias_games.append(row["game_id"])
        validation_totals.update(
            {
                key: value
                for key, value in diagnostics.items()
                if isinstance(value, int) and key != "final_scores"
            }
        )
        issue_reason_totals.update(diagnostics["issue_reasons"])
        game_manifest.append(
            {
                "cohort": row["cohort"],
                "decision_rows": len(decisions),
                "decision_uncompressed_sha256": sha256_bytes(
                    b"\n".join(encoded_decisions) + b"\n"
                ),
                "game_id": row["game_id"],
                "map_uncompressed_sha256": sha256_bytes(map_line + b"\n"),
                "numeric_aliases_normalized": sum(aliases.values()),
                "movement_outcome_forcing": dict(sorted(movement.items())),
                "syntax_normalization": dict(sorted(syntax.items())),
                "referee_seed": map_record["referee_seed"],
                "seat": row["current_seat"],
                "validation": diagnostics,
            }
        )

    maps_jsonl = b"\n".join(map_lines) + b"\n"
    decisions_jsonl = b"\n".join(decision_lines) + b"\n"
    maps_gzip = gzip_deterministic(maps_jsonl)
    decisions_gzip = gzip_deterministic(decisions_jsonl)
    maps_path = output_prefix.with_suffix(".maps.jsonl.gz")
    decisions_path = output_prefix.with_suffix(".decisions.jsonl.gz")
    manifest_path = output_prefix.with_suffix(".manifest.json")
    atomic_write(maps_path, maps_gzip)
    atomic_write(decisions_path, decisions_gzip)

    manifest = {
        "created_utc": created_utc,
        "exact_ids_only": True,
        "files": {
            maps_path.name: {
                "bytes": len(maps_gzip),
                "rows": len(map_lines),
                "sha256": sha256_bytes(maps_gzip),
                "uncompressed_bytes": len(maps_jsonl),
                "uncompressed_sha256": sha256_bytes(maps_jsonl),
            },
            decisions_path.name: {
                "bytes": len(decisions_gzip),
                "rows": len(decision_lines),
                "sha256": sha256_bytes(decisions_gzip),
                "uncompressed_bytes": len(decisions_jsonl),
                "uncompressed_sha256": sha256_bytes(decisions_jsonl),
            },
        },
        "games": game_manifest,
        "locked_sources": {
            logical_path: expected_hash for logical_path, expected_hash in locked_paths.items()
        },
        "numeric_alias_normalization": {
            "affected_game_ids": affected_alias_games,
            "count": sum(aliases_total.values()),
            "counts": {
                f"{verb}_{item}": count
                for (verb, item), count in sorted(aliases_total.items())
            },
            "mapping": {"0": "PLUM", "1": "LEMON", "2": "APPLE", "3": "BANANA"},
            "reason": (
                "The locked parser explicitly accepts numeric fruit aliases but passes the "
                "raw numeric token to the historical engine, which panics. The extraction "
                "wrapper canonicalizes only that accepted token before the unchanged locked "
                "referee step; raw issued commands remain preserved in decision rows."
            ),
        },
        "public_movement_outcome_forcing": {
            "counts": dict(sorted(movement_total.items())),
            "reason": (
                "The locked continued-RNG replay first diverged from a public landed MOVE "
                "at game 897781216 turn 12. Each raw MOVE is therefore replaced only for "
                "the unchanged referee step by its same-turn public summary landing, or WAIT "
                "when no landing occurred. Raw commands remain in decision rows. Current-turn "
                "outcomes are used only to construct the next decision state."
            ),
        },
        "accepted_syntax_normalization": {
            "counts": dict(sorted(syntax_total.items())),
            "reason": (
                "The platform accepts an empty MSG command (`MSG ;`). The locked parser "
                "classifies trimmed `MSG` as unknown while accepting `MSG <text>`. The replay "
                "wrapper supplies inert text only to the unchanged referee step; raw issued "
                "commands remain preserved in decision rows."
            ),
        },
        "referee_binary": {
            "logical_build_path": "rust/target/release/h3a_open_trajectory_state_export",
            "sha256": sha256_file(binary),
            "source_logical_path": "rust/src/bin/h3a_open_trajectory_state_export.rs",
            "source_sha256": sha256_file(
                repo_root / "rust/src/bin/h3a_open_trajectory_state_export.rs"
            ),
        },
        "schema": (
            "One static-map row per game and one outcome-blind authoritative state row per "
            "resident decision. Trees use exact policy cell identity plus current input order; "
            "created_by is causal initial/landed-plant provenance."
        ),
        "schema_version": 1,
        "sealed_data_included": False,
        "source_package": {
            "games_sha256": EXPECTED_SOURCE_PACKAGE_SHA256,
            "manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        },
        "task_id": "20260802-h3a-conditioned-value-unblock",
        "validation": {
            "decision_rows": len(decision_lines),
            "games": len(rows),
            "map_rows": len(map_lines),
            "outcome_fields_in_decision_rows": False,
            "legality_issue_reasons": dict(sorted(issue_reason_totals.items())),
            **dict(sorted(validation_totals.items())),
        },
    }
    manifest_bytes = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    atomic_write(manifest_path, manifest_bytes)
    return maps_path, decisions_path, manifest_path


def self_test() -> None:
    assert split_commands("MSG test;PICK 0 0; \n") == ["MSG test", "PICK 0 0"]
    assert parse_inventories("1 2 3 4 5 6\n6 5 4 3 2 1") == [
        [1, 2, 3, 4, 5, 6],
        [6, 5, 4, 3, 2, 1],
    ]
    moves, trains, plants = summary_facts(
        "$0: troll 2 moved to (3, 4)\n$1: trained a troll\n"
        "$1: troll 3 planted a BANANA"
    )
    assert moves == [(0, 2, 3, 4)]
    assert trains == Counter({1: 1})
    assert plants == Counter({(1, 3, "BANANA"): 1})
    assert score([1, 2, 3, 4, 5, 6]) == 34
    rewritten, forced, stopped, empty = force_movement_outcomes(
        "MSG ;MOVE 2 9 9;MOVE 3 8 8;PICK 4 0", {2: (4, 5)}
    )
    assert rewritten == "MSG replay-empty;MOVE 2 4 5;WAIT;PICK 4 0"
    assert (forced, stopped, empty) == (1, 1, 1)
    print("self-test: ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--output-prefix", type=Path)
    parser.add_argument("--created-utc")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    required = (
        args.package,
        args.source_manifest,
        args.binary,
        args.output_prefix,
        args.created_utc,
    )
    if any(value is None for value in required):
        raise SystemExit(
            "--package, --source-manifest, --binary, --output-prefix and --created-utc "
            "are required"
        )
    paths = export(
        args.package,
        args.source_manifest,
        args.binary,
        args.output_prefix,
        args.created_utc,
        args.repo_root,
    )
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
