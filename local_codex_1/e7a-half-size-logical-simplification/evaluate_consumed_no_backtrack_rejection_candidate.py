#!/usr/bin/env python3
"""Evaluate one declared source on the consumed 9,865,000--042 transfer panel.

This is diagnostic attribution after the locked verdict. It cannot qualify a source and
exposes no seed-range or panel-shape controls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import evaluate_fresh_no_backtrack_gate as gate
import evaluate_open_panel as shared


REPO = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.candidate = arguments.candidate.resolve()
    if arguments.panel.exists() or arguments.output.exists():
        parser.error("diagnostic output path already exists")
    if sha256(arguments.candidate) != arguments.candidate_sha256:
        parser.error("candidate hash mismatch")

    gate.CANDIDATE = arguments.candidate
    gate.CANDIDATE_SHA256 = arguments.candidate_sha256
    with tempfile.TemporaryDirectory(
        prefix="e7a-half-consumed-no-backtrack-rejection-diagnostic-"
    ) as temporary:
        binary, compiler = gate.compile_runner(Path(temporary))
        completed = subprocess.run(
            [
                str(binary),
                str(gate.FRESH_START),
                str(gate.FRESH_MAPS),
                str(arguments.panel),
                str(gate.THREADS),
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=3600,
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr[-12000:])

    rows, latency = shared.parse_panel(arguments.panel)
    result = shared.analyze(
        rows,
        latency,
        maps=gate.FRESH_MAPS,
        bootstrap_samples=gate.BOOTSTRAP_SAMPLES,
        compiler=compiler,
        panel_path=arguments.panel,
        candidate=arguments.candidate,
        candidate_sha256=arguments.candidate_sha256,
        runner=gate.RUNNER_TEMPLATE,
        evidence_boundary=(
            "diagnostic replay of consumed transfer maps; cannot qualify a source"
        ),
    )
    result["schema"] = "troll-farm-e7a-half-size-consumed-fresh-diagnostic-v1"
    result["diagnostic_driver_sha256"] = sha256(Path(__file__))
    result["consumed_range"] = {
        "start": gate.FRESH_START,
        "end_inclusive": gate.FRESH_END - 1,
        "qualification_allowed": False,
    }
    result["run_stderr"] = completed.stderr.strip()
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "mean": result["metrics"]["mean_margin_delta"],
                "lower": result["metrics"]["bootstrap_95_lower"],
                "catastrophes": result["metrics"]["catastrophes"],
                "negative_mass": result["metrics"]["negative_margin_mass"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
