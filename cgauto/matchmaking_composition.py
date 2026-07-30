#!/usr/bin/env python3
"""M4: characterize exact-resident matchmaking composition and temporal drift."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import load_leaderboard  # noqa: E402
from cgauto.seat_asymmetry import load_source as load_game_source  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
PROJECT = Path("/home/tarstars/prj/troll_farm")
DEFAULT_GAMES = PROJECT / "data/processed/games.jsonl"
DEFAULT_LEADERBOARD = (
    PROJECT / "data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json"
)
DEFAULT_OUTPUT = REPO / "local_codex_1/m4-matchmaking-composition"
EXPECTED_LEADERBOARD_HASH = (
    "7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815"
)
PRIMARY_WINDOW = 60
SENSITIVITY_WINDOWS = (40, 80)
BLOCK_LENGTH = 10
BOOTSTRAP_REPS = 20_000
SEED = 20_260_730
SCORE_BINS = (
    ("lt_20", float("-inf"), 20.0),
    ("20_to_lt_22", 20.0, 22.0),
    ("22_to_lt_24", 22.0, 24.0),
    ("24_to_lt_26", 24.0, 26.0),
    ("ge_26", 26.0, float("inf")),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ordered_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: (row["game_id"], row["record_index"]))


def endpoints(rows: list[dict], window: int) -> tuple[list[dict], list[dict]]:
    ordered = ordered_rows(rows)
    if 2 * window > len(ordered):
        raise ValueError(f"window {window} exceeds half of panel {len(ordered)}")
    return ordered[:window], ordered[-window:]


def relation_to_resident(row: dict) -> str:
    gap = row["opponent_score"] - row["resident_score"]
    if gap < -0.5:
        return "below_by_gt_0_5"
    if gap > 0.5:
        return "above_by_gt_0_5"
    return "within_0_5"


def score_bin(score: float) -> str:
    for label, lower, upper in SCORE_BINS:
        if lower <= score < upper:
            return label
    raise AssertionError(score)


def normalized_counts(counter: Counter, labels: list[str]) -> dict[str, float]:
    total = sum(counter.values())
    return {label: counter.get(label, 0) / total for label in labels}


def hhi(values: list[object]) -> float:
    counts = Counter(values)
    total = len(values)
    return sum((count / total) ** 2 for count in counts.values())


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize_window(
    rows: list[dict], active_ids: set[int], active_pseudos: set[str]
) -> dict:
    scores = [row["opponent_score"] for row in rows]
    ids = [row["opponent_id"] for row in rows]
    pseudos = [row["opponent_pseudo"] for row in rows]
    identity_hhi = hhi(ids)
    pseudo_hhi = hhi(pseudos)
    relations = Counter(relation_to_resident(row) for row in rows)
    bins = Counter(score_bin(row["opponent_score"]) for row in rows)
    maps = Counter(f"{row['map_width']}x{row['map_height']}" for row in rows)
    seats = Counter(str(row["seat"]) for row in rows)
    margins = [row["margin"] for row in rows]
    wins = [row["win"] for row in rows]
    return {
        "games": len(rows),
        "game_id_min": min(row["game_id"] for row in rows),
        "game_id_max": max(row["game_id"] for row in rows),
        "opponent_score": {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "q10": quantile(scores, 0.10),
            "q25": quantile(scores, 0.25),
            "q75": quantile(scores, 0.75),
            "q90": quantile(scores, 0.90),
        },
        "resident_score_mean": statistics.mean(row["resident_score"] for row in rows),
        "opponent_minus_resident_mean": statistics.mean(
            row["opponent_score"] - row["resident_score"] for row in rows
        ),
        "exact_identity": {
            "unique": len(set(ids)),
            "hhi": identity_hhi,
            "effective_count": 1 / identity_hhi,
            "repeat_game_share": (len(ids) - len(set(ids))) / len(ids),
        },
        "pseudo_lineage": {
            "unique": len(set(pseudos)),
            "hhi": pseudo_hhi,
            "effective_count": 1 / pseudo_hhi,
            "repeat_game_share": (len(pseudos) - len(set(pseudos))) / len(pseudos),
        },
        "current_active": {
            "games": sum(row["opponent_id"] in active_ids for row in rows),
            "game_share": statistics.mean(
                row["opponent_id"] in active_ids for row in rows
            ),
            "unique_identities": len(
                {row["opponent_id"] for row in rows if row["opponent_id"] in active_ids}
            ),
        },
        "current_active_lineage": {
            "games": sum(row["opponent_pseudo"] in active_pseudos for row in rows),
            "game_share": statistics.mean(
                row["opponent_pseudo"] in active_pseudos for row in rows
            ),
            "unique_pseudos": len(
                {
                    row["opponent_pseudo"]
                    for row in rows
                    if row["opponent_pseudo"] in active_pseudos
                }
            ),
        },
        "relative_score_fractions": normalized_counts(
            relations,
            ["below_by_gt_0_5", "within_0_5", "above_by_gt_0_5"],
        ),
        "score_bin_fractions": normalized_counts(
            bins, [label for label, _lower, _upper in SCORE_BINS]
        ),
        "seat_fractions": normalized_counts(seats, ["0", "1"]),
        "map_dimension_fractions": normalized_counts(maps, sorted(maps)),
        "initial_trees": {
            "mean": statistics.mean(row["initial_trees"] for row in rows),
            "median": statistics.median(row["initial_trees"] for row in rows),
        },
        "descriptive_terminal_outcomes": {
            "mean_margin": statistics.mean(margins),
            "mean_win": statistics.mean(wins),
            "mean_turns": statistics.mean(row["turns"] for row in rows),
        },
    }


def contrast(early: list[dict], late: list[dict]) -> dict:
    return {
        "mean_opponent_score": statistics.mean(
            row["opponent_score"] for row in late
        )
        - statistics.mean(row["opponent_score"] for row in early),
        "median_opponent_score": statistics.median(
            row["opponent_score"] for row in late
        )
        - statistics.median(row["opponent_score"] for row in early),
        "mean_opponent_minus_resident_gap": statistics.mean(
            row["opponent_score"] - row["resident_score"] for row in late
        )
        - statistics.mean(
            row["opponent_score"] - row["resident_score"] for row in early
        ),
        "mean_margin_descriptive": statistics.mean(row["margin"] for row in late)
        - statistics.mean(row["margin"] for row in early),
        "mean_win_descriptive": statistics.mean(row["win"] for row in late)
        - statistics.mean(row["win"] for row in early),
    }


def js_divergence(first: dict[str, float], second: dict[str, float]) -> float:
    labels = sorted(set(first) | set(second))
    middle = {label: (first.get(label, 0) + second.get(label, 0)) / 2 for label in labels}

    def kl(left: dict[str, float], right: dict[str, float]) -> float:
        return sum(
            value * math.log2(value / right[label])
            for label, value in left.items()
            if value > 0
        )

    return (kl(first, middle) + kl(second, middle)) / 2


def circular_block_sample(
    values: list[float], block_length: int, rng: random.Random
) -> list[float]:
    sample = []
    while len(sample) < len(values):
        start = rng.randrange(len(values))
        sample.extend(
            values[(start + offset) % len(values)] for offset in range(block_length)
        )
    return sample[: len(values)]


def block_bootstrap_ci(
    early: list[dict],
    late: list[dict],
    *,
    reps: int,
    block_length: int,
    seed: int,
) -> tuple[float, float]:
    early_values = [row["opponent_score"] for row in early]
    late_values = [row["opponent_score"] for row in late]
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        early_sample = circular_block_sample(early_values, block_length, rng)
        late_sample = circular_block_sample(late_values, block_length, rng)
        estimates.append(statistics.mean(late_sample) - statistics.mean(early_sample))
    estimates.sort()
    return quantile(estimates, 0.025), quantile(estimates, 0.975)


def circular_shift_p(rows: list[dict], window: int) -> dict:
    values = [row["opponent_score"] for row in ordered_rows(rows)]
    observed = statistics.mean(values[-window:]) - statistics.mean(values[:window])
    shifts = []
    for offset in range(len(values)):
        rotated = values[offset:] + values[:offset]
        shifts.append(
            statistics.mean(rotated[-window:]) - statistics.mean(rotated[:window])
        )
    exceedances = sum(abs(value) >= abs(observed) for value in shifts)
    return {
        "rotations": len(shifts),
        "observed": observed,
        "two_sided_p": exceedances / len(shifts),
        "null_min": min(shifts),
        "null_max": max(shifts),
    }


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


def trend_summary(rows: list[dict]) -> dict:
    ordered = ordered_rows(rows)
    x = [index / (len(ordered) - 1) for index in range(len(ordered))]
    y = [row["opponent_score"] for row in ordered]
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)
    slope = sum(
        (xvalue - x_mean) * (yvalue - y_mean)
        for xvalue, yvalue in zip(x, y)
    ) / sum((xvalue - x_mean) ** 2 for xvalue in x)
    return {
        "ols_change_over_full_normalized_ordinal": slope,
        "spearman_rho": pearson(average_ranks(x), average_ranks(y)),
    }


def same_sign(value: float | None, reference: float) -> bool:
    if value is None or value == 0 or reference == 0:
        return False
    return (value > 0) == (reference > 0)


def opponent_table(
    rows: list[dict],
    early: list[dict],
    late: list[dict],
    leaderboard: dict[int, dict],
) -> list[dict]:
    early_counts = Counter(row["opponent_id"] for row in early)
    late_counts = Counter(row["opponent_id"] for row in late)
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["opponent_id"]].append(row)
    table = []
    for opponent_id, subset in sorted(grouped.items()):
        current = leaderboard.get(opponent_id)
        table.append(
            {
                "opponent_id": opponent_id,
                "pseudos": "|".join(sorted({row["opponent_pseudo"] for row in subset})),
                "games_full": len(subset),
                "games_early_60": early_counts[opponent_id],
                "games_late_60": late_counts[opponent_id],
                "first_game_id": min(row["game_id"] for row in subset),
                "last_game_id": max(row["game_id"] for row in subset),
                "mean_contemporaneous_score": statistics.mean(
                    row["opponent_score"] for row in subset
                ),
                "current_active": current is not None,
                "current_rank": current["rank"] if current else None,
                "current_score": current["score"] if current else None,
            }
        )
    return table


def endpoint_sensitivity(
    rows: list[dict],
    window: int,
    active_ids: set[int],
    active_pseudos: set[str],
) -> dict:
    early, late = endpoints(rows, window)
    return {
        "window": window,
        "early": summarize_window(early, active_ids, active_pseudos),
        "late": summarize_window(late, active_ids, active_pseudos),
        "contrast": contrast(early, late),
    }


def seat_sensitivities(early: list[dict], late: list[dict]) -> dict:
    result = {}
    for seat in (0, 1):
        early_seat = [row for row in early if row["seat"] == seat]
        late_seat = [row for row in late if row["seat"] == seat]
        result[str(seat)] = {
            "early_games": len(early_seat),
            "late_games": len(late_seat),
            "mean_opponent_score_drift": (
                statistics.mean(row["opponent_score"] for row in late_seat)
                - statistics.mean(row["opponent_score"] for row in early_seat)
                if early_seat and late_seat
                else None
            ),
        }
    return result


def leave_one_identity_out(early: list[dict], late: list[dict]) -> list[dict]:
    results = []
    identities = sorted(
        {row["opponent_id"] for row in early} | {row["opponent_id"] for row in late}
    )
    for opponent_id in identities:
        kept_early = [row for row in early if row["opponent_id"] != opponent_id]
        kept_late = [row for row in late if row["opponent_id"] != opponent_id]
        results.append(
            {
                "omitted_opponent_id": opponent_id,
                "early_games": len(kept_early),
                "late_games": len(kept_late),
                "mean_opponent_score_drift": statistics.mean(
                    row["opponent_score"] for row in kept_late
                )
                - statistics.mean(row["opponent_score"] for row in kept_early),
            }
        )
    return results


def build_result(
    rows: list[dict],
    source: dict,
    leaderboard: dict[int, dict],
    *,
    bootstrap_reps: int,
    seed: int,
) -> dict:
    rows = ordered_rows(rows)
    active_ids = set(leaderboard)
    active_pseudos = {
        str(row["pseudo"]) for row in leaderboard.values() if row["pseudo"] is not None
    }
    early, late = endpoints(rows, PRIMARY_WINDOW)
    early_summary = summarize_window(early, active_ids, active_pseudos)
    late_summary = summarize_window(late, active_ids, active_pseudos)
    primary = contrast(early, late)
    ci = block_bootstrap_ci(
        early,
        late,
        reps=bootstrap_reps,
        block_length=BLOCK_LENGTH,
        seed=seed,
    )
    temporal_null = circular_shift_p(rows, PRIMARY_WINDOW)
    primary["block_bootstrap_ci95"] = list(ci)
    primary["circular_shift_two_sided_p"] = temporal_null["two_sided_p"]
    early_ids = {row["opponent_id"] for row in early}
    late_new_games = [row for row in late if row["opponent_id"] not in early_ids]
    early_pseudos = {row["opponent_pseudo"] for row in early}
    late_new_pseudo_games = [
        row for row in late if row["opponent_pseudo"] not in early_pseudos
    ]
    score_js = js_divergence(
        early_summary["score_bin_fractions"], late_summary["score_bin_fractions"]
    )
    window_sensitivities = {
        str(window): endpoint_sensitivity(rows, window, active_ids, active_pseudos)
        for window in SENSITIVITY_WINDOWS
    }
    active_early = [row for row in early if row["opponent_id"] in active_ids]
    active_late = [row for row in late if row["opponent_id"] in active_ids]
    seat_sensitivity = seat_sensitivities(early, late)
    leave_one_out = leave_one_identity_out(early, late)
    midpoint = len(rows) // 2
    first_half = rows[:midpoint]
    second_half = rows[midpoint:]
    support_gates = {
        "source_integrity": bool(source["hash_check"])
        and all(source["count_checks"].values())
        and source["leaderboard_hash_check"],
        "resident_panel_241": len(rows) == 241,
        "endpoint_windows_60_each": len(early) == 60 and len(late) == 60,
    }
    support = all(support_gates.values())
    drift = primary["mean_opponent_score"]
    window_drifts = [
        window_sensitivities[str(window)]["contrast"]["mean_opponent_score"]
        for window in SENSITIVITY_WINDOWS
    ]
    seat_drifts = [
        seat_sensitivity[str(seat)]["mean_opponent_score_drift"] for seat in (0, 1)
    ]
    actionability_gates = {
        "source_and_endpoint_support": support,
        "absolute_mean_drift_at_least_0_50": abs(drift) >= 0.50,
        "block_bootstrap_ci_excludes_zero": ci[0] > 0 or ci[1] < 0,
        "circular_shift_p_at_most_0_05": temporal_null["two_sided_p"] <= 0.05,
        "median_same_sign_and_at_least_0_25": same_sign(
            primary["median_opponent_score"], drift
        )
        and abs(primary["median_opponent_score"]) >= 0.25,
        "opponent_minus_resident_gap_same_sign": same_sign(
            primary["mean_opponent_minus_resident_gap"], drift
        ),
        "window_40_and_80_same_sign_at_least_0_25": all(
            same_sign(value, drift) and abs(value) >= 0.25
            for value in window_drifts
        ),
        "both_seats_same_sign": all(
            same_sign(value, drift) for value in seat_drifts
        ),
        "leave_one_exact_opponent_out_same_sign": all(
            same_sign(row["mean_opponent_score_drift"], drift)
            for row in leave_one_out
        ),
    }
    material = all(actionability_gates.values())
    verdict = (
        "UNIDENTIFIABLE"
        if not support
        else "MATERIAL_STRONGER_OPPONENT_DRIFT"
        if material and drift > 0
        else "MATERIAL_WEAKER_OPPONENT_DRIFT"
        if material and drift < 0
        else "NO_MATERIAL_MATCHMAKING_DRIFT"
    )
    return {
        "verdict": verdict,
        "source": source,
        "protocol": {
            "primary_window": PRIMARY_WINDOW,
            "sensitivity_windows": list(SENSITIVITY_WINDOWS),
            "block_length": BLOCK_LENGTH,
            "bootstrap_reps": bootstrap_reps,
            "seed": seed,
            "chronology": "game_id_then_record_index",
            "primary_estimand": "late_minus_early_mean_opponent_arena_score",
        },
        "full_panel": summarize_window(rows, active_ids, active_pseudos),
        "early_60": early_summary,
        "late_60": late_summary,
        "primary_contrast": primary,
        "composition_shift": {
            "score_bin_js_divergence_bits": score_js,
            "late_new_identity_games": len(late_new_games),
            "late_new_identity_game_share": len(late_new_games) / len(late),
            "late_new_unique_identities": len(
                {row["opponent_id"] for row in late_new_games}
            ),
            "late_new_pseudo_games": len(late_new_pseudo_games),
            "late_new_pseudo_game_share": len(late_new_pseudo_games) / len(late),
            "late_new_unique_pseudos": len(
                {row["opponent_pseudo"] for row in late_new_pseudo_games}
            ),
            "early_unique_identities": len(early_ids),
            "late_unique_identities": len(
                {row["opponent_id"] for row in late}
            ),
            "early_unique_pseudos": len(early_pseudos),
            "late_unique_pseudos": len(
                {row["opponent_pseudo"] for row in late}
            ),
        },
        "temporal_null": temporal_null,
        "trend": trend_summary(rows),
        "sensitivities": {
            "windows": window_sensitivities,
            "active_current_only": {
                "early_games": len(active_early),
                "late_games": len(active_late),
                "mean_opponent_score_drift": statistics.mean(
                    row["opponent_score"] for row in active_late
                )
                - statistics.mean(row["opponent_score"] for row in active_early),
            },
            "seats": seat_sensitivity,
            "leave_one_exact_opponent_out": leave_one_out,
            "first_half_second_half": {
                "first_games": len(first_half),
                "second_games": len(second_half),
                "mean_opponent_score_drift": statistics.mean(
                    row["opponent_score"] for row in second_half
                )
                - statistics.mean(row["opponent_score"] for row in first_half),
            },
        },
        "support_gates": support_gates,
        "material_drift_gates": actionability_gates,
        "failed_material_drift_gates": [
            key for key, passed in actionability_gates.items() if not passed
        ],
        "opponents": opponent_table(rows, early, late, leaderboard),
    }


def report_text(result: dict) -> str:
    contrast_row = result["primary_contrast"]
    composition = result["composition_shift"]
    early = result["early_60"]
    late = result["late_60"]
    failed = ", ".join(result["failed_material_drift_gates"]) or "none"
    return f"""# M4 — resident matchmaking composition

