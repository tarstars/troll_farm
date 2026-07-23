#!/usr/bin/env python3
"""Prospective complete-policy evaluation for the frozen D41e branch/gap selector."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.rl_macro_env import BRANCHES, DEFAULT_LIBRARY, OPPONENTS, TASKS_PER_MAP, MacroVecEnv
from cgauto.train_d41a_macro_bc import summarize
from cgauto.train_d41c_residual_ppo import ExactPriorResidualActorCritic


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41e-branch-gap-complete-policy-protocol-2026-07-21.md"
DISCOVERY = ANALYSIS / "d41e-threshold-discovery-2026-07-21.json"
CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
KERNEL = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
OUTPUT = ANALYSIS / "d41e-branch-gap-complete-policy-result.json"
EXPECTED = {
    "discovery": "1d781d1bead197d26aa3ca41e1f86d6ae6ea05f90cf26385e74b8afed47ad4d7",
    "checkpoint": "1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a",
    "kernel": "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62",
    "library": "5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173",
}
STAGES = {
    "a": {"seed_base": 9_770_000, "maps": 64, "random_seed": 419, "mean_floor": 5.0},
    "b": {"seed_base": 9_771_000, "maps": 64, "random_seed": 421, "mean_floor": 3.0},
}
NUM_ENVS = 64
EVACUATION_GAP_MIN = 0.020
EVACUATION_GAP_MAX = 0.030
RATE_GAP_MIN = 0.280
RATE_GAP_MAX = 0.340
MIDDLE_START = 100
LATE_START = 200


def phase_index(turn: int) -> int:
    return 0 if turn < MIDDLE_START else (1 if turn < LATE_START else 2)


def rule_select(branch: int, turn: int, gap: float) -> bool:
    if branch == BRANCHES.index("evacuation"):
        return EVACUATION_GAP_MIN <= gap <= EVACUATION_GAP_MAX
    if branch == BRANCHES.index("rate"):
        outside_middle = turn < MIDDLE_START or turn >= LATE_START
        return outside_middle and RATE_GAP_MIN <= gap <= RATE_GAP_MAX
    return False


def distribution(values: list[float]) -> dict:
    array = np.asarray(values, dtype=np.float64)
    if not len(array):
        return {"samples": 0}
    standard_error = float(array.std(ddof=1) / math.sqrt(len(array))) if len(array) > 1 else 0.0
    mean = float(array.mean())
    return {
        "samples": len(array),
        "mean": mean,
        "standard_error": standard_error,
        "normal_95_low": mean - 1.96 * standard_error,
        "normal_95_high": mean + 1.96 * standard_error,
        "minimum": float(array.min()),
        "p10": float(np.quantile(array, 0.10)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "maximum": float(array.max()),
        "positive_rate": float(np.mean(array > 0)),
        "tie_rate": float(np.mean(array == 0)),
        "negative_rate": float(np.mean(array < 0)),
    }


def load_model() -> ExactPriorResidualActorCritic:
    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = ExactPriorResidualActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    model.eval()
    return model


@torch.inference_mode()
def candidate_indices(
    env: MacroVecEnv, model: ExactPriorResidualActorCritic
) -> tuple[np.ndarray, np.ndarray]:
    maximum = int(env.counts.max())
    features = torch.from_numpy(env.features[:, :maximum])
    residual = model.actor_output(F.relu(model.actor_hidden(features))).squeeze(-1).numpy()
    selected = env.teacher_indices.astype(np.int64).copy()
    gaps = np.full(env.num_envs, np.nan, dtype=np.float32)
    for slot in range(env.num_envs):
        count = int(env.counts[slot])
        if count < 2:
            continue
        ranks = env.prior_ranks[slot, :count]
        rank_zero = int(np.flatnonzero(ranks == 0)[0])
        rank_one = int(np.flatnonzero(ranks == 1)[0])
        if rank_zero != int(env.teacher_indices[slot]):
            raise RuntimeError("D41e rank-zero/teacher mismatch")
        gap = float(residual[slot, rank_one] - residual[slot, rank_zero])
        gaps[slot] = gap
        turn = int(round(float(env.features[slot, 0, 1]) * 300))
        if rule_select(int(env.branches[slot]), turn, gap):
            selected[slot] = rank_one
    return selected, gaps


def random_indices(env: MacroVecEnv, rng: np.random.Generator) -> np.ndarray:
    return np.asarray(
        [rng.integers(int(count)) for count in env.counts], dtype=np.int64
    )


def arm_summary(rows: list[dict], telemetry: dict) -> dict:
    report = summarize(rows)
    report.update(
        {
            "maximum_workers": max(row["own_workers"] for row in rows),
            "catastrophes": sum(row["margin"] <= -100 for row in rows),
            "changed_episodes": sum(row["overrides"] > 0 for row in rows),
            **telemetry,
        }
    )
    return report


@torch.inference_mode()
def run_arm(
    policy: str,
    *,
    seed_base: int,
    maps: int,
    model: ExactPriorResidualActorCritic | None = None,
    random_seed: int = 0,
    num_envs: int = NUM_ENVS,
) -> dict:
    if policy not in {"d40", "random", "d41e"}:
        raise ValueError(policy)
    if policy == "d41e" and model is None:
        raise ValueError("D41e policy requires the frozen residual model")
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    rng = np.random.default_rng(random_seed)
    slot_returns = np.zeros(num_envs, dtype=np.float64)
    slot_decisions = np.zeros(num_envs, dtype=np.int64)
    slot_overrides = np.zeros(num_envs, dtype=np.int64)
    slot_branch_decisions = np.zeros((num_envs, len(BRANCHES)), dtype=np.int64)
    slot_branch_overrides = np.zeros_like(slot_branch_decisions)
    slot_phase_overrides = np.zeros((num_envs, 3), dtype=np.int64)
    branch_decisions: collections.Counter[int] = collections.Counter()
    branch_overrides: collections.Counter[int] = collections.Counter()
    phase_overrides: collections.Counter[int] = collections.Counter()
    selected_gaps: list[float] = []
    illegal_actions = rule_mismatches = decisions = overrides = 0
    maximum_reward_identity_error = 0.0
    decision_digest = hashlib.sha256()
    rounds = 0
    started = time.perf_counter()

    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            rounds += 1
            if rounds > 20_000:
                raise RuntimeError("D41e decision loop")
            if policy == "d40":
                indices = env.teacher_indices.astype(np.int64).copy()
                gaps = np.full(num_envs, np.nan, dtype=np.float32)
            elif policy == "random":
                indices = random_indices(env, rng)
                gaps = np.full(num_envs, np.nan, dtype=np.float32)
            else:
                indices, gaps = candidate_indices(env, model)
            illegal_actions += int(np.count_nonzero(indices >= env.counts))
            if illegal_actions:
                raise RuntimeError("D41e selected an illegal candidate index")

            active = env.task_indices < target_tasks
            for slot in np.flatnonzero(active):
                task_index = int(env.task_indices[slot])
                branch = int(env.branches[slot])
                turn = int(round(float(env.features[slot, 0, 1]) * 300))
                changed = int(indices[slot] != int(env.teacher_indices[slot]))
                if policy == "d41e":
                    expected = bool(np.isfinite(gaps[slot])) and rule_select(
                        branch, turn, float(gaps[slot])
                    )
                    rule_mismatches += int(changed != expected)
                    if changed:
                        selected_gaps.append(float(gaps[slot]))
                slot_decisions[slot] += 1
                slot_overrides[slot] += changed
                slot_branch_decisions[slot, branch] += 1
                slot_branch_overrides[slot, branch] += changed
                slot_phase_overrides[slot, phase_index(turn)] += changed
                branch_decisions[branch] += 1
                branch_overrides[branch] += changed
                phase_overrides[phase_index(turn)] += changed
                decisions += 1
                overrides += changed
                action = int(env.actions[slot, indices[slot]])
                decision_digest.update(f"{task_index}:{action}:{branch}\n".encode())

            task_before = env.task_indices.copy()
            actions = env.actions[np.arange(num_envs), indices]
            _, _, _, rewards, info = env.step(actions)
            slot_returns += rewards.astype(np.float64)
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                if terminal["task_index"] != int(task_before[slot]):
                    raise RuntimeError("D41e terminal task drift")
                identity_error = abs(100.0 * slot_returns[slot] - terminal["margin"])
                maximum_reward_identity_error = max(maximum_reward_identity_error, identity_error)
                if terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = {
                        **terminal,
                        "decisions": int(slot_decisions[slot]),
                        "overrides": int(slot_overrides[slot]),
                        "branch_decisions": {
                            BRANCHES[index]: int(slot_branch_decisions[slot, index])
                            for index in range(len(BRANCHES))
                        },
                        "branch_overrides": {
                            BRANCHES[index]: int(slot_branch_overrides[slot, index])
                            for index in range(len(BRANCHES))
                        },
                        "phase_overrides": {
                            phase: int(slot_phase_overrides[slot, index])
                            for index, phase in enumerate(("early", "middle", "late"))
                        },
                        "reward_identity_error": identity_error,
                    }
                slot_returns[slot] = 0.0
                slot_decisions[slot] = 0
                slot_overrides[slot] = 0
                slot_branch_decisions[slot].fill(0)
                slot_branch_overrides[slot].fill(0)
                slot_phase_overrides[slot].fill(0)

    rows = [completed[index] for index in range(target_tasks)]
    telemetry = {
        "rounds": rounds,
        "decisions": decisions,
        "overrides": overrides,
        "disagreement_rate": overrides / decisions,
        "branch_decisions": {
            BRANCHES[index]: branch_decisions[index] for index in range(len(BRANCHES))
        },
        "branch_overrides": {
            BRANCHES[index]: branch_overrides[index] for index in range(len(BRANCHES))
        },
        "phase_overrides": {
            phase: phase_overrides[index]
            for index, phase in enumerate(("early", "middle", "late"))
        },
        "selected_gap": distribution(selected_gaps),
        "illegal_actions": illegal_actions,
        "rule_mismatches": rule_mismatches,
        "maximum_reward_identity_error": maximum_reward_identity_error,
        "decision_hash_sha256": decision_digest.hexdigest(),
    }
    return {
        "policy": policy,
        "seed_base": seed_base,
        "maps": maps,
        "episodes": target_tasks,
        "num_envs": num_envs,
        "elapsed_seconds": time.perf_counter() - started,
        "summary": arm_summary(rows, telemetry),
        "episodes_detail": rows,
    }


def paired_report(candidate: list[dict], baseline: list[dict]) -> dict:
    if len(candidate) != len(baseline):
        raise ValueError("paired D41e rows must align")
    deltas = []
    for learned, teacher in zip(candidate, baseline):
        identity = (learned["task_index"], learned["map_seed"], learned["seat"], learned["opponent"])
        expected = (teacher["task_index"], teacher["map_seed"], teacher["seat"], teacher["opponent"])
        if identity != expected:
            raise ValueError("paired D41e task mismatch")
        deltas.append(
            {
                "opponent": learned["opponent"],
                "margin": learned["margin"] - teacher["margin"],
                "own_score": learned["own_score"] - teacher["own_score"],
                "opponent_score": learned["opponent_score"] - teacher["opponent_score"],
                "changed": learned["overrides"] > 0,
            }
        )
    by_opponent = {
        opponent: distribution(
            [row["margin"] for row in deltas if row["opponent"] == opponent]
        )
        for opponent in OPPONENTS
    }
    changed = [row["margin"] for row in deltas if row["changed"]]
    return {
        "margin_delta": distribution([row["margin"] for row in deltas]),
        "own_score_delta": distribution([row["own_score"] for row in deltas]),
        "opponent_score_delta": distribution([row["opponent_score"] for row in deltas]),
        "changed_episode_margin_delta": distribution(changed),
        "by_opponent": by_opponent,
        "baseline_catastrophes": sum(row["margin"] <= -100 for row in baseline),
        "candidate_catastrophes": sum(row["margin"] <= -100 for row in candidate),
    }


def candidate_replicas_equal(left: dict, right: dict) -> bool:
    return (
        left["summary"]["decision_hash_sha256"] == right["summary"]["decision_hash_sha256"]
        and left["episodes_detail"] == right["episodes_detail"]
    )


def stage_gates(stage: dict, mean_floor: float) -> dict:
    baseline = stage["d40"]["summary"]
    random = stage["random"]["summary"]
    candidate = stage["candidate_a"]["summary"]
    paired = stage["paired"]
    family_means = [paired["by_opponent"][opponent]["mean"] for opponent in OPPONENTS]
    complete = all(
        arm["summary"]["episodes"] == stage["expected_episodes"]
        for arm in (stage["d40"], stage["random"], stage["candidate_a"], stage["candidate_b"])
    )
    integrity_fields = (
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
    )
    integrity = all(
        arm["summary"][field] == 0
        for arm in (stage["d40"], stage["random"], stage["candidate_a"], stage["candidate_b"])
        for field in integrity_fields
    ) and all(
        arm["summary"]["maximum_workers"] <= 3
        and arm["summary"]["illegal_actions"] == 0
        and arm["summary"]["maximum_reward_identity_error"] <= 1e-4
        for arm in (stage["d40"], stage["random"], stage["candidate_a"], stage["candidate_b"])
    )
    branch = candidate["branch_overrides"]
    gates = {
        "complete_unique_grid": complete,
        "candidate_repeat_exact": stage["candidate_repeat_exact"],
        "integrity": integrity,
        "rule_and_branch_isolation": candidate["rule_mismatches"] == 0
        and branch["train"] == 0
        and branch["deficit"] == 0
        and branch["evacuation"] > 0
        and branch["rate"] > 0,
        "bounded_activation": 0.001 <= candidate["disagreement_rate"] <= 0.05
        and candidate["changed_episodes"] >= 64,
        "paired_margin": paired["margin_delta"]["mean"] >= mean_floor
        and paired["margin_delta"]["normal_95_low"] > 0,
        "own_score_floor": paired["own_score_delta"]["mean"] >= -2,
        "opponent_breadth_and_tail": sum(value > 0 for value in family_means) >= 5
        and min(family_means) >= -10,
        "workforce_and_crop": candidate["worker_two_rate"] >= 0.95
        and candidate["worker_three_rate"] >= 0.88
        and candidate["crop_rate"] >= 0.97
        and candidate["worker_two_rate"] >= baseline["worker_two_rate"] - 0.01
        and candidate["worker_three_rate"] >= baseline["worker_three_rate"] - 0.01
        and candidate["crop_rate"] >= baseline["crop_rate"] - 0.01,
        "catastrophe_nonincrease": paired["candidate_catastrophes"]
        <= paired["baseline_catastrophes"],
        "random_margin_floor": candidate["mean_margin"] >= random["mean_margin"] + 150,
    }
    return {"gates": gates, "pass": all(gates.values())}


def run_stage(
    name: str,
    config: dict,
    model: ExactPriorResidualActorCritic,
    *,
    num_envs: int = NUM_ENVS,
) -> dict:
    common = {
        "seed_base": config["seed_base"],
        "maps": config["maps"],
        "num_envs": num_envs,
    }
    d40 = run_arm("d40", **common)
    print(json.dumps({"progress": f"stage_{name}_d40", "summary": d40["summary"]}), flush=True)
    random = run_arm("random", **common, random_seed=config["random_seed"])
    print(json.dumps({"progress": f"stage_{name}_random", "summary": random["summary"]}), flush=True)
    candidate_a = run_arm("d41e", **common, model=model)
    print(
        json.dumps({"progress": f"stage_{name}_candidate_a", "summary": candidate_a["summary"]}),
        flush=True,
    )
    candidate_b = run_arm("d41e", **common, model=model)
    print(
        json.dumps({"progress": f"stage_{name}_candidate_b", "summary": candidate_b["summary"]}),
        flush=True,
    )
    report = {
        "stage": name,
        "config": config,
        "expected_episodes": config["maps"] * TASKS_PER_MAP,
        "d40": d40,
        "random": random,
        "candidate_a": candidate_a,
        "candidate_b": candidate_b,
        "candidate_repeat_exact": candidate_replicas_equal(candidate_a, candidate_b),
        "paired": paired_report(candidate_a["episodes_detail"], d40["episodes_detail"]),
    }
    report.update(stage_gates(report, config["mean_floor"]))
    print(json.dumps({"progress": f"stage_{name}_gate", "pass": report["pass"], "gates": report["gates"]}), flush=True)
    return report


def pooled_report(stage_a: dict, stage_b: dict) -> dict:
    candidate = stage_a["candidate_a"]["episodes_detail"] + stage_b["candidate_a"]["episodes_detail"]
    baseline = stage_a["d40"]["episodes_detail"] + stage_b["d40"]["episodes_detail"]
    paired = paired_report(candidate, baseline)
    family_means = [paired["by_opponent"][opponent]["mean"] for opponent in OPPONENTS]
    gates = {
        "mean_at_least_5": paired["margin_delta"]["mean"] >= 5,
        "normal_95_low_above_zero": paired["margin_delta"]["normal_95_low"] > 0,
        "at_least_six_positive_opponents": sum(value > 0 for value in family_means) >= 6,
        "no_opponent_below_minus_10": min(family_means) >= -10,
        "catastrophe_nonincrease": paired["candidate_catastrophes"]
        <= paired["baseline_catastrophes"],
    }
    return {"paired": paired, "gates": gates, "pass": all(gates.values())}


def compact_stage(stage: dict | None) -> dict | None:
    if stage is None:
        return None
    return {
        "pass": stage["pass"],
        "gates": stage["gates"],
        "paired": stage["paired"],
        "d40": stage["d40"]["summary"],
        "random": stage["random"]["summary"],
        "candidate": stage["candidate_a"]["summary"],
        "candidate_repeat_exact": stage["candidate_repeat_exact"],
    }


def verify_inputs() -> None:
    required = (PROTOCOL, DISCOVERY, CHECKPOINT, KERNEL, Path(DEFAULT_LIBRARY))
    for path in required:
        if not path.exists():
            raise SystemExit(f"missing D41e prerequisite: {path}")
    actual = {
        "discovery": sha256(DISCOVERY),
        "checkpoint": sha256(CHECKPOINT),
        "kernel": sha256(KERNEL),
        "library": sha256(Path(DEFAULT_LIBRARY)),
    }
    if actual != EXPECTED:
        raise SystemExit(f"D41e frozen input mismatch: {actual}")
    discovery = json.loads(DISCOVERY.read_text())
    if discovery["analysis"]["pass"] is not True:
        raise SystemExit("D41e discovery rule did not pass")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    verify_inputs()
    torch.set_num_threads(20)
    torch.set_num_interop_threads(4)
    model = load_model()
    if args.preflight_only:
        smoke = {
            "seed_base": 9_760_000,
            "maps": 2,
            "num_envs": 32,
        }
        d40 = run_arm("d40", **smoke)
        first = run_arm("d41e", **smoke, model=model)
        repeat = run_arm("d41e", **smoke, model=model)
        report = {
            "candidate_repeat_exact": candidate_replicas_equal(first, repeat),
            "paired": paired_report(first["episodes_detail"], d40["episodes_detail"]),
            "candidate": first["summary"],
        }
        if not report["candidate_repeat_exact"] or first["summary"]["rule_mismatches"]:
            raise SystemExit("D41e consumed-bank preflight failed")
        print(json.dumps(report, sort_keys=True))
        return
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D41e prospective result")

    started = time.perf_counter()
    stage_a = run_stage("a", STAGES["a"], model)
    stage_b = run_stage("b", STAGES["b"], model) if stage_a["pass"] else None
    pooled = pooled_report(stage_a, stage_b) if stage_b is not None and stage_b["pass"] else None
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "discovery_sha256": sha256(DISCOVERY),
            "checkpoint_sha256": sha256(CHECKPOINT),
            "kernel_sha256": sha256(KERNEL),
            "library_sha256": sha256(Path(DEFAULT_LIBRARY)),
        },
        "rule": json.loads(DISCOVERY.read_text())["analysis"]["rule"],
        "stage_a": stage_a,
        "stage_b": stage_b,
        "pooled": pooled,
        "pass": stage_a["pass"]
        and stage_b is not None
        and stage_b["pass"]
        and pooled is not None
        and pooled["pass"],
        "elapsed_seconds": time.perf_counter() - started,
        "scope": "local prospective D41e development only; no confirmation or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass": report["pass"],
                "stage_a": compact_stage(stage_a),
                "stage_b": compact_stage(stage_b),
                "pooled": pooled,
                "elapsed_seconds": report["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
