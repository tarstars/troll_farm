#!/usr/bin/env python3
"""Reproduce source, timing, selector-label, and dynamic-stream gates for the rollout bot."""

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
    BotSession,
    action_commands,
    compile_source,
    grid_text,
    turn_text,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402


SUBMISSIONS = REPO / "cgauto/submissions"
CANDIDATE = SUBMISSIONS / "candidate-agent6553250-compact-gold-rollout30.min.rs"
CONTROL = SUBMISSIONS / "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
OPTION = SUBMISSIONS / "candidate-agent6553250-adaptive-max-bank-first-hp0.min.rs"
LABELS = REPO / "data/analysis/live-agent-6553250/local-model-rollouts-120-179.tsv"
OPPONENTS = {
    "ringfix3": SUBMISSIONS / "v1.59.0-ringfix3.min.rs",
    "taskplan": SUBMISSIONS / "v1.27.0-taskplan.min.rs",
}
DYNAMIC_CASES = (
    (120, 1),
    (143, 1),
    (163, 0),
    (179, 0),
    (121, 0),
    (121, 1),
    (157, 0),
    (157, 1),
    (178, 0),
    (179, 1),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gold_labels(path: Path) -> dict[tuple[int, int], bool]:
    labels = {}
    with path.open() as handle:
        header = handle.readline().rstrip().split("\t")
        for line in handle:
            row = dict(zip(header, line.rstrip().split("\t"), strict=True))
            if row["model"] == "gold_elite":
                labels[(int(row["seed"]), int(row["seat"]))] = float(row["delta"]) > 30
    return labels


def first_command(binary: Path, text: str) -> tuple[str, float]:
    started = time.perf_counter()
    result = subprocess.run(
        [binary], input=text, capture_output=True, text=True, timeout=10
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    if result.returncode:
        raise RuntimeError(
            f"{binary.name} exited {result.returncode}: {result.stderr[:500]}"
        )
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise RuntimeError(f"{binary.name} produced {len(lines)} first-turn lines")
    return lines[0], elapsed_ms


def dynamic_trace(ours: Path, opponent: Path, seed: int, seat: int) -> dict:
    game = generate_bronze(seed)
    binaries = [ours, opponent] if seat == 0 else [opponent, ours]
    sessions = [BotSession(binaries[index], game, index) for index in (0, 1)]
    turns = []
    turns_until_end = 0
    try:
        while game.turn <= 300:
            raw = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in raw]
            turns.append([raw[seat], raw[1 - seat]])
            step(game, commands[0], commands[1])
            ended, turns_until_end = has_stalled(game, turns_until_end)
            if ended:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    return {
        "turns": turns,
        "terminal_turn": game.turn - 1,
        "scores": list(game.scores),
        "inventories": copy.deepcopy(game.inventories),
        "stderrs": stderrs,
    }


def percentile(values: list[float], fraction: float) -> float:
    return values[round((len(values) - 1) * fraction)]


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
        / "data/analysis/live-agent-6553250/compact-gold-rollout-live-gate-2026-07-17.json",
    )
    args = parser.parse_args()
    labels = gold_labels(LABELS)
    if sorted(labels) != [(seed, seat) for seed in range(120, 180) for seat in (0, 1)]:
        raise SystemExit("label registry does not exactly cover seeds 120..179, both seats")

    with tempfile.TemporaryDirectory(prefix="rollout-live-gate-") as directory:
        temp = Path(directory)
        binaries = {
            "candidate": temp / "candidate",
            "control": temp / "control",
            "option": temp / "option",
        }
        for name, source in (
            ("candidate", CANDIDATE),
            ("control", CONTROL),
            ("option", OPTION),
        ):
            compile_source(source, binaries[name], f"rollout_gate_{name}")
        for name, source in OPPONENTS.items():
            binaries[name] = temp / name
            compile_source(source, binaries[name], f"rollout_gate_{name}")

        timing = []
        mismatches = []
        first_command_distinguished = []
        for seed in range(120, 180):
            game = generate_bronze(seed)
            for seat in (0, 1):
                input_text = grid_text(game, seat) + turn_text(game, seat)
                control, _ = first_command(binaries["control"], input_text)
                option, _ = first_command(binaries["option"], input_text)
                actual, elapsed_ms = first_command(binaries["candidate"], input_text)
                use_option = labels[(seed, seat)]
                expected = option if use_option else control
                timing.append(elapsed_ms)
                if control != option:
                    first_command_distinguished.append([seed, seat])
                if actual != expected:
                    mismatches.append(
                        {
                            "seed": seed,
                            "seat": seat,
                            "expected_policy": "option" if use_option else "control",
                            "control": control,
                            "option": option,
                            "actual": actual,
                        }
                    )
        if mismatches:
            raise RuntimeError(f"{len(mismatches)} frozen selector command mismatches")

        dynamic_rows = []
        selected = {cell for cell, use_option in labels.items() if use_option}
        for index, (seed, seat) in enumerate(DYNAMIC_CASES):
            policy = "option" if (seed, seat) in selected else "control"
            opponent = tuple(OPPONENTS)[index % len(OPPONENTS)]
            actual = dynamic_trace(binaries["candidate"], binaries[opponent], seed, seat)
            expected = dynamic_trace(binaries[policy], binaries[opponent], seed, seat)
            exact = actual == expected
            dynamic_rows.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "expected_policy": policy,
                    "opponent": opponent,
                    "turns": len(actual["turns"]),
                    "exact": exact,
                }
            )
            if not exact:
                raise RuntimeError(f"dynamic stream mismatch on seed {seed}, seat {seat}")

    timing.sort()
    payload = {
        "schema": 1,
        "scope": (
            "local exact-engine deployment gate; frozen 120..179 Gold labels; "
            "not an arena result"
        ),
        "sources": {
            "candidate": {"path": str(CANDIDATE.relative_to(REPO)), "sha256": digest(CANDIDATE)},
            "control": {"path": str(CONTROL.relative_to(REPO)), "sha256": digest(CONTROL)},
            "option": {"path": str(OPTION.relative_to(REPO)), "sha256": digest(OPTION)},
            "labels": str(LABELS.relative_to(REPO)),
        },
        "source_bytes": CANDIDATE.stat().st_size,
        "source_limit_bytes": 100_000,
        "first_turn_limit_ms": 1000,
        "internal_rollout_deadline_ms": 700,
        "selector": {
            "model": "CompactGold (exact GoldElite::new command parity)",
            "rule": "option terminal margin - control terminal margin > 30",
            "frozen_cells": len(labels),
            "selected_cells": [list(cell) for cell in sorted(selected)],
            "command_mismatches": mismatches,
            "first_command_distinguished_cells": len(first_command_distinguished),
        },
        "first_turn_wall_ms": {
            "n": len(timing),
            "mean": statistics.mean(timing),
            "p50": percentile(timing, 0.50),
            "p95": percentile(timing, 0.95),
            "maximum": max(timing),
        },
        "dynamic_stream_gate": {
            "cases": dynamic_rows,
            "exact_cases": sum(row["exact"] for row in dynamic_rows),
        },
        "verdict": "PASS",
    }
    save(args.output, payload)
    print(
        f"PASS: {len(labels)} frozen cells, {len(dynamic_rows)} dynamic streams, "
        f"p95={payload['first_turn_wall_ms']['p95']:.2f} ms, {CANDIDATE.stat().st_size} bytes"
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
