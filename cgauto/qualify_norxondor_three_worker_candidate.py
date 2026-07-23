#!/usr/bin/env python3
"""Apply the frozen standalone qualification gates to the three-worker candidate."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time


REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-norxondor-three-worker-silver.min.rs"
)
DEFAULT_FORMATTED_BINARY = REPO / "rust/target/release/norxondor_three_worker_live"
DEFAULT_PARITY = (
    REPO
    / "data/analysis/live-agent-6553250/norxondor-three-worker-parity-0-29.tsv"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "norxondor-three-worker-standalone-qualification-2026-07-19.json"
)
OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}


def load_protocol_builder():
    path = REPO / "rust/parity.py"
    spec = importlib.util.spec_from_file_location("troll_farm_parity", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build_full_input


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, (len(ordered) * int(fraction * 100) + 99) // 100 - 1)
    return ordered[index]


def analyze_parity(path: Path) -> dict:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    identities = {
        (int(row["seed"]), row["opponent"], int(row["seat"])) for row in rows
    }
    expected = {
        (seed, opponent, seat)
        for seed in range(30)
        for opponent in OPPONENTS
        for seat in range(2)
    }
    decisions = sum(int(row["decisions"]) for row in rows)
    elapsed_ns = sum(int(row["elapsed_ns"]) for row in rows)
    per_match_p95_ms = [int(row["p95_ns"]) / 1_000_000 for row in rows]
    maximum_ms = max(int(row["max_ns"]) for row in rows) / 1_000_000
    workers = [int(row["workers"]) for row in rows]
    return {
        "path": str(path),
        "rows": len(rows),
        "unique_rows": len(identities),
        "expected_grid": identities == expected,
        "decisions": decisions,
        "weighted_mean_decision_ms": elapsed_ns / decisions / 1_000_000,
        "median_match_p95_ms": statistics.median(per_match_p95_ms),
        "maximum_match_p95_ms": max(per_match_p95_ms),
        "maximum_decision_ms": maximum_ms,
        "three_worker_terminal_matches": sum(worker >= 3 for worker in workers),
        "minimum_terminal_workers": min(workers),
        "maximum_terminal_workers": max(workers),
        "gates": {
            "exact_480_grid": len(rows) == 480 and identities == expected,
            "p95_at_most_5ms": max(per_match_p95_ms) <= 5.0,
            "maximum_at_most_50ms": maximum_ms <= 50.0,
        },
    }


def run_stream(binary: Path, input_text: str) -> tuple[subprocess.CompletedProcess, float]:
    started = time.perf_counter()
    result = subprocess.run(
        [binary], input=input_text, text=True, capture_output=True, timeout=60
    )
    return result, time.perf_counter() - started


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--formatted-binary", type=Path, default=DEFAULT_FORMATTED_BINARY)
    parser.add_argument("--parity", type=Path, default=DEFAULT_PARITY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.read_bytes()
    source_hash = hashlib.sha256(source).hexdigest()
    sidecar = args.source.with_name(args.source.name + ".sha256").read_text().split()[0]
    parity = analyze_parity(args.parity)
    build_full_input = load_protocol_builder()

    with tempfile.TemporaryDirectory(prefix="norx-three-worker-") as directory:
        candidate_binary = Path(directory) / "candidate"
        compile_result = subprocess.run(
            [
                "rustc",
                "--edition",
                "2021",
                "-O",
                "--crate-name",
                "norxondor_three_worker_candidate",
                args.source,
                "-o",
                candidate_binary,
            ],
            text=True,
            capture_output=True,
        )
        stream_rows = []
        if compile_result.returncode == 0:
            for seed in range(10):
                lines, _ = build_full_input(seed)
                input_text = "\n".join(lines) + "\n"
                candidate, candidate_seconds = run_stream(candidate_binary, input_text)
                formatted, formatted_seconds = run_stream(args.formatted_binary, input_text)
                stream_rows.append(
                    {
                        "seed": seed,
                        "turns": len(candidate.stdout.splitlines()),
                        "candidate_returncode": candidate.returncode,
                        "formatted_returncode": formatted.returncode,
                        "candidate_stderr": candidate.stderr,
                        "formatted_stderr": formatted.stderr,
                        "stdout_identical": candidate.stdout == formatted.stdout,
                        "candidate_seconds": candidate_seconds,
                        "formatted_seconds": formatted_seconds,
                    }
                )

    streams_pass = len(stream_rows) == 10 and all(
        row["turns"] == 300
        and row["candidate_returncode"] == 0
        and row["formatted_returncode"] == 0
        and not row["candidate_stderr"]
        and not row["formatted_stderr"]
        and row["stdout_identical"]
        for row in stream_rows
    )
    gates = {
        "rustc_2021_compile": compile_result.returncode == 0,
        "source_at_most_100000_bytes": len(source) <= 100_000,
        "sidecar_matches": sidecar == source_hash,
        "ten_stream_stdout_parity": streams_pass,
        "complete_match_grid_and_command_parity": parity["gates"]["exact_480_grid"],
        "decision_p95_at_most_5ms": parity["gates"]["p95_at_most_5ms"],
        "decision_maximum_at_most_50ms": parity["gates"]["maximum_at_most_50ms"],
    }
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(args.source),
            "bytes": len(source),
            "sha256": source_hash,
            "sidecar_sha256": sidecar,
        },
        "formatted_binary": str(args.formatted_binary),
        "compile": {
            "returncode": compile_result.returncode,
            "stderr": compile_result.stderr,
        },
        "protocol_streams": stream_rows,
        "protocol_candidate_seconds_p95": percentile(
            [row["candidate_seconds"] for row in stream_rows], 0.95
        )
        if stream_rows
        else None,
        "complete_match_parity": parity,
        "gates": gates,
        "pass": all(gates.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"pass": payload["pass"], "gates": gates, "parity": parity}, indent=1))
    print(f"wrote {args.output}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

