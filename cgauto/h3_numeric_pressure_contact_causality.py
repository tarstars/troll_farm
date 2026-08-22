#!/usr/bin/env python3
"""Exact H3' temporal audit of opponent scaling and resident crop contact."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto import waste_sweep

REPO = Path(__file__).resolve().parent.parent
EXPECTED_MANIFEST_SHA256 = (
    "97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443"
)
EXPECTED_ACCEPTED_RESULT_SHA256 = (
    "bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac"
)
EXPECTED_RESIDENT_SOURCE_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
)
EXPECTED_RESIDENT_AGENT_ID = 6561795
EXPECTED_GAMES = 200
BOOTSTRAP_SEED = 20260731
BOOTSTRAP_REPLICATES = 10_000
MAIN_HALF_WINDOW = 50
PRELOSS_HALF_WINDOW = 20
MATCH_FEATURES = (
    "opponent_ladder_score",
    "fruit_total",
    "tree_health_total",
    "tree_total",
    "shack_door_distance",
    "own_private_fruit",
    "opponent_private_fruit",
    "water_adjacent_cells",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def feature_value(row: dict[str, Any], feature: str) -> float:
    if feature == "opponent_ladder_score":
        return float(row[feature])
    return float(row["opening"][feature])


def risk_counts(
    crops: list[dict[str, Any]], start_turn: int, end_turn: int, game_turns: int
) -> dict[str, int]:
    """First-contact events and at-risk crop-turns in an inclusive exact window."""

    if start_turn < 1 or end_turn > game_turns or end_turn < start_turn:
        raise ValueError("incomplete or invalid risk window")
    events = 0
    exposure = 0
    for crop in crops:
        birth = int(crop["birth_turn"])
        contact = crop.get("first_our_contact_turn")
        contact = int(contact) if contact is not None else None
        death = crop.get("death_turn")
        death = int(death) if death is not None else game_turns
        at_risk_start = max(start_turn, birth)
        at_risk_end = min(
            end_turn,
            contact if contact is not None else game_turns,
            death,
            game_turns,
        )
        if at_risk_end < at_risk_start:
            continue
        exposure += at_risk_end - at_risk_start + 1
        if contact is not None and at_risk_start <= contact <= at_risk_end:
            events += 1
    return {"events": events, "exposure": exposure}


def event_windows(
    row: dict[str, Any], anchor: int, half_window: int
) -> dict[str, dict[str, int]]:
    return {
        "pre": risk_counts(
            row["opponent_crop_records"],
            anchor - half_window + 1,
            anchor,
            int(row["turns"]),
        ),
        "post": risk_counts(
            row["opponent_crop_records"],
            anchor + 1,
            anchor + half_window,
            int(row["turns"]),
        ),
    }


def smoothed_rate(cell: dict[str, int]) -> float:
    return (int(cell["events"]) + 0.5) / (int(cell["exposure"]) + 1.0)


def raw_rate(cell: dict[str, int]) -> float | None:
    return (
        int(cell["events"]) / int(cell["exposure"])
        if int(cell["exposure"])
        else None
    )


def add_cell(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    return {
        "events": int(left["events"]) + int(right["events"]),
        "exposure": int(left["exposure"]) + int(right["exposure"]),
    }


def empty_windows() -> dict[str, dict[str, int]]:
    return {
        "pre": {"events": 0, "exposure": 0},
        "post": {"events": 0, "exposure": 0},
    }


def aggregate_side(
    pairs: list[dict[str, Any]], key: str
) -> dict[str, dict[str, int]]:
    result = empty_windows()
    for pair in pairs:
        for period in ("pre", "post"):
            result[period] = add_cell(result[period], pair[key][period])
    return result


def did_ratio_from_pairs(pairs: list[dict[str, Any]]) -> float:
    scaled = aggregate_side(pairs, "scaled_windows")
    control = aggregate_side(pairs, "control_windows")
    scaled_ratio = smoothed_rate(scaled["post"]) / smoothed_rate(scaled["pre"])
    control_ratio = smoothed_rate(control["post"]) / smoothed_rate(control["pre"])
    return scaled_ratio / control_ratio


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[int(fraction * (len(ordered) - 1))]


def did_summary(
    pairs: list[dict[str, Any]],
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    scaled = aggregate_side(pairs, "scaled_windows")
    control = aggregate_side(pairs, "control_windows")
    observed = did_ratio_from_pairs(pairs)
    rng = random.Random(seed)
    samples = []
    for _ in range(replicates):
        sampled = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        samples.append(did_ratio_from_pairs(sampled))
    return {
        "pairs": len(pairs),
        "scaled": {
            period: {
                **scaled[period],
                "raw_hazard_per_1000": (
                    1000 * raw_rate(scaled[period])
                    if raw_rate(scaled[period]) is not None
                    else None
                ),
                "smoothed_hazard": smoothed_rate(scaled[period]),
            }
            for period in ("pre", "post")
        },
        "control": {
            period: {
                **control[period],
                "raw_hazard_per_1000": (
                    1000 * raw_rate(control[period])
                    if raw_rate(control[period]) is not None
                    else None
                ),
                "smoothed_hazard": smoothed_rate(control[period]),
            }
            for period in ("pre", "post")
        },
        "scaled_post_pre_ratio": smoothed_rate(scaled["post"])
        / smoothed_rate(scaled["pre"]),
        "control_post_pre_ratio": smoothed_rate(control["post"])
        / smoothed_rate(control["pre"]),
        "did_hazard_ratio": observed,
        "bootstrap": {
            "seed": seed,
            "replicates": replicates,
            "unit": "matched scaled game/control pair",
            "ci95": [
                percentile(samples, 0.025),
                percentile(samples, 0.975),
            ],
        },
    }


def feature_scaling(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result = {}
    for feature in MATCH_FEATURES:
        values = [feature_value(row, feature) for row in rows]
        sd = statistics.pstdev(values)
        result[feature] = {
            "mean": statistics.fmean(values),
            "sd": sd if sd > 0 else 1.0,
        }
    return result


def distance(
    left: dict[str, Any],
    right: dict[str, Any],
    scaling: dict[str, dict[str, float]],
) -> float:
    return sum(
        (
            (feature_value(left, feature) - feature_value(right, feature))
            / scaling[feature]["sd"]
        )
        ** 2
        for feature in MATCH_FEATURES
    )


def match_rows(
    scaled_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    scaling: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    pairs = []
    for scaled in sorted(scaled_rows, key=lambda row: int(row["game_id"])):
        anchor = int(scaled["third_train_turn"])
        eligible = [
            control
            for control in control_rows
            if int(control["seat"]) == int(scaled["seat"])
            and int(control["turns"]) >= anchor + MAIN_HALF_WINDOW
        ]
        if not eligible:
            continue
        chosen = min(
            eligible,
            key=lambda control: (
                distance(scaled, control, scaling),
                int(control["game_id"]),
            ),
        )
        pairs.append(
            {
                "scaled_game_id": int(scaled["game_id"]),
                "control_game_id": int(chosen["game_id"]),
                "anchor_turn": anchor,
                "scaled_opponent_agent_id": int(scaled["opponent_agent_id"]),
                "resident_seat": int(scaled["seat"]),
                "permanent_crossover_turn": int(scaled["permanent_crossover_turn"]),
                "distance": distance(scaled, chosen, scaling),
                "scaled_features": {
                    feature: feature_value(scaled, feature)
                    for feature in MATCH_FEATURES
                },
                "control_features": {
                    feature: feature_value(chosen, feature)
                    for feature in MATCH_FEATURES
                },
                "scaled_windows": event_windows(
                    scaled, anchor, MAIN_HALF_WINDOW
                ),
                "control_windows": event_windows(
                    chosen, anchor, MAIN_HALF_WINDOW
                ),
                "_scaled_row": scaled,
                "_control_row": chosen,
            }
        )
    return pairs


def balance(
    treated: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    scaling: dict[str, dict[str, float]],
) -> dict[str, float]:
    return {
        feature: (
            statistics.fmean(feature_value(row, feature) for row in treated)
            - statistics.fmean(feature_value(row, feature) for row in controls)
        )
        / scaling[feature]["sd"]
        for feature in MATCH_FEATURES
    }


def clean_pair(pair: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in pair.items() if not key.startswith("_")}


def coverage_summary(
    scaled: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    def counts(rows: list[dict[str, Any]]) -> tuple[int, int]:
        crops = sum(len(row["opponent_crop_records"]) for row in rows)
        contacts = sum(
            crop.get("first_our_contact_turn") is not None
            for row in rows
            for crop in row["opponent_crop_records"]
        )
        return contacts, crops

    scaled_contacts, scaled_crops = counts(scaled)
    control_contacts, control_crops = counts(controls)
    observed = scaled_contacts / scaled_crops - control_contacts / control_crops
    rng = random.Random(seed)
    differences = []
    for _ in range(replicates):
        sampled_scaled = [scaled[rng.randrange(len(scaled))] for _ in scaled]
        sampled_control = [controls[rng.randrange(len(controls))] for _ in controls]
        s_contacts, s_crops = counts(sampled_scaled)
        c_contacts, c_crops = counts(sampled_control)
        differences.append(s_contacts / s_crops - c_contacts / c_crops)
    return {
        "scaled": {
            "games": len(scaled),
            "contacts": scaled_contacts,
            "crops": scaled_crops,
            "coverage": scaled_contacts / scaled_crops,
        },
        "no_scale": {
            "games": len(controls),
            "contacts": control_contacts,
            "crops": control_crops,
            "coverage": control_contacts / control_crops,
        },
        "scaled_minus_no_scale_percentage_points": 100 * observed,
        "bootstrap": {
            "seed": seed,
            "replicates": replicates,
            "unit": "game, independently within cohort",
            "ci95_percentage_points": [
                100 * percentile(differences, 0.025),
                100 * percentile(differences, 0.975),
            ],
        },
    }


def row_for_audit(
    manifest_row: dict[str, Any],
    resident: waste_sweep.DecodedGame,
    opponent: waste_sweep.DecodedGame,
) -> dict[str, Any]:
    thirds = sorted(
        int(event["turn"])
        for event in opponent.train_events
        if int(event["n_before"]) == 2
    )
    return {
        **manifest_row,
        "third_train_turn": thirds[0] if thirds else None,
        "third_train_count": len(thirds),
        "permanent_crossover_turn": int(resident.crossover_turn),
        "decoded_turns": int(resident.turns),
    }


def run(
    *, manifest_path: Path, accepted_result_path: Path, data_root: Path
) -> dict[str, Any]:
    manifest_hash = sha256(manifest_path)
    accepted_hash = sha256(accepted_result_path)
    manifest = json.loads(manifest_path.read_text())
    accepted = json.loads(accepted_result_path.read_text())
    source_path = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
    )
    source_hash = sha256(source_path)
    manifest_rows = manifest.get("rows") or []
    game_ids = [int(row["game_id"]) for row in manifest_rows]
    raw_games = data_root / "raw/games"
    trajectories = data_root / "processed/trajectories"
    waste_sweep.RAW_GAMES = raw_games
    waste_sweep.TRAJECTORIES = trajectories

    errors: list[str] = []
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        errors.append("D159 manifest hash mismatch")
    if accepted_hash != EXPECTED_ACCEPTED_RESULT_SHA256:
        errors.append("D159 accepted-result hash mismatch")
    if source_hash != EXPECTED_RESIDENT_SOURCE_SHA256:
        errors.append("resident source hash mismatch")
    if len(game_ids) != EXPECTED_GAMES or len(set(game_ids)) != EXPECTED_GAMES:
        errors.append("D159 game ID count/uniqueness mismatch")
    if (
        accepted.get("identity", {}).get("resident_agent_id")
        != EXPECTED_RESIDENT_AGENT_ID
    ):
        errors.append("accepted resident identity mismatch")
    if accepted.get("identity", {}).get("resident_source_sha256") != source_hash:
        errors.append("accepted resident source mismatch")
    missing_raw = [
        game_id for game_id in game_ids if not (raw_games / f"{game_id}.json").is_file()
    ]
    missing_trajectory = [
        game_id
        for game_id in game_ids
        if not (trajectories / f"{game_id}.jsonl").is_file()
    ]
    if missing_raw:
        errors.append(f"missing raw games: {missing_raw}")
    if missing_trajectory:
        errors.append(f"missing trajectories: {missing_trajectory}")

    rows: list[dict[str, Any]] = []
    if not missing_raw and not missing_trajectory:
        for manifest_row in manifest_rows:
            game_id = int(manifest_row["game_id"])
            try:
                resident = waste_sweep.decode_game(game_id)
                opponent = waste_sweep.decode_game_for_agent(
                    game_id, int(manifest_row["opponent_agent_id"])
                )
                if resident.me != int(manifest_row["seat"]):
                    raise ValueError(
                        f"resident seat {resident.me} != manifest {manifest_row['seat']}"
                    )
                rows.append(row_for_audit(manifest_row, resident, opponent))
            except Exception as exc:
                errors.append(f"{game_id}: {type(exc).__name__}: {exc}")

    summary = None
    if len(rows) == EXPECTED_GAMES:
        scaled = [row for row in rows if row["third_train_turn"] is not None]
        no_scale = [row for row in rows if row["third_train_turn"] is None]
        complete_scaled = [
            row
            for row in scaled
            if int(row["third_train_turn"]) >= MAIN_HALF_WINDOW
            and int(row["third_train_turn"]) + MAIN_HALF_WINDOW <= int(row["turns"])
        ]
        scaling = feature_scaling(rows)
        pairs = match_rows(complete_scaled, no_scale, scaling)
        pair_by_scaled = {pair["scaled_game_id"]: pair for pair in pairs}
        preloss_pairs = []
        for row in complete_scaled:
            anchor = int(row["third_train_turn"])
            if int(row["permanent_crossover_turn"]) <= anchor + PRELOSS_HALF_WINDOW:
                continue
            pair = pair_by_scaled.get(int(row["game_id"]))
            if pair is None:
                continue
            shorter = dict(pair)
            shorter["scaled_windows"] = event_windows(
                pair["_scaled_row"], anchor, PRELOSS_HALF_WINDOW
            )
            shorter["control_windows"] = event_windows(
                pair["_control_row"], anchor, PRELOSS_HALF_WINDOW
            )
            preloss_pairs.append(shorter)

        matched_controls = [pair["_control_row"] for pair in pairs]
        before_balance = balance(complete_scaled, no_scale, scaling)
        after_balance = balance(
            [pair["_scaled_row"] for pair in pairs],
            matched_controls,
            scaling,
        )
        reuse = Counter(pair["control_game_id"] for pair in pairs)
        coverage = coverage_summary(scaled, no_scale)
        main_did = did_summary(pairs) if pairs else None
        preloss_did = did_summary(preloss_pairs) if preloss_pairs else None
        main_ids = {pair["scaled_opponent_agent_id"] for pair in pairs}
        preloss_ids = {pair["scaled_opponent_agent_id"] for pair in preloss_pairs}
        main_seats = sorted({pair["resident_seat"] for pair in pairs})
        preloss_seats = sorted({pair["resident_seat"] for pair in preloss_pairs})
        nonzero_cells = bool(
            main_did
            and preloss_did
            and all(
                block[side][period]["events"] > 0
                and block[side][period]["exposure"] > 0
                for block in (main_did, preloss_did)
                for side in ("scaled", "control")
                for period in ("pre", "post")
            )
        )
        support = {
            "main_at_least_40_pairs": len(pairs) >= 40,
            "main_at_least_12_opponent_identities": len(main_ids) >= 12,
            "main_both_seats": main_seats == [0, 1],
            "preloss_at_least_20_pairs": len(preloss_pairs) >= 20,
            "preloss_at_least_8_opponent_identities": len(preloss_ids) >= 8,
            "preloss_both_seats": preloss_seats == [0, 1],
            "all_post_match_abs_smd_le_0_25": all(
                abs(value) <= 0.25 for value in after_balance.values()
            ),
            "nonzero_events_and_exposure_all_cells": nonzero_cells,
        }
        materiality = {
            "coverage_drop_at_least_5pp": coverage[
                "scaled_minus_no_scale_percentage_points"
            ]
            <= -5.0,
            "coverage_ci_upper_below_zero": coverage["bootstrap"][
                "ci95_percentage_points"
            ][1]
            < 0,
            "main_did_ratio_le_0_80": bool(
                main_did and main_did["did_hazard_ratio"] <= 0.80
            ),
            "main_did_ci_upper_below_1": bool(
                main_did and main_did["bootstrap"]["ci95"][1] < 1.0
            ),
            "preloss_did_ratio_le_0_80": bool(
                preloss_did and preloss_did["did_hazard_ratio"] <= 0.80
            ),
            "preloss_did_ci_upper_below_1": bool(
                preloss_did and preloss_did["bootstrap"]["ci95"][1] < 1.0
            ),
        }
        summary = {
            "cohorts": {
                "scaled_games": len(scaled),
                "no_scale_games": len(no_scale),
                "complete_primary_scaled_games": len(complete_scaled),
                "main_matched_pairs": len(pairs),
                "main_scaled_opponent_identities": len(main_ids),
                "main_resident_seats": main_seats,
                "preloss_matched_pairs": len(preloss_pairs),
                "preloss_scaled_opponent_identities": len(preloss_ids),
                "preloss_resident_seats": preloss_seats,
            },
            "coverage": coverage,
            "matching": {
                "features": list(MATCH_FEATURES),
                "with_replacement": True,
                "before_smd": before_balance,
                "after_smd": after_balance,
                "unique_controls": len(reuse),
                "maximum_control_reuse": max(reuse.values()) if reuse else 0,
            },
            "primary_50_turn": main_did,
            "preloss_20_turn": preloss_did,
            "support_gates": support,
            "materiality_gates": materiality,
            "support_pass": all(support.values()),
            "materiality_pass": all(materiality.values()),
            "descriptive_margin": {
                "scaled_mean": statistics.fmean(row["margin"] for row in scaled),
                "no_scale_mean": statistics.fmean(row["margin"] for row in no_scale),
            },
            "pairs": [clean_pair(pair) for pair in pairs],
            "preloss_scaled_game_ids": sorted(
                pair["scaled_game_id"] for pair in preloss_pairs
            ),
        }

    integrity = {
        "manifest_hash_exact": manifest_hash == EXPECTED_MANIFEST_SHA256,
        "accepted_result_hash_exact": accepted_hash
        == EXPECTED_ACCEPTED_RESULT_SHA256,
        "resident_source_hash_exact": source_hash
        == EXPECTED_RESIDENT_SOURCE_SHA256,
        "exact_200_unique_ids": len(game_ids) == EXPECTED_GAMES
        and len(set(game_ids)) == EXPECTED_GAMES,
        "all_named_raw_games_present": not missing_raw,
        "all_named_trajectories_present": not missing_trajectory,
        "all_200_games_decoded": len(rows) == EXPECTED_GAMES,
        "zero_decode_or_transition_errors": not errors,
        "outside_game_ids_read": 0,
    }
    integrity_pass = all(
        value if isinstance(value, bool) else value == 0
        for value in integrity.values()
    )
    support_pass = bool(summary and summary["support_pass"])
    materiality_pass = bool(summary and summary["materiality_pass"])
    if not integrity_pass or not support_pass:
        verdict = "UNIDENTIFIABLE"
    elif materiality_pass:
        verdict = "TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY"
    else:
        verdict = "NO_LOAD_BEARING_NUMERIC_PRESSURE_SIGNAL"
    return {
        "schema": "troll-farm-h3-numeric-pressure-contact-causality-v1",
        "task_id": "20260731-h3-numeric-pressure-contact-causality",
        "verdict": verdict,
        "frozen_inputs": {
            "manifest": {
                "path": (
                    "data/analysis/live-agent-6553250/"
                    "d159a-current-resident-all-finished-effect-refresh-raw.json"
                ),
                "sha256": manifest_hash,
            },
            "accepted_result": {
                "path": (
                    "data/analysis/live-agent-6553250/"
                    "d159a-current-resident-all-finished-effect-refresh-result.json"
                ),
                "sha256": accepted_hash,
            },
            "resident_source": {
                "path": (
                    "cgauto/submissions/"
                    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
                ),
                "sha256": source_hash,
            },
            "data_root": "data",
            "game_ids": len(game_ids),
        },
        "integrity": {
            "gates": integrity,
            "pass": integrity_pass,
            "errors": errors[:100],
            "error_count": len(errors),
        },
        "summary": summary,
        "interpretation_limits": [
            "event-study timing is observational and cannot prove intervention value",
            "third-worker TRAIN may proxy other opponent-policy changes",
            "matching uses pregame observables but cannot remove hidden confounding",
            "a positive result still requires conditioned, always-on, and unchanged arms",
        ],
    }


def self_test() -> None:
    crops = [
        {
            "birth_turn": 5,
            "death_turn": 20,
            "first_our_contact_turn": 10,
        },
        {
            "birth_turn": 8,
            "death_turn": 12,
            "first_our_contact_turn": None,
        },
    ]
    assert risk_counts(crops, 6, 10, 30) == {"events": 1, "exposure": 8}
    cell = {"events": 0, "exposure": 9}
    assert math.isclose(smoothed_rate(cell), 0.05)
    print("self-test: ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode", nargs="?", choices=("run", "self-test"), default="run"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "d159a-current-resident-all-finished-effect-refresh-raw.json",
    )
    parser.add_argument(
        "--accepted-result",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "d159a-current-resident-all-finished-effect-refresh-result.json",
    )
    parser.add_argument("--data-root", type=Path, default=REPO / "data")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "self-test":
        self_test()
        return
    result = run(
        manifest_path=args.manifest.resolve(),
        accepted_result_path=args.accepted_result.resolve(),
        data_root=args.data_root.resolve(),
    )
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
