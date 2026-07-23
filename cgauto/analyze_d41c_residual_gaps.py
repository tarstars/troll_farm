#!/usr/bin/env python3
"""Measure how far the failed D41c residual remained from changing D40 argmax."""

from __future__ import annotations

import collections
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.rl_macro_env import BRANCHES, MacroVecEnv, OPPONENTS, TASKS_PER_MAP
from cgauto.train_d41c_residual_ppo import ExactPriorResidualActorCritic


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
TRAINING_RESULT = ANALYSIS / "d41c-residual-ppo-seed411-result.json"
OUTPUT = ANALYSIS / "d41c-residual-gap-diagnostic-2026-07-21.json"


def distribution(values: list[float]) -> dict:
    array = np.asarray(values, dtype=np.float64)
    if not len(array):
        return {"count": 0}
    return {
        "count": len(array),
        "mean": float(array.mean()),
        "minimum": float(array.min()),
        "p01": float(np.quantile(array, 0.01)),
        "p10": float(np.quantile(array, 0.10)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "p99": float(np.quantile(array, 0.99)),
        "maximum": float(array.max()),
    }


@torch.inference_mode()
def analyze(model: ExactPriorResidualActorCritic) -> dict:
    model.eval()
    seed_base = 9_740_000
    target_tasks = 32 * TASKS_PER_MAP
    completed = set()
    rank_one_gaps: list[float] = []
    flip_margins: list[float] = []
    best_alternative_ranks: collections.Counter[int] = collections.Counter()
    branch_gaps: dict[int, list[float]] = collections.defaultdict(list)
    phase_gaps: dict[str, list[float]] = collections.defaultdict(list)
    top_states = []
    decisions = actionable_decisions = residual_prefers_rank_one = 0
    singleton_decisions = 0
    residual_min = float("inf")
    residual_max = float("-inf")

    with MacroVecEnv(64, seed_base) as env:
        while len(completed) < target_tasks:
            active = np.flatnonzero(env.task_indices < target_tasks)
            maximum = int(env.counts.max())
            features = torch.from_numpy(env.features[:, :maximum])
            residual = model.actor_output(F.relu(model.actor_hidden(features))).squeeze(-1)
            residual_np = residual.numpy()
            for slot in active:
                count = int(env.counts[slot])
                ranks = env.prior_ranks[slot, :count].astype(np.int64)
                rank_zero = int(np.flatnonzero(ranks == 0)[0])
                decisions += 1
                if count == 1:
                    singleton_decisions += 1
                    residual_min = min(residual_min, float(residual_np[slot, 0]))
                    residual_max = max(residual_max, float(residual_np[slot, 0]))
                    continue
                rank_one = int(np.flatnonzero(ranks == 1)[0])
                actionable_decisions += 1
                row = residual_np[slot, :count]
                residual_min = min(residual_min, float(row.min()))
                residual_max = max(residual_max, float(row.max()))
                rank_one_gap = float(row[rank_one] - row[rank_zero])
                rank_one_gaps.append(rank_one_gap)
                residual_prefers_rank_one += int(rank_one_gap > 0)

                logits = -4.0 * ranks.astype(np.float64) + row.astype(np.float64)
                logits[rank_zero] = -np.inf
                alternative = int(np.argmax(logits))
                alternative_rank = int(ranks[alternative])
                best_alternative_ranks[alternative_rank] += 1
                flip_margin = float(
                    4.0 * alternative_rank - (row[alternative] - row[rank_zero])
                )
                flip_margins.append(flip_margin)
                branch = int(env.branches[slot])
                branch_gaps[branch].append(rank_one_gap)
                turn = int(round(float(env.features[slot, 0, 1]) * 300))
                phase = "early" if turn < 100 else ("middle" if turn < 200 else "late")
                phase_gaps[phase].append(rank_one_gap)
                task_index = int(env.task_indices[slot])
                top_states.append(
                    {
                        "task_index": task_index,
                        "map_seed": seed_base + task_index // TASKS_PER_MAP,
                        "seat": (task_index % TASKS_PER_MAP) // len(OPPONENTS),
                        "opponent": OPPONENTS[task_index % len(OPPONENTS)],
                        "turn": turn,
                        "branch": BRANCHES[branch],
                        "candidate_count": count,
                        "rank_one_residual_gap": rank_one_gap,
                        "best_alternative_rank": alternative_rank,
                        "flip_margin": flip_margin,
                        "teacher_action": int(env.actions[slot, rank_zero]),
                        "alternative_action": int(env.actions[slot, alternative]),
                    }
                )
            _, _, _, _, info = env.step(env.teacher_actions())
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed.add(terminal["task_index"])

    top_states.sort(key=lambda row: row["flip_margin"])
    return {
        "decisions": decisions,
        "actionable_decisions": actionable_decisions,
        "singleton_decisions": singleton_decisions,
        "rank_one_residual_gap": distribution(rank_one_gaps),
        "best_alternative_flip_margin": distribution(flip_margins),
        "residual_prefers_rank_one": residual_prefers_rank_one,
        "residual_prefers_rank_one_rate": residual_prefers_rank_one
        / actionable_decisions,
        "best_alternative_rank_histogram": {
            str(rank): count for rank, count in sorted(best_alternative_ranks.items())
        },
        "residual_output_minimum": residual_min,
        "residual_output_maximum": residual_max,
        "by_branch": {
            BRANCHES[branch]: distribution(values)
            for branch, values in sorted(branch_gaps.items())
        },
        "by_phase": {
            phase: distribution(phase_gaps[phase])
            for phase in ("early", "middle", "late")
        },
        "closest_states": top_states[:100],
    }


def main() -> None:
    for required in (CHECKPOINT, TRAINING_RESULT):
        if not required.exists():
            raise SystemExit(f"missing D41c artifact: {required}")
    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = ExactPriorResidualActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    result = json.loads(TRAINING_RESULT.read_text())
    if result.get("pass") is not False:
        raise SystemExit("D41c gap diagnostic is only defined for the failed final checkpoint")
    diagnostic = analyze(model)
    output = {
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "training_result": str(TRAINING_RESULT),
        "training_result_sha256": sha256(TRAINING_RESULT),
        "diagnostic": diagnostic,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