- Verdict: **{result['verdict']}**
- Oldest/newest endpoint size: 60 / 60
- Mean opponent score: {early['opponent_score']['mean']:.3f} → {late['opponent_score']['mean']:.3f}
- Late-minus-early mean drift: {contrast_row['mean_opponent_score']:+.3f}
- Moving-block 95% CI: [{contrast_row['block_bootstrap_ci95'][0]:+.3f}, {contrast_row['block_bootstrap_ci95'][1]:+.3f}]
- Exact circular-shift p: {contrast_row['circular_shift_two_sided_p']:.6f}
- Median drift: {contrast_row['median_opponent_score']:+.3f}
- Opponent-minus-resident gap drift: {contrast_row['mean_opponent_minus_resident_gap']:+.3f}

## Composition

- Exact identities: {early['exact_identity']['unique']} → {late['exact_identity']['unique']}
- Effective exact identities: {early['exact_identity']['effective_count']:.2f} → {late['exact_identity']['effective_count']:.2f}
- Late games from identities absent in the early endpoint: {composition['late_new_identity_games']}/60
- Late games from pseudonyms absent in the early endpoint: {composition['late_new_pseudo_games']}/60
- Score-bin Jensen–Shannon divergence: {composition['score_bin_js_divergence_bits']:.4f} bits
- Current-active exact-ID game share: {early['current_active']['game_share']:.3f} → {late['current_active']['game_share']:.3f}
- Current-active pseudonym game share: {early['current_active_lineage']['game_share']:.3f} → {late['current_active_lineage']['game_share']:.3f}

