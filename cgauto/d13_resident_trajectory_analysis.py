#!/usr/bin/env python3
"""Analyze the resident trajectory distribution and freeze a residual interface."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d11_recipe_catalog_analysis import summary  # noqa: E402

FROZEN_SEEDS = list(range(24, 40))
FROZEN_OPPONENTS = [
    "compact_gold",
    "gold_adaptive",
    "legend_balanced",
    "mybot",
    "norx_native_three",
    "resident",
]
GAME_NUMERIC = {
    "seed",
    "seat",
    "margin",
    "wood_edge",
    "terminal_turn",
    "workers",
    "opponent_workers",
    "score",
    "opponent_score",
}
DECISION_STRINGS = {
    "opponent",
    "policy",
    "local_plant_type",
    "resident_command",
    "resident_verb",
    "actor_command",
    "actor_verb",
    "previous_verb",
    "other_verb",
    "state_fingerprint",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path, string_fields: set[str]) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field, value in list(row.items()):
            if field not in string_fields:
                row[field] = int(value)
    return rows


def nearest_rank(values, percentile: float) -> int | float | None:
    ordered = sorted(values)
    if not ordered:
        return None
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def role(row: dict) -> str:
    if row["ordinal"] == 0:
        return "starter"
    if row["ordinal"] == 1:
        return "second"
    return "later"


def counts_and_rates(values) -> dict:
    counts = Counter(values)
    total = sum(counts.values())
    return {
        key: {"count": count, "rate": count / total}
        for key, count in sorted(counts.items(), key=lambda item: str(item[0]))
    }


def validate(games: list[dict], decisions: list[dict]) -> None:
    expected = {
        (seed, seat, opponent)
        for seed in FROZEN_SEEDS
        for seat in range(2)
        for opponent in FROZEN_OPPONENTS
    }
    observed = {(row["seed"], row["seat"], row["opponent"]) for row in games}
    if len(games) != 192 or observed != expected:
        raise ValueError(
            f"incomplete resident game block: games={len(games)}, expected=192"
        )
    if any(row["policy"] != "resident" for row in games):
        raise ValueError("game block must contain resident policy only")
    if not decisions:
        raise ValueError("resident decision table is empty")
    if any(row["policy"] != "resident" for row in decisions):
        raise ValueError("decision block must contain resident policy only")
    game_by_key = {
        (row["seed"], row["seat"], row["opponent"]): row for row in games
    }
    for row in decisions:
        key = (row["seed"], row["seat"], row["opponent"])
        if key not in game_by_key:
            raise ValueError(f"decision has no terminal game row: {key}")
        game = game_by_key[key]
        if (
            row["terminal_margin"] != game["margin"]
            or row["terminal_wood_edge"] != game["wood_edge"]
            or row["terminal_turn"] != game["terminal_turn"]
        ):
            raise ValueError(f"decision terminal outcome mismatch: {key}")


def analyze(games: list[dict], decisions: list[dict], games_path: Path, decisions_path: Path) -> dict:
    validate(games, decisions)
    decision_counts = Counter(
        (row["seed"], row["seat"], row["opponent"]) for row in decisions
    )
    consecutive = [row for row in decisions if row["previous_verb"] != "-"]
    target_eligible = [
        row
        for row in consecutive
        if row["resident_target_x"] >= 0 and row["previous_target_x"] >= 0
    ]
    move_target_eligible = [
        row
        for row in target_eligible
        if row["resident_verb"] == "MOVE" and row["previous_verb"] == "MOVE"
    ]
    multiworker = [row for row in decisions if row["worker_count"] >= 2]
    local_available = [row for row in decisions if row["local_productive_actions"] > 0]
    direct_rate = statistics.mean(
        row["resident_directly_decodable"] for row in decisions
    )
    option_p95 = nearest_rank(
        (row["residual_options"] for row in decisions), 0.95
    )
    target_persistence_rate = (
        statistics.mean(row["target_persistent"] for row in target_eligible)
        if target_eligible
        else 0
    )
    multiworker_rate = len(multiworker) / len(decisions)
    local_available_rate = len(local_available) / len(decisions)
    spatial_interface = direct_rate >= 0.95 and option_p95 <= 64
    include_previous_intent = target_persistence_rate >= 0.20
    include_other_worker_intent = multiworker_rate >= 0.10
    retain_poi_moves = local_available_rate < 0.20

    roles = {}
    for role_name in ("starter", "second", "later"):
        rows = [row for row in decisions if role(row) == role_name]
        roles[role_name] = {
            "decisions": len(rows),
            "rate": len(rows) / len(decisions),
            "verbs": counts_and_rates(row["resident_verb"] for row in rows),
            "wait_rate": (
                statistics.mean(row["resident_verb"] == "WAIT" for row in rows)
                if rows
                else None
            ),
            "local_productive_available_rate": (
                statistics.mean(row["local_productive_actions"] > 0 for row in rows)
                if rows
                else None
            ),
        }

    carry_fields = [f"carry{index}" for index in range(6)]
    inv_fields = [f"inv{index}" for index in range(6)]
    local_signatures = {
        (
            row["ordinal"],
            row["worker_count"],
            row["ms"],
            row["cc"],
            row["hp"],
            row["chop"],
            row["free"],
            *(row[field] for field in carry_fields),
            *(min(row[field], 9) for field in inv_fields),
            row["local_plant_type"],
            min(row["local_plant_fruits"], 3),
            row["near_home"],
            row["near_iron"],
            row["resident_verb"],
            row["previous_verb"],
            row["other_verb"],
        )
        for row in decisions
    }
    actor_exact = statistics.mean(
        row["resident_command"] == row["actor_command"] for row in decisions
    )
    actor_verb = statistics.mean(
        row["resident_verb"] == row["actor_verb"] for row in decisions
    )

    return {
        "schema": 1,
        "scope": (
            "D13 exact resident trajectory interface audit on reused development "
            "seeds; no candidate, prospective, submission, or Arena authorization"
        ),
        "source": {
            "games": str(games_path),
            "games_sha256": sha256(games_path),
            "decisions": str(decisions_path),
            "decisions_sha256": sha256(decisions_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "seeds": FROZEN_SEEDS,
            "seats": [0, 1],
            "opponents": FROZEN_OPPONENTS,
            "games": len(games),
            "decisions": len(decisions),
            "complete": True,
        },
        "terminal": {
            "margin": summary(row["margin"] for row in games),
            "wood_edge": summary(row["wood_edge"] for row in games),
            "turn": summary(row["terminal_turn"] for row in games),
            "workers": counts_and_rates(row["workers"] for row in games),
        },
        "coverage": {
            "decisions_per_game": summary(decision_counts.values()),
            "roles": roles,
            "verbs": counts_and_rates(row["resident_verb"] for row in decisions),
            "worker_count_at_decision": counts_and_rates(
                row["worker_count"] for row in decisions
            ),
            "worker_specs": counts_and_rates(
                f"{row['ms']}/{row['cc']}/{row['hp']}/{row['chop']}"
                for row in decisions
            ),
            "opponent_decisions": counts_and_rates(
                row["opponent"] for row in decisions
            ),
            "unique_state_fingerprints": len(
                {row["state_fingerprint"] for row in decisions}
            ),
            "unique_state_unit_pairs": len(
                {(row["state_fingerprint"], row["unit_id"]) for row in decisions}
            ),
            "unique_local_signatures": len(local_signatures),
            "local_signature_unique_rate": len(local_signatures) / len(decisions),
        },
        "intent": {
            "consecutive_decisions": len(consecutive),
            "exact_command_persistence_rate": statistics.mean(
                row["exact_persistent"] for row in consecutive
            ),
            "verb_persistence_rate": statistics.mean(
                row["verb_persistent"] for row in consecutive
            ),
            "target_eligible_decisions": len(target_eligible),
            "target_persistence_rate": target_persistence_rate,
            "move_target_eligible_decisions": len(move_target_eligible),
            "move_target_persistence_rate": (
                statistics.mean(row["target_persistent"] for row in move_target_eligible)
                if move_target_eligible
                else None
            ),
            "intent_age": summary(row["intent_age"] for row in decisions),
            "intent_age_p95_nearest_rank": nearest_rank(
                (row["intent_age"] for row in decisions), 0.95
            ),
            "multiworker_decisions": len(multiworker),
            "multiworker_rate": multiworker_rate,
            "paired_target_collision_rate_with_multiworker": statistics.mean(
                row["paired_target_collision"] for row in multiworker
            ),
        },
        "action_space": {
            "resident_directly_decodable_rate": direct_rate,
            "poi_move_targets": summary(row["poi_move_targets"] for row in decisions),
            "poi_move_targets_p95_nearest_rank": nearest_rank(
                (row["poi_move_targets"] for row in decisions), 0.95
            ),
            "local_productive_actions": summary(
                row["local_productive_actions"] for row in decisions
            ),
            "local_productive_available_rate": local_available_rate,
            "residual_options": summary(row["residual_options"] for row in decisions),
            "residual_options_p95_nearest_rank": option_p95,
        },
        "descriptive_d11_shadow": {
            "exact_agreement_rate": actor_exact,
            "verb_agreement_rate": actor_verb,
            "warning": (
                "D11 is closed and these rates cannot define the new policy or a gate"
            ),
        },
        "interface_selection": {
            "selected": (
                "spatial_keep_plus_action"
                if spatial_interface
                else "binary_keep_or_generated_alternative"
            ),
            "spatial_gate": {
                "direct_decodability_at_least_95_percent": direct_rate >= 0.95,
                "residual_options_p95_at_most_64": option_p95 <= 64,
            },
            "include_previous_resident_intent": include_previous_intent,
            "include_other_worker_intent": include_other_worker_intent,
            "retain_point_of_interest_moves_due_to_sparse_local_actions": retain_poi_moves,
            "rules": {
                "previous_intent_threshold": 0.20,
                "other_worker_threshold": 0.10,
                "sparse_local_action_threshold": 0.20,
            },
            "authorization": (
                "environment construction and smoke testing only; no candidate, "
                "submission, or Arena activity"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("games", type=Path)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    games = read_tsv(args.games, {"opponent", "policy", "layer"})
    decisions = read_tsv(args.decisions, DECISION_STRINGS)
    result = analyze(games, decisions, args.games, args.decisions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "design": result["design"],
                "intent": result["intent"],
                "action_space": result["action_space"],
                "interface_selection": result["interface_selection"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

