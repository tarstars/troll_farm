#!/usr/bin/env python3
"""N2: reconstruct B4.4 and adjudicate every published claim.

This is a read-only audit. It reads exact processed, raw-game, trajectory, leaderboard,
and resident-source paths and writes only compact outputs under ``--output-dir``.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d101a_production_suppression import (  # noqa: E402
    compatible_event,
    reconstruct_generation_actions,
)
from cgauto.analyze_d61p_field_snapshot import read_jsonl  # noqa: E402
from cgauto.analyze_d95a_rank_one_scaler import (  # noqa: E402
    MATERIAL_VERBS,
    reconstruct_actions,
)
from cgauto.peer_cohort_analysis import (  # noqa: E402
    build_cohort,
    counterpart_vs_scale,
    index_agent_occurrences,
    resident_vs_group,
    score_production_stats,
    score_trajectory_shape,
)
from cgauto.recent_resident_field_census import (  # noqa: E402
    decoded_states,
    successful_events,
)
from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    is_clean,
    load_leaderboard,
)
from cgauto.top_player_opening_analysis import analyze_players  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
DEFAULT_PROJECT = Path("/home/tarstars/prj/troll_farm")
DEFAULT_OUTPUT = REPO / "local_codex_1/n2-b4-4-verification"
DEFAULT_GAMES = DEFAULT_PROJECT / "data/processed/games.jsonl"
DEFAULT_RAW = DEFAULT_PROJECT / "data/raw/games"
DEFAULT_TRAJECTORIES = DEFAULT_PROJECT / "data/processed/trajectories"
DEFAULT_HISTORICAL_LEADERBOARD = (
    DEFAULT_PROJECT
    / "data/raw/snapshots/20260728T110709Z-d61p-wide/leaderboard.json"
)
DEFAULT_CURRENT_LEADERBOARD = (
    DEFAULT_PROJECT
    / "data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json"
)
DEFAULT_RESIDENT = REPO / "rust/src/bin/yamo_orchard_live.rs"

DOCUMENTED_CUT = 8131
ANCHOR_CUT = 8395
CURRENT_CUT = 9082
EXPECTED_PREFIX_HASHES = {
    DOCUMENTED_CUT: "c93a273cbeabc7f142432461a6e084a9bb1d5d9c6ac59c6d445f14538e47bde1",
    ANCHOR_CUT: "1f9e3855fad01f5ade6dd1ece17f0e6b20597d0b01889ef5240ee27700b68d40",
    CURRENT_CUT: "12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d",
}
EXPECTED_LEADERBOARD_HASHES = {
    "historical": "5299a96991129fb118cf8a9fd0a491f9e1de8d70f1fb49caa75f2dbb6850e7e2",
    "current": "7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815",
}
EXPECTED_RESIDENT_HASH = (
    "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
)
EXPECTED_ANCHORS = {
    "cohort_agents": 25,
    "strong_agents": 12,
    "peer_weak_agents": 13,
    "tracked_occurrences": 2787,
    "clean_games": 8336,
    "resident_occurrences": 204,
    "resident_rank": 43,
    "strong_rank_min": 7,
    "strong_rank_max": 38,
    "peer_rank_min": 46,
    "peer_rank_max": 104,
}
FRUIT_ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA")
BANDS = ("early_1_50", "middle_51_250", "late_251_plus")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_games_and_prefix_hashes(path: Path, cuts: tuple[int, ...]) -> tuple[list[dict], dict[int, str]]:
    wanted = set(cuts)
    hashers = {cut: hashlib.sha256() for cut in cuts}
    games = []
    with path.open("rb") as handle:
        for record_index, line in enumerate(handle, 1):
            for cut, digest in hashers.items():
                if record_index <= cut:
                    digest.update(line)
            row = json.loads(line)
            row["_n2_record_index"] = record_index
            games.append(row)
    if len(games) < max(wanted):
        raise ValueError(f"{path} has {len(games)} records, need {max(wanted)}")
    return games, {cut: digest.hexdigest() for cut, digest in hashers.items()}


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def value_stats(values: list[float | int]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def birth_band(turn: int) -> str:
    if turn <= 50:
        return "early_1_50"
    if turn <= 250:
        return "middle_51_250"
    return "late_251_plus"


def group_tag(agent_id: int, strong_ids: set[int]) -> str:
    if agent_id == RESIDENT_AGENT_ID:
        return "resident"
    return "strong" if agent_id in strong_ids else "peer_weak"


def make_cut(
    name: str,
    games: list[dict],
    n_records: int,
    leaderboard: dict[int, dict],
) -> dict:
    selected = games[:n_records]
    clean = [game for game in selected if is_clean(game)]
    cohort = build_cohort(clean, leaderboard)
    strong_ids = {row["agent_id"] for row in cohort["strong"]}
    peer_ids = {row["agent_id"] for row in cohort["peer_weak"]}
    tracked_ids = strong_ids | peer_ids | {RESIDENT_AGENT_ID}
    occurrence_index = index_agent_occurrences(clean, tracked_ids)

    def pairs(ids: set[int]) -> list[tuple[dict, int]]:
        result = []
        for agent_id in ids:
            result.extend(occurrence_index[agent_id])
        return result

    strong_pairs = pairs(strong_ids)
    peer_pairs = pairs(peer_ids)
    resident_pairs = occurrence_index[RESIDENT_AGENT_ID]
    top5_ids = {
        agent_id
        for agent_id, info in leaderboard.items()
        if info["division_index"] == 5 and info["rank"] <= 5
    }
    tasks = []
    for agent_id in tracked_ids:
        info = leaderboard[agent_id]
        for game, seat in occurrence_index[agent_id]:
            tasks.append(
                {
                    "record_index": game["_n2_record_index"],
                    "game_id": int(game["gameId"]),
                    "agent_id": agent_id,
                    "seat": seat,
                    "pseudo": info["pseudo"],
                    "rank": info["rank"],
                    "group": group_tag(agent_id, strong_ids),
                }
            )
    tasks.sort(key=lambda row: (row["record_index"], row["agent_id"]))
    strong_ranks = [row["rank"] for row in cohort["strong"]]
    peer_ranks = [row["rank"] for row in cohort["peer_weak"]]
    public = {
        "name": name,
        "n_records": n_records,
        "first_game_id": int(selected[0]["gameId"]),
        "last_game_id": int(selected[-1]["gameId"]),
        "unique_game_ids": len({int(game["gameId"]) for game in selected}),
        "duplicate_game_records": len(selected) - len({int(game["gameId"]) for game in selected}),
        "n_clean": len(clean),
        "cohort": cohort,
        "structural": {
            "cohort_agents": cohort["n_total"],
            "strong_agents": cohort["n_strong"],
            "peer_weak_agents": cohort["n_peer_weak"],
            "tracked_occurrences": len(tasks),
            "clean_games": len(clean),
            "resident_occurrences": len(resident_pairs),
            "resident_rank": cohort["resident"]["rank"],
            "resident_mean_roster": cohort["resident"]["mean_roster"],
            "resident_median_roster": cohort["resident"]["median_roster"],
            "strong_rank_min": min(strong_ranks) if strong_ranks else None,
            "strong_rank_max": max(strong_ranks) if strong_ranks else None,
            "peer_rank_min": min(peer_ranks) if peer_ranks else None,
            "peer_rank_max": max(peer_ranks) if peer_ranks else None,
        },
        "score_production": {
            "resident": score_production_stats(resident_pairs),
            "strong": score_production_stats(strong_pairs),
            "peer_weak": score_production_stats(peer_pairs),
            "per_agent": {
                str(agent_id): {
                    "pseudo": leaderboard[agent_id]["pseudo"],
                    "rank": leaderboard[agent_id]["rank"],
                    "group": group_tag(agent_id, strong_ids),
                    **score_production_stats(occurrence_index[agent_id]),
                }
                for agent_id in sorted(tracked_ids, key=lambda item: leaderboard[item]["rank"])
            },
        },
        "trajectory_shape": {
            "resident": score_trajectory_shape(resident_pairs),
            "strong": score_trajectory_shape(strong_pairs),
            "peer_weak": score_trajectory_shape(peer_pairs),
        },
        "head_to_head": {
            "resident_vs_strong": resident_vs_group(clean, strong_ids),
            "resident_vs_peer_weak": resident_vs_group(clean, peer_ids),
            "resident_vs_scale": counterpart_vs_scale(resident_pairs, top5_ids),
            "strong_vs_scale": counterpart_vs_scale(strong_pairs, top5_ids),
            "peer_weak_vs_scale": counterpart_vs_scale(peer_pairs, top5_ids),
        },
    }
    return {
        "public": public,
        "tasks": tasks,
        "task_keys": {(row["record_index"], row["agent_id"]) for row in tasks},
    }


def anchors_match(structural: dict) -> tuple[bool, dict]:
    checks = {
        key: structural.get(key) == expected
        for key, expected in EXPECTED_ANCHORS.items()
    }
    checks["resident_mean_roster"] = structural.get("resident_mean_roster") == 2
    checks["resident_median_roster"] = structural.get("resident_median_roster") == 2
    return all(checks.values()), checks


def replay_occurrence(task: dict) -> dict:
    raw_path = Path(task["raw_path"])
    trajectory_path = Path(task["trajectory_path"])
    try:
        raw = json.loads(raw_path.read_text())
        trajectory = read_jsonl(trajectory_path)
        _map, states, unknown = decoded_states(raw, trajectory)
        if len(states) - 1 != len(trajectory):
            raise ValueError(
                f"turn mismatch: decoded={len(states) - 1}, trajectory={len(trajectory)}"
            )
        analyses = analyze_players(states, trajectory)
        actor = int(task["seat"])
        opponent = 1 - actor
        actor_ordinals = {
            int(worker["unit_id"]): int(worker["ordinal"])
            for worker in analyses[actor]["workers"]
        }
        opponent_ordinals = {
            int(worker["unit_id"]): int(worker["ordinal"])
            for worker in analyses[opponent]["workers"]
        }
        actor_events, generations, lineage, quality = reconstruct_generation_actions(
            states, trajectory, actor, actor_ordinals
        )
        opponent_events, _opponent_generations, _opponent_lineage, _opponent_quality = (
            reconstruct_generation_actions(states, trajectory, opponent, opponent_ordinals)
        )
        reference_events, reference_lineage, reference_quality = reconstruct_actions(
            states, trajectory, actor, actor_ordinals
        )
        event_reference_compatible = len(actor_events) == len(reference_events) and all(
            compatible_event(event, reference)
            for event, reference in zip(actor_events, reference_events)
        )
        lineage_origins = [
            {
                cell: generations[identifier]["origin"]
                for cell, identifier in generation.items()
            }
            for generation in lineage
        ]
        lineage_reference_compatible = (
            len(lineage_origins) == len(reference_lineage)
            and all(
                set(generation) == set(reference)
                and all(
                    reference[cell] == origin
                    or (reference[cell] == "unknown" and origin in {"actor", "opponent"})
                    for cell, origin in generation.items()
                )
                for generation, reference in zip(lineage_origins, reference_lineage)
            )
        )
        actor_material = [
            event
            for event in actor_events
            if event["success"] and event["verb"] in MATERIAL_VERBS
        ]
        opponent_material = [
            event
            for event in opponent_events
            if event["success"] and event["verb"] in MATERIAL_VERBS
        ]
        plants = [
            event
            for event in actor_material
            if event["verb"] == "PLANT" and event["created_origin"] == "actor"
        ]
        own_ids = {event["created_generation"] for event in plants}
        actor_targets: dict[str, list[dict]] = defaultdict(list)
        opponent_targets: dict[str, list[dict]] = defaultdict(list)
        for event in actor_material:
            if event.get("target_generation"):
                actor_targets[event["target_generation"]].append(event)
        for event in opponent_material:
            if event.get("target_generation"):
                opponent_targets[event["target_generation"]].append(event)
        final_live = set(lineage[-1].values()) if lineage else set()
        outcomes = []
        for generation_id in sorted(own_ids):
            generation = generations[generation_id]
            actor_rows = actor_targets.get(generation_id, [])
            opponent_rows = opponent_targets.get(generation_id, [])
            actor_harvests = [row for row in actor_rows if row["verb"] == "HARVEST"]
            actor_chops = [row for row in actor_rows if row["verb"] == "CHOP"]
            opponent_harvests = [
                row for row in opponent_rows if row["verb"] == "HARVEST"
            ]
            opponent_chops = [row for row in opponent_rows if row["verb"] == "CHOP"]
            birth_turn = int(generation["birth_turn"])
            outcomes.append(
                {
                    "birth_turn": birth_turn,
                    "band": birth_band(birth_turn),
                    "kind": generation["kind"],
                    "actor_harvested": bool(actor_harvests),
                    "actor_harvest_actions": len(actor_harvests),
                    "actor_fruit_gained": sum(
                        sum(row["gained"].get(item, 0) for item in FRUIT_ITEMS)
                        for row in actor_harvests
                    ),
                    "actor_chopped": bool(actor_chops),
                    "actor_chop_actions": len(actor_chops),
                    "actor_wood_gained": sum(
                        row["gained"].get("WOOD", 0) for row in actor_chops
                    ),
                    "opponent_harvested": bool(opponent_harvests),
                    "opponent_chopped": bool(opponent_chops),
                    "survived_to_end": generation_id in final_live,
                }
            )
        summary = successful_events(raw["frames"])[actor]
        summary_first_plant = min(
            (event["turn"] for event in summary if event["kind"] == "PLANT"),
            default=None,
        )
        reconstructed_first_plant = min(
            (event["turn"] for event in plants),
            default=None,
        )
        actor_reaped = sum(row["actor_harvested"] for row in outcomes)
        return {
            "ok": True,
            "record_index": task["record_index"],
            "game_id": task["game_id"],
            "agent_id": task["agent_id"],
            "seat": actor,
            "turns": len(trajectory),
            "summary_first_plant_turn": summary_first_plant,
            "first_plant_turn": reconstructed_first_plant,
            "actor_created": len(outcomes),
            "actor_created_reaped": actor_reaped,
            "has_self_plant_self_chop": any(row["actor_chopped"] for row in outcomes),
            "generation_outcomes": outcomes,
            "integrity": {
                "unknown_diff_updates": unknown,
                "workers": len(analyses[actor]["workers"]),
                "successful_trains": len(analyses[actor]["training_events"]),
                "spawn_train_exact": len(analyses[actor]["workers"])
                == 1 + len(analyses[actor]["training_events"]),
                "unknown_births": quality.get("unknown_births", 0),
                "ambiguous_births": quality.get("ambiguous_births", 0),
                "missing_live_generations": quality.get("missing_live_generations", 0),
                "missing_worker_ordinals": quality.get("missing_worker_ordinals", 0),
                "unassigned_cargo_deltas": quality.get("unassigned_cargo_deltas", 0),
                "reference_unknown_births": reference_quality["unknown_births"],
                "reference_unassigned_cargo_deltas": reference_quality[
                    "unassigned_cargo_deltas"
                ],
                "event_reference_compatible": event_reference_compatible,
                "lineage_reference_compatible": lineage_reference_compatible,
                "summary_first_plant_equal": summary_first_plant
                == reconstructed_first_plant,
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "record_index": task["record_index"],
            "game_id": task["game_id"],
            "agent_id": task["agent_id"],
            "error": f"{type(exc).__name__}: {exc}",
        }


def summarize_replay_rows(rows: list[dict]) -> dict:
    first_turns = [row["first_plant_turn"] for row in rows if row["first_plant_turn"] is not None]
    created = sum(row["actor_created"] for row in rows)
    reaped = sum(row["actor_created_reaped"] for row in rows)
    bands = {}
    for band in BANDS:
        outcomes = [
            outcome
            for row in rows
            for outcome in row["generation_outcomes"]
            if outcome["band"] == band
        ]
        bands[band] = {
            "created": len(outcomes),
            "actor_harvested": sum(row["actor_harvested"] for row in outcomes),
            "actor_chopped": sum(row["actor_chopped"] for row in outcomes),
            "opponent_harvested": sum(row["opponent_harvested"] for row in outcomes),
            "opponent_chopped": sum(row["opponent_chopped"] for row in outcomes),
            "survived_to_end": sum(row["survived_to_end"] for row in outcomes),
            "actor_fruit_gained": sum(row["actor_fruit_gained"] for row in outcomes),
            "actor_wood_gained": sum(row["actor_wood_gained"] for row in outcomes),
        }
    return {
        "games": len(rows),
        "first_plant_turn": {
            "n_reached": len(first_turns),
            "n_total": len(rows),
            "coverage": rate(len(first_turns), len(rows)),
            **value_stats(first_turns),
        },
        "actor_generations": {
            "created": created,
            "created_reaped": reaped,
            "pooled_reaped_coverage": rate(reaped, created),
        },
        "self_plant_self_chop_games": sum(
            row["has_self_plant_self_chop"] for row in rows
        ),
        "self_plant_self_chop_game_rate": rate(
            sum(row["has_self_plant_self_chop"] for row in rows), len(rows)
        ),
        "generation_outcomes_by_birth_band": bands,
    }


def attach_replay_summaries(cut: dict, replay_by_key: dict[tuple[int, int], dict]) -> None:
    task_rows = []
    failures = []
    for task in cut["tasks"]:
        row = replay_by_key[(task["record_index"], task["agent_id"])]
        if row["ok"]:
            task_rows.append({**row, **{key: task[key] for key in ("pseudo", "rank", "group")}})
        else:
            failures.append(row)
    by_group: dict[str, list[dict]] = defaultdict(list)
    by_agent: dict[int, list[dict]] = defaultdict(list)
    for row in task_rows:
        by_group[row["group"]].append(row)
        by_agent[row["agent_id"]].append(row)
    cut["public"]["replay"] = {
        "attempted": len(cut["tasks"]),
        "succeeded": len(task_rows),
        "failed": len(failures),
        "failures": failures,
        "integrity": {
            "zero_unknown_diff_updates": sum(
                row["integrity"]["unknown_diff_updates"] == 0 for row in task_rows
            ),
            "spawn_train_exact": sum(
                row["integrity"]["spawn_train_exact"] for row in task_rows
            ),
            "event_reference_compatible": sum(
                row["integrity"]["event_reference_compatible"] for row in task_rows
            ),
            "lineage_reference_compatible": sum(
                row["integrity"]["lineage_reference_compatible"] for row in task_rows
            ),
            "summary_first_plant_equal": sum(
                row["integrity"]["summary_first_plant_equal"] for row in task_rows
            ),
        },
        "groups": {
            group: summarize_replay_rows(by_group.get(group, []))
            for group in ("resident", "strong", "peer_weak")
        },
        "per_agent": {
            str(agent_id): {
                "pseudo": rows[0]["pseudo"],
                "rank": rows[0]["rank"],
                "group": rows[0]["group"],
                **summarize_replay_rows(rows),
            }
            for agent_id, rows in sorted(
                by_agent.items(), key=lambda item: item[1][0]["rank"]
            )
        },
    }


def build_manifest(
    game_memberships: dict[int, set[str]],
    raw_root: Path,
    trajectory_root: Path,
) -> tuple[list[dict], list[dict]]:
    rows = []
    failures = []
    for game_id in sorted(game_memberships):
        for kind, path in (
            ("raw", raw_root / f"{game_id}.json"),
            ("trajectory", trajectory_root / f"{game_id}.jsonl"),
        ):
            if not path.is_file():
                failures.append(
                    {"game_id": game_id, "kind": kind, "path": str(path), "error": "missing"}
                )
                continue
            rows.append(
                {
                    "game_id": game_id,
                    "kind": kind,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "cuts": ",".join(sorted(game_memberships[game_id])),
                }
            )
    return rows, failures


def code_audit(path: Path) -> dict:
    text = path.read_text()
    checks = {
        "default_factory_disabled": "banana_factory_enabled: false" in text,
        "default_selector_disabled": "banana_factory_selector_enabled: false" in text,
        "selector_is_one_shot": "!self.banana_factory_selector_decided" in text
        and "self.banana_factory_selector_decided = true;" in text,
        "selector_waits_for_two_workers": "&& own_count >= 2" in text,
        "renewable_harvest_seed_path": "BananaFactoryPlantSource::RenewableHarvest" in text,
        "endgame_conversion_rule_present": "view.turn > 250" in text,
        "factory_tests_present": "fn banana_factory_reconciles_successful_and_failed_bootstrap_plants"
        in text,
    }
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "expected_sha256": EXPECTED_RESIDENT_HASH,
        "hash_match": sha256_file(path) == EXPECTED_RESIDENT_HASH,
        "historical_commit_46d36098_expected_sha256": EXPECTED_RESIDENT_HASH,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def close_enough(value: float | None, target: float, tolerance: float) -> bool:
    return value is not None and abs(value - target) <= tolerance


def adjudicate(documented: dict, anchor: dict, current: dict, source: dict, code: dict) -> dict:
    anchor_replay = anchor.get("replay") or {}
    current_replay = current.get("replay") or {}
    anchor_groups = anchor_replay.get("groups") or {}
    current_groups = current_replay.get("groups") or {}
    anchor_agents = anchor_replay.get("per_agent") or {}
    current_agents = current_replay.get("per_agent") or {}
    complete = (
        anchor_replay.get("attempted") == anchor_replay.get("succeeded")
        and current_replay.get("attempted") == current_replay.get("succeeded")
    )

    resident_plant = (
        anchor_groups.get("resident", {}).get("first_plant_turn", {}).get("median")
    )
    peer_plant_rows = [
        row
        for agent_id, row in anchor_agents.items()
        if int(agent_id) != RESIDENT_AGENT_ID
    ]
    every_peer_21_29 = len(peer_plant_rows) == 25 and all(
        row["first_plant_turn"]["median"] is not None
        and 21 <= row["first_plant_turn"]["median"] <= 29
        for row in peer_plant_rows
    )
    c2_exact = close_enough(resident_plant, 191.5, 0.05) and every_peer_21_29

    historical_rates = {
        group: anchor_groups.get(group, {})
        .get("actor_generations", {})
        .get("pooled_reaped_coverage")
        for group in ("resident", "strong", "peer_weak")
    }
    c3_pooled = (
        close_enough(historical_rates["resident"], 0.0093, 0.0005)
        and close_enough(historical_rates["strong"], 0.153, 0.0005)
        and close_enough(historical_rates["peer_weak"], 0.172, 0.0005)
    )
    resident_rate = historical_rates["resident"]
    every_peer_above_resident = (
        resident_rate is not None
        and len(peer_plant_rows) == 25
        and all(
            row["actor_generations"]["pooled_reaped_coverage"] is not None
            and row["actor_generations"]["pooled_reaped_coverage"] > resident_rate
            for row in peer_plant_rows
        )
    )

    score = anchor["score_production"]
    strong_score = score["strong"]["score"]["mean"]
    resident_score = score["resident"]["score"]["mean"]
    c4_headline = close_enough(strong_score, 215.6, 0.05) and close_enough(
        resident_score, 185.7, 0.05
    )

    early = {
        group: anchor_groups.get(group, {})
        .get("generation_outcomes_by_birth_band", {})
        .get("early_1_50", {})
        for group in ("resident", "strong", "peer_weak")
    }
    late = {
        group: anchor_groups.get(group, {})
        .get("generation_outcomes_by_birth_band", {})
        .get("late_251_plus", {})
        for group in ("resident", "strong", "peer_weak")
    }
    purpose_observable = complete and any(
        row.get("actor_harvested", 0) + row.get("actor_chopped", 0) > 0
        for row in [*early.values(), *late.values()]
    )

    return {
        "C1": {
            "verdict": "CORRECTED",
            "reason": (
                "The tracked 8,131-game stats cut yields "
                f"{documented['structural']['cohort_agents']} peers and "
                f"{documented['structural']['tracked_occurrences']} occurrences. "
                "Only the inferred 8,395 prefix matches 25/2,787; the original output "
                "and input manifest are absent."
            ),
        },
        "C2": {
            "verdict": "VERIFIED" if complete and c2_exact else "CORRECTED",
            "reason": (
                f"Anchor reconstruction resident conditional median={resident_plant}; "
                f"all 25 peer conditional medians in 21–29={every_peer_21_29}. "
                "Every median is paired with event coverage; timing alone is not purpose."
            ),
        },
        "C3": {
            "verdict": (
                "VERIFIED"
                if complete and c3_pooled and every_peer_above_resident
                else "CORRECTED"
            ),
            "reason": (
                f"Anchor pooled rates={historical_rates}; published rounded rates "
                f"match={c3_pooled}; every peer exceeds resident={every_peer_above_resident}."
            ),
        },
        "C4": {
            "verdict": "CORRECTED",
            "reason": (
                f"Anchor group score headline match={c4_headline}, but pooled group "
                "composition cannot support a per-agent wood-purity claim and H3's "
                "quartet comparison reverses that interpretation."
            ),
        },
        "C5": {
            "verdict": "CORRECTED" if purpose_observable else "RETIRED_UNIDENTIFIABLE",
            "reason": (
                "Plant birth bands and subsequent self-harvest/self-chop are reported "
                "separately. Early orchard establishment and late fruit-to-wood "
                "conversion are compatible; turn alone is not a causal purpose label."
            ),
        },
        "C6": {
            "verdict": "CORRECTED" if code["hash_match"] and code["all_checks"] else "RETIRED_UNIDENTIFIABLE",
            "reason": (
                "The byte-identified current and commit-46d source grounds disabled "
                "factory machinery, a one-shot two-worker selector, renewable harvesting, "
                "and >250 conversion logic. It does not prove that the factory gate caused "
                "the observed field timing."
            ),
        },
        "C7": {
            "verdict": "CORRECTED",
            "reason": (
                "Later H3 controls dissolve the scale-survival headline, establish a "
                "self-plant→self-chop wood loop for all five audited agents, reverse the "
                "quartet wood-concentration comparison, and make suppression metrics "
                "indistinguishable. Those superseding results remain binding."
            ),
        },
        "support": {
            "replay_complete": complete,
            "source_hashes_all_match": source["all_hashes_match"],
            "current_cohort_agents": current["structural"]["cohort_agents"],
            "current_replay_agents": len(current_agents),
            "current_group_reap_rates": {
                group: current_groups.get(group, {})
                .get("actor_generations", {})
                .get("pooled_reaped_coverage")
                for group in ("resident", "strong", "peer_weak")
            },
        },
    }


def write_manifest(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("game_id", "kind", "path", "bytes", "sha256", "cuts")
        )
        writer.writeheader()
        writer.writerows(rows)


def write_per_agent(path: Path, cuts: list[dict]) -> None:
    fields = (
        "cut",
        "agent_id",
        "pseudo",
        "rank",
        "group",
        "games",
        "first_plant_n",
        "first_plant_coverage",
        "first_plant_median",
        "created",
        "created_reaped",
        "reap_rate",
        "self_chop_game_rate",
        "mean_score",
        "mean_fruit_points",
        "mean_wood_points",
        "mean_wood_share",
    )
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for cut in cuts:
            replay = cut["replay"]["per_agent"]
            score = cut["score_production"]["per_agent"]
            for agent_id, row in sorted(
                replay.items(), key=lambda item: item[1]["rank"]
            ):
                score_row = score[agent_id]
                writer.writerow(
                    {
                        "cut": cut["name"],
                        "agent_id": agent_id,
                        "pseudo": row["pseudo"],
                        "rank": row["rank"],
                        "group": row["group"],
                        "games": row["games"],
                        "first_plant_n": row["first_plant_turn"]["n_reached"],
                        "first_plant_coverage": row["first_plant_turn"]["coverage"],
                        "first_plant_median": row["first_plant_turn"]["median"],
                        "created": row["actor_generations"]["created"],
                        "created_reaped": row["actor_generations"]["created_reaped"],
                        "reap_rate": row["actor_generations"]["pooled_reaped_coverage"],
                        "self_chop_game_rate": row["self_plant_self_chop_game_rate"],
                        "mean_score": score_row["score"]["mean"],
                        "mean_fruit_points": score_row["fruit_points"]["mean"],
                        "mean_wood_points": score_row["wood_points"]["mean"],
                        "mean_wood_share": score_row["wood_share_of_score"]["mean"],
                    }
                )


def render_report(result: dict) -> str:
    anchor = result["cuts"]["anchor_matching"]
    current = result["cuts"]["current"]
    lines = [
        "# N2 — B4.4 verification result",
        "",
        f"- Generated UTC: {result['generated_at']}",
        f"- Overall: **{result['overall_verdict']}**",
        f"- Replay coverage: {result['replay']['succeeded']}/{result['replay']['attempted']}",
        "",
        "## Claim verdicts",
        "",
        "| claim | verdict | reason |",
        "|---|---|---|",
    ]
    for claim_id in (f"C{index}" for index in range(1, 8)):
        row = result["claims"][claim_id]
        lines.append(f"| {claim_id} | **{row['verdict']}** | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Reconstruction",
            "",
            (
                f"The documented 8,131-record cut produces "
                f"{result['cuts']['documented_stats']['structural']['cohort_agents']} peers/"
                f"{result['cuts']['documented_stats']['structural']['tracked_occurrences']} "
                "tracked occurrences. The unique 8,395-record anchor match produces "
                f"{anchor['structural']['cohort_agents']} peers/"
                f"{anchor['structural']['tracked_occurrences']} occurrences. It is an "
                "inferred reconstruction, not the missing original report."
            ),
            "",
            "## Citation-safe consequence",
            "",
            (
                "Do not cite B4.4 as proving that every two-worker peer follows one "
                "plant-reap mechanism, that the resident lacks a loop, or that planting "
                "timings contradict the yamo postmortem. Report conditional first-plant "
                "timing with coverage and per-agent rows; distinguish early orchard "
                "establishment from post-250 fruit-to-wood conversion; retain H3's "
                "controlled corrections for survival, loop type, and wood concentration."
            ),
            "",
            "## Current sensitivity",
            "",
            (
                f"The current cut has {current['structural']['cohort_agents']} cohort agents "
                f"and {current['structural']['tracked_occurrences']} tracked occurrences. "
                "Exact current group values are in `result.json`; `per_agent.csv` preserves "
                "all conditional denominators."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def self_test() -> None:
    assert birth_band(1) == "early_1_50"
    assert birth_band(50) == "early_1_50"
    assert birth_band(51) == "middle_51_250"
    assert birth_band(250) == "middle_51_250"
    assert birth_band(251) == "late_251_plus"
    rows = [
        {
            "first_plant_turn": 20,
            "actor_created": 2,
            "actor_created_reaped": 1,
            "has_self_plant_self_chop": True,
            "generation_outcomes": [
                {
                    "band": "early_1_50",
                    "actor_harvested": True,
                    "actor_chopped": False,
                    "opponent_harvested": False,
                    "opponent_chopped": False,
                    "survived_to_end": True,
                    "actor_fruit_gained": 2,
                    "actor_wood_gained": 0,
                },
                {
                    "band": "late_251_plus",
                    "actor_harvested": False,
                    "actor_chopped": True,
                    "opponent_harvested": False,
                    "opponent_chopped": False,
                    "survived_to_end": False,
                    "actor_fruit_gained": 0,
                    "actor_wood_gained": 3,
                },
            ],
        },
        {
            "first_plant_turn": None,
            "actor_created": 0,
            "actor_created_reaped": 0,
            "has_self_plant_self_chop": False,
            "generation_outcomes": [],
        },
    ]
    summary = summarize_replay_rows(rows)
    assert summary["first_plant_turn"]["coverage"] == 0.5
    assert summary["actor_generations"]["pooled_reaped_coverage"] == 0.5
    assert summary["generation_outcomes_by_birth_band"]["early_1_50"]["actor_harvested"] == 1
    assert summary["generation_outcomes_by_birth_band"]["late_251_plus"]["actor_wood_gained"] == 3
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    parser.add_argument(
        "--historical-leaderboard", type=Path, default=DEFAULT_HISTORICAL_LEADERBOARD
    )
    parser.add_argument(
        "--current-leaderboard", type=Path, default=DEFAULT_CURRENT_LEADERBOARD
    )
    parser.add_argument("--raw-games", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--trajectories", type=Path, default=DEFAULT_TRAJECTORIES)
    parser.add_argument("--resident-source", type=Path, default=DEFAULT_RESIDENT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    started = time.monotonic()
    cuts = (DOCUMENTED_CUT, ANCHOR_CUT, CURRENT_CUT)
    games, prefix_hashes = load_games_and_prefix_hashes(args.games, cuts)
    observed_source_hashes = {
        "games_prefixes": prefix_hashes,
        "historical_leaderboard": sha256_file(args.historical_leaderboard),
        "current_leaderboard": sha256_file(args.current_leaderboard),
    }
    source_checks = {
        f"games_prefix_{cut}": prefix_hashes[cut] == EXPECTED_PREFIX_HASHES[cut]
        for cut in cuts
    }
    source_checks["historical_leaderboard"] = (
        observed_source_hashes["historical_leaderboard"]
        == EXPECTED_LEADERBOARD_HASHES["historical"]
    )
    source_checks["current_leaderboard"] = (
        observed_source_hashes["current_leaderboard"]
        == EXPECTED_LEADERBOARD_HASHES["current"]
    )
    if not all(source_checks.values()):
        raise ValueError(f"source hash mismatch: {source_checks}")

    historical_leaderboard = load_leaderboard(args.historical_leaderboard)
    current_leaderboard = load_leaderboard(args.current_leaderboard)
    documented = make_cut(
        "documented_stats", games, DOCUMENTED_CUT, historical_leaderboard
    )
    anchor = make_cut(
        "anchor_matching", games, ANCHOR_CUT, historical_leaderboard
    )
    current = make_cut("current", games, CURRENT_CUT, current_leaderboard)
    anchor_ok, anchor_checks = anchors_match(anchor["public"]["structural"])
    if not anchor_ok:
        raise ValueError(f"anchor-matching cut no longer matches: {anchor_checks}")

    task_map = {}
    memberships: dict[int, set[str]] = defaultdict(set)
    for cut in (anchor, current):
        for task in cut["tasks"]:
            key = (task["record_index"], task["agent_id"])
            task_map[key] = {
                **task,
                "raw_path": str(args.raw_games / f"{task['game_id']}.json"),
                "trajectory_path": str(
                    args.trajectories / f"{task['game_id']}.jsonl"
                ),
            }
            memberships[task["game_id"]].add(cut["public"]["name"])

    manifest_started = time.monotonic()
    manifest, manifest_failures = build_manifest(
        memberships, args.raw_games, args.trajectories
    )
    if manifest_failures:
        raise ValueError(f"input manifest failures: {manifest_failures[:10]}")
    manifest_seconds = time.monotonic() - manifest_started

    tasks = [task_map[key] for key in sorted(task_map)]
    replay_started = time.monotonic()
    if args.jobs <= 1:
        replay_results = [replay_occurrence(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            replay_results = list(executor.map(replay_occurrence, tasks, chunksize=4))
    replay_seconds = time.monotonic() - replay_started
    replay_by_key = {
        (row["record_index"], row["agent_id"]): row for row in replay_results
    }
    attach_replay_summaries(anchor, replay_by_key)
    attach_replay_summaries(current, replay_by_key)
    replay_failures = [row for row in replay_results if not row["ok"]]

    source = {
        "paths": {
            "games": str(args.games),
            "historical_leaderboard": str(args.historical_leaderboard),
            "current_leaderboard": str(args.current_leaderboard),
            "raw_games": str(args.raw_games),
            "trajectories": str(args.trajectories),
        },
        "expected_prefix_hashes": EXPECTED_PREFIX_HASHES,
        "expected_leaderboard_hashes": EXPECTED_LEADERBOARD_HASHES,
        "observed_hashes": observed_source_hashes,
        "checks": source_checks,
        "all_hashes_match": all(source_checks.values()),
        "manifest_rows": len(manifest),
        "manifest_failures": manifest_failures,
    }
    code = code_audit(args.resident_source)
    claims = adjudicate(
        documented["public"], anchor["public"], current["public"], source, code
    )
    verdicts = [claims[f"C{index}"]["verdict"] for index in range(1, 8)]
    overall = (
        "B4_4_RETIRED"
        if "RETIRED_UNIDENTIFIABLE" in verdicts
        else "B4_4_CORRECTED"
        if "CORRECTED" in verdicts
        else "B4_4_VERIFIED"
    )
    result = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "docs/n2-b4-4-verification-protocol-v2-2026-07-30.md",
        "overall_verdict": overall,
        "source": source,
        "code_audit": code,
        "cuts": {
            "documented_stats": documented["public"],
            "anchor_matching": anchor["public"],
            "current": current["public"],
        },
        "anchor_checks": anchor_checks,
        "claims": claims,
        "replay": {
            "attempted": len(replay_results),
            "succeeded": sum(row["ok"] for row in replay_results),
            "failed": len(replay_failures),
            "failures": replay_failures,
        },
        "timing_seconds": {
            "manifest": manifest_seconds,
            "replay": replay_seconds,
            "total": time.monotonic() - started,
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    manifest_path = args.output_dir / "source_manifest.csv"
    agent_path = args.output_dir / "per_agent.csv"
    report_path = args.output_dir / "report.md"
    result_path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    write_manifest(manifest_path, manifest)
    write_per_agent(agent_path, [anchor["public"], current["public"]])
    report_path.write_text(render_report(result))
    print(
        json.dumps(
            {
                "overall_verdict": overall,
                "output": str(result_path),
                "claims": {
                    claim_id: claims[claim_id]["verdict"]
                    for claim_id in (f"C{index}" for index in range(1, 8))
                },
                "replay": result["replay"],
                "timing_seconds": result["timing_seconds"],
            },
            indent=2,
        )
    )
    return 0 if not replay_failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