## Failed material-drift gates

{failed}

Terminal margin/win changes are descriptive only and do not enter this verdict. Even a
material result would update longitudinal interpretation and surveillance, not authorize
resident, policy, simulation, or Arena changes.
"""


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n"
    )
    (output_dir / "report.md").write_text(report_text(result))
    fields = [
        "opponent_id",
        "pseudos",
        "games_full",
        "games_early_60",
        "games_late_60",
        "first_game_id",
        "last_game_id",
        "mean_contemporaneous_score",
        "current_active",
        "current_rank",
        "current_score",
    ]
    with (output_dir / "opponents.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["opponents"])


def synthetic_rows() -> list[dict]:
    rows = []
    for index in range(12):
        rows.append(
            {
                "record_index": index + 1,
                "game_id": 100 + index,
                "seat": index % 2,
                "resident_score": 22.0,
                "opponent_score": 20.0 + index,
                "opponent_id": 10 + index % 4,
                "opponent_pseudo": f"p{index % 3}",
                "map_width": 12,
                "map_height": 12,
                "initial_trees": 20 + index % 2,
                "margin": float(index - 6),
                "win": 1.0 if index >= 6 else 0.0,
                "resident_final_score": 100.0,
                "opponent_final_score": 100.0,
                "resident_final_fruit": 0.0,
                "resident_final_wood_points": 0.0,
                "opponent_final_fruit": 0.0,
                "opponent_final_wood_points": 0.0,
                "turns": 200,
            }
        )
    return rows


def self_test() -> None:
    rows = synthetic_rows()
    early, late = endpoints(rows, 3)
    assert [row["game_id"] for row in early] == [100, 101, 102]
    assert [row["game_id"] for row in late] == [109, 110, 111]
    assert contrast(early, late)["mean_opponent_score"] == 9.0
    first = block_bootstrap_ci(
        early, late, reps=200, block_length=2, seed=7
    )
    second = block_bootstrap_ci(
        early, late, reps=200, block_length=2, seed=7
    )
    assert first == second
    shift = circular_shift_p(rows, 3)
    assert shift["rotations"] == 12 and 0 < shift["two_sided_p"] <= 1
    same = {label: 0.2 for label, _lower, _upper in SCORE_BINS}
    assert js_divergence(same, same) == 0.0
    assert same_sign(1.0, 2.0) and not same_sign(-1.0, 2.0)
    print("self-test: ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--leaderboard", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    rows, source = load_game_source(args.games)
    leaderboard_hash = sha256_file(args.leaderboard)
    if leaderboard_hash != EXPECTED_LEADERBOARD_HASH:
        raise ValueError(
            "leaderboard hash mismatch: "
            f"expected {EXPECTED_LEADERBOARD_HASH}, observed {leaderboard_hash}"
        )
    leaderboard = load_leaderboard(args.leaderboard)
    source.update(
        {
            "leaderboard_path": str(args.leaderboard),
            "expected_leaderboard_hash": EXPECTED_LEADERBOARD_HASH,
            "observed_leaderboard_hash": leaderboard_hash,
            "leaderboard_hash_check": True,
        }
    )
    result = build_result(
        rows,
        source,
        leaderboard,
        bootstrap_reps=args.bootstrap_reps,
        seed=args.seed,
    )
    write_outputs(result, args.output_dir)
    drift = result["primary_contrast"]["mean_opponent_score"]
    print(
        f"{result['verdict']}: opponent-score drift={drift:+.3f}, "
        f"early/late={PRIMARY_WINDOW}/{PRIMARY_WINDOW}"
    )
    return 2 if result["verdict"] == "UNIDENTIFIABLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
