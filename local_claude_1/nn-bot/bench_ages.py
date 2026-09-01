#!/usr/bin/env python3
"""Bench a run's checkpoints at fixed ages, for the gate's scout and confirmation panels.

Gate 1 wants the same fixed updates benched for both arms — scouts at 500…2,500 on the 48-cell
panel, confirmations at 1,500 and 2,500 on the 144-cell locked panel. Doing that by hand is ten
long commands per panel with ten chances to differ in one flag between the arms, which is exactly
the difference the gate is trying to measure. This driver takes the run directory and the list of
ages and produces one bench per age, with the same flags for every arm by construction.

It is deliberately conservative about the machine: benches run at a low priority with a small
thread count each, because on this host they share the cores with training that must not be
starved. A bench whose output already exists is skipped, so the driver can be re-run as more
checkpoints land without repeating work.

    bench_ages.py --checkpoint-dir <run dir> --tag e00b --ages 500,1000,1500,2000,2500 \\
        --panel local_claude_1/third-troll/smoke-maps-seed0.jsonl \\
        --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs \\
        --library rust/target/release/libtroll_farm.so --out-dir <somewhere>
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Iterable

CHECKPOINT_SUFFIX = ".pt"


def checkpoint_for_age(directory: pathlib.Path, age: int) -> pathlib.Path | None:
    """The checkpoint written at exactly `age` updates, whatever the run is called.

    The trainer writes `<run name>-update<six digits>.pt`; the run name is not assumed here so a
    directory holding a salvaged copy (`mid-run-<run name>-update...pt`) resolves just as well.
    Exactly one match is required — two would mean two runs' outputs share a directory, and
    picking either silently would be the kind of mix-up that invalidates a paired comparison.
    """

    needle = f"update{age:06d}{CHECKPOINT_SUFFIX}"
    matches = sorted(p for p in directory.glob(f"*{needle}") if p.is_file())
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(
            f"{directory} holds {len(matches)} checkpoints for update {age}: "
            + ", ".join(p.name for p in matches)
        )
    return matches[0]


def output_path(out_dir: pathlib.Path, tag: str, age: int) -> pathlib.Path:
    return out_dir / f"bench-{tag}-u{age}.json"


def bench_command(
    *,
    checkpoint: pathlib.Path,
    out_json: pathlib.Path,
    panel: str,
    bot: str,
    library: str,
    seed: int,
    train_p: float,
    threads: int,
    nice: int,
    python: str,
    script: str,
    replays: bool,
) -> list[str]:
    """The one command shape every arm and every age share."""

    command = [
        "nice", "-n", str(nice),
        "env", f"OMP_NUM_THREADS={threads}", f"MKL_NUM_THREADS={threads}",
        python, script,
        "--maps", panel,
        "--bot", bot,
        "--library", library,
        "--policy", "network",
        "--checkpoint", str(checkpoint),
        "--both-seats",
        "--seed", str(seed),
        "--train-p", str(train_p),
        "--out", str(out_json),
    ]
    if replays:
        command += ["--replays", str(out_json.with_name(out_json.stem + "-replays.jsonl"))]
    else:
        command += ["--no-replays"]
    return command


def pending_ages(
    directory: pathlib.Path, out_dir: pathlib.Path, tag: str, ages: Iterable[int]
) -> tuple[list[tuple[int, pathlib.Path]], list[int], list[int]]:
    """Split the requested ages into (to run), (already benched), (checkpoint missing)."""

    to_run: list[tuple[int, pathlib.Path]] = []
    done: list[int] = []
    missing: list[int] = []
    for age in ages:
        if output_path(out_dir, tag, age).exists():
            done.append(age)
            continue
        checkpoint = checkpoint_for_age(directory, age)
        if checkpoint is None:
            missing.append(age)
        else:
            to_run.append((age, checkpoint))
    return to_run, done, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--tag", required=True, help="names the outputs: bench-<tag>-u<age>.json")
    parser.add_argument("--ages", default="500,1000,1500,2000,2500")
    parser.add_argument("--panel", required=True)
    parser.add_argument("--bot", required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-p", type=float, default=0.02)
    parser.add_argument("--jobs", type=int, default=2, help="benches running at once")
    parser.add_argument("--threads-per-job", type=int, default=2)
    parser.add_argument("--nice", type=int, default=19)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--script", default=str(pathlib.Path(__file__).with_name("bench.py")))
    parser.add_argument("--no-replays", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    directory = pathlib.Path(args.checkpoint_dir)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ages = [int(one) for one in args.ages.split(",") if one.strip()]

    to_run, done, missing = pending_ages(directory, out_dir, args.tag, ages)
    print(f"{args.tag}: {len(done)} already benched, {len(to_run)} to run, "
          f"{len(missing)} without a checkpoint yet"
          + (f" ({missing})" if missing else ""))

    running: list[tuple[int, subprocess.Popen]] = []
    started: list[int] = []
    failed: list[int] = []

    def report(age: int, code: int) -> None:
        if code != 0:
            failed.append(age)
            print(f"  u{age}: bench exited {code}", file=sys.stderr)
            return
        result = output_path(out_dir, args.tag, age)
        wins = "?"
        games = "?"
        try:
            payload = json.loads(result.read_text())
            wins = str(payload["policy_wins"])
            games = str(payload["games"])
        except Exception:
            pass
        print(f"  u{age}: done, {wins}/{games} wins -> {result.name}")

    def reap(block: bool) -> bool:
        """Collect every bench that has finished. When `block`, wait until at least one has.

        Returns True if anything was collected. Blocking stops at the first collection rather
        than draining the whole set, so a free slot is refilled immediately instead of waiting
        for the slowest bench of the batch.
        """

        collected = False
        while True:
            for index, (age, process) in enumerate(running):
                code = process.poll()
                if code is None:
                    continue
                running.pop(index)
                report(age, code)
                collected = True
                break
            else:
                if collected or not block or not running:
                    return collected
                time.sleep(5)

    for age, checkpoint in to_run:
        command = bench_command(
            checkpoint=checkpoint,
            out_json=output_path(out_dir, args.tag, age),
            panel=args.panel,
            bot=args.bot,
            library=args.library,
            seed=args.seed,
            train_p=args.train_p,
            threads=args.threads_per_job,
            nice=args.nice,
            python=args.python,
            script=args.script,
            replays=not args.no_replays,
        )
        if args.dry_run:
            print("  " + " ".join(command))
            continue
        while len(running) >= args.jobs:
            reap(block=True)
        log = out_dir / f"bench-{args.tag}-u{age}.log"
        handle = log.open("w")
        process = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT,
                                   env={**os.environ})
        running.append((age, process))
        started.append(age)
        print(f"  u{age}: started ({checkpoint.name})")

    while running:
        reap(block=True)

    if failed:
        print(f"{args.tag}: {len(failed)} benches failed: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
