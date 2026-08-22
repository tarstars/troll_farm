#!/usr/bin/env python3
"""Prove the E7a candidate is exactly CONTROL or full-FLIP per initial state.

This is a deterministic semantic bridge on a representative replay set. It does not
estimate value and never publishes traces or command streams.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chatgpt_1 import e7a_sector_candidate_builder as builder
from cgauto import e7_type_to_cut_audit as e7


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def representative_seeds() -> list[tuple[int, str]]:
    rows = builder.load_sector_rows()
    selected = [int(row["seed"]) for row in rows if builder.row_is_sector(row)]
    outside_lemon = [
        int(row["seed"])
        for row in rows
        if row["default_species"] == "LEMON" and not builder.row_is_sector(row)
    ]
    outside_plum = [
        int(row["seed"])
        for row in rows
        if row["default_species"] == "PLUM"
    ]
    seeds = (
        [(seed, "FLIP") for seed in selected[:4]]
        + [(seed, "CONTROL") for seed in outside_lemon[:2]]
        + [(seed, "CONTROL") for seed in outside_plum[:2]]
    )
    if len(seeds) != 8 or len({seed for seed, _ in seeds}) != 8:
        raise RuntimeError(f"representative seed selection failed: {seeds}")
    return seeds


def differing_keys(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    keys = sorted(set(left) | set(right))
    return [key for key in keys if left.get(key) != right.get(key)]


def run(output: Path) -> dict[str, Any]:
    rows = {int(row["seed"]): row for row in builder.load_sector_rows()}
    seeds = representative_seeds()
    opponent_name = "motion"
    if opponent_name not in e7.OPPONENT_SOURCES:
        raise RuntimeError("frozen motion opponent is unavailable")

    with tempfile.TemporaryDirectory(prefix="e7a-sector-bridge-") as directory:
        temp = Path(directory)
        candidate_source = temp / "candidate.rs"
        candidate_manifest = temp / "candidate-manifest.json"
        builder.build(candidate_source, candidate_manifest, compile_source=False)

        parent = builder.PARENT.read_bytes()
        flip_source = temp / "flip.rs"
        flip_source.write_bytes(e7.transform_source(parent))

        control_binary = temp / "control"
        flip_binary = temp / "flip"
        candidate_binary = temp / "candidate"
        opponent_binary = temp / "opponent"
        e7.compile_source(builder.PARENT, control_binary, "e7a_bridge_control")
        e7.compile_source(flip_source, flip_binary, "e7a_bridge_flip")
        e7.compile_source(candidate_source, candidate_binary, "e7a_bridge_candidate")
        e7.compile_source(
            e7.OPPONENT_SOURCES[opponent_name],
            opponent_binary,
            "e7a_bridge_motion",
        )
        runtime_shim = e7.compile_runtime_shim(temp)

        previous_preload = os.environ.get("LD_PRELOAD")
        os.environ["LD_PRELOAD"] = (
            str(runtime_shim)
            if not previous_preload
            else f"{runtime_shim}:{previous_preload}"
        )
        comparisons = []
        try:
            for seed, expected_arm in seeds:
                row = rows[seed]
                computed_arm = "FLIP" if builder.row_is_sector(row) else "CONTROL"
                if computed_arm != expected_arm:
                    raise RuntimeError(
                        f"seed {seed}: expected fixture {expected_arm}, rule gives {computed_arm}"
                    )
                expected_binary = (
                    flip_binary if expected_arm == "FLIP" else control_binary
                )
                for seat in (0, 1):
                    candidate = e7.policy_match(
                        seed,
                        candidate_binary,
                        opponent_binary,
                        seat,
                        diagnostic=False,
                    )
                    expected = e7.policy_match(
                        seed,
                        expected_binary,
                        opponent_binary,
                        seat,
                        diagnostic=False,
                    )
                    differences = differing_keys(candidate, expected)
                    if differences:
                        raise RuntimeError(
                            f"bridge mismatch seed={seed} seat={seat} arm={expected_arm}: "
                            f"{differences}"
                        )
                    if candidate.get("malformed_commands"):
                        raise RuntimeError(f"malformed commands seed={seed} seat={seat}")
                    if candidate.get("unexpected_stderr_bytes"):
                        raise RuntimeError(f"unexpected stderr seed={seed} seat={seat}")
                    comparisons.append(
                        {
                            "seed": seed,
                            "seat": seat,
                            "expected_arm": expected_arm,
                            "default_species": row["default_species"],
                            "delta_dist_sum": int(float(row["delta_dist_sum"])),
                            "exact_full_result": True,
                            "policy_action_stream_sha256": candidate.get(
                                "policy_action_stream_sha256"
                            ),
                            "opponent_action_stream_sha256": candidate.get(
                                "opponent_action_stream_sha256"
                            ),
                            "terminal_state_sha256": candidate.get(
                                "terminal_state_sha256"
                            ),
                        }
                    )
        finally:
            if previous_preload is None:
                os.environ.pop("LD_PRELOAD", None)
            else:
                os.environ["LD_PRELOAD"] = previous_preload

        result = {
            "schema": "troll-farm-e7a-sector-bridge/1",
            "task": "20260802-e7a-sector-candidate",
            "verdict": "EXACT_CONTROL_OR_FLIP_BRIDGE",
            "parent_sha256": builder.PARENT_SHA256,
            "flip_sha256": digest(flip_source),
            "candidate_sha256": digest(candidate_source),
            "opponent": opponent_name,
            "seed_count": len(seeds),
            "seat_game_count": len(comparisons),
            "inside_sector_seed_count": sum(arm == "FLIP" for _, arm in seeds),
            "outside_sector_seed_count": sum(arm == "CONTROL" for _, arm in seeds),
            "all_exact": all(row["exact_full_result"] for row in comparisons),
            "runtime_or_command_faults": 0,
            "comparisons": comparisons,
            "value_estimate": None,
            "arena_authorized": False,
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "candidate_sha256": result["candidate_sha256"],
                "seed_count": result["seed_count"],
                "seat_game_count": result["seat_game_count"],
                "all_exact": result["all_exact"],
            },
            sort_keys=True,
        )
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "chatgpt_1/e7a-sector-candidate-bridge-2026-08-02.json",
    )
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
