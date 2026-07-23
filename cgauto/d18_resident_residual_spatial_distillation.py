#!/usr/bin/env python3
"""Fresh-map validation of compact spatial MC-teacher distillation."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d17_resident_residual_precision_distillation import (  # noqa: E402
    feature_names as scalar_feature_names,
    matrix as scalar_matrix,
    quantile_threshold,
    read_rows,
    selection_report,
)
from cgauto.rl_resident_residual_env import (  # noqa: E402
    ACTION_PLANES,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
)


MODEL_SEEDS = (1801, 1802)
SELECTION_RATES = (0.005, 0.01, 0.02, 0.04, 0.08)
VALIDATION_RANGE = range(408_000, 408_480)
PLANT_BASES = (31, 37, 43, 49)
TARGET_NAMES = (
    "own_shack_access",
    "opponent_shack_access",
    "iron_access",
    "empty_wet",
    "other_own_worker",
    "opponent_worker",
    "plum_plant",
    "lemon_plant",
    "apple_plant",
    "banana_plant",
    "ripe_plum",
    "ripe_lemon",
    "ripe_apple",
    "ripe_banana",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def neighbors(index: int) -> tuple[int, ...]:
    y, x = divmod(index, OBS_WIDTH)
    values = []
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < OBS_WIDTH and 0 <= ny < OBS_HEIGHT:
            values.append(ny * OBS_WIDTH + nx)
    return tuple(values)


NEIGHBORS = tuple(neighbors(index) for index in range(OBS_HEIGHT * OBS_WIDTH))


def adjacent(mask: np.ndarray, walkable: np.ndarray) -> np.ndarray:
    result = np.zeros_like(mask, dtype=bool)
    for source in np.flatnonzero(mask):
        for target in NEIGHBORS[int(source)]:
            if walkable[target]:
                result[target] = True
    return result


def distance_from_active(walkable: np.ndarray, active: int) -> np.ndarray:
    distance = np.full(OBS_HEIGHT * OBS_WIDTH, -1, dtype=np.int16)
    distance[active] = 0
    queue = deque([active])
    while queue:
        source = queue.popleft()
        for target in NEIGHBORS[source]:
            if walkable[target] and distance[target] < 0:
                distance[target] = distance[source] + 1
                queue.append(target)
    return distance


def geometry_feature_names() -> list[str]:
    names = [
        "valid_cells",
        "walkable_cells",
        "water_cells",
        "iron_cells",
        "active_walkable_degree",
    ]
    for target in TARGET_NAMES:
        names.extend(
            (
                f"{target}_minimum_distance",
                f"{target}_reachable_count",
                f"{target}_within3",
                f"{target}_within6",
            )
        )
    return names


def geometry_feature_row(observation: np.ndarray) -> list[float]:
    if observation.shape != (OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH):
        raise ValueError(f"invalid observation shape {observation.shape}")
    flat = observation.reshape(OBS_CHANNELS, -1)
    valid = flat[0] > 0
    walkable = flat[1] > 0
    active_cells = np.flatnonzero(flat[6])
    if len(active_cells) != 1:
        raise ValueError(f"expected one active cell, found {len(active_cells)}")
    active = int(active_cells[0])
    distance = distance_from_active(walkable, active)
    plant_masks = [flat[base] > 0 for base in PLANT_BASES]
    any_plant = np.logical_or.reduce(plant_masks)
    wet = adjacent(flat[3] > 0, walkable)
    other_own = flat[7] > 0
    other_own = other_own.copy()
    other_own[active] = False
    targets = [
        adjacent(flat[4] > 0, walkable),
        adjacent(flat[5] > 0, walkable),
        adjacent(flat[2] > 0, walkable),
        wet & ~any_plant,
        other_own,
        flat[8] > 0,
        *plant_masks,
        *(plant & (flat[base + 3] > 0) for plant, base in zip(plant_masks, PLANT_BASES, strict=True)),
    ]
    values = [
        float(valid.sum()) / (OBS_HEIGHT * OBS_WIDTH),
        float(walkable.sum()) / (OBS_HEIGHT * OBS_WIDTH),
        float(np.count_nonzero(flat[3])) / 64.0,
        float(np.count_nonzero(flat[2])) / 64.0,
        sum(walkable[target] for target in NEIGHBORS[active]) / 4.0,
    ]
    for target in targets:
        reachable = distance[target & (distance >= 0)]
        values.extend(
            (
                min(float(reachable.min()) / 32.0, 1.0) if len(reachable) else 1.0,
                min(float(len(reachable)) / 64.0, 1.0),
                min(float(np.sum(reachable <= 3)) / 16.0, 1.0),
                min(float(np.sum(reachable <= 6)) / 32.0, 1.0),
            )
        )
    if len(values) != len(geometry_feature_names()):
        raise AssertionError("geometry feature schema mismatch")
    return values


def geometry_matrix(observations: np.ndarray) -> np.ndarray:
    return np.asarray(
        [geometry_feature_row(observation) for observation in observations],
        dtype=np.float32,
    )


class GeometryMlp(nn.Module):
    def __init__(self, inputs: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(inputs, 24),
            nn.Tanh(),
            nn.Linear(24, 12),
            nn.Tanh(),
            nn.Linear(12, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)


class TinySpatialScorer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.stem = nn.Conv2d(OBS_CHANNELS, 4, 3, padding=1)
        self.middle = nn.Conv2d(4, 4, 3, padding=2, dilation=2)
        self.far = nn.Conv2d(4, 4, 3, padding=4, dilation=4)
        self.actor = nn.Linear(12, ACTION_PLANES)

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        observations = observations.float() * (1.0 / 255.0)
        valid = observations[:, :1]
        active = observations[:, 6:7]
        hidden = F.relu(self.stem(observations))
        hidden = F.relu(hidden + self.middle(hidden))
        hidden = F.relu(hidden + self.far(hidden))
        local = (hidden * active).sum(dim=(2, 3))
        mean = (hidden * valid).sum(dim=(2, 3)) / valid.sum(dim=(2, 3)).clamp_min(1.0)
        masked = hidden.masked_fill(valid == 0, -torch.inf)
        maximum = masked.amax(dim=(2, 3))
        return self.actor(torch.cat((local, mean, maximum), dim=1))


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def weighted_loss(
    prediction: torch.Tensor,
    advantage: torch.Tensor,
    *,
    binary: bool,
    positive_weight: float,
) -> torch.Tensor:
    if binary:
        target = (advantage > 0).float()
        raw = F.binary_cross_entropy_with_logits(prediction, target, reduction="none")
        negative_cost = 1.0 + (-advantage).clamp(0, 32) / 8.0
        weight = torch.where(
            target.bool(), torch.full_like(target, positive_weight), negative_cost
        )
        return (raw * weight).mean()
    target = advantage.clamp(-32, 32) / 16.0
    weight = 1.0 + advantage.abs().clamp(0, 32) / 16.0
    return (F.smooth_l1_loss(prediction, target, reduction="none") * weight).mean()


def train_geometry(
    family: str,
    seed: int,
    features: np.ndarray,
    advantages: np.ndarray,
) -> GeometryMlp:
    torch.manual_seed(seed)
    model = GeometryMlp(features.shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-4)
    x = torch.from_numpy(features)
    y = torch.from_numpy(advantages.astype(np.float32, copy=False))
    positive_weight = float(np.sum(advantages <= 0) / max(np.sum(advantages > 0), 1))
    generator = torch.Generator().manual_seed(seed ^ 0xD18)
    for _ in range(64):
        order = torch.randperm(len(features), generator=generator)
        for start in range(0, len(features), 1024):
            indexes = order[start : start + 1024]
            loss = weighted_loss(
                model(x[indexes]),
                y[indexes],
                binary=family.endswith("binary"),
                positive_weight=positive_weight,
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()
    return model


def train_spatial(
    family: str,
    seed: int,
    observations: np.ndarray,
    advantages: np.ndarray,
    planes: np.ndarray,
) -> TinySpatialScorer:
    torch.manual_seed(seed)
    model = TinySpatialScorer()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    y = torch.from_numpy(advantages.astype(np.float32, copy=False))
    action_planes = torch.from_numpy(planes.astype(np.int64, copy=False))
    positive_weight = float(np.sum(advantages <= 0) / max(np.sum(advantages > 0), 1))
    rng = np.random.default_rng(seed ^ 0xD18)
    for _ in range(20):
        order = rng.permutation(len(observations))
        for start in range(0, len(observations), 256):
            indexes_np = order[start : start + 256]
            indexes = torch.from_numpy(indexes_np)
            batch = torch.from_numpy(np.asarray(observations[indexes_np]))
            logits = model(batch)
            prediction = logits.gather(1, action_planes[indexes, None]).squeeze(1)
            loss = weighted_loss(
                prediction,
                y[indexes],
                binary=family.endswith("binary"),
                positive_weight=positive_weight,
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()
    return model


@torch.inference_mode()
def geometry_scores(model: nn.Module, family: str, features: np.ndarray) -> np.ndarray:
    raw = model(torch.from_numpy(features)).numpy()
    return normalize_scores(raw, family)


@torch.inference_mode()
def spatial_scores(
    model: TinySpatialScorer,
    family: str,
    observations: np.ndarray,
    planes: np.ndarray,
) -> np.ndarray:
    result = []
    for start in range(0, len(observations), 512):
        batch = torch.from_numpy(np.asarray(observations[start : start + 512]))
        logits = model(batch).numpy()
        indexes = np.arange(len(logits))
        result.append(logits[indexes, planes[start : start + len(logits)]])
    return normalize_scores(np.concatenate(result), family)


def normalize_scores(raw: np.ndarray, family: str) -> np.ndarray:
    if family.endswith("binary"):
        return 1.0 / (1.0 + np.exp(-np.clip(raw, -30, 30)))
    return raw * 16.0


def validation_eligible(report: dict, parameters: int) -> tuple[bool, dict]:
    gates = {
        "selected_at_least_72": report["selected"] >= 72,
        "selection_rate_at_most_8_percent": report["selection_rate"] <= 0.08,
        "precision_at_least_70_percent": report["precision"] >= 0.70,
        "conditional_mean_at_least_plus2": report["conditional_mean_advantage"] >= 2.0,
        "map_bootstrap_lower_bound_positive": report["map_bootstrap"]["ci95"][0] > 0,
        "no_new_catastrophe": report["new_catastrophes"] == 0,
        "positive_on_at_least_12_maps": report["positive_maps"] >= 12,
        "positive_against_at_least_4_opponents": report["positive_opponents"] >= 4,
        "positive_in_both_roles": {0, 1}.issubset(report["positive_roles"]),
        "parameters_at_most_10000": parameters <= 10_000,
        "estimated_int8_bytes_at_most_10000": parameters <= 10_000,
    }
    return all(gates.values()), gates


def model_payload(model: nn.Module, family: str, seed: int) -> dict:
    return {
        "family": family,
        "seed": seed,
        "parameters": parameter_count(model),
        "state": {
            name: tensor.detach().cpu().tolist()
            for name, tensor in model.state_dict().items()
        },
    }


def load_observations(paths: list[Path], expected_rows: list[int]) -> np.ndarray:
    arrays = [np.load(path, mmap_mode="r") for path in paths]
    for path, array, rows in zip(paths, arrays, expected_rows, strict=True):
        expected = (rows, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH)
        if array.shape != expected or array.dtype != np.uint8:
            raise ValueError(f"{path}: expected uint8 {expected}, found {array.dtype} {array.shape}")
    return np.concatenate(arrays, axis=0)


def validate_fresh_rows(rows: list[dict]) -> None:
    scenarios = {row["scenario"] for row in rows}
    if len(rows) != 5_760 or scenarios != set(VALIDATION_RANGE):
        raise ValueError("incomplete D18 fresh-validation block")
    if len({row["map_seed"] for row in rows}) != 40:
        raise ValueError("D18 validation must contain 40 maps")


def analyze(
    train_rows: list[dict],
    train_observations: np.ndarray,
    validation_rows: list[dict],
    validation_observations: np.ndarray,
) -> dict:
    validate_fresh_rows(validation_rows)
    train_maps = {row["map_seed"] for row in train_rows}
    validation_maps = {row["map_seed"] for row in validation_rows}
    if train_maps & validation_maps:
        raise ValueError("D18 train/validation map overlap")
    if len(train_rows) != len(train_observations):
        raise ValueError("training label/observation length mismatch")
    if len(validation_rows) != len(validation_observations):
        raise ValueError("validation label/observation length mismatch")

    train_geometry_features = np.concatenate(
        (scalar_matrix(train_rows), geometry_matrix(train_observations)), axis=1
    )
    validation_geometry_features = np.concatenate(
        (scalar_matrix(validation_rows), geometry_matrix(validation_observations)), axis=1
    )
    train_advantages = np.asarray(
        [row["margin_advantage"] for row in train_rows], dtype=np.float32
    )
    train_planes = np.asarray(
        [row["alternative_plane"] for row in train_rows], dtype=np.int64
    )
    validation_planes = np.asarray(
        [row["alternative_plane"] for row in validation_rows], dtype=np.int64
    )
    models = {}
    scores = {}
    for family in ("geometry_binary", "geometry_value"):
        for seed in MODEL_SEEDS:
            name = f"{family}_s{seed}"
            model = train_geometry(
                family, seed, train_geometry_features, train_advantages
            )
            models[name] = (family, seed, model)
            scores[name] = geometry_scores(
                model, family, validation_geometry_features
            )
    for family in ("spatial_binary", "spatial_value"):
        for seed in MODEL_SEEDS:
            name = f"{family}_s{seed}"
            model = train_spatial(
                family, seed, train_observations, train_advantages, train_planes
            )
            models[name] = (family, seed, model)
            scores[name] = spatial_scores(
                model, family, validation_observations, validation_planes
            )

    reports = []
    for name, values in sorted(scores.items()):
        parameters = parameter_count(models[name][2])
        for rate in SELECTION_RATES:
            threshold = quantile_threshold(values, rate)
            report = selection_report(validation_rows, values >= threshold)
            eligible, gates = validation_eligible(report, parameters)
            reports.append(
                {
                    "model": name,
                    "target_selection_rate": rate,
                    "threshold": threshold,
                    "parameters": parameters,
                    "report": report,
                    "gates": gates,
                    "eligible": eligible,
                }
            )
    lexical_rank = {name: -index for index, name in enumerate(sorted(scores))}
    eligible = [report for report in reports if report["eligible"]]
    eligible.sort(
        key=lambda item: (
            item["report"]["map_bootstrap"]["ci95"][0],
            item["report"]["conditional_mean_advantage"],
            item["report"]["selected"],
            -item["parameters"],
            lexical_rank[item["model"]],
        ),
        reverse=True,
    )
    selected = eligible[0] if eligible else None
    selected_model = None
    if selected is not None:
        family, seed, model = models[selected["model"]]
        selected_model = {
            "model": selected["model"],
            "threshold": selected["threshold"],
            **model_payload(model, family, seed),
            "estimated_int8_payload_bytes": parameter_count(model),
        }
    reports.sort(
        key=lambda item: (
            item["eligible"],
            item["report"]["map_bootstrap"]["ci95"][0],
            item["report"]["conditional_mean_advantage"],
        ),
        reverse=True,
    )
    return {
        "schema": 1,
        "scope": (
            "D18 fresh-map validation of geometry-augmented and tiny spatial exact-MC "
            "distillation; no locked test, policy, candidate, submission, or Arena activity"
        ),
        "features": {
            "scalar": len(scalar_feature_names()),
            "geometry": len(geometry_feature_names()),
            "geometry_total": train_geometry_features.shape[1],
            "geometry_names": geometry_feature_names(),
            "spatial_shape": [OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH],
        },
        "corpus": {
            "train_rows": len(train_rows),
            "train_maps": len(train_maps),
            "validation_rows": len(validation_rows),
            "validation_maps": len(validation_maps),
            "train_positive": int(np.sum(train_advantages > 0)),
            "validation_positive": sum(
                row["margin_advantage"] > 0 for row in validation_rows
            ),
        },
        "models": {
            name: {
                "family": family,
                "seed": seed,
                "parameters": parameter_count(model),
            }
            for name, (family, seed, model) in sorted(models.items())
        },
        "validation": {
            "eligible_thresholds": len(eligible),
            "selected": selected,
            "top_thresholds": reports[:20],
        },
        "selected_model": selected_model,
        "decision": {
            "authorize_fresh_locked_test": selected is not None,
            "authorize_exact_policy_prototype": False,
            "authorize_source_integration": False,
            "authorize_candidate": False,
            "authorize_submission": False,
            "authorize_arena": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-labels", type=Path, action="append", required=True)
    parser.add_argument("--train-observations", type=Path, action="append", required=True)
    parser.add_argument("--validation-labels", type=Path, required=True)
    parser.add_argument("--validation-observations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    if len(args.train_labels) != len(args.train_observations):
        raise ValueError("each training label file needs one observation file")
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(2, args.threads))
    train_groups = [read_rows(path) for path in args.train_labels]
    train_rows = [row for group in train_groups for row in group]
    train_observations = load_observations(
        args.train_observations, [len(group) for group in train_groups]
    )
    validation_rows = read_rows(args.validation_labels)
    validation_observations = load_observations(
        [args.validation_observations], [len(validation_rows)]
    )
    payload = analyze(
        train_rows, train_observations, validation_rows, validation_observations
    )
    payload["source"] = {
        "train_labels": [str(path) for path in args.train_labels],
        "train_label_sha256": [sha256(path) for path in args.train_labels],
        "train_observations": [str(path) for path in args.train_observations],
        "train_observation_sha256": [sha256(path) for path in args.train_observations],
        "validation_labels": str(args.validation_labels),
        "validation_label_sha256": sha256(args.validation_labels),
        "validation_observations": str(args.validation_observations),
        "validation_observation_sha256": sha256(args.validation_observations),
        "analyzer": str(Path(__file__).relative_to(REPO)),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "features": payload["features"],
                "corpus": payload["corpus"],
                "models": payload["models"],
                "validation": {
                    "eligible_thresholds": payload["validation"]["eligible_thresholds"],
                    "selected": payload["validation"]["selected"],
                    "top_thresholds": payload["validation"]["top_thresholds"][:5],
                },
                "decision": payload["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
