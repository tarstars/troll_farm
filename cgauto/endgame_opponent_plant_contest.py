#!/usr/bin/env python3
"""N5: audit replay-observed value around late opponent-created crop generations.

This is a read-only observational audit. It reconstructs the exact H13 event population:
an opponent successfully creates a crop after turn 250 while the named subject leads in
the pre-turn bank-score margin. It then follows that exact generation, measures both
players' extracted carried resources, and computes the frozen generous factor-two
replay-conditioned observed-yield ceiling.

The result is not a causal estimate of adding an endgame policy. Enemy units may share
cells, extracted cargo is not banked score, and a changed policy would change later play.

Task: coordination/tasks/20260730-n5-endgame-opponent-plant-contest.md
Protocol: docs/n5-endgame-opponent-plant-contest-protocol-2026-07-30.md
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys
from types import SimpleNamespace

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d101a_production_suppression import (  # noqa: E402
    reconstruct_generation_actions,
)
from cgauto.top_player_opening_analysis import analyze_players, bfs  # noqa: E402
import cgauto.waste_sweep as waste_sweep  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO / "local_codex_1/n5-endgame-opponent-plant-contest"

RESIDENT_AGENT_ID = 6561795
YAMO_AGENT_ID = 6479814
COHORTS = (("resident", RESIDENT_AGENT_ID), ("yamo", YAMO_AGENT_ID))

EXPECTED_INDEX_HASH = "12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d"
EXPECTED_INDEX_RECORDS = 9_082
EXPECTED_FROZEN_MANIFEST_HASH = (
    "53ee5cf3347fbc72dcd1021369cb2b41ce48eb6c3ca22fc9981f7abf14a2b26f"
)
EXPECTED_COHORTS = {
    "resident": {
        "count": 242,
        "ids_hash": "3ea12d776e10019905b098ca159b4688266fe6874935a7d03c58ce216b8ec91c",
    },
    "yamo": {
        "count": 140,
        "ids_hash": "0dc44b60be9e6ed893cc0226b3e1f170a6a6b1da46e67b0f8b266802ad9a2ec0",
    },
}
EXPECTED_DEPENDENCIES = {
    "cgauto/fidelity_gap_audit.py": (
        "1ede4eef0b2f6af23c8b90b90603664b4701746483a73e764bb5b32d9d024a77"
    ),
    "cgauto/analyze_d101a_production_suppression.py": (
        "9ffb10092180fa8a9ac848033650dc5d1c8fe95f83bff3a0aad9dc0dd37d4d30"
    ),
    "cgauto/waste_sweep.py": (
        "cb5c813d591f3defd3809f97b25b61f6c7cdf67f039836d7b43c0544d29cad02"
    ),
    "rust/src/bin/yamo_orchard_live.rs": (
        "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
    ),
}

ENDGAME_TURN_EXCLUSIVE = 250
MATERIAL_MARGIN = 20.0
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 20_260_730
MIN_TARGETS = 30
MIN_TARGET_GAMES = 20
MIN_POSITIVE_TARGETS = 20
MIN_POSITIVE_GAMES = 10
FRUIT_ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA")
TARGET_FIELDS = (
    "cohort",
    "agent_id",
    "game_id",
    "subject_seat",
    "birth_turn",
    "cell_x",
    "cell_y",
    "species",
    "pre_turn_margin",
    "final_margin",
    "turns_remaining",
    "distance_to_opponent_shack",
    "subject_eta_at_birth",
    "subject_eta_zero",
    "subject_eta_le_one",
    "subject_reachable_within_remaining",
    "subject_first_contact_turn",
    "subject_first_contact_verb",
    "opponent_first_contact_turn",
    "opponent_first_contact_verb",
    "subject_harvest_actions",
    "subject_fruit_gained",
    "subject_chop_actions",
    "subject_wood_gained",
    "subject_extracted_score_equivalent",
    "opponent_harvest_actions",
    "opponent_fruit_gained",
    "opponent_chop_actions",
    "opponent_wood_gained",
    "opponent_extracted_score_equivalent",
    "observed_yield_swing_ceiling",
    "missed_contact_swing_ceiling",
    "death_turn",
    "feller",
    "survived_to_end",
    "unique_plant_event",
    "lineage_agreement",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ids_hash(game_ids: list[int]) -> str:
    payload = ("\n".join(str(game_id) for game_id in game_ids) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("percentile requires values")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return float(
        sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight
    )


def bootstrap_mean_interval(
    values: list[float],
    *,
    reps: int = BOOTSTRAP_REPS,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    if not values:
        return {"mean": None, "ci_lo": None, "ci_hi": None, "reps": reps, "seed": seed}
    rng = random.Random(seed)
    n = len(values)
    draws = []
    for _ in range(reps):
        draws.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    draws.sort()
    return {
        "mean": statistics.mean(values),
        "ci_lo": percentile(draws, 0.025),
        "ci_hi": percentile(draws, 0.975),
        "reps": reps,
        "seed": seed,
    }


def decide_verdict(
    *,
    source_integrity: bool,
    decode_integrity: bool,
    target_integrity: bool,
    target_count: int,
    target_games: int,
    positive_targets: int,
    positive_games: int,
    ci_lo: float | None,
    ci_hi: float | None,
) -> tuple[str, dict]:
    gates = {
        "source_integrity": source_integrity,
        "decode_integrity": decode_integrity,
        "target_integrity": target_integrity,
        "resident_targets_ge_30": target_count >= MIN_TARGETS,
        "resident_target_games_ge_20": target_games >= MIN_TARGET_GAMES,
        "resident_positive_targets_ge_20": positive_targets >= MIN_POSITIVE_TARGETS,
        "resident_positive_games_ge_10": positive_games >= MIN_POSITIVE_GAMES,
        "ci_lower_ge_20": ci_lo is not None and ci_lo >= MATERIAL_MARGIN,
        "ci_upper_lt_20": ci_hi is not None and ci_hi < MATERIAL_MARGIN,
    }
    support = all(
        gates[key]
        for key in (
            "source_integrity",
            "decode_integrity",
            "target_integrity",
            "resident_targets_ge_30",
            "resident_target_games_ge_20",
        )
    )
    material = (
        support
        and gates["resident_positive_targets_ge_20"]
        and gates["resident_positive_games_ge_10"]
        and gates["ci_lower_ge_20"]
    )
    if material:
        verdict = "MATERIAL_CONTEST_OPPORTUNITY"
    elif support and gates["ci_upper_lt_20"]:
        verdict = "NO_MATERIAL_CONTEST_OPPORTUNITY"
    else:
        verdict = "UNIDENTIFIABLE"
    gates["support_pass"] = support
    gates["material_pass"] = material
    return verdict, gates


def configure_corpus(corpus_root: Path) -> None:
    waste_sweep.GAMES_INDEX = corpus_root / "data/processed/games.jsonl"
    waste_sweep.RAW_GAMES = corpus_root / "data/raw/games"
    waste_sweep.TRAJECTORIES = corpus_root / "data/processed/trajectories"


def load_index(index_path: Path) -> list[dict]:
    return [json.loads(line) for line in index_path.read_text().splitlines() if line.strip()]


def cohort_game_ids(rows: list[dict], agent_id: int) -> list[int]:
    return sorted(
        int(row["gameId"])
        for row in rows
        if any(int(player["agentId"]) == agent_id for player in row["players"])
    )


def cohort_game_ids_from_manifest(manifest: dict) -> dict[str, list[int]]:
    selected = {}
    for label, agent_id in COHORTS:
        entries = [
            entry
            for entry in manifest.get("entries", [])
            if entry.get("cohort") == label
        ]
        if any(int(entry.get("agent_id", -1)) != agent_id for entry in entries):
            raise ValueError(f"{label}: frozen manifest agent mismatch")
        selected[label] = sorted(int(entry["game_id"]) for entry in entries)
    return selected


def build_input_manifest(corpus_root: Path, selected: dict[str, list[int]]) -> dict:
    file_cache: dict[int, dict] = {}
    entries = []
    missing = []
    for label, agent_id in COHORTS:
        for game_id in selected[label]:
            if game_id not in file_cache:
                raw = corpus_root / f"data/raw/games/{game_id}.json"
                trajectory = (
                    corpus_root / f"data/processed/trajectories/{game_id}.jsonl"
                )
                if not raw.is_file() or not trajectory.is_file():
                    if not raw.is_file():
                        missing.append(f"data/raw/games/{game_id}.json")
                    if not trajectory.is_file():
                        missing.append(
                            f"data/processed/trajectories/{game_id}.jsonl"
                        )
                    file_cache[game_id] = {
                        "raw_sha256": None,
                        "trajectory_sha256": None,
                    }
                else:
                    file_cache[game_id] = {
                        "raw_sha256": sha256_file(raw),
                        "trajectory_sha256": sha256_file(trajectory),
                    }
            entries.append(
                {
                    "cohort": label,
                    "agent_id": agent_id,
                    "game_id": game_id,
                    **file_cache[game_id],
                }
            )
    return {
        "schema": 1,
        "logical_paths": {
            "index": "data/processed/games.jsonl",
            "raw": "data/raw/games/<gameId>.json",
            "trajectory": "data/processed/trajectories/<gameId>.jsonl",
        },
        "cohort_occurrences": len(entries),
        "unique_games": len(file_cache),
        "cross_cohort_game_ids": sorted(
            set(selected["resident"]) & set(selected["yamo"])
        ),
        "missing": sorted(set(missing)),
        "entries": entries,
    }


def action_summary(events: list[dict], generation_id: str) -> dict:
    selected = [
        event
        for event in events
        if event.get("success")
        and event.get("target_generation") == generation_id
        and event.get("verb") in {"HARVEST", "CHOP"}
    ]
    harvests = [event for event in selected if event["verb"] == "HARVEST"]
    chops = [event for event in selected if event["verb"] == "CHOP"]
    fruit = sum(
        sum(int(event["gained"].get(item, 0)) for item in FRUIT_ITEMS)
        for event in harvests
    )
    wood = sum(int(event["gained"].get("WOOD", 0)) for event in chops)
    first = min(selected, key=lambda event: (int(event["turn"]), event["verb"]), default=None)
    return {
        "first_turn": int(first["turn"]) if first else None,
        "first_verb": first["verb"] if first else None,
        "harvest_actions": len(harvests),
        "fruit_gained": fruit,
        "chop_actions": len(chops),
        "wood_gained": wood,
        "extracted_score_equivalent": fruit + 4 * wood,
    }


def generation_fate(
    generation_id: str,
    birth_turn: int,
    lineage: list[dict],
    subject_events: list[dict],
    opponent_events: list[dict],
) -> dict:
    death_turn = None
    for turn in range(max(1, birth_turn + 1), len(lineage)):
        before_live = generation_id in lineage[turn - 1].values()
        after_live = generation_id in lineage[turn].values()
        if before_live and not after_live:
            death_turn = turn
            break
    if death_turn is None:
        return {"death_turn": None, "feller": None, "survived_to_end": True}

    subject_chop = any(
        event.get("success")
        and event.get("verb") == "CHOP"
        and event.get("target_generation") == generation_id
        and int(event["turn"]) == death_turn
        for event in subject_events
    )
    opponent_chop = any(
        event.get("success")
        and event.get("verb") == "CHOP"
        and event.get("target_generation") == generation_id
        and int(event["turn"]) == death_turn
        for event in opponent_events
    )
    if subject_chop and opponent_chop:
        feller = "both"
    elif subject_chop:
        feller = "subject"
    elif opponent_chop:
        feller = "opponent"
    else:
        feller = "unaccounted"
    return {"death_turn": death_turn, "feller": feller, "survived_to_end": False}


def is_target_generation(meta: dict, birth_turn: int, margin_series: list[int]) -> bool:
    return (
        meta.get("origin") == "opponent"
        and birth_turn > ENDGAME_TURN_EXCLUSIVE
        and birth_turn < len(margin_series)
        and margin_series[birth_turn - 1] > 0
    )


def generation_identity_checks(
    generation_id: str,
    meta: dict,
    birth_turn: int,
    counterpart: dict | None,
    subject_lineage: list[dict],
    opponent_lineage: list[dict],
    opponent_events: list[dict],
) -> tuple[bool, bool]:
    cell = tuple(meta["cell"])
    lineage_agreement = bool(
        counterpart
        and counterpart.get("origin") == "actor"
        and int(counterpart["birth_turn"]) == birth_turn
        and list(counterpart["cell"]) == list(meta["cell"])
        and counterpart["kind"] == meta["kind"]
        and birth_turn < len(subject_lineage)
        and birth_turn < len(opponent_lineage)
        and subject_lineage[birth_turn].get(cell) == generation_id
        and opponent_lineage[birth_turn].get(cell) == generation_id
    )
    plant_events = [
        event
        for event in opponent_events
        if event.get("success")
        and event.get("verb") == "PLANT"
        and event.get("created_generation") == generation_id
        and event.get("created_origin") == "actor"
    ]
    return lineage_agreement, len(plant_events) == 1


def subject_eta_at_birth(game, birth_turn: int, cell: tuple[int, int]) -> int | None:
    at_birth = game.states[birth_turn]
    best = None
    for unit in at_birth["units"]:
        if int(unit["player"]) != game.me:
            continue
        distances = bfs(game.board["walkable"], [(int(unit["x"]), int(unit["y"]))])
        distance = distances.get(cell)
        if distance is None:
            continue
        eta = math.ceil(distance / max(1, int(unit["ms"])))
        if best is None or eta < best:
            best = eta
    return best


def worker_ordinals(game, seat: int) -> dict[int, int]:
    analyses = analyze_players(game.states, game.trajectory)
    return {
        int(worker["unit_id"]): int(worker["ordinal"])
        for worker in analyses[seat]["workers"]
    }


def analyze_game(
    corpus_root_text: str,
    cohort: str,
    agent_id: int,
    game_id: int,
) -> dict:
    try:
        corpus_root = Path(corpus_root_text)
        configure_corpus(corpus_root)
        game = waste_sweep.decode_game_for_agent(game_id, agent_id)
        if len(game.states) - 1 != len(game.trajectory):
            raise ValueError(
                f"turn mismatch: states={len(game.states) - 1}, "
                f"trajectory={len(game.trajectory)}"
            )
        subject_ordinals = worker_ordinals(game, game.me)
        opponent_ordinals = worker_ordinals(game, game.opponent)
        (
            subject_events,
            subject_generations,
            subject_lineage,
            subject_quality,
        ) = reconstruct_generation_actions(
            game.states, game.trajectory, game.me, subject_ordinals
        )
        (
            opponent_events,
            opponent_generations,
            opponent_lineage,
            opponent_quality,
        ) = reconstruct_generation_actions(
            game.states, game.trajectory, game.opponent, opponent_ordinals
        )

        targets = []
        for generation_id, meta in sorted(
            subject_generations.items(),
            key=lambda item: (
                int(item[1]["birth_turn"]),
                tuple(item[1]["cell"]),
                item[0],
            ),
        ):
            birth_turn = int(meta["birth_turn"])
            if not is_target_generation(meta, birth_turn, game.margin_series):
                continue
            counterpart = opponent_generations.get(generation_id)
            lineage_agreement, unique_plant_event = generation_identity_checks(
                generation_id,
                meta,
                birth_turn,
                counterpart,
                subject_lineage,
                opponent_lineage,
                opponent_events,
            )
            subject = action_summary(subject_events, generation_id)
            opponent = action_summary(opponent_events, generation_id)
            cell = (int(meta["cell"][0]), int(meta["cell"][1]))
            eta = subject_eta_at_birth(game, birth_turn, cell)
            turns_remaining = game.turns - birth_turn
            reachable = eta is not None and eta <= turns_remaining
            ceiling = (
                2 * opponent["extracted_score_equivalent"] if reachable else 0
            )
            missed = ceiling if subject["first_turn"] is None else 0
            fate = generation_fate(
                generation_id,
                birth_turn,
                subject_lineage,
                subject_events,
                opponent_events,
            )
            targets.append(
                {
                    "cohort": cohort,
                    "agent_id": agent_id,
                    "game_id": game_id,
                    "subject_seat": game.me,
                    "birth_turn": birth_turn,
                    "cell_x": cell[0],
                    "cell_y": cell[1],
                    "species": meta["kind"],
                    "pre_turn_margin": game.margin_series[birth_turn - 1],
                    "final_margin": game.margin,
                    "turns_remaining": turns_remaining,
                    "distance_to_opponent_shack": abs(cell[0] - game.opp_shack[0])
                    + abs(cell[1] - game.opp_shack[1]),
                    "subject_eta_at_birth": eta,
                    "subject_eta_zero": eta == 0,
                    "subject_eta_le_one": eta is not None and eta <= 1,
                    "subject_reachable_within_remaining": reachable,
                    "subject_first_contact_turn": subject["first_turn"],
                    "subject_first_contact_verb": subject["first_verb"],
                    "opponent_first_contact_turn": opponent["first_turn"],
                    "opponent_first_contact_verb": opponent["first_verb"],
                    "subject_harvest_actions": subject["harvest_actions"],
                    "subject_fruit_gained": subject["fruit_gained"],
                    "subject_chop_actions": subject["chop_actions"],
                    "subject_wood_gained": subject["wood_gained"],
                    "subject_extracted_score_equivalent": subject[
                        "extracted_score_equivalent"
                    ],
                    "opponent_harvest_actions": opponent["harvest_actions"],
                    "opponent_fruit_gained": opponent["fruit_gained"],
                    "opponent_chop_actions": opponent["chop_actions"],
                    "opponent_wood_gained": opponent["wood_gained"],
                    "opponent_extracted_score_equivalent": opponent[
                        "extracted_score_equivalent"
                    ],
                    "observed_yield_swing_ceiling": ceiling,
                    "missed_contact_swing_ceiling": missed,
                    **fate,
                    "unique_plant_event": unique_plant_event,
                    "lineage_agreement": lineage_agreement,
                }
            )
        return {
            "ok": True,
            "cohort": cohort,
            "agent_id": agent_id,
            "game_id": game_id,
            "seat": game.me,
            "turns": game.turns,
            "final_margin": game.margin,
            "targets": targets,
            "quality": {
                "subject": dict(subject_quality),
                "opponent": dict(opponent_quality),
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "cohort": cohort,
            "agent_id": agent_id,
            "game_id": game_id,
            "error": f"{type(exc).__name__}: {exc}",
        }


def counter_dict(values) -> dict:
    return dict(sorted(Counter(str(value) for value in values).items()))


def summarize_cohort(
    label: str,
    agent_id: int,
    game_ids: list[int],
    results: list[dict],
    *,
    bootstrap_reps: int,
) -> tuple[dict, list[dict], list[dict]]:
    ok = sorted((row for row in results if row["ok"]), key=lambda row: row["game_id"])
    failed = sorted(
        (row for row in results if not row["ok"]), key=lambda row: row["game_id"]
    )
    targets = sorted(
        (target for row in ok for target in row["targets"]),
        key=lambda row: (row["game_id"], row["birth_turn"], row["cell_x"], row["cell_y"]),
    )
    targets_by_game: dict[int, list[dict]] = defaultdict(list)
    for target in targets:
        targets_by_game[target["game_id"]].append(target)

    game_rows = []
    for game_id in game_ids:
        rows = targets_by_game.get(game_id, [])
        game_rows.append(
            {
                "game_id": game_id,
                "targets": len(rows),
                "positive_yield_targets": sum(
                    target["opponent_extracted_score_equivalent"] > 0
                    for target in rows
                ),
                "opponent_extracted_score_equivalent": sum(
                    target["opponent_extracted_score_equivalent"] for target in rows
                ),
                "subject_extracted_score_equivalent": sum(
                    target["subject_extracted_score_equivalent"] for target in rows
                ),
                "observed_yield_swing_ceiling": sum(
                    target["observed_yield_swing_ceiling"] for target in rows
                ),
                "missed_contact_swing_ceiling": sum(
                    target["missed_contact_swing_ceiling"] for target in rows
                ),
            }
        )
    ceilings = [row["observed_yield_swing_ceiling"] for row in game_rows]
    missed = [row["missed_contact_swing_ceiling"] for row in game_rows]
    target_game_ceilings = [
        row["observed_yield_swing_ceiling"] for row in game_rows if row["targets"]
    ]
    positive = [
        target for target in targets if target["opponent_extracted_score_equivalent"] > 0
    ]
    positive_games = {
        target["game_id"]
        for target in targets
        if target["opponent_extracted_score_equivalent"] > 0
    }
    integrity_failures = [
        {
            "game_id": target["game_id"],
            "birth_turn": target["birth_turn"],
            "cell": [target["cell_x"], target["cell_y"]],
            "unique_plant_event": target["unique_plant_event"],
            "lineage_agreement": target["lineage_agreement"],
        }
        for target in targets
        if not target["unique_plant_event"] or not target["lineage_agreement"]
    ]
    summary = {
        "label": label,
        "agent_id": agent_id,
        "games_requested": len(game_ids),
        "games_decoded": len(ok),
        "games_failed": len(failed),
        "failures": failed,
        "games_reaching_turn_gt_250": sum(row["turns"] > 250 for row in ok),
        "target_generations": len(targets),
        "target_games": len(targets_by_game),
        "target_game_share_of_reaching_window": (
            len(targets_by_game) / sum(row["turns"] > 250 for row in ok)
            if any(row["turns"] > 250 for row in ok)
            else None
        ),
        "mean_targets_per_game_reaching_window": (
            len(targets) / sum(row["turns"] > 250 for row in ok)
            if any(row["turns"] > 250 for row in ok)
            else None
        ),
        "positive_opponent_yield_targets": len(positive),
        "positive_opponent_yield_games": len(positive_games),
        "subject_contacted_targets": sum(
            target["subject_first_contact_turn"] is not None for target in targets
        ),
        "subject_eta_zero_targets": sum(target["subject_eta_zero"] for target in targets),
        "subject_eta_le_one_targets": sum(
            target["subject_eta_le_one"] for target in targets
        ),
        "subject_reachable_within_remaining_targets": sum(
            target["subject_reachable_within_remaining"] for target in targets
        ),
        "opponent_extracted_score_equivalent_total": sum(
            target["opponent_extracted_score_equivalent"] for target in targets
        ),
        "subject_extracted_score_equivalent_total": sum(
            target["subject_extracted_score_equivalent"] for target in targets
        ),
        "all_game_observed_yield_swing_ceiling": bootstrap_mean_interval(
            ceilings, reps=bootstrap_reps
        ),
        "all_game_missed_contact_swing_ceiling": {
            "mean": statistics.mean(missed) if missed else None,
        },
        "target_game_observed_yield_swing_ceiling_mean": (
            statistics.mean(target_game_ceilings) if target_game_ceilings else None
        ),
        "breakdowns": {
            "seat": counter_dict(target["subject_seat"] for target in targets),
            "species": counter_dict(target["species"] for target in targets),
            "birth_turn_band": counter_dict(
                "251_274" if target["birth_turn"] <= 274 else "275_300"
                for target in targets
            ),
            "opponent_shack_distance": counter_dict(
                target["distance_to_opponent_shack"] for target in targets
            ),
        },
        "target_integrity_failures": integrity_failures,
        "quality_totals": {
            orientation: dict(
                sorted(
                    sum(
                        (
                            Counter(row["quality"][orientation])
                            for row in ok
                        ),
                        Counter(),
                    ).items()
                )
            )
            for orientation in ("subject", "opponent")
        },
    }
    return summary, targets, game_rows


def render_report(report: dict) -> str:
    resident = report["cohorts"]["resident"]
    yamo = report["cohorts"]["yamo"]
    interval = resident["all_game_observed_yield_swing_ceiling"]
    lines = [
        "# N5 endgame opponent-plant contest audit",
        "",
        f"- Verdict: **`{report['verdict']}`**.",
        (
            f"- Exact replay coverage: {report['coverage']['decoded_occurrences']}/"
            f"{report['coverage']['requested_occurrences']} cohort occurrences "
            f"({report['coverage']['unique_games']} unique games)."
        ),
        (
            f"- Resident targets: {resident['target_generations']} generations in "
            f"{resident['target_games']} games; "
            f"{resident['positive_opponent_yield_targets']} targets in "
            f"{resident['positive_opponent_yield_games']} games yield carried resources "
            "to the opponent."
        ),
        (
            "- Resident replay-conditioned factor-two observed-yield ceiling across all "
            f"games: {interval['mean']:.6f}, bootstrap 95% CI "
            f"[{interval['ci_lo']:.6f}, {interval['ci_hi']:.6f}] versus 20."
        ),
        (
            f"- Subject contact: {resident['subject_contacted_targets']}/"
            f"{resident['target_generations']}; optimistic reach within remaining turns: "
            f"{resident['subject_reachable_within_remaining_targets']}/"
            f"{resident['target_generations']}."
        ),
        (
            f"- H13 fidelity census: resident {resident['target_generations']} targets / "
            f"{resident['target_games']} games, yamo {yamo['target_generations']} targets / "
            f"{yamo['target_games']} games."
        ),
        "",
        "## Boundary",
        "",
        (
            "Enemy units can share cells, so this is access for later HARVEST/CHOP, not "
            "body-blocking. Extracted fruit/wood is carried resource, not banked score. "
            "The factor-two quantity is deliberately generous and replay-conditioned; "
            "it is not a causal policy-value estimate."
        ),
        "",
        "## Gates",
        "",
    ]
    for name, passed in report["gates"].items():
        lines.append(f"- `{name}`: **{str(bool(passed)).lower()}**")
    return "\n".join(lines) + "\n"


def self_test() -> None:
    assert percentile([0.0, 10.0], 0.5) == 5.0
    first = bootstrap_mean_interval([0.0, 2.0, 4.0], reps=200, seed=7)
    second = bootstrap_mean_interval([0.0, 2.0, 4.0], reps=200, seed=7)
    assert first == second
    verdict, gates = decide_verdict(
        source_integrity=True,
        decode_integrity=True,
        target_integrity=True,
        target_count=40,
        target_games=25,
        positive_targets=22,
        positive_games=12,
        ci_lo=1.0,
        ci_hi=5.0,
    )
    assert verdict == "NO_MATERIAL_CONTEST_OPPORTUNITY"
    assert gates["support_pass"]
    verdict, _ = decide_verdict(
        source_integrity=True,
        decode_integrity=True,
        target_integrity=True,
        target_count=40,
        target_games=25,
        positive_targets=22,
        positive_games=12,
        ci_lo=21.0,
        ci_hi=30.0,
    )
    assert verdict == "MATERIAL_CONTEST_OPPORTUNITY"
    verdict, _ = decide_verdict(
        source_integrity=True,
        decode_integrity=True,
        target_integrity=True,
        target_count=40,
        target_games=25,
        positive_targets=22,
        positive_games=12,
        ci_lo=10.0,
        ci_hi=25.0,
    )
    assert verdict == "UNIDENTIFIABLE"
    summary = action_summary(
        [
            {
                "success": True,
                "target_generation": "g",
                "verb": "HARVEST",
                "turn": 4,
                "gained": {"APPLE": 2},
            },
            {
                "success": True,
                "target_generation": "g",
                "verb": "CHOP",
                "turn": 5,
                "gained": {"WOOD": 1},
            },
        ],
        "g",
    )
    assert summary["extracted_score_equivalent"] == 6
    assert is_target_generation(
        {"origin": "opponent"}, 251, [0] * 250 + [1, 1]
    )
    game = SimpleNamespace(
        states=[
            {"units": [{"player": 0, "x": 3, "y": 0, "ms": 1}]},
            {"units": [{"player": 0, "x": 0, "y": 0, "ms": 2}]},
        ],
        board={"walkable": {(0, 0), (1, 0), (2, 0), (3, 0)}},
        me=0,
    )
    assert subject_eta_at_birth(game, 1, (3, 0)) == 2
    print("self-test: ok")


def run(args: argparse.Namespace) -> tuple[dict, dict, list[dict]]:
    corpus_root = args.corpus_root.resolve()
    index_path = corpus_root / "data/processed/games.jsonl"
    index_hash = sha256_file(index_path)
    rows = load_index(index_path)
    frozen_manifest = None
    frozen_manifest_hash = None
    if args.frozen_input_manifest is not None:
        frozen_manifest_path = args.frozen_input_manifest.resolve()
        frozen_manifest_hash = sha256_file(frozen_manifest_path)
        frozen_manifest = json.loads(frozen_manifest_path.read_text())
        selected = cohort_game_ids_from_manifest(frozen_manifest)
        selection_mode = "frozen_input_manifest"
    else:
        selected = {
            label: cohort_game_ids(rows, agent_id) for label, agent_id in COHORTS
        }
        selection_mode = "live_index"
    dependency_checks = {}
    for relative, expected in EXPECTED_DEPENDENCIES.items():
        actual = sha256_file(REPO / relative)
        dependency_checks[relative] = {
            "expected_sha256": expected,
            "actual_sha256": actual,
            "pass": actual == expected,
        }
    cohort_checks = {}
    for label, _agent_id in COHORTS:
        actual_hash = ids_hash(selected[label])
        expected = EXPECTED_COHORTS[label]
        cohort_checks[label] = {
            "expected_count": expected["count"],
            "actual_count": len(selected[label]),
            "expected_ids_sha256": expected["ids_hash"],
            "actual_ids_sha256": actual_hash,
            "unique_within_cohort": len(selected[label]) == len(set(selected[label])),
            "pass": (
                len(selected[label]) == expected["count"]
                and actual_hash == expected["ids_hash"]
                and len(selected[label]) == len(set(selected[label]))
            ),
        }
    manifest = build_input_manifest(corpus_root, selected)
    if frozen_manifest is None:
        source_checks = {
            "index_hash": index_hash == EXPECTED_INDEX_HASH,
            "index_records": len(rows) == EXPECTED_INDEX_RECORDS,
            "dependency_hashes": all(row["pass"] for row in dependency_checks.values()),
            "cohort_lists": all(row["pass"] for row in cohort_checks.values()),
            "all_inputs_present": not manifest["missing"],
        }
    else:
        source_checks = {
            "frozen_manifest_hash": (
                frozen_manifest_hash == EXPECTED_FROZEN_MANIFEST_HASH
            ),
            "frozen_manifest_inputs_unchanged": manifest == frozen_manifest,
            "dependency_hashes": all(row["pass"] for row in dependency_checks.values()),
            "cohort_lists": all(row["pass"] for row in cohort_checks.values()),
            "all_inputs_present": not manifest["missing"],
        }
    source_integrity = all(source_checks.values())

    tasks = [
        (str(corpus_root), label, agent_id, game_id)
        for label, agent_id in COHORTS
        for game_id in selected[label]
    ]
    if args.jobs == 1:
        results = [analyze_game(*task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            results = list(executor.map(_analyze_task, tasks, chunksize=2))

    cohort_summaries = {}
    all_targets = []
    per_game = {}
    for label, agent_id in COHORTS:
        cohort_results = [row for row in results if row["cohort"] == label]
        summary, targets, game_rows = summarize_cohort(
            label,
            agent_id,
            selected[label],
            cohort_results,
            bootstrap_reps=args.bootstrap_reps,
        )
        cohort_summaries[label] = summary
        all_targets.extend(targets)
        per_game[label] = game_rows

    requested = sum(len(ids) for ids in selected.values())
    decoded = sum(row["ok"] for row in results)
    decode_integrity = decoded == requested
    target_integrity = all(
        not summary["target_integrity_failures"]
        for summary in cohort_summaries.values()
    )
    resident = cohort_summaries["resident"]
    interval = resident["all_game_observed_yield_swing_ceiling"]
    verdict, gates = decide_verdict(
        source_integrity=source_integrity,
        decode_integrity=decode_integrity,
        target_integrity=target_integrity,
        target_count=resident["target_generations"],
        target_games=resident["target_games"],
        positive_targets=resident["positive_opponent_yield_targets"],
        positive_games=resident["positive_opponent_yield_games"],
        ci_lo=interval["ci_lo"],
        ci_hi=interval["ci_hi"],
    )
    report = {
        "schema": 1,
        "task": "20260730-n5-endgame-opponent-plant-contest",
        "verdict": verdict,
        "scope": (
            "read-only observational generation-lineage audit; extracted cargo is not "
            "banked score; factor-two ceiling is replay-conditioned, not causal"
        ),
        "parameters": {
            "endgame_turn_exclusive": ENDGAME_TURN_EXCLUSIVE,
            "material_margin": MATERIAL_MARGIN,
            "bootstrap_reps": args.bootstrap_reps,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "source": {
            "logical_index": "data/processed/games.jsonl",
            "selection_mode": selection_mode,
            "frozen_index_sha256": EXPECTED_INDEX_HASH,
            "frozen_index_records": EXPECTED_INDEX_RECORDS,
            "live_index_sha256": index_hash,
            "live_index_records": len(rows),
            "frozen_input_manifest_sha256": frozen_manifest_hash,
            "checks": source_checks,
            "dependencies": dependency_checks,
            "cohorts": cohort_checks,
        },
        "coverage": {
            "requested_occurrences": requested,
            "decoded_occurrences": decoded,
            "unique_games": manifest["unique_games"],
            "cross_cohort_game_ids": manifest["cross_cohort_game_ids"],
        },
        "cohorts": cohort_summaries,
        "gates": gates,
        "causal_boundary": {
            "enemy_units_can_share_cells": True,
            "contest_is_body_block": False,
            "extracted_resource_is_banked_score": False,
            "causal_policy_value_identified": False,
            "material_verdict_authorizes_only_new_simulation_protocol": True,
        },
        "per_game": per_game,
    }
    return report, manifest, all_targets


def _analyze_task(task: tuple[str, str, int, int]) -> dict:
    return analyze_game(*task)


def write_outputs(
    output_dir: Path,
    report: dict,
    manifest: dict,
    targets: list[dict],
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "result.json"
    manifest_path = output_dir / "input-manifest.json"
    targets_path = output_dir / "targets.csv"
    report_path = output_dir / "report.md"
    result_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with targets_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TARGET_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in targets:
            writer.writerow({field: row.get(field) for field in TARGET_FIELDS})
    report_path.write_text(render_report(report))
    return {
        path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in (result_path, manifest_path, targets_path, report_path)
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=REPO,
        help="repository worktree containing the frozen logical data paths",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--frozen-input-manifest",
        type=Path,
        help=(
            "reuse the exact previously validated 382-occurrence manifest when the "
            "append-only live index has advanced"
        ),
    )
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if args.bootstrap_reps < 1:
        parser.error("--bootstrap-reps must be positive")
    return args


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    report, manifest, targets = run(args)
    hashes = write_outputs(args.output_dir, report, manifest, targets)
    print(json.dumps({"verdict": report["verdict"], "outputs": hashes}, indent=2))
    return 0 if report["verdict"] != "UNIDENTIFIABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
