#!/usr/bin/env python3
"""Train and evaluate the frozen D29 canonical spatial option critic."""

from __future__ import annotations

import argparse
import base64
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct

import numpy as np
import torch
from torch import nn


OPPONENTS = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)
STRUCTURAL_FAMILY = {
    "compact_gold": "static_gold",
    "gold_elite": "static_gold",
    "gold_adaptive": "gold_adaptive",
    "mybot": "mybot",
    "printer_bot": "printer_bot",
    "sched_bot": "sched_bot",
    "script_boss": "script_boss",
    "silver_boss": "silver_boss",
}
FAMILIES = tuple(sorted(set(STRUCTURAL_FAMILY.values())))
KEY_FIELDS = ("seed", "seat", "opponent")
SPATIAL_SHAPE = (36, 11, 22)
SPATIAL_SIZE = math.prod(SPATIAL_SHAPE)
PLANE_SCALES = np.asarray(
    [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        4,
        20,
        3,
        9,
        1,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        1,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
    ],
    dtype=np.float32,
).reshape(1, 36, 1, 1)
MODEL_SEED = 2901
BATCH_SIZE = 256
EPOCHS = 30
QUANTILE = 0.25


def robust_summary(values) -> dict:
    values = list(values)
    if not values:
        return {"n": 0, "mean": None, "ci95_normal": [None, None]}
    ordered = sorted(values)
    trim = math.floor(0.05 * len(ordered))
    trimmed = ordered[trim : len(ordered) - trim] if trim else ordered
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "trimmed_5pct_mean": statistics.mean(trimmed),
        "standard_deviation": sd,
        "standard_error": se,
        "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se],
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def row_key(row: dict) -> tuple[int, int, str]:
    return int(row["seed"]), int(row["seat"]), row["opponent"]


