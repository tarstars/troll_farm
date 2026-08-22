#!/usr/bin/env python3
"""X1 source-backed referee/local mechanics conformance audit.

The primary source is the public Troll Farm referee repository pinned by
``REFEREE_COMMIT``.  This tool does not mutate simulator semantics.  It verifies the
source identity, extracts the mechanics facts that matter to Architecture-2, runs
executable edge checks against the maintained Python simulator, and records the two
known boundaries that the A2 parity harness must close.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bot.main import ITEM_INDEX, training_cost
from sim.engine import (
    apply_chop,
    apply_harvest,
    has_stalled,
    recompute_scores,
    step,
    tick_plants,
)
from sim.state import SimPlant, SimUnit, from_ascii


REFEREE_COMMIT = "290129129db7a7539d98739ebdb0ed63ee6ceb50"
RUST_ENGINE_SHA256 = "7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05"
RUST_ENGINE_LOCK = (
    "data/analysis/live-agent-6553250/"
    "d169a-resident-option-interface-envelope-lock.json"
)
REFEREE_FILES = {
    "src/main/java/com/codingame/game/Referee.java": "3f78f4acffaffcdcb6b72fdf4cd89a8c5cf07fbc5427e66a66fbbe9e395fa7b1",
    "src/main/java/com/codingame/game/Player.java": "dd5b920004bf56682f7ff4fd901509d85368e24ff11168e32131098fb865b8d9",
    "src/main/java/engine/Board.java": "0bf37fef892168d0eb6b43de91095201d0a717ad20f87b3df6f1d956839b7905",
    "src/main/java/engine/Constants.java": "98fb505d0f2a1b662e882e1b2102ea241a13fe071ca954f325d00e34b27ff004",
    "src/main/java/engine/Unit.java": "5588b256473941d561ea775d6c4f9d6dfbc3a236a33fdc32fce3aaab9bc0c884",
    "src/main/java/engine/Plant.java": "8bea6a508014f246483c01ae6afa86353d1184d10e40486090f77e83861729a2",
    "src/main/java/engine/task/MoveTask.java": "7d4448f5833a1f758e716110669764d792a918f8e1994f7d05d73ba66f6e4745",
    "src/main/java/engine/task/HarvestTask.java": "c0da62e072305abd8ad4b16fbcee0f53b6f3bb2149255b5d0edda81bdb472eb6",
    "src/main/java/engine/task/PlantTask.java": "a635a9f755520907e1fa6df812be000136723da9cb1fe0e6b2918bbac7bf60a0",
    "src/main/java/engine/task/ChopTask.java": "5e3fed658a3aff9714f2176fc37cd3e494ec6e8c451354eeb95c3c084149aaab",
    "src/main/java/engine/task/PickTask.java": "f9b67a9e57ecfefa3d29f6b8a5228e134300e8a00644eb48e19dfd53cf4718fe",
    "src/main/java/engine/task/TrainTask.java": "bd88f4dec739b0b8f0bd808174166eac77951e242ec3bc551cb8eee9256b884d",
    "src/main/java/engine/task/DropTask.java": "3d53882482a912c7231b5171685ec85f86a115fae4e3328c0856721744a77166",
    "src/main/java/engine/task/MineTask.java": "427d9bd966a11aad54cb3e288468e843b3415fefddc481e9d413c3679b7d7f3e",
    "src/main/java/engine/task/Task.java": "98da98706598e3a5424c6303f4fe25841acb5b60646742dc0eb85aae333d5b9f",
    "src/main/java/engine/task/TaskManager.java": "a9086ad4de367dc473c4af4abb309f4a6806a830b54633f8a4a6fc413d8c71f6",
}

JAVA_ANCHORS = {
    "legend_turn_limit": (
        "src/main/java/engine/Constants.java",
        "public static final int GAME_TURNS = 300;",
    ),
    "starting_resource_bounds": (
        "src/main/java/engine/Constants.java",
        "public static final int MIN_STARTING_RESOURCE = 2;",
    ),
    "starting_inventory_draw": (
        "src/main/java/engine/Board.java",
        "inventory[i] = Constants.MIN_STARTING_RESOURCE + random.nextInt",
    ),
    "symmetric_starting_inventory": (
        "src/main/java/engine/Board.java",
        "player.setInventory(inventory);",
    ),
    "initial_score_includes_fruit": (
        "src/main/java/com/codingame/game/Player.java",
        "inventory.getItemCount(Item.PLUM) +",
    ),
    "training_cost_is_roster_plus_square": (
        "src/main/java/engine/Unit.java",
        "result[i] = baseCost + talents[i] * talents[i];",
    ),
    "move_before_harvest": (
        "src/main/java/engine/task/MoveTask.java",
        "return 1;",
    ),
    "train_after_pick_before_drop": (
        "src/main/java/engine/task/TrainTask.java",
        "return 6;",
    ),
    "movement_tie_is_random": (
        "src/main/java/engine/Board.java",
        "return closest.get(random.nextInt(closest.size()));",
    ),
    "ownership_validation": (
        "src/main/java/engine/task/Task.java",
        "if (unit.getPlayer() == player)",
    ),
    "plant_growth_preserves_damage": (
        "src/main/java/engine/Plant.java",
        "if (updateHealth) health += Constants.PLANT_DELTA_HEALTH",
    ),
    "stall_rule_present": (
        "src/main/java/engine/Board.java",
        "public boolean hasStalled()",
    ),
}

RUST_ENGINE_ANCHORS = {
    "score_fruit_plus_4x_wood": (
        "game.scores[p] = inv[0] + inv[1] + inv[2] + inv[3] "
        "+ WOOD_POINTS * inv[WOOD];"
    ),
    "training_cost_roster_plus_stat_squared": "cost[PLUM] = n + ms * ms;",
    "same_type_plant_collision_merges": "if types.len() != 1 {",
    "last_fruit_can_duplicate": "if game.plants[pi].fruits > 0 {",
    "last_wood_can_duplicate": "u.carry[WOOD] += 1;",
    "task_priority": (
        "Priority order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE,"
    ),
    "new_plant_ticks_same_turn": "tick_plants(game);",
    "stall_rule": "pub fn has_stalled(game: &GameState, turns_until_end: &mut i32)",
    "known_lexicographic_movement_tie": (
        "Among ties, pick the lexicographically smallest cell"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def check(name: str, condition: bool, expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "name": name,
        "status": "MATCH" if condition else "MISMATCH",
        "expected": expected,
        "observed": observed,
    }


def local_dynamic_checks() -> list[dict[str, Any]]:
    """Exercise A2-critical rules in the maintained Python referee model."""

    checks: list[dict[str, Any]] = []

    observed_cost = training_cost(2, (2, 3, 0, 2))
    checks.append(
        check(
            "training_cost_roster_plus_stat_squared",
            observed_cost == [6, 11, 2, 0, 6, 0],
            [6, 11, 2, 0, 6, 0],
            observed_cost,
        )
    )

    score_game = from_ascii(["0....1"])
    score_game.inventories[0] = [3, 2, 1, 4, 9, 2]
    recompute_scores(score_game)
    checks.append(check("score_fruit_plus_4x_wood", score_game.scores[0] == 18, 18, score_game.scores[0]))

    growth_game = from_ascii(["0....1", ".~...."])
    growth_game.plants = [SimPlant("BANANA", 1, 0, 4, 6, 0, 1)]
    tick_plants(growth_game)
    growth = growth_game.plants[0]
    checks.append(
        check(
            "water_adjusted_growth_cooldown",
            (growth.fruits, growth.cooldown) == (1, 4),
            [1, 4],
            [growth.fruits, growth.cooldown],
        )
    )

    harvest_game = from_ascii(["0....1"])
    harvest_game.units = [
        SimUnit(0, 0, 2, 0, 1, 1, 1, 0, [0] * 6),
        SimUnit(1, 1, 2, 0, 1, 1, 1, 0, [0] * 6),
    ]
    harvest_game.plants = [SimPlant("PLUM", 2, 0, 4, 12, 1, 5)]
    apply_harvest(harvest_game, [0, 1])
    observed_harvest = [
        harvest_game.units[0].carry[ITEM_INDEX["PLUM"]],
        harvest_game.units[1].carry[ITEM_INDEX["PLUM"]],
        harvest_game.plants[0].fruits,
    ]
    checks.append(check("last_fruit_duplicates", observed_harvest == [1, 1, 0], [1, 1, 0], observed_harvest))

    chop_game = from_ascii(["0....1"])
    chop_game.units = [
        SimUnit(0, 0, 2, 0, 1, 1, 0, 1, [0] * 6),
        SimUnit(1, 1, 2, 0, 1, 1, 0, 1, [0] * 6),
    ]
    chop_game.plants = [SimPlant("BANANA", 2, 0, 1, 1, 0, 5)]
    apply_chop(chop_game, [0, 1])
    observed_wood = [
        chop_game.units[0].carry[ITEM_INDEX["WOOD"]],
        chop_game.units[1].carry[ITEM_INDEX["WOOD"]],
    ]
    checks.append(check("last_wood_duplicates", observed_wood == [1, 1], [1, 1], observed_wood))

    move_train = from_ascii(["0....1", "..+..."])
    move_train.inventories[0] = [2, 2, 2, 0, 1, 0]
    step(move_train, ["MOVE 0 1 0", "TRAIN 1 1 1 0"], ["WAIT"])
    player_zero_units = [unit for unit in move_train.units if unit.player == 0]
    observed_move_train = [len(player_zero_units), sorted(unit.pos for unit in player_zero_units)]
    checks.append(
        check(
            "move_vacates_shack_before_train",
            observed_move_train == [2, [(0, 0), (1, 0)]],
            [2, [(0, 0), (1, 0)]],
            observed_move_train,
        )
    )

    pick_train = from_ascii(["0....1", "..+..."])
    pick_train.units[0].x = 1
    pick_train.inventories[0] = [2, 2, 2, 1, 1, 0]
    step(pick_train, ["PICK 0 PLUM", "TRAIN 1 1 1 0"], ["WAIT"])
    observed_pick_train = [
        sum(unit.player == 0 for unit in pick_train.units),
        pick_train.inventories[0][ITEM_INDEX["PLUM"]],
        pick_train.units[0].carry[ITEM_INDEX["PLUM"]],
    ]
    checks.append(
        check(
            "pick_spends_bank_before_train_recheck",
            observed_pick_train == [1, 1, 1],
            [1, 1, 1],
            observed_pick_train,
        )
    )

    drop_train = from_ascii(["0....1", "..+..."])
    drop_train.units[0].x = 1
    drop_train.units[0].carry[ITEM_INDEX["PLUM"]] = 1
    drop_train.inventories[0] = [1, 2, 2, 0, 1, 0]
    step(drop_train, ["DROP 0", "TRAIN 1 1 1 0"], ["WAIT"])
    observed_drop_train = [
        sum(unit.player == 0 for unit in drop_train.units),
        drop_train.inventories[0][ITEM_INDEX["PLUM"]],
    ]
    checks.append(
        check(
            "train_precedes_drop_so_same_turn_cargo_cannot_fund",
            observed_drop_train == [1, 2],
            [1, 2],
            observed_drop_train,
        )
    )

    plant_game = from_ascii(["0....1"])
    plant_game.units = [SimUnit(0, 0, 2, 0, 1, 1, 1, 1, [0, 0, 0, 1, 0, 0])]
    step(plant_game, ["PLANT 0 BANANA"], ["WAIT"])
    planted = plant_game.plants[0]
    observed_plant = [planted.size, planted.health, planted.fruits, planted.cooldown]
    checks.append(
        check(
            "new_plant_ticks_on_creation_turn",
            observed_plant == [1, 3, 0, 6],
            [1, 3, 0, 6],
            observed_plant,
        )
    )

    stall_game = from_ascii(["0....1"])
    ended, counter = has_stalled(stall_game, 0)
    checks.append(check("zero_grace_no_plants_ends", ended and counter == -1, [True, -1], [ended, counter]))

    return checks


def verify_referee(referee_root: Path) -> dict[str, Any]:
    head = git_head(referee_root)
    files = {}
    for relative, expected in REFEREE_FILES.items():
        path = referee_root / relative
        observed = sha256(path) if path.is_file() else None
        files[relative] = {
            "status": "MATCH" if observed == expected else "MISMATCH",
            "expected_sha256": expected,
            "observed_sha256": observed,
        }
    sources = {
        relative: (referee_root / relative).read_text(encoding="utf-8")
        for relative in REFEREE_FILES
    }
    anchors = {}
    for name, (relative, anchor) in JAVA_ANCHORS.items():
        anchors[name] = {
            "status": "MATCH" if anchor in sources[relative] else "MISMATCH",
            "source": relative,
            "anchor": anchor,
        }
    return {
        "commit": {
            "status": "MATCH" if head == REFEREE_COMMIT else "MISMATCH",
            "expected": REFEREE_COMMIT,
            "observed": head,
        },
        "files": files,
        "anchors": anchors,
        "sources": sources,
    }


def d33_evidence(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    result_path = (
        repo_root
        / "data/analysis/live-agent-6553250/d33-official-mapgen-parity-result-2026-07-20.json"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    frozen_sha = result["implementation"]["official_mapgen_source_sha256"]
    current_sha = sha256(repo_root / "rust/src/game/official_mapgen.rs")
    return {
        "status": "MATCH"
        if result["confirmation"]["passes"] == result["confirmation"]["games"] == 120
        and not result["confirmation"]["failure_counts"]
        and frozen_sha == current_sha
        else "MISMATCH",
        "confirmation_games": result["confirmation"]["games"],
        "confirmation_passes": result["confirmation"]["passes"],
        "failure_counts": result["confirmation"]["failure_counts"],
        "frozen_source_sha256": frozen_sha,
        "current_source_sha256": current_sha,
    }


def rust_engine_evidence(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Verify the maintained Rust engine used by frozen experiment locks."""

    source_path = repo_root / "rust/src/game/engine.rs"
    lock_path = repo_root / RUST_ENGINE_LOCK
    source = source_path.read_text(encoding="utf-8")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    frozen_sha = lock["sha256"]["rust/src/game/engine.rs"]
    current_sha = sha256(source_path)
    anchors = {
        name: {
            "status": "MATCH" if anchor in source else "MISMATCH",
            "anchor": anchor,
        }
        for name, anchor in RUST_ENGINE_ANCHORS.items()
    }
    return {
        "status": "MATCH"
        if frozen_sha == current_sha == RUST_ENGINE_SHA256
        and all(item["status"] == "MATCH" for item in anchors.values())
        else "MISMATCH",
        "lock": RUST_ENGINE_LOCK,
        "expected_sha256": RUST_ENGINE_SHA256,
        "frozen_source_sha256": frozen_sha,
        "current_source_sha256": current_sha,
        "anchors": anchors,
    }


