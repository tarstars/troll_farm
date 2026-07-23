#!/usr/bin/env python3
"""YT mapper wrapper for the self-contained D112 exact q6 teacher binary."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def log(event: str, **payload: object) -> None:
    print(
        "[d132-yt-map] " + json.dumps({"event": event, **payload}, sort_keys=True),
        file=sys.stderr,
        flush=True,
    )


def input_specs():
    for line in sys.stdin:
        if line.strip():
            yield json.loads(line)


def emit_tsv(path: Path, record_type: str, spec: dict) -> int:
    count = 0
    with path.open(encoding="utf-8", newline="") as source:
        for row_index, raw in enumerate(source):
            line = raw[:-1] if raw.endswith("\n") else raw
            if line.endswith("\r"):
                line = line[:-1]
            print(
                json.dumps(
                    {
                        "record_type": record_type,
                        "shard_id": str(spec["shard_id"]),
                        "start_seed": int(spec["start_seed"]),
                        "row_index": row_index,
                        "line": line,
                    },
                    ensure_ascii=True,
                    separators=(",", ":"),
                )
            )
            count += 1
    return count


def run_spec(spec: dict, base: Path) -> None:
    shard = str(spec["shard_id"])
    work = base / shard
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    arms = work / "arms.tsv"
    baselines = work / "baselines.tsv"
    threads = int(spec.get("threads", os.environ.get("TF_D132_THREADS", "16")))
    command = [
        "./d112_q6_dense_counterfactual_teacher",
        "./d105a-q6-expert-population.tsv",
        str(int(spec["start_seed"])),
        str(int(spec["maps"])),
        str(arms),
        str(baselines),
        str(threads),
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    elapsed = time.perf_counter() - started
    log(
        "collector_complete",
        shard_id=shard,
        return_code=completed.returncode,
        elapsed_seconds=elapsed,
        stderr=completed.stderr[-2000:],
    )
    if completed.returncode != 0:
        raise RuntimeError(f"collector failed for {shard}: {completed.stderr[-2000:]}")
    arm_lines = emit_tsv(arms, "arms", spec)
    baseline_lines = emit_tsv(baselines, "baselines", spec)
    print(
        json.dumps(
            {
                "record_type": "metadata",
                "shard_id": shard,
                "start_seed": int(spec["start_seed"]),
                "row_index": 0,
                "line": json.dumps(
                    {
                        "elapsed_seconds": elapsed,
                        "arm_lines": arm_lines,
                        "baseline_lines": baseline_lines,
                        "threads": threads,
                        "collector_stderr": completed.stderr.strip(),
                    },
                    sort_keys=True,
                ),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        ),
        flush=True,
    )


def main() -> int:
    base = Path("d132_mapper_work").resolve()
    base.mkdir(exist_ok=True)
    specs = list(input_specs())
    log("mapper_start", specs=len(specs))
    for spec in specs:
        run_spec(spec, base)
    log("mapper_complete", specs=len(specs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
