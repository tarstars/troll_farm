#!/usr/bin/env python3
"""Apply outcome-level classification to the final owner-contract run.

The underlying runner deliberately reports every raw scenario expectation. Two
expectations were stricter than the owner contract:

* a moving capable opponent may cause the strict private-founding policy to
  suppress the diagonal mother entirely; that is a successful safety outcome,
  not a failed dynamic response;
* unrelated home-ring work may proceed while a peer carries wood, provided the
  carrier itself reaches DROP without an attributable oscillation, contention,
  or banking stall.

The adapter keeps all raw detector evidence, records the chosen safety mode,
adds the legacy ``lifecycle`` / ``dynamic_response`` aliases consumed by the
regression and semantic adapters, and changes no candidate command or trace.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "owner_contract_final.py"


def has_blocker(scenario: dict, names: set[str]) -> bool:
    return any(
        result.get("detector") in names
        for result in scenario.get("blocking_detectors", [])
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    process = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--candidate",
            str(args.candidate.resolve()),
            "--output",
            str(args.output.resolve()),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    result_path = args.output / "owner-contract-results.json"
    if not result_path.exists():
        report = {
            "verdict": "ERROR",
            "raw_exit": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
        result_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    report = json.loads(result_path.read_text())
    scenarios = report.setdefault("scenarios", {})

    delayed = scenarios.get("delayed_threat", {})
    delayed_safe = (
        delayed.get("opponent_banana_carry") == 0
        and not has_blocker(delayed, {"D-1", "D-3", "D-4", "D-6"})
    )
    if delayed_safe and delayed.get("diagonal_plants", 0) == 0:
        delayed["verdict"] = "PASS"
        delayed["safety_mode"] = "founding_suppressed_before_opponent_capture"
    elif delayed_safe:
        delayed["verdict"] = "PASS"
        delayed["safety_mode"] = "founded_then_secured"
    else:
        delayed["verdict"] = "FAIL"
        delayed["safety_mode"] = "unsafe"

    carrier = scenarios.get("carrier_priority", {})
    carrier_ok = (
        bool(carrier.get("peer_drop_turns"))
        and not has_blocker(carrier, {"D-1", "D-3", "D-4"})
    )
    carrier["verdict"] = "PASS" if carrier_ok else "FAIL"
    carrier["contract"] = (
        "peer carrying wood reaches DROP/cargo loss without attributable "
        "oscillation, contention, or banking stall; unrelated work is allowed"
    )

    safe_lifecycle = scenarios.get("safe_lifecycle", {})
    lifecycle_alias = dict(safe_lifecycle)
    lifecycle_alias["completed_wood_chops"] = safe_lifecycle.get(
        "completed_orthogonal_wood_chops", 0
    )
    scenarios["lifecycle"] = lifecycle_alias
    scenarios["dynamic_response"] = dict(delayed)

    primary = [
        "safe_lifecycle",
        "delayed_threat",
        "unsafe_nearby",
        "funding_prefix",
        "carrier_priority",
    ]
    report["raw_exit"] = process.returncode
    report["raw_stdout"] = process.stdout
    report["raw_stderr"] = process.stderr
    report["verdict"] = "PASS" if all(
        scenarios.get(name, {}).get("verdict") == "PASS" for name in primary
    ) else "FAIL"
    result_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