def known_boundaries(
    referee_sources: dict[str, str], repo_root: Path = REPO_ROOT
) -> list[dict[str, Any]]:
    board = referee_sources["src/main/java/engine/Board.java"]
    task = referee_sources["src/main/java/engine/task/Task.java"]
    python_engine = (repo_root / "sim/engine.py").read_text(encoding="utf-8")
    rust_engine = (repo_root / "rust/src/game/engine.rs").read_text(encoding="utf-8")
    movement_detected = (
        "random.nextInt(closest.size())" in board
        and "return min(c for c in in_range" in python_engine
        and "pick the lexicographically smallest cell" in rust_engine
    )
    validation_detected = (
        "if (unit.getPlayer() == player)" in task
        and "def _parse(cmds):" in python_engine
        and "pub fn parse_cmds(cmds: &[String])" in rust_engine
        and "player: i32" not in rust_engine.split("pub fn parse_cmds", 1)[1].split("}", 1)[0]
    )
    return [
        {
            "name": "movement_equal_best_tie_break",
            "status": "MISMATCH" if movement_detected else "UNTESTED",
            "referee": "random among equal best in-range cells",
            "local": "lexicographic minimum",
            "impact": "A2_BLOCKING_UNTIL_PARITY_OR_TIE_AVOIDANCE",
        },
        {
            "name": "command_legality_and_ownership_validation",
            "status": "MISMATCH" if validation_detected else "UNTESTED",
            "referee": "strict ownership, league, skill, syntax, and critical-error checks",
            "local": "simplified parser; legal-controller boundary expected",
            "impact": "A2_REQUIRES_ZERO_INVALID_COMMAND_PROOF_OR_FULL_VALIDATION",
        },
    ]