def fnv_i16(values: np.ndarray) -> int:
    value = 0xCBF29CE484222325
    for byte in values.astype("<i2", copy=False).tobytes():
        value ^= byte
        value = (value * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def read_spatial(path: Path) -> tuple[dict[tuple, dict], dict]:
    rows = {}
    bad_lengths = 0
    bad_hashes = 0
    bad_shapes = 0
    bad_canonical = 0
    with path.open(newline="") as stream:
        for raw in csv.DictReader(stream, delimiter="\t"):
            key = row_key(raw)
            if key in rows:
                raise ValueError(f"duplicate spatial key: {key}")
            grid = np.fromstring(raw["grid"], sep=",", dtype=np.int16)
            bad_lengths += grid.size != SPATIAL_SIZE or int(raw["grid_len"]) != SPATIAL_SIZE
            bad_shapes += (
                int(raw["grid_channels"]),
                int(raw["grid_height"]),
                int(raw["grid_width"]),
            ) != SPATIAL_SHAPE
            if grid.size == SPATIAL_SIZE:
                bad_hashes += fnv_i16(grid) != int(raw["grid_hash"])
                shaped = grid.reshape(SPATIAL_SHAPE)
                own = np.argwhere(shaped[4] != 0)
                opponent = np.argwhere(shaped[5] != 0)
                if own.shape != (1, 2) or opponent.shape != (1, 2):
                    bad_canonical += 1
                else:
                    own_xy = (int(own[0, 1]), int(own[0, 0]))
                    opponent_xy = (int(opponent[0, 1]), int(opponent[0, 0]))
                    bad_canonical += own_xy >= opponent_xy
            rows[key] = {
                "grid": grid,
                "reached_cut": int(raw["reached_cut"]),
                "root_turn": int(raw["root_turn"]),
                "root_my_score": int(raw["root_my_score"]),
                "root_opponent_score": int(raw["root_opponent_score"]),
                "root_my_wood": int(raw["root_my_wood"]),
                "root_opponent_wood": int(raw["root_opponent_wood"]),
                "root_my_workers": int(raw["root_my_workers"]),
                "root_opponent_workers": int(raw["root_opponent_workers"]),
                "root_plants": int(raw["root_plants"]),
                "rotated": int(raw["rotated"]),
            }
    return rows, {
        "bad_grid_lengths": int(bad_lengths),
        "bad_grid_shapes": int(bad_shapes),
        "bad_grid_hashes": int(bad_hashes),
        "bad_canonical_orientations": int(bad_canonical),
    }


def read_scalars(path: Path) -> tuple[dict[tuple, dict], tuple[str, ...]]:
    rows = {}
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        feature_names = tuple(
            name
            for name in reader.fieldnames or ()
            if name not in {*KEY_FIELDS, "reached_cut"}
        )
        forbidden = [
            name
            for name in feature_names
            if any(token in name for token in ("terminal", "command", "future", "agent_identity"))
        ]
        if forbidden:
            raise ValueError("forbidden scalar features: " + ", ".join(forbidden))
        for raw in reader:
            key = row_key(raw)
            if key in rows:
                raise ValueError(f"duplicate scalar key: {key}")
            values = np.asarray([float(raw[name]) for name in feature_names], dtype=np.float32)
            if not np.isfinite(values).all():
                raise ValueError(f"non-finite scalar feature: {key}")
            rows[key] = {
                "values": values,
                "reached_cut": int(raw["reached_cut"]),
                "raw": raw,
            }
    return rows, feature_names


def read_labels(paths: list[Path]) -> dict[tuple, dict[str, dict]]:
    rows: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for path in paths:
        with path.open(newline="") as stream:
            for raw in csv.DictReader(stream, delimiter="\t"):
                if int(raw["decision_turn"]) != 75 or raw["option"] not in {
                    "resident",
                    "ownership2",
                }:
                    continue
                key = row_key(raw)
                if raw["option"] in rows[key]:
                    raise ValueError(f"duplicate label: {key} / {raw['option']}")
                rows[key][raw["option"]] = raw
    return dict(rows)


def expected_keys(seed_start: int, seed_count: int) -> set[tuple]:
    return {
        (seed, seat, opponent)
        for seed in range(seed_start, seed_start + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }


def build_dataset(
    spatial_rows: dict,
    scalar_rows: dict,
    labels: dict,
    feature_names: tuple[str, ...],
    seed_start: int,
    seed_count: int,
    spatial_checks: dict,
) -> tuple[dict, dict]:
    expected = expected_keys(seed_start, seed_count)
    keys = sorted(expected & set(spatial_rows) & set(scalar_rows) & set(labels))
    bad_label_branches = {
        str(key): sorted(set(branches) ^ {"resident", "ownership2"})
        for key, branches in labels.items()
        if set(branches) != {"resident", "ownership2"}
    }
    root_mismatches = []
    reached_mismatches = []
    for key in keys:
        spatial = spatial_rows[key]
        scalar = scalar_rows[key]
        resident = labels[key]["resident"]
        option = labels[key]["ownership2"]
        reached = [
            spatial["reached_cut"],
            scalar["reached_cut"],
            int(resident["reached_cut"]),
            int(option["reached_cut"]),
        ]
        if len(set(reached)) != 1:
            reached_mismatches.append({"key": key, "values": reached})
        comparisons = {
            "root_turn": (spatial["root_turn"], int(resident["root_turn"])),
            "root_my_score": (spatial["root_my_score"], int(resident["root_my_score"])),
            "root_opponent_score": (
                spatial["root_opponent_score"],
                int(resident["root_opponent_score"]),
            ),
            "root_my_wood": (spatial["root_my_wood"], int(resident["root_my_wood"])),
            "root_opponent_wood": (
                spatial["root_opponent_wood"],
                int(resident["root_opponent_wood"]),
            ),
            "root_my_workers": (
                spatial["root_my_workers"],
                int(resident["root_my_workers"]),
            ),
            "root_opponent_workers": (
                spatial["root_opponent_workers"],
                int(resident["root_opponent_workers"]),
            ),
            "root_plants": (spatial["root_plants"], int(resident["root_plants"])),
            "scalar_my_score": (
                int(float(scalar["raw"]["t75_my_score"])),
                int(resident["root_my_score"]),
            ),
            "scalar_opponent_score": (
                int(float(scalar["raw"]["t75_opponent_score"])),
                int(resident["root_opponent_score"]),
            ),
            "scalar_my_wood": (
                int(float(scalar["raw"]["t75_my_inv_wood"])),
                int(resident["root_my_wood"]),
            ),
            "scalar_opponent_wood": (
                int(float(scalar["raw"]["t75_opponent_inv_wood"])),
                int(resident["root_opponent_wood"]),
            ),
            "scalar_my_workers": (
                int(float(scalar["raw"]["t75_my_workers"])),
                int(resident["root_my_workers"]),
            ),
            "scalar_opponent_workers": (
                int(float(scalar["raw"]["t75_opponent_workers"])),
                int(resident["root_opponent_workers"]),
            ),
            "scalar_plants": (
                int(float(scalar["raw"]["t75_plants"])),
                int(resident["root_plants"]),
            ),
        }
        for field, values in comparisons.items():
            if values[0] != values[1]:
                root_mismatches.append({"key": key, "field": field, "values": values})

    grids = np.stack([spatial_rows[key]["grid"] for key in keys]).reshape(
        -1, *SPATIAL_SHAPE
    )
    scalars = np.stack([scalar_rows[key]["values"] for key in keys])
    resident_margin = np.asarray(
        [int(labels[key]["resident"]["margin"]) for key in keys], dtype=np.int32
    )
    option_margin = np.asarray(
        [int(labels[key]["ownership2"]["margin"]) for key in keys], dtype=np.int32
    )
    resident_score = np.asarray(
        [int(labels[key]["resident"]["my_score"]) for key in keys], dtype=np.int32
    )
    option_score = np.asarray(
        [int(labels[key]["ownership2"]["my_score"]) for key in keys], dtype=np.int32
    )
    target = option_margin - resident_margin
    integrity = {
        "expected_cells": len(expected),
        "joined_cells": len(keys),
        "spatial_cells": len(spatial_rows),
        "scalar_cells": len(scalar_rows),
        "label_cells": len(labels),
        "missing_spatial": len(expected - set(spatial_rows)),
        "missing_scalars": len(expected - set(scalar_rows)),
        "missing_labels": len(expected - set(labels)),
        "unexpected_spatial": len(set(spatial_rows) - expected),
        "unexpected_scalars": len(set(scalar_rows) - expected),
        "unexpected_labels": len(set(labels) - expected),
        "bad_label_branches": bad_label_branches,
        "root_mismatch_count": len(root_mismatches),
        "root_mismatches": root_mismatches[:50],
        "reached_mismatch_count": len(reached_mismatches),
        "reached_mismatches": reached_mismatches[:50],
        "all_reached_cut": all(spatial_rows[key]["reached_cut"] == 1 for key in keys),
        "feature_count": len(feature_names),
        "spatial_shape": list(SPATIAL_SHAPE),
        "spatial_checks": spatial_checks,
        "rotated_by_seat": {
            str(seat): sum(spatial_rows[key]["rotated"] for key in keys if key[1] == seat)
            for seat in (0, 1)
        },
    }
    integrity["complete"] = bool(
        len(keys) == len(expected)
        and set(spatial_rows) == expected
        and set(scalar_rows) == expected
        and set(labels) == expected
        and not bad_label_branches
        and not root_mismatches
        and not reached_mismatches
        and integrity["all_reached_cut"]
        and all(value == 0 for value in spatial_checks.values())
        and bool(np.isfinite(scalars).all())
    )
    data = {
        "keys": keys,
        "grids": grids,
        "scalars": scalars,
        "resident_margin": resident_margin,
        "option_margin": option_margin,
        "resident_score": resident_score,
        "option_score": option_score,
        "target": target,
        "feature_names": feature_names,
    }
    return data, integrity


class SpatialCritic(nn.Module):
    def __init__(self, scalar_count: int):
        super().__init__()
        self.conv1 = nn.Conv2d(36, 8, 3, padding=1)
        self.conv2 = nn.Conv2d(8, 8, 3, padding=1)
        self.scalar = nn.Linear(scalar_count, 8)
        self.hidden = nn.Linear(24, 16)
        self.output = nn.Linear(16, 1)

    def forward(self, spatial: torch.Tensor, scalars: torch.Tensor) -> torch.Tensor:
        mask = spatial[:, :1]
        value = torch.relu(self.conv1(spatial))
        value = torch.relu(self.conv2(value))
        denominator = mask.sum(dim=(2, 3)).clamp_min(1.0)
        mean = (value * mask).sum(dim=(2, 3)) / denominator
        maximum = value.masked_fill(mask == 0, -1e9).amax(dim=(2, 3))
        scalar_value = torch.relu(self.scalar(scalars))
        combined = torch.cat((mean, maximum, scalar_value), dim=1)
        return self.output(torch.relu(self.hidden(combined))).squeeze(1)


def configure_torch() -> None:
    torch.set_num_threads(14)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)


def initialize_model(scalar_count: int) -> SpatialCritic:
    torch.manual_seed(MODEL_SEED)
    model = SpatialCritic(scalar_count)
    parameters = sum(parameter.numel() for parameter in model.parameters())
    if parameters > 8000:
        raise ValueError(f"D29 parameter ceiling exceeded: {parameters}")
    return model


def plane_batch(grids: np.ndarray, indices: np.ndarray) -> torch.Tensor:
    values = torch.from_numpy(grids[indices].astype(np.float32, copy=False))
    return values / torch.from_numpy(PLANE_SCALES)


def train_model(
    data: dict, train_indices: np.ndarray
) -> tuple[SpatialCritic, dict, list[float]]:
    scalar_values = data["scalars"][train_indices].astype(np.float64)
    scalar_mean = scalar_values.mean(axis=0).astype(np.float32)
    scalar_std = scalar_values.std(axis=0).astype(np.float32)
    scalar_std[scalar_std < 1e-6] = 1.0
    target_values = data["target"][train_indices].astype(np.float64)
    target_mean = float(target_values.mean())
    target_std = float(target_values.std())
    if target_std < 1e-6:
        target_std = 1.0

    model = initialize_model(data["scalars"].shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
    losses = []
    ordered = np.sort(train_indices)
    model.train()
    for _ in range(EPOCHS):
        total_loss = 0.0
        total_rows = 0
        for start in range(0, len(ordered), BATCH_SIZE):
            batch = ordered[start : start + BATCH_SIZE]
            spatial = plane_batch(data["grids"], batch)
            scalars = torch.from_numpy(
                (data["scalars"][batch] - scalar_mean) / scalar_std
            )
            target = torch.from_numpy(
                ((data["target"][batch].astype(np.float32) - target_mean) / target_std)
            )
            prediction = model(spatial, scalars)
            error = target - prediction
            loss = torch.maximum(QUANTILE * error, (QUANTILE - 1.0) * error).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.detach()) * len(batch)
            total_rows += len(batch)
        losses.append(total_loss / total_rows)
    metadata = {
        "scalar_mean": scalar_mean,
        "scalar_std": scalar_std,
        "target_mean": target_mean,
        "target_std": target_std,
    }
    return model, metadata, losses


def predict_model(
    model: SpatialCritic, metadata: dict, data: dict, indices: np.ndarray
) -> np.ndarray:
    result = np.empty(len(indices), dtype=np.float32)
    model.eval()
    with torch.no_grad():
        for start in range(0, len(indices), BATCH_SIZE):
            batch = indices[start : start + BATCH_SIZE]
            spatial = plane_batch(data["grids"], batch)
            scalars = torch.from_numpy(
                (data["scalars"][batch] - metadata["scalar_mean"])
                / metadata["scalar_std"]
            )
            normalized = model(spatial, scalars).numpy().astype(np.float32)
            result[start : start + len(batch)] = (
                normalized * metadata["target_std"] + metadata["target_mean"]
            )
    return result


def crossed_predictions(data: dict, seed_start: int) -> tuple[np.ndarray, list[dict]]:
    keys = data["keys"]
    blocks = np.asarray([(key[0] - seed_start) // 100 for key in keys], dtype=np.int8)
    families = np.asarray([STRUCTURAL_FAMILY[key[2]] for key in keys], dtype=object)
    predictions = np.full(len(keys), np.nan, dtype=np.float32)
    folds = []
    for block in range(6):
        for family in FAMILIES:
            test = np.flatnonzero((blocks == block) & (families == family))
            train = np.flatnonzero((blocks != block) & (families != family))
            if not len(test) or not len(train):
                raise ValueError(f"empty D29 fold: block={block}, family={family}")
            model, metadata, losses = train_model(data, train)
            if np.isfinite(predictions[test]).any():
                raise ValueError("overlapping D29 crossed folds")
            predictions[test] = predict_model(model, metadata, data, test)
            folds.append(
                {
                    "block": block,
                    "family": family,
                    "train_rows": len(train),
                    "test_rows": len(test),
                    "first_loss": losses[0],
                    "final_loss": losses[-1],
                }
            )
    if not np.isfinite(predictions).all():
        raise ValueError("incomplete or non-finite D29 predictions")
    return predictions, folds


def seed_cluster(keys: list[tuple], values: np.ndarray) -> list[float]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for key, value in zip(keys, values, strict=True):
        grouped[key[0]].append(float(value))
    return [statistics.mean(grouped[seed]) for seed in sorted(grouped)]


def negative_mass(values: np.ndarray) -> int:
    return int(np.maximum(-values, 0).sum())


def evaluate_policy(
    data: dict,
    predictions: np.ndarray,
    seed_start: int,
    *,
    block_size: int,
    block_count: int,
    precision_floor: float,
) -> dict:
    keys = data["keys"]
    target = data["target"]
    decision = predictions > 0
    selected_delta = np.where(decision, target, 0)
    selected_score_delta = np.where(
        decision, data["option_score"] - data["resident_score"], 0
    )
    terminal_margin = np.where(decision, data["option_margin"], data["resident_margin"])
    switched = int(decision.sum())
    precision = float((target[decision] > 0).mean()) if switched else 0.0
    seed_summary = robust_summary(seed_cluster(keys, selected_delta))
    score_summary = robust_summary(seed_cluster(keys, selected_score_delta))
    opponents = {
        opponent: float(
            selected_delta[[key[2] == opponent for key in keys]].astype(np.float64).mean()
        )
        for opponent in OPPONENTS
    }
    block_ids = np.asarray(
        [(key[0] - seed_start) // block_size for key in keys], dtype=np.int16
    )
    expected_blocks = set(range(block_count))
    if set(block_ids.tolist()) != expected_blocks:
        raise ValueError(
            f"D29 map blocks differ: got {sorted(set(block_ids.tolist()))}, "
            f"expected {sorted(expected_blocks)}"
        )
    blocks = {
        str(block): float(
            selected_delta[block_ids == block].astype(np.float64).mean()
        )
        for block in range(block_count)
    }
    resident_catastrophes = int((data["resident_margin"] <= -100).sum())
    selected_catastrophes = int((terminal_margin <= -100).sum())
    resident_mass = negative_mass(data["resident_margin"])
    selected_mass = negative_mass(terminal_margin)
    oracle_delta = np.maximum(target, 0)
    oracle_mean = statistics.mean(seed_cluster(keys, oracle_delta))
    oracle_capture = seed_summary["mean"] / oracle_mean if oracle_mean else 0.0
    report = {
        "cells": len(keys),
        "seeds": len(set(key[0] for key in keys)),
        "switches": switched,
        "switch_rate": switched / len(keys),
        "positive_cell_precision": precision,
        "selected_positive": int((target[decision] > 0).sum()),
        "selected_zero": int((target[decision] == 0).sum()),
        "selected_negative": int((target[decision] < 0).sum()),
        "seed_clustered_margin_delta": seed_summary,
        "seed_clustered_own_score_delta": score_summary,
        "opponent_mean_margin_deltas": opponents,
        "nonnegative_opponent_means": sum(value >= 0 for value in opponents.values()),
        "worst_opponent": min(opponents, key=opponents.get),
        "worst_opponent_mean_delta": min(opponents.values()),
        "map_block_mean_margin_deltas": blocks,
        "all_map_blocks_nonnegative": all(value >= 0 for value in blocks.values()),
        "tail": {
            "resident_catastrophic_frequency": resident_catastrophes / len(keys),
            "selected_catastrophic_frequency": selected_catastrophes / len(keys),
            "resident_negative_margin_mass": resident_mass,
            "selected_negative_margin_mass": selected_mass,
            "selected_to_resident_negative_mass_ratio": (
                selected_mass / resident_mass
                if resident_mass
                else (0.0 if selected_mass == 0 else None)
            ),
        },
        "oracle": {
            "positive_cell_seed_mean": oracle_mean,
            "captured_fraction": oracle_capture,
        },
        "prediction": {
            "mean": float(predictions.mean()),
            "standard_deviation": float(predictions.std()),
            "minimum": float(predictions.min()),
            "maximum": float(predictions.max()),
        },
    }
    precision_gate = f"precision_at_least_{round(100 * precision_floor)}pct"
    report["gates"] = {
        "switch_rate_5_to_55pct": 0.05 <= report["switch_rate"] <= 0.55,
        precision_gate: precision >= precision_floor,
        "mean_margin_at_least_8": seed_summary["mean"] >= 8,
        "trimmed_margin_at_least_5": seed_summary["trimmed_5pct_mean"] >= 5,
        "ci95_lower_above_zero": seed_summary["ci95_normal"][0] > 0,
        "six_of_eight_opponents_nonnegative": report["nonnegative_opponent_means"] >= 6,
        "worst_opponent_at_least_minus_5": report["worst_opponent_mean_delta"] >= -5,
        "all_map_blocks_nonnegative": report["all_map_blocks_nonnegative"],
        "catastrophic_frequency_not_higher": selected_catastrophes <= resident_catastrophes,
        "negative_margin_mass_not_higher": selected_mass <= resident_mass,
        "oracle_capture_at_least_25pct": oracle_capture >= 0.25,
    }
    report["passed"] = all(report["gates"].values())
    return report


def prediction_hash(predictions: np.ndarray, decisions: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(predictions.astype("<f4", copy=False).tobytes())
    digest.update(decisions.astype(np.uint8, copy=False).tobytes())
    return digest.hexdigest()


def save_predictions(path: Path, data: dict, predictions: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            (
                "seed",
                "seat",
                "opponent",
                "prediction_f32_hex",
                "prediction",
                "switch",
                "target",
                "resident_margin",
                "option_margin",
            )
        )
        for index, key in enumerate(data["keys"]):
            value = np.float32(predictions[index])
            writer.writerow(
                (
                    *key,
                    struct.pack("<f", value).hex(),
                    repr(float(value)),
                    int(value > 0),
                    int(data["target"][index]),
                    int(data["resident_margin"][index]),
                    int(data["option_margin"][index]),
                )
            )
    temporary.replace(path)


def encode_array(array: np.ndarray) -> dict:
    value = np.asarray(array, dtype="<f4")
    return {
        "shape": list(value.shape),
        "data_f32_base64": base64.b64encode(value.tobytes()).decode("ascii"),
    }


def decode_array(payload: dict) -> np.ndarray:
    value = np.frombuffer(base64.b64decode(payload["data_f32_base64"]), dtype="<f4")
    return value.reshape(payload["shape"]).copy()


def save_checkpoint(
    path: Path, model: SpatialCritic, metadata: dict, feature_names: tuple[str, ...]
) -> str:
    payload = {
        "schema": 1,
        "model_seed": MODEL_SEED,
        "epochs": EPOCHS,
        "quantile": QUANTILE,
        "feature_names": feature_names,
        "plane_scales": PLANE_SCALES.reshape(-1).tolist(),
        "scalar_mean": encode_array(metadata["scalar_mean"]),
        "scalar_std": encode_array(metadata["scalar_std"]),
        "target_mean": metadata["target_mean"],
        "target_std": metadata["target_std"],
        "state": {
            name: encode_array(value.detach().numpy())
            for name, value in sorted(model.state_dict().items())
        },
    }
    encoded = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return hashlib.sha256(encoded).hexdigest()


def load_checkpoint(
    path: Path, feature_names: tuple[str, ...]
) -> tuple[SpatialCritic, dict, dict]:
    payload = json.loads(path.read_text())
    if tuple(payload["feature_names"]) != feature_names:
        raise ValueError("D29 checkpoint feature names differ")
    model = initialize_model(len(feature_names))
    state = {name: torch.from_numpy(decode_array(value)) for name, value in payload["state"].items()}
    model.load_state_dict(state)
    metadata = {
        "scalar_mean": decode_array(payload["scalar_mean"]),
        "scalar_std": decode_array(payload["scalar_std"]),
        "target_mean": float(payload["target_mean"]),
        "target_std": float(payload["target_std"]),
    }
    return model, metadata, payload


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spatial", type=Path, required=True)
    parser.add_argument("--scalar", type=Path, required=True)
    parser.add_argument("--labels", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--mode", choices=("smoke", "development", "confirmation"), required=True)
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--repeat-spatial", type=Path)
    parser.add_argument(
        "--repeat-predictions",
        type=Path,
        help="first-run development prediction artifact for exact rerun comparison",
    )
    args = parser.parse_args()

    configure_torch()
    spatial_rows, spatial_checks = read_spatial(args.spatial)
    scalar_rows, feature_names = read_scalars(args.scalar)
    labels = read_labels(args.labels)
    data, integrity = build_dataset(
        spatial_rows,
        scalar_rows,
        labels,
        feature_names,
        args.seed_start,
        args.seed_count,
        spatial_checks,
    )
    model_probe = initialize_model(len(feature_names))
    integrity["trainable_parameters"] = sum(
        parameter.numel() for parameter in model_probe.parameters()
    )
    integrity["parameter_ceiling_passed"] = integrity["trainable_parameters"] <= 8000
    if args.repeat_spatial:
        integrity["repeat_spatial_path"] = str(args.repeat_spatial)
        integrity["repeat_spatial_byte_identical"] = (
            args.spatial.read_bytes() == args.repeat_spatial.read_bytes()
        )
    else:
        integrity["repeat_spatial_path"] = None
        integrity["repeat_spatial_byte_identical"] = None
    integrity["readiness_passed"] = (
        integrity["complete"]
        and integrity["parameter_ceiling_passed"]
        and (args.mode != "smoke" or integrity["repeat_spatial_byte_identical"] is True)
    )

    payload = {
        "schema": 1,
        "scope": "D29 canonical spatial resident/farm option critic; no candidate, submission, or Arena action",
        "mode": args.mode,
        "sources": {
            "spatial": str(args.spatial),
            "scalar": str(args.scalar),
            "labels": [str(path) for path in args.labels],
        },
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "model": {
            "seed": MODEL_SEED,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "quantile": QUANTILE,
            "feature_count": len(feature_names),
            "trainable_parameters": integrity["trainable_parameters"],
        },
        "integrity": integrity,
        "evaluation": None,
        "folds": None,
        "prediction_hash": None,
        "checkpoint": None,
        "decision": None,
    }

    if args.mode == "smoke":
        payload["decision"] = {
            "open_development": integrity["readiness_passed"],
            "train_on_smoke": False,
        }
    elif args.mode == "development":
        if args.seed_count != 600:
            raise SystemExit("D29 development requires exactly 600 maps")
        if not args.predictions:
            raise SystemExit("D29 development requires --predictions")
        if not integrity["readiness_passed"]:
            raise SystemExit("D29 development integrity failed before training")
        predictions, folds = crossed_predictions(data, args.seed_start)
        report = evaluate_policy(
            data,
            predictions,
            args.seed_start,
            block_size=100,
            block_count=6,
            precision_floor=0.78,
        )
        base_passed = report["passed"]
        decisions = predictions > 0
        digest = prediction_hash(predictions, decisions)
        if args.repeat_predictions:
            if args.repeat_predictions.resolve() == args.predictions.resolve():
                raise SystemExit(
                    "--repeat-predictions must differ from the current --predictions path"
                )
            if not args.repeat_predictions.is_file():
                raise SystemExit("D29 repeat prediction reference does not exist")
        save_predictions(args.predictions, data, predictions)
        repeat_exact = (
            args.predictions.read_bytes() == args.repeat_predictions.read_bytes()
            if args.repeat_predictions
            else None
        )
        report["base_passed"] = base_passed
        report["reproducibility"] = {
            "reference_path": (
                str(args.repeat_predictions) if args.repeat_predictions else None
            ),
            "prediction_artifact_byte_identical": repeat_exact,
        }
        report["gates"]["repeat_predictions_exact"] = repeat_exact is True
        report["passed"] = all(report["gates"].values())
        payload["evaluation"] = report
        payload["folds"] = folds
        payload["prediction_hash"] = digest
        checkpoint = None
        if report["passed"]:
            if not args.checkpoint:
                raise SystemExit("passing D29 development requires --checkpoint")
            model, metadata, losses = train_model(data, np.arange(len(data["keys"])))
            checkpoint = {
                "path": str(args.checkpoint),
                "sha256": save_checkpoint(args.checkpoint, model, metadata, feature_names),
                "first_loss": losses[0],
                "final_loss": losses[-1],
            }
        payload["checkpoint"] = checkpoint
        payload["decision"] = {
            "open_confirmation": report["passed"],
            "checkpoint_written": checkpoint is not None,
            "await_exact_rerun": base_passed and repeat_exact is None,
        }
    else:
        if not args.predictions or not args.checkpoint:
            raise SystemExit("D29 confirmation requires --predictions and --checkpoint")
        if not integrity["readiness_passed"]:
            raise SystemExit("D29 confirmation integrity failed")
        model, metadata, checkpoint_payload = load_checkpoint(args.checkpoint, feature_names)
        predictions = predict_model(
            model, metadata, data, np.arange(len(data["keys"]))
        )
        report = evaluate_policy(
            data,
            predictions,
            args.seed_start,
            block_size=20,
            block_count=6,
            precision_floor=0.75,
        )
        report["confirmation_20_map_block_means"] = report[
            "map_block_mean_margin_deltas"
        ]
        report["confirmation_gates"] = dict(report["gates"])
        report["confirmation_passed"] = report["passed"]
        digest = prediction_hash(predictions, predictions > 0)
        save_predictions(args.predictions, data, predictions)
        payload["evaluation"] = report
        payload["prediction_hash"] = digest
        payload["checkpoint"] = {
            "path": str(args.checkpoint),
            "sha256": hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
            "model_seed": checkpoint_payload["model_seed"],
        }
        payload["decision"] = {
            "deployment_feasibility_authorized": report["confirmation_passed"]
        }

    save_json(args.output, payload)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "integrity": integrity,
                "evaluation": payload["evaluation"],
                "prediction_hash": payload["prediction_hash"],
                "checkpoint": payload["checkpoint"],
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
