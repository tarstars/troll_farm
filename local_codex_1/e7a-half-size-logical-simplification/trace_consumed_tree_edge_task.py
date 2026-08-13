#!/usr/bin/env python3
"""Trace one declared candidate on one consumed 9,866,000--042 task.

This diagnostic cannot qualify a source. It derives a temporary runner from the
hash-locked tree-edge panel, restricts execution to one explicit consumed task, and
records candidate-side state plus both command lists before every referee step.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

import evaluate_fresh_tree_edge_reversal_gate as gate
import evaluate_open_panel as shared


REPO = Path(__file__).resolve().parents[2]
CONSUMED_START = 9_866_000
CONSUMED_END = 9_866_043


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def traced_runner_source(seed: int, seat: int, opponent: int) -> str:
    source = gate.fresh_runner_source()
    relative_snapshot = '#[path = "../../rust/src/d171a_control_resident_snapshot.rs"]'
    absolute_snapshot = (
        f'#[path = "{REPO / "rust/src/d171a_control_resident_snapshot.rs"}"]'
    )
    if source.count(relative_snapshot) != 1:
        raise RuntimeError("runner resident snapshot path changed")
    source = source.replace(relative_snapshot, absolute_snapshot, 1)
    task_block = r"""    let tasks: Vec<Task> = (start..start + maps).flat_map(|map_seed| {
        (0..2).flat_map(move |seat| {
            (0..OPPONENTS).map(move |opponent| Task { map_seed, seat, opponent })
        })
    }).collect();
"""
    one_task = (
        "    let tasks: Vec<Task> = vec![Task { "
        f"map_seed: {seed}, seat: {seat}, opponent: {opponent} "
        "}];\n"
    )
    if source.count(task_block) != 1:
        raise RuntimeError("runner task block changed")
    source = source.replace(task_block, one_task, 1)

    command_marker = r"""        let theirs = opponent.commands(&referee.game, opponent_seat);
        let commands = if task.seat == 0 { [ours, theirs] } else { [theirs, ours] };
"""
    trace_block = r"""        let theirs = opponent.commands(&referee.game, opponent_seat);
        let trace_arm = match arm { Arm::Baseline => "baseline", Arm::Candidate => "candidate" };
        let our_units: Vec<_> = referee.game.units.iter()
            .filter(|unit| unit.player as usize == task.seat)
            .map(|unit| (unit.id, unit.pos(), unit.ms, unit.cc, unit.hp, unit.chop, unit.carry))
            .collect();
        let opponent_units: Vec<_> = referee.game.units.iter()
            .filter(|unit| unit.player as usize == opponent_seat)
            .map(|unit| (unit.id, unit.pos(), unit.ms, unit.cc, unit.hp, unit.chop, unit.carry))
            .collect();
        let plants: Vec<_> = referee.game.plants.iter()
            .map(|plant| (&plant.plant_type, plant.pos(), plant.health, plant.fruits))
            .collect();
        eprintln!(
            "TRACE\t{}\t{}\t{}\t{}\t{}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{}\t{:?}",
            trace_arm,
            task.map_seed,
            task.seat,
            task.opponent,
            turn,
            ours,
            theirs,
            our_units,
            opponent_units,
            referee.game.inventories[task.seat],
            referee.game.inventories[opponent_seat],
            referee.game.scores,
            referee.game.plants.len(),
            plants,
        );
        let commands = if task.seat == 0 { [ours, theirs] } else { [theirs, ours] };
"""
    if source.count(command_marker) != 1:
        raise RuntimeError("runner command marker changed")
    return source.replace(command_marker, trace_block, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--opponent", type=int, choices=range(6), required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.candidate = arguments.candidate.resolve()
    if not CONSUMED_START <= arguments.seed < CONSUMED_END:
        parser.error("seed is outside the already-consumed diagnostic range")
    if arguments.output.exists():
        parser.error("trace output already exists")
    if sha256(arguments.candidate) != arguments.candidate_sha256:
        parser.error("candidate hash mismatch")
    if sha256(shared.BASELINE) != shared.BASELINE_SHA256:
        parser.error("baseline hash mismatch")
    if sha256(shared.SACRED) != shared.SACRED_SHA256:
        parser.error("sacred source hash mismatch")
    if not shared.RUST_LIBRARY.is_file():
        parser.error("release Rust library is missing")

    with tempfile.TemporaryDirectory(prefix="e7a-half-consumed-tree-edge-trace-") as temporary:
        directory = Path(temporary)
        baseline_module = directory / "baseline_module.rs"
        candidate_module = directory / "candidate_module.rs"
        runner = directory / "trace_runner.rs"
        binary = directory / "trace_runner"
        panel = directory / "single-task.tsv"
        baseline_module.write_text(
            shared.module_source(shared.BASELINE.read_text(), "baseline")
        )
        candidate_module.write_text(
            shared.module_source(arguments.candidate.read_text(), "candidate")
        )
        runner.write_text(
            traced_runner_source(arguments.seed, arguments.seat, arguments.opponent)
        )
        environment = dict(os.environ)
        environment.update(
            {
                "E7A_HALF_BASELINE_MODULE": str(baseline_module),
                "E7A_HALF_CANDIDATE_MODULE": str(candidate_module),
            }
        )
        compiled = subprocess.run(
            [
                "rustc",
                "--crate-name",
                "e7a_half_consumed_tree_edge_task_trace",
                "--edition=2021",
                "-C",
                "opt-level=3",
                "-C",
                "overflow-checks=off",
                "-A",
                "warnings",
                str(runner),
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
        if compiled.returncode:
            raise RuntimeError(compiled.stderr[:12000])
        completed = subprocess.run(
            [str(binary), str(arguments.seed), "1", str(panel), "1"],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=600,
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr[-12000:])
        trace = "\n".join(
            line for line in completed.stderr.splitlines() if line.startswith("TRACE\t")
        )
        arguments.output.write_text(trace + "\n")
        print(panel.read_text().splitlines()[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
