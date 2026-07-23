#!/usr/bin/env python3
"""Apply the preregistered D21 PPO pilot promotion gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level2_env import level2_recipe  # noqa: E402
from cgauto.rl_level6_env import (  # noqa: E402
    LEVEL6_OPPONENT_NAMES,
    aggregate,
    level6_opponent,
)
from cgauto.train_d21_competitive_ppo import (  # noqa: E402
    FROZEN,
    INITIAL_CHECKPOINT_SHA256,
)


VALIDATION_BASE = 8_100_000
VALIDATION_EPISODES = 960
VALIDATION_STOP = VALIDATION_BASE + VALIDATION_EPISODES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_evaluation(payload: dict, label: str) -> None:
    if (
        payload.get("policy") != "actor"
        or payload.get("seed_base") != VALIDATION_BASE
        or payload.get("seed_stop_exclusive") != VALIDATION_STOP
        or payload.get("episodes") != VALIDATION_EPISODES
        or payload.get("num_envs") != 100
        or payload.get("max_turns") != 300
    ):
        raise ValueError(f"{label} does not use the exact D21 validation design")
    rows = payload.get("rows", [])
    if [row.get("seed") for row in rows] != list(
        range(VALIDATION_BASE, VALIDATION_STOP)
    ):
        raise ValueError(f"{label} does not cover the exact reserved seed interval")
    for row in rows:
        recipe_id, target = level2_recipe(row["seed"])
        opponent_id, opponent = level6_opponent(row["seed"])
        if (
            row["recipe_id"] != recipe_id
            or tuple(row["target"]) != target
            or row["opponent_id"] != opponent_id
            or row["opponent"] != opponent
        ):
            raise ValueError(f"{label} assignment mismatch at seed {row['seed']}")
    if aggregate(rows) != payload.get("aggregate"):
        raise ValueError(f"{label} aggregate does not reproduce from rows")


def finite_tree(value: object) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(child) for child in value)
    return True


def model_weight_drift(initial_checkpoint: Path, final_checkpoint: Path) -> dict:
    """Describe cumulative parameter movement; this is diagnostic, not a gate."""

    import torch

    initial = torch.load(initial_checkpoint, map_location="cpu", weights_only=False)[
        "model"
    ]
    final = torch.load(final_checkpoint, map_location="cpu", weights_only=False)["model"]
    if initial.keys() != final.keys():
        raise ValueError("initial/final model key mismatch")
    accumulators: dict[str, list[float | int]] = {}
    for name, initial_tensor in initial.items():
        group = name.split(".", 1)[0]
        base_squared, delta_squared, parameters = accumulators.setdefault(
            group, [0.0, 0.0, 0]
        )
        initial_float = initial_tensor.float()
        delta = final[name].float() - initial_float
        accumulators[group] = [
            float(base_squared) + float(initial_float.square().sum()),
            float(delta_squared) + float(delta.square().sum()),
            int(parameters) + initial_tensor.numel(),
        ]
    by_group = {}
    for group, (base_squared, delta_squared, parameters) in accumulators.items():
        base_l2 = math.sqrt(float(base_squared))
        delta_l2 = math.sqrt(float(delta_squared))
        by_group[group] = {
            "parameters": int(parameters),
            "initial_l2": base_l2,
            "delta_l2": delta_l2,
            "relative_delta_l2": delta_l2 / base_l2 if base_l2 else None,
        }
    total_base = sum(float(values[0]) for values in accumulators.values())
    total_delta = sum(float(values[1]) for values in accumulators.values())
    return {
        "overall_relative_delta_l2": math.sqrt(total_delta / total_base),
        "by_group": by_group,
    }


def validate_training(training: dict) -> None:
    config = training.get("config", {})
    for key, value in FROZEN.items():
        if config.get(key) != value:
            raise ValueError(f"training config drift for {key}")
    if config.get("initial_checkpoint_sha256") != INITIAL_CHECKPOINT_SHA256:
        raise ValueError("training initialization hash mismatch")


def analyze(
    initial: dict,
    final: dict,
    training: dict,
    *,
    checkpoint_integrity: bool = True,
) -> dict:
    validate_evaluation(initial, "unchanged D11 baseline")
    validate_evaluation(final, "D21 final actor")
    validate_training(training)
    if initial.get("checkpoint_sha256") != INITIAL_CHECKPOINT_SHA256:
        raise ValueError("validation baseline is not the accepted D11 checkpoint")

    initial_rows = {row["seed"]: row for row in initial["rows"]}
    final_rows = {row["seed"]: row for row in final["rows"]}
    paired_deltas = [
        final_rows[seed]["margin"] - initial_rows[seed]["margin"]
        for seed in range(VALIDATION_BASE, VALIDATION_STOP)
    ]
    initial_margin = initial["aggregate"]["margin"]["mean"]
    final_margin = final["aggregate"]["margin"]["mean"]
    opponent_deltas = {
        opponent: (
            final["aggregate"]["by_opponent"][opponent]["margin"]["mean"]
            - initial["aggregate"]["by_opponent"][opponent]["margin"]["mean"]
        )
        for opponent in LEVEL6_OPPONENT_NAMES
    }
    opponent_score_decomposition = {
        opponent: {
            "own_score_delta": (
                final["aggregate"]["by_opponent"][opponent]["own_score"]["mean"]
                - initial["aggregate"]["by_opponent"][opponent]["own_score"]["mean"]
            ),
            "opponent_score_delta": (
                final["aggregate"]["by_opponent"][opponent]["opponent_score"][
                    "mean"
                ]
                - initial["aggregate"]["by_opponent"][opponent]["opponent_score"][
                    "mean"
                ]
            ),
        }
        for opponent in LEVEL6_OPPONENT_NAMES
    }
    recipe_deltas = {
        recipe_id: (
            final["aggregate"]["by_recipe"][recipe_id]["margin"]["mean"]
            - initial["aggregate"]["by_recipe"][recipe_id]["margin"]["mean"]
        )
        for recipe_id in sorted(initial["aggregate"]["by_recipe"], key=int)
    }
    improved_opponents = [
        opponent for opponent, delta in opponent_deltas.items() if delta > 0
    ]
    logs = training.get("logs", [])
    exact_training = (
        training.get("global_step") == FROZEN["total_transitions"]
        and training.get("updates_completed") == 100
        and len(logs) == 100
        and [row.get("global_step") for row in logs]
        == list(range(10_000, FROZEN["total_transitions"] + 1, 10_000))
        and training.get("config", {}).get("intermediate_evaluations") == 0
    )
    finite_and_legal = (
        finite_tree(logs)
        and finite_tree(final["aggregate"])
        and training.get("illegal_actor_actions") == 0
        and final.get("illegal_selected_actions") == 0
        and final["aggregate"]["terminal_turn_min"] == 300
        and final["aggregate"]["terminal_turn_max"] == 300
        and final["aggregate"]["maximum_return_margin_error"] <= 1e-4
        and checkpoint_integrity
    )
    paired_std = float(np.std(paired_deltas, ddof=1))
    paired_standard_error = paired_std / math.sqrt(len(paired_deltas))
    paired_mean = float(np.mean(paired_deltas))
    quantiles = np.quantile(paired_deltas, [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95])
    gates = {
        "exact_frozen_1m_training_without_intermediate_validation": exact_training,
        "mean_margin_gain_at_least_5": final_margin - initial_margin >= 5,
        "at_least_four_of_six_opponent_means_improve": len(improved_opponents) >= 4,
        "no_opponent_mean_regression_below_minus_15": min(opponent_deltas.values())
        >= -15,
        "final_training_completion_at_least_90_percent": final["aggregate"][
            "training_completion_rate"
        ]
        >= 0.90,
        "final_crop_creation_at_least_70_percent": final["aggregate"][
            "crop_creation_rate"
        ]
        >= 0.70,
        "finite_legal_and_checkpoint_integrity": finite_and_legal,
    }
    pilot_pass = all(gates.values())
    return {
        "schema": 1,
        "scope": (
            "D21 frozen local PPO pilot gate; pass authorizes only exact-engine "
            "paired qualification, not a candidate, submission, or Arena"
        ),
        "design": {
            "validation_seed_base": VALIDATION_BASE,
            "validation_seed_stop_exclusive": VALIDATION_STOP,
            "validation_episodes": VALIDATION_EPISODES,
            "training_transitions": training.get("global_step"),
            "intermediate_evaluations": training.get("config", {}).get(
                "intermediate_evaluations"
            ),
        },
        "metrics": {
            "mean_margin": {"initial_d11": initial_margin, "final_d21": final_margin},
            "mean_margin_gain": final_margin - initial_margin,
            "mean_own_score_delta": (
                final["aggregate"]["own_score"]["mean"]
                - initial["aggregate"]["own_score"]["mean"]
            ),
            "mean_opponent_score_delta": (
                final["aggregate"]["opponent_score"]["mean"]
                - initial["aggregate"]["opponent_score"]["mean"]
            ),
            "paired_margin_delta": {
                "mean": paired_mean,
                "median": float(np.median(paired_deltas)),
                "standard_deviation": paired_std,
                "standard_error": paired_standard_error,
                "normal_approximation_95_percent_interval": [
                    paired_mean - 1.96 * paired_standard_error,
                    paired_mean + 1.96 * paired_standard_error,
                ],
                "minimum": float(np.min(paired_deltas)),
                "maximum": float(np.max(paired_deltas)),
                "quantiles": {
                    "q05": float(quantiles[0]),
                    "q10": float(quantiles[1]),
                    "q25": float(quantiles[2]),
                    "q50": float(quantiles[3]),
                    "q75": float(quantiles[4]),
                    "q90": float(quantiles[5]),
                    "q95": float(quantiles[6]),
                },
                "improved_seeds": sum(delta > 0 for delta in paired_deltas),
                "tied_seeds": sum(delta == 0 for delta in paired_deltas),
                "regressed_seeds": sum(delta < 0 for delta in paired_deltas),
                "large_improvements_at_least_50": sum(
                    delta >= 50 for delta in paired_deltas
                ),
                "large_regressions_at_most_minus_50": sum(
                    delta <= -50 for delta in paired_deltas
                ),
            },
            "catastrophic_margin_at_most_minus_100": {
                "initial_d11": sum(row["margin"] <= -100 for row in initial["rows"]),
                "final_d21": sum(row["margin"] <= -100 for row in final["rows"]),
            },
            "opponent_mean_margin_delta": opponent_deltas,
            "opponent_score_decomposition": opponent_score_decomposition,
            "recipe_mean_margin_delta": recipe_deltas,
            "improved_opponents": improved_opponents,
            "improved_opponent_count": len(improved_opponents),
            "worst_opponent_mean_delta": min(opponent_deltas.values()),
            "final_win_rate": final["aggregate"]["win_rate"],
            "final_training_completion_rate": final["aggregate"][
                "training_completion_rate"
            ],
            "final_crop_creation_rate": final["aggregate"]["crop_creation_rate"],
            "final_renewable_harvest_rate": final["aggregate"][
                "renewable_harvest_rate"
            ],
            "training_illegal_actor_actions": training.get("illegal_actor_actions"),
            "final_illegal_selected_actions": final.get("illegal_selected_actions"),
            "teacher_auxiliary": training.get("teacher_auxiliary"),
        },
        "gates": gates,
        "pilot_pass": pilot_pass,
        "authorization": (
            "run exact-engine paired qualification against resident and strategic panel"
            if pilot_pass
            else "close this D21 pilot; do not qualify or promote the checkpoint"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("initial", type=Path)
    parser.add_argument("final", type=Path)
    parser.add_argument("training", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--protocol", type=Path)
    args = parser.parse_args()
    initial = json.loads(args.initial.read_text())
    final = json.loads(args.final.read_text())
    training = json.loads(args.training.read_text())
    checkpoint_path = Path(training["checkpoint"])
    initial_checkpoint_path = Path(training["config"]["initial_checkpoint"])
    checkpoint_integrity = (
        checkpoint_path.exists()
        and initial_checkpoint_path.exists()
        and sha256(initial_checkpoint_path) == INITIAL_CHECKPOINT_SHA256
        and sha256(checkpoint_path) == training.get("checkpoint_sha256")
        and final.get("checkpoint_sha256") == training.get("checkpoint_sha256")
    )
    result = analyze(
        initial,
        final,
        training,
        checkpoint_integrity=checkpoint_integrity,
    )
    result["metrics"]["model_weight_drift"] = model_weight_drift(
        initial_checkpoint_path, checkpoint_path
    )
    sources = {
        "initial": args.initial,
        "final": args.final,
        "training": args.training,
        "initial_checkpoint": initial_checkpoint_path,
        "checkpoint": checkpoint_path,
    }
    result["source"] = {
        "paths": {label: str(path) for label, path in sources.items()},
        "sha256": {label: sha256(path) for label, path in sources.items()},
        "analyzer": str(Path(__file__).relative_to(REPO)),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    if args.protocol is not None:
        result["source"]["protocol"] = str(args.protocol)
        result["source"]["protocol_sha256"] = sha256(args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "pilot_pass": result["pilot_pass"],
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
