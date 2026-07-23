#!/usr/bin/env python3
"""Validate the slim crop candidate against the frozen research controller.

This gate consumes no new outcome data.  It reuses Phase-17 seeds only to
prove source specialization, command-stream parity, and local latency.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.make_opponent_crop_candidate import (  # noqa: E402
    make_candidate,
    OUTPUT as CANDIDATE,
    PARENT,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402


RESIDENT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
RESEARCH = REPO / "rust/src/bin/yamo_orchard_live.rs"
OPPONENTS = {
    "ringfix3": REPO / "cgauto/submissions/v1.59.0-ringfix3.min.rs",
    "taskplan": REPO / "cgauto/submissions/v1.27.0-taskplan.min.rs",
}
DYNAMIC_CELLS = tuple(
    (seed, seat, "ringfix3" if seat == 0 else "taskplan")
    for seed in range(1300, 1308)
    for seat in (0, 1)
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def activate_research_source(source: str) -> str:
    before = "    let mut bot = SecureOrchardBot::new();"
    after = (
        "    let mut bot = "
        "SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1);"
    )
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one research main anchor, found {count}")
    return source.replace(before, after, 1)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot take percentile of an empty list")
    return ordered[round((len(ordered) - 1) * fraction)]


def capture_reference_stream(
    reference: Path, opponent: Path, seed: int, seat: int
) -> dict:
    game = generate_bronze(seed)
    initial = copy.deepcopy(game)
    binaries = [reference, opponent] if seat == 0 else [opponent, reference]
    sessions = [BotSession(binaries[index], game, index) for index in (0, 1)]
    turn_blocks = []
    reference_lines = []
    turns_until_end = 0
    try:
        while game.turn <= 300:
            turn_blocks.append(turn_text(game, seat))
            raw = [session.command(game) for session in sessions]
            reference_lines.append(raw[seat])
            commands = [action_commands(line) for line in raw]
            step(game, commands[0], commands[1])
            ended, turns_until_end = has_stalled(game, turns_until_end)
            if ended:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError(f"reference stream wrote stderr: {stderrs}")
    return {
        "grid": grid_text(initial, seat),
        "turn_blocks": turn_blocks,
        "reference_lines": reference_lines,
        "terminal_turn": game.turn - 1,
    }


def replay_interactive(binary: Path, grid: str, turn_blocks: list[str]) -> dict:
    process = subprocess.Popen(
        [binary],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdin is not None and process.stdout is not None
    process.stdin.write(grid)
    process.stdin.flush()
    lines = []
    elapsed_ms = []
    for block in turn_blocks:
        started = time.perf_counter()
        process.stdin.write(block)
        process.stdin.flush()
        line = process.stdout.readline()
        elapsed_ms.append((time.perf_counter() - started) * 1000)
        if not line:
            stderr = process.stderr.read() if process.stderr else ""
            raise RuntimeError(
                f"{binary.name} produced no output (exit={process.poll()}): {stderr[:500]}"
            )
        lines.append(line.rstrip("\r\n"))
    process.stdin.close()
    returncode = process.wait(timeout=30)
    stderr = process.stderr.read() if process.stderr else ""
    if returncode:
        raise RuntimeError(f"{binary.name} exited {returncode}: {stderr[:500]}")
    return {"lines": lines, "elapsed_ms": elapsed_ms, "stderr": stderr}


def first_turn_gate(resident: Path, candidate: Path) -> dict:
    mismatches = []
    for seed in range(1300, 1360):
        game = generate_bronze(seed)
        for seat in (0, 1):
            stream = grid_text(game, seat) + turn_text(game, seat)
            resident_lines, resident_stderr = run_batch(resident, stream)
            candidate_lines, candidate_stderr = run_batch(candidate, stream)
            if resident_stderr or candidate_stderr:
                raise RuntimeError("first-turn source unexpectedly wrote stderr")
            if len(resident_lines) != 1 or len(candidate_lines) != 1:
                raise RuntimeError("first-turn source did not emit exactly one line")
            if action_commands(resident_lines[0]) != action_commands(candidate_lines[0]):
                mismatches.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "resident": action_commands(resident_lines[0]),
                        "candidate": action_commands(candidate_lines[0]),
                    }
                )
    return {"cells": 120, "mismatches": mismatches, "passed": not mismatches}


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/"
        "opponent-crop-candidate-local-gate-2026-07-18.json",
    )
    args = parser.parse_args()

    expected_candidate = make_candidate(PARENT.read_text())
    if CANDIDATE.read_text() != expected_candidate:
        raise RuntimeError("candidate artifact does not match the fail-closed generator")
    sidecar = CANDIDATE.with_name(CANDIDATE.name + ".sha256").read_text().strip()
    expected_sidecar = f"{digest(CANDIDATE)}  {CANDIDATE.name}"
    if sidecar != expected_sidecar:
        raise RuntimeError("candidate SHA-256 sidecar mismatch")
    if CANDIDATE.stat().st_size >= 100_000:
        raise RuntimeError("candidate exceeds the 100,000-byte source limit")

    with tempfile.TemporaryDirectory(prefix="crop-candidate-gate-") as directory:
        temp = Path(directory)
        activated_source = temp / "activated_research.rs"
        activated_source.write_text(activate_research_source(RESEARCH.read_text()))
        binaries = {
            "candidate": temp / "candidate",
            "resident": temp / "resident",
            "reference": temp / "reference",
        }
        compile_source(CANDIDATE, binaries["candidate"], "crop_gate_candidate")
        compile_source(RESIDENT, binaries["resident"], "crop_gate_resident")
        compile_source(activated_source, binaries["reference"], "crop_gate_reference")
        for name, source in OPPONENTS.items():
            binaries[name] = temp / name
            compile_source(source, binaries[name], f"crop_gate_{name}")

        first_turn = first_turn_gate(binaries["resident"], binaries["candidate"])
        dynamic = []
        latencies = []
        for seed, seat, opponent in DYNAMIC_CELLS:
            stream = capture_reference_stream(
                binaries["reference"], binaries[opponent], seed, seat
            )
            candidate = replay_interactive(
                binaries["candidate"], stream["grid"], stream["turn_blocks"]
            )
            resident = replay_interactive(
                binaries["resident"], stream["grid"], stream["turn_blocks"]
            )
            exact = candidate["lines"] == stream["reference_lines"]
            if not exact:
                first = next(
                    index
                    for index, (actual, expected) in enumerate(
                        zip(candidate["lines"], stream["reference_lines"]), 1
                    )
                    if actual != expected
                )
                raise RuntimeError(
                    f"slim/reference stream mismatch seed={seed} seat={seat} turn={first}"
                )
            if candidate["stderr"]:
                raise RuntimeError("candidate unexpectedly wrote to stderr")
            divergence = next(
                (
                    turn
                    for turn, (candidate_line, resident_line) in enumerate(
                        zip(candidate["lines"], resident["lines"]), 1
                    )
                    if action_commands(candidate_line) != action_commands(resident_line)
                ),
                None,
            )
            latencies.extend(candidate["elapsed_ms"])
            dynamic.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "turns": len(candidate["lines"]),
                    "terminal_turn": stream["terminal_turn"],
                    "exact_reference_stream": exact,
                    "first_resident_divergence_turn": divergence,
                }
            )

    latency = {
        "commands": len(latencies),
        "mean_ms": statistics.mean(latencies),
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "maximum_ms": max(latencies),
        "p95_limit_ms": 20,
        "maximum_limit_ms": 100,
    }
    latency["passed"] = (
        latency["p95_ms"] <= latency["p95_limit_ms"]
        and latency["maximum_ms"] <= latency["maximum_limit_ms"]
    )
    dynamic_passed = all(row["exact_reference_stream"] for row in dynamic)
    passed = first_turn["passed"] and dynamic_passed and latency["passed"]
    payload = {
        "schema": 1,
        "scope": (
            "local candidate packaging/parity/latency gate on consumed Phase-17 seeds; "
            "not an outcome discriminator and not an arena result"
        ),
        "sources": {
            "parent": {"path": str(PARENT.relative_to(REPO)), "sha256": digest(PARENT)},
            "resident": {
                "path": str(RESIDENT.relative_to(REPO)),
                "bytes": RESIDENT.stat().st_size,
                "sha256": digest(RESIDENT),
            },
            "candidate": {
                "path": str(CANDIDATE.relative_to(REPO)),
                "bytes": CANDIDATE.stat().st_size,
                "sha256": digest(CANDIDATE),
            },
            "research": str(RESEARCH.relative_to(REPO)),
        },
        "fixed_treatment": {
            "bonus": 100,
            "eta_limit": 6,
            "start_turn": 1,
            "minimum_seen": 1,
        },
        "first_turn_resident_parity": first_turn,
        "dynamic_reference_parity": {
            "streams": len(dynamic),
            "exact_streams": sum(row["exact_reference_stream"] for row in dynamic),
            "activated_streams": sum(
                row["first_resident_divergence_turn"] is not None for row in dynamic
            ),
            "rows": dynamic,
            "passed": dynamic_passed,
        },
        "interactive_latency": latency,
        "verdict": "PASS" if passed else "FAIL",
    }
    save(args.output, payload)
    print(
        f"{payload['verdict']}: {CANDIDATE.stat().st_size} bytes, "
        f"turn1={120-len(first_turn['mismatches'])}/120, "
        f"dynamic={sum(row['exact_reference_stream'] for row in dynamic)}/{len(dynamic)}, "
        f"activated={payload['dynamic_reference_parity']['activated_streams']}, "
        f"p95={latency['p95_ms']:.3f} ms, max={latency['maximum_ms']:.3f} ms"
    )
    print(f"saved {args.output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
