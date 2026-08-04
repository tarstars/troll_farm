#!/usr/bin/env python3
"""Replay-conditioned audit of SecureOrchardBot activation and orchard species.

The input is the eight exact one-hour orchard/no-orchard Arena replay packages from
20260803-orchard-ab-night-cycle.  The script:

* verifies full command parity for the deployed source in every game;
* compares the current APPLE orchard, idle-only APPLE orchard, BANANA orchard,
  and idle-only BANANA orchard on the same official states up to first divergence;
* reconstructs the exact activation state and current inner (no-orchard) starter command;
* measures actual APPLE-mother planting, harvesting, banking, survival, and terminal outcomes;
* audits exact repeated initial-state matches between orchard and no-orchard legs;
* prices APPLE versus BANANA mother growth under the actual water-adjacent geometry.

All counterfactual command comparisons are teacher-forced.  Only the first divergence from
no-orchard is treated as exact; post-divergence commands are never interpreted as terminal
counterfactual value.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.replay_conformance import action_commands, effective_chop_unit_ids
from cgauto.replay_state import decode_replay

TASK_ID = "20260804-orchard-activation-species-audit"
PACKAGE_ROOT = ROOT / "data/shared-lfs/orchard-ab-night-20260803"
ANALYSIS_ROOT = ROOT / "data/analysis/live-agent-6553250/orchard-ab-night-20260803"
CURRENT_SOURCE = ROOT / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
NO_ORCHARD_SOURCE = ROOT / "claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs"
OUTPUT_JSON = ROOT / "chatgpt_1/orchard-activation-species-audit-2026-08-04.json"
OUTPUT_CSV = ROOT / "chatgpt_1/orchard-activation-opportunities-2026-08-04.csv"
OUTPUT_MD = ROOT / "chatgpt_1/orchard-activation-species-audit-2026-08-04.md"

APPLE = 2
BANANA = 3
WOOD = 5
TOTAL_TURNS = 300
NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))

CURRENT_CONSTRUCTOR = (
    "pub fn new()->Self{Self::with_policy("
    "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),8,false,11,1,)}"
)
IDLE_CONSTRUCTOR = CURRENT_CONSTRUCTOR.replace(",8,false,11,1,", ",8,true,11,1,")
ORCHARD_BLOCK_START = "#[derive(Clone,Copy,Debug,Eq,PartialEq)]enum OrchardPhase"
ORCHARD_BLOCK_END = "use crate::game::GameState;pub trait Bot"

CSV_FIELDS = (
    "variant_leg",
    "leg",
    "game_id",
    "deployed_variant",
    "deployed_first_mismatch_turn",
    "seat",
    "opponent_agent_id",
    "opponent_submission_id",
    "margin",
    "win",
    "catastrophe",
    "initial_fingerprint",
    "static_fingerprint",
    "current_apple_activation_turn",
    "apple_idle_activation_turn",
    "banana_activation_turn",
    "banana_idle_activation_turn",
    "starter_base_verb",
    "starter_base_command",
    "starter_cell",
    "mother_cell",
    "starter_to_mother_turns",
    "enemy_eta",
    "apple_enemy_kill_eta",
    "banana_enemy_kill_eta",
    "apple_kill_safe",
    "banana_kill_safe",
    "apple_first_bank_eta",
    "banana_first_bank_eta",
    "apple_payback_safe",
    "banana_payback_safe",
    "apple_projected_banked_fruit",
    "banana_projected_banked_fruit",
    "bank_apple",
    "bank_banana",
    "actual_mother_planted",
    "actual_first_plant_turn",
    "actual_first_harvest_turn",
    "actual_first_bank_turn",
    "actual_banked_fruit",
    "actual_harvested_fruit",
    "actual_mother_survived",
)


def load_parser() -> Any:
    path = ROOT / "data/scripts/parse.py"
    spec = importlib.util.spec_from_file_location("troll_farm_parse", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parser from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mean(values: Iterable[float | int]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def median(values: Iterable[float | int]) -> float | None:
    values = list(values)
    return float(statistics.median(values)) if values else None


def percentile(values: Iterable[float | int], q: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    position = (len(rows) - 1) * q
    lo = math.floor(position)
    hi = math.ceil(position)
    if lo == hi:
        return rows[lo]
    fraction = position - lo
    return rows[lo] * (1 - fraction) + rows[hi] * fraction


def summarize_outcomes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    margins = [int(row["margin"]) for row in rows]
    return {
        "games": len(rows),
        "wins": sum(value > 0 for value in margins),
        "ties": sum(value == 0 for value in margins),
        "losses": sum(value < 0 for value in margins),
        "win_rate": sum(value > 0 for value in margins) / len(rows) if rows else None,
        "mean_margin": mean(margins),
        "median_margin": median(margins),
        "catastrophes": sum(value <= -100 for value in margins),
        "catastrophe_rate": sum(value <= -100 for value in margins) / len(rows) if rows else None,
        "negative_margin_mass": sum(-value for value in margins if value < 0),
    }


def paired_bootstrap(deltas: list[float], repetitions: int = 100_000) -> dict[str, Any] | None:
    if not deltas:
        return None
    # Deterministic tiny LCG avoids importing numpy and keeps the result reproducible.
    state = 0x6A09E667
    n = len(deltas)
    draws: list[float] = []
    for _ in range(repetitions):
        total = 0.0
        for _ in range(n):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            total += deltas[state % n]
        draws.append(total / n)
    draws.sort()
    return {
        "pairs": n,
        "repetitions": repetitions,
        "mean": mean(deltas),
        "median": median(deltas),
        "lower_95": draws[int(0.025 * repetitions)],
        "upper_95": draws[min(repetitions - 1, int(0.975 * repetitions))],
        "probability_le_zero": sum(value <= 0 for value in draws) / repetitions,
    }


def build_sources(work: Path) -> dict[str, Path]:
    current = CURRENT_SOURCE.read_text(encoding="utf-8")
    if current.count(CURRENT_CONSTRUCTOR) != 1:
        raise RuntimeError("current orchard constructor anchor is not unique")
    if current.count(ORCHARD_BLOCK_START) != 1 or current.count(ORCHARD_BLOCK_END) != 1:
        raise RuntimeError("secure orchard block anchors are not unique")

    idle = current.replace(CURRENT_CONSTRUCTOR, IDLE_CONSTRUCTOR, 1)
    start = current.index(ORCHARD_BLOCK_START)
    end = current.index(ORCHARD_BLOCK_END, start)
    block = current[start:end]
    banana_block = block.replace("PlantKind::Apple", "PlantKind::Banana")
    banana_block = banana_block.replace("[APPLE]", "[BANANA]")
    banana_block = banana_block.replace('"APPLE"', '"BANANA"')
    if banana_block == block:
        raise RuntimeError("banana orchard transform changed no text")
    banana = current[:start] + banana_block + current[end:]
    if banana.count(CURRENT_CONSTRUCTOR) != 1:
        raise RuntimeError("banana transform damaged constructor anchor")
    banana_idle = banana.replace(CURRENT_CONSTRUCTOR, IDLE_CONSTRUCTOR, 1)

    sources = {
        "no_orchard": NO_ORCHARD_SOURCE,
        "apple_current": CURRENT_SOURCE,
        "apple_idle": work / "apple-idle.rs",
        "banana_current": work / "banana-current.rs",
        "banana_idle": work / "banana-idle.rs",
    }
    sources["apple_idle"].write_text(idle, encoding="utf-8")
    sources["banana_current"].write_text(banana, encoding="utf-8")
    sources["banana_idle"].write_text(banana_idle, encoding="utf-8")
    return sources


def compile_sources(sources: dict[str, Path], work: Path) -> dict[str, Path]:
    binaries: dict[str, Path] = {}
    for name, source in sources.items():
        binary = work / name
        result = subprocess.run(
            ["rustc", "--edition=2021", "--crate-name", "orchard_audit", "-O", str(source), "-o", str(binary)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise RuntimeError(f"rustc failed for {name}:\n{result.stderr[-8000:]}")
        binaries[name] = binary
    return binaries


def package_paths() -> list[tuple[int, str, Path, Path]]:
    rows: list[tuple[int, str, Path, Path]] = []
    for leg_dir in sorted(PACKAGE_ROOT.glob("leg-*-*")):
        parts = leg_dir.name.split("-", 2)
        if len(parts) != 3:
            continue
        leg = int(parts[1])
        variant = parts[2]
        manifests = list(leg_dir.glob("manifest.json"))
        packages = list(leg_dir.glob("games-agent*-submission*.jsonl.gz"))
        if len(manifests) != 1 or len(packages) != 1:
            raise RuntimeError(f"leg {leg_dir} lacks one manifest/package")
        if packages[0].read_bytes().startswith(b"version https://git-lfs.github.com/spec"):
            raise RuntimeError(f"Git LFS object was not materialized: {packages[0]}")
        rows.append((leg, variant, manifests[0], packages[0]))
    if [leg for leg, _variant, _manifest, _package in rows] != list(range(1, 9)):
        raise RuntimeError(f"expected legs 1..8, got {[row[0] for row in rows]}")
    return rows


def load_games() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for leg, variant, manifest_path, package_path in package_paths():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if file_digest(package_path) != manifest["package_sha256"]:
            raise RuntimeError(f"package hash mismatch for leg {leg}")
        meta_by_game = {int(row["game_id"]): row for row in manifest["games"]}
        with gzip.open(package_path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                replay = json.loads(line)
                game_id = int(replay["gameId"])
                meta = meta_by_game.get(game_id)
                if meta is None:
                    raise RuntimeError(f"game {game_id} absent from manifest leg {leg}")
                output.append(
                    {
                        "leg": leg,
                        "variant": variant,
                        "manifest": manifest,
                        "meta": meta,
                        "replay": replay,
                    }
                )
        if sum(row["leg"] == leg for row in output) != int(manifest["game_count"]):
            raise RuntimeError(f"leg {leg} package count mismatch")
    if len(output) != 1280:
        raise RuntimeError(f"expected 1280 games, got {len(output)}")
    return output


def bfs(walkable: set[tuple[int, int]], sources: Iterable[tuple[int, int]]) -> dict[tuple[int, int], int]:
    distances: dict[tuple[int, int], int] = {}
    queue: deque[tuple[int, int]] = deque()
    for source in sources:
        if source in walkable and source not in distances:
            distances[source] = 0
            queue.append(source)
    while queue:
        cell = queue.popleft()
        for dx, dy in NEIGHBORS:
            nxt = (cell[0] + dx, cell[1] + dy)
            if nxt in walkable and nxt not in distances:
                distances[nxt] = distances[cell] + 1
                queue.append(nxt)
    return distances


def adjacent(cell: tuple[int, int]) -> list[tuple[int, int]]:
    return [(cell[0] + dx, cell[1] + dy) for dx, dy in NEIGHBORS]


def terrain(map_data: dict[str, Any]) -> dict[str, Any]:
    walkable: set[tuple[int, int]] = set()
    water: set[tuple[int, int]] = set()
    shacks: list[tuple[int, int] | None] = [None, None]
    for y, row in enumerate(map_data["rows"]):
        for x, char in enumerate(row):
            cell = (x, y)
            if char == ".":
                walkable.add(cell)
            elif char == "~":
                water.add(cell)
            elif char in "01":
                shacks[int(char)] = cell
    if shacks[0] is None or shacks[1] is None:
        raise RuntimeError("map lacks shacks")
    return {"walkable": walkable, "water": water, "shacks": shacks}


def orchard_geometry(map_data: dict[str, Any], state0: dict[str, Any], seat: int) -> dict[str, Any] | None:
    board = terrain(map_data)
    own_shack = board["shacks"][seat]
    enemy_shack = board["shacks"][1 - seat]
    doors = sorted(cell for cell in adjacent(own_shack) if cell in board["walkable"])
    initial_natural = [
        (int(plant["x"]), int(plant["y"]))
        for plant in state0["plants"]
        if int(plant["health"]) > 0
    ]
    if len(doors) < 2 or not initial_natural:
        return None
    enemy_doors = [cell for cell in adjacent(enemy_shack) if cell in board["walkable"]]
    home_distance = bfs(board["walkable"], doors)
    enemy_distance = bfs(board["walkable"], enemy_doors)
    returns = [home_distance[cell] for cell in initial_natural if cell in home_distance]
    if len(returns) != len(initial_natural) or statistics.median(returns) < 8:
        return None
    occupied_plants = {(int(plant["x"]), int(plant["y"])) for plant in state0["plants"]}
    mothers = [
        door
        for door in doors
        if door not in occupied_plants
        and any(abs(door[0] - water[0]) + abs(door[1] - water[1]) == 1 for water in board["water"])
        and enemy_distance.get(door, 10_000) >= 11
    ]
    mothers.sort(key=lambda cell: (-enemy_distance.get(cell, 10_000), cell))
    if not mothers:
        return None
    mother = mothers[0]
    return {
        "mother": mother,
        "doors": doors,
        "alternate_doors": [door for door in doors if door != mother],
        "enemy_door_distance": enemy_distance.get(mother, 10_000),
        "natural_return_median": float(statistics.median(returns)),
    }


def oriented_rows(map_data: dict[str, Any], seat: int) -> list[str]:
    rows: list[str] = []
    for row in map_data["rows"]:
        if seat == 0:
            rows.append(row)
        else:
            rows.append(row.translate(str.maketrans({"0": "1", "1": "0"})))
    return rows


def serialize_game(map_data: dict[str, Any], states: list[dict[str, Any]], turns: int, seat: int) -> str:
    rows = oriented_rows(map_data, seat)
    lines = [f"{map_data['width']} {map_data['height']}", *rows]
    for state in states[:turns]:
        for player in (seat, 1 - seat):
            lines.append(" ".join(str(int(value)) for value in state["inventories"][player]))
        lines.append(str(len(state["plants"])))
        for plant in state["plants"]:
            lines.append(
                f"{plant['type']} {plant['x']} {plant['y']} {plant['size']} "
                f"{plant['health']} {plant['fruits']} {plant['cooldown']}"
            )
        lines.append(str(len(state["units"])))
        for unit in state["units"]:
            relative_player = 0 if int(unit["player"]) == seat else 1
            carry = " ".join(str(int(value)) for value in unit["carry"])
            lines.append(
                f"{unit['id']} {relative_player} {unit['x']} {unit['y']} {unit['ms']} "
                f"{unit['cc']} {unit['hp']} {unit['chop']} {carry}"
            )
    return "\n".join(lines) + "\n"


def run_bot(binary: Path, stdin_text: str, expected_turns: int) -> list[list[str]]:
    result = subprocess.run(
        [str(binary)],
        input=stdin_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    if result.returncode != 0 or result.stderr:
        raise RuntimeError(
            f"bot {binary.name} failed exit={result.returncode} stderr={result.stderr[-2000:]}"
        )
    lines = result.stdout.splitlines()
    if len(lines) != expected_turns:
        raise RuntimeError(f"bot {binary.name} emitted {len(lines)} lines for {expected_turns} turns")
    return [action_commands(line) for line in lines]


def assigned(commands: list[str], units: list[dict[str, Any]], seat: int) -> dict[int, str]:
    unit_ids = sorted(int(unit["id"]) for unit in units if int(unit["player"]) == seat)
    result: dict[int, str] = {}
    slot = 0
    for command in commands:
        fields = command.split()
        if not fields:
            continue
        verb = fields[0].upper()
        if verb in ("TRAIN", "MSG"):
            continue
        positional = unit_ids[slot] if slot < len(unit_ids) else None
        slot += 1
        if verb == "WAIT":
            unit_id = positional
        else:
            try:
                unit_id = int(fields[1])
            except (IndexError, ValueError):
                unit_id = positional
        if unit_id is not None and unit_id not in result:
            result[unit_id] = command
    return result


def first_divergence(a: list[list[str]], b: list[list[str]]) -> int | None:
    for index, (left, right) in enumerate(zip(a, b)):
        if left != right:
            return index
    return None


def effective_cooldown(species: str) -> int:
    return {"APPLE": 2, "BANANA": 4}[species]


def first_bank_eta(species: str, starter_to_mother_turns: int) -> int:
    # Activation turn includes either MOVE-to-mother or PICK-at-mother.  PLANT is one turn
    # after arrival/PICK. A newly planted tree ticks immediately to stage 1; four further
    # cooldown events produce its first fruit. HARVEST and DROP then consume two turns.
    return starter_to_mother_turns + 4 * effective_cooldown(species) + 3


def projected_banked_fruit(species: str, activation_turn: int, eta: int) -> int:
    first_turn = activation_turn + eta
    if first_turn > TOTAL_TURNS:
        return 0
    interval = max(2, effective_cooldown(species))
    return 1 + (TOTAL_TURNS - first_turn) // interval


def enemy_eta(state: dict[str, Any], seat: int, mother: tuple[int, int], walkable: set[tuple[int, int]]) -> int:
    distance = bfs(walkable, [mother])
    values = []
    for unit in state["units"]:
        if int(unit["player"]) != 1 - seat or int(unit["chop"]) <= 0:
            continue
        cell = (int(unit["x"]), int(unit["y"]))
        if cell in distance:
            speed = max(1, int(unit["ms"]))
            values.append((distance[cell] + speed - 1) // speed)
    return min(values, default=10_000)


def earliest_enemy_kill_eta(
    state: dict[str, Any],
    seat: int,
    mother: tuple[int, int],
    walkable: set[tuple[int, int]],
    species: str,
    plant_turn_offset: int,
) -> int | None:
    """Earliest adversarial kill under continuous chopping after arrival.

    MOVE consumes an action, a just-planted tree is not choppable on its plant turn, and
    plant growth happens after CHOP. This is a conservative mechanical safety bound, not
    a prediction that the real opponent will choose to attack.
    """
    base = {"APPLE": 8, "BANANA": 2}[species]
    slope = {"APPLE": 3, "BANANA": 1}[species]
    cooldown_effective = effective_cooldown(species)
    distances = bfs(walkable, [mother])
    arrivals: list[tuple[int, int]] = []
    for unit in state["units"]:
        if int(unit["player"]) != 1 - seat or int(unit["chop"]) <= 0:
            continue
        cell = (int(unit["x"]), int(unit["y"]))
        if cell not in distances:
            continue
        speed = max(1, int(unit["ms"]))
        arrival = (distances[cell] + speed - 1) // speed
        arrivals.append((arrival, int(unit["chop"])))
    if not arrivals:
        return None

    size = 0
    health = base
    cooldown = 0
    for offset in range(plant_turn_offset, TOTAL_TURNS + 1):
        if offset == plant_turn_offset:
            # PLANT resolves before CHOP, but new trees are excluded from that turn's
            # choppable-cell snapshot. The end-of-turn tick immediately creates size 1.
            size = 1
            health = base + slope
            cooldown = cooldown_effective
            continue

        damage = sum(chop for arrival, chop in arrivals if offset >= arrival + 1)
        health -= damage
        if health <= 0:
            return offset

        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0:
            if size < 4:
                size += 1
                health += slope
            cooldown = cooldown_effective
    return None


def state_fingerprint(map_data: dict[str, Any], state0: dict[str, Any], seat: int) -> tuple[str, str]:
    static = digest({"rows": oriented_rows(map_data, seat)})
    initial = digest(
        {
            "rows": oriented_rows(map_data, seat),
            "inventories": [state0["inventories"][seat], state0["inventories"][1 - seat]],
            "units": [
                {
                    **unit,
                    "player": 0 if int(unit["player"]) == seat else 1,
                }
                for unit in state0["units"]
            ],
            "plants": state0["plants"],
        }
    )
    return static, initial


def actual_orchard_lifecycle(
    states: list[dict[str, Any]],
    recorded: list[list[str]],
    seat: int,
    starter_id: int,
    mother: tuple[int, int] | None,
    activation_index: int | None,
) -> dict[str, Any]:
    result = {
        "actual_mother_planted": False,
        "actual_first_plant_turn": None,
        "actual_first_harvest_turn": None,
        "actual_first_bank_turn": None,
        "actual_banked_fruit": 0,
        "actual_harvested_fruit": 0,
        "actual_mother_survived": False,
    }
    if mother is None or activation_index is None:
        return result
    for index in range(activation_index, min(len(recorded), len(states) - 1)):
        before = states[index]
        after = states[index + 1]
        command = assigned(recorded[index], before["units"], seat).get(starter_id, "")
        verb = command.split()[0].upper() if command else ""
        before_unit = next((u for u in before["units"] if int(u["id"]) == starter_id), None)
        after_unit = next((u for u in after["units"] if int(u["id"]) == starter_id), None)
        before_mother = next(
            (p for p in before["plants"] if (int(p["x"]), int(p["y"])) == mother), None
        )
        after_mother = next(
            (p for p in after["plants"] if (int(p["x"]), int(p["y"])) == mother), None
        )
        turn = index + 1
        if (
            verb == "PLANT"
            and len(command.split()) >= 3
            and command.split()[2].upper() == "APPLE"
            and after_mother is not None
            and str(after_mother["type"]).upper() == "APPLE"
        ):
            result["actual_mother_planted"] = True
            result["actual_first_plant_turn"] = result["actual_first_plant_turn"] or turn
        if verb == "HARVEST" and before_unit is not None and after_unit is not None:
            gained = max(0, int(after_unit["carry"][APPLE]) - int(before_unit["carry"][APPLE]))
            if before_mother is not None and str(before_mother["type"]).upper() == "APPLE" and gained:
                result["actual_harvested_fruit"] += gained
                result["actual_first_harvest_turn"] = result["actual_first_harvest_turn"] or turn
        banked = max(
            0,
            int(after["inventories"][seat][APPLE]) - int(before["inventories"][seat][APPLE]),
        )
        if verb == "DROP" and banked:
            result["actual_banked_fruit"] += banked
            result["actual_first_bank_turn"] = result["actual_first_bank_turn"] or turn
    final_mother = next(
        (p for p in states[-1]["plants"] if (int(p["x"]), int(p["y"])) == mother), None
    )
    result["actual_mother_survived"] = bool(
        final_mother is not None
        and str(final_mother["type"]).upper() == "APPLE"
        and int(final_mother["health"]) > 0
    )
    return result


def decode_one(replay: dict[str, Any], parse: Any) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    frames = replay["frames"]
    map_data, _units, inv0, inv1 = parse.parse_frame0(frames[0]["view"])
    trajectory, _final_inventory = parse.extract_turns(frames, inv0, inv1)
    chop_ids = []
    for row in trajectory:
        commands0 = action_commands(row.get("commands0"))
        commands1 = action_commands(row.get("commands1"))
        chop_ids.append(effective_chop_unit_ids(commands0) + effective_chop_unit_ids(commands1))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as stream:
        json.dump(replay, stream)
        temp_path = Path(stream.name)
    try:
        decoded = decode_replay(temp_path, chop_unit_ids_by_turn=chop_ids)
    finally:
        temp_path.unlink(missing_ok=True)
    states = decoded["states"]
    if len(states) - 1 != len(trajectory):
        raise RuntimeError(
            f"game {replay['gameId']} decoded {len(states)-1} states for {len(trajectory)} turns"
        )
    # decode_replay uses width/height/rows keys; parse map uses w/h/rows. Keep the exact decoder map.
    return decoded["map"], states, trajectory


def analyze_game(item: dict[str, Any], binaries: dict[str, Path], parse: Any) -> dict[str, Any]:
    replay = item["replay"]
    meta = item["meta"]
    leg = int(item["leg"])
    deployed_variant = str(item["variant"])
    seat = int(meta["target_index"])
    map_data, states, trajectory = decode_one(replay, parse)
    turns = len(trajectory)
    stdin_text = serialize_game(map_data, states, turns, seat)
    recorded = [action_commands(row.get(f"commands{seat}")) for row in trajectory]

    outputs = {name: run_bot(binary, stdin_text, turns) for name, binary in binaries.items()}
    deployed_name = "apple_current" if deployed_variant == "orchard" else "no_orchard"
    deployed_mismatch_index = first_divergence(outputs[deployed_name], recorded)

    state0 = states[0]
    geometry = orchard_geometry(map_data, state0, seat)
    starter_id = min(int(unit["id"]) for unit in state0["units"] if int(unit["player"]) == seat)
    static_fp, initial_fp = state_fingerprint(map_data, state0, seat)
    scores = [int(value) for value in replay["scores"]]
    margin = scores[seat] - scores[1 - seat]

    baseline = outputs["no_orchard"]
    raw_activation_indices = {
        "current_apple": first_divergence(outputs["apple_current"], baseline),
        "apple_idle": first_divergence(outputs["apple_idle"], baseline),
        "banana": first_divergence(outputs["banana_current"], baseline),
        "banana_idle": first_divergence(outputs["banana_idle"], baseline),
    }
    activation_indices = {}
    for name, index in raw_activation_indices.items():
        exact_prefix = (
            index is not None
            and index < 100
            and (deployed_mismatch_index is None or index < deployed_mismatch_index)
        )
        # Once the deployed APPLE wrapper has diverged, other generated wrappers are no
        # longer on their own exact state trajectory. Measure those on no-orchard legs.
        if deployed_variant == "orchard" and name != "current_apple":
            exact_prefix = False
        activation_indices[name] = index if exact_prefix else None

    activation_index = activation_indices["current_apple"]
    activation_state = states[activation_index] if activation_index is not None else None
    mother = geometry["mother"] if geometry else None
    base_command = None
    base_verb = None
    starter_cell = None
    travel_turns = None
    eta_enemy = None
    apple_eta = None
    banana_eta = None
    apple_kill_eta = None
    banana_kill_eta = None
    apple_kill_safe = None
    banana_kill_safe = None
    apple_safe = None
    banana_safe = None
    apple_projected = None
    banana_projected = None
    bank_apple = None
    bank_banana = None
    if activation_state is not None and mother is not None:
        base_command = assigned(baseline[activation_index], activation_state["units"], seat).get(starter_id)
        base_verb = base_command.split()[0].upper() if base_command else None
        starter = next(unit for unit in activation_state["units"] if int(unit["id"]) == starter_id)
        starter_cell = (int(starter["x"]), int(starter["y"]))
        board = terrain(map_data)
        distance = bfs(board["walkable"], [starter_cell]).get(mother, 10_000)
        speed = max(1, int(starter["ms"]))
        travel_turns = (distance + speed - 1) // speed
        eta_enemy = enemy_eta(activation_state, seat, mother, board["walkable"])
        apple_eta = first_bank_eta("APPLE", travel_turns)
        banana_eta = first_bank_eta("BANANA", travel_turns)
        plant_turn_offset = travel_turns + 1
        apple_kill_eta = earliest_enemy_kill_eta(
            activation_state, seat, mother, board["walkable"], "APPLE", plant_turn_offset
        )
        banana_kill_eta = earliest_enemy_kill_eta(
            activation_state, seat, mother, board["walkable"], "BANANA", plant_turn_offset
        )
        # HARVEST resolves before CHOP. If the mother dies on the first harvest turn,
        # the carried fruit can still be dropped on the following turn.
        apple_kill_safe = apple_kill_eta is None or apple_kill_eta >= apple_eta - 1
        banana_kill_safe = banana_kill_eta is None or banana_kill_eta >= banana_eta - 1
        # Retain the older travel-only discriminator as a deliberately conservative audit.
        apple_safe = eta_enemy > apple_eta
        banana_safe = eta_enemy > banana_eta
        activation_turn = activation_index + 1
        apple_projected = projected_banked_fruit("APPLE", activation_turn, apple_eta)
        banana_projected = projected_banked_fruit("BANANA", activation_turn, banana_eta)
        bank_apple = int(activation_state["inventories"][seat][APPLE])
        bank_banana = int(activation_state["inventories"][seat][BANANA])

    lifecycle = actual_orchard_lifecycle(
        states,
        recorded,
        seat,
        starter_id,
        mother,
        activation_index if deployed_variant == "orchard" else None,
    )

    return {
        "variant_leg": f"leg-{leg:02d}-{deployed_variant}",
        "leg": leg,
        "game_id": int(replay["gameId"]),
        "deployed_variant": deployed_variant,
        "deployed_first_mismatch_turn": (
            None if deployed_mismatch_index is None else deployed_mismatch_index + 1
        ),
        "seat": seat,
        "opponent_agent_id": int(meta["opponent_agent_id"]),
        "opponent_submission_id": int(meta["opponent_submission_id"]),
        "margin": margin,
        "win": margin > 0,
        "catastrophe": margin <= -100,
        "initial_fingerprint": initial_fp,
        "static_fingerprint": static_fp,
        "current_apple_activation_turn": None if activation_index is None else activation_index + 1,
        "apple_idle_activation_turn": (
            None if activation_indices["apple_idle"] is None else activation_indices["apple_idle"] + 1
        ),
        "banana_activation_turn": (
            None if activation_indices["banana"] is None else activation_indices["banana"] + 1
        ),
        "banana_idle_activation_turn": (
            None if activation_indices["banana_idle"] is None else activation_indices["banana_idle"] + 1
        ),
        "starter_base_verb": base_verb,
        "starter_base_command": base_command,
        "starter_cell": starter_cell,
        "mother_cell": mother,
        "starter_to_mother_turns": travel_turns,
        "enemy_eta": eta_enemy,
        "apple_enemy_kill_eta": apple_kill_eta,
        "banana_enemy_kill_eta": banana_kill_eta,
        "apple_kill_safe": apple_kill_safe,
        "banana_kill_safe": banana_kill_safe,
        "apple_first_bank_eta": apple_eta,
        "banana_first_bank_eta": banana_eta,
        "apple_payback_safe": apple_safe,
        "banana_payback_safe": banana_safe,
        "apple_projected_banked_fruit": apple_projected,
        "banana_projected_banked_fruit": banana_projected,
        "bank_apple": bank_apple,
        "bank_banana": bank_banana,
        "geometry_exists": geometry is not None,
        "geometry_enemy_door_distance": geometry["enemy_door_distance"] if geometry else None,
        "geometry_natural_return_median": geometry["natural_return_median"] if geometry else None,
        "turns": turns,
        **lifecycle,
    }


def group_activation(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    active = [row for row in rows if row[field] is not None]
    return {
        "field": field,
        "activations": len(active),
        "activation_rate": len(active) / len(rows) if rows else None,
        "turn_median": median(row[field] for row in active),
        "outcomes": summarize_outcomes(active),
    }


def summarize_actual_apple(rows: list[dict[str, Any]]) -> dict[str, Any]:
    orchard_rows = [row for row in rows if row["deployed_variant"] == "orchard"]
    active = [row for row in orchard_rows if row["current_apple_activation_turn"] is not None]
    idle_kept = [row for row in active if row["starter_base_verb"] == "WAIT"]
    idle_blocked = [row for row in active if row["starter_base_verb"] != "WAIT"]
    payback_kept = [row for row in active if row["apple_payback_safe"]]
    payback_blocked = [row for row in active if not row["apple_payback_safe"]]
    kill_kept = [row for row in active if row["apple_kill_safe"]]
    kill_blocked = [row for row in active if not row["apple_kill_safe"]]
    combined = [row for row in active if row["starter_base_verb"] == "WAIT" and row["apple_kill_safe"]]
    return {
        "orchard_games": len(orchard_rows),
        "activated": len(active),
        "activation_rate": len(active) / len(orchard_rows),
        "base_command_verbs": dict(sorted(Counter(row["starter_base_verb"] for row in active).items())),
        "work_conserving_kept": len(idle_kept),
        "work_conserving_blocked": len(idle_blocked),
        "payback_safe_kept": len(payback_kept),
        "payback_safe_blocked": len(payback_blocked),
        "kill_safe_kept": len(kill_kept),
        "kill_safe_blocked": len(kill_blocked),
        "combined_kept": len(combined),
        "all_active_outcomes": summarize_outcomes(active),
        "work_conserving_kept_outcomes": summarize_outcomes(idle_kept),
        "work_conserving_blocked_outcomes": summarize_outcomes(idle_blocked),
        "payback_safe_kept_outcomes": summarize_outcomes(payback_kept),
        "payback_safe_blocked_outcomes": summarize_outcomes(payback_blocked),
        "kill_safe_kept_outcomes": summarize_outcomes(kill_kept),
        "kill_safe_blocked_outcomes": summarize_outcomes(kill_blocked),
        "combined_kept_outcomes": summarize_outcomes(combined),
        "mother_planted": sum(row["actual_mother_planted"] for row in active),
        "mother_survived": sum(row["actual_mother_survived"] for row in active),
        "games_with_banked_fruit": sum(int(row["actual_banked_fruit"]) > 0 for row in active),
        "total_harvested_fruit": sum(int(row["actual_harvested_fruit"]) for row in active),
        "total_banked_fruit": sum(int(row["actual_banked_fruit"]) for row in active),
        "banked_fruit_median": median(int(row["actual_banked_fruit"]) for row in active),
        "first_bank_delay_median": median(
            int(row["actual_first_bank_turn"]) - int(row["current_apple_activation_turn"])
            for row in active
            if row["actual_first_bank_turn"] is not None
        ),
        "enemy_eta_minus_apple_bank_eta": {
            "median": median(int(row["enemy_eta"]) - int(row["apple_first_bank_eta"]) for row in active),
            "p10": percentile(
                (int(row["enemy_eta"]) - int(row["apple_first_bank_eta"]) for row in active), 0.10
            ),
            "p90": percentile(
                (int(row["enemy_eta"]) - int(row["apple_first_bank_eta"]) for row in active), 0.90
            ),
        },
    }


def exact_pairs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    key_fields = ("initial_fingerprint", "opponent_agent_id", "opponent_submission_id", "seat")
    grouped: dict[tuple[Any, ...], dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {"orchard": [], "no-orchard": []}
    )
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        grouped[key][row["deployed_variant"]].append(row)
    pairs: list[dict[str, Any]] = []
    for key, variants in grouped.items():
        left = sorted(variants["no-orchard"], key=lambda row: row["leg"])
        right = sorted(variants["orchard"], key=lambda row: row["leg"])
        for no_row, orchard_row in zip(left, right):
            pairs.append(
                {
                    "key": key,
                    "no_orchard_game": no_row["game_id"],
                    "orchard_game": orchard_row["game_id"],
                    "no_orchard_leg": no_row["leg"],
                    "orchard_leg": orchard_row["leg"],
                    "activation": orchard_row["current_apple_activation_turn"] is not None,
                    "idle_kept": orchard_row["starter_base_verb"] == "WAIT",
                    "payback_safe": bool(orchard_row["apple_payback_safe"]),
                    "kill_safe": bool(orchard_row["apple_kill_safe"]),
                    "margin_delta": int(orchard_row["margin"]) - int(no_row["margin"]),
                    "win_delta": int(orchard_row["margin"] > 0) - int(no_row["margin"] > 0),
                    "catastrophe_delta": int(orchard_row["margin"] <= -100)
                    - int(no_row["margin"] <= -100),
                }
            )
    def pair_summary(selected: list[dict[str, Any]]) -> dict[str, Any]:
        deltas = [float(row["margin_delta"]) for row in selected]
        return {
            "pairs": len(selected),
            "mean_margin_delta": mean(deltas),
            "median_margin_delta": median(deltas),
            "wins_added": sum(int(row["win_delta"]) for row in selected),
            "catastrophes_added": sum(int(row["catastrophe_delta"]) for row in selected),
            "bootstrap": paired_bootstrap(deltas) if deltas else None,
        }
    return {
        "matching_key": list(key_fields),
        "exact_pairs": len(pairs),
        "all": pair_summary(pairs),
        "activation": pair_summary([row for row in pairs if row["activation"]]),
        "inactive": pair_summary([row for row in pairs if not row["activation"]]),
        "activation_idle_kept": pair_summary(
            [row for row in pairs if row["activation"] and row["idle_kept"]]
        ),
        "activation_idle_blocked": pair_summary(
            [row for row in pairs if row["activation"] and not row["idle_kept"]]
        ),
        "activation_payback_safe": pair_summary(
            [row for row in pairs if row["activation"] and row["payback_safe"]]
        ),
        "activation_payback_unsafe": pair_summary(
            [row for row in pairs if row["activation"] and not row["payback_safe"]]
        ),
        "activation_kill_safe": pair_summary(
            [row for row in pairs if row["activation"] and row["kill_safe"]]
        ),
        "activation_kill_unsafe": pair_summary(
            [row for row in pairs if row["activation"] and not row["kill_safe"]]
        ),
        "rows": pairs,
    }


def species_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    no_rows = [row for row in rows if row["deployed_variant"] == "no-orchard"]
    apple = [row for row in no_rows if row["current_apple_activation_turn"] is not None]
    banana = [row for row in no_rows if row["banana_activation_turn"] is not None]
    apple_ids = {row["game_id"] for row in apple}
    banana_ids = {row["game_id"] for row in banana}
    overlap = apple_ids & banana_ids
    apple_only = apple_ids - banana_ids
    banana_only = banana_ids - apple_ids
    both_rows = [row for row in no_rows if row["game_id"] in overlap]
    return {
        "scope": "640 no-orchard trajectories; exact only through each variant's first divergence",
        "apple": group_activation(no_rows, "current_apple_activation_turn"),
        "apple_idle": group_activation(no_rows, "apple_idle_activation_turn"),
        "banana": group_activation(no_rows, "banana_activation_turn"),
        "banana_idle": group_activation(no_rows, "banana_idle_activation_turn"),
        "support_overlap": {
            "both": len(overlap),
            "apple_only": len(apple_only),
            "banana_only": len(banana_only),
            "neither": len(no_rows) - len(apple_ids | banana_ids),
        },
        "both_species_projected": {
            "games": len(both_rows),
            "mean_apple_banked_fruit_ceiling": mean(
                int(row["apple_projected_banked_fruit"]) for row in both_rows
            ),
            "mean_banana_banked_fruit_ceiling": mean(
                int(row["banana_projected_banked_fruit"]) for row in both_rows
            ),
            "mean_apple_minus_banana_ceiling": mean(
                int(row["apple_projected_banked_fruit"])
                - int(row["banana_projected_banked_fruit"])
                for row in both_rows
            ),
            "apple_seed_also_available": sum(int(row["bank_apple"] or 0) > 0 for row in both_rows),
            "banana_seed_also_available": sum(int(row["bank_banana"] or 0) > 0 for row in both_rows),
        },
        "mechanics": {
            "water_adjacent_effective_cooldown": {"APPLE": 2, "BANANA": 4},
            "mature_health": {"APPLE": 20, "BANANA": 6},
            "first_bank_eta_formula": {
                "APPLE": "starter_travel_turns + 11",
                "BANANA": "starter_travel_turns + 19",
            },
            "steady_state_bank_interval": {"APPLE": 2, "BANANA": 4},
            "interpretation": (
                "The secure mother is harvested and protected, not chopped. APPLE's hard-to-chop "
                "health is defensive value; water reduces APPLE cooldown to 2 versus BANANA 4."
            ),
        },
    }


def render_report(report: dict[str, Any]) -> str:
    ab = report["arena_ab"]
    actual = report["actual_apple"]
    species = report["species"]
    pairs = report["exact_initial_pairs"]
    lines = [
        "# Secure orchard activation and species audit",
        "",
        f"Task: `{TASK_ID}`  ",
        "Data: eight exact one-hour Arena legs, 1,280 games  ",
        "Platform mutation: none",
        "",
        "## Executive verdict",
        "",
        report["verdict"],
        "",
        "The repeated Arena evidence supports keeping a secure orchard, but not activating it",
        "indiscriminately. The exact replay audit separates the activation cases that would survive",
        "an idle-only gate, checks a first-bank safety gate, and compares an otherwise identical",
        "BANANA mother on the same no-orchard states. Teacher-forced counterfactuals are interpreted",
        "only through first divergence.",
        "",
        "## Repeated Arena result",
        "",
        "| Variant | Legs | Games | Mean Arena score | Median score | Wins | Catastrophes | Mean margin |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in ("no-orchard", "orchard"):
        row = ab[variant]
        lines.append(
            f"| {variant} | {row['legs']} | {row['games']} | {row['mean_arena_score']:.3f} | "
            f"{row['median_arena_score']:.3f} | {row['wins']} | {row['catastrophes']} | "
            f"{row['mean_margin']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"Adjacent orchard-minus-no-orchard score deltas: `{ab['paired_score_deltas']}`; "
            f"mean `{ab['paired_score_mean']:+.3f}`.",
            "",
            "## Actual APPLE orchard activation",
            "",
            f"The orchard activated in **{actual['activated']}/{actual['orchard_games']}** orchard-leg games "
            f"({actual['activation_rate']:.2%}). Its underlying no-orchard starter verbs were "
            f"`{actual['base_command_verbs']}`.",
            "",
            "| Gate/stratum | Games | Mean margin | Win rate | Catastrophes | Negative mass |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    strata = [
        ("all activations", actual["all_active_outcomes"]),
        ("idle-only kept", actual["work_conserving_kept_outcomes"]),
        ("idle-only blocked", actual["work_conserving_blocked_outcomes"]),
        ("enemy-arrival-after-bank kept", actual["payback_safe_kept_outcomes"]),
        ("enemy-arrival-after-bank blocked", actual["payback_safe_blocked_outcomes"]),
        ("adversarial-kill-safe kept", actual["kill_safe_kept_outcomes"]),
        ("adversarial-kill-safe blocked", actual["kill_safe_blocked_outcomes"]),
        ("idle + adversarial-kill-safe", actual["combined_kept_outcomes"]),
    ]
    for label, row in strata:
        lines.append(
            f"| {label} | {row['games']} | {row['mean_margin'] if row['mean_margin'] is not None else 'n/a'} | "
            f"{row['win_rate'] if row['win_rate'] is not None else 'n/a'} | {row['catastrophes']} | "
            f"{row['negative_margin_mass']} |"
        )
    lines.extend(
        [
            "",
            f"Successful mothers: {actual['mother_planted']}; games banking orchard fruit: "
            f"{actual['games_with_banked_fruit']}; total banked APPLE: {actual['total_banked_fruit']}; "
            f"median first-bank delay: {actual['first_bank_delay_median']} turns.",
            "",
            "## Exact initial-state pairs",
            "",
            f"The eight queues contain **{pairs['exact_pairs']}** exact matches on initial state, opponent",
            "submission, and seat. These are reported as repeated deterministic comparisons, not as a",
            "perfect randomized experiment because movement tie RNG may differ.",
            "",
            "| Pair stratum | Pairs | Mean orchard-minus-no-orchard margin | Wins added | Catastrophes added |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for key, label in [
        ("all", "all"),
        ("activation", "orchard activates"),
        ("inactive", "orchard inactive"),
        ("activation_idle_kept", "activation: idle-only kept"),
        ("activation_idle_blocked", "activation: idle-only blocked"),
        ("activation_payback_safe", "activation: first-bank safe"),
        ("activation_payback_unsafe", "activation: enemy arrives before bank"),
        ("activation_kill_safe", "activation: survives continuous attack to first harvest"),
        ("activation_kill_unsafe", "activation: cannot survive continuous attack to first harvest"),
    ]:
        row = pairs[key]
        lines.append(
            f"| {label} | {row['pairs']} | {row['mean_margin_delta'] if row['mean_margin_delta'] is not None else 'n/a'} | "
            f"{row['wins_added']} | {row['catastrophes_added']} |"
        )
    overlap = species["support_overlap"]
    both = species["both_species_projected"]
    lines.extend(
        [
            "",
            "## Why APPLE rather than BANANA?",
            "",
            "The mother cell is always water-adjacent and is protected from ordinary chopping. Under that",
            "geometry APPLE has effective cooldown **2**, while BANANA has cooldown **4**. A new APPLE",
            "can first bank fruit after `travel + 11` turns; BANANA needs `travel + 19`. Mature APPLE",
            "health is **20** versus BANANA **6**. For a persistent mother, being difficult to chop is an",
            "advantage, not a defect.",
            "",
            f"On the 640 no-orchard trajectories, activation support was: APPLE "
            f"{species['apple']['activations']}, idle-only APPLE {species['apple_idle']['activations']}, "
            f"BANANA {species['banana']['activations']}, idle-only BANANA "
            f"{species['banana_idle']['activations']}. Overlap: both {overlap['both']}, APPLE-only "
            f"{overlap['apple_only']}, BANANA-only {overlap['banana_only']}.",
            "",
            f"Where both species could activate, the projected uninterrupted bank ceiling averaged "
            f"{both['mean_apple_banked_fruit_ceiling']} APPLE versus "
            f"{both['mean_banana_banked_fruit_ceiling']} BANANA, a mean APPLE advantage of "
            f"{both['mean_apple_minus_banana_ceiling']} fruit.",
            "",
            "A BANANA self-sustained orchard is therefore not a stronger version of this mechanism. It is",
            "a different, lower-yield and more fragile mother. BANANA is attractive for cut/replant wood",
            "production because it is easy to chop; that is precisely the opposite objective from a",
            "protected harvest mother.",
            "",
            "## Recommendation",
            "",
            report["recommendation"],
            "",
            "## Reproducibility",
            "",
            f"- full command-parity games: {report['quality']['deployed_command_parity_games']}/1280;",
            f"- exact deployed command prefix through the activation window: "
            f"{report['quality']['deployed_prefix_exact_through_turn_100_games']}/1280;",
            f"- replay packages: {report['quality']['packages']} with exact SHA verification;",
            f"- row table: `{OUTPUT_CSV.relative_to(ROOT)}`;",
            f"- machine report: `{OUTPUT_JSON.relative_to(ROOT)}`;",
            "- raw replay bodies remain in the existing Git LFS namespace; no duplicate raw data is written.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be in 1..8")
    parse = load_parser()
    games = load_games()
    with tempfile.TemporaryDirectory(prefix="orchard-species-audit-") as directory:
        work = Path(directory)
        sources = build_sources(work)
        binaries = compile_sources(sources, work)
        rows: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {executor.submit(analyze_game, item, binaries, parse): item for item in games}
            for completed, future in enumerate(as_completed(futures), 1):
                item = futures[future]
                try:
                    rows.append(future.result())
                except Exception as error:
                    failures.append(
                        {
                            "game_id": int(item["replay"]["gameId"]),
                            "leg": item["leg"],
                            "error": f"{type(error).__name__}: {error}",
                        }
                    )
                if completed % 40 == 0 or completed == len(futures):
                    print(f"processed {completed}/{len(futures)} failures={len(failures)}", flush=True)
        if failures:
            raise RuntimeError(f"analysis failed closed; first failures: {failures[:10]}")

    rows.sort(key=lambda row: (row["leg"], row["game_id"]))
    if len(rows) != 1280:
        raise RuntimeError(f"expected 1280 rows, got {len(rows)}")

    state = json.loads((ANALYSIS_ROOT / "state.json").read_text(encoding="utf-8"))
    by_variant = {
        variant: [leg for leg in state["legs"] if leg["variant"] == variant]
        for variant in ("no-orchard", "orchard")
    }
    arena_ab: dict[str, Any] = {}
    for variant, legs in by_variant.items():
        arena_ab[variant] = {
            "legs": len(legs),
            "games": sum(int(leg["game_count"]) for leg in legs),
            "mean_arena_score": mean(float(leg["arena"]["score"]) for leg in legs),
            "median_arena_score": median(float(leg["arena"]["score"]) for leg in legs),
            "wins": sum(int(leg["summary"]["wins"]) for leg in legs),
            "ties": sum(int(leg["summary"]["ties"]) for leg in legs),
            "losses": sum(int(leg["summary"]["losses"]) for leg in legs),
            "catastrophes": sum(int(leg["summary"]["catastrophic_losses"]) for leg in legs),
            "negative_margin_mass": sum(float(leg["summary"]["negative_margin_mass"]) for leg in legs),
            "mean_margin": mean(float(leg["summary"]["mean_margin"]) for leg in legs),
        }
    paired_scores = [
        float(state["legs"][index + 1]["arena"]["score"])
        - float(state["legs"][index]["arena"]["score"])
        for index in range(0, 8, 2)
    ]
    arena_ab["paired_score_deltas"] = paired_scores
    arena_ab["paired_score_mean"] = mean(paired_scores)
    arena_ab["paired_score_median"] = median(paired_scores)
    arena_ab["paired_score_bootstrap"] = paired_bootstrap(paired_scores)

    actual = summarize_actual_apple(rows)
    species = species_summary(rows)
    pairs = exact_pairs(rows)

    # Data-driven but bounded disposition; do not fit a new selector on terminal outcomes.
    idle_blocked = actual["work_conserving_blocked_outcomes"]
    idle_kept = actual["work_conserving_kept_outcomes"]
    payback_blocked = actual["payback_safe_blocked_outcomes"]
    payback_kept = actual["payback_safe_kept_outcomes"]
    kill_blocked = actual["kill_safe_blocked_outcomes"]
    kill_kept = actual["kill_safe_kept_outcomes"]
    idle_direction = (
        idle_kept["mean_margin"] is not None
        and idle_blocked["mean_margin"] is not None
        and idle_kept["mean_margin"] > idle_blocked["mean_margin"]
        and idle_kept["catastrophe_rate"] <= idle_blocked["catastrophe_rate"]
    )
    payback_direction = (
        payback_kept["mean_margin"] is not None
        and payback_blocked["mean_margin"] is not None
        and payback_kept["mean_margin"] > payback_blocked["mean_margin"]
        and payback_kept["catastrophe_rate"] <= payback_blocked["catastrophe_rate"]
    )
    kill_direction = (
        kill_kept["mean_margin"] is not None
        and kill_blocked["mean_margin"] is not None
        and kill_kept["mean_margin"] > kill_blocked["mean_margin"]
        and kill_kept["catastrophe_rate"] <= kill_blocked["catastrophe_rate"]
    )
    if idle_direction:
        recommendation = (
            "Promote the already-existing idle-only (`work_conserving`) activation rule to the first "
            "closed-loop candidate. Keep APPLE. Treat dynamic first-bank safety as a second arm only "
            "if it also has favorable direction and adequate support; do not combine thresholds before "
            "a fresh controlled panel."
        )
    else:
        recommendation = (
            "Do not change activation from replay association alone. Keep current APPLE orchard and "
            "run a fresh closed-loop three-arm panel (current, idle-only, idle-only plus first-bank "
            "safety). The existing replays do not show a clean enough direction for an immediate gate "
            "change."
        )
    verdict = (
        "APPLE remains the correct species for the current protected, water-adjacent harvest mother. "
        f"Idle-only activation has {'favorable' if idle_direction else 'non-decisive'} replay direction; "
        f"travel-only first-bank safety has {'favorable' if payback_direction else 'non-decisive'} direction; "
        f"adversarial kill safety has {'favorable' if kill_direction else 'non-decisive'} direction. "
        "Any terminal-value claim still requires a fresh closed-loop comparison."
    )

    report = {
        "schema": "troll-farm-orchard-activation-species-audit/1",
        "task_id": TASK_ID,
        "data": {
            "games": len(rows),
            "legs": 8,
            "packages": [
                {
                    "leg": leg,
                    "variant": variant,
                    "manifest": str(manifest.relative_to(ROOT)),
                    "package": str(package.relative_to(ROOT)),
                    "package_sha256": file_digest(package),
                }
                for leg, variant, manifest, package in package_paths()
            ],
        },
        "source_identity": {
            "current": {
                "path": str(CURRENT_SOURCE.relative_to(ROOT)),
                "sha256": file_digest(CURRENT_SOURCE),
            },
            "no_orchard": {
                "path": str(NO_ORCHARD_SOURCE.relative_to(ROOT)),
                "sha256": file_digest(NO_ORCHARD_SOURCE),
            },
            "generated_variants": {
                "apple_idle": "current source with require_idle_starter false -> true only",
                "banana_current": "current SecureOrchardBot APPLE references -> BANANA only",
                "banana_idle": "banana_current plus require_idle_starter true",
            },
        },
        "arena_ab": arena_ab,
        "actual_apple": actual,
        "species": species,
        "exact_initial_pairs": pairs,
        "quality": {
            "deployed_command_parity_games": sum(
                row["deployed_first_mismatch_turn"] is None for row in rows
            ),
            "deployed_prefix_exact_through_turn_100_games": sum(
                row["deployed_first_mismatch_turn"] is None
                or int(row["deployed_first_mismatch_turn"]) > 100
                for row in rows
            ),
            "packages": 8,
            "teacher_forced_boundary": (
                "only first divergence from no-orchard is interpreted for generated variants"
            ),
            "raw_replays_republished": False,
        },
        "direction_checks": {
            "idle_only_favorable": idle_direction,
            "first_bank_safety_favorable": payback_direction,
            "adversarial_kill_safety_favorable": kill_direction,
        },
        "verdict": verdict,
        "recommendation": recommendation,
        "rows_sha256": digest(rows),
    }

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            serialized = row.copy()
            for field in ("starter_cell", "mother_cell"):
                if serialized.get(field) is not None:
                    serialized[field] = f"{serialized[field][0]}:{serialized[field][1]}"
            writer.writerow({field: serialized.get(field) for field in CSV_FIELDS})
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_report(report), encoding="utf-8")
    print(json.dumps({"games": len(rows), "activated": actual["activated"], "verdict": verdict}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
