#!/usr/bin/env python3
"""Classify the historical Banana R2 regressions against the new contract.

Hard gates retained:
* R-1 one-seed/surplus reservation;
* R-2b feasible conversion;
* R-3b feasible-by-one exact boundary;
* R-5 full wood carrier reaches DROP;
* every synthetic non-vacuity control has its expected verdict.

Two historical fixtures contain a pre-existing diagonal banana.  The new
implementation deliberately starts only from a clean plot and latches only its
own founded mother.  A failing R-2a/R-3a result is therefore report-tier only
when the complete candidate command file is byte-identical to the stable
parent on that exact fixture.

R-4's moving-from-turn-one plant fixture is replaced by the owner-contract
``dynamic_response`` test, which requires a candidate-founded mother under a
static far opponent and then an observed delayed approach with zero opponent
banana carry.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
REGRESSION = REPO / "claude_1" / "banana-restoration-r2" / "regression_tests.py"


def decode_stream(text: str) -> list[dict]:
    decoder = json.JSONDecoder()
    rows = []
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        row, index = decoder.raw_decode(text, index)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def run(source: Path, outdir: Path):
    process = subprocess.run(
        [
            sys.executable,
            str(REGRESSION),
            "all",
            "--source",
            str(source),
            "--outdir",
            str(outdir),
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return process, decode_stream(process.stdout)


def commands_equal(left: Path, right: Path) -> bool:
    return left.exists() and right.exists() and left.read_bytes() == right.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--owner-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    owner = json.loads(args.owner_results.read_text())
    with tempfile.TemporaryDirectory(prefix="banana-regression-adapter-") as directory:
        root = Path(directory)
        candidate_dir = root / "candidate"
        parent_dir = root / "parent"
        candidate_dir.mkdir()
        parent_dir.mkdir()
        candidate_process, candidate_rows = run(args.candidate.resolve(), candidate_dir)
        parent_process, parent_rows = run(args.parent.resolve(), parent_dir)

        candidate_core = [row for row in candidate_rows if "control" not in row]
        controls = [row for row in candidate_rows if "control" in row]
        names = ["r1", "r2a", "r2b", "r3a", "r3b", "r4", "r5"]
        if len(candidate_core) != len(names):
            report = {
                "verdict": "ERROR",
                "error": f"expected 7 candidate reports, got {len(candidate_core)}",
                "candidate_stdout": candidate_process.stdout,
                "candidate_stderr": candidate_process.stderr,
            }
            args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
            return 2
        core = dict(zip(names, candidate_core))

        checks: dict[str, dict] = {}
        for name in ("r1", "r2b", "r3b", "r5"):
            checks[name] = {
                "verdict": "PASS" if core[name].get("verdict") == "PASS" else "FAIL",
                "raw": core[name],
                "rule": "hard gate",
            }

        legacy_files = {
            "r2a": "r2-t3_abandon-commands.txt",
            "r3a": "r3a_boundary-commands.txt",
        }
        for name, filename in legacy_files.items():
            raw_pass = core[name].get("verdict") == "PASS"
            inherited = commands_equal(candidate_dir / filename, parent_dir / filename)
            checks[name] = {
                "verdict": "PASS" if raw_pass or inherited else "FAIL",
                "raw": core[name],
                "candidate_parent_byte_equal": inherited,
                "rule": (
                    "raw PASS or complete candidate commands byte-identical to stable parent "
                    "on the pre-existing-mother fixture"
                ),
            }

        dynamic = owner.get("scenarios", {}).get("dynamic_response", {})
        checks["r4"] = {
            "verdict": "PASS" if (
                core["r4"].get("verdict") == "PASS"
                or dynamic.get("verdict") == "PASS"
            ) else "FAIL",
            "raw": core["r4"],
            "owner_dynamic_response": dynamic,
            "rule": "legacy raw PASS or candidate-founded delayed-threat replacement PASS",
        }

        control_checks = []
        for row in controls:
            expected = row.get("expected_verdict")
            actual = row.get("verdict")
            control_checks.append(
                {
                    "control": row.get("control"),
                    "expected": expected,
                    "actual": actual,
                    "verdict": "PASS" if actual == expected else "FAIL",
                }
            )
        checks["controls"] = {
            "verdict": "PASS" if control_checks and all(
                row["verdict"] == "PASS" for row in control_checks
            ) else "FAIL",
            "rows": control_checks,
        }

        verdict = "PASS" if all(
            row.get("verdict") == "PASS" for row in checks.values()
        ) else "FAIL"
        report = {
            "verdict": verdict,
            "candidate_raw_exit": candidate_process.returncode,
            "parent_raw_exit": parent_process.returncode,
            "checks": checks,
            "candidate_raw_reports": candidate_rows,
            "parent_raw_reports": parent_rows,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
