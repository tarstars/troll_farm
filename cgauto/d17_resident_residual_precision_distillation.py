#!/usr/bin/env python3
"""Precision-first distillation of exact resident-residual MC labels."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
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

TRAIN_RANGE = range(372_000, 373_920)
VALIDATION_RANGE = range(384_000, 384_480)
TEST_RANGE = range(396_000, 396_480)
SAMPLES_PER_SCENARIO = 12
MODEL_SEEDS = (1701, 1702, 1703)
SELECTION_RATES = (0.005, 0.01, 0.02, 0.04, 0.08, 0.12)
VERBS = ("WAIT", "MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK")
PLANT_TYPES = ("-", "PLUM", "LEMON", "APPLE", "BANANA")
STRING_FIELDS = {
    "opponent",
    "local_plant_type",
    "resident_command",
    "resident_verb",
    "previous_command",
    "previous_verb",
    "other_command",
    "other_verb",
    "alternative_command",
    "alternative_verb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field, value in list(row.items()):
            if field not in STRING_FIELDS:
                row[field] = int(value)
    return rows


def validate_split(rows: list[dict], scenarios: range, label: str) -> None:
    expected_rows = len(scenarios) * SAMPLES_PER_SCENARIO
    if len(rows) != expected_rows:
        raise ValueError(f"{label}: expected {expected_rows} rows, found {len(rows)}")
    seen = defaultdict(set)
    for row in rows:
        scenario = row["scenario"]
        if scenario not in scenarios:
            raise ValueError(f"{label}: scenario {scenario} outside frozen range")
        seen[scenario].add(row["sample_slot"])
        if row["alternative_plane"] == 0:
            raise ValueError(f"{label}: KEEP row in alternative corpus")
    expected_slots = set(range(SAMPLES_PER_SCENARIO))
    if set(seen) != set(scenarios):
        raise ValueError(f"{label}: incomplete scenario range")
    if any(slots != expected_slots for slots in seen.values()):
        raise ValueError(f"{label}: incomplete sample slots")


def _scaled(value: float, scale: float, *, signed: bool = False) -> float:
    if signed:
        return float(np.clip(value / scale, -1.0, 1.0))
    return float(np.clip(value / scale, 0.0, 1.0))


NUMERIC_FEATURES = (
    "turn",
    "ordinal",
    "worker_count",
    "ms",
    "cc",
    "hp",
    "chop",
    "free",
    *(f"carry{item}" for item in range(6)),
    *(f"inv{item}" for item in range(6)),
    "state_score",
    "state_opponent_score",
    "state_margin",
    "state_wood_edge",
    "plants",
    "local_plant_health",
    "local_plant_fruits",
    "near_home",
    "near_iron",
    "intent_age",
    "legal_actions",
)


def feature_names() -> list[str]:
    names = list(NUMERIC_FEATURES)
    names.extend(f"local_plant_type={value}" for value in PLANT_TYPES)
    for source in ("resident", "previous", "other"):
        names.extend(f"{source}_verb={value}" for value in VERBS)
        names.extend(f"{source}_plane={value}" for value in range(-1, 13))
    names.extend(f"alternative_plane={value}" for value in range(1, 13))
    names.extend(("same_as_resident_plane", "same_as_resident_command"))
    return names


def feature_row(row: dict) -> list[float]:
    values = [
        _scaled(row["turn"], 300),
        _scaled(row["ordinal"], 5),
        _scaled(row["worker_count"], 6),
        _scaled(row["ms"], 3),
        _scaled(row["cc"], 4),
        _scaled(row["hp"], 3),
        _scaled(row["chop"], 4),
        _scaled(row["free"], 4),
    ]
    values.extend(_scaled(row[f"carry{item}"], 4) for item in range(6))
    values.extend(
        _scaled(row[f"inv{item}"], 100 if item == 5 else 30)
        for item in range(6)
    )
    values.extend(
        (
            _scaled(row["state_score"], 500),
            _scaled(row["state_opponent_score"], 500),
            _scaled(row["state_margin"], 400, signed=True),
            _scaled(row["state_wood_edge"], 100, signed=True),
            _scaled(row["plants"], 64),
            _scaled(max(row["local_plant_health"], 0), 24),
            _scaled(max(row["local_plant_fruits"], 0), 3),
            float(bool(row["near_home"])),
            float(bool(row["near_iron"])),
            _scaled(row["intent_age"], 16),
            _scaled(row["legal_actions"], 7),
        )
    )
    local_type = row["local_plant_type"]
    values.extend(float(local_type == value) for value in PLANT_TYPES)
    for source in ("resident", "previous", "other"):
        source_verb = row[f"{source}_verb"]
        source_plane = row[f"{source}_plane"]
        values.extend(float(source_verb == value) for value in VERBS)
        values.extend(float(source_plane == value) for value in range(-1, 13))
    alternative_plane = row["alternative_plane"]
    values.extend(float(alternative_plane == value) for value in range(1, 13))
    values.extend(
        (
            float(alternative_plane == row["resident_plane"]),
            float(row["alternative_command"] == row["resident_command"]),
        )
    )
    if len(values) != len(feature_names()):
        raise AssertionError("feature schema mismatch")
    return values


def matrix(rows: list[dict]) -> np.ndarray:
    return np.asarray([feature_row(row) for row in rows], dtype=np.float32)


class LinearScorer(nn.Module):
    def __init__(self, inputs: int) -> None:
        super().__init__()
        self.output = nn.Linear(inputs, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(features).squeeze(-1)


class MlpScorer(nn.Module):
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


def make_model(family: str, inputs: int) -> nn.Module:
    if family == "binary_linear":
        return LinearScorer(inputs)
    if family in {"binary_mlp", "value_mlp"}:
        return MlpScorer(inputs)
    raise ValueError(family)


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def train_model(
    family: str,
    seed: int,
    features: np.ndarray,
    advantages: np.ndarray,
) -> nn.Module:
    torch.manual_seed(seed)
    model = make_model(family, features.shape[1])
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.02 if family == "binary_linear" else 0.003,
        weight_decay=1e-4,
    )
    feature_tensor = torch.from_numpy(features)
    advantage_tensor = torch.from_numpy(advantages.astype(np.float32, copy=False))
    positive = advantages > 0
    positive_weight = float((~positive).sum() / max(positive.sum(), 1))
    epochs = 80 if family == "binary_linear" else 64
    batch_size = 1024
    generator = torch.Generator().manual_seed(seed ^ 0xD17)
    for _ in range(epochs):
        ordering = torch.randperm(len(features), generator=generator)
        for start in range(0, len(features), batch_size):
            indexes = ordering[start : start + batch_size]
            prediction = model(feature_tensor[indexes])
            batch_advantage = advantage_tensor[indexes]
            if family.startswith("binary"):
                target = (batch_advantage > 0).float()
                loss = F.binary_cross_entropy_with_logits(
                    prediction, target, reduction="none"
                )
                negative_cost = 1.0 + (-batch_advantage).clamp(0, 32) / 8.0
                weights = torch.where(
                    target.bool(),
                    torch.full_like(target, positive_weight),
                    negative_cost,
                )
                loss = (loss * weights).mean()
            else:
                target = batch_advantage.clamp(-32, 32) / 16.0
                weights = 1.0 + batch_advantage.abs().clamp(0, 32) / 16.0
                loss = (
                    F.smooth_l1_loss(prediction, target, reduction="none")
                    * weights
                ).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()
    return model


@torch.inference_mode()
def score(model: nn.Module, family: str, features: np.ndarray) -> np.ndarray:
    raw = model(torch.from_numpy(features)).numpy()
    if family.startswith("binary"):
        return 1.0 / (1.0 + np.exp(-np.clip(raw, -30, 30)))
    return raw * 16.0


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


def map_bootstrap(
    rows: list[dict], selected: np.ndarray, *, seed: int = 1717, samples: int = 10_000
) -> dict:
    per_map = defaultdict(list)
    for row, choose in zip(rows, selected, strict=True):
        per_map[row["map_seed"]].append(row["margin_advantage"] if choose else 0)
    map_values = np.asarray(
        [np.mean(per_map[map_seed]) for map_seed in sorted(per_map)], dtype=np.float64
    )
    rng = np.random.default_rng(seed)
    draws = rng.choice(map_values, size=(samples, len(map_values)), replace=True).mean(axis=1)
    return {
        "maps": len(map_values),
        "mean_contribution": float(map_values.mean()),
        "ci95": [float(value) for value in np.quantile(draws, (0.025, 0.975))],
    }


def selection_report(rows: list[dict], selected: np.ndarray) -> dict:
    indexes = np.flatnonzero(selected)
    advantages = np.asarray([row["margin_advantage"] for row in rows], dtype=np.float64)
    selected_advantages = advantages[indexes]
    positive_indexes = [index for index in indexes if advantages[index] > 0]
    opponents = sorted({rows[index]["opponent"] for index in positive_indexes})
    roles = sorted({rows[index]["ordinal"] for index in positive_indexes})
    maps = sorted({rows[index]["map_seed"] for index in positive_indexes})
    by_opponent = {}
    for opponent in sorted({row["opponent"] for row in rows}):
        values = [
            advantages[index]
            for index in indexes
            if rows[index]["opponent"] == opponent
        ]
        by_opponent[opponent] = {
            "selected": len(values),
            "mean_advantage": float(np.mean(values)) if values else None,
        }
    selected_count = len(indexes)
    positive_count = len(positive_indexes)
    return {
        "selected": selected_count,
        "selection_rate": selected_count / len(rows),
        "positive": positive_count,
        "negative": int(np.sum(selected_advantages < 0)),
        "ties": int(np.sum(selected_advantages == 0)),
        "precision": positive_count / selected_count if selected_count else 1.0,
        "conditional_mean_advantage": (
            float(selected_advantages.mean()) if selected_count else 0.0
        ),
        "conditional_median_advantage": (
            float(np.median(selected_advantages)) if selected_count else 0.0
        ),
        "new_catastrophes": int(
            sum(rows[index]["new_catastrophe"] for index in indexes)
        ),
        "positive_maps": len(maps),
        "positive_opponents": len(opponents),
        "positive_roles": roles,
        "map_bootstrap": map_bootstrap(rows, selected),
        "by_opponent": by_opponent,
    }


def validation_eligible(report: dict) -> tuple[bool, dict]:
    gates = {
        "selected_at_least_72": report["selected"] >= 72,
        "selection_rate_at_most_12_percent": report["selection_rate"] <= 0.12,
        "precision_at_least_70_percent": report["precision"] >= 0.70,
        "conditional_mean_at_least_plus2": report["conditional_mean_advantage"] >= 2.0,
        "no_new_catastrophe": report["new_catastrophes"] == 0,
        "positive_on_at_least_12_maps": report["positive_maps"] >= 12,
        "positive_against_at_least_4_opponents": report["positive_opponents"] >= 4,
        "positive_in_both_roles": {0, 1}.issubset(report["positive_roles"]),
        "map_bootstrap_lower_bound_positive": report["map_bootstrap"]["ci95"][0] > 0,
    }
    return all(gates.values()), gates


def test_eligible(report: dict, parameters: int) -> tuple[bool, dict]:
    gates = {
        "selected_at_least_72": report["selected"] >= 72,
        "selection_rate_at_most_12_percent": report["selection_rate"] <= 0.12,
        "precision_at_least_65_percent": report["precision"] >= 0.65,
        "conditional_mean_at_least_plus1": report["conditional_mean_advantage"] >= 1.0,
        "map_bootstrap_lower_bound_positive": report["map_bootstrap"]["ci95"][0] > 0,
        "no_new_catastrophe": report["new_catastrophes"] == 0,
        "positive_on_at_least_12_maps": report["positive_maps"] >= 12,
        "positive_against_at_least_4_opponents": report["positive_opponents"] >= 4,
        "positive_in_both_roles": {0, 1}.issubset(report["positive_roles"]),
        "parameters_at_most_10000": parameters <= 10_000,
        "estimated_int8_bytes_at_most_10000": parameters <= 10_000,
    }
    return all(gates.values()), gates


def quantile_threshold(scores: np.ndarray, selection_rate: float) -> float:
    return float(np.quantile(scores, 1.0 - selection_rate, method="higher"))


def analyze(
    train_rows: list[dict], validation_rows: list[dict], test_path: Path
) -> dict:
    validate_split(train_rows, TRAIN_RANGE, "train")
    validate_split(validation_rows, VALIDATION_RANGE, "validation")
    train_maps = {row["map_seed"] for row in train_rows}
    validation_maps = {row["map_seed"] for row in validation_rows}
    if train_maps & validation_maps:
        raise ValueError("D17 train/validation map overlap")

    train_features = matrix(train_rows)
    validation_features = matrix(validation_rows)
    train_advantages = np.asarray(
        [row["margin_advantage"] for row in train_rows], dtype=np.float32
    )
    models: dict[str, tuple[str, nn.Module]] = {}
    validation_scores: dict[str, np.ndarray] = {}
    for family in ("binary_linear", "binary_mlp", "value_mlp"):
        component_names = []
        for seed in MODEL_SEEDS:
            name = f"{family}_s{seed}"
            model = train_model(family, seed, train_features, train_advantages)
            models[name] = (family, model)
            component_names.append(name)
            validation_scores[name] = score(model, family, validation_features)
        ensemble = f"{family}_ensemble"
        validation_scores[ensemble] = np.mean(
            [validation_scores[name] for name in component_names], axis=0
        )

    threshold_reports = []
    for name, scores in sorted(validation_scores.items()):
        for rate in SELECTION_RATES:
            threshold = quantile_threshold(scores, rate)
            report = selection_report(validation_rows, scores >= threshold)
            eligible, gates = validation_eligible(report)
            threshold_reports.append(
                {
                    "model": name,
                    "target_selection_rate": rate,
                    "threshold": threshold,
                    "report": report,
                    "gates": gates,
                    "eligible": eligible,
                }
            )
    eligible_reports = [report for report in threshold_reports if report["eligible"]]
    lexical_rank = {
        name: -index for index, name in enumerate(sorted(validation_scores))
    }
    eligible_reports.sort(
        key=lambda item: (
            item["report"]["map_bootstrap"]["ci95"][0],
            item["report"]["conditional_mean_advantage"],
            item["report"]["selected"],
            -sum(parameter_count(models[name][1]) for name in component_names(item["model"])),
            lexical_rank[item["model"]],
        ),
        reverse=True,
    )
    selected = eligible_reports[0] if eligible_reports else None
    if selected is None:
        selected_payload = None
        locked_test = None
        test_passed = False
        test_corpus = {
            "opened": False,
            "expected_rows": len(TEST_RANGE) * SAMPLES_PER_SCENARIO,
            "expected_scenarios": len(TEST_RANGE),
            "expected_maps": len(TEST_RANGE) // 12,
        }
    else:
        names = component_names(selected["model"])
        parameters = sum(parameter_count(models[name][1]) for name in names)
        # The locked file is deliberately not read until a validation recipe exists.
        test_rows = read_rows(test_path)
        validate_split(test_rows, TEST_RANGE, "test")
        test_maps = {row["map_seed"] for row in test_rows}
        if test_maps & (train_maps | validation_maps):
            raise ValueError("D17 locked-test map overlap")
        test_features = matrix(test_rows)
        component_test_scores = [
            score(models[name][1], models[name][0], test_features) for name in names
        ]
        selected_test_scores = np.mean(component_test_scores, axis=0)
        test_report = selection_report(
            test_rows,
            selected_test_scores >= selected["threshold"],
        )
        test_passed, test_gates = test_eligible(test_report, parameters)
        selected_payload = {
            "model": selected["model"],
            "threshold": selected["threshold"],
            "components": [
                model_payload(models[name][1], models[name][0], int(name.rsplit("s", 1)[1]))
                for name in names
            ],
            "parameters": parameters,
            "estimated_int8_payload_bytes": parameters,
        }
        locked_test = {
            "report": test_report,
            "gates": test_gates,
            "passed": test_passed,
        }
        test_corpus = {"opened": True, **corpus_summary(test_rows)}

    return {
        "schema": 1,
        "scope": (
            "D17 map-disjoint precision-first offline distillation; locked test is opened "
            "once after validation selection; no candidate, submission, or Arena authorization"
        ),
        "feature_schema": {
            "count": len(feature_names()),
            "names": feature_names(),
            "excluded": [
                "scenario/map identity",
                "opponent-policy identity",
                "absolute x/y",
                "reservoir/candidate index",
                "baseline and alternative terminal outcomes",
                "continuation latency",
            ],
        },
        "corpus": {
            "train": corpus_summary(train_rows),
            "validation": corpus_summary(validation_rows),
            "test": test_corpus,
        },
        "training": {
            "model_seeds": list(MODEL_SEEDS),
            "families": ["binary_linear", "binary_mlp", "value_mlp"],
            "selection_rates": list(SELECTION_RATES),
            "candidate_scorers": len(validation_scores),
        },
        "validation": {
            "eligible_thresholds": len(eligible_reports),
            "selected": selected,
            "top_thresholds": sorted(
                threshold_reports,
                key=lambda item: (
                    item["eligible"],
                    item["report"]["map_bootstrap"]["ci95"][0],
                    item["report"]["conditional_mean_advantage"],
                ),
                reverse=True,
            )[:20],
        },
        "selected_model": selected_payload,
        "locked_test": locked_test,
        "decision": {
            "authorize_exact_policy_prototype": test_passed,
            "authorize_source_integration": False,
            "authorize_candidate": False,
            "authorize_submission": False,
            "authorize_arena": False,
        },
    }


def component_names(name: str) -> list[str]:
    if name.endswith("_ensemble"):
        family = name.removesuffix("_ensemble")
        return [f"{family}_s{seed}" for seed in MODEL_SEEDS]
    return [name]


def corpus_summary(rows: list[dict]) -> dict:
    advantages = np.asarray([row["margin_advantage"] for row in rows])
    return {
        "rows": len(rows),
        "scenarios": len({row["scenario"] for row in rows}),
        "maps": len({row["map_seed"] for row in rows}),
        "positive": int(np.sum(advantages > 0)),
        "positive_rate": float(np.mean(advantages > 0)),
        "negative": int(np.sum(advantages < 0)),
        "mean_advantage": float(np.mean(advantages)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=3)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(2, args.threads))
    payload = analyze(read_rows(args.train), read_rows(args.validation), args.test)
    payload["source"] = {
        "train": str(args.train),
        "train_sha256": sha256(args.train),
        "validation": str(args.validation),
        "validation_sha256": sha256(args.validation),
        "test": str(args.test),
        "test_sha256": sha256(args.test) if payload["locked_test"] is not None else None,
        "analyzer": str(Path(__file__).relative_to(REPO)),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "corpus": payload["corpus"],
                "validation": {
                    "eligible_thresholds": payload["validation"]["eligible_thresholds"],
                    "selected": payload["validation"]["selected"],
                },
                "locked_test": payload["locked_test"],
                "decision": payload["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
