#!/usr/bin/env python3
"""Apply D75's unchanged analyzer with D75b's strict horizon repair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
import cgauto.analyze_d75a_two_batch_option_sequences as base  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d75b-two-batch-option-sequence-repair-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d75b-option-sequence-manifest.tsv"
MANIFEST_SUMMARY = ANALYSIS / "d75b-option-sequence-manifest-summary.json"
GENERATOR = ROOT / "cgauto/make_d75b_option_sequence_manifest.py"


def strict_horizon_failures(rows: list[dict[str, str]]) -> int:
    return sum(int(row["turn"]) >= 299 for row in rows)


def build_report(
    rows_a_path: Path,
    rows_b_path: Path,
    time_a_path: Path,
    time_b_path: Path,
) -> dict:
    original_paths = (base.PROTOCOL, base.MANIFEST, base.MANIFEST_SUMMARY, base.GENERATOR)
    original_validate = base.validate_manifest

    def validate_repaired_manifest(rows: list[dict[str, str]], summary: dict) -> dict:
        report = original_validate(rows, summary)
        failures = strict_horizon_failures(rows)
        report["horizon_failures"] = failures
        report["maximum_eligible_turn_exclusive"] = 299
        report["pass"] = report["pass"] and failures == 0
        return report

    base.PROTOCOL = PROTOCOL
    base.MANIFEST = MANIFEST
    base.MANIFEST_SUMMARY = MANIFEST_SUMMARY
    base.GENERATOR = GENERATOR
    base.validate_manifest = validate_repaired_manifest
    try:
        report = base.build_report(rows_a_path, rows_b_path, time_a_path, time_b_path)
    finally:
        base.PROTOCOL, base.MANIFEST, base.MANIFEST_SUMMARY, base.GENERATOR = original_paths
        base.validate_manifest = original_validate
    report["schema"] = "troll-farm-d75b-two-batch-option-sequences-v1"
    report["scope"] = "horizon-repaired paired two-batch ordinary-option sequence headroom"
    report["repair"] = {
        "d75a_result": "17b9ff7353bd3ed1ea439c8daf9aab5c6e0e3acb89279870af132cd6f203a4e2",
        "only_change": "maximum eligible turn exclusive changed from 300 to 299",
    }
    report["inputs"]["base_analyzer"] = report["inputs"]["analyzer"]
    report["inputs"]["analyzer"] = sha256_file(Path(__file__))
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-a", type=Path, required=True)
    parser.add_argument("--rows-b", type=Path, required=True)
    parser.add_argument("--time-a", type=Path, required=True)
    parser.add_argument("--time-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.rows_a, args.rows_b, args.time_a, args.time_b)
    atomic_write_new(args.output, report)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "activity": report["activity"],
                "full_oracle": report["full_oracle"],
                "prefix_oracle": report["prefix_oracle"],
                "incremental_oracle": report["incremental_oracle"],
                "gates": report["gates"],
                "decision": report["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
