#!/usr/bin/env python3
"""M5: characterize game length and matched turn-cap outcome associations."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import random
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.seat_asymmetry import load_source  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
PROJECT = Path("/home/tarstars/prj/troll_farm")
DEFAULT_GAMES = PROJECT / "data/processed/games.jsonl"
DEFAULT_OUTPUT = REPO / "local_codex_1/m5-game-length-effects"
CAP_TURNS = 300
PRIMARY_BAND = 1.0
SENSITIVITY_BANDS = (0.5, 1.5)
BOOTSTRAP_REPS = 20_000
NULL_REPS = 50_000
SEED = 20_260_730
EXPECTED_DURATION = {
    "min": 106,
    "max": 300,
    "cap_games": 125,
}
DURATION_BINS = (
    ("100_to_149", 100, 149),
    ("150_to_199", 150, 199),
    ("200_to_249", 200, 249),
    ("250_to_299", 250, 299),
    ("300", 300, 300),
)


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: (item[1], item[0]))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        rank = (index + 1 + end) / 2
        for original, _value in indexed[index:end]:
            ranks[original] = rank
        index = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    numerator = sum(
        (lvalue - left_mean) * (rvalue - right_mean)
        for lvalue, rvalue in zip(left, right)
    )
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return numerator / denominator if denominator else 0.0


def duration_summary(rows: list[dict]) -> dict:
    return {
        "games": len(rows),
        "exact_identities": len({row["opponent_id"] for row in rows}),
        "pseudos": len({row["opponent_pseudo"] for row in rows}),
        "seat_0": sum(row["seat"] == 0 for row in rows),
        "seat_1": sum(row["seat"] == 1 for row in rows),
        "mean_turns": statistics.mean(row["turns"] for row in rows),
        "median_turns": statistics.median(row["turns"] for row in rows),
        "mean_margin": statistics.mean(row["margin"] for row in rows),
        "mean_win": statistics.mean(row["win"] for row in rows),
        "mean_resident_final_score": statistics.mean(
            row["resident_final_score"] for row in rows
        ),
        "mean_opponent_final_score": statistics.mean(
            row["opponent_final_score"] for row in rows
        ),
        "mean_resident_score_pre": statistics.mean(
            row["resident_score"] for row in rows
        ),
        "mean_opponent_score_pre": statistics.mean(
            row["opponent_score"] for row in rows
        ),
    }


def raw_characterization(rows: list[dict]) -> dict:
    bins = {}
    for label, lower, upper in DURATION_BINS:
        subset = [row for row in rows if lower <= row["turns"] <= upper]
        bins[label] = duration_summary(subset)
    cap = [row for row in rows if row["turns"] == CAP_TURNS]
    noncap = [row for row in rows if row["turns"] < CAP_TURNS]
    noncap_turns = [row["turns"] for row in noncap]
    duration_counts = Counter(row["turns"] for row in rows)
    return {
        "duration_range": [min(row["turns"] for row in rows), max(row["turns"] for row in rows)],
        "duration_counts": {str(turns): count for turns, count in sorted(duration_counts.items())},
        "bins": bins,
        "cap": duration_summary(cap),
        "noncap": duration_summary(noncap),
        "raw_cap_minus_noncap": {
            "margin": statistics.mean(row["margin"] for row in cap)
            - statistics.mean(row["margin"] for row in noncap),
            "win": statistics.mean(row["win"] for row in cap)
            - statistics.mean(row["win"] for row in noncap),
            "resident_final_score": statistics.mean(
                row["resident_final_score"] for row in cap
            )
            - statistics.mean(row["resident_final_score"] for row in noncap),
            "opponent_final_score": statistics.mean(
                row["opponent_final_score"] for row in cap
            )
            - statistics.mean(row["opponent_final_score"] for row in noncap),
        },
        "noncap_turn_quantiles": {
            "q10": quantile(noncap_turns, 0.10),
            "q25": quantile(noncap_turns, 0.25),
            "median": statistics.median(noncap_turns),
            "q75": quantile(noncap_turns, 0.75),
            "q90": quantile(noncap_turns, 0.90),
        },
        "noncap_spearman_turns_margin": pearson(
            average_ranks([row["turns"] for row in noncap]),
            average_ranks([row["margin"] for row in noncap]),
        ),
    }


def identity_matches(target: dict, control: dict, mode: str) -> bool:
    if mode == "exclude_pseudo":
        return control["opponent_pseudo"] != target["opponent_pseudo"]
    if mode == "same_pseudo":
        return control["opponent_pseudo"] == target["opponent_pseudo"]
    if mode == "same_exact":
        return control["opponent_id"] == target["opponent_id"]
    raise ValueError(f"unknown identity mode: {mode}")


def is_control(
    target: dict,
    control: dict,
    *,
    identity_mode: str,
    opponent_score_band: float,
    min_control_turns: int | None,
) -> bool:
    return (
        control["turns"] < CAP_TURNS
        and (min_control_turns is None or control["turns"] >= min_control_turns)
        and identity_matches(target, control, identity_mode)
        and control["seat"] == target["seat"]
        and control["map_width"] == target["map_width"]
        and control["map_height"] == target["map_height"]
        and abs(control["opponent_score"] - target["opponent_score"])
        <= opponent_score_band
        and abs(control["resident_score"] - target["resident_score"]) <= 0.25
        and abs(control["initial_trees"] - target["initial_trees"]) <= 4
    )


def matched_targets(
    rows: list[dict],
    *,
    identity_mode: str = "exclude_pseudo",
    opponent_score_band: float = PRIMARY_BAND,
    min_control_turns: int | None = None,
) -> tuple[list[dict], list[dict]]:
    targets = sorted(
        (row for row in rows if row["turns"] == CAP_TURNS),
        key=lambda row: (row["game_id"], row["record_index"]),
    )
    supported = []
    unsupported = []
    for target in targets:
        controls = [
            control
            for control in rows
            if is_control(
                target,
                control,
                identity_mode=identity_mode,
                opponent_score_band=opponent_score_band,
                min_control_turns=min_control_turns,
            )
        ]
        controls.sort(key=lambda row: (row["game_id"], row["record_index"]))
        if not controls:
            unsupported.append(
                {
                    "game_id": target["game_id"],
                    "opponent_id": target["opponent_id"],
                    "opponent_pseudo": target["opponent_pseudo"],
                }
            )
            continue
        expected_margin = statistics.mean(control["margin"] for control in controls)
        expected_win = statistics.mean(control["win"] for control in controls)
        supported.append(
            {
                "game_id": target["game_id"],
                "record_index": target["record_index"],
                "opponent_id": target["opponent_id"],
                "opponent_pseudo": target["opponent_pseudo"],
                "seat": target["seat"],
                "control_count": len(controls),
                "control_game_ids": [control["game_id"] for control in controls],
                "control_turn_min": min(control["turns"] for control in controls),
                "control_turn_max": max(control["turns"] for control in controls),
                "target_margin": target["margin"],
                "expected_margin": expected_margin,
                "margin_residual": target["margin"] - expected_margin,
                "target_win": target["win"],
                "expected_win": expected_win,
                "win_residual": target["win"] - expected_win,
                "_control_margins": [control["margin"] for control in controls],
            }
        )
    return supported, unsupported


def cluster_values(matched: list[dict], field: str) -> dict[int, list[float]]:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in matched:
        clusters[row["opponent_id"]].append(row[field])
    return dict(sorted(clusters.items()))


def cluster_bootstrap_ci(
    matched: list[dict],
    *,
    field: str,
    reps: int,
    seed: int,
) -> tuple[float, float]:
    clusters = cluster_values(matched, field)
    if not clusters:
        raise ValueError("no clusters")
    keys = list(clusters)
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sampled = [rng.choice(keys) for _key in keys]
        values = [value for key in sampled for value in clusters[key]]
        estimates.append(statistics.mean(values))
    estimates.sort()
    return quantile(estimates, 0.025), quantile(estimates, 0.975)


def matched_null_p(
    matched: list[dict],
    *,
    reps: int,
    seed: int,
) -> float:
    observed = abs(statistics.mean(row["margin_residual"] for row in matched))
    centers = [
        statistics.mean(row["_control_margins"]) for row in matched
    ]
    rng = random.Random(seed)
    exceedances = 0
    for _ in range(reps):
        value = abs(
            statistics.mean(
                rng.choice(row["_control_margins"]) - center
                for row, center in zip(matched, centers)
            )
        )
        exceedances += value >= observed
    return (1 + exceedances) / (reps + 1)


def supported_summary(matched: list[dict]) -> dict:
    if not matched:
        return {
            "supported_targets": 0,
            "exact_identities": 0,
            "pseudos": 0,
            "margin_residual": None,
            "win_residual": None,
        }
    return {
        "supported_targets": len(matched),
        "exact_identities": len({row["opponent_id"] for row in matched}),
        "pseudos": len({row["opponent_pseudo"] for row in matched}),
        "control_count_min": min(row["control_count"] for row in matched),
        "control_count_median": statistics.median(
            row["control_count"] for row in matched
        ),
        "control_count_max": max(row["control_count"] for row in matched),
        "margin_residual": statistics.mean(row["margin_residual"] for row in matched),
        "win_residual": statistics.mean(row["win_residual"] for row in matched),
    }


def split_summaries(matched: list[dict]) -> dict:
    seats = {}
    for seat in (0, 1):
        subset = [row for row in matched if row["seat"] == seat]
        seats[str(seat)] = supported_summary(subset)
    ordered = sorted(
        matched, key=lambda row: (row["game_id"], row["record_index"])
    )
    midpoint = len(ordered) // 2
    halves = {
        "early": supported_summary(ordered[:midpoint]),
        "late": supported_summary(ordered[midpoint:]),
    }
    return {"seats": seats, "chronological_halves": halves}


def leave_one_pseudo_out(matched: list[dict]) -> list[dict]:
    results = []
    for pseudo in sorted({row["opponent_pseudo"] for row in matched}):
        kept = [row for row in matched if row["opponent_pseudo"] != pseudo]
        results.append(
            {
                "omitted_pseudo": pseudo,
                "targets_remaining": len(kept),
                "margin_residual": statistics.mean(
                    row["margin_residual"] for row in kept
                ),
                "win_residual": statistics.mean(row["win_residual"] for row in kept),
            }
        )
    return results


def same_sign(value: float | None, reference: float) -> bool:
    if value is None or value == 0 or reference == 0:
        return False
    return (value > 0) == (reference > 0)


def strip_private(matched: list[dict]) -> list[dict]:
    return [
        {key: value for key, value in row.items() if not key.startswith("_")}
        for row in matched
    ]


def lineage_table(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["opponent_pseudo"]].append(row)
    table = []
    for pseudo, subset in sorted(grouped.items()):
        cap = [row for row in subset if row["turns"] == CAP_TURNS]
        noncap = [row for row in subset if row["turns"] < CAP_TURNS]
        table.append(
            {
                "pseudo": pseudo,
                "exact_ids": len({row["opponent_id"] for row in subset}),
                "games": len(subset),
                "cap_games": len(cap),
                "cap_share": len(cap) / len(subset),
                "mean_turns": statistics.mean(row["turns"] for row in subset),
                "cap_mean_margin": (
                    statistics.mean(row["margin"] for row in cap) if cap else None
                ),
                "noncap_mean_margin": (
                    statistics.mean(row["margin"] for row in noncap)
                    if noncap
                    else None
                ),
            }
        )
    return table


def build_result(
    rows: list[dict],
    source: dict,
    *,
    bootstrap_reps: int,
    null_reps: int,
    seed: int,
) -> dict:
    duration_checks = {
        "min": min(row["turns"] for row in rows) == EXPECTED_DURATION["min"],
        "max": max(row["turns"] for row in rows) == EXPECTED_DURATION["max"],
        "cap_games": sum(row["turns"] == CAP_TURNS for row in rows)
        == EXPECTED_DURATION["cap_games"],
    }
    if not all(duration_checks.values()):
        raise ValueError(f"duration support mismatch: {duration_checks}")
    primary_rows, primary_unsupported = matched_targets(rows)
    primary = supported_summary(primary_rows)
    primary["unsupported_targets"] = len(primary_unsupported)
    ci = cluster_bootstrap_ci(
        primary_rows,
        field="margin_residual",
        reps=bootstrap_reps,
        seed=seed,
    )
    p_value = matched_null_p(primary_rows, reps=null_reps, seed=seed + 1)
    primary["margin_ci95"] = list(ci)
    primary["two_sided_matched_null_p"] = p_value
    primary["targets"] = strip_private(primary_rows)
    primary["unsupported"] = primary_unsupported
    split = split_summaries(primary_rows)
    band_rows = {
        str(band): matched_targets(
            rows,
            opponent_score_band=band,
        )[0]
        for band in SENSITIVITY_BANDS
    }
    band_summaries = {
        band: supported_summary(subset) for band, subset in band_rows.items()
    }
    same_pseudo_rows, _ = matched_targets(rows, identity_mode="same_pseudo")
    exact_rows, _ = matched_targets(rows, identity_mode="same_exact")
    near_cap_rows, _ = matched_targets(rows, min_control_turns=250)
    same_pseudo = supported_summary(same_pseudo_rows)
    same_exact = supported_summary(exact_rows)
    near_cap = supported_summary(near_cap_rows)
    near_cap["identified"] = (
        near_cap["supported_targets"] >= 30
        and near_cap["exact_identities"] >= 15
    )
    leave_one_out = leave_one_pseudo_out(primary_rows)
    support_gates = {
        "source_integrity": source["hash_check"]
        and all(source["count_checks"].values())
        and all(duration_checks.values()),
        "at_least_80_supported_targets": primary["supported_targets"] >= 80,
        "at_least_30_exact_identities": primary["exact_identities"] >= 30,
        "at_least_30_supported_each_seat": all(
            split["seats"][str(seat)]["supported_targets"] >= 30 for seat in (0, 1)
        ),
        "at_least_35_supported_each_half": all(
            summary["supported_targets"] >= 35
            for summary in split["chronological_halves"].values()
        ),
    }
    support = all(support_gates.values())
    margin = primary["margin_residual"]
    win = primary["win_residual"]
    actionability_gates = {
        "source_and_primary_support": support,
        "absolute_margin_residual_at_least_20": abs(margin) >= 20,
        "bootstrap_ci_excludes_zero": ci[0] > 0 or ci[1] < 0,
        "two_sided_matched_null_p_at_most_0_05": p_value <= 0.05,
        "win_residual_same_sign_and_at_least_0_10": same_sign(win, margin)
        and abs(win) >= 0.10,
        "both_seats_same_sign": all(
            same_sign(split["seats"][str(seat)]["margin_residual"], margin)
            for seat in (0, 1)
        ),
        "both_time_halves_same_sign": all(
            same_sign(summary["margin_residual"], margin)
            for summary in split["chronological_halves"].values()
        ),
        "both_score_bands_same_sign": all(
            same_sign(summary["margin_residual"], margin)
            for summary in band_summaries.values()
        ),
        "same_pseudo_sensitivity_same_sign": same_sign(
            same_pseudo["margin_residual"], margin
        ),
        "leave_one_pseudo_out_same_sign": all(
            same_sign(row["margin_residual"], margin) for row in leave_one_out
        ),
    }
    material = all(actionability_gates.values())
    verdict = (
        "UNIDENTIFIABLE"
        if not support
        else "MATERIAL_CAP_LOSS_ASSOCIATION"
        if material and margin < 0
        else "MATERIAL_CAP_GAIN_ASSOCIATION"
        if material and margin > 0
        else "NO_MATERIAL_LENGTH_ASSOCIATION"
    )
    return {
        "verdict": verdict,
        "source": {
            **source,
            "duration_expected": EXPECTED_DURATION,
            "duration_checks": duration_checks,
        },
        "protocol": {
            "cap_turns": CAP_TURNS,
            "primary_identity_mode": "exclude_same_pseudo",
            "opponent_score_band": PRIMARY_BAND,
            "resident_score_band": 0.25,
            "initial_tree_band": 4,
            "bootstrap_reps": bootstrap_reps,
            "null_reps": null_reps,
            "seed": seed,
        },
        "raw": raw_characterization(rows),
        "primary": primary,
        "splits": split,
        "sensitivities": {
            "opponent_score_bands": band_summaries,
            "same_pseudo": same_pseudo,
            "same_exact_opponent": same_exact,
            "near_cap_250_to_299": near_cap,
        },
        "support_gates": support_gates,
        "material_association_gates": actionability_gates,
        "failed_material_association_gates": [
            key for key, passed in actionability_gates.items() if not passed
        ],
        "leave_one_pseudo_out": leave_one_out,
        "lineages": lineage_table(rows),
    }


def duration_bin_table(result: dict) -> list[dict]:
    table = []
    for label, _lower, _upper in DURATION_BINS:
        summary = result["raw"]["bins"][label]
        table.append({"duration_bin": label, **summary})
    return table


def report_text(result: dict) -> str:
    primary = result["primary"]
    raw = result["raw"]
    splits = result["splits"]
    failed = ", ".join(result["failed_material_association_gates"]) or "none"
    return f"""# M5 — exact-resident game length / turn cap

