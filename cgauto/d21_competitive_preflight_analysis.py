#!/usr/bin/env python3
"""Apply the frozen D21 full-length competitive preflight gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level2_env import level2_recipe  # noqa: E402
from cgauto.rl_level6_env import aggregate, level6_opponent  # noqa: E402


SEED_BASE = 8_000_000
EPISODES = 480
SEED_STOP = SEED_BASE + EPISODES
CHECKPOINT_SHA256 = "44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_evaluation(payload: dict) -> bytes:
    return json.dumps(
        {"aggregate": payload["aggregate"], "rows": payload["rows"]},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def validate_payload(payload: dict, policy: str, label: str) -> None:
    if payload.get("policy") != policy:
        raise ValueError(f"{label} policy mismatch")
    if (
        payload.get("seed_base") != SEED_BASE
        or payload.get("seed_stop_exclusive") != SEED_STOP
        or payload.get("episodes") != EPISODES
        or payload.get("num_envs") != 80
        or payload.get("max_turns") != 300
    ):
        raise ValueError(f"{label} does not use the frozen D21 block")
    if policy == "random" and payload.get("random_seed") != 2101:
        raise ValueError("random control RNG seed mismatch")
    if policy == "actor" and payload.get("checkpoint_sha256") != CHECKPOINT_SHA256:
        raise ValueError("actor checkpoint hash mismatch")
    rows = payload.get("rows", [])
    if [row.get("seed") for row in rows] != list(range(SEED_BASE, SEED_STOP)):
        raise ValueError(f"{label} rows do not exactly cover the frozen seed interval")
    for row in rows:
        recipe_id, target = level2_recipe(row["seed"])
        opponent_id, opponent = level6_opponent(row["seed"])
        if (
            row["recipe_id"] != recipe_id
            or tuple(row["target"]) != target
            or row["opponent_id"] != opponent_id
            or row["opponent"] != opponent
        ):
            raise ValueError(f"{label} deterministic assignment mismatch at {row['seed']}")
    if aggregate(rows) != payload.get("aggregate"):
        raise ValueError(f"{label} aggregate does not reproduce from episode rows")


def analyze(
    teacher_a: dict,
    teacher_b: dict,
    random_control: dict,
    actor: dict,
    *,
    paths: dict[str, Path] | None = None,
    protocol_path: Path | None = None,
) -> dict:
    payloads = {
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "random": random_control,
        "actor": actor,
    }
    validate_payload(teacher_a, "teacher", "teacher A")
    validate_payload(teacher_b, "teacher", "teacher B")
    validate_payload(random_control, "random", "random")
    validate_payload(actor, "actor", "actor")

    main_controls = (teacher_a, random_control, actor)
    all_rows = [row for payload in main_controls for row in payload["rows"]]
    actor_aggregate = actor["aggregate"]
    random_margin = random_control["aggregate"]["margin"]["mean"]
    teacher_margin = teacher_a["aggregate"]["margin"]["mean"]
    actor_margin = actor_aggregate["margin"]["mean"]
    opponent_means = {
        name: bucket["margin"]["mean"]
        for name, bucket in actor_aggregate["by_opponent"].items()
    }
    finite_opponent_means = [
        value for value in opponent_means.values() if math.isfinite(value)
    ]
    gates = {
        "all_1440_complete_at_turn_300": (
            len(all_rows) == 3 * EPISODES
            and all(row["turn"] == 300 for row in all_rows)
        ),
        "no_illegal_selected_action": all(
            payload["illegal_selected_actions"] == 0 for payload in payloads.values()
        ),
        "actor_opponent_and_recipe_coverage_at_least_40": (
            actor_aggregate["minimum_opponent_episodes"] >= 40
            and actor_aggregate["minimum_recipe_episodes"] >= 40
        ),
        "return_identity_within_1e_4_margin_points": all(
            row["return_margin_error"] <= 1e-4
            for payload in payloads.values()
            for row in payload["rows"]
        ),
        "teacher_repeat_identical": (
            canonical_evaluation(teacher_a) == canonical_evaluation(teacher_b)
        ),
        "teacher_beats_random_by_20_mean_margin": teacher_margin - random_margin >= 20,
        "actor_beats_random_by_20_mean_margin": actor_margin - random_margin >= 20,
        "actor_training_completion_at_least_90_percent": (
            actor_aggregate["training_completion_rate"] >= 0.90
        ),
        "actor_crop_creation_at_least_70_percent": (
            actor_aggregate["crop_creation_rate"] >= 0.70
        ),
        "actor_has_wins_and_losses": (
            actor_aggregate["wins"] > 0 and actor_aggregate["losses"] > 0
        ),
        "at_least_four_finite_distinct_actor_opponent_means": (
            len({round(value, 12) for value in finite_opponent_means}) >= 4
        ),
    }
    result = {
        "schema": 1,
        "scope": (
            "D21 frozen full-length competitive preflight; passing opens only the "
            "preregistered local 1M-transition PPO pilot"
        ),
        "design": {
            "seed_base": SEED_BASE,
            "seed_stop_exclusive": SEED_STOP,
            "episodes_per_policy": EPISODES,
            "main_control_episodes": len(all_rows),
            "teacher_repeat_episodes": len(teacher_b["rows"]),
            "max_turns": 300,
        },
        "metrics": {
            "mean_margin": {
                "teacher": teacher_margin,
                "random": random_margin,
                "actor": actor_margin,
            },
            "mean_margin_advantage_over_random": {
                "teacher": teacher_margin - random_margin,
                "actor": actor_margin - random_margin,
            },
            "actor_win_rate": actor_aggregate["win_rate"],
            "actor_training_completion_rate": actor_aggregate[
                "training_completion_rate"
            ],
            "actor_crop_creation_rate": actor_aggregate["crop_creation_rate"],
            "actor_renewable_harvest_rate": actor_aggregate[
                "renewable_harvest_rate"
            ],
            "actor_opponent_mean_margin": opponent_means,
            "actor_minimum_opponent_episodes": actor_aggregate[
                "minimum_opponent_episodes"
            ],
            "actor_minimum_recipe_episodes": actor_aggregate[
                "minimum_recipe_episodes"
            ],
            "maximum_return_margin_error": max(
                payload["aggregate"]["maximum_return_margin_error"]
                for payload in payloads.values()
            ),
            "illegal_selected_actions": {
                label: payload["illegal_selected_actions"]
                for label, payload in payloads.items()
            },
        },
        "gates": gates,
        "preflight_pass": all(gates.values()),
        "authorization": (
            "run the frozen local 1M-transition D21 PPO pilot only"
            if all(gates.values())
            else "close D21 Level-6 formulation before training"
        ),
    }
    if paths is not None:
        result["source"] = {
            "inputs": {label: str(path) for label, path in paths.items()},
            "input_sha256": {label: sha256(path) for label, path in paths.items()},
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        }
        if protocol_path is not None:
            result["source"]["protocol"] = str(protocol_path)
            result["source"]["protocol_sha256"] = sha256(protocol_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teacher_a", type=Path)
    parser.add_argument("teacher_b", type=Path)
    parser.add_argument("random", type=Path)
    parser.add_argument("actor", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--protocol", type=Path)
    args = parser.parse_args()
    paths = {
        "teacher_a": args.teacher_a,
        "teacher_b": args.teacher_b,
        "random": args.random,
        "actor": args.actor,
    }
    payloads = {label: json.loads(path.read_text()) for label, path in paths.items()}
    result = analyze(
        payloads["teacher_a"],
        payloads["teacher_b"],
        payloads["random"],
        payloads["actor"],
        paths=paths,
        protocol_path=args.protocol,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "preflight_pass": result["preflight_pass"],
                "metrics": result["metrics"],
                "failed_gates": [
                    name for name, passed in result["gates"].items() if not passed
                ],
                "authorization": result["authorization"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