def build_report(referee_root: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    referee = verify_referee(referee_root)
    dynamic = local_dynamic_checks()
    d33 = d33_evidence(repo_root)
    rust_engine = rust_engine_evidence(repo_root)
    boundaries = known_boundaries(referee["sources"], repo_root)

    source_failures = (
        int(referee["commit"]["status"] != "MATCH")
        + sum(item["status"] != "MATCH" for item in referee["files"].values())
        + sum(item["status"] != "MATCH" for item in referee["anchors"].values())
    )
    dynamic_failures = sum(item["status"] != "MATCH" for item in dynamic)
    known_mismatches = sum(item["status"] == "MISMATCH" for item in boundaries)
    report = {
        "schema": "troll-farm-x1-mechanics-rederivation-v1",
        "referee": {
            key: value for key, value in referee.items() if key != "sources"
        },
        "starting_state": {
            "fruit_draws": {
                "items": ["PLUM", "LEMON", "APPLE", "BANANA"],
                "each_uniform_inclusive": [2, 10],
                "expected_total": 24,
            },
            "iron_draw": {"uniform_inclusive": [2, 10], "expected": 6},
            "same_inventory_for_both_players": True,
            "initial_score_is_starting_fruit_total": True,
        },
        "d33_official_mapgen": d33,
        "rust_engine": rust_engine,
        "dynamic_checks": dynamic,
        "known_boundaries": boundaries,
        "summary": {
            "source_failures": source_failures,
            "dynamic_failures": dynamic_failures,
            "known_mismatches": known_mismatches,
            "unexpected_mismatches": source_failures
            + dynamic_failures
            + int(d33["status"] != "MATCH")
            + int(rust_engine["status"] != "MATCH"),
            "verdict": (
                "SOURCE_OR_LOCAL_CONFORMANCE_FAILURE"
                if source_failures
                + dynamic_failures
                + int(d33["status"] != "MATCH")
                + int(rust_engine["status"] != "MATCH")
                else "CORE_MATCH_WITH_TWO_A2_PARITY_OBLIGATIONS"
            ),
        },
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--referee-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.referee_root.resolve())
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return int(report["summary"]["unexpected_mismatches"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
