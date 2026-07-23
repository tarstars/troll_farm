#!/usr/bin/env python3
"""Qualify KEEP parity, random causality, masks, and throughput for D14."""

from __future__ import annotations

import argparse
from collections import defaultdict
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
from cgauto.rl_resident_residual_env import OPPONENTS  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_reference(paths: list[Path]) -> dict[tuple[int, int, str], dict]:
    rows = {}
    numeric = {
        "seed",
        "seat",
        "margin",
        "wood_edge",
        "terminal_turn",
        "workers",
        "opponent_workers",
    }
    for path in paths:
        with path.open(newline="") as handle:
            source = csv.DictReader(handle, delimiter="\t")
            for raw in source:
                if raw["policy"] != "resident":
                    continue
                row = dict(raw)
                for field in numeric:
                    row[field] = int(row[field])
                if not 0 <= row["seed"] < 20:
                    continue
                key = (row["seed"], row["seat"], row["opponent"])
                if key in rows:
                    raise ValueError(f"duplicate resident reference cell {key}")
                rows[key] = row
    if len(rows) != 240:
        raise ValueError(f"expected 240 resident reference rows, got {len(rows)}")
    return rows


def validate_payload(payload: dict, policy: str) -> None:
    if payload.get("policy") != policy:
        raise ValueError(f"expected {policy} payload")
    rows = payload.get("rows") or []
    if len(rows) != 240 or {row["scenario"] for row in rows} != set(range(240)):
        raise ValueError(f"{policy} payload is not scenarios 0--239")
    for row in rows:
        scenario = row["scenario"]
        if (
            row["map_seed"] != scenario // 12
            or row["seat"] != (scenario // 6) % 2
            or row["opponent"] != OPPONENTS[scenario % 6]
        ):
            raise ValueError(f"scenario mapping mismatch at {scenario}")


def map_means(rows: list[dict], field: str) -> dict[int, float]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["map_seed"]].append(row[field])
    return {seed: statistics.mean(values) for seed, values in grouped.items()}


def analyze(
    keep: dict,
    random: dict,
    reference: dict[tuple[int, int, str], dict],
    keep_path: Path,
    random_path: Path,
    reference_paths: list[Path],
) -> dict:
    validate_payload(keep, "keep")
    validate_payload(random, "random")
    keep_by_scenario = {row["scenario"]: row for row in keep["rows"]}
    random_by_scenario = {row["scenario"]: row for row in random["rows"]}
    parity_fields = {
        "margin": "margin",
        "wood_edge": "wood_edge",
        "turn": "terminal_turn",
        "workers": "workers",
        "opponent_workers": "opponent_workers",
    }
    mismatches = []
    for scenario, row in keep_by_scenario.items():
        key = (row["map_seed"], row["seat"], row["opponent"])
        expected = reference[key]
        unequal = {
            field: {"environment": row[field], "reference": expected[reference_field]}
            for field, reference_field in parity_fields.items()
            if row[field] != expected[reference_field]
        }
        if unequal:
            mismatches.append({"scenario": scenario, "differences": unequal})

    return_errors = [
        row["scenario"]
        for row in keep["rows"]
        if not math.isfinite(row["return"])
        or abs(row["return"] - row["margin"] / 100.0) > 1e-4
    ]
    changed = [
        scenario
        for scenario in range(240)
        if random_by_scenario[scenario]["margin"]
        != keep_by_scenario[scenario]["margin"]
    ]
    keep_maps = map_means(keep["rows"], "margin")
    random_maps = map_means(random["rows"], "margin")
    map_deltas = [random_maps[seed] - keep_maps[seed] for seed in range(20)]
    keep_map_mean = statistics.mean(keep_maps.values())
    random_map_mean = statistics.mean(random_maps.values())

    gates = {
        "keep_reference_parity_240_of_240": not mismatches,
        "keep_zero_overrides": all(row["overrides"] == 0 for row in keep["rows"]),
        "keep_finite_telescoping_returns": not return_errors,
        "keep_present_and_mask_between_1_and_7": (
            keep["keep_missing_observations"] == 0
            and random["keep_missing_observations"] == 0
            and keep["mask_legal_min"] >= 1
            and random["mask_legal_min"] >= 1
            and keep["mask_legal_max"] <= 7
            and random["mask_legal_max"] <= 7
        ),
        "no_selected_actions_rejected": (
            keep["rejected_actions"] == 0 and random["rejected_actions"] == 0
        ),
        "random_complete_240_of_240": len(random["rows"]) == 240,
        "random_override_episode_rate_at_least_95_percent": (
            random["override_episode_rate"] >= 0.95
        ),
        "random_changes_at_least_half_of_terminal_margins": len(changed) >= 120,
        "random_map_mean_worse_than_keep": random_map_mean < keep_map_mean,
        "throughput_at_least_500_decisions_per_second": min(
            keep["transitions_per_second"], random["transitions_per_second"]
        )
        >= 500,
    }
    qualified = all(gates.values())
    return {
        "schema": 1,
        "scope": (
            "D14 resident residual environment smoke on consumed development maps; "
            "not policy selection or Arena authorization"
        ),
        "source": {
            "keep": str(keep_path),
            "keep_sha256": sha256(keep_path),
            "random": str(random_path),
            "random_sha256": sha256(random_path),
            "references": [str(path) for path in reference_paths],
            "reference_sha256": {str(path): sha256(path) for path in reference_paths},
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "scenarios": 240,
            "maps": 20,
            "seats": [0, 1],
            "opponents": list(OPPONENTS),
            "complete": True,
        },
        "keep": {
            "map_balanced_margin": keep_map_mean,
            "mean_wood_edge": keep["mean_wood_edge"],
            "transitions": keep["transitions"],
            "transitions_per_second": keep["transitions_per_second"],
            "mask_legal_min": keep["mask_legal_min"],
            "mask_legal_max": keep["mask_legal_max"],
            "parity_matches": 240 - len(mismatches),
            "parity_mismatches": mismatches,
            "return_errors": return_errors,
        },
        "random": {
            "map_balanced_margin": random_map_mean,
            "mean_wood_edge": random["mean_wood_edge"],
            "margin_delta_vs_keep": summary(map_deltas),
            "changed_terminal_margins": len(changed),
            "override_episode_rate": random["override_episode_rate"],
            "residual_attempt_episode_rate": random[
                "residual_attempt_episode_rate"
            ],
            "rejected_actions": random["rejected_actions"],
            "transitions": random["transitions"],
            "transitions_per_second": random["transitions_per_second"],
            "mask_legal_min": random["mask_legal_min"],
            "mask_legal_max": random["mask_legal_max"],
        },
        "qualification": {
            "gates": gates,
            "qualified_for_short_ppo_signal_run": qualified,
            "authorization": (
                "short PPO signal run only; no candidate, prospective, submission, "
                "or Arena activity"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("keep", type=Path)
    parser.add_argument("random", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("references", nargs="+", type=Path)
    args = parser.parse_args()
    keep = json.loads(args.keep.read_text())
    random = json.loads(args.random.read_text())
    reference = read_reference(args.references)
    result = analyze(
        keep,
        random,
        reference,
        args.keep,
        args.random,
        args.references,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "keep": result["keep"],
        "random": result["random"],
        "qualification": result["qualification"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

