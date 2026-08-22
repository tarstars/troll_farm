#!/usr/bin/env python3
"""Validate bounded banana-ring packaging, parity, tests, and latency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source
from cgauto.make_banana_ring_b100_candidate import (
    BuildError,
    CONTROL_REL,
    SOURCE_REL,
    build,
)
from cgauto.slim_banana_ring_b100_candidate import make_slim_candidate
from cgauto.validate_opponent_crop_candidate import (
    capture_reference_stream,
    percentile,
    replay_interactive,
)


RESEARCH = REPO / "local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.research.rs"
COMPACT = REPO / "local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.compact.rs"
CANDIDATE = REPO / "local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.arena.rs"
OPPONENTS = {
    "ringfix3": REPO / "cgauto/submissions/v1.59.0-ringfix3.min.rs",
    "taskplan": REPO / "cgauto/submissions/v1.27.0-taskplan.min.rs",
}
CELLS = tuple(
    (seed, seat, "ringfix3" if seat == 0 else "taskplan")
    for seed in range(1300, 1304)
    for seat in (0, 1)
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_tests(source: Path, directory: Path) -> dict:
    binary = directory / "semantic-tests"
    compile_result = subprocess.run(
        [
            "rustc",
            "--edition=2021",
            "--crate-name=banana_ring_semantic_tests",
            "--test",
            "-O",
            str(source),
            "-o",
            str(binary),
        ],
        capture_output=True,
        text=True,
    )
    if compile_result.returncode:
        raise RuntimeError(f"semantic test compilation failed:\n{compile_result.stderr}")
    result = subprocess.run([binary], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f"semantic tests failed:\n{result.stdout}\n{result.stderr}")
    summary = next(
        (line for line in result.stdout.splitlines() if line.startswith("test result:")),
        "",
    )
    if "39 passed; 0 failed" not in summary:
        raise RuntimeError(f"unexpected semantic test summary: {summary}")
    return {"passed": 39, "failed": 0, "summary": summary}


def mutated_parent_gate(directory: Path) -> bool:
    fake = directory / "mutated-repo"
    (fake / SOURCE_REL.parent).mkdir(parents=True)
    (fake / CONTROL_REL.parent).mkdir(parents=True)
    source = (REPO / SOURCE_REL).read_bytes()
    (fake / SOURCE_REL).write_bytes(source + b"\n")
    shutil.copyfile(REPO / CONTROL_REL, fake / CONTROL_REL)
    try:
        build(fake, directory / "mutated-output")
    except BuildError:
        return True
    return False


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if CANDIDATE.stat().st_size >= 100_000:
        raise RuntimeError("candidate exceeds the Arena source limit")
    sidecar = CANDIDATE.with_name(CANDIDATE.name + ".sha256").read_text().strip()
    if sidecar != f"{digest(CANDIDATE)}  {CANDIDATE.name}":
        raise RuntimeError("candidate hash sidecar mismatch")
    if make_slim_candidate(COMPACT.read_text()) != CANDIDATE.read_text():
        raise RuntimeError("candidate does not match the fail-closed slimmer")

    with tempfile.TemporaryDirectory(prefix="banana-ring-gate-") as raw_directory:
        directory = Path(raw_directory)
        generated = build(REPO, directory / "generated")
        if (directory / "generated/banana-ring-b100-e6.research.rs").read_bytes() != RESEARCH.read_bytes():
            raise RuntimeError("checked-in research artifact differs from fresh generation")
        if (directory / "generated/banana-ring-b100-e6.compact.rs").read_bytes() != COMPACT.read_bytes():
            raise RuntimeError("checked-in compact artifact differs from fresh generation")
        tests = run_tests(RESEARCH, directory)
        mutated_rejected = mutated_parent_gate(directory)
        if not mutated_rejected:
            raise RuntimeError("mutated byte-sacred parent was accepted")

        binaries = {
            "research": directory / "research",
            "candidate": directory / "candidate",
        }
        compile_source(RESEARCH, binaries["research"], "banana_ring_research")
        compile_source(CANDIDATE, binaries["candidate"], "banana_ring_candidate")
        for name, source in OPPONENTS.items():
            binaries[name] = directory / name
            compile_source(source, binaries[name], f"banana_ring_{name}")

        empty = subprocess.run(
            [binaries["candidate"]], input="", capture_output=True, text=True, timeout=10
        )
        if empty.returncode or empty.stdout or empty.stderr:
            raise RuntimeError("candidate failed empty-input/zero-stderr gate")

        rows = []
        latencies = []
        total_commands = 0
        for seed, seat, opponent in CELLS:
            stream = capture_reference_stream(
                binaries["research"], binaries[opponent], seed, seat
            )
            candidate = replay_interactive(
                binaries["candidate"], stream["grid"], stream["turn_blocks"]
            )
            if candidate["stderr"]:
                raise RuntimeError("candidate wrote runtime stderr")
            if candidate["lines"] != stream["reference_lines"]:
                first = next(
                    turn
                    for turn, pair in enumerate(
                        zip(candidate["lines"], stream["reference_lines"]), 1
                    )
                    if pair[0] != pair[1]
                )
                raise RuntimeError(
                    f"research/Arena mismatch seed={seed} seat={seat} turn={first}"
                )
            latencies.extend(candidate["elapsed_ms"])
            total_commands += len(candidate["lines"])
            rows.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "turns": len(candidate["lines"]),
                    "terminal_turn": stream["terminal_turn"],
                    "exact": True,
                }
            )

    latency = {
        "commands": len(latencies),
        "mean_ms": statistics.mean(latencies),
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "maximum_ms": max(latencies),
        "p95_gate_ms": 2.0,
        "maximum_gate_ms": 10.0,
    }
    latency["passed"] = latency["p95_ms"] < 2.0 and latency["maximum_ms"] < 10.0
    payload = {
        "schema": 1,
        "status": "MECHANICALLY_READY" if latency["passed"] else "CLOSED",
        "candidate": {
            "path": str(CANDIDATE.relative_to(REPO)),
            "bytes": CANDIDATE.stat().st_size,
            "sha256": digest(CANDIDATE),
        },
        "fresh_generation": generated,
        "gates": {
            "semantic_tests": tests,
            "mutated_parent_rejected": mutated_rejected,
            "standalone_compile": "PASS",
            "empty_input_zero_stderr": "PASS",
            "stream_equality": {
                "streams": len(rows),
                "exact_streams": sum(row["exact"] for row in rows),
                "commands": total_commands,
                "rows": rows,
            },
            "latency": latency,
        },
    }
    save(args.output, payload)
    print(
        f"{payload['status']}: {CANDIDATE.stat().st_size} bytes, tests=39/39, "
        f"streams={len(rows)}/{len(rows)}, commands={total_commands}, "
        f"p95={latency['p95_ms']:.3f} ms, max={latency['maximum_ms']:.3f} ms"
    )
    return 0 if payload["status"] == "MECHANICALLY_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
