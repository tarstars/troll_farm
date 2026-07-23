#!/usr/bin/env python3
"""Analyze the frozen D159 exact-resident replay refresh."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.recent_resident_field_census import summarize


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/analysis/live-agent-6553250"
DEFAULT_RAW = BASE / "d159a-current-resident-all-finished-effect-refresh-raw.json"
DEFAULT_HISTORY = BASE / "d23-current-resident-field-refresh-2026-07-20.json"
DEFAULT_OUTPUT = BASE / "d159a-current-resident-all-finished-effect-refresh-result.json"
RESIDENT_SOURCE = (
    ROOT
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
EXPECTED_AGENT = 6561795
EXPECTED_SOURCE_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
)
EXPECTED_HISTORY_SHA256 = (
    "0567f474d44270cb97087a2254c3506f55f49ae122694d82d2fb1dd863cc5075"
)
BOOTSTRAP_SEED = 15901
BOOTSTRAP_REPLICATES = 10_000
CUTS = (50, 75, 100, 150, 200, 225, 300)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def mean(values: list[int | float]) -> float | None:
    return statistics.mean(values) if values else None


def field(row: dict, *keys: str) -> int | float | None:
    value = row
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value if isinstance(value, (int, float)) else None


def field_mean(rows: list[dict], *keys: str) -> float | None:
    values = [value for row in rows if (value := field(row, *keys)) is not None]
    return mean(values)


def bootstrap_mean_ci(
    rows: list[dict], *, seed: int = BOOTSTRAP_SEED, replicates: int = BOOTSTRAP_REPLICATES
) -> list[float | None]:
    if not rows:
        return [None, None]
    margins = [float(row["margin"]) for row in sorted(rows, key=lambda row: row["game_id"])]
    generator = random.Random(seed)
    count = len(margins)
    samples = [
        sum(margins[generator.randrange(count)] for _ in range(count)) / count
        for _ in range(replicates)
    ]
    return [quantile(samples, 0.025), quantile(samples, 0.975)]


def tail_report(rows: list[dict]) -> dict:
    losses = [row for row in rows if row["margin"] < 0]
    catastrophic = [row for row in rows if row["margin"] <= -100]
    noncatastrophic = [row for row in rows if row["margin"] > -100]
    negative_mass = sum(-row["margin"] for row in losses)
    catastrophic_mass = sum(-row["margin"] for row in catastrophic)
    catastrophic_wood = field_mean(catastrophic, "final", "opponent", "wood")
    noncatastrophic_wood = field_mean(noncatastrophic, "final", "opponent", "wood")
    wood_gap = (
        catastrophic_wood - noncatastrophic_wood
        if catastrophic_wood is not None and noncatastrophic_wood is not None
        else None
    )
    conditions = {
        "frequency_at_least_10pct": bool(
            rows and len(catastrophic) / len(rows) >= 0.10
        ),
        "negative_mass_share_at_least_50pct": bool(
            negative_mass and catastrophic_mass / negative_mass >= 0.50
        ),
        "at_least_3_opponents": len({row["opponent"] for row in catastrophic}) >= 3,
        "opponent_wood_gap_at_least_20": bool(wood_gap is not None and wood_gap >= 20),
    }
    return {
        "definition": "terminal margin <= -100",
        "games": len(catastrophic),
        "frequency": len(catastrophic) / len(rows) if rows else 0.0,
        "negative_margin_mass": negative_mass,
        "catastrophic_negative_margin_mass": catastrophic_mass,
        "negative_margin_mass_share": (
            catastrophic_mass / negative_mass if negative_mass else 0.0
        ),
        "distinct_opponents": len({row["opponent"] for row in catastrophic}),
        "mean_opponent_final_wood": catastrophic_wood,
        "opponent_wood_gap_vs_noncatastrophic": wood_gap,
        "mean_opponent_crop_wood": field_mean(
            catastrophic, "opponent_crop_summary", "opponent_wood_collected"
        ),
        "mean_our_crop_interception_rate": field_mean(
            catastrophic, "opponent_crop_summary", "our_interception_rate"
        ),
        "replication_conditions": conditions,
        "signature_replicates": all(conditions.values()),
    }


def early_lead_reversal(rows: list[dict], cut: int = 100) -> dict:
    key = str(cut)
    valid = [
        row
        for row in rows
        if field(row, "timeline", key, "my", "score") is not None
        and field(row, "timeline", key, "opponent", "score") is not None
    ]
    losses = [row for row in valid if row["margin"] < 0]
    reversals = [
        row
        for row in losses
        if field(row, "timeline", key, "my", "score")
        > field(row, "timeline", key, "opponent", "score")
    ]
    return {
        "definition": f"positive resident score margin at turn {cut}, negative terminal margin",
        "valid_games": len(valid),
        "terminal_losses": len(losses),
        "reversals": len(reversals),
        "share_of_losses": len(reversals) / len(losses) if losses else 0.0,
        "catastrophic_reversals": sum(row["margin"] <= -100 for row in reversals),
        "distinct_opponents": len({row["opponent"] for row in reversals}),
        "mean_terminal_margin": mean([row["margin"] for row in reversals]),
    }


def trajectory_report(rows: list[dict]) -> dict:
    result = {}
    for cut in CUTS:
        key = str(cut)
        valid = [
            row
            for row in rows
            if field(row, "timeline", key, "my", "score") is not None
            and field(row, "timeline", key, "opponent", "score") is not None
        ]
        my_score = field_mean(valid, "timeline", key, "my", "score")
        opponent_score = field_mean(valid, "timeline", key, "opponent", "score")
        result[key] = {
            "games": len(valid),
            "mean_score_margin": (
                my_score - opponent_score
                if my_score is not None and opponent_score is not None
                else None
            ),
            "my_score": my_score,
            "opponent_score": opponent_score,
            "my_wood": field_mean(valid, "timeline", key, "my", "wood"),
            "opponent_wood": field_mean(
                valid, "timeline", key, "opponent", "wood"
            ),
            "my_workers": field_mean(valid, "timeline", key, "my", "workers"),
            "opponent_workers": field_mean(
                valid, "timeline", key, "opponent", "workers"
            ),
            "my_plants": field_mean(
                valid, "timeline", key, "my", "successful_plants"
            ),
            "opponent_plants": field_mean(
                valid, "timeline", key, "opponent", "successful_plants"
            ),
        }
    return result


def cohort_report(rows: list[dict]) -> dict:
    wins = [row for row in rows if row["margin"] > 0]
    ties = [row for row in rows if row["margin"] == 0]
    ordinary_losses = [row for row in rows if -100 < row["margin"] < 0]
    catastrophic = [row for row in rows if row["margin"] <= -100]
    margins = [row["margin"] for row in rows]
    return {
        "games": len(rows),
        "outcomes": {
            "wins": len(wins),
            "ties": len(ties),
            "ordinary_losses": len(ordinary_losses),
            "catastrophic_losses": len(catastrophic),
        },
        "margin": {
            "mean": mean(margins),
            "median": statistics.median(margins) if margins else None,
            "bootstrap_95pct_mean_ci": bootstrap_mean_ci(rows),
            "minimum": min(margins) if margins else None,
            "maximum": max(margins) if margins else None,
        },
        "all": summarize(rows),
        "wins": summarize(wins),
        "ordinary_losses": summarize(ordinary_losses),
        "catastrophic_losses": summarize(catastrophic),
        "catastrophic_tail": tail_report(rows),
        "turn100_early_lead_reversal": early_lead_reversal(rows),
        "trajectory": trajectory_report(rows),
    }


def mechanism_evidence(rows: list[dict]) -> dict:
    wins = [row for row in rows if row["margin"] > 0]
    losses = [row for row in rows if row["margin"] < 0]
    catastrophic = [row for row in rows if row["margin"] <= -100]
    noncatastrophic = [row for row in rows if row["margin"] > -100]

    def gap(left: list[dict], right: list[dict], *keys: str) -> float | None:
        left_mean = field_mean(left, *keys)
        right_mean = field_mean(right, *keys)
        if left_mean is None or right_mean is None:
            return None
        return left_mean - right_mean

    scaled_loss_opponents = [
        row for row in losses if field(row, "final", "opponent", "workers") >= 3
    ]
    return {
        "resident_fixed_two_workers": {
            "games": sum(field(row, "final", "my", "workers") == 2 for row in rows),
            "frequency": (
                sum(field(row, "final", "my", "workers") == 2 for row in rows)
                / len(rows)
                if rows
                else 0.0
            ),
        },
        "scaled_opponents_in_losses": {
            "definition": "terminal opponent workforce >=3",
            "games": len(scaled_loss_opponents),
            "losses": len(losses),
            "frequency": len(scaled_loss_opponents) / len(losses) if losses else 0.0,
            "opponent_worker_gap_loss_vs_win": gap(
                losses, wins, "final", "opponent", "workers"
            ),
        },
        "crop_interaction": {
            "our_interception_gap_loss_vs_win": gap(
                losses,
                wins,
                "opponent_crop_summary",
                "our_interception_rate",
            ),
            "catastrophic_opponent_crop_wood_gap_vs_noncatastrophic": gap(
                catastrophic,
                noncatastrophic,
                "opponent_crop_summary",
                "opponent_wood_collected",
            ),
            "catastrophic_opponent_crop_count_gap_vs_noncatastrophic": gap(
                catastrophic, noncatastrophic, "opponent_crop_summary", "crops"
            ),
        },
        "turn100_early_lead_reversal": early_lead_reversal(rows),
    }


def rank_attack_angles() -> list[dict]:
    """Frozen six-axis scoring applied after the suffix mechanisms are known."""

    axes = (
        "suffix_replication",
        "resident_relative_upside",
        "resident_preserving_testability",
        "field_fidelity",
        "implementation_tractability",
        "tail_safety",
    )
    candidates = [
        {
            "angle": "field_native_bounded_midgame_probe_bank",
            "mechanism": "turn-100 lead reversal into turn-200/225 opponent compounding",
            "scores": [5, 4, 5, 5, 3, 5],
            "history_constraint": (
                "must use finite resident-anchored probes; permanent farm D32 already failed"
            ),
            "next_test": (
                "small common-map TestSession A/B bank of bounded integrated scale/renew/intercept "
                "responses, with exact resident before/after each probe"
            ),
        },
        {
            "angle": "resident_anchored_integrated_scale_response",
            "mechanism": "fixed two-worker resident versus scaled losing opponents",
            "scores": [5, 5, 4, 4, 3, 4],
            "history_constraint": (
                "isolated TRAIN and permanent farm are closed; funding, TRAIN, renewable supply, "
                "roles, and termination must be one option"
            ),
            "next_test": "terminal paired value of one finite coherent response over exact resident",
        },
        {
            "angle": "resident_fallback_recurrent_macro_controller",
            "mechanism": "long-horizon reversal requires repeated state-conditioned choices",
            "scores": [5, 5, 5, 3, 2, 4],
            "history_constraint": (
                "rebuild q6 around exact resident fallback; D158's D40 baseline is invalid"
            ),
            "next_test": "mechanics and same-panel resident-dominance pilot before PPO scaling",
        },
        {
            "angle": "integrated_orchard_interception_response",
            "mechanism": "losses contact fewer reachable opponent crops and yield crop wood",
            "scores": [5, 4, 4, 4, 3, 3],
            "history_constraint": (
                "crop-only priority patches are closed; denial must preserve own scale and resident "
                "suppression"
            ),
            "next_test": "bounded joint scale-plus-interception option, never a scalar retune",
        },
        {
            "angle": "tail_triggered_safe_policy_portfolio",
            "mechanism": "catastrophes dominate downside but early observable precision is limited",
            "scores": [5, 4, 5, 4, 3, 2],
            "history_constraint": (
                "D23/D29 field selectors lacked stable activation; prove option value before fitting "
                "a trigger"
            ),
            "next_test": "defer selector training until a field-positive response option exists",
        },
        {
            "angle": "field_native_counterfactual_value_dataset",
            "mechanism": "generated-map value models transfer poorly to official terrain",
            "scores": [4, 4, 5, 5, 2, 5],
            "history_constraint": (
                "D30 measured domain shift and D31 replay continuation lacked causal fidelity"
            ),
            "next_test": "collect prospective common-map A/B labels rather than replay pseudo-labels",
        },
        {
            "angle": "opponent_archetype_portfolio",
            "mechanism": "same opponents can produce both wins and catastrophes",
            "scores": [3, 3, 5, 5, 3, 3],
            "history_constraint": "catastrophes span twelve suffix opponents; names are not a robust state",
            "next_test": "use behavior/state features only after option value is established",
        },
        {
            "angle": "opening_or_first_move_selector",
            "mechanism": "opening geometry may modulate risk",
            "scores": [1, 2, 5, 4, 4, 4],
            "history_constraint": (
                "most suffix losses lead at turn 100 and prior turn-one Monte Carlo found no robust "
                "activation"
            ),
            "next_test": "do not reopen while the repeated reversal begins in midgame",
        },
        {
            "angle": "online_single_move_monte_carlo",
            "mechanism": "local tactical mistakes may accumulate",
            "scores": [2, 2, 5, 3, 2, 4],
            "history_constraint": (
                "exact-resident prospective bank-only gain was +0.508 at 92.85 ms p95"
            ),
            "next_test": "closed unless a new batched evaluator changes the value/latency frontier",
        },
        {
            "angle": "unanchored_end_to_end_ppo",
            "mechanism": "a complete controller could in principle learn the whole economy",
            "scores": [3, 5, 1, 3, 2, 1],
            "history_constraint": (
                "prior PPO eroded production and D158 showed nonresident baseline gates are invalid"
            ),
            "next_test": "do not resume without exact-resident initialization/fallback and gates",
        },
    ]
    result = []
    for candidate in candidates:
        scores = dict(zip(axes, candidate.pop("scores"), strict=True))
        result.append({**candidate, "scores": scores, "total": sum(scores.values())})
    result.sort(
        key=lambda row: (
            row["total"],
            row["scores"]["suffix_replication"],
            row["scores"]["resident_preserving_testability"],
        ),
        reverse=True,
    )
    for rank, row in enumerate(result, 1):
        row["rank"] = rank
    return result


def telemetry_complete(row: dict) -> bool:
    required = (
        field(row, "scores", "my"),
        field(row, "scores", "opponent"),
        field(row, "final", "my", "score"),
        field(row, "final", "opponent", "score"),
        field(row, "final", "my", "workers"),
        field(row, "final", "opponent", "workers"),
        field(row, "opponent_crop_summary", "crops"),
        field(row, "crop_attribution_quality", "decoded_turns"),
    )
    return all(value is not None for value in required) and all(
        row["timeline"].get(str(cut)) is not None for cut in CUTS
    )


def analyze(raw: dict, history: dict, raw_path: Path, history_path: Path) -> dict:
    raw_rows = raw.get("rows", [])
    history_rows = history.get("rows", [])
    history_ids = {row["game_id"] for row in history_rows}
    exact_rows = [row for row in raw_rows if row.get("agent_id") == EXPECTED_AGENT]
    historical = [row for row in exact_rows if row["game_id"] in history_ids]
    suffix = [row for row in exact_rows if row["game_id"] not in history_ids]
    retained_ids = [row["game_id"] for row in exact_rows]
    raw_ids = [row["game_id"] for row in raw_rows]
    history_counts = {
        game_id: sum(row["game_id"] == game_id for row in exact_rows)
        for game_id in history_ids
    }
    unknown = [
        row["game_id"]
        for row in exact_rows
        if field(row, "crop_attribution_quality", "unknown_diff_updates") != 0
    ]
    score_mismatches = [
        row["game_id"]
        for row in exact_rows
        if field(row, "scores", "my") != field(row, "final", "my", "score")
        or field(row, "scores", "opponent")
        != field(row, "final", "opponent", "score")
    ]
    gates = {
        "leaderboard_exact_resident": raw.get("arena_snapshot", {}).get(
            "resident_agent_id"
        )
        == EXPECTED_AGENT,
        "at_least_160_exact_resident_games": len(exact_rows) >= 160,
        "at_least_80_suffix_games": len(suffix) >= 80,
        "all_80_historical_ids_once": len(history_ids) == 80
        and all(count == 1 for count in history_counts.values()),
        "no_duplicate_retained_ids": len(retained_ids) == len(set(retained_ids)),
        "no_fetch_failures": not raw.get("arena_snapshot", {}).get("fetch_failures"),
        "no_identity_mismatches": len(exact_rows) == len(raw_rows),
        "zero_unknown_diff_updates": not unknown,
        "complete_terminal_effect_crop_telemetry": all(
            telemetry_complete(row) for row in exact_rows
        ),
        "source_hash_exact": sha256(RESIDENT_SOURCE) == EXPECTED_SOURCE_SHA256,
        "historical_artifact_hash_exact": sha256(history_path)
        == EXPECTED_HISTORY_SHA256,
    }
    cohorts = {
        "historical80": cohort_report(historical),
        "suffix": cohort_report(suffix),
        "all_current": cohort_report(exact_rows),
    }
    attack_angles = rank_attack_angles()
    integrity_pass = all(gates.values())
    suffix_replicates = cohorts["suffix"]["catastrophic_tail"][
        "signature_replicates"
    ]
    return {
        "schema": "troll-farm-d159a-current-resident-refresh-result-v1",
        "identity": {
            "resident_agent_id": EXPECTED_AGENT,
            "resident_submission_id": 41015603,
            "resident_source_sha256": sha256(RESIDENT_SOURCE),
            "historical_artifact_sha256": sha256(history_path),
            "raw_artifact_sha256": sha256(raw_path),
        },
        "platform_snapshot": raw.get("arena_snapshot", {}),
        "partition": {
            "raw_rows": len(raw_rows),
            "raw_unique_ids": len(set(raw_ids)),
            "exact_resident_rows": len(exact_rows),
            "historical80_rows": len(historical),
            "suffix_rows": len(suffix),
            "identity_mismatch_ids": [
                row.get("game_id")
                for row in raw_rows
                if row.get("agent_id") != EXPECTED_AGENT
            ],
            "missing_historical_ids": sorted(
                game_id for game_id, count in history_counts.items() if count == 0
            ),
            "duplicate_retained_ids": sorted(
                game_id for game_id in set(retained_ids) if retained_ids.count(game_id) > 1
            ),
            "unknown_diff_game_ids": unknown,
            "score_mismatch_game_ids": score_mismatches,
        },
        "integrity": {"gates": gates, "pass": integrity_pass},
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "replicates": BOOTSTRAP_REPLICATES,
            "unit": "game ID",
        },
        "cohorts": cohorts,
        "suffix_mechanism_evidence": mechanism_evidence(suffix),
        "attack_angle_scoring": {
            "scale": "1 weak to 5 strong",
            "aggregation": (
                "unweighted total, then suffix replication, then resident-preserving testability"
            ),
            "angles": attack_angles,
        },
        "decision": {
            "decision_bearing": integrity_pass,
            "anti_compounding_signature_replicates_in_suffix": suffix_replicates,
            "selected_next_direction": (
                attack_angles[0]["angle"] if integrity_pass else None
            ),
            "construct_candidate": False,
            "submit": False,
            "next_experiment": (
                "freeze a small field-native common-map A/B bank of finite integrated midgame "
                "responses, each exact-resident anchored, before training another selector"
                if integrity_pass
                else "repair the failed D159 integrity gate before prioritizing implementation"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text())
    history = json.loads(args.history.read_text())
    payload = analyze(raw, history, args.raw, args.history)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    suffix = payload["cohorts"]["suffix"]
    tail = suffix["catastrophic_tail"]
    reversal = suffix["turn100_early_lead_reversal"]
    print(
        f"integrity={payload['integrity']['pass']} suffix={suffix['games']} "
        f"margin={suffix['margin']['mean']:+.3f} "
        f"catastrophes={tail['games']}/{suffix['games']} "
        f"tail_mass={tail['negative_margin_mass_share']:.1%} "
        f"replicates={tail['signature_replicates']}"
    )
    print(
        f"turn100 reversals={reversal['reversals']}/{reversal['terminal_losses']} losses; "
        f"next={payload['decision']['selected_next_direction']}"
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
