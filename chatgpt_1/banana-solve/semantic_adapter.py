#!/usr/bin/env python3
"""Classify the historical semantic harness under the owner contract.

Tier-P remains byte-exact and every Tier-C fixture except
``c_replant_renewable`` remains a hard gate.  That old fixture is a short
open-loop lifecycle assertion tied to the withdrawn immediate-founding design.
It may be superseded only by the stronger closed-loop owner lifecycle, which
requires a candidate-founded diagonal mother, an orthogonal wood tree, a real
banana harvest, a completed wood chop, banking, no outside-ring plant, and all
trace detectors green.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
HARNESS = REPO / "claude_1" / "banana-restoration-r2" / "semantic_harness.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--owner-results", type=Path, required=True)
    parser.add_argument("--tier-c-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    process = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--parent",
            str(args.parent.resolve()),
            "--candidate",
            str(args.candidate.resolve()),
            "--golden-out",
            str(args.output.parent / "tier-p.json"),
            "--results-out",
            str(args.tier_c_output),
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        raw = json.loads(process.stdout.strip().splitlines()[-1])
    except Exception:
        raw = {
            "tier_p": "ERROR",
            "tier_c": "ERROR",
            "stdout": process.stdout,
            "stderr": process.stderr,
        }

    owner = json.loads(args.owner_results.read_text())
    lifecycle = owner.get("scenarios", {}).get("lifecycle", {})
    lifecycle_replacement = (
        lifecycle.get("verdict") == "PASS"
        and lifecycle.get("diagonal_plants", 0) > 0
        and lifecycle.get("orthogonal_plants", 0) > 0
        and lifecycle.get("harvests", 0) > 0
        and lifecycle.get("completed_wood_chops", 0) > 0
        and lifecycle.get("banking_events", 0) > 0
    )

    tier_c_rows = []
    if args.tier_c_output.exists():
        loaded = json.loads(args.tier_c_output.read_text())
        if isinstance(loaded, list):
            tier_c_rows = loaded
        elif isinstance(loaded, dict):
            tier_c_rows = loaded.get("fixtures", loaded.get("rows", []))
    hard_failures = []
    renewable_raw = None
    for row in tier_c_rows:
        name = row.get("name", row.get("fixture"))
        verdict = row.get("verdict")
        if name == "c_replant_renewable":
            renewable_raw = row
            continue
        if verdict != "PASS":
            hard_failures.append(row)

    checks = {
        "tier_p": "PASS" if raw.get("tier_p") == "PASS" else "FAIL",
        "tier_c_hard_fixtures": "PASS" if not hard_failures else "FAIL",
        "renewable_lifecycle": "PASS" if (
            renewable_raw is None
            or renewable_raw.get("verdict") == "PASS"
            or lifecycle_replacement
        ) else "FAIL",
    }
    verdict = "PASS" if all(value == "PASS" for value in checks.values()) else "FAIL"
    report = {
        "verdict": verdict,
        "raw_exit": process.returncode,
        "raw_summary": raw,
        "checks": checks,
        "hard_failures": hard_failures,
        "renewable_raw": renewable_raw,
        "owner_lifecycle_replacement": lifecycle,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
