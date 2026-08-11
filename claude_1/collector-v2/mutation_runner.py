#!/usr/bin/env python3
"""Shared mutation-drive runner for collector v2 (task `20260811-s3-collector-v2`).

Extracted from the B2 drive when B3 needed the same machinery. Each caller supplies its own
mutants; the mechanics — control run, apply, restore, verify restoration, classify — live
here once.

Exit status describes the EXPERIMENT, not just the outcome:
  0 drive complete, every mutant caught
  1 control suite not green before mutating (nothing below can be trusted)
  2 drive completed, but some mutants survived
  3 drive could not be completed — a pattern no longer matches its source, so reporting a
    pass would be a silent false pass
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run_tests(tests: Path, extras: tuple[str, ...] = ()) -> tuple[bool, str]:
    """Run the suite, optionally with extra packages installed.

    `extras` exists because some defects are only reachable in an environment the default run
    does not have. Hard-coding `application/gzip` is invisible while gzip IS the codec, so
    that mutant is inert unless `zstandard` is installed — and an inert mutant proves nothing.
    Rather than delete the mutant or accept a blind spot, the drive runs it where it bites.
    """
    command = ["uvx", "--with", "boto3"]
    for package in extras:
        command += ["--with", package]
    command += ["pytest", str(tests), "-q", "--no-header", "-x"]
    proc = subprocess.run(command, capture_output=True, text=True, cwd=REPO)
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-600:]


def run_drive(*, drive: str, target: Path, tests: Path, mutants: list[tuple],
              out: Path) -> int:
    """Apply each mutant to `target`, run `tests`, restore, and write JSON evidence.

    A mutant is `(id, description, old, new)` or `(id, description, old, new, extras)`, where
    `extras` names packages the suite must be run with for that mutant to be reachable.
    """
    original = target.read_text()
    control_green, control_output = _run_tests(tests)
    results: list[dict] = []
    incomplete: list[str] = []

    if control_green:
        for mutant_id, description, old, new, *rest in mutants:
            extras = tuple(rest[0]) if rest else ()
            occurrences = original.count(old)
            if occurrences != 1:
                incomplete.append(mutant_id)
                results.append({"id": mutant_id, "description": description,
                                "status": "NOT_APPLIED", "extras": list(extras),
                                "reason": f"pattern occurs {occurrences} times, expected 1"})
                continue
            target.write_text(original.replace(old, new, 1))
            try:
                green, tail = _run_tests(tests, extras)
            finally:
                target.write_text(original)
            results.append({"id": mutant_id, "description": description, "status": "APPLIED",
                            "extras": list(extras), "caught": not green,
                            "test_output_tail": None if not green else tail})

    if target.read_text() != original:
        raise RuntimeError(f"{target} was not restored — refusing to report a result")

    applied = [r for r in results if r["status"] == "APPLIED"]
    survivors = [r["id"] for r in applied if not r["caught"]]
    report = {
        "drive": drive,
        "task_id": "20260811-s3-collector-v2",
        "target": str(target.relative_to(REPO)),
        "tests": str(tests.relative_to(REPO)),
        "control_green": control_green,
        "control_output_tail": None if control_green else control_output,
        "mutants_defined": len(mutants),
        "mutants_applied": len(applied),
        "caught": sum(1 for r in applied if r["caught"]),
        "survivors": survivors,
        "not_applied": incomplete,
        "results": results,
    }
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("drive", "control_green", "mutants_defined", "mutants_applied",
                       "caught", "survivors", "not_applied")}, indent=2))

    if not control_green:
        return 1
    if incomplete:
        return 3
    return 2 if survivors else 0
