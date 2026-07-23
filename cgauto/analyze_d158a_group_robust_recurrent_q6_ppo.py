#!/usr/bin/env python3
"""Select and, when authorized, confirm D158a's frozen objective variants."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import torch

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto import train_d108a_recurrent_q6_ppo as d108  # noqa: E402
from cgauto.train_d158a_group_robust_recurrent_q6_ppo import (  # noqa: E402
    BASE,
    FROZEN,
    LOCK,
    OBJECTIVES,
    PROTOCOL,
    VARIANT_ORDER,
    output_paths,
    sha256,
    validate_lock,
)


OUTPUT = BASE / "d158a-group-robust-recurrent-q6-ppo-result.json"
CONFIRMATION_A = BASE / "d158a-group-robust-recurrent-q6-ppo-confirmation-a.tsv"
CONFIRMATION_B = BASE / "d158a-group-robust-recurrent-q6-ppo-confirmation-b.tsv"


def policy_rows_sha(path: Path, policies: set[str]) -> str:
    digest = hashlib.sha256()
    with path.open(newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            if row["policy"] not in policies:
                continue
            digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def candidate_key(candidate: dict) -> tuple:
    final = candidate["evaluation"]["summaries"]["final"]
    return (
        final["worst_family"],
        final["mean_margin_delta"],
        final["mean_own_score_delta"],
        final["strict_improvement_rate"],
        -VARIANT_ORDER.index(candidate["variant"]),
    )


def select_candidate(candidates: list[dict]) -> dict | None:
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    return max(eligible, key=candidate_key) if eligible else None


def confirmation_gates(summaries: dict, repeat_exact: bool) -> dict:
    control = summaries["control"]
    final = summaries["final"]
    return {
        "mechanics": {
            "control_tasks_1024": control["tasks"] == 1_024,
            "final_tasks_1024": final["tasks"] == 1_024,
            "repeat_byte_exact": repeat_exact,
            "raw_reward_identity": max(
                summary["maximum_reward_identity_error"] for summary in summaries.values()
            ) < 1e-4,
            "zero_failures": all(
                value == 0 for value in final["mechanical_failures"].values()
            ),
        },
        "safety": {
            "crop_100pct": final["crop_rate"] == 1.0,
            "worker_three_within_5pp": final["worker_three_rate"]
            >= control["worker_three_rate"] - 0.05,
        },
        "value": {
            "mean_gain_at_least_2": final["mean_margin_delta"] >= 2.0,
            "strict_improvement_40pct": final["strict_improvement_rate"] >= 0.40,
            "six_positive_families": final["positive_families"] >= 6,
            "worst_family_at_least_minus3": final["worst_family"] >= -3.0,
            "own_nonnegative_or_opponent_nonpositive": final["mean_own_score_delta"] >= 0.0
            or final["mean_opponent_score_delta"] <= 0.0,
        },
    }


def load_candidates() -> tuple[list[dict], dict]:
    lock = validate_lock()
    candidates = []
    common_hashes: dict[str, set[str]] = {"control": set(), "initial": set()}
    trainer_hash = sha256(Path(__file__).with_name("train_d158a_group_robust_recurrent_q6_ppo.py"))
    for variant in VARIANT_ORDER:
        paths = output_paths(variant)
        result = json.loads(paths["result"].read_text())
        if result["schema"] != "troll-farm-d158a-group-robust-recurrent-q6-ppo-variant-v1":
            raise RuntimeError(f"D158a schema drift for {variant}")
        if result["variant"] != variant or result["objective"] != OBJECTIVES[variant]:
            raise RuntimeError(f"D158a variant/objective drift for {variant}")
        if result["config"] != FROZEN:
            raise RuntimeError(f"D158a config drift for {variant}")
        if result["inputs"]["trainer"] != trainer_hash:
            raise RuntimeError(f"D158a trainer hash drift for {variant}")
        for key in ("checkpoint", "evaluation_a", "evaluation_b"):
            if result["inputs"][key] != sha256(paths[key]):
                raise RuntimeError(f"D158a output hash drift for {variant}/{key}")
        if not result["evaluation"]["repeat_exact"]:
            raise RuntimeError(f"D158a evaluation repeat drift for {variant}")
        for policy in common_hashes:
            common_hashes[policy].add(policy_rows_sha(paths["evaluation_a"], {policy}))
        candidates.append(result)
    if any(len(values) != 1 for values in common_hashes.values()):
        raise RuntimeError("D158a common control/initial evaluation drift")
    return candidates, {
        "lock": lock,
        "common_policy_sha256": {
            policy: next(iter(values)) for policy, values in common_hashes.items()
        },
    }


def run_confirmation(selected: dict) -> dict:
    variant = selected["variant"]
    checkpoint_path = output_paths(variant)["checkpoint"]
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if checkpoint["variant"] != variant or checkpoint["config"] != FROZEN:
        raise RuntimeError("D158a selected checkpoint metadata drift")
    model = d108.RecurrentProposalActorCritic()
    model.load_state_dict(checkpoint["model"])
    confirmation_config = {
        **FROZEN,
        "evaluation_seed_base": FROZEN["confirmation_seed_base"],
        "evaluation_maps": FROZEN["confirmation_maps"],
    }
    d108.FROZEN = confirmation_config
    rows_a = [*d108.evaluate_policy("control", None), *d108.evaluate_policy("final", model)]
    rows_b = [*d108.evaluate_policy("control", None), *d108.evaluate_policy("final", model)]
    d108.write_evaluation(CONFIRMATION_A, rows_a)
    d108.write_evaluation(CONFIRMATION_B, rows_b)
    repeat_exact = CONFIRMATION_A.read_bytes() == CONFIRMATION_B.read_bytes()
    summaries = {
        policy: d108.evaluation_summary(rows_a, policy) for policy in ("control", "final")
    }
    gates = confirmation_gates(summaries, repeat_exact)
    passes = {name: all(values.values()) for name, values in gates.items()}
    return {
        "variant": variant,
        "config": confirmation_config,
        "evaluation_a_sha256": sha256(CONFIRMATION_A),
        "evaluation_b_sha256": sha256(CONFIRMATION_B),
        "repeat_exact": repeat_exact,
        "summaries": summaries,
        "gates": {**gates, "passes": passes},
        "pass": all(passes.values()),
    }


def compact_candidate(candidate: dict) -> dict:
    return {
        "variant": candidate["variant"],
        "objective": candidate["objective"],
        "eligible": candidate["eligible"],
        "passes": candidate["gates"]["passes"],
        "training": {
            "wall_seconds": candidate["training"]["wall_seconds"],
            "effective_cpu_cores": candidate["training"]["effective_cpu_cores"],
            "transitions_per_second": candidate["training"]["transitions_per_second"],
            "mean_margin_delta": candidate["training"]["episodes"]["mean_margin_delta"],
            "mean_own_score_delta": candidate["training"]["episodes"]["mean_own_score_delta"],
            "mean_objective_return": candidate["training"]["episodes"]["mean_objective_return"],
            "final_family_weights": candidate["training"]["final_family_weights"],
        },
        "probe": candidate["probe"],
        "development": candidate["evaluation"]["summaries"]["final"],
        "result_sha256": sha256(output_paths(candidate["variant"])["result"]),
        "checkpoint_sha256": candidate["inputs"]["checkpoint"],
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    candidates, integrity = load_candidates()
    selected = select_candidate(candidates)
    for path in (CONFIRMATION_A, CONFIRMATION_B):
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    confirmation = None
    if selected is not None:
        confirmation = run_confirmation(selected)
    result = {
        "schema": "troll-farm-d158a-group-robust-recurrent-q6-ppo-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "protocol": sha256(PROTOCOL),
        "lock": sha256(LOCK),
        "integrity": integrity,
        "candidates": [compact_candidate(candidate) for candidate in candidates],
        "eligible_variants": [
            candidate["variant"] for candidate in candidates if candidate["eligible"]
        ],
        "selected_variant": None if selected is None else selected["variant"],
        "confirmation": confirmation,
        "pass": bool(confirmation and confirmation["pass"]),
        "decision": (
            "open_source_reconstruction"
            if confirmation and confirmation["pass"]
            else "close_group_robust_recurrent_q6"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "eligible_variants": result["eligible_variants"],
                "selected_variant": result["selected_variant"],
                "pass": result["pass"],
                "decision": result["decision"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    os.environ["RAYON_NUM_THREADS"] = "20"
    torch.set_num_threads(20)
    torch.set_num_interop_threads(4)
    raise SystemExit(main())

