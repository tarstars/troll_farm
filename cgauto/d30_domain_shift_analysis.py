#!/usr/bin/env python3
"""Decompose D29b's generated-to-official turn-75 prediction shift."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d29_spatial_option_critic import (
    PLANE_SCALES,
    SPATIAL_SHAPE,
    load_checkpoint,
    read_scalars,
    read_spatial,
)
from cgauto.d29c_official_field_activation import protocol_transcript
from cgauto.recent_resident_field_census import (
    corpus_parser,
    current_player,
    decoded_states,
)


ROOT = REPO
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
CHECKPOINT = ANALYSIS / "d29b-pretransfer-resident-checkpoint-2026-07-20.json"
D29C_RESULT = ANALYSIS / "d29c-official-field-activation-audit-2026-07-20.json"
FIELD_FEATURES = ANALYSIS / "d30-field-features-development-first80.json"
OUTPUT = ANALYSIS / "d30-official-state-domain-shift-development-2026-07-20.json"
BINARY = ROOT / "rust/target/release/d30_field_features"
MODEL = ANALYSIS / "d29a-option-critic-int8-verification.checkpoint.json"
GEN_SCALARS = ANALYSIS / "d29b-scalar-features-confirmation-53720-53839.tsv"
GEN_SPATIAL = ANALYSIS / "d29b-spatial-features-confirmation-53720-53839.tsv"
GEN_PREDICTIONS = ANALYSIS / "d29b-predictions-confirmation-run1-53720-53839.tsv"
EXPECTED_AGENT = 6561795
EXPECTED_SUBMISSION = 41015603
PLANE_NAMES = (
    "map_mask", "walkable", "water", "iron", "own_shack", "opponent_shack",
    "plum", "lemon", "apple", "banana", "plant_size", "plant_health",
    "plant_fruits", "plant_cooldown", "own_unit", "own_movement",
    "own_capacity", "own_harvest", "own_chop", "own_carry_plum",
    "own_carry_lemon", "own_carry_apple", "own_carry_banana", "own_carry_iron",
    "own_carry_wood", "opponent_unit", "opponent_movement", "opponent_capacity",
    "opponent_harvest", "opponent_chop", "opponent_carry_plum",
    "opponent_carry_lemon", "opponent_carry_apple", "opponent_carry_banana",
    "opponent_carry_iron", "opponent_carry_wood",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    temporary.replace(path)


def extract_one(row: dict, binary: Path) -> dict:
    from cgauto import battle_taxonomy as arena

    game_id = int(row["game_id"])
    game = arena.call("gameResult/findByGameId", [game_id, None])
    seat = current_player(game)
    agents = game.get("agents") or []
    if seat is None or agents[seat].get("agentId") != EXPECTED_AGENT:
        raise ValueError(f"official identity differs for {game_id}")
    parser = corpus_parser()
    frames = game.get("frames") or []
    _, _, inventory0, inventory1 = parser.parse_frame0(frames[0]["view"])
    trajectory, _ = parser.extract_turns(frames, inventory0, inventory1)
    map_data, states, unknown = decoded_states(game, trajectory)
    if len(states) < 75 or unknown:
        raise ValueError(f"incomplete replay for {game_id}: states={len(states)} unknown={unknown}")
    completed = subprocess.run(
        [binary],
        input=protocol_transcript(map_data, states, seat),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    features = json.loads(completed.stdout)
    return {"game_id": game_id, "seat": seat, **features}


def extract_field_features(checkpoint_path: Path, binary: Path, output: Path) -> list[dict]:
    checkpoint = json.loads(checkpoint_path.read_text())
    if checkpoint.get("agent_id") != EXPECTED_AGENT:
        raise ValueError("resident agent differs")
    if checkpoint.get("submission_id") != EXPECTED_SUBMISSION:
        raise ValueError("resident submission differs")
    requested = checkpoint.get("rows", [])[:80]
    if len(requested) != 80:
        raise ValueError("D30 requires the frozen first 80 checkpoint rows")
    by_game = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(extract_one, row, binary): row for row in requested}
        for completed, future in enumerate(as_completed(futures), 1):
            item = future.result()
            by_game[item["game_id"]] = item
            if completed % 10 == 0 or completed == 80:
                print(f"extracted {completed}/80 official feature roots", flush=True)
    result = [by_game[int(row["game_id"])] for row in requested]
    atomic_json(
        output,
        {
            "schema": 1,
            "scope": "D30 development-only exact features for frozen D29c first80",
            "checkpoint_sha256": sha256(checkpoint_path),
            "binary_sha256": sha256(binary),
            "rows": result,
        },
    )
    return result


def model_embeddings(model, spatial: torch.Tensor, scalar_z: torch.Tensor):
    mask = spatial[:, :1]
    value = torch.relu(model.conv1(spatial))
    value = torch.relu(model.conv2(value))
    denominator = mask.sum(dim=(2, 3)).clamp_min(1.0)
    mean = (value * mask).sum(dim=(2, 3)) / denominator
    maximum = value.masked_fill(mask == 0, -1e9).amax(dim=(2, 3))
    scalar = torch.relu(model.scalar(scalar_z))
    return torch.cat((mean, maximum), dim=1), scalar


def normalized_head(model, spatial_embedding: torch.Tensor, scalar_embedding: torch.Tensor):
    combined = torch.cat((spatial_embedding, scalar_embedding), dim=1)
    return model.output(torch.relu(model.hidden(combined))).squeeze(1)


def raw_prediction(model, metadata, spatial: torch.Tensor, scalar_z: torch.Tensor):
    with torch.no_grad():
        value = model(spatial, scalar_z)
    return value.numpy() * metadata["target_std"] + metadata["target_mean"]


def cross_mean(model, metadata, spatial_embedding, scalar_embedding, chunk=256) -> float:
    total = 0.0
    count = 0
    with torch.no_grad():
        for left in range(0, len(spatial_embedding), chunk):
            sp = spatial_embedding[left : left + chunk]
            for right in range(0, len(scalar_embedding), chunk):
                sc = scalar_embedding[right : right + chunk]
                a, b = len(sp), len(sc)
                sp_grid = sp[:, None, :].expand(a, b, -1).reshape(a * b, -1)
                sc_grid = sc[None, :, :].expand(a, b, -1).reshape(a * b, -1)
                normalized = normalized_head(model, sp_grid, sc_grid)
                raw = normalized * metadata["target_std"] + metadata["target_mean"]
                total += float(raw.double().sum())
                count += a * b
    return total / count


def prediction_table(path: Path) -> dict[tuple[int, int, str], float]:
    with path.open(newline="") as stream:
        return {
            (int(row["seed"]), int(row["seat"]), row["opponent"]): float(row["raw_prediction"])
            for row in csv.DictReader(stream, delimiter="\t")
        }


def analyze(field_payload: dict) -> dict:
    field_rows = field_payload["rows"]
    if len(field_rows) != 80:
        raise ValueError("field feature corpus must contain 80 rows")
    field_scalars = np.asarray([row["scalars"] for row in field_rows], dtype=np.float32)
    field_grids = np.asarray([row["grid"] for row in field_rows], dtype=np.int16).reshape(
        -1, *SPATIAL_SHAPE
    )
    generated_scalar_rows, feature_names = read_scalars(GEN_SCALARS)
    generated_spatial_rows, spatial_checks = read_spatial(GEN_SPATIAL)
    generated_keys = sorted(set(generated_scalar_rows) & set(generated_spatial_rows))
    if len(generated_keys) != 1920 or any(spatial_checks.values()):
        raise ValueError("generated confirmation feature corpus failed integrity")
    generated_scalars = np.stack([generated_scalar_rows[key]["values"] for key in generated_keys])
    generated_grids = np.stack([generated_spatial_rows[key]["grid"] for key in generated_keys]).reshape(
        -1, *SPATIAL_SHAPE
    )

    model, metadata, _ = load_checkpoint(MODEL, feature_names)
    model.eval()
    mean = metadata["scalar_mean"]
    std = metadata["scalar_std"]
    plane_scales = torch.from_numpy(PLANE_SCALES)
    field_spatial = torch.from_numpy(field_grids.astype(np.float32)) / plane_scales
    generated_spatial = torch.from_numpy(generated_grids.astype(np.float32)) / plane_scales
    field_z = torch.from_numpy((field_scalars - mean) / std)
    generated_z = torch.from_numpy((generated_scalars - mean) / std)

    field_raw = raw_prediction(model, metadata, field_spatial, field_z)
    generated_raw = raw_prediction(model, metadata, generated_spatial, generated_z)
    d29c = json.loads(D29C_RESULT.read_text())
    expected_field = {int(row["game_id"]): float(row["raw_prediction"]) for row in d29c["rows"]}
    expected_hash = {int(row["game_id"]): int(row["grid_hash"]) for row in d29c["rows"]}
    field_prediction_error = max(
        abs(float(value) - expected_field[int(row["game_id"])])
        for row, value in zip(field_rows, field_raw, strict=True)
    )
    grid_hash_mismatches = [
        int(row["game_id"])
        for row in field_rows
        if int(row["grid_hash"]) != expected_hash[int(row["game_id"])]
    ]
    expected_generated = prediction_table(GEN_PREDICTIONS)
    generated_prediction_error = max(
        abs(float(value) - expected_generated[key])
        for key, value in zip(generated_keys, generated_raw, strict=True)
    )

    with torch.no_grad():
        field_spatial_embedding, field_scalar_embedding = model_embeddings(
            model, field_spatial, field_z
        )
        generated_spatial_embedding, generated_scalar_embedding = model_embeddings(
            model, generated_spatial, generated_z
        )
    cross = {
        "generated_spatial__generated_scalar": cross_mean(
            model, metadata, generated_spatial_embedding, generated_scalar_embedding
        ),
        "field_spatial__generated_scalar": cross_mean(
            model, metadata, field_spatial_embedding, generated_scalar_embedding
        ),
        "generated_spatial__field_scalar": cross_mean(
            model, metadata, generated_spatial_embedding, field_scalar_embedding
        ),
        "field_spatial__field_scalar": cross_mean(
            model, metadata, field_spatial_embedding, field_scalar_embedding
        ),
    }
    base = cross["generated_spatial__generated_scalar"]
    spatial_marginal = cross["field_spatial__generated_scalar"] - base
    scalar_marginal = cross["generated_spatial__field_scalar"] - base
    factorial_interaction = (
        cross["field_spatial__field_scalar"]
        - cross["field_spatial__generated_scalar"]
        - cross["generated_spatial__field_scalar"]
        + base
    )
    leading_branch = (
        "spatial"
        if abs(spatial_marginal) >= 2 * abs(scalar_marginal)
        else "scalar"
        if abs(scalar_marginal) >= 2 * abs(spatial_marginal)
        else "mixed"
    )

    generated_median = np.median(generated_scalars, axis=0).astype(np.float32)
    generated_min = generated_scalars.min(axis=0)
    generated_max = generated_scalars.max(axis=0)
    baseline_field_mean = float(field_raw.mean())
    scalar_rows = []
    for index, name in enumerate(feature_names):
        replacement = field_scalars.copy()
        replacement[:, index] = generated_median[index]
        replacement_z = torch.from_numpy((replacement - mean) / std)
        replaced = raw_prediction(model, metadata, field_spatial, replacement_z)
        outside = (field_scalars[:, index] < generated_min[index]) | (
            field_scalars[:, index] > generated_max[index]
        )
        scalar_rows.append(
            {
                "feature": name,
                "field_mean": float(field_scalars[:, index].mean()),
                "generated_mean": float(generated_scalars[:, index].mean()),
                "generated_median": float(generated_median[index]),
                "standardized_mean_shift": float(
                    (field_scalars[:, index].mean() - generated_scalars[:, index].mean())
                    / std[index]
                ),
                "field_outside_generated_support": int(outside.sum()),
                "replacement_raw_mean_delta": float(replaced.mean() - baseline_field_mean),
            }
        )
    scalar_ranked = sorted(
        scalar_rows, key=lambda row: abs(row["replacement_raw_mean_delta"]), reverse=True
    )

    generated_plane_mean = generated_spatial.mean(dim=0)
    field_plane_totals = field_grids.sum(axis=(2, 3))
    generated_plane_totals = generated_grids.sum(axis=(2, 3))
    spatial_rows = []
    for index, name in enumerate(PLANE_NAMES):
        replacement = field_spatial.clone()
        replacement[:, index] = generated_plane_mean[index]
        replaced = raw_prediction(model, metadata, replacement, field_z)
        gen_min = generated_plane_totals[:, index].min()
        gen_max = generated_plane_totals[:, index].max()
        outside = (field_plane_totals[:, index] < gen_min) | (
            field_plane_totals[:, index] > gen_max
        )
        spatial_rows.append(
            {
                "plane": name,
                "field_total_mean": float(field_plane_totals[:, index].mean()),
                "generated_total_mean": float(generated_plane_totals[:, index].mean()),
                "field_outside_generated_total_support": int(outside.sum()),
                "replacement_raw_mean_delta": float(replaced.mean() - baseline_field_mean),
            }
        )
    spatial_ranked = sorted(
        spatial_rows, key=lambda row: abs(row["replacement_raw_mean_delta"]), reverse=True
    )

    field_paired = float(field_raw.mean())
    generated_paired = float(generated_raw.mean())
    return {
        "schema": 1,
        "complete": (
            not grid_hash_mismatches
            and field_prediction_error <= 0.001
            and generated_prediction_error <= 0.001
        ),
        "scope": "D30 development-only decomposition; no threshold tuning or Arena action",
        "integrity": {
            "field_rows": len(field_rows),
            "generated_rows": len(generated_keys),
            "scalar_features": field_scalars.shape[1],
            "spatial_shape": list(field_grids.shape[1:]),
            "grid_hash_mismatches": grid_hash_mismatches,
            "maximum_field_raw_prediction_error": field_prediction_error,
            "maximum_generated_raw_prediction_error": generated_prediction_error,
        },
        "paired_prediction_means": {
            "generated": generated_paired,
            "field": field_paired,
            "field_minus_generated": field_paired - generated_paired,
        },
        "independent_branch_factorial_raw_means": cross,
        "factorial_attribution": {
            "spatial_marginal_at_generated_scalars": spatial_marginal,
            "scalar_marginal_at_generated_spatial": scalar_marginal,
            "factorial_interaction": factorial_interaction,
            "generated_pairing_effect": generated_paired - base,
            "field_pairing_effect": field_paired - cross["field_spatial__field_scalar"],
            "leading_branch_by_frozen_2x_rule": leading_branch,
        },
        "scalar_support": {
            "field_feature_values_outside_generated_support": int(
                sum(row["field_outside_generated_support"] for row in scalar_rows)
            ),
            "field_rows_with_any_value_outside_generated_support": int(
                (((field_scalars < generated_min) | (field_scalars > generated_max)).any(axis=1)).sum()
            ),
            "top25_single_feature_replacement_effects": scalar_ranked[:25],
            "top25_absolute_standardized_mean_shifts": sorted(
                scalar_rows,
                key=lambda row: abs(row["standardized_mean_shift"]),
                reverse=True,
            )[:25],
        },
        "spatial_support": {
            "field_plane_totals_outside_generated_support": int(
                sum(row["field_outside_generated_total_support"] for row in spatial_rows)
            ),
            "top20_single_plane_replacement_effects": spatial_ranked[:20],
            "planes": spatial_rows,
        },
        "artifacts": {
            "field_features": str(FIELD_FEATURES),
            "field_features_sha256": sha256(FIELD_FEATURES),
            "model_sha256": sha256(MODEL),
            "binary_sha256": field_payload["binary_sha256"],
            "checkpoint_sha256": field_payload["checkpoint_sha256"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--binary", type=Path, default=BINARY)
    parser.add_argument("--field-features", type=Path, default=FIELD_FEATURES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh or not args.field_features.exists():
        rows = extract_field_features(args.checkpoint, args.binary, args.field_features)
        field_payload = json.loads(args.field_features.read_text())
        assert len(rows) == 80
    else:
        field_payload = json.loads(args.field_features.read_text())
    result = analyze(field_payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({
        "complete": result["complete"],
        "paired": result["paired_prediction_means"],
        "attribution": result["factorial_attribution"],
        "top_scalar": result["scalar_support"]["top25_single_feature_replacement_effects"][:5],
        "top_spatial": result["spatial_support"]["top20_single_plane_replacement_effects"][:5],
        "output": str(args.output),
    }, indent=1))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