- Verdict: **{result['verdict']}**
- Raw duration range: {raw['duration_range'][0]}–{raw['duration_range'][1]}
- Turn-300 games: {raw['cap']['games']} / {raw['cap']['games'] + raw['noncap']['games']}
- Primary support: {primary['supported_targets']} cap targets / {primary['exact_identities']} exact identities
- Matched cap-minus-shorter margin: {primary['margin_residual']:+.3f}
- Cluster-bootstrap 95% CI: [{primary['margin_ci95'][0]:+.3f}, {primary['margin_ci95'][1]:+.3f}]
- Two-sided matched-null p: {primary['two_sided_matched_null_p']:.6f}
- Matched win residual: {primary['win_residual']:+.3f}

## Stability

- Seat 0 / 1: {splits['seats']['0']['margin_residual']:+.3f} / {splits['seats']['1']['margin_residual']:+.3f}
- Early / late targets: {splits['chronological_halves']['early']['margin_residual']:+.3f} / {splits['chronological_halves']['late']['margin_residual']:+.3f}
- Same-pseudonym sensitivity: {result['sensitivities']['same_pseudo']['margin_residual']:+.3f}
- Same-exact-opponent sensitivity: {result['sensitivities']['same_exact_opponent']['margin_residual']:+.3f}
- Near-cap 250–299 sensitivity: {result['sensitivities']['near_cap_250_to_299']['margin_residual']:+.3f}

