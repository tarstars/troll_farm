#!/usr/bin/env python3
"""Closed-loop preflight for the D41b exact-prior zero-residual actor."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import exact_prior_order, sha256
from cgauto.rl_macro_env import BRANCHES, MacroVecEnv, TASKS_PER_MAP


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41b-exact-prior-residual-preflight-protocol-2026-07-21.md"
TEACHER_BASELINE = ANALYSIS / "d41a-development-teacher-9711000-9711031.tsv"
KERNEL = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
DEFAULT_OUTPUT = ANALYSIS / "d41b-exact-prior-preflight-2026-07-21.json"
CELLS = 11 * 22
RESIDUAL_PARAMETERS = 44 * 16 + 16 + 16 + 1
COMPARISON_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "successful_trains",
    "own_created_crops",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "action_hash",
    "state_hash",
)


def read_baseline(path: Path) -> dict[tuple[int, int, str], dict]:
    with path.open(newline="") as source:
        raw = list(csv.DictReader(source, delimiter="\t"))
    output = {}
    for row in raw:
        if row["policy"] != "work_conserving":
            raise ValueError(f"unexpected baseline policy: {row['policy']}")
        converted = {
            "map_seed": int(row["map_seed"]),
            "seat": int(row["seat"]),
            "opponent": row["opponent"],
            **{field: int(row[field]) for field in COMPARISON_FIELDS},
        }
        key = (converted["map_seed"], converted["seat"], converted["opponent"])
        if key in output:
            raise ValueError(f"duplicate baseline task: {key}")
        output[key] = converted
    return output


def terminal_digest(rows: list[dict]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(
            (
                f"{row['task_index']}:{row['action_hash']}:{row['state_hash']}:"
                f"{row['own_score']}:{row['opponent_score']}\n"
            ).encode()
        )
    return digest.hexdigest()


def summarize(rows: list[dict]) -> dict:
    return {
        "episodes": len(rows),
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "mean_opponent_score": float(
            np.mean([row["opponent_score"] for row in rows])
        ),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "worker_two_rate": float(np.mean([row["own_workers"] >= 2 for row in rows])),
        "worker_three_rate": float(
            np.mean([row["own_workers"] >= 3 for row in rows])
        ),
        "crop_rate": float(
            np.mean([row["own_created_crops"] > 0 for row in rows])
        ),
        "invalid_direct_commands": sum(
            row["invalid_direct_commands"] for row in rows
        ),
        "provenance_failures": sum(row["provenance_failures"] for row in rows),
        "deposit_prediction_failures": sum(
            row["deposit_prediction_failures"] for row in rows
        ),
        "maximum_workers": max(row["own_workers"] for row in rows),
        "terminal_hash_sha256": terminal_digest(rows),
    }


def run_exact_prior(*, seed_base: int, maps: int, num_envs: int) -> dict:
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    branch_total: collections.Counter[int] = collections.Counter()
    branch_match: collections.Counter[int] = collections.Counter()
    zero_residual_matches = 0
    decisions = 0
    rounds = 0
    decision_digest = hashlib.sha256()
    started = time.perf_counter()

    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            rounds += 1
            if rounds > 20_000:
                raise RuntimeError("D41b decision loop")
            selected = np.empty(num_envs, dtype=np.int32)
            for slot in range(num_envs):
                count = int(env.counts[slot])
                actions = env.actions[slot, :count]
                order = exact_prior_order(
                    env.features[slot, :count], actions, int(env.branches[slot])
                )
                # With zero residual, logits are exactly -rank. Verify the actor
                # interface independently of taking order[0] directly.
                rank = np.empty(count, dtype=np.int32)
                rank[np.asarray(order, dtype=np.int64)] = np.arange(count)
                selected_index = int(np.argmax(-rank))
                zero_residual_matches += int(selected_index == order[0])
                selected[slot] = actions[selected_index]

                if int(env.task_indices[slot]) < target_tasks:
                    branch = int(env.branches[slot])
                    teacher_index = int(env.teacher_indices[slot])
                    branch_total[branch] += 1
                    branch_match[branch] += int(selected_index == teacher_index)
                    decisions += 1
                    decision_digest.update(
                        (
                            f"{int(env.task_indices[slot])}:{int(selected[slot])}:"
                            f"{branch}\n"
                        ).encode()
                    )

            _, _, _, _, info = env.step(selected)
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal

    rows = [completed[index] for index in range(target_tasks)]
    branches = {
        BRANCHES[index]: {
            "decisions": branch_total[index],
            "exact_matches": branch_match[index],
            "accuracy": (
                branch_match[index] / branch_total[index]
                if branch_total[index]
                else 1.0
            ),
        }
        for index in range(len(BRANCHES))
    }
    return {
        "seed_base": seed_base,
        "maps": maps,
        "num_envs": num_envs,
        "rounds": rounds,
        "decisions": decisions,
        "exact_matches": sum(branch_match.values()),
        "accuracy": sum(branch_match.values()) / decisions,
        "zero_residual_argmax_matches": zero_residual_matches,
        "branches": branches,
        "decision_hash_sha256": decision_digest.hexdigest(),
        "summary": summarize(rows),
        "elapsed_seconds": time.perf_counter() - started,
        "episodes_detail": rows,
    }


def compare_baseline(rows: list[dict], baseline: dict) -> dict:
    mismatches = []
    for row in rows:
        key = (row["map_seed"], row["seat"], row["opponent"])
        expected = baseline.get(key)
        if expected is None:
            mismatches.append({"task": key, "field": "missing_baseline"})
            continue
        for field in COMPARISON_FIELDS:
            if row[field] != expected[field]:
                mismatches.append(
                    {
                        "task": key,
                        "field": field,
                        "expected": expected[field],
                        "actual": row[field],
                    }
                )
    return {
        "tasks": len(rows),
        "baseline_tasks": len(baseline),
        "mismatch_count": len(mismatches),
        "exact": len(rows) == len(baseline) and not mismatches,
        "mismatch_examples": mismatches[:20],
    }


def compare_repeats(left: list[dict], right: list[dict]) -> dict:
    mismatches = []
    for a, b in zip(left, right):
        for field in ("task_index", "map_seed", "seat", "opponent", *COMPARISON_FIELDS):
            if a[field] != b[field]:
                mismatches.append(
                    {
                        "task_index": a["task_index"],
                        "field": field,
                        "left": a[field],
                        "right": b[field],
                    }
                )
    return {
        "mismatch_count": len(mismatches),
        "exact": len(left) == len(right) and not mismatches,
        "mismatch_examples": mismatches[:20],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-base", type=int, default=9_711_000)
    parser.add_argument("--maps", type=int, default=32)
    parser.add_argument("--num-envs", type=int, default=16)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for required in (PROTOCOL, TEACHER_BASELINE, KERNEL):
        if not required.exists():
            raise SystemExit(f"missing D41b input: {required}")
    baseline = read_baseline(TEACHER_BASELINE)
    expected_tasks = args.maps * TASKS_PER_MAP
    if len(baseline) != expected_tasks:
        raise SystemExit(f"expected {expected_tasks} D40 baseline tasks")

    first = run_exact_prior(
        seed_base=args.seed_base, maps=args.maps, num_envs=args.num_envs
    )
    repeat = run_exact_prior(
        seed_base=args.seed_base, maps=args.maps, num_envs=args.num_envs
    )
    baseline_comparison = compare_baseline(first["episodes_detail"], baseline)
    repeat_comparison = compare_repeats(
        first["episodes_detail"], repeat["episodes_detail"]
    )
    kernel_bytes = KERNEL.stat().st_size
    integrity = all(
        first["summary"][field] == 0
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        )
    ) and first["summary"]["maximum_workers"] <= 3
    gates = {
        "exact_selection_every_decision": first["accuracy"] == 1.0
        and all(branch["accuracy"] == 1.0 for branch in first["branches"].values()),
        "all_terminal_rows_match_d40": baseline_comparison["exact"],
        "independent_repeat_exact": repeat_comparison["exact"]
        and first["decision_hash_sha256"] == repeat["decision_hash_sha256"],
        "integrity": integrity,
        "zero_residual_argmax_exact": first["zero_residual_argmax_matches"]
        >= first["decisions"],
        "residual_size": RESIDUAL_PARAMETERS == 737
        and RESIDUAL_PARAMETERS * 4 <= 2_948
        and RESIDUAL_PARAMETERS <= 737,
        "kernel_source_size": kernel_bytes <= 10_000,
    }
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "teacher_baseline": str(TEACHER_BASELINE),
        "teacher_baseline_sha256": sha256(TEACHER_BASELINE),
        "kernel": str(KERNEL),
        "kernel_sha256": sha256(KERNEL),
        "kernel_source_bytes": kernel_bytes,
        "residual_parameters": RESIDUAL_PARAMETERS,
        "residual_float_bytes": RESIDUAL_PARAMETERS * 4,
        "residual_int8_bytes": RESIDUAL_PARAMETERS,
        "first": first,
        "repeat": repeat,
        "baseline_comparison": baseline_comparison,
        "repeat_comparison": repeat_comparison,
        "gates": gates,
        "pass": all(gates.values()),
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "pass": report["pass"],
                "gates": gates,
                "first": {key: value for key, value in first.items() if key != "episodes_detail"},
                "repeat": {key: value for key, value in repeat.items() if key != "episodes_detail"},
                "baseline_comparison": baseline_comparison,
                "repeat_comparison": repeat_comparison,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
