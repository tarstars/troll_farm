#!/usr/bin/env python3
"""Apply D88c's conservative support-count correction to immutable D88b JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correct(payload: dict, *, input_hash: str | None = None) -> dict:
    if payload.get("schema") != "d88b-yaichi-task-state-v1":
        raise ValueError("expected immutable D88b aggregate")
    validation = payload["mechanism"]["validation"]
    if validation["renewable_games"] != 10:
        raise ValueError("D86 support correction requires exactly ten renewable games")
    original = payload["mechanism_gates"]
    gates = {
        "bank_before_maintenance_all_10": (
            validation["bank_bootstrap_before_maintenance_games"] == 10
        ),
        "supported_starter_plants_at_least_0.80": original[
            "supported_starter_plants_at_least_0.80"
        ],
        "own_crop_same_worker_replant_at_least_0.80": original[
            "own_crop_same_worker_replant_at_least_0.80"
        ],
        "trained_chop_drop_at_least_0.95": original[
            "trained_chop_drop_at_least_0.95"
        ],
        "trained_farm_in_at_most_one_game": original[
            "trained_farm_in_at_most_one_game"
        ],
        "complete_ordered_phases_all_10": (
            validation["complete_ordered_phase_games"] == 10
        ),
        "current_same_qualitative_direction": original[
            "current_same_qualitative_direction"
        ],
    }
    integrity_pass = all(group["pass"] for group in payload["integrity"].values())
    decision = (
        "pass_write_blueprint_open_d89"
        if integrity_pass and all(gates.values())
        else "reject_or_repair_under_corrected_support"
    )
    return {
        "schema": "d88c-support-count-correction-v1",
        "source_schema": payload["schema"],
        "source_sha256": input_hash,
        "source_rows_hash": payload["rows_hash"],
        "original_decision": payload["decision"],
        "known_support": {
            "validation_games": payload["counts"]["validation"],
            "renewable_games": validation["renewable_games"],
            "nonrenewable_games": payload["counts"]["validation"]
            - validation["renewable_games"],
        },
        "integrity_pass": integrity_pass,
        "mechanism": payload["mechanism"],
        "corrected_gates": gates,
        "decision": decision,
    }


def write_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = correct(
        json.loads(args.input.read_text()), input_hash=sha256_file(args.input)
    )
    write_atomic(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
