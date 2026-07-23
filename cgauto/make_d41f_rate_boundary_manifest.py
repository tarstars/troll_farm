#!/usr/bin/env python3
"""Build the outcome-blind D41f early/late rate-gap manifest."""

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
PROTOCOL = ANALYSIS / "d41f-rate-boundary-one-deviation-protocol-2026-07-21.md"
CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
MANIFEST = ANALYSIS / "d41f-rate-boundary-manifest-9772000-9772031.tsv"
SUMMARY = ANALYSIS / "d41f-rate-boundary-manifest-2026-07-21.json"
SEED_BASE = 9_772_000
MAPS = 32
PER_STRATUM = 16
EDGES = (0.100, 0.200, 0.240, 0.260, 0.280, 0.300, 0.320, 0.340)


def phase(turn: int) -> str | None:
    if turn < 100:
        return "early"
    if turn >= 200:
        return "late"
    return None


def gap_bin(gap: float) -> str | None:
    for index, (lower, upper) in enumerate(zip(EDGES, EDGES[1:])):
        inside = lower <= gap <= upper if index == len(EDGES) - 2 else lower <= gap < upper
        if inside:
            return f"gap_{int(lower * 1000):03d}_{int(upper * 1000):03d}"
    return None


def identity(row: dict) -> tuple[int, int, int, int]:
    return (
        row["map_seed"],
        row["seat"],
        row["opponent_index"],
        row["decision_ordinal"],
    )


def state_hash(row: dict) -> str:
    return hashlib.sha256(":".join(map(str, identity(row))).encode()).hexdigest()


def select_rows(rows: list[dict]) -> list[dict]:
    strata: dict[tuple[str, str, str], list[dict]] = collections.defaultdict(list)
    for row in rows:
        strata[(row["cohort"], row["phase"], row["opponent"])].append(row)
    selected = []
    for _, bucket in sorted(strata.items()):
        by_task: dict[int, dict] = {}
        for row in bucket:
            current = by_task.get(row["task_index"])
            if current is None or (state_hash(row), identity(row)) < (
                state_hash(current),
                identity(current),
            ):
                by_task[row["task_index"]] = row
        chosen = sorted(by_task.values(), key=lambda row: (state_hash(row), identity(row)))[
            :PER_STRATUM
        ]
        selected.extend({**row, "control_hash": state_hash(row)} for row in chosen)
    selected.sort(
        key=lambda row: (
            row["cohort"],
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
    total_decisions = rate_phase_decisions = in_range_decisions = 0
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
                turn = int(round(float(env.features[slot, 0, 1]) * 300))
                phase_name = phase(turn)
                if (
                    int(env.branches[slot]) != BRANCHES.index("rate")
                    or phase_name is None
                    or count < 2
                ):
                    continue
                rate_phase_decisions += 1
                ranks = env.prior_ranks[slot, :count]
                rank_zero = int(np.flatnonzero(ranks == 0)[0])
                rank_one = int(np.flatnonzero(ranks == 1)[0])
                gap = float(residual[slot, rank_one] - residual[slot, rank_zero])
                bin_name = gap_bin(gap)
                if bin_name is None:
                    continue
                in_range_decisions += 1
                opponent_index = task_index % len(OPPONENTS)
                rows.append(
                    {
                        "cohort": bin_name,
                        "map_seed": SEED_BASE + task_index // TASKS_PER_MAP,
                        "task_index": task_index,
                        "seat": (task_index % TASKS_PER_MAP) // len(OPPONENTS),
                        "opponent_index": opponent_index,
                        "opponent": OPPONENTS[opponent_index],
                        "decision_ordinal": ordinal,
                        "turn": turn,
                        "branch_index": BRANCHES.index("rate"),
                        "branch": "rate",
                        "phase": phase_name,
                        "candidate_count": count,
                        "teacher_action": int(env.actions[slot, rank_zero]),
                        "alternative_action": int(env.actions[slot, rank_one]),
                        "residual_gap": gap,
                    }
                )
            _, _, _, _, info = env.step(env.teacher_actions())
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed.add(terminal["task_index"])
    return rows, {
        "episodes": target_tasks,
        "decisions": total_decisions,
        "early_late_rate_actionable_decisions": rate_phase_decisions,
        "in_range_decisions": in_range_decisions,
    }


def main() -> None:
    for required in (PROTOCOL, CHECKPOINT):
        if not required.exists():
            raise SystemExit(f"missing D41f prerequisite: {required}")
    if sha256(CHECKPOINT) != "1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a":
        raise SystemExit("D41f checkpoint hash mismatch")
    if MANIFEST.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite D41f manifest artifacts")
    saved = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = ExactPriorResidualActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    bank, census = collect_states(model)
    selected = select_rows(bank)
    fields = (
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
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(selected)
    stratum_counts = collections.Counter(
        (row["cohort"], row["phase"], row["opponent"]) for row in selected
    )
    bin_counts = collections.Counter(row["cohort"] for row in selected)
    report = {
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
        "unique_tasks": len({row["task_index"] for row in selected}),
        "bin_counts": dict(sorted(bin_counts.items())),
        "stratum_counts": {"|".join(key): value for key, value in sorted(stratum_counts.items())},
        "selection_outcome_blind": True,
        "at_most_one_state_per_task_stratum": True,
    }
    SUMMARY.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
