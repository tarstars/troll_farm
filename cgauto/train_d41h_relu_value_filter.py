#!/usr/bin/env python3
"""Run the frozen D41h grouped tiny-ReLU continuation-value discovery."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.train_d41g_linear_value_filter import (
    discovery_metrics,
    external_metrics,
    load_npz,
    threshold_for_share,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41h-relu-continuation-value-filter-protocol-2026-07-21.md"
TRAIN_FEATURES = ANALYSIS / "d41g-d41f-linear-features.npz"
EXTERNAL_FEATURES = ANALYSIS / "d41g-d41d-external-features.npz"
OUTPUT = ANALYSIS / "d41h-relu-value-filter-result.json"
WEIGHTS = ANALYSIS / "d41h-relu-value-filter-weights.npz"

EXPECTED_PROTOCOL_SHA256 = "c24a981e23bc95551d98aba6b165d440d1ea004e88ebf17b6184c671d3ed0652"
EXPECTED_TRAIN_SHA256 = "881cbbe5c4a1c86eeb3954604d30889380671ffa4da4c7ec62e62659605d5f1b"
EXPECTED_EXTERNAL_SHA256 = "c8c0aa33fc2c22406edff837c878fb95863ecee001fc5cb2f28c54e9e9128d69"

FEATURES = 100
FOLDS = 8
EPOCHS = 600
LEARNING_RATE = 0.01
TARGETS = ("clip50_mse", "positive_bce", "nonnegative_bce")
WIDTHS = (8, 16)
WEIGHT_DECAYS = (0.0001, 0.01)
SHARES = (0.50, 0.60, 0.70)


class TinyReluValue(nn.Module):
    def __init__(self, input_features: int, width: int):
        super().__init__()
        self.hidden = nn.Linear(input_features, width)
        self.output = nn.Linear(width, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(F.relu(self.hidden(features))).squeeze(-1)


def initialization_seed(
    target_index: int, width_index: int, decay_index: int, fold: int
) -> int:
    return 431 + 100 * target_index + 10 * width_index + 1000 * decay_index + fold


def target_values(name: str, margin: np.ndarray) -> np.ndarray:
    margin = np.asarray(margin, dtype=np.float32)
    if name == "clip50_mse":
        return (np.clip(margin, -50, 50) / 50.0).astype(np.float32)
    if name == "positive_bce":
        return (margin > 0).astype(np.float32)
    if name == "nonnegative_bce":
        return (margin >= 0).astype(np.float32)
    raise ValueError(name)


def standardization(features: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features = np.asarray(features, dtype=np.float32)
    mean = features.mean(axis=0, dtype=np.float64).astype(np.float32)
    scale = features.std(axis=0, dtype=np.float64).astype(np.float32)
    scale[scale < 1e-8] = 1.0
    standardized = ((features - mean) / scale).astype(np.float32)
    if not np.isfinite(standardized).all():
        raise RuntimeError("nonfinite D41h standardized feature")
    return standardized, mean, scale


def fit_relu(
    features: np.ndarray,
    margin: np.ndarray,
    *,
    target_name: str,
    width: int,
    weight_decay: float,
    seed: int,
) -> dict:
    features = np.asarray(features, dtype=np.float32)
    if features.ndim != 2 or not len(features) or not np.isfinite(features).all():
        raise ValueError("invalid D41h fit features")
    if width not in WIDTHS and features.shape[1] == FEATURES:
        raise ValueError("unfrozen D41h width")
    standardized, mean, scale = standardization(features)
    targets = target_values(target_name, margin)
    if targets.shape != (len(features),):
        raise ValueError("invalid D41h fit target")

    torch.manual_seed(seed)
    model = TinyReluValue(features.shape[1], width)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=LEARNING_RATE, weight_decay=weight_decay
    )
    feature_tensor = torch.from_numpy(standardized)
    target_tensor = torch.from_numpy(targets)
    model.train()
    for _ in range(EPOCHS):
        prediction = model(feature_tensor)
        if target_name == "clip50_mse":
            loss = F.mse_loss(prediction, target_tensor)
        else:
            loss = F.binary_cross_entropy_with_logits(prediction, target_tensor)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.inference_mode():
        prediction = model(feature_tensor).numpy().copy()
    state = {
        name: value.detach().cpu().numpy().copy()
        for name, value in model.state_dict().items()
    }
    return {
        "mean": mean,
        "scale": scale,
        "state": state,
        "prediction": prediction,
        "final_loss": float(loss.detach()),
        "target_name": target_name,
        "width": width,
        "weight_decay": weight_decay,
        "seed": seed,
    }


def standardized_predict(fitted: dict, features: np.ndarray) -> np.ndarray:
    features = np.asarray(features, dtype=np.float32)
    standardized = (features - fitted["mean"]) / fitted["scale"]
    state = fitted["state"]
    with torch.inference_mode():
        hidden = F.linear(
            torch.from_numpy(standardized),
            torch.from_numpy(state["hidden.weight"]),
            torch.from_numpy(state["hidden.bias"]),
        )
        prediction = F.linear(
            F.relu(hidden),
            torch.from_numpy(state["output.weight"]),
            torch.from_numpy(state["output.bias"]),
        ).squeeze(-1)
    return prediction.numpy().copy()


def raw_parameters(fitted: dict) -> dict[str, np.ndarray]:
    state = fitted["state"]
    hidden_weight = torch.from_numpy(state["hidden.weight"])
    hidden_bias = torch.from_numpy(state["hidden.bias"])
    mean = torch.from_numpy(fitted["mean"])
    scale = torch.from_numpy(fitted["scale"])
    with torch.inference_mode():
        input_weight = hidden_weight / scale.unsqueeze(0)
        input_bias = hidden_bias - F.linear(
            mean.unsqueeze(0), input_weight, None
        ).squeeze(0)
    return {
        "input_weight": input_weight.numpy().copy(),
        "input_bias": input_bias.numpy().copy(),
        "output_weight": state["output.weight"].reshape(-1).copy(),
        "output_bias": state["output.bias"].reshape(()).copy(),
    }


def raw_predict(parameters: dict[str, np.ndarray], features: np.ndarray) -> np.ndarray:
    features = np.asarray(features, dtype=np.float32)
    with torch.inference_mode():
        hidden = F.linear(
            torch.from_numpy(features),
            torch.from_numpy(parameters["input_weight"]),
            torch.from_numpy(parameters["input_bias"]),
        )
        prediction = F.linear(
            F.relu(hidden),
            torch.from_numpy(parameters["output_weight"].reshape(1, -1)),
            torch.from_numpy(np.asarray(parameters["output_bias"]).reshape(1)),
        ).squeeze(-1)
    return prediction.numpy().copy()


def maximum_raw_parity_error(fitted: dict, features: np.ndarray) -> float:
    standardized = standardized_predict(fitted, features)
    raw = raw_predict(raw_parameters(fitted), features)
    return float(np.max(np.abs(standardized - raw)))


def fits_bit_exact(first: dict, second: dict) -> bool:
    names = ("mean", "scale", "prediction")
    if not all(np.array_equal(first[name], second[name]) for name in names):
        return False
    if first["state"].keys() != second["state"].keys():
        return False
    return all(
        np.array_equal(first["state"][name], second["state"][name])
        for name in first["state"]
    )


def scalar_parameters(width: int) -> int:
    return FEATURES * width + width + width + 1 + 1


def validate_dataset(data: dict[str, np.ndarray], *, rows: int) -> dict:
    required = {
        "features",
        "margin_delta",
        "map_seed",
        "fold",
        "opponent",
        "phase",
        "residual_gap",
        "sample_id",
    }
    if set(data) != required:
        raise RuntimeError(f"unexpected D41h archive fields: {sorted(data)}")
    if data["features"].shape != (rows, FEATURES):
        raise RuntimeError("unexpected D41h feature shape")
    if any(data[name].shape != (rows,) for name in required - {"features"}):
        raise RuntimeError("unexpected D41h metadata shape")
    if not np.isfinite(data["features"]).all() or not np.isfinite(data["margin_delta"]).all():
        raise RuntimeError("nonfinite D41h archive")
    if set(data["fold"].tolist()) != set(range(FOLDS)):
        raise RuntimeError("D41h archive does not contain all frozen folds")
    if len(np.unique(data["sample_id"])) != rows:
        raise RuntimeError("duplicate D41h sample identity")
    return {
        "rows": rows,
        "features": FEATURES,
        "finite": True,
        "folds": FOLDS,
        "unique_sample_ids": rows,
    }


def safe_external_metrics(data: dict, scores: np.ndarray, threshold: float) -> dict:
    if np.any(scores >= threshold):
        return external_metrics(data, scores, threshold)
    gates = {
        "at_least_64_rows": False,
        "at_least_24_below_0280": False,
        "mean_at_least_8": False,
        "normal_95_low_above_zero": False,
        "positive_rate_at_least_60pct": False,
        "both_phase_means_positive": False,
        "opponent_breadth": False,
    }
    return {
        "selected_rows": 0,
        "below_0280": 0,
        "margin": {"samples": 0},
        "phase_means": {},
        "opponent_means": {},
        "gates": gates,
        "pass": False,
    }


def main() -> None:
    started = time.monotonic()
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (TRAIN_FEATURES, EXPECTED_TRAIN_SHA256),
        (EXTERNAL_FEATURES, EXPECTED_EXTERNAL_SHA256),
    ):
        if not path.exists():
            raise SystemExit(f"missing D41h prerequisite: {path}")
        if sha256(path) != expected:
            raise SystemExit(f"D41h prerequisite hash mismatch: {path}")
    if OUTPUT.exists() or WEIGHTS.exists():
        raise SystemExit("refusing to overwrite D41h artifacts")

    training = load_npz(TRAIN_FEATURES)
    external = load_npz(EXTERNAL_FEATURES)
    training_audit = validate_dataset(training, rows=600)
    external_audit = validate_dataset(external, rows=126)
    training_features = training["features"].astype(np.float32, copy=False)
    training_margin = training["margin_delta"].astype(np.float32, copy=False)
    eligible = (training["residual_gap"] >= 0.200) & (
        training["residual_gap"] <= 0.340
    )

    candidates = []
    for target_index, target_name in enumerate(TARGETS):
        for width_index, width in enumerate(WIDTHS):
            for decay_index, weight_decay in enumerate(WEIGHT_DECAYS):
                oof = np.empty(len(training_margin), dtype=np.float32)
                fold_parity = []
                fold_losses = []
                for fold in range(FOLDS):
                    train = training["fold"] != fold
                    held = ~train
                    fitted = fit_relu(
                        training_features[train],
                        training_margin[train],
                        target_name=target_name,
                        width=width,
                        weight_decay=weight_decay,
                        seed=initialization_seed(
                            target_index, width_index, decay_index, fold
                        ),
                    )
                    oof[held] = standardized_predict(fitted, training_features[held])
                    fold_parity.append(
                        maximum_raw_parity_error(fitted, training_features[held])
                    )
                    fold_losses.append(fitted["final_loss"])

                for share in SHARES:
                    threshold = threshold_for_share(oof[eligible], share)
                    metrics = discovery_metrics(training, oof, threshold)
                    candidates.append(
                        {
                            "target": target_name,
                            "target_index": target_index,
                            "width": width,
                            "width_index": width_index,
                            "weight_decay": weight_decay,
                            "decay_index": decay_index,
                            "share_target": share,
                            "maximum_fold_raw_parity_error": max(fold_parity),
                            "mean_fold_final_loss": float(np.mean(fold_losses)),
                            **metrics,
                        }
                    )

    passing = [candidate for candidate in candidates if candidate["pass"]]
    selected = None
    external_report = None
    repeat_exact = None
    final_parity = None
    size = 0
    if passing:
        selected = max(
            passing,
            key=lambda item: (
                item["margin"]["normal_95_low"],
                item["margin"]["samples"],
                -item["width"],
                item["weight_decay"],
                -item["target_index"],
                -item["share_target"],
            ),
        )
        full_seed = initialization_seed(
            selected["target_index"],
            selected["width_index"],
            selected["decay_index"],
            FOLDS,
        )
        fit_arguments = {
            "target_name": selected["target"],
            "width": selected["width"],
            "weight_decay": selected["weight_decay"],
            "seed": full_seed,
        }
        first = fit_relu(training_features, training_margin, **fit_arguments)
        second = fit_relu(training_features, training_margin, **fit_arguments)
        repeat_exact = fits_bit_exact(first, second)
        raw = raw_parameters(first)
        full_scores = standardized_predict(first, training_features)
        final_parity = maximum_raw_parity_error(first, training_features)
        production_threshold = threshold_for_share(
            full_scores[eligible], selected["selected_share"]
        )
        external_scores = raw_predict(raw, external["features"])
        external_report = safe_external_metrics(
            external, external_scores, production_threshold
        )
        size = scalar_parameters(selected["width"])
        np.savez(
            WEIGHTS,
            input_weight=raw["input_weight"],
            input_bias=raw["input_bias"],
            output_weight=raw["output_weight"],
            output_bias=raw["output_bias"],
            threshold=np.asarray(production_threshold, dtype=np.float32),
            residual_gap_min=np.asarray(0.200, dtype=np.float32),
            residual_gap_max=np.asarray(0.340, dtype=np.float32),
        )
        selected = {
            **selected,
            "full_seed": full_seed,
            "production_threshold": production_threshold,
            "full_training_metrics": discovery_metrics(
                training, full_scores, production_threshold
            ),
            "full_repeat_bit_exact": repeat_exact,
            "full_raw_prediction_parity_error": final_parity,
            "scalar_parameters_including_threshold": size,
        }

    qualifies = bool(
        selected is not None
        and repeat_exact
        and final_parity is not None
        and final_parity <= 1e-5
        and size <= 1634
        and external_report is not None
        and external_report["pass"]
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "training_features": str(TRAIN_FEATURES),
            "training_features_sha256": sha256(TRAIN_FEATURES),
            "external_features": str(EXTERNAL_FEATURES),
            "external_features_sha256": sha256(EXTERNAL_FEATURES),
            "training_audit": training_audit,
            "external_audit": external_audit,
        },
        "matrix": {
            "targets": TARGETS,
            "widths": WIDTHS,
            "weight_decays": WEIGHT_DECAYS,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "shares": SHARES,
            "configurations": len(TARGETS) * len(WIDTHS) * len(WEIGHT_DECAYS),
            "evaluated_candidates": len(candidates),
            "candidates": candidates,
            "passing_candidates": len(passing),
        },
        "selected": selected,
        "external_replication": external_report,
        "weights": str(WEIGHTS) if WEIGHTS.exists() else None,
        "weights_sha256": sha256(WEIGHTS) if WEIGHTS.exists() else None,
        "scalar_parameters": size,
        "pass": qualifies,
        "wall_seconds": time.monotonic() - started,
        "scope": "consumed-label D41h discovery only; no fresh outcome or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass": qualifies,
                "passing_candidates": len(passing),
                "selected": selected,
                "external_replication": external_report,
                "weights_sha256": report["weights_sha256"],
                "wall_seconds": report["wall_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
