#!/usr/bin/env python3
"""Analyze only the open products of one passed immutable D61p field snapshot."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.recent_resident_field_census import (  # noqa: E402
    crop_provenance,
    decoded_states,
    summarize_crop_records,
    successful_events,
)
from cgauto.rich_opponent_scheduler_transition_study import (  # noqa: E402
    partition_summary,
    snapshots_and_intervals,
    verified_training_events,
    worker_scheduler,
)
from cgauto.top_player_macro_census import summarize_occurrences  # noqa: E402
from cgauto.top_player_opening_analysis import analyze_players  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d61p-open-field-transfer-analysis-protocol-2026-07-21.md"
)
ELIGIBLE_STATUSES = {"fetched", "already_present", "already_present_race"}
TARGET_SPLITS = {"discovery", "validation"}
OPEN_SPLITS = TARGET_SPLITS | {"calibration_only", "top_legend_observation"}
ATTACK_ORDER = ("F1", "F7", "F2", "F4", "F3", "F5", "F6")
REQUIRED_QA_GATES = {
    "all_acquisition_rows_eligible",
    "all_eligible_games_parsed",
    "zero_duplicate_game_ids",
    "zero_duplicate_trajectories",
    "zero_unexpected_scores",
    "all_turns_have_decoded_states",
    "zero_unknown_diff_updates",
    "all_maps_and_plants_symmetric",
    "at_least_80_resident_games",
    "at_least_15_top20_source_agents",
    "at_least_75_top20_games",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def safe_child(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"path escapes root: {relative!r}")
    return path


def verify_product_file(processed: Path, product: dict, relative: str) -> Path:
    metadata = (product.get("files") or {}).get(relative)
    if metadata is None:
        raise ValueError(f"processed manifest omits {relative}")
    path = safe_child(processed, relative)
    if not path.is_file():
        raise ValueError(f"processed product is missing {relative}")
    if path.stat().st_size != int(metadata["bytes"]):
        raise ValueError(f"processed product size differs for {relative}")
    if sha256_file(path) != metadata["sha256"]:
        raise ValueError(f"processed product hash differs for {relative}")
    return path


def verify_snapshot_file(snapshot: Path, manifest: dict, relative: str) -> Path:
    metadata = (manifest.get("files") or {}).get(relative)
    if metadata is None:
        raise ValueError(f"snapshot manifest omits {relative}")
    path = safe_child(snapshot, relative)
    if not path.is_file():
        raise ValueError(f"snapshot product is missing {relative}")
    if path.stat().st_size != int(metadata["bytes"]):
        raise ValueError(f"snapshot product size differs for {relative}")
    if sha256_file(path) != metadata["sha256"]:
        raise ValueError(f"snapshot product hash differs for {relative}")
    return path


def load_open_inputs(snapshot: Path) -> dict:
    """Verify one passed snapshot while never opening sealed-confirmation products."""

    snapshot = Path(snapshot).resolve()
    manifest_path = snapshot / "manifest.json"
    processed = snapshot / "processed"
    product_path = processed / "manifest.json"
    if not manifest_path.is_file() or not product_path.is_file():
        raise ValueError("snapshot lacks immutable raw or processed manifest")
    manifest = json.loads(manifest_path.read_text())
    product = json.loads(product_path.read_text())
    if manifest.get("schema") != "troll-farm-d61p-snapshot-v1":
        raise ValueError("unknown D61p snapshot schema")
    if not manifest.get("complete") or not manifest.get("all_wanted_games_classified"):
        raise ValueError("D61p snapshot is incomplete")
    if product.get("schema") != "troll-farm-d61p-processed-v1":
        raise ValueError("unknown D61p processed schema")
    if product.get("source_snapshot_id") != manifest.get("snapshot_id"):
        raise ValueError("raw and processed snapshot IDs differ")
    if product.get("source_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("processed product references another source manifest")

    # These are the only raw snapshot products whose content this analysis consumes.
    leaderboard_path = verify_snapshot_file(snapshot, manifest, "leaderboard.json")
    players_path = verify_snapshot_file(snapshot, manifest, "players.json")
    acquisitions_path = verify_snapshot_file(snapshot, manifest, "games.json")
    qa_path = verify_product_file(processed, product, "qa.json")
    split_path = verify_product_file(processed, product, "split_manifest.json")
    open_games_path = verify_product_file(processed, product, "open/games.jsonl")

    qa = json.loads(qa_path.read_text())
    if qa.get("schema") != "troll-farm-d61p-qa-v1":
        raise ValueError("unknown D61p QA schema")
    if qa.get("confirmation_content_exposed") is not False:
        raise ValueError("D61p QA does not attest confirmation sealing")
    qa_gates = qa.get("gates") or {}
    if set(qa_gates) != REQUIRED_QA_GATES:
        raise ValueError("D61p QA gate set differs from the frozen protocol")
    if not qa.get("pass") or not all(qa_gates.values()):
        raise ValueError("D61p QA or a frozen integrity/volume gate did not pass")

    split_manifest = json.loads(split_path.read_text())
    if split_manifest.get("schema") != "troll-farm-d61p-splits-v1":
        raise ValueError("unknown D61p split schema")
    resident_agent_id = int(manifest["config"]["resident_agent_id"])
    if int(split_manifest.get("resident_agent_id", -1)) != resident_agent_id:
        raise ValueError("resident agent differs between source and split manifests")
    split_by_game = {
        int(row["game_id"]): row["label"] for row in split_manifest.get("rows") or []
    }
    if len(split_by_game) != len(split_manifest.get("rows") or []):
        raise ValueError("duplicate game ID in split manifest")

    open_games = read_jsonl(open_games_path)
    open_ids = [int(game["gameId"]) for game in open_games]
    if len(open_ids) != len(set(open_ids)):
        raise ValueError("duplicate game ID in open product")
    expected_open = {
        game_id for game_id, label in split_by_game.items() if label != "confirmation"
    }
    if set(open_ids) != expected_open:
        raise ValueError("open game IDs do not exactly match nonconfirmation split IDs")
    for game in open_games:
        game_id = int(game["gameId"])
        if game.get("split") not in OPEN_SPLITS:
            raise ValueError(f"sealed or unknown split in open product for {game_id}")
        if game["split"] != split_by_game[game_id]:
            raise ValueError(f"split disagreement for open game {game_id}")

    acquisitions = json.loads(acquisitions_path.read_text())
    acquisition_by_game = {int(row["game_id"]): row for row in acquisitions}
    if len(acquisition_by_game) != len(acquisitions):
        raise ValueError("duplicate game ID in acquisition product")
    players = json.loads(players_path.read_text())
    top20_ids = {
        int(player["agent_id"])
        for player in players
        if "legend_top20" in (player.get("groups") or [])
        and int(player["agent_id"]) != resident_agent_id
    }
    if not top20_ids:
        raise ValueError("snapshot has no nonresident top-20 source agents")

    raw_root = snapshot.parent.parent.resolve()
    tasks = []
    input_hashes = {
        "snapshot_manifest": sha256_file(manifest_path),
        "processed_manifest": sha256_file(product_path),
        "qa": sha256_file(qa_path),
        "split_manifest": sha256_file(split_path),
        "open_games": sha256_file(open_games_path),
        "protocol": sha256_file(PROTOCOL),
        "analyzer": sha256_file(Path(__file__)),
    }
    for game in sorted(open_games, key=lambda row: int(row["gameId"])):
        game_id = int(game["gameId"])
        acquisition = acquisition_by_game.get(game_id)
        if acquisition is None or acquisition.get("status") not in ELIGIBLE_STATUSES:
            raise ValueError(f"open game {game_id} lacks an eligible acquisition")
        if acquisition.get("response_sha256") != game["acquisition"]["response_sha256"]:
            raise ValueError(f"acquisition hash disagreement for open game {game_id}")
        raw_path = safe_child(raw_root, acquisition["cache_file"])
        if not raw_path.is_file() or sha256_file(raw_path) != acquisition["response_sha256"]:
            raise ValueError(f"raw replay hash differs for open game {game_id}")
        trajectory_relative = f"open/trajectories/{game_id}.jsonl"
        trajectory_path = verify_product_file(processed, product, trajectory_relative)
        source_top_ids = {
            int(source["agent_id"])
            for source in acquisition.get("sources") or []
            if "legend_top20" in (source.get("groups") or [])
        }
        tasks.append(
            {
                "game": game,
                "raw_path": str(raw_path),
                "trajectory_path": str(trajectory_path),
                "resident_agent_id": resident_agent_id,
                "top_source_ids": sorted(source_top_ids & top20_ids),
            }
        )

    return {
        "snapshot": snapshot,
        "snapshot_id": manifest["snapshot_id"],
        "resident_agent_id": resident_agent_id,
        "top20_ids": top20_ids,
        "leaderboard": json.loads(leaderboard_path.read_text()),
        "qa": qa,
        "tasks": tasks,
        "input_hashes": input_hashes,
    }


def score_status(scores: list[int]) -> str:
    return "penalty" if any(int(value) < 0 for value in scores) else "exact"


def player_macro_row(game: dict, player: int, training_events: list[dict]) -> dict:
    player_row = next(row for row in game["players"] if int(row["index"]) == player)
    per_player = game["per_player"][str(player)]
    opponent_score = int(game["scores"][1 - player])
    trains = [[int(event["turn"]), list(event["spec"])] for event in training_events]
    return {
        "game_id": int(game["gameId"]),
        "split": game["split"],
        "agent_id": player_row.get("agentId"),
        "name": player_row.get("name"),
        "leaderboard_rank": player_row.get("localRank"),
        "seat": player,
        "turns": int(game["n_turns"]),
        "score": int(game["scores"][player]),
        "opponent_score": opponent_score,
        "margin": int(game["scores"][player]) - opponent_score,
        "won": int(game["scores"][player]) > opponent_score,
        "successful_trains": trains,
        "successful_train_count": len(trains),
        "final_worker_count": 1 + len(trains),
        "attempted_trains": per_player.get("trains", []),
        "command_counts": per_player.get("commands_summary", {}),
        "planted_ok": per_player.get("planted_ok", {}),
        "collected_wood": per_player.get("effects", {}).get("collected_WOOD", 0),
        "chops_landed": per_player.get("effects", {}).get("chops_landed", 0),
        "final_wood": per_player.get("final_inv", [0] * 6)[5],
    }


def scheduler_row(
    game: dict,
    player: int,
    analysis: dict,
    states: list[dict],
    trajectory: list[dict],
    events: dict[int, list[dict]],
) -> dict:
    has_iron = bool(game["map"]["iron"])
    training_events = verified_training_events(analysis, states, player, has_iron)
    if len(analysis["workers"]) != 1 + len(training_events):
        raise ValueError("spawned worker/TRAIN mismatch")
    scheduler = worker_scheduler(states, trajectory, player, analysis["workers"])
    final_inventory = tuple(
        list(game["per_player"][str(index)]["final_inv"]) for index in (0, 1)
    )
    snapshots, intervals = snapshots_and_intervals(
        trajectory, final_inventory, events[player], player
    )
    final = snapshots[str(len(trajectory))]
    expected_score = sum(final_inventory[player][:4]) + 4 * final_inventory[player][5]
    if final["score"] != expected_score:
        raise ValueError("scheduler snapshot/final inventory mismatch")
    transitions = Counter(scheduler["transitions"])
    workers = scheduler["workers"]
    later_events = [event for event in training_events if event["ordinal"] >= 2]
    third_worker_turn = next(
        (event["turn"] for event in training_events if event["ordinal"] == 2), 301
    )
    t100 = snapshots.get("100") or final
    opponent_row = next(
        row for row in game["players"] if int(row["index"]) == 1 - player
    )
    return {
        "game_id": int(game["gameId"]),
        "split": game["split"],
        "opponent": opponent_row.get("name"),
        "opponent_agent_id": opponent_row.get("agentId"),
        "turns": len(trajectory),
        "has_iron": has_iron,
        "training_events": training_events,
        "final_worker_count": len(workers),
        "third_worker_turn_or_301": third_worker_turn,
        "trained_workers": max(0, len(workers) - 1),
        "hybrid_trained_workers": sum(
            worker["ordinal"] > 0 and worker["spec"][2] > 0 and worker["spec"][3] > 0
            for worker in workers
        ),
        "active_50_workers": sum(worker["active_turns"] >= 50 for worker in workers),
        "multi_role_active_50_workers": sum(
            worker["active_turns"] >= 50 and worker["multi_role"] for worker in workers
        ),
        "later_training_events": len(later_events),
        "coordinated_later_training_events": sum(
            event["useful_funding_contributor_count"] >= 2 for event in later_events
        ),
        "has_harvest_to_plant": transitions["HARVEST->PLANT"] > 0,
        "has_chop_to_drop": transitions["CHOP->DROP"] > 0,
        "late_plant_share": (
            (final["successful_plants"] - t100["successful_plants"])
            / final["successful_plants"]
            if final["successful_plants"]
            else 0.0
        ),
        "late_wood_share": (
            (final["wood"] - t100["wood"]) / final["wood"] if final["wood"] else 0.0
        ),
        "scheduler": scheduler,
        "snapshots": snapshots,
        "intervals": intervals,
    }


def resident_row(
    game: dict,
    raw: dict,
    trajectory: list[dict],
    states: list[dict],
    player: int,
    scheduler: dict,
) -> dict:
    opponent = 1 - player
    records, quality = crop_provenance(raw, trajectory, player)
    per_player = game["per_player"][str(player)]
    opponent_features = game["per_player"][str(opponent)]
    opponent_row = next(
        row for row in game["players"] if int(row["index"]) == opponent
    )
    own_plants = sum(int(value) for value in per_player.get("planted_ok", {}).values())
    scores = [int(value) for value in game["scores"]]
    return {
        "game_id": int(game["gameId"]),
        "split": game["split"],
        "seat": player,
        "opponent": opponent_row.get("name"),
        "opponent_agent_id": opponent_row.get("agentId"),
        "turns": int(game["n_turns"]),
        "score_status": score_status(scores),
        "scores": {"resident": scores[player], "opponent": scores[opponent]},
        "margin": scores[player] - scores[opponent],
        "won": scores[player] > scores[opponent],
        "starting_inventory": list(states[0]["inventories"][player]),
        "own_crops_created": own_plants,
        "own_planted_by_type": per_player.get("planted_ok", {}),
        "final": {
            "resident_inventory": per_player.get("final_inv"),
            "opponent_inventory": opponent_features.get("final_inv"),
            "resident_wood": per_player.get("final_inv", [0] * 6)[5],
            "opponent_wood": opponent_features.get("final_inv", [0] * 6)[5],
            "resident_workers": scheduler["final_worker_count"],
        },
        "opponent_crop_summary": summarize_crop_records(records),
        "opponent_crop_records": records,
        "crop_attribution_quality": quality,
    }


def analyze_open_game(task: dict) -> dict:
    game = task["game"]
    game_id = int(game["gameId"])
    raw = json.loads(Path(task["raw_path"]).read_text())
    if int(raw.get("gameId", -1)) != game_id:
        raise ValueError(f"raw replay ID mismatch for {game_id}")
    trajectory = read_jsonl(Path(task["trajectory_path"]))
    if len(trajectory) != int(game["n_turns"]):
        raise ValueError(f"trajectory length mismatch for {game_id}")
    _map, states, unknown = decoded_states(raw, trajectory)
    if unknown or len(states) != len(trajectory) + 1:
        raise ValueError(f"official-state decode mismatch for {game_id}")
    expected_final = [
        list(game["per_player"][str(player)]["final_inv"]) for player in (0, 1)
    ]
    if states[-1]["inventories"] != expected_final:
        raise ValueError(f"official-state final inventory mismatch for {game_id}")
    analyses = analyze_players(states, trajectory)
    events = successful_events(raw["frames"])
    players = []
    resident = None
    for player in (0, 1):
        player_row = next(
            row for row in game["players"] if int(row["index"]) == player
        )
        agent_id = player_row.get("agentId")
        is_resident = agent_id == task["resident_agent_id"]
        is_selected_top_source = agent_id in set(task["top_source_ids"])
        if not is_resident and not is_selected_top_source:
            continue
        schedule = scheduler_row(
            game, player, analyses[player], states, trajectory, events
        )
        training_events = schedule["training_events"]
        macro = player_macro_row(game, player, training_events)
        players.append(
            {
                "agent_id": agent_id,
                "is_resident": is_resident,
                "is_selected_top_source": is_selected_top_source,
                "macro": macro,
                "scheduler": schedule,
            }
        )
        if is_resident:
            resident = resident_row(
                game, raw, trajectory, states, player, schedule
            )
    return {
        "game_id": game_id,
        "split": game["split"],
        "players": players,
        "resident": resident,
        "integrity": {
            "trajectory_turns": len(trajectory),
            "decoded_turns": len(states) - 1,
            "unknown_diff_updates": unknown,
            "final_inventory_exact": True,
        },
    }


def mean(values) -> float | None:
    values = list(values)
    return statistics.mean(values) if values else None


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    return numerator / denominator if denominator else None


def empty_macro_summary() -> dict:
    return {"appearances": 0, "distinct_agents": 0}


def cohort_summary(macro_rows: list[dict], scheduler_rows: list[dict]) -> dict:
    if not macro_rows:
        return {
            "appearances": 0,
            "macro": empty_macro_summary(),
            "scheduler": {"games": 0},
        }
    return {
        "appearances": len(macro_rows),
        "macro": summarize_occurrences(macro_rows),
        "scheduler": partition_summary(scheduler_rows),
    }


def resident_outcome_summary(rows: list[dict]) -> dict:
    exact = [row for row in rows if row["score_status"] == "exact"]
    penalties = [row for row in rows if row["score_status"] == "penalty"]
    losses = [row for row in exact if row["margin"] < 0]
    catastrophic = [row for row in exact if row["margin"] <= -100]
    comparison = [row for row in exact if row["margin"] > -100]
    negative_mass = sum(-row["margin"] for row in losses)
    catastrophic_mass = sum(-row["margin"] for row in catastrophic)
    opponent_wood_gap = (
        (mean(row["final"]["opponent_wood"] for row in catastrophic) or 0.0)
        - (mean(row["final"]["opponent_wood"] for row in comparison) or 0.0)
        if catastrophic and comparison
        else None
    )
    crop_wood_gap = (
        (
            mean(
                row["opponent_crop_summary"]["opponent_wood_collected"]
                for row in catastrophic
            )
            or 0.0
        )
        - (
            mean(
                row["opponent_crop_summary"]["opponent_wood_collected"]
                for row in comparison
            )
            or 0.0
        )
        if catastrophic and comparison
        else None
    )
    zero_crop = [row for row in rows if row["own_crops_created"] == 0]
    return {
        "games": len(rows),
        "exact_score_games": len(exact),
        "penalty_games": len(penalties),
        "penalty_game_ids": [row["game_id"] for row in penalties],
        "wins": sum(row["margin"] > 0 for row in exact),
        "ties": sum(row["margin"] == 0 for row in exact),
        "losses": len(losses),
        "mean_margin": mean(row["margin"] for row in exact),
        "catastrophic": {
            "definition": "exact-score final margin <= -100",
            "games": len(catastrophic),
            "game_ids": [row["game_id"] for row in catastrophic],
            "frequency": ratio(len(catastrophic), len(exact)),
            "negative_margin_mass_share": ratio(catastrophic_mass, negative_mass),
            "distinct_opponents": len(
                {row["opponent_agent_id"] for row in catastrophic}
            ),
            "opponent_final_wood_gap": opponent_wood_gap,
            "opponent_crop_wood_gap": crop_wood_gap,
            "crop_share_of_opponent_wood_gap": (
                crop_wood_gap / opponent_wood_gap
                if crop_wood_gap is not None
                and opponent_wood_gap is not None
                and opponent_wood_gap > 0
                else None
            ),
        },
        "zero_crop_tail": {
            "interpretation": (
                "descriptive only; field replays do not label counterfactual crop feasibility"
            ),
            "games": len(zero_crop),
            "rate": ratio(len(zero_crop), len(rows)),
            "rows": [
                {
                    "game_id": row["game_id"],
                    "split": row["split"],
                    "margin": row["margin"],
                    "score_status": row["score_status"],
                    "opponent": row["opponent"],
                    "starting_inventory": row["starting_inventory"],
                    "final_workers": row["final"]["resident_workers"],
                    "opponent_crops": row["opponent_crop_summary"]["crops"],
                }
                for row in zero_crop
            ],
        },
        "mean_own_crops_created": mean(row["own_crops_created"] for row in rows),
        "mean_final_workers": mean(row["final"]["resident_workers"] for row in rows),
    }


def support_status(enough: bool, supported: bool) -> str:
    if not enough:
        return "insufficient"
    return "supported" if supported else "unsupported"


def training_delay_summary(rows: list[dict]) -> dict:
    grouped: dict[int, list[int]] = {}
    unavailable: Counter[int] = Counter()
    for row in rows:
        for event in row["training_events"]:
            ordinal = int(event["ordinal"])
            delay = event.get("delay_after_affordable")
            if delay is None:
                unavailable[ordinal] += 1
            else:
                grouped.setdefault(ordinal, []).append(int(delay))
    ordinals = sorted(set(grouped) | set(unavailable))
    return {
        str(ordinal): {
            "events": len(grouped.get(ordinal, [])) + unavailable[ordinal],
            "affordability_observed": len(grouped.get(ordinal, [])),
            "affordability_unobserved": unavailable[ordinal],
            "median_delay_after_affordable": (
                statistics.median(grouped[ordinal]) if grouped.get(ordinal) else None
            ),
            "immediate_train_rate": ratio(
                sum(delay == 0 for delay in grouped.get(ordinal, [])),
                len(grouped.get(ordinal, [])),
            ),
        }
        for ordinal in ordinals
    }


def attack_angle_matrix(
    resident_target: list[dict],
    resident_by_split: dict[str, list[dict]],
    resident_scheduler: list[dict],
    top_macro: list[dict],
    top_scheduler: list[dict],
) -> list[dict]:
    target_outcomes = resident_outcome_summary(resident_target)
    discovery_outcomes = resident_outcome_summary(resident_by_split["discovery"])
    validation_outcomes = resident_outcome_summary(resident_by_split["validation"])
    tail = target_outcomes["catastrophic"]
    f1_enough = target_outcomes["exact_score_games"] >= 20
    f1_supported = bool(
        (tail["frequency"] or 0) >= 0.10
        and (tail["negative_margin_mass_share"] or 0) >= 0.50
        and tail["distinct_opponents"] >= 3
    )

    top_agents = len({row["agent_id"] for row in top_macro})
    top_three_rate = ratio(
        sum(row["final_worker_count"] >= 3 for row in top_macro), len(top_macro)
    )
    resident_three_rate = ratio(
        sum(row["final_worker_count"] >= 3 for row in resident_scheduler),
        len(resident_scheduler),
    )
    workforce_gap = (
        top_three_rate - resident_three_rate
        if top_three_rate is not None and resident_three_rate is not None
        else None
    )
    f2_enough = (
        len(top_macro) >= 30 and top_agents >= 5 and len(resident_scheduler) >= 20
    )

    top_summary = partition_summary(top_scheduler) if top_scheduler else {"games": 0}
    metrics = top_summary.get("mechanism_metrics") or {}
    scale = metrics.get("front_loaded_scale") or {}
    funding = metrics.get("coordinated_later_funding") or {}
    hybrid = metrics.get("hybrid_workers") or {}
    renewable = metrics.get("late_renewable_loop") or {}

    crop_share = tail["crop_share_of_opponent_wood_gap"]
    f7_enough = tail["games"] >= 5 and tail["distinct_opponents"] >= 3
    f7_supported = bool(
        (tail["opponent_final_wood_gap"] or 0) >= 20
        and crop_share is not None
        and crop_share >= 0.50
    )

    later_events = int(funding.get("later_training_events") or 0)
    trained_workers = int(hybrid.get("trained_workers") or 0)
    active_workers = int(hybrid.get("active_50_workers") or 0)
    rows = [
        {
            "id": "F1",
            "attack_angle": "catastrophic-tail control",
            "status": support_status(f1_enough, f1_supported),
            "evidence": tail,
            "partition_check": {
                "discovery": discovery_outcomes["catastrophic"],
                "validation": validation_outcomes["catastrophic"],
            },
        },
        {
            "id": "F2",
            "attack_angle": "workforce capitalization",
            "status": support_status(f2_enough, (workforce_gap or 0) >= 0.20),
            "evidence": {
                "top_appearances": len(top_macro),
                "top_agents": top_agents,
                "resident_target_appearances": len(resident_scheduler),
                "top_final_workers_ge3_rate": top_three_rate,
                "resident_final_workers_ge3_rate": resident_three_rate,
                "rate_gap": workforce_gap,
            },
        },
        {
            "id": "F3",
            "attack_angle": "front-loaded scale",
            "status": support_status(
                len(top_scheduler) >= 30,
                (scale.get("median_third_worker_turn_or_301") or 301) <= 100
                and (scale.get("four_plus_rate") or 0) >= 0.60,
            ),
            "evidence": scale,
        },
        {
            "id": "F4",
            "attack_angle": "coordinated later funding",
            "status": support_status(
                later_events >= 10, (funding.get("rate") or 0) >= 0.50
            ),
            "evidence": funding,
        },
        {
            "id": "F5",
            "attack_angle": "hybrid and multi-role labor",
            "status": support_status(
                trained_workers >= 20 and active_workers >= 20,
                (hybrid.get("hybrid_rate") or 0) >= 0.50
                and (hybrid.get("multi_role_rate") or 0) >= 0.40,
            ),
            "evidence": hybrid,
        },
        {
            "id": "F6",
            "attack_angle": "late renewable loop",
            "status": support_status(
                len(top_scheduler) >= 30,
                (renewable.get("late_plant_share") or 0) >= 0.45
                and (renewable.get("late_wood_share") or 0) >= 0.45
                and (renewable.get("harvest_to_plant_rate") or 0) >= 0.60
                and (renewable.get("chop_to_drop_rate") or 0) >= 0.60,
            ),
            "evidence": renewable,
        },
        {
            "id": "F7",
            "attack_angle": "opponent-crop compounding",
            "status": support_status(f7_enough, f7_supported),
            "evidence": {
                "catastrophic_games": tail["games"],
                "distinct_opponents": tail["distinct_opponents"],
                "opponent_final_wood_gap": tail["opponent_final_wood_gap"],
                "opponent_crop_wood_gap": tail["opponent_crop_wood_gap"],
                "crop_share_of_opponent_wood_gap": crop_share,
            },
        },
        {
            "id": "F8",
            "attack_angle": "resident zero-crop tail",
            "status": "descriptive",
            "evidence": target_outcomes["zero_crop_tail"],
        },
        {
            "id": "F9",
            "attack_angle": "TRAIN timing delay",
            "status": "descriptive",
            "evidence": {
                "resident_delay_by_ordinal": training_delay_summary(
                    resident_scheduler
                ),
                "top_delay_by_ordinal": training_delay_summary(top_scheduler),
            },
        },
        {
            "id": "F10",
            "attack_angle": "worker utilization",
            "status": "descriptive",
            "evidence": {
                "resident_phase_actions": (
                    partition_summary(resident_scheduler).get(
                        "mean_issued_actions_by_phase", {}
                    )
                    if resident_scheduler
                    else {}
                ),
                "top_phase_actions": top_summary.get("mean_issued_actions_by_phase", {}),
                "resident_transitions": (
                    partition_summary(resident_scheduler).get(
                        "mean_transition_counts", {}
                    )
                    if resident_scheduler
                    else {}
                ),
                "top_transitions": top_summary.get("mean_transition_counts", {}),
            },
        },
    ]
    return rows


def build_report(loaded: dict, results: list[dict]) -> dict:
    results = sorted(results, key=lambda row: row["game_id"])
    resident_rows = [row["resident"] for row in results if row["resident"] is not None]
    resident_by_split = {
        split: [row for row in resident_rows if row["split"] == split]
        for split in ("discovery", "validation", "calibration_only")
    }
    resident_target = [
        row for row in resident_rows if row["split"] in TARGET_SPLITS
    ]
    resident_macro = []
    resident_scheduler = []
    resident_macro_by_split = {split: [] for split in resident_by_split}
    resident_scheduler_by_split = {split: [] for split in resident_by_split}
    top_macro = []
    top_scheduler = []
    for result in results:
        for player in result["players"]:
            if player["is_resident"] and result["split"] in TARGET_SPLITS:
                resident_macro.append(player["macro"])
                resident_scheduler.append(player["scheduler"])
            if player["is_resident"] and result["split"] in resident_macro_by_split:
                resident_macro_by_split[result["split"]].append(player["macro"])
                resident_scheduler_by_split[result["split"]].append(
                    player["scheduler"]
                )
            if player["is_selected_top_source"] and not player["is_resident"]:
                top_macro.append(player["macro"])
                top_scheduler.append(player["scheduler"])

    matrix = attack_angle_matrix(
        resident_target,
        resident_by_split,
        resident_scheduler,
        top_macro,
        top_scheduler,
    )
    by_id = {row["id"]: row for row in matrix}
    supported = [
        angle for angle in ATTACK_ORDER if by_id[angle]["status"] == "supported"
    ]
    next_angle = supported[0] if supported else None
    by_agent: dict[int, list[dict]] = {}
    for row in top_macro:
        by_agent.setdefault(int(row["agent_id"]), []).append(row)
    return {
        "schema": "troll-farm-d61p-open-field-analysis-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": loaded["snapshot_id"],
        "resident_agent_id": loaded["resident_agent_id"],
        "scope": (
            "offline analysis of integrity-passed open D61p products; confirmation content "
            "remained unopened"
        ),
        "input_hashes": loaded["input_hashes"],
        "integrity": {
            "qa_pass": loaded["qa"]["pass"],
            "frozen_qa_gates": loaded["qa"]["gates"],
            "open_games": len(results),
            "resident_open_games": len(resident_rows),
            "resident_target_games": len(resident_target),
            "top_source_appearances": len(top_macro),
            "top_source_agents": len(by_agent),
            "all_turn_streams_exact": all(
                row["integrity"]["trajectory_turns"]
                == row["integrity"]["decoded_turns"]
                for row in results
            ),
            "unknown_diff_updates": sum(
                row["integrity"]["unknown_diff_updates"] for row in results
            ),
            "all_final_inventories_exact": all(
                row["integrity"]["final_inventory_exact"] for row in results
            ),
            "confirmation_products_read": False,
        },
        "resident_outcomes": {
            "discovery": resident_outcome_summary(resident_by_split["discovery"]),
            "validation": resident_outcome_summary(resident_by_split["validation"]),
            "target_union": resident_outcome_summary(resident_target),
            "calibration_only": resident_outcome_summary(
                resident_by_split["calibration_only"]
            ),
        },
        "cohorts": {
            "resident_target": cohort_summary(resident_macro, resident_scheduler),
            "resident_discovery": cohort_summary(
                resident_macro_by_split["discovery"],
                resident_scheduler_by_split["discovery"],
            ),
            "resident_validation": cohort_summary(
                resident_macro_by_split["validation"],
                resident_scheduler_by_split["validation"],
            ),
            "resident_calibration_only": cohort_summary(
                resident_macro_by_split["calibration_only"],
                resident_scheduler_by_split["calibration_only"],
            ),
            "selected_top20_nonresident": cohort_summary(top_macro, top_scheduler),
            "selected_top20_by_agent": {
                str(agent_id): summarize_occurrences(rows)
                for agent_id, rows in sorted(by_agent.items())
            },
        },
        "attack_angle_matrix": matrix,
        "decision": {
            "supported_directions_in_fixed_priority_order": supported,
            "next_eligible_offline_direction": next_angle,
            "construct_candidate": False,
            "open_confirmation": False,
            "arena_or_submission": False,
            "reason": (
                "field evidence can select the next offline mechanism protocol only; candidate "
                "and platform actions require later frozen gates and explicit authorization"
            ),
        },
        "resident_rows": resident_rows,
        "resident_scheduler_rows": resident_scheduler,
        "top_scheduler_rows": top_scheduler,
    }


def atomic_write_new(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            json.dump(value, target, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def analyze_snapshot(snapshot: Path, output: Path, jobs: int) -> dict:
    if jobs < 1 or jobs > 32:
        raise ValueError("jobs must be between 1 and 32")
    loaded = load_open_inputs(snapshot)
    if jobs == 1:
        results = [analyze_open_game(task) for task in loaded["tasks"]]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(analyze_open_game, loaded["tasks"], chunksize=2))
    report = build_report(loaded, results)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze_snapshot(args.snapshot, args.output, args.jobs)
    print(
        json.dumps(
            {
                "snapshot_id": report["snapshot_id"],
                "open_games": report["integrity"]["open_games"],
                "resident_target_games": report["integrity"]["resident_target_games"],
                "top_source_appearances": report["integrity"]["top_source_appearances"],
                "supported": report["decision"][
                    "supported_directions_in_fixed_priority_order"
                ],
                "next": report["decision"]["next_eligible_offline_direction"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
