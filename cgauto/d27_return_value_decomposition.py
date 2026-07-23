#!/usr/bin/env python3
"""Decompose D26's turn-150 return using shared D24/D26 trajectories."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import statistics


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
FIELDS = ("margin", "my_score", "opponent_score", "my_wood", "opponent_wood")
ROOT_FIELDS = (
    "reached_cut",
    "root_turn",
    "root_my_score",
    "root_opponent_score",
    "root_my_wood",
    "root_opponent_wood",
    "root_my_workers",
    "root_opponent_workers",
    "root_plants",
)
CONTROL_FIELDS = (
    *ROOT_FIELDS,
    "final_turn",
    *FIELDS,
    "my_workers",
    "opponent_workers",
    "max_my_workers",
    "command_hash",
)


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


def key(row: dict) -> tuple[int, int, str]:
    return int(row["seed"]), int(row["seat"]), row["opponent"]


def index_rows(paths: list[Path], source: str) -> dict[tuple, dict[str, dict]]:
    indexed: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for path in paths:
        with path.open(newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                if source == "d24" and int(row["decision_turn"]) != 75:
                    continue
                wanted = (
                    {"resident", "ownership2"}
                    if source == "d24"
                    else {"resident", "pulse150"}
                )
                if row["option"] not in wanted:
                    continue
                row_key = key(row)
                if row["option"] in indexed[row_key]:
                    raise ValueError(f"duplicate {source} row: {row_key} / {row['option']}")
                indexed[row_key][row["option"]] = row
    return dict(indexed)


def integer(row: dict, field: str) -> int:
    return int(row[field])


def seed_cluster(rows: list[dict], field: str) -> list[float]:
    clustered: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        clustered[row["seed"]].append(row[field])
    return [statistics.mean(values) for _, values in sorted(clustered.items())]


def sign(value: int) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def policy_tail(values: list[int]) -> dict:
    negative = sum(max(-value, 0) for value in values)
    return {
        "margin": robust_summary(values),
        "catastrophic_cells": sum(value <= -100 for value in values),
        "catastrophic_frequency": sum(value <= -100 for value in values) / len(values),
        "negative_margin_mass": negative,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d24", type=Path, action="append", required=True)
    parser.add_argument("--d26", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed-start", type=int, default=50000)
    parser.add_argument("--seed-count", type=int, default=120)
    args = parser.parse_args()

    d24 = index_rows(args.d24, "d24")
    d26 = index_rows([args.d26], "d26")
    expected_keys = {
        (seed, seat, opponent)
        for seed in range(args.seed_start, args.seed_start + args.seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    required_d24 = {"resident", "ownership2"}
    required_d26 = {"resident", "pulse150"}
    bad_d24 = {str(k): sorted(set(v) ^ required_d24) for k, v in d24.items() if set(v) != required_d24}
    bad_d26 = {str(k): sorted(set(v) ^ required_d26) for k, v in d26.items() if set(v) != required_d26}

    control_mismatches = []
    root_mismatches = []
    rows = []
    for row_key in sorted(expected_keys & set(d24) & set(d26)):
        resident24 = d24[row_key]["resident"]
        farm = d24[row_key]["ownership2"]
        resident26 = d26[row_key]["resident"]
        pulse = d26[row_key]["pulse150"]
        for field in CONTROL_FIELDS:
            if integer(resident24, field) != integer(resident26, field):
                control_mismatches.append(
                    {
                        "key": row_key,
                        "field": field,
                        "d24": integer(resident24, field),
                        "d26": integer(resident26, field),
                    }
                )
        for field in ROOT_FIELDS:
            values = [integer(row, field) for row in (resident24, farm, resident26, pulse)]
            if len(set(values)) != 1:
                root_mismatches.append({"key": row_key, "field": field, "values": values})

        result = {"seed": row_key[0], "seat": row_key[1], "opponent": row_key[2]}
        for field in FIELDS:
            resident_value = integer(resident24, field)
            farm_value = integer(farm, field)
            pulse_value = integer(pulse, field)
            result[f"resident_{field}"] = resident_value
            result[f"farm_{field}"] = farm_value
            result[f"pulse_{field}"] = pulse_value
            result[f"farm_path_{field}"] = farm_value - resident_value
            result[f"return_effect_{field}"] = pulse_value - farm_value
            result[f"pulse_value_{field}"] = pulse_value - resident_value
            result[f"identity_residual_{field}"] = (
                result[f"farm_path_{field}"]
                + result[f"return_effect_{field}"]
                - result[f"pulse_value_{field}"]
            )
        rows.append(result)

    integrity = {
        "expected_cells": len(expected_keys),
        "matched_cells": len(rows),
        "d24_keys": len(d24),
        "d26_keys": len(d26),
        "missing_d24_keys": len(expected_keys - set(d24)),
        "missing_d26_keys": len(expected_keys - set(d26)),
        "unexpected_d24_keys": len(set(d24) - expected_keys),
        "unexpected_d26_keys": len(set(d26) - expected_keys),
        "bad_d24_branch_sets": bad_d24,
        "bad_d26_branch_sets": bad_d26,
        "control_mismatch_count": len(control_mismatches),
        "control_mismatches": control_mismatches[:50],
        "root_mismatch_count": len(root_mismatches),
        "root_mismatches": root_mismatches[:50],
        "identity_max_abs_residual": {
            field: max(abs(row[f"identity_residual_{field}"]) for row in rows)
            for field in FIELDS
        },
        "shared_turn150_state": "by deterministic source construction; D24 and D26 use identical ownership2/opponent continuations through turn 149",
    }
    integrity["passed"] = (
        len(rows) == len(expected_keys)
        and set(d24) == expected_keys
        and set(d26) == expected_keys
        and not bad_d24
        and not bad_d26
        and not control_mismatches
        and not root_mismatches
        and all(value == 0 for value in integrity["identity_max_abs_residual"].values())
    )

    effects = {}
    for field in FIELDS:
        effects[field] = {
            component: robust_summary(seed_cluster(rows, f"{component}_{field}"))
            for component in ("farm_path", "return_effect", "pulse_value")
        }
    opponent_means = {
        opponent: {
            component: statistics.mean(
                row[f"{component}_margin"]
                for row in rows
                if row["opponent"] == opponent
            )
            for component in ("farm_path", "return_effect", "pulse_value")
        }
        for opponent in OPPONENTS
    }
    catastrophic = [row for row in rows if row["resident_margin"] <= -100]
    catastrophic_effects = {
        component: robust_summary(row[f"{component}_margin"] for row in catastrophic)
        for component in ("farm_path", "return_effect", "pulse_value")
    }
    quadrants = Counter(
        f"farm_{sign(row['farm_path_margin'])}__return_{sign(row['return_effect_margin'])}"
        for row in rows
    )
    tails = {
        policy: policy_tail([row[f"{policy}_margin"] for row in rows])
        for policy in ("resident", "farm", "pulse")
    }
    tails["farm_to_resident_negative_mass_ratio"] = (
        tails["farm"]["negative_margin_mass"] / tails["resident"]["negative_margin_mass"]
    )
    tails["pulse_to_resident_negative_mass_ratio"] = (
        tails["pulse"]["negative_margin_mass"] / tails["resident"]["negative_margin_mass"]
    )

    return_margin = effects["margin"]["return_effect"]
    if return_margin["mean"] <= -10 and return_margin["ci95_normal"][1] < 0:
        classification = "cold_reentry_primary_failure"
        next_priority = "implementable_handoff_state_mechanisms"
    elif return_margin["mean"] >= 5 and return_margin["ci95_normal"][0] > 0:
        classification = "cold_reentry_beneficial_map_state_dominant"
        next_priority = "private_planting_geometry"
    else:
        classification = "mixed"
        farm_worsens_tail = (
            tails["farm"]["catastrophic_frequency"]
            > tails["resident"]["catastrophic_frequency"]
            or tails["farm"]["negative_margin_mass"]
            > tails["resident"]["negative_margin_mass"]
        )
        next_priority = (
            "private_planting_geometry" if farm_worsens_tail else "implementable_handoff_state_mechanisms"
        )

    payload = {
        "schema": 1,
        "scope": "read-only paired decomposition on already-consumed D24/D26 common trajectories; no candidate or Arena authorization",
        "sources": {"d24": [str(path) for path in args.d24], "d26": str(args.d26)},
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "integrity": integrity,
        "effects_seed_clustered": effects,
        "opponent_mean_margin_components": opponent_means,
        "resident_catastrophic_cells": len(catastrophic),
        "resident_catastrophic_cell_effects": catastrophic_effects,
        "cell_sign_quadrants": dict(sorted(quadrants.items())),
        "terminal_tails": tails,
        "decision": {
            "classification": classification if integrity["passed"] else "invalid",
            "next_priority": next_priority if integrity["passed"] else None,
            "opens_new_seed": False,
            "authorizes_candidate": False,
        },
    }
    save(args.output, payload)
    print(
        json.dumps(
            {
                "integrity": integrity,
                "margin": effects["margin"],
                "own_score": effects["my_score"],
                "opponents": opponent_means,
                "catastrophic_effects": catastrophic_effects,
                "tails": tails,
                "quadrants": dict(sorted(quadrants.items())),
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
