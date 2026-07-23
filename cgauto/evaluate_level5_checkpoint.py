#!/usr/bin/env python3
"""Evaluate one frozen spatial actor against an explicit Level-5 opponent mode."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import torch

from cgauto.train_level1_ppo import (
    SpatialActorCritic,
    evaluate,
    level5_mechanism_gate,
    paired_teacher_turn_delta,
    sha256,
)


def d11_final_functional_gate(payload: dict) -> bool:
    """Apply the functional portion of the frozen D11 final gate."""
    return bool(
        payload["success_rate"] >= 0.90
        and payload["nontrivial_success_rate"] >= 0.88
        and payload["recipe_success_floor"] >= 0.82
        and payload["height_success_floor"] >= 0.85
        and payload["created_crop_rate"] >= 0.90
        and payload["renewable_harvest_rate"] >= 0.95
        and payload["paired_teacher_median_turn_delta"] <= 30.0
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument(
        "--opponent-mode",
        choices=(
            "complete",
            "complete-recovery",
            "natural-forager",
            "natural-planter",
            "one-shot-reaper",
            "funded-pair",
            "funded-trio",
            "funded-trio-sustained",
            "funded-trio-sustained-180",
            "crop-first-funded-trio-sustained-180",
            "crop-first-funded-trio-repeated-pressure-180",
            "crop-first-funded-trio-repeated-pressure-reacquire-180",
        ),
        required=True,
    )
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--max-turns", type=int, default=240)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--teacher-baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.episodes <= 0 or args.num_envs <= 0:
        raise SystemExit("episodes and num-envs must be positive")
    if not args.checkpoint.exists():
        raise SystemExit(f"missing checkpoint {args.checkpoint}")
    if args.teacher_baseline is not None and not args.teacher_baseline.exists():
        raise SystemExit(f"missing teacher baseline {args.teacher_baseline}")

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    saved = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"])
    result = evaluate(
        model,
        seed_base=args.seed_base,
        episodes=args.episodes,
        num_envs=args.num_envs,
        curriculum_level=5,
        max_turns=args.max_turns,
        level5_opponent_mode=args.opponent_mode,
    )
    payload = asdict(result)
    rows = payload.pop("rows")
    payload["episodes_detail"] = rows
    payload["curriculum_level"] = 5
    payload["opponent_mode"] = args.opponent_mode
    payload["checkpoint"] = str(args.checkpoint)
    payload["checkpoint_sha256"] = sha256(args.checkpoint)
    payload["threads"] = args.threads

    nontrivial = [row for row in rows if row["initial_total_deficit"] > 0]
    payload["nontrivial_episodes"] = len(nontrivial)
    payload["nontrivial_successes"] = sum(row["success"] for row in nontrivial)
    payload["nontrivial_success_rate"] = (
        payload["nontrivial_successes"] / len(nontrivial) if nontrivial else None
    )
    payload["height_success_floor"] = min(
        bucket["success_rate"] for bucket in payload["by_height"].values()
    )
    payload["recipe_success_floor"] = min(
        bucket["success_rate"]
        for bucket in payload["by_recipe"].values()
        if bucket["episodes"]
    )
    payload["level5_mechanism_gate"] = level5_mechanism_gate(result)

    if args.teacher_baseline is not None:
        teacher = json.loads(args.teacher_baseline.read_text())
        payload["teacher_baseline"] = str(args.teacher_baseline)
        payload["teacher_baseline_sha256"] = sha256(args.teacher_baseline)
        payload["paired_teacher_median_turn_delta"] = paired_teacher_turn_delta(
            result, teacher
        )
        payload["d11_final_functional_gate"] = d11_final_functional_gate(payload)
        payload["d11_functional_and_mechanism_gate"] = bool(
            payload["d11_final_functional_gate"]
            and payload["level5_mechanism_gate"]
        )

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.write_text(rendered + "\n")
    print(
        json.dumps(
            {key: value for key, value in payload.items() if key != "episodes_detail"},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
