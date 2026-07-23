#!/usr/bin/env python3
"""Research-capacity and oracle-opponent diagnostic for residual MC labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
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
    matrix as scalar_matrix,
    quantile_threshold,
    read_rows,
    selection_report,
)
from cgauto.d18_resident_residual_spatial_distillation import (  # noqa: E402
    geometry_matrix,
    load_observations,
    weighted_loss,
)
from cgauto.rl_resident_residual_env import (  # noqa: E402
    ACTION_PLANES,
    OBS_CHANNELS,
    OPPONENTS,
)


MODEL_SEEDS = (1901, 1902)
SELECTION_RATES = (0.005, 0.01, 0.02, 0.04, 0.08)
_GEOMETRY_SOURCE: np.ndarray | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _geometry_chunk(bounds: tuple[int, int]) -> np.ndarray:
    if _GEOMETRY_SOURCE is None:
        raise RuntimeError("geometry worker has no inherited source")
    start, stop = bounds
    return geometry_matrix(_GEOMETRY_SOURCE[start:stop])


def parallel_geometry_matrix(observations: np.ndarray, workers: int) -> np.ndarray:
    global _GEOMETRY_SOURCE
    workers = max(1, min(workers, len(observations)))
    if workers == 1:
        return geometry_matrix(observations)
    boundaries = np.linspace(0, len(observations), workers + 1, dtype=int)
    ranges = [
        (int(boundaries[index]), int(boundaries[index + 1]))
        for index in range(workers)
        if boundaries[index] < boundaries[index + 1]
    ]
    _GEOMETRY_SOURCE = observations
    try:
        context = multiprocessing.get_context("fork")
        with context.Pool(len(ranges)) as pool:
            chunks = pool.map(_geometry_chunk, ranges)
    finally:
        _GEOMETRY_SOURCE = None
    return np.concatenate(chunks, axis=0)


class LargeGeometryMlp(nn.Module):
    def __init__(self, inputs: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(inputs, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)


class LargeSpatialScorer(nn.Module):
    def __init__(self, *, oracle: bool) -> None:
        super().__init__()
        self.oracle = oracle
        self.stem = nn.Conv2d(OBS_CHANNELS, 12, 3, padding=1)
        self.middle = nn.Conv2d(12, 12, 3, padding=2, dilation=2)
        self.far = nn.Conv2d(12, 12, 3, padding=4, dilation=4)
        inputs = 36 + (len(OPPONENTS) if oracle else 0)
        self.actor = nn.Sequential(
            nn.Linear(inputs, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, ACTION_PLANES),
        )

    def forward(
        self, observations: torch.Tensor, opponents: torch.Tensor
    ) -> torch.Tensor:
        observations = observations.float() * (1.0 / 255.0)
        valid = observations[:, :1]
        active = observations[:, 6:7]
        hidden = F.relu(self.stem(observations))
        hidden = F.relu(hidden + self.middle(hidden))
        hidden = F.relu(hidden + self.far(hidden))
        local = (hidden * active).sum(dim=(2, 3))
        mean = (hidden * valid).sum(dim=(2, 3)) / valid.sum(dim=(2, 3)).clamp_min(1.0)
        maximum = hidden.masked_fill(valid == 0, -torch.inf).amax(dim=(2, 3))
        context = torch.cat((local, mean, maximum), dim=1)
        if self.oracle:
            context = torch.cat((context, opponents), dim=1)
        return self.actor(context)


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def opponent_matrix(rows: list[dict]) -> np.ndarray:
    index = {opponent: value for value, opponent in enumerate(OPPONENTS)}
    result = np.zeros((len(rows), len(OPPONENTS)), dtype=np.float32)
    for row_index, row in enumerate(rows):
        result[row_index, index[row["opponent"]]] = 1.0
    return result


def train_geometry(
    seed: int,
    features: np.ndarray,
    advantages: np.ndarray,
) -> LargeGeometryMlp:
    torch.manual_seed(seed)
    model = LargeGeometryMlp(features.shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    x = torch.from_numpy(features)
    y = torch.from_numpy(advantages.astype(np.float32, copy=False))
    positive_weight = float(np.sum(advantages <= 0) / max(np.sum(advantages > 0), 1))
    generator = torch.Generator().manual_seed(seed ^ 0xD19)
    for _ in range(80):
        order = torch.randperm(len(features), generator=generator)
        for start in range(0, len(features), 1024):
            indexes = order[start : start + 1024]
            loss = weighted_loss(
                model(x[indexes]),
                y[indexes],
                binary=True,
                positive_weight=positive_weight,
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()
    return model


def train_spatial(
    seed: int,
    observations: np.ndarray,
    opponents: np.ndarray,
    advantages: np.ndarray,
    planes: np.ndarray,
    *,
    oracle: bool,
) -> LargeSpatialScorer:
    torch.manual_seed(seed)
    model = LargeSpatialScorer(oracle=oracle)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0015, weight_decay=1e-4)
    y = torch.from_numpy(advantages.astype(np.float32, copy=False))
    plane_tensor = torch.from_numpy(planes.astype(np.int64, copy=False))
    opponent_tensor = torch.from_numpy(opponents)
    positive_weight = float(np.sum(advantages <= 0) / max(np.sum(advantages > 0), 1))
    rng = np.random.default_rng(seed ^ 0xD19)
    for _ in range(30):
        order = rng.permutation(len(observations))
        for start in range(0, len(observations), 256):
            indexes_np = order[start : start + 256]
            indexes = torch.from_numpy(indexes_np)
            batch = torch.from_numpy(np.asarray(observations[indexes_np]))
            logits = model(batch, opponent_tensor[indexes])
            prediction = logits.gather(1, plane_tensor[indexes, None]).squeeze(1)
            loss = weighted_loss(
                prediction,
                y[indexes],
                binary=True,
                positive_weight=positive_weight,
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()
    return model


@torch.inference_mode()
def geometry_scores(model: nn.Module, features: np.ndarray) -> np.ndarray:
    raw = model(torch.from_numpy(features)).numpy()
    return 1.0 / (1.0 + np.exp(-np.clip(raw, -30, 30)))


@torch.inference_mode()
def spatial_scores(
    model: LargeSpatialScorer,
    observations: np.ndarray,
    opponents: np.ndarray,
    planes: np.ndarray,
) -> np.ndarray:
    result = []
    for start in range(0, len(observations), 512):
        stop = min(start + 512, len(observations))
        logits = model(
            torch.from_numpy(np.asarray(observations[start:stop])),
            torch.from_numpy(opponents[start:stop]),
        ).numpy()
        result.append(logits[np.arange(stop - start), planes[start:stop]])
    raw = np.concatenate(result)
    return 1.0 / (1.0 + np.exp(-np.clip(raw, -30, 30)))


def capacity_gate(report: dict) -> tuple[bool, dict]:
    gates = {
        "selected_at_least_72": report["selected"] >= 72,
        "precision_at_least_65_percent": report["precision"] >= 0.65,
        "conditional_mean_positive": report["conditional_mean_advantage"] > 0,
        "map_ci_lower_positive": report["map_bootstrap"]["ci95"][0] > 0,
        "no_new_catastrophe": report["new_catastrophes"] == 0,
        "positive_on_at_least_12_maps": report["positive_maps"] >= 12,
        "positive_against_at_least_4_opponents": report["positive_opponents"] >= 4,
        "positive_in_both_roles": {0, 1}.issubset(report["positive_roles"]),
    }
    return all(gates.values()), gates


def analyze(
    train_rows: list[dict],
    train_observations: np.ndarray,
    validation_rows: list[dict],
    validation_observations: np.ndarray,
    *,
    geometry_workers: int,
    torch_threads: int,
) -> dict:
    train_geometry_features = np.concatenate(
        (
            scalar_matrix(train_rows),
            parallel_geometry_matrix(train_observations, geometry_workers),
        ),
        axis=1,
    )
    validation_geometry_features = np.concatenate(
        (
            scalar_matrix(validation_rows),
            parallel_geometry_matrix(validation_observations, geometry_workers),
        ),
        axis=1,
    )
    torch.set_num_threads(torch_threads)
    torch.set_num_interop_threads(min(2, torch_threads))
    train_opponents = opponent_matrix(train_rows)
    validation_opponents = opponent_matrix(validation_rows)
    advantages = np.asarray(
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
    for oracle in (False, True):
        prefix = "geometry_oracle" if oracle else "geometry_large"
        features = (
            np.concatenate((train_geometry_features, train_opponents), axis=1)
            if oracle
            else train_geometry_features
        )
        held_features = (
            np.concatenate((validation_geometry_features, validation_opponents), axis=1)
            if oracle
            else validation_geometry_features
        )
        for seed in MODEL_SEEDS:
            name = f"{prefix}_s{seed}"
            model = train_geometry(seed, features, advantages)
            models[name] = model
            scores[name] = geometry_scores(model, held_features)
    for oracle in (False, True):
        prefix = "spatial_oracle" if oracle else "spatial_large"
        for seed in MODEL_SEEDS:
            name = f"{prefix}_s{seed}"
            model = train_spatial(
                seed,
                train_observations,
                train_opponents,
                advantages,
                train_planes,
                oracle=oracle,
            )
            models[name] = model
            scores[name] = spatial_scores(
                model,
                validation_observations,
                validation_opponents,
                validation_planes,
            )

    reports = []
    indexed = {}
    for name, values in sorted(scores.items()):
        for rate in SELECTION_RATES:
            threshold = quantile_threshold(values, rate)
            report = selection_report(validation_rows, values >= threshold)
            item = {
                "model": name,
                "target_selection_rate": rate,
                "threshold": threshold,
                "parameters": parameter_count(models[name]),
                "report": report,
            }
            reports.append(item)
            indexed[(name, rate)] = item

    capacity_candidates = []
    for item in reports:
        if "oracle" in item["model"] or item["target_selection_rate"] < 0.02:
            continue
        passed, gates = capacity_gate(item["report"])
        capacity_candidates.append({**item, "gates": gates, "passed": passed})
    capacity_passed = any(item["passed"] for item in capacity_candidates)

    identity_comparisons = []
    for architecture in ("geometry", "spatial"):
        for seed in MODEL_SEEDS:
            base_name = f"{architecture}_large_s{seed}"
            oracle_name = f"{architecture}_oracle_s{seed}"
            for rate in SELECTION_RATES:
                if rate < 0.02:
                    continue
                base = indexed[(base_name, rate)]["report"]
                oracle = indexed[(oracle_name, rate)]["report"]
                gates = {
                    "precision_gain_at_least_10pp": oracle["precision"] - base["precision"] >= 0.10,
                    "conditional_mean_gain_at_least_plus1": (
                        oracle["conditional_mean_advantage"]
                        - base["conditional_mean_advantage"]
                        >= 1.0
                    ),
                    "oracle_map_ci_lower_positive": oracle["map_bootstrap"]["ci95"][0] > 0,
                    "oracle_no_new_catastrophe": oracle["new_catastrophes"] == 0,
                }
                identity_comparisons.append(
                    {
                        "architecture": architecture,
                        "seed": seed,
                        "target_selection_rate": rate,
                        "base_model": base_name,
                        "oracle_model": oracle_name,
                        "base": base,
                        "oracle": oracle,
                        "precision_gain": oracle["precision"] - base["precision"],
                        "conditional_mean_gain": (
                            oracle["conditional_mean_advantage"]
                            - base["conditional_mean_advantage"]
                        ),
                        "gates": gates,
                        "passed": all(gates.values()),
                    }
                )
    identity_passed = any(item["passed"] for item in identity_comparisons)
    reports.sort(
        key=lambda item: (
            item["target_selection_rate"] >= 0.02,
            item["report"]["map_bootstrap"]["ci95"][0],
            item["report"]["precision"],
            item["report"]["conditional_mean_advantage"],
        ),
        reverse=True,
    )
    identity_comparisons.sort(
        key=lambda item: (
            item["passed"],
            item["precision_gain"],
            item["conditional_mean_gain"],
        ),
        reverse=True,
    )
    return {
        "schema": 1,
        "scope": (
            "D19 nondeployable research-capacity and oracle-opponent diagnostic on "
            "already-open D18 data; no held-out or policy authorization"
        ),
        "corpus": {
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
            "train_maps": len({row["map_seed"] for row in train_rows}),
            "validation_maps": len({row["map_seed"] for row in validation_rows}),
        },
        "models": {
            name: {"parameters": parameter_count(model)}
            for name, model in sorted(models.items())
        },
        "top_reports": reports[:20],
        "capacity_diagnostic": {
            "passed": capacity_passed,
            "candidates": capacity_candidates,
        },
        "identity_diagnostic": {
            "passed": identity_passed,
            "comparisons": identity_comparisons,
        },
        "decision": {
            "freeze_large_teacher_compression_experiment": capacity_passed,
            "freeze_observable_opponent_history_experiment": identity_passed,
            "close_single_state_terminal_advantage_distillation": not (
                capacity_passed or identity_passed
            ),
            "authorize_locked_test": False,
            "authorize_policy": False,
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
    parser.add_argument("--geometry-workers", type=int, default=12)
    parser.add_argument("--torch-threads", type=int, default=10)
    args = parser.parse_args()
    if len(args.train_labels) != len(args.train_observations):
        raise ValueError("each training label file needs one observation file")
    groups = [read_rows(path) for path in args.train_labels]
    train_rows = [row for group in groups for row in group]
    train_observations = load_observations(
        args.train_observations, [len(group) for group in groups]
    )
    validation_rows = read_rows(args.validation_labels)
    validation_observations = load_observations(
        [args.validation_observations], [len(validation_rows)]
    )
    payload = analyze(
        train_rows,
        train_observations,
        validation_rows,
        validation_observations,
        geometry_workers=args.geometry_workers,
        torch_threads=args.torch_threads,
    )
    payload["source"] = {
        "train_labels": [str(path) for path in args.train_labels],
        "train_observations": [str(path) for path in args.train_observations],
        "validation_labels": str(args.validation_labels),
        "validation_observations": str(args.validation_observations),
        "analyzer": str(Path(__file__).relative_to(REPO)),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "corpus": payload["corpus"],
                "models": payload["models"],
                "top_reports": payload["top_reports"][:5],
                "capacity_diagnostic": {
                    "passed": payload["capacity_diagnostic"]["passed"],
                    "passing": sum(
                        item["passed"]
                        for item in payload["capacity_diagnostic"]["candidates"]
                    ),
                },
                "identity_diagnostic": {
                    "passed": payload["identity_diagnostic"]["passed"],
                    "top": payload["identity_diagnostic"]["comparisons"][:3],
                },
                "decision": payload["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