## Failed material-association gates

{failed}

Duration/cap status is post-game. No result here is a causal turn-limit effect or
authorization for a duration-conditioned policy, resident change, simulation, or Arena.
"""


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n"
    )
    (output_dir / "report.md").write_text(report_text(result))
    duration_rows = duration_bin_table(result)
    duration_fields = list(duration_rows[0])
    with (output_dir / "duration_bins.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=duration_fields, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(duration_rows)
    lineage_fields = list(result["lineages"][0])
    with (output_dir / "lineages.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=lineage_fields, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(result["lineages"])


def synthetic_rows() -> list[dict]:
    rows = []
    game_id = 1
    for opponent_id, pseudo in ((10, "alpha"), (11, "beta"), (12, "gamma")):
        for seat in (0, 1):
            for turns, margin in ((260, 30.0), (280, 20.0), (300, -20.0)):
                rows.append(
                    {
                        "record_index": game_id,
                        "game_id": game_id,
                        "seat": seat,
                        "resident_score": 22.0,
                        "opponent_score": 23.0,
                        "opponent_id": opponent_id,
                        "opponent_pseudo": pseudo,
                        "map_width": 12,
                        "map_height": 12,
                        "initial_trees": 20,
                        "margin": margin,
                        "win": 1.0 if margin > 0 else 0.0,
                        "resident_final_score": 100.0,
                        "opponent_final_score": 100.0 - margin,
                        "resident_final_fruit": 10.0,
                        "resident_final_wood_points": 80.0,
                        "opponent_final_fruit": 10.0,
                        "opponent_final_wood_points": 80.0,
                        "turns": turns,
                    }
                )
                game_id += 1
    return rows


def self_test() -> None:
    rows = synthetic_rows()
    matched, unsupported = matched_targets(rows)
    assert len(matched) == 6 and not unsupported
    assert statistics.mean(row["margin_residual"] for row in matched) == -45.0
    same, _ = matched_targets(rows, identity_mode="same_pseudo")
    assert statistics.mean(row["margin_residual"] for row in same) == -45.0
    ci_one = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=200, seed=7
    )
    ci_two = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=200, seed=7
    )
    assert ci_one == ci_two == (-45.0, -45.0)
    p_one = matched_null_p(matched, reps=200, seed=8)
    p_two = matched_null_p(matched, reps=200, seed=8)
    assert p_one == p_two and 0 < p_one <= 1
    assert same_sign(-1.0, -2.0) and not same_sign(1.0, -2.0)
    print("self-test: ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    parser.add_argument("--null-reps", type=int, default=NULL_REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    rows, source = load_source(args.games)
    result = build_result(
        rows,
        source,
        bootstrap_reps=args.bootstrap_reps,
        null_reps=args.null_reps,
        seed=args.seed,
    )
    write_outputs(result, args.output_dir)
    print(
        f"{result['verdict']}: "
        f"margin={result['primary']['margin_residual']:+.3f}, "
        f"targets={result['primary']['supported_targets']}"
    )
    return 2 if result["verdict"] == "UNIDENTIFIABLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
