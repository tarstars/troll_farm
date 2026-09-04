#!/usr/bin/env python3
"""Measure local map-level noise and size the sealed holdout."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
from typing import Any


RESULT_ROOT = "claude_1/h2h-panel/results"
CONTROLS = {
    "champion": "champion-vs-champion.json",
    "nn-clone": "champion-vs-nn-clone.json",
    "old-denial-on": "champion-vs-old-denial-on.json",
    "orchard6": "champion-vs-orchard6.json",
}
PAIR_FILES = [
    (f"{candidate}-vs-{opponent}.json", CONTROLS[opponent])
    for candidate in ("opening-dispatcher", "port-v2", "port-v31")
    for opponent in ("champion", "nn-clone", "old-denial-on", "orchard6")
] + [("orchard6-vs-champion.json", CONTROLS["champion"])]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_bytes(ref: str, path: str) -> bytes:
    completed = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode(errors="replace").strip())
    return completed.stdout


def map_margins(payload: dict[str, Any], policy_seat: int) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in payload["rows"]:
        if row["policy_seat"] != policy_seat:
            continue
        grouped.setdefault(row["map_hash"], []).append(row["policy_score"] - row["bot_score"])
    if not grouped or any(len(values) != 1 for values in grouped.values()):
        raise RuntimeError("each map must have exactly one row at the selected seat")
    return {key: statistics.mean(values) for key, values in grouped.items()}


def centered(values: list[float]) -> list[float]:
    mean = statistics.mean(values)
    return [value - mean for value in values]


def compute(ref: str, target_halfwidth: float, round_to: int) -> dict[str, Any]:
    blobs: dict[str, bytes] = {}
    pooled_arm_residuals: list[float] = []
    pooled_paired_residuals: list[float] = []
    pair_rows: list[dict[str, Any]] = []
    for candidate_name, control_name in PAIR_FILES:
        candidate_path = f"{RESULT_ROOT}/{candidate_name}"
        control_path = f"{RESULT_ROOT}/{control_name}"
        for path in (candidate_path, control_path):
            if path not in blobs:
                blobs[path] = git_bytes(ref, path)
        # TestSession fixes submitted code at player 0.  Use the matching local seat rather
        # than gaining artificial precision from averaging a seat swap unavailable there.
        candidate = map_margins(json.loads(blobs[candidate_path]), policy_seat=0)
        control = map_margins(json.loads(blobs[control_path]), policy_seat=0)
        if candidate.keys() != control.keys():
            raise RuntimeError(f"map identities do not align: {candidate_name} / {control_name}")
        candidate_values = list(candidate.values())
        control_values = list(control.values())
        differences = [candidate[key] - control[key] for key in candidate]
        pooled_arm_residuals.extend(centered(candidate_values))
        pooled_arm_residuals.extend(centered(control_values))
        pooled_paired_residuals.extend(centered(differences))
        pair_rows.append(
            {
                "candidate": candidate_path,
                "control": control_path,
                "maps": len(candidate),
                "candidate_mean_margin": statistics.mean(candidate_values),
                "control_mean_margin": statistics.mean(control_values),
                "mean_paired_delta": statistics.mean(differences),
                "arm_sd": statistics.stdev(candidate_values + control_values),
                "paired_difference_sd": statistics.stdev(differences),
            }
        )

    arm_sd = statistics.stdev(pooled_arm_residuals)
    paired_sd = statistics.stdev(pooled_paired_residuals)
    raw_n = math.ceil(2 * (1.96 * arm_sd / target_halfwidth) ** 2)
    selected_n = math.ceil(raw_n / round_to) * round_to
    required_halfwidth = 1.96 * arm_sd * math.sqrt(2 / selected_n)
    direct_paired_halfwidth = 1.96 * paired_sd / math.sqrt(selected_n)
    source_commit = subprocess.check_output(["git", "rev-parse", ref], text=True).strip()
    return {
        "schema_version": 1,
        "created_utc": utc_now(),
        "purpose": "sample-size calibration only; the retired panel is not a generalisation test",
        "source_ref": ref,
        "source_commit": source_commit,
        "unit": "official map with candidate/control each at player 0",
        "seat_choice": (
            "policy_seat=0, matching TestSession's submitted-code player index; "
            "the unavailable seat swap is not averaged in"
        ),
        "pair_count": len(PAIR_FILES),
        "maps_per_pair": pair_rows[0]["maps"],
        "centered_arm_observations": len(pooled_arm_residuals),
        "centered_paired_observations": len(pooled_paired_residuals),
        "local_paired_arm_sd": arm_sd,
        "local_pooled_paired_difference_sd": paired_sd,
        "required_formula": "halfwidth = 1.96 * local_paired_arm_sd * sqrt(2 / n_maps)",
        "target_halfwidth": target_halfwidth,
        "minimum_n_unrounded": raw_n,
        "rounding_multiple": round_to,
        "selected_n_maps": selected_n,
        "selected_required_formula_halfwidth": required_halfwidth,
        "selected_direct_paired_halfwidth_check": direct_paired_halfwidth,
        "detectable_effect_interpretation": (
            "A true paired mean score delta must exceed the required-formula half-width "
            "for its normal-approximation 95% lower bound to clear zero."
        ),
        "inputs": [
            {"path": path, "sha256": hashlib.sha256(content).hexdigest()}
            for path, content in sorted(blobs.items())
        ],
        "pairs": pair_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--target-halfwidth", type=float, default=5.0)
    parser.add_argument("--round-to", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.target_halfwidth <= 0 or args.round_to <= 0:
        parser.error("target half-width and round-to must be positive")
    report = compute(args.ref, args.target_halfwidth, args.round_to)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "local_arm_sd={:.6f} local_paired_sd={:.6f} selected_n={} halfwidth={:.6f}".format(
            report["local_paired_arm_sd"],
            report["local_pooled_paired_difference_sd"],
            report["selected_n_maps"],
            report["selected_required_formula_halfwidth"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
