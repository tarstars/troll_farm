#!/usr/bin/env python3
"""Classify the historical semantic harness under the owner contract.

Tier-P remains byte-exact and every Tier-C fixture except
``c_replant_renewable`` remains a hard gate. That old fixture is a short
open-loop lifecycle assertion tied to the withdrawn immediate-founding design.
It may be superseded only by the stronger closed-loop owner lifecycle, which
requires a candidate-founded diagonal mother, an orthogonal wood tree, a real
banana harvest, a completed wood chop, banking, no outside-ring plant, and all
blocking trace detectors green.
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


def all_pass(value) -> bool:
    if value == "PASS":
        return True
    if isinstance(value, dict) and value:
        return all(item == "PASS" for item in value.values())
    return False


def normalize_tier_c(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("results"), dict):
        return [
            {
                "name": name,
                "verdict": row.get("status") if isinstance(row, dict) else row,
                "raw": row,
            }
            for name, row in sorted(payload["results"].items())
        ]
    for key in ("fixtures", "rows"):
        if isinstance(payload.get(key), list):
            return payload[key]
    if payload and all(isinstance(value, str) for value in payload.values()):
        return [
            {"name": name, "verdict": verdict}
            for name, verdict in sorted(payload.items())
        ]
    return []


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
        and not lifecycle.get("outside_ring_plants")
        and not lifecycle.get("blocking_detectors")
    )

    tier_c_rows = []
    if args.tier_c_output.exists():
        tier_c_rows = normalize_tier_c(
            json.loads(args.tier_c_output.read_text())
        )
    if not tier_c_rows:
        tier_c_rows = normalize_tier_c(raw.get("tier_c"))

    hard_failures = []
    renewable_raw = None
    for row in tier_c_rows:
        name = row.get("name", row.get("fixture"))
        verdict = row.get("verdict", row.get("status"))
        if name == "c_replant_renewable":
            renewable_raw = row
            continue
        if verdict != "PASS":
            hard_failures.append(row)

    checks = {
        "tier_p": "PASS" if all_pass(raw.get("tier_p")) else "FAIL",
        "tier_c_hard_fixtures": "PASS" if not hard_failures else "FAIL",
        "renewable_lifecycle": "PASS" if (
            renewable_raw is None
            or renewable_raw.get("verdict", renewable_raw.get("status")) == "PASS"
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
