#!/usr/bin/env python3
"""Pair D15 learned residual evaluations with the exact all-KEEP baseline."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d11_recipe_catalog_analysis import summary  # noqa: E402
from cgauto.rl_resident_residual_env import OPPONENTS  # noqa: E402

EVAL_START = 240_000
EVAL_STOP = 240_240


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_rows(rows: list[dict], label: str) -> None:
    if len(rows) != 240 or {row["scenario"] for row in rows} != set(
        range(EVAL_START, EVAL_STOP)
    ):
        raise ValueError(f"{label} does not cover exact D15 evaluation scenarios")
    for row in rows:
        scenario = row["scenario"]
        if (
            row["map_seed"] != scenario // 12
            or row["seat"] != (scenario // 6) % 2
            or row["opponent"] != OPPONENTS[scenario % 6]
        ):
            raise ValueError(f"{label} scenario mapping mismatch at {scenario}")


def map_means(rows: list[dict], field: str) -> dict[int, float]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["map_seed"]].append(row[field])
    return {seed: statistics.mean(values) for seed, values in grouped.items()}


def analyze_run(payload: dict, baseline: dict) -> dict:
    rows = payload["evaluation"]["rows"]
    baseline_rows = baseline["rows"]
    validate_rows(rows, "learned evaluation")
    validate_rows(baseline_rows, "KEEP baseline")
    learned = {row["scenario"]: row for row in rows}
    keep = {row["scenario"]: row for row in baseline_rows}
    deltas = {
        scenario: learned[scenario]["margin"] - keep[scenario]["margin"]
        for scenario in range(EVAL_START, EVAL_STOP)
    }
    wood_deltas = {
        scenario: learned[scenario]["wood_edge"] - keep[scenario]["wood_edge"]
        for scenario in range(EVAL_START, EVAL_STOP)
    }
    map_delta_groups = defaultdict(list)
    for scenario, delta in deltas.items():
        map_delta_groups[learned[scenario]["map_seed"]].append(delta)
    map_deltas = {
        seed: statistics.mean(values) for seed, values in map_delta_groups.items()
    }
    opponent_deltas = {}
    for opponent in OPPONENTS:
        opponent_deltas[opponent] = statistics.mean(
            delta
            for scenario, delta in deltas.items()
            if learned[scenario]["opponent"] == opponent
        )
    changed = [scenario for scenario, delta in deltas.items() if delta != 0]
    changed_maps = {
        learned[scenario]["map_seed"] for scenario in changed
    }
    override_episodes = [row for row in rows if row["overrides"] > 0]
    keep_catastrophic = sum(row["margin"] <= -100 for row in baseline_rows)
    learned_catastrophic = sum(row["margin"] <= -100 for row in rows)
    cell_summary = summary(deltas.values())
    map_summary = summary(map_deltas.values())
    gates = {
        "complete_training_and_240_evaluations": (
            payload["config"]["total_transitions"] == 131_072
            and len(rows) == 240
        ),
        "override_episode_rate_at_least_5_percent": len(override_episodes) >= 12,
        "at_least_12_changed_terminal_margins": len(changed) >= 12,
        "map_mean_margin_delta_nonnegative": map_summary["mean"] >= 0,
        "worst_opponent_mean_delta_at_least_minus5": min(opponent_deltas.values()) >= -5,
        "worst_decile_cell_delta_at_least_minus20": cell_summary[
            "worst_decile_mean"
        ]
        >= -20,
        "catastrophic_count_increase_at_most_2": (
            learned_catastrophic - keep_catastrophic <= 2
        ),
    }
    signal_positive = all(gates.values())
    override_rate = len(override_episodes) / 240
    if signal_positive:
        classification = "useful_signal"
    elif override_rate < 0.05:
        classification = "collapse_to_keep"
    elif override_rate >= 0.50 and map_summary["mean"] < 0:
        classification = "unsafe_widespread_intervention"
    else:
        classification = "learned_but_unprofitable_sparse_intervention"
    return {
        "run_name": payload["config"].get("output_prefix"),
        "model_seed": payload["config"]["model_seed"],
        "keep_bias": payload["config"]["keep_bias"],
        "parameter_count": payload["config"]["parameter_count"],
        "training": {
            "transitions": payload["config"]["total_transitions"],
            "episodes": payload["training_episodes"],
            "wall_seconds": payload["wall_seconds"],
            "final_log": payload["logs"][-1],
        },
        "evaluation": {
            "learned_map_balanced_margin": statistics.mean(
                map_means(rows, "margin").values()
            ),
            "keep_map_balanced_margin": statistics.mean(
                map_means(baseline_rows, "margin").values()
            ),
            "map_margin_delta": map_summary,
            "cell_margin_delta": cell_summary,
            "cell_wood_delta": summary(wood_deltas.values()),
            "opponent_mean_margin_delta": opponent_deltas,
            "worst_opponent_mean_margin_delta": min(opponent_deltas.values()),
            "changed_terminal_margins": len(changed),
            "changed_maps": len(changed_maps),
            "override_episodes": len(override_episodes),
            "override_episode_rate": override_rate,
            "total_overrides": sum(row["overrides"] for row in rows),
            "mean_overrides_per_episode": statistics.mean(
                row["overrides"] for row in rows
            ),
            "keep_catastrophic_count": keep_catastrophic,
            "learned_catastrophic_count": learned_catastrophic,
            "catastrophic_count_delta": learned_catastrophic - keep_catastrophic,
            "rejected_actions": sum(row["rejected_actions"] for row in rows),
        },
        "gates": gates,
        "signal_positive": signal_positive,
        "classification": classification,
    }


def analyze(run_payloads: list[dict], baseline: dict, run_paths: list[Path], baseline_path: Path) -> dict:
    per_run = [analyze_run(payload, baseline) for payload in run_payloads]
    positive = [run["run_name"] for run in per_run if run["signal_positive"]]
    return {
        "schema": 1,
        "scope": (
            "D15 short resident-residual PPO learning-signal study on development "
            "scenario streams; no candidate or Arena authorization"
        ),
        "source": {
            "runs": [str(path) for path in run_paths],
            "run_sha256": {str(path): sha256(path) for path in run_paths},
            "keep_baseline": str(baseline_path),
            "keep_baseline_sha256": sha256(baseline_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "runs": len(per_run),
            "transitions_per_run": 131_072,
            "evaluation_scenarios": 240,
            "complete": True,
        },
        "per_run": per_run,
        "selection": {
            "signal_positive_runs": positive,
            "any_useful_signal": bool(positive),
            "authorization": (
                "positive runs may enter a larger local replication only; no candidate, "
                "submission, or Arena activity"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("runs", nargs="+", type=Path)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    payloads = [json.loads(path.read_text()) for path in args.runs]
    result = analyze(payloads, baseline, args.runs, args.baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "selection": result["selection"],
        "runs": [{
            "run": run["run_name"],
            "classification": run["classification"],
            "signal_positive": run["signal_positive"],
            "mean_delta": run["evaluation"]["map_margin_delta"]["mean"],
            "worst_opponent": run["evaluation"]["worst_opponent_mean_margin_delta"],
            "override_rate": run["evaluation"]["override_episode_rate"],
        } for run in result["per_run"]],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

