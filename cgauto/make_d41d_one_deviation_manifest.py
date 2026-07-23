#!/usr/bin/env python3
"""Build the outcome-blind D41d residual-top and hash-control state manifest."""

from __future__ import annotations

import collections
import csv
import hashlib
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
PROTOCOL = ANALYSIS / "d41d-residual-ranked-one-deviation-protocol-2026-07-21.md"
CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
MANIFEST = ANALYSIS / "d41d-one-deviation-manifest-9760000-9760031.tsv"
SUMMARY = ANALYSIS / "d41d-one-deviation-manifest-2026-07-21.json"
SEED_BASE = 9_760_000
MAPS = 32
TOP_PER_STRATUM = 8
CONTROL_PER_STRATUM = 4


def phase(turn: int) -> str:
    return "early" if turn < 100 else ("middle" if turn < 200 else "late")


def identity(row: dict) -> tuple:
    return (
        row["map_seed"],
        row["seat"],
        row["opponent_index"],
        row["decision_ordinal"],
    )


def control_hash(row: dict) -> str:
    return hashlib.sha256(":".join(map(str, identity(row))).encode()).hexdigest()


def select_cohorts(rows: list[dict]) -> list[dict]:
    strata: dict[tuple, list[dict]] = collections.defaultdict(list)
    for row in rows:
        strata[(row["branch"], row["phase"], row["opponent"])].append(row)
    selected = []
    for stratum, bucket in sorted(strata.items()):
        top = sorted(bucket, key=lambda row: (-row["residual_gap"], identity(row)))[
            :TOP_PER_STRATUM
        ]
        top_ids = {identity(row) for row in top}
        control_pool = [row for row in bucket if identity(row) not in top_ids]
        control = sorted(control_pool, key=lambda row: (control_hash(row), identity(row)))[
            :CONTROL_PER_STRATUM
        ]
        for cohort, cohort_rows in (("residual_top", top), ("hash_control", control)):
            for row in cohort_rows:
                selected.append({**row, "cohort": cohort, "control_hash": control_hash(row)})
    selected.sort(
        key=lambda row: (
            row["cohort"],
            row["branch"],
            row["phase"],
            row["opponent"],
            identity(row),
        )
    )
    for sample_id, row in enumerate(selected):
        row["sample_id"] = sample_id
    return selected


@torch.inference_mode()
def collect_states(model: ExactPriorResidualActorCritic) -> tuple[list[dict], dict]:
    target_tasks = MAPS * TASKS_PER_MAP
    completed = set()
    ordinals: collections.Counter[int] = collections.Counter()
    rows = []
    total_decisions = singleton_decisions = 0
    model.eval()
    with MacroVecEnv(64, SEED_BASE) as env:
        while len(completed) < target_tasks:
            active = np.flatnonzero(env.task_indices < target_tasks)
            maximum = int(env.counts.max())
            features = torch.from_numpy(env.features[:, :maximum])
            residual = model.actor_output(F.relu(model.actor_hidden(features))).squeeze(-1).numpy()
            for slot in active:
                task_index = int(env.task_indices[slot])
                ordinal = ordinals[task_index]
                ordinals[task_index] += 1
                total_decisions += 1
                count = int(env.counts[slot])
                if count < 2:
                    singleton_decisions += 1
                    continue
                ranks = env.prior_ranks[slot, :count]
                rank_zero = int(np.flatnonzero(ranks == 0)[0])
                rank_one = int(np.flatnonzero(ranks == 1)[0])
                turn = int(round(float(env.features[slot, 0, 1]) * 300))
                opponent_index = task_index % len(OPPONENTS)
                branch_index = int(env.branches[slot])
                rows.append(
                    {
                        "map_seed": SEED_BASE + task_index // TASKS_PER_MAP,
                        "task_index": task_index,
                        "seat": (task_index % TASKS_PER_MAP) // len(OPPONENTS),
                        "opponent_index": opponent_index,
                        "opponent": OPPONENTS[opponent_index],
                        "decision_ordinal": ordinal,
                        "turn": turn,
                        "branch_index": branch_index,
                        "branch": BRANCHES[branch_index],
                        "phase": phase(turn),
                        "candidate_count": count,
                        "teacher_action": int(env.actions[slot, rank_zero]),
                        "alternative_action": int(env.actions[slot, rank_one]),
                        "residual_gap": float(
                            residual[slot, rank_one] - residual[slot, rank_zero]
                        ),
                    }
                )
            _, _, _, _, info = env.step(env.teacher_actions())
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed.add(terminal["task_index"])
    return rows, {
        "episodes": target_tasks,
        "decisions": total_decisions,
        "actionable_states": len(rows),
        "singleton_decisions": singleton_decisions,
    }


def main() -> None:
    for required in (PROTOCOL, CHECKPOINT):
        if not required.exists():
            raise SystemExit(f"missing D41d prerequisite: {required}")
    expected_checkpoint = "1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a"
    if sha256(CHECKPOINT) != expected_checkpoint:
        raise SystemExit("D41d checkpoint hash mismatch")
    if MANIFEST.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite D41d manifest artifacts")
    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = ExactPriorResidualActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    bank, census = collect_states(model)
    selected = select_cohorts(bank)
    fieldnames = (
        "sample_id",
        "cohort",
        "map_seed",
        "task_index",
        "seat",
        "opponent_index",
        "opponent",
        "decision_ordinal",
        "turn",
        "branch_index",
        "branch",
        "phase",
        "candidate_count",
        "teacher_action",
        "alternative_action",
        "residual_gap",
        "control_hash",
    )
    with MANIFEST.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(selected)
    cohort_counts = collections.Counter(row["cohort"] for row in selected)
    stratum_counts = collections.Counter(
        (row["cohort"], row["branch"], row["phase"], row["opponent"])
        for row in selected
    )
    summary = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "seed_base": SEED_BASE,
        "maps": MAPS,
        "census": census,
        "manifest": str(MANIFEST),
        "manifest_sha256": sha256(MANIFEST),
        "samples": len(selected),
        "unique_samples": len({identity(row) for row in selected}),
        "cohort_counts": dict(sorted(cohort_counts.items())),
        "stratum_counts": {
            "|".join(key): value for key, value in sorted(stratum_counts.items())
        },
        "selection_outcome_blind": True,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
