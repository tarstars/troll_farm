#!/usr/bin/env python3
"""Build D75's outcome-blind two-batch option-sequence state manifest."""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.rl_batch_option_env import OPPONENTS, TASKS_PER_MAP  # noqa: E402
from cgauto.rl_opening_recurrent_env import (  # noqa: E402
    OPENING_RECURRENT_ACTIONS,
    OPENING_RECURRENT_FEATURES,
    OpeningRecurrentVecEnv,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d75a-two-batch-option-sequence-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d75a-option-sequence-manifest.tsv"
SUMMARY = ANALYSIS / "d75a-option-sequence-manifest-summary.json"
SEED_BASE = 9_813_000
MAPS = 32
PER_STRATUM = 6
FEATURE_FIELDS = tuple(f"feature_{index:02}" for index in range(OPENING_RECURRENT_FEATURES))
FIELDS = (
    "sample_id",
    "partition",
    "map_seed",
    "task_index",
    "seat",
    "opponent_index",
    "opponent",
    "decision_ordinal",
    "turn",
    "phase",
    "legal_mask",
    "feature_hash",
    "selection_hash",
    *FEATURE_FIELDS,
)


def phase(turn: int) -> str:
    return "early" if turn < 100 else ("middle" if turn < 200 else "late")


def identity(row: dict) -> tuple[int, int, int, int]:
    return (
        row["map_seed"],
        row["seat"],
        row["opponent_index"],
        row["decision_ordinal"],
    )


def identity_hash(row: dict) -> str:
    return hashlib.sha256(":".join(map(str, identity(row))).encode()).hexdigest()


def feature_hash(features: np.ndarray) -> str:
    values = np.ascontiguousarray(features, dtype="<f4")
    return hashlib.sha256(values.tobytes()).hexdigest()


def select_rows(bank: list[dict]) -> list[dict]:
    strata: dict[tuple[str, str, int, str], list[dict]] = collections.defaultdict(list)
    for row in bank:
        strata[(row["partition"], row["opponent"], row["seat"], row["phase"])].append(row)
    selected = []
    for _, rows in sorted(strata.items()):
        chosen = sorted(rows, key=lambda row: (identity_hash(row), identity(row)))[
            :PER_STRATUM
        ]
        selected.extend({**row, "selection_hash": identity_hash(row)} for row in chosen)
    selected.sort(
        key=lambda row: (
            row["partition"],
            row["opponent"],
            row["seat"],
            row["phase"],
            identity(row),
        )
    )
    for sample_id, row in enumerate(selected):
        row["sample_id"] = sample_id
    return selected


def collect_bank() -> tuple[list[dict], dict]:
    total_tasks = MAPS * TASKS_PER_MAP
    ordinals: collections.Counter[int] = collections.Counter()
    completed: set[int] = set()
    bank = []
    decisions = unlocked = horizon_exclusions = 0
    with OpeningRecurrentVecEnv(64, SEED_BASE) as env:
        for _ in range(5_000):
            for slot in np.flatnonzero(env.task_indices < total_tasks):
                task_index = int(env.task_indices[slot])
                ordinal = ordinals[task_index]
                ordinals[task_index] += 1
                decisions += 1
                if int(env.masks[slot].sum()) != OPENING_RECURRENT_ACTIONS:
                    continue
                turn = int(round(float(env.features[slot, 1]) * 300.0))
                if turn >= 300:
                    horizon_exclusions += 1
                    continue
                unlocked += 1
                within = task_index % TASKS_PER_MAP
                seat = within // len(OPPONENTS)
                opponent_index = within % len(OPPONENTS)
                map_seed = SEED_BASE + task_index // TASKS_PER_MAP
                features = env.features[slot].copy()
                if not np.isfinite(features).all():
                    raise RuntimeError("non-finite D75 manifest feature")
                if np.any(features[56:64] != 0.0) or features[69] != 0.0:
                    raise RuntimeError("D75 ordinary state reports explicit-source memory")
                if features[70] != 1.0 or features[71] != 0.0:
                    raise RuntimeError("D75 ordinary state reports source-action lifecycle")
                bank.append(
                    {
                        "partition": (
                            "discovery" if map_seed < SEED_BASE + 16 else "validation"
                        ),
                        "map_seed": map_seed,
                        "task_index": task_index,
                        "seat": seat,
                        "opponent_index": opponent_index,
                        "opponent": OPPONENTS[opponent_index],
                        "decision_ordinal": ordinal,
                        "turn": turn,
                        "phase": phase(turn),
                        "legal_mask": "1111",
                        "feature_hash": feature_hash(features),
                        "features": features,
                    }
                )
            _, _, _, info = env.step(np.zeros(64, dtype=np.int32))
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < total_tasks:
                    completed.add(terminal["task_index"])
            if len(completed) == total_tasks:
                break
        else:
            raise RuntimeError("D75 state census exceeded decision guard")
    return bank, {
        "tasks": total_tasks,
        "decisions": decisions,
        "eligible_states": unlocked,
        "horizon_exclusions": horizon_exclusions,
    }


def serialize(rows: list[dict]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        output = {field: row[field] for field in FIELDS[:13]}
        output.update(
            {
                field: f"{float(row['features'][index]):.9g}"
                for index, field in enumerate(FEATURE_FIELDS)
            }
        )
        writer.writerow(output)
    return target.getvalue().encode()


def main() -> int:
    if MANIFEST.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite D75 manifest artifacts")
    bank_a, census_a = collect_bank()
    bank_b, census_b = collect_bank()
    selected_a = select_rows(bank_a)
    selected_b = select_rows(bank_b)
    payload_a = serialize(selected_a)
    payload_b = serialize(selected_b)
    repeat_exact = payload_a == payload_b and census_a == census_b
    if not repeat_exact:
        raise RuntimeError("D75 outcome-blind manifest generation is not deterministic")
    with MANIFEST.open("xb") as target:
        target.write(payload_a)

    partitions = collections.Counter(row["partition"] for row in selected_a)
    strata = collections.Counter(
        (row["partition"], row["opponent"], row["seat"], row["phase"])
        for row in selected_a
    )
    expected_strata = {
        (partition, opponent, seat, phase_name)
        for partition in ("discovery", "validation")
        for opponent in OPPONENTS
        for seat in (0, 1)
        for phase_name in ("early", "middle", "late")
    }
    gates = {
        "repeat_byte_exact": repeat_exact,
        "exactly_576_unique_states": (
            len(selected_a) == 576
            and len({identity(row) for row in selected_a}) == len(selected_a)
        ),
        "exactly_288_each_partition": partitions
        == collections.Counter({"discovery": 288, "validation": 288}),
        "all_partition_opponent_seat_phase_strata": set(strata) == expected_strata,
        "six_rows_each_stratum": all(strata[key] == PER_STRATUM for key in expected_strata),
        "all_features_finite_source_free_and_before_horizon": all(
            row["turn"] < 300
            and np.isfinite(row["features"]).all()
            and np.all(row["features"][56:64] == 0.0)
            and row["features"][69] == 0.0
            and row["features"][70] == 1.0
            and row["features"][71] == 0.0
            for row in selected_a
        ),
    }
    report = {
        "schema": "troll-farm-d75a-option-sequence-manifest-v1",
        "protocol": sha256_file(PROTOCOL),
        "generator": sha256_file(Path(__file__)),
        "seed_base": SEED_BASE,
        "maps": MAPS,
        "quota_per_stratum": PER_STRATUM,
        "census": census_a,
        "samples": len(selected_a),
        "partition_counts": dict(sorted(partitions.items())),
        "stratum_counts": {
            "|".join(map(str, key)): value for key, value in sorted(strata.items())
        },
        "manifest": sha256_file(MANIFEST),
        "gates": gates,
        "pass": all(gates.values()),
        "selection_outcome_blind": True,
    }
    atomic_write_new(SUMMARY, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
