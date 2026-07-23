#!/usr/bin/env python3
"""Run the frozen D33/D33a/D33b official-map parity gate."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.arena_rollout_forensics import render_turn_one  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "data/analysis/live-agent-6553250/d33-official-map-confirmation-manifest.json"
D32_PANEL = REPO / "data/panels/d32a-deterministic-field-option-ab-20260720.json"
CHECKPOINT = REPO / "data/analysis/live-agent-6553250/d29b-pretransfer-resident-checkpoint-2026-07-20.json"
BINARY = REPO / "rust/target/release/d33_official_mapgen"
SOURCE = REPO / "rust/src/game/official_mapgen.rs"
BIN_SOURCE = REPO / "rust/src/bin/d33_official_mapgen.rs"
OUTPUT = REPO / "data/analysis/live-agent-6553250/d33-official-mapgen-parity-result-2026-07-20.json"
MANIFEST_BUILDER = REPO / "cgauto/make_d33_official_map_manifest.py"
PROTOCOL = REPO / "data/analysis/live-agent-6553250/d33-authoritative-official-mapgen-parity-protocol-2026-07-20.md"
AMENDMENT_A = REPO / "data/analysis/live-agent-6553250/d33a-sha1prng-seed-layer-amendment-2026-07-20.md"
AMENDMENT_B = REPO / "data/analysis/live-agent-6553250/d33b-replay-plant-order-amendment-2026-07-20.md"
FRUITS = ("PLUM", "LEMON", "APPLE", "BANANA")
NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def parse_turn_one(text: str) -> dict:
    if not text.endswith("\n"):
        raise ValueError("missing trailing newline")
    lines = text.splitlines()
    if not lines:
        raise ValueError("empty turn-one stream")
    header = lines[0].split()
    if len(header) != 2:
        raise ValueError("invalid dimension header")
    width, height = map(int, header)
    if len(lines) < height + 5:
        raise ValueError("truncated turn-one stream")
    grid = lines[1 : 1 + height]
    if len(grid) != height or any(len(row) != width for row in grid):
        raise ValueError("invalid grid dimensions")
    inventories = [
        [int(value) for value in lines[height + offset].split()]
        for offset in (1, 2)
    ]
    if any(len(inventory) != 6 for inventory in inventories):
        raise ValueError("invalid inventory")
    plant_count_index = height + 3
    plant_count = int(lines[plant_count_index])
    plant_start = plant_count_index + 1
    plant_end = plant_start + plant_count
    if plant_end >= len(lines):
        raise ValueError("truncated plant list")
    plants = lines[plant_start:plant_end]
    for line in plants:
        fields = line.split()
        if len(fields) != 7 or fields[0] not in FRUITS:
            raise ValueError("invalid plant line")
        list(map(int, fields[1:]))
    unit_count = int(lines[plant_end])
    units = lines[plant_end + 1 :]
    if len(units) != unit_count:
        raise ValueError("invalid unit count")
    for line in units:
        fields = line.split()
        if len(fields) != 14:
            raise ValueError("invalid unit line")
        list(map(int, fields))
    return {
        "width": width,
        "height": height,
        "grid": grid,
        "inventories": inventories,
        "plants": plants,
        "units": units,
        "prefix": lines[:plant_start],
        "suffix": lines[plant_end:],
        "trailing_newline": True,
    }


def live_plant_order(parsed: dict) -> bool:
    plants = [line.split() for line in parsed["plants"]]
    ranks = [FRUITS.index(fields[0]) for fields in plants]
    if ranks != sorted(ranks):
        return False
    cursor = 0
    while cursor < len(plants):
        plant_type = plants[cursor][0]
        end = cursor
        while end < len(plants) and plants[end][0] == plant_type:
            end += 1
        if (end - cursor) % 2:
            return False
        for index in range(cursor, end, 2):
            first, mirror = plants[index], plants[index + 1]
            x0, y0 = map(int, first[1:3])
            x1, y1 = map(int, mirror[1:3])
            if (x1, y1) != (parsed["width"] - 1 - x0, parsed["height"] - 1 - y0):
                return False
            if first[0] != mirror[0] or first[3:] != mirror[3:]:
                return False
        cursor = end
    return True


def canonical_comparison(expected_text: str, generated_text: str) -> dict:
    try:
        expected = parse_turn_one(expected_text)
        generated = parse_turn_one(generated_text)
    except (TypeError, ValueError) as error:
        return {
            "pass": False,
            "parse_error": type(error).__name__,
            "prefix_exact": False,
            "plant_multiset_exact": False,
            "unit_suffix_exact": False,
            "generated_live_order": False,
            "trailing_newline_exact": expected_text.endswith("\n")
            and generated_text.endswith("\n"),
        }
    result = {
        "parse_error": None,
        "prefix_exact": expected["prefix"] == generated["prefix"],
        "plant_multiset_exact": Counter(expected["plants"])
        == Counter(generated["plants"]),
        "unit_suffix_exact": expected["suffix"] == generated["suffix"],
        "generated_live_order": live_plant_order(generated),
        "trailing_newline_exact": expected_text.endswith("\n")
        and generated_text.endswith("\n"),
    }
    result["pass"] = all(
        result[key]
        for key in (
            "prefix_exact",
            "plant_multiset_exact",
            "unit_suffix_exact",
            "generated_live_order",
            "trailing_newline_exact",
        )
    )
    return result


def adjacent(cell: tuple[int, int], width: int, height: int):
    for dx, dy in NEIGHBORS:
        neighbor = (cell[0] + dx, cell[1] + dy)
        if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
            yield neighbor


def distances(grid: list[str], start: tuple[int, int]) -> dict[tuple[int, int], int]:
    height, width = len(grid), len(grid[0])
    result = {start: 0}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for neighbor in adjacent(cell, width, height):
            if grid[neighbor[1]][neighbor[0]] == "." and neighbor not in result:
                result[neighbor] = result[cell] + 1
                queue.append(neighbor)
    return result


def structural_invariants(text: str) -> dict:
    try:
        parsed = parse_turn_one(text)
    except (TypeError, ValueError):
        return {"pass": False, "parse": False}
    width, height, grid = parsed["width"], parsed["height"], parsed["grid"]
    cells = {
        symbol: {(x, y) for y, row in enumerate(grid) for x, value in enumerate(row) if value == symbol}
        for symbol in ".~#+01"
    }
    allowed = all(set(row) <= set(".~#+01") for row in grid)
    point_symmetric = True
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            mirror = grid[height - 1 - y][width - 1 - x]
            expected = {"0": "1", "1": "0"}.get(value, value)
            point_symmetric &= mirror == expected
    shacks_exact = len(cells["0"]) == len(cells["1"]) == 1
    shack0 = next(iter(cells["0"]), (-1, -1))
    shack1 = next(iter(cells["1"]), (-1, -1))
    shack_has_grass = any(neighbor in cells["."] for neighbor in adjacent(shack0, width, height))
    shack_clear_of_iron = all(neighbor not in cells["+"] for neighbor in adjacent(shack0, width, height))
    iron_reachable = any(
        neighbor in cells["."]
        for iron in cells["+"]
        for neighbor in adjacent(iron, width, height)
    )
    connected = False
    if cells["."]:
        reached = distances(grid, next(iter(cells["."])))
        connected = cells["."] <= reached.keys()
    shack_distances = distances(grid, shack0)
    opponent_distance = min(
        (shack_distances.get(neighbor, 10**9) + 1 for neighbor in adjacent(shack1, width, height) if neighbor in cells["."]),
        default=10**9,
    )

    plant_fields = [line.split() for line in parsed["plants"]]
    plant_positions = [(int(fields[1]), int(fields[2])) for fields in plant_fields]
    plant_counts = Counter(fields[0] for fields in plant_fields)
    plant_ranges = all(
        count in {2, 4, 6} for count in plant_counts.values()
    ) and set(plant_counts) == set(FRUITS)
    plants_on_unique_grass = len(plant_positions) == len(set(plant_positions)) and all(
        position in cells["."] for position in plant_positions
    )
    inventory_valid = (
        parsed["inventories"][0] == parsed["inventories"][1]
        and all(2 <= value <= 10 for value in parsed["inventories"][0][:5])
        and parsed["inventories"][0][5] == 0
    )
    expected_units = [
        [0, 0, *shack0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, *shack1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    ]
    units_valid = [list(map(int, line.split())) for line in parsed["units"]] == expected_units
    checks = {
        "parse": True,
        "dimensions": 8 <= height <= 11 and width == 2 * height,
        "symbols": allowed,
        "point_symmetry": point_symmetric,
        "shacks": shacks_exact and shack_has_grass and shack_clear_of_iron,
        "terrain_counts": len(cells["+"]) in {2, 4}
        and 2 <= len(cells["#"]) <= 20
        and len(cells["#"]) % 2 == 0
        and len(cells["~"]) > 0,
        "connectivity": connected and iron_reachable and opponent_distance <= 16,
        "inventory": inventory_valid,
        "plants": plant_ranges and plants_on_unique_grass and live_plant_order(parsed),
        "units": units_valid,
    }
    checks["pass"] = all(checks.values())
    return checks


def run_generator(binary: Path, seed: int) -> str:
    completed = subprocess.run(
        [binary, str(seed)],
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    if completed.returncode or completed.stderr:
        raise RuntimeError(
            f"generator failed for seed {seed}: exit={completed.returncode}, stderr_bytes={len(completed.stderr.encode())}"
        )
    return completed.stdout


def development_witnesses(panel: dict) -> list[dict]:
    selected = {}
    for row in panel["rows"]:
        selected.setdefault(int(row["block"]), row)
    if sorted(selected) != [0, 1, 2]:
        raise ValueError("D32 panel does not contain exactly three development blocks")
    return [selected[index] for index in sorted(selected)]


def compare_one(expected: str, generated: str, repeated: str) -> dict:
    comparison = canonical_comparison(expected, generated)
    invariants = structural_invariants(generated)
    return {
        **comparison,
        "deterministic_repeat": generated == repeated,
        "invariants": invariants,
        "expected_bytes": len(expected.encode()),
        "expected_sha256": text_digest(expected),
        "generated_bytes": len(generated.encode()),
        "generated_sha256": text_digest(generated),
        "repeat_sha256": text_digest(repeated),
        "complete_pass": comparison["pass"]
        and generated == repeated
        and invariants["pass"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--panel", type=Path, default=D32_PANEL)
    parser.add_argument("--binary", type=Path, default=BINARY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    panel = json.loads(args.panel.read_text())
    development = []
    for row in development_witnesses(panel):
        expected = row["trace"]["turn_one"]["text"]
        generated = run_generator(args.binary, int(row["seed"]))
        repeated = run_generator(args.binary, int(row["seed"]))
        result = compare_one(expected, generated, repeated)
        result.update({"block": int(row["block"]), "seed": int(row["seed"])})
        development.append(result)

    development_pass = len(development) == 3 and all(row["complete_pass"] for row in development)

    # Freeze implementation identity before any held-out raw replay is opened.
    implementation = {
        "official_mapgen_source_sha256": digest(SOURCE),
        "renderer_source_sha256": digest(BIN_SOURCE),
        "release_binary_sha256": digest(args.binary),
        "analyzer_source_sha256": digest(Path(__file__)),
        "protocol_sha256": digest(PROTOCOL),
        "sha1prng_amendment_sha256": digest(AMENDMENT_A),
        "plant_order_amendment_sha256": digest(AMENDMENT_B),
    }

    checkpoint = json.loads(CHECKPOINT.read_text())
    excluded = {int(row["game_id"]) for row in checkpoint["rows"]}
    excluded.update(int(row["game_id"]) for row in panel["rows"])
    game_ids = [int(row["game_id"]) for row in manifest["games"]]
    seeds = [int(row["seed"]) for row in manifest["games"]]
    manifest_checks = {
        "schema_1": manifest.get("schema") == 1,
        "source_commit_exact": manifest.get("source_commit")
        == "290129129db7a7539d98739ebdb0ed63ee6ceb50",
        "count_120": len(game_ids) == 120,
        "unique_game_ids": len(set(game_ids)) == len(game_ids),
        "unique_seeds": len(set(seeds)) == len(seeds),
        "ascending_game_ids": game_ids == sorted(game_ids),
        "zero_seeds": sum(seed == 0 for seed in seeds),
        "excluded_overlap": len(set(game_ids) & excluded),
        "reported_excluded_count_exact": manifest.get("excluded_game_ids") == len(excluded),
        "checkpoint_hash_exact": manifest.get("checkpoint_sha256") == digest(CHECKPOINT),
        "d32_panel_hash_exact": manifest.get("d32_panel_sha256") == digest(args.panel),
    }

    confirmation = []
    raw_hashes_exact = True
    turn_one_hashes_exact = True
    manifest_repeat_exact = False
    if development_pass and all(
        value == 0 if key in {"zero_seeds", "excluded_overlap"} else bool(value)
        for key, value in manifest_checks.items()
    ):
        with tempfile.TemporaryDirectory(prefix="d33-manifest-") as directory:
            repeat_path = Path(directory) / "manifest.json"
            completed = subprocess.run(
                [sys.executable, MANIFEST_BUILDER, "--output", repeat_path],
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
            )
            manifest_repeat_exact = (
                completed.returncode == 0
                and repeat_path.exists()
                and repeat_path.read_bytes() == args.manifest.read_bytes()
            )
        if manifest_repeat_exact:
            for record in manifest["games"]:
                raw_path = REPO / record["path"]
                raw_hash_exact = digest(raw_path) == record["raw_sha256"]
                raw_hashes_exact &= raw_hash_exact
                game = json.loads(raw_path.read_text())
                raw_identity_exact = (
                    int(game.get("gameId")) == int(record["game_id"])
                    and game.get("refereeInput") == f"seed={int(record['seed'])}\n"
                )
                expected = render_turn_one(game, 0)
                turn_one_hash_exact = (
                    text_digest(expected) == record["turn_one_sha256"]
                    and len(expected.encode()) == record["turn_one_bytes"]
                )
                turn_one_hashes_exact &= turn_one_hash_exact
                generated = run_generator(args.binary, int(record["seed"]))
                comparison = canonical_comparison(expected, generated)
                invariants = structural_invariants(generated)
                confirmation.append(
                    {
                        "game_id": int(record["game_id"]),
                        "seed": int(record["seed"]),
                        "raw_hash_exact": raw_hash_exact,
                        "raw_identity_exact": raw_identity_exact,
                        "turn_one_hash_exact": turn_one_hash_exact,
                        **comparison,
                        "invariants_pass": invariants["pass"],
                        "complete_pass": raw_hash_exact
                        and raw_identity_exact
                        and turn_one_hash_exact
                        and comparison["pass"]
                        and invariants["pass"],
                    }
                )

    manifest_pass = (
        all(
            value == 0 if key in {"zero_seeds", "excluded_overlap"} else bool(value)
            for key, value in manifest_checks.items()
        )
        and manifest_repeat_exact
        and raw_hashes_exact
        and turn_one_hashes_exact
    )
    confirmation_pass = len(confirmation) == 120 and all(
        row["complete_pass"] for row in confirmation
    )
    gates = {
        "manifest_integrity": manifest_pass,
        "development_3_of_3": development_pass,
        "implementation_frozen_before_confirmation": bool(implementation),
        "confirmation_120_of_120": confirmation_pass,
        "all_invariants": all(row["invariants"]["pass"] for row in development)
        and len(confirmation) == 120
        and all(row["invariants_pass"] for row in confirmation),
    }
    decision = (
        "accept_generate_official_as_new_experiment_substrate"
        if all(gates.values())
        else "reject_d33_official_mapgen_parity"
    )
    failure_counts = Counter()
    for row in confirmation:
        for key in (
            "raw_hash_exact",
            "raw_identity_exact",
            "turn_one_hash_exact",
            "prefix_exact",
            "plant_multiset_exact",
            "unit_suffix_exact",
            "generated_live_order",
            "trailing_newline_exact",
            "invariants_pass",
        ):
            if not row[key]:
                failure_counts[key] += 1
    payload = {
        "schema": 1,
        "decision": decision,
        "gates": gates,
        "manifest": {
            "path": str(args.manifest.relative_to(REPO)),
            "sha256": digest(args.manifest),
            "checks": manifest_checks,
            "deterministic_repeat_exact": manifest_repeat_exact,
            "raw_hashes_exact": raw_hashes_exact,
            "turn_one_hashes_exact": turn_one_hashes_exact,
        },
        "implementation": implementation,
        "development": development,
        "confirmation": {
            "games": len(confirmation),
            "passes": sum(row["complete_pass"] for row in confirmation),
            "failure_counts": dict(sorted(failure_counts.items())),
            "rows": confirmation,
        },
    }
    atomic_write(args.output, json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print(
        f"decision={decision} development={sum(row['complete_pass'] for row in development)}/3 "
        f"confirmation={sum(row['complete_pass'] for row in confirmation)}/120 output={args.output}"
    )
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
