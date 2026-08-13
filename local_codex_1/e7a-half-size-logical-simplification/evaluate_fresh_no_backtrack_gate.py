#!/usr/bin/env python3
"""Run the one-shot untouched gate for the locked no-backtrack successor.

This launcher exposes no seed-range, map-count, thread-count, or bootstrap arguments.
It transforms the reviewed open-panel runner only by replacing its bounded seed
constants, then runs exactly 43 maps, both seats, and the same six opponent families.
The source, range, launcher, and lock must be pushed before this program is executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import evaluate_open_panel as shared


REPO = Path(__file__).resolve().parents[2]
DIRECTORY = Path(__file__).resolve().parent
CANDIDATE = DIRECTORY / "focused-yamo-bank-convoy-no-backtrack.rs"
CANDIDATE_SHA256 = "a767e36228c872ad566b4347825f5282f95e50ae9f59fcf5a42b682989d85fea"
RUNNER_TEMPLATE = DIRECTORY / "open_panel_runner.rs"
RUNNER_TEMPLATE_SHA256 = (
    "05335ff0226394abe0216e172bf234c56051358bbc29fceb5f5de86da9361a45"
)
FRESH_START = 9_865_000
FRESH_MAPS = 43
FRESH_END = FRESH_START + FRESH_MAPS
THREADS = 8
BOOTSTRAP_SAMPLES = 50_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fresh_runner_source() -> str:
    if sha256(RUNNER_TEMPLATE) != RUNNER_TEMPLATE_SHA256:
        raise RuntimeError("runner-template hash mismatch")
    source = RUNNER_TEMPLATE.read_text()
    replacements = {
        "const OPEN_START: i64 = 9_854_000;": (
            f"const OPEN_START: i64 = {FRESH_START:_};"
        ),
        "const OPEN_END: i64 = 9_854_128;": f"const OPEN_END: i64 = {FRESH_END:_};",
    }
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise RuntimeError(f"runner range marker is not unique: {old}")
        source = source.replace(old, new, 1)
    return source


def compile_runner(directory: Path) -> tuple[Path, dict]:
    if sha256(shared.BASELINE) != shared.BASELINE_SHA256:
        raise RuntimeError("baseline hash mismatch")
    if sha256(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("candidate hash mismatch")
    if sha256(shared.SACRED) != shared.SACRED_SHA256:
        raise RuntimeError("sacred hash mismatch")
    if not shared.RUST_LIBRARY.is_file():
        raise FileNotFoundError(
            f"missing {shared.RUST_LIBRARY}; run cargo build --release --lib in rust"
        )

    baseline_module = directory / "baseline_module.rs"
    candidate_module = directory / "candidate_module.rs"
    runner_text = fresh_runner_source()
    baseline_module.write_text(
        shared.module_source(shared.BASELINE.read_text(), "baseline")
    )
    candidate_module.write_text(
        shared.module_source(CANDIDATE.read_text(), "candidate")
    )
    runner_file = tempfile.NamedTemporaryFile(
        mode="w",
        prefix=".e7a-half-no-backtrack-fresh-runner-",
        suffix=".rs",
        dir=DIRECTORY,
        delete=False,
    )
    try:
        runner_file.write(runner_text)
        runner_file.close()
        runner_source = Path(runner_file.name)
        binary = directory / "fresh_panel_runner"
        environment = dict(os.environ)
        environment.update(
            {
                "E7A_HALF_BASELINE_MODULE": str(baseline_module),
                "E7A_HALF_CANDIDATE_MODULE": str(candidate_module),
            }
        )
        completed = subprocess.run(
            [
                "rustc",
                "--crate-name",
                "e7a_half_no_backtrack_fresh_runner",
                "--edition=2021",
                "-C",
                "opt-level=3",
                "-C",
                "overflow-checks=off",
                "-A",
                "warnings",
                str(runner_source),
                "--extern",
                f"troll_farm={shared.RUST_LIBRARY}",
                "-L",
                f"dependency={shared.RUST_DEPS}",
                "-o",
                str(binary),
            ],
            cwd=REPO,
            env=environment,
            text=True,
            capture_output=True,
            timeout=180,
        )
    finally:
        Path(runner_file.name).unlink(missing_ok=True)
    if completed.returncode:
        raise RuntimeError(f"runner compile failed:\n{completed.stderr[:12000]}")
    return binary, {
        "evaluator_sha256": sha256(Path(__file__)),
        "runner_template_sha256": RUNNER_TEMPLATE_SHA256,
        "fresh_runner_sha256": hashlib.sha256(runner_text.encode()).hexdigest(),
        "baseline_module_sha256": sha256(baseline_module),
        "candidate_module_sha256": sha256(candidate_module),
        "rust_library_sha256": sha256(shared.RUST_LIBRARY),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.panel.exists() or arguments.output.exists():
        parser.error("one-shot output path already exists")

    with tempfile.TemporaryDirectory(
        prefix="e7a-half-no-backtrack-fresh-gate-"
    ) as temporary:
        binary, compiler = compile_runner(Path(temporary))
        completed = subprocess.run(
            [
                str(binary),
                str(FRESH_START),
                str(FRESH_MAPS),
                str(arguments.panel),
                str(THREADS),
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=3600,
        )
        if completed.returncode:
            raise RuntimeError(f"fresh panel failed:\n{completed.stderr[-12000:]}")
        run_stderr = completed.stderr.strip()

    rows, latency = shared.parse_panel(arguments.panel)
    observed_seeds = sorted({int(row["map_seed"]) for row in rows})
    expected_seeds = list(range(FRESH_START, FRESH_END))
    if observed_seeds != expected_seeds:
        raise RuntimeError("fresh range identity mismatch")
    result = shared.analyze(
        rows,
        latency,
        maps=FRESH_MAPS,
        bootstrap_samples=BOOTSTRAP_SAMPLES,
        compiler=compiler,
        panel_path=arguments.panel,
        candidate=CANDIDATE,
        candidate_sha256=CANDIDATE_SHA256,
        runner=RUNNER_TEMPLATE,
        evidence_boundary=(
            "one-shot untouched continued-referee engineering transfer gate; "
            "not an Arena predictor"
        ),
    )
    result["schema"] = "troll-farm-e7a-half-size-fresh-panel-v1"
    result["fresh_gate"] = {
        "locked_start_seed": FRESH_START,
        "locked_end_seed_inclusive": FRESH_END - 1,
        "one_shot": True,
        "range_arguments_exposed": False,
        "map_count_arguments_exposed": False,
        "threads": THREADS,
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
    }
    result["run_stderr"] = run_stderr
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "tasks": result["panel"]["tasks"],
                "mean_delta": result["metrics"]["mean_margin_delta"],
                "lower": result["metrics"]["bootstrap_95_lower"],
                "failed_gates": [
                    name for name, passed in result["gates"].items() if not passed
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
