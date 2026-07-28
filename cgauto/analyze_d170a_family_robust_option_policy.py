#!/usr/bin/env python3
"""D170a Phase 2 (admission/selection) and Phase 3 (veto/confirmation).

Loads Phase 1 checkpoints, evaluates each deterministically (argmax) on the
frozen LOBO selection blocks, applies the frozen admission gates, selects one
fit per the frozen tie-break, then (subcommands) runs the veto panel and,
if it passes, the sealed one-shot confirmation block. See
`data/analysis/live-agent-6553250/d170a-family-robust-option-policy-protocol-2026-07-28.md`
and `...-lock.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.rl_d170a_option_policy_env import D170aVecEnv  # noqa: E402
from cgauto.rl_macro_env import OPPONENTS  # noqa: E402
from cgauto.train_d170a_family_robust_option_policy import (  # noqa: E402
    BASE,
    EXTERNAL,
    HIDDEN,
    LOCK,
    MODEL_SEEDS,
    PROTOCOL,
    VARIANT_ORDER,
    D170aActorCritic,
    git_rev,
    output_paths,
    sha256,
)

ROOT = Path(__file__).resolve().parents[1]

SELECTION_SEED_BASE = 9_851_000
SELECTION_BLOCKS = 8
SELECTION_BLOCK_MAPS = 16
SELECTION_MAP_POOL = SELECTION_BLOCKS * SELECTION_BLOCK_MAPS  # 128
VETO_SEED_BASE = 9_844_136
VETO_MAP_POOL = 64  # 1,024 consumed panel tasks; veto-only
CONFIRMATION_SEED_BASE = 9_852_000
CONFIRMATION_MAP_POOL = 64  # 1,024 sealed tasks; opened exactly once

CATASTROPHE_THRESHOLD = -100
EVAL_NUM_ENVS = 32


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_model(checkpoint_path: Path) -> D170aActorCritic:
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model = D170aActorCritic()
    model.load_state_dict(payload["model"])
    model.eval()
    return model


def evaluate_deterministic(
    model: D170aActorCritic,
    seed_base: int,
    map_pool: int,
    *,
    num_envs: int = EVAL_NUM_ENVS,
) -> list[dict]:
    """Exhaustive, deterministic (argmax) evaluation of every (map, seat,
    opponent) task in [seed_base, seed_base+map_pool) x 2 seats x 8
    opponents, exactly once each (task_index-indexed; D108/D158's own
    `evaluate_policy` convention)."""
    tasks = map_pool * 2 * len(OPPONENTS)
    completed: dict[int, dict] = {}
    hidden = torch.zeros((num_envs, HIDDEN), dtype=torch.float32)
    guard = 0
    guard_limit = tasks * 25 + 5_000
    with D170aVecEnv(num_envs, seed_base, map_pool) as env:
        inputs, pending = env.observe()
        while len(completed) < tasks:
            guard += 1
            if guard > guard_limit:
                raise RuntimeError("D170a evaluate_deterministic iteration guard tripped")
            valid_before = pending.copy()
            with torch.inference_mode():
                action, _, _, _, next_hidden = model.action_and_value(
                    torch.from_numpy(inputs), hidden, deterministic=True
                )
            selected = action.numpy().astype(np.int32)
            inputs, pending, raw_rewards, dones, terminals = env.step(selected)
            valid_t = torch.from_numpy(valid_before.astype(np.float32)).unsqueeze(-1)
            done_t = torch.from_numpy(dones.astype(np.float32)).unsqueeze(-1)
            hidden = torch.where(valid_t.bool(), next_hidden, hidden) * (1.0 - done_t)
            for slot, terminal in enumerate(terminals):
                if terminal is None:
                    continue
                identity = abs(100.0 * raw_rewards[slot] - terminal.paired_margin)
                if identity >= 1.0e-3:
                    raise RuntimeError("D170a evaluation reward-identity failure")
                if terminal.task_index < tasks and terminal.task_index not in completed:
                    completed[terminal.task_index] = {
                        "task_index": int(terminal.task_index),
                        "map_seed": int(terminal.map_seed),
                        "seat": int(terminal.seat),
                        "opponent": int(terminal.opponent),
                        "opponent_name": OPPONENTS[terminal.opponent],
                        "own_score": int(terminal.own_score),
                        "opponent_score": int(terminal.opponent_score),
                        "margin": int(terminal.margin),
                        "control_margin": int(terminal.control_margin),
                        "control_own_score": int(terminal.control_own_score),
                        "paired_margin": int(terminal.paired_margin),
                        "own_score_delta": int(terminal.own_score_delta),
                        "chosen_arm": int(terminal.chosen_arm),
                        "chosen_arm_label": terminal.chosen_arm_label,
                        "decisions_seen": int(terminal.decisions_seen),
                        "budget_used": bool(terminal.budget_used),
                        "purity_violations": int(terminal.purity_violations),
                        "invalid_direct_commands": int(terminal.invalid_direct_commands),
                        "provenance_failures": int(terminal.provenance_failures),
                    }
    return [completed[index] for index in range(tasks)]


def rows_digest(rows: list[dict]) -> str:
    payload = json.dumps(rows, sort_keys=True).encode("utf-8")
    return sha256_bytes(payload)


def summarize_rows(rows: list[dict], *, block_seed_base: int | None = None, block_maps: int = 0) -> dict:
    pooled_mean = float(np.mean([row["paired_margin"] for row in rows]))
    family_means = {
        name: float(np.mean([row["paired_margin"] for row in rows if row["opponent_name"] == name]))
        for name in OPPONENTS
    }
    worst_family = min(family_means.values())
    mean_own_score_delta = float(np.mean([row["own_score_delta"] for row in rows]))
    crop_safety_exact = all(
        row["purity_violations"] == 0
        and row["invalid_direct_commands"] == 0
        and row["provenance_failures"] == 0
        for row in rows
    )
    catastrophes_policy = sum(1 for row in rows if row["margin"] <= CATASTROPHE_THRESHOLD)
    catastrophes_control = sum(
        1 for row in rows if (row["margin"] - row["paired_margin"]) <= CATASTROPHE_THRESHOLD
    )
    negative_mass_policy = float(sum(max(0, -row["margin"]) for row in rows))
    negative_mass_control = float(
        sum(max(0, -(row["margin"] - row["paired_margin"])) for row in rows)
    )
    summary = {
        "tasks": len(rows),
        "pooled_mean": pooled_mean,
        "family_means": family_means,
        "worst_family": worst_family,
        "mean_own_score_delta": mean_own_score_delta,
        "crop_safety_exact": crop_safety_exact,
        "catastrophes_policy": catastrophes_policy,
        "catastrophes_control": catastrophes_control,
        "negative_mass_policy": negative_mass_policy,
        "negative_mass_control": negative_mass_control,
        "strict_improvement_rate": float(np.mean([row["paired_margin"] > 0 for row in rows])),
        "arm_offer_note": "chosen_arm distribution, informational",
        "chosen_arm_counts": {
            label: sum(1 for row in rows if row["chosen_arm_label"] == label)
            for label in sorted({row["chosen_arm_label"] for row in rows})
        },
        "budget_used_rate": float(np.mean([row["budget_used"] for row in rows])),
    }
    if block_seed_base is not None:
        block_of = lambda row: (row["map_seed"] - block_seed_base) // block_maps  # noqa: E731
        blocks: dict[int, list[dict]] = {}
        for row in rows:
            blocks.setdefault(block_of(row), []).append(row)
        block_means = {
            block: float(np.mean([row["paired_margin"] for row in block_rows]))
            for block, block_rows in blocks.items()
        }
        summary["block_means"] = block_means
        summary["worst_block"] = min(block_means.values())
        summary["block_counts"] = {block: len(rows_) for block, rows_ in blocks.items()}
    return summary


def clustered_ci(
    rows: list[dict],
    *,
    value_key: str = "paired_margin",
    cluster_key: str = "map_seed",
    resamples: int = 10_000,
    seed: int = 20260728,
) -> dict:
    rng = np.random.default_rng(seed)
    by_cluster: dict[int, list[float]] = {}
    for row in rows:
        by_cluster.setdefault(row[cluster_key], []).append(float(row[value_key]))
    clusters = list(by_cluster.keys())
    n = len(clusters)
    means = np.empty(resamples, dtype=np.float64)
    for i in range(resamples):
        picked = rng.choice(clusters, size=n, replace=True)
        values = np.concatenate([by_cluster[c] for c in picked])
        means[i] = float(values.mean())
    overall_mean = float(np.mean([value for values in by_cluster.values() for value in values]))
    return {
        "mean": overall_mean,
        "ci_low": float(np.percentile(means, 2.5)),
        "ci_high": float(np.percentile(means, 97.5)),
        "clusters": n,
        "resamples": resamples,
        "bootstrap_seed": seed,
    }


def admission_gates(summary: dict) -> dict:
    gates = {
        "lobo_pooled_mean_at_least_1_5": summary["pooled_mean"] >= 1.5,
        "worst_held_block_at_least_0": summary["worst_block"] >= 0.0,
        "worst_family_mean_at_least_minus1": summary["worst_family"] >= -1.0,
        "mean_own_score_delta_at_least_minus0_5": summary["mean_own_score_delta"] >= -0.5,
        "crop_workforce_safety_exact": summary["crop_safety_exact"],
        "catastrophes_le_control": summary["catastrophes_policy"] <= summary["catastrophes_control"],
    }
    return {"gates": gates, "admitted": all(gates.values())}


def veto_gates(summary: dict) -> dict:
    gates = {
        "mean_at_least_1_0": summary["pooled_mean"] >= 1.0,
        "no_family_below_minus2": summary["worst_family"] >= -2.0,
        "catastrophes_le_control": summary["catastrophes_policy"] <= summary["catastrophes_control"],
        "negative_mass_le_control": summary["negative_mass_policy"] <= summary["negative_mass_control"],
    }
    return {"gates": gates, "veto_pass": all(gates.values())}


def confirmation_gates(summary: dict, ci: dict) -> dict:
    gates = {
        "mean_at_least_2_0": summary["pooled_mean"] >= 2.0,
        "clustered_ci_floor_positive": ci["ci_low"] > 0.0,
        "all_families_at_least_minus1": summary["worst_family"] >= -1.0,
        "catastrophes_le_control": summary["catastrophes_policy"] <= summary["catastrophes_control"],
        "negative_mass_le_1_1x_control": summary["negative_mass_policy"]
        <= 1.1 * summary["negative_mass_control"],
    }
    return {"gates": gates, "confirmation_pass": all(gates.values())}


def fit_result_path(variant: str, seed: int) -> Path:
    return output_paths(variant, seed)["result"]


def fit_checkpoint_path(variant: str, seed: int) -> Path:
    return output_paths(variant, seed)["checkpoint_pt"]


def all_fit_keys() -> list[tuple[str, int]]:
    return [(variant, seed) for variant in VARIANT_ORDER for seed in MODEL_SEEDS[variant]]


def phase2(threads: int, output: Path) -> dict:
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    fit_summaries = []
    for variant, seed in all_fit_keys():
        result_path = fit_result_path(variant, seed)
        if not result_path.exists():
            fit_summaries.append(
                {"variant": variant, "seed": seed, "status": "missing_result"}
            )
            continue
        fit_result = json.loads(result_path.read_text())
        if fit_result["decision"] != "trained":
            fit_summaries.append(
                {"variant": variant, "seed": seed, "status": fit_result["decision"]}
            )
            continue
        checkpoint = fit_checkpoint_path(variant, seed)
        model = load_model(checkpoint)
        started = time.perf_counter()
        rows = evaluate_deterministic(model, SELECTION_SEED_BASE, SELECTION_MAP_POOL)
        elapsed = time.perf_counter() - started
        summary = summarize_rows(
            rows, block_seed_base=SELECTION_SEED_BASE, block_maps=SELECTION_BLOCK_MAPS
        )
        admission = admission_gates(summary)
        fit_summaries.append(
            {
                "variant": variant,
                "seed": seed,
                "status": "evaluated",
                "checkpoint_sha256": sha256(checkpoint),
                "eval_seconds": elapsed,
                "rows_digest_sha256": rows_digest(rows),
                "summary": summary,
                "admission": admission,
            }
        )
        print(
            json.dumps(
                {
                    "event": "phase2_fit",
                    "variant": variant,
                    "seed": seed,
                    "pooled_mean": summary["pooled_mean"],
                    "worst_block": summary["worst_block"],
                    "worst_family": summary["worst_family"],
                    "admitted": admission["admitted"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    admitted = [f for f in fit_summaries if f.get("status") == "evaluated" and f["admission"]["admitted"]]
    selected = None
    if admitted:
        admitted_sorted = sorted(
            admitted,
            key=lambda f: (-f["summary"]["worst_block"], -f["summary"]["pooled_mean"], f["seed"]),
        )
        selected = {"variant": admitted_sorted[0]["variant"], "seed": admitted_sorted[0]["seed"]}

    result = {
        "schema": "troll-farm-d170a-phase2-admission-selection-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "threads": threads,
        "selection_seed_base": SELECTION_SEED_BASE,
        "selection_map_pool": SELECTION_MAP_POOL,
        "selection_blocks": SELECTION_BLOCKS,
        "fits": fit_summaries,
        "admitted_count": len(admitted),
        "selected": selected,
        "decision": "selection_admitted" if selected else "no_admission_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"admitted_count": len(admitted), "selected": selected}, sort_keys=True))
    return result


def phase3_veto(variant: str, seed: int, threads: int, output: Path) -> dict:
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    checkpoint = fit_checkpoint_path(variant, seed)
    model = load_model(checkpoint)
    started = time.perf_counter()
    rows = evaluate_deterministic(model, VETO_SEED_BASE, VETO_MAP_POOL)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    verdict = veto_gates(summary)
    result = {
        "schema": "troll-farm-d170a-phase3-veto-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "variant": variant,
        "seed": seed,
        "threads": threads,
        "veto_seed_base": VETO_SEED_BASE,
        "veto_map_pool": VETO_MAP_POOL,
        "eval_seconds": elapsed,
        "checkpoint_sha256": sha256(checkpoint),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "verdict": verdict,
        "decision": "veto_pass" if verdict["veto_pass"] else "veto_fail_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"veto_pass": verdict["veto_pass"], "summary": summary}, sort_keys=True))
    return result


def phase3_confirm(variant: str, seed: int, threads: int, output: Path) -> dict:
    if output.exists():
        raise SystemExit(
            f"refusing to overwrite {output}: the sealed confirmation block may be opened exactly once"
        )
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    checkpoint = fit_checkpoint_path(variant, seed)
    model = load_model(checkpoint)
    started = time.perf_counter()
    rows = evaluate_deterministic(model, CONFIRMATION_SEED_BASE, CONFIRMATION_MAP_POOL)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    ci = clustered_ci(rows)
    verdict = confirmation_gates(summary, ci)
    result = {
        "schema": "troll-farm-d170a-phase3-confirmation-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "variant": variant,
        "seed": seed,
        "threads": threads,
        "confirmation_seed_base": CONFIRMATION_SEED_BASE,
        "confirmation_map_pool": CONFIRMATION_MAP_POOL,
        "sealed_block_opened_exactly_once": True,
        "eval_seconds": elapsed,
        "checkpoint_sha256": sha256(checkpoint),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "clustered_ci": ci,
        "verdict": verdict,
        "decision": "CONFIRMED" if verdict["confirmation_pass"] else "confirmation_fail_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"confirmation_pass": verdict["confirmation_pass"], "summary": summary, "ci": ci}, sort_keys=True))
    return result


def verify_thread_parity(variant: str, seed: int, seed_base: int, map_pool: int) -> dict:
    """Run the same deterministic evaluation at 1 and 20 Rayon threads and
    hash-compare the row set for byte identity (the frozen threading rule)."""
    checkpoint = fit_checkpoint_path(variant, seed)
    digests = {}
    for threads in (1, 20):
        os.environ["RAYON_NUM_THREADS"] = str(threads)
        torch.set_num_threads(1)
        model = load_model(checkpoint)
        rows = evaluate_deterministic(model, seed_base, map_pool)
        digests[threads] = rows_digest(rows)
    identical = digests[1] == digests[20]
    return {"digests": digests, "byte_identical_1_vs_20_threads": identical}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p2 = sub.add_parser("phase2")
    p2.add_argument("--threads", type=int, default=1)
    p2.add_argument("--output", type=Path, default=BASE / "d170a-family-robust-option-policy-phase2-result.json")

    p3v = sub.add_parser("phase3-veto")
    p3v.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    p3v.add_argument("--seed", type=int, required=True)
    p3v.add_argument("--threads", type=int, default=1)
    p3v.add_argument("--output", type=Path, default=BASE / "d170a-family-robust-option-policy-phase3-veto-result.json")

    p3c = sub.add_parser("phase3-confirm")
    p3c.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    p3c.add_argument("--seed", type=int, required=True)
    p3c.add_argument("--threads", type=int, default=1)
    p3c.add_argument(
        "--output", type=Path, default=BASE / "d170a-family-robust-option-policy-phase3-confirmation-result.json"
    )

    parity = sub.add_parser("thread-parity")
    parity.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    parity.add_argument("--seed", type=int, required=True)
    parity.add_argument("--seed-base", type=int, default=VETO_SEED_BASE)
    parity.add_argument("--map-pool", type=int, default=4)
    parity.add_argument("--output", type=Path, default=None)

    args = parser.parse_args()
    if args.command == "phase2":
        phase2(args.threads, args.output)
    elif args.command == "phase3-veto":
        phase3_veto(args.variant, args.seed, args.threads, args.output)
    elif args.command == "phase3-confirm":
        phase3_confirm(args.variant, args.seed, args.threads, args.output)
    elif args.command == "thread-parity":
        result = verify_thread_parity(args.variant, args.seed, args.seed_base, args.map_pool)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
