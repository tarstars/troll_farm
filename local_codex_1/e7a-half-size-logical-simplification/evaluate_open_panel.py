#!/usr/bin/env python3
"""Build, run, and analyze the frozen continued-referee E7a open panel."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
DIRECTORY = Path(__file__).resolve().parent
BASELINE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
)
BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
CANDIDATE = DIRECTORY / "integrated-half-r32.rs"
CANDIDATE_SHA256 = "abb202db71040f8784b7d02cc114ced9f71d82e82d3c8a1cc975d87d3feeb4da"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
RUNNER = DIRECTORY / "open_panel_runner.rs"
RUST_DEPS = REPO / "rust/target/release/deps"
RUST_LIBRARY = RUST_DEPS / "libtroll_farm.rlib"
OPEN_START = 9_854_000
OPEN_END = 9_854_128
OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_source(source: str, module: str) -> str:
    """Expose top modules and redirect absolute paths without changing policy logic."""

    for marker in ("mod game{", "mod bot{"):
        if source.count(marker) != 1:
            raise ValueError(f"expected one {marker!r}")
        source = source.replace(marker, f"pub {marker}", 1)
    source = source.replace("crate::game", f"crate::{module}::game")
    source = source.replace("crate::bot", f"crate::{module}::bot")
    return source


def compile_runner(directory: Path) -> tuple[Path, dict]:
    if sha256(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("baseline hash mismatch")
    if sha256(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("candidate hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred hash mismatch")
    if not RUST_LIBRARY.is_file():
        raise FileNotFoundError(
            f"missing {RUST_LIBRARY}; run cargo build --release --lib in rust"
        )
    baseline_module = directory / "baseline_module.rs"
    candidate_module = directory / "candidate_module.rs"
    baseline_module.write_text(module_source(BASELINE.read_text(), "baseline"))
    candidate_module.write_text(module_source(CANDIDATE.read_text(), "candidate"))
    binary = directory / "open_panel_runner"
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
            "--edition=2021",
            "-C",
            "opt-level=3",
            "-C",
            "overflow-checks=off",
            "-A",
            "warnings",
            str(RUNNER),
            "--extern",
            f"troll_farm={RUST_LIBRARY}",
            "-L",
            f"dependency={RUST_DEPS}",
            "-o",
            str(binary),
        ],
        cwd=REPO,
        env=environment,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(f"runner compile failed:\n{completed.stderr[:12000]}")
    return binary, {
        "runner_sha256": sha256(RUNNER),
        "baseline_module_sha256": sha256(baseline_module),
        "candidate_module_sha256": sha256(candidate_module),
        "rust_library_sha256": sha256(RUST_LIBRARY),
    }


def parse_panel(path: Path) -> tuple[list[dict], dict]:
    data_lines = []
    latency = {}
    for line in path.read_text().splitlines():
        if line.startswith("#latency\t"):
            _, arm, count, p95, maximum = line.split("\t")
            latency[arm] = {
                "samples": int(count),
                "p95_ns": int(p95),
                "maximum_ns": int(maximum),
                "p95_ms": int(p95) / 1_000_000,
                "maximum_ms": int(maximum) / 1_000_000,
            }
        elif line:
            data_lines.append(line)
    reader = csv.DictReader(data_lines, delimiter="\t")
    integer_fields = set(reader.fieldnames or ()) - {"opponent"}
    rows = []
    for raw in reader:
        row = {
            key: (int(value) if key in integer_fields and value else None)
            for key, value in raw.items()
        }
        row["opponent"] = raw["opponent"]
        rows.append(row)
    return rows, latency


def mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def bootstrap_lower(rows: list[dict], samples: int) -> float:
    by_seed = {}
    for row in rows:
        by_seed.setdefault(row["map_seed"], []).append(row["delta"])
    seed_means = [statistics.mean(values) for _, values in sorted(by_seed.items())]
    randomizer = random.Random(20260803)
    distribution = []
    for _ in range(samples):
        distribution.append(
            statistics.mean(randomizer.choice(seed_means) for _ in seed_means)
        )
    distribution.sort()
    return distribution[int(0.025 * samples)]


def analyze(
    rows: list[dict],
    latency: dict,
    *,
    maps: int,
    bootstrap_samples: int,
    compiler: dict,
    panel_path: Path,
    candidate: Path = CANDIDATE,
    candidate_sha256: str = CANDIDATE_SHA256,
    runner: Path = RUNNER,
    evidence_boundary: str = (
        "continued-referee engineering gate on already-consumed official maps; "
        "not an Arena predictor"
    ),
) -> dict:
    expected = maps * 2 * len(OPPONENTS)
    keys = {(row["map_seed"], row["seat"], row["opponent"]) for row in rows}
    if len(rows) != expected or len(keys) != expected:
        raise RuntimeError(
            f"panel coverage mismatch: rows={len(rows)}, unique={len(keys)}, expected={expected}"
        )
    if set(row["opponent"] for row in rows) != set(OPPONENTS):
        raise RuntimeError("opponent-family identity mismatch")

    family_means = {
        family: statistics.mean(
            row["delta"] for row in rows if row["opponent"] == family
        )
        for family in OPPONENTS
    }
    seat_means = {
        str(seat): statistics.mean(row["delta"] for row in rows if row["seat"] == seat)
        for seat in (0, 1)
    }
    baseline_catastrophes = sum(row["baseline_margin"] <= -100 for row in rows)
    candidate_catastrophes = sum(row["candidate_margin"] <= -100 for row in rows)
    baseline_negative_mass = sum(
        -row["baseline_margin"] for row in rows if row["baseline_margin"] < 0
    )
    candidate_negative_mass = sum(
        -row["candidate_margin"] for row in rows if row["candidate_margin"] < 0
    )
    baseline_training = [row for row in rows if row["baseline_train_turn"] is not None]
    candidate_training_on_baseline = [
        row for row in baseline_training if row["candidate_train_turn"] is not None
    ]
    training_delays = [
        row["candidate_train_turn"] - row["baseline_train_turn"]
        for row in candidate_training_on_baseline
    ]
    lower = bootstrap_lower(rows, bootstrap_samples)
    latency_ratio = (
        latency["candidate"]["p95_ns"] / latency["baseline"]["p95_ns"]
        if latency["baseline"]["p95_ns"]
        else None
    )
    gates = {
        "coverage_at_least_512": len(rows) >= 512,
        "six_families": len(family_means) == 6,
        "zero_critical": sum(
            row["baseline_critical"] + row["candidate_critical"] for row in rows
        ) == 0,
        "zero_unclassified": sum(
            row["baseline_unclassified"] + row["candidate_unclassified"] for row in rows
        ) == 0,
        "mean_delta_at_least_minus_0_5": mean(rows, "delta") >= -0.5,
        "bootstrap_lower_above_minus_2": lower > -2.0,
        "catastrophes_not_increased": candidate_catastrophes <= baseline_catastrophes,
        "negative_mass_not_increased": candidate_negative_mass <= baseline_negative_mass,
        "five_of_six_family_means_nonnegative": sum(
            value >= 0 for value in family_means.values()
        ) >= 5,
        "both_seat_means_nonnegative": all(value >= 0 for value in seat_means.values()),
        "worker2_coverage_at_least_95pct": (
            len(candidate_training_on_baseline) / len(baseline_training) >= 0.95
            if baseline_training
            else False
        ),
        "median_worker2_delay_at_most_10": (
            statistics.median(training_delays) <= 10 if training_delays else False
        ),
        "latency_p95_at_most_120pct": latency_ratio is not None and latency_ratio <= 1.2,
        "latency_max_below_50ms": latency["candidate"]["maximum_ms"] < 50,
    }
    full_panel = len(rows) >= 512
    return {
        "schema": "troll-farm-e7a-half-size-open-panel-v1",
        "evidence_boundary": evidence_boundary,
        "inputs": {
            "baseline": {
                "path": str(BASELINE.relative_to(REPO)),
                "bytes": BASELINE.stat().st_size,
                "sha256": BASELINE_SHA256,
            },
            "candidate": {
                "path": str(candidate.relative_to(REPO)),
                "bytes": candidate.stat().st_size,
                "sha256": candidate_sha256,
            },
            "sacred_sha256": SACRED_SHA256,
            "runner": str(runner.relative_to(REPO)),
            "compiler": compiler,
            "panel_tsv": str(panel_path),
        },
        "panel": {
            "start_seed": min(row["map_seed"] for row in rows),
            "maps": maps,
            "tasks": len(rows),
            "opponents": list(OPPONENTS),
            "seats": [0, 1],
            "bootstrap_samples": bootstrap_samples,
        },
        "metrics": {
            "mean_margin_delta": mean(rows, "delta"),
            "bootstrap_95_lower": lower,
            "family_mean_delta": family_means,
            "seat_mean_delta": seat_means,
            "mean_score": {
                "baseline": mean(rows, "baseline_score"),
                "candidate": mean(rows, "candidate_score"),
            },
            "mean_opponent_score": {
                "baseline": mean(rows, "baseline_opponent_score"),
                "candidate": mean(rows, "candidate_opponent_score"),
            },
            "catastrophes": {
                "baseline": baseline_catastrophes,
                "candidate": candidate_catastrophes,
            },
            "negative_margin_mass": {
                "baseline": baseline_negative_mass,
                "candidate": candidate_negative_mass,
            },
            "training": {
                "baseline_games": len(baseline_training),
                "candidate_on_baseline_games": len(candidate_training_on_baseline),
                "coverage": (
                    len(candidate_training_on_baseline) / len(baseline_training)
                    if baseline_training
                    else None
                ),
                "median_delay": statistics.median(training_delays)
                if training_delays
                else None,
            },
            "period2_ge6": {
                "baseline": sum(row["baseline_period2"] >= 6 for row in rows),
                "candidate": sum(row["candidate_period2"] >= 6 for row in rows),
            },
            "maximum_period2": {
                "baseline": max(row["baseline_period2"] for row in rows),
                "candidate": max(row["candidate_period2"] for row in rows),
            },
            "issues": {
                "baseline": sum(row["baseline_issues"] for row in rows),
                "candidate": sum(row["candidate_issues"] for row in rows),
            },
            "latency": {**latency, "candidate_p95_ratio": latency_ratio},
        },
        "gates": gates,
        "verdict": (
            "QUALIFIED_OPEN_PANEL"
            if full_panel and all(gates.values())
            else "SMOKE_ONLY"
            if not full_panel
            else "REJECTED_OPEN_PANEL"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=OPEN_START)
    parser.add_argument("--maps", type=int, required=True)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--bootstrap", type=int, default=50_000)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if not (OPEN_START <= arguments.start < arguments.start + arguments.maps <= OPEN_END):
        parser.error("range must stay inside the consumed A2-0b calibration maps")
    if arguments.threads <= 0 or arguments.bootstrap <= 0:
        parser.error("threads and bootstrap must be positive")

    with tempfile.TemporaryDirectory(prefix="e7a-half-open-panel-") as temporary:
        binary, compiler = compile_runner(Path(temporary))
        completed = subprocess.run(
            [
                str(binary),
                str(arguments.start),
                str(arguments.maps),
                str(arguments.panel),
                str(arguments.threads),
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=3600,
        )
        if completed.returncode:
            raise RuntimeError(f"panel failed:\n{completed.stderr[-12000:]}")
        run_stderr = completed.stderr.strip()

    rows, latency = parse_panel(arguments.panel)
    result = analyze(
        rows,
        latency,
        maps=arguments.maps,
        bootstrap_samples=arguments.bootstrap,
        compiler=compiler,
        panel_path=arguments.panel,
    )
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
