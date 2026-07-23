#!/usr/bin/env python3
"""YT mapper for D151 conditional-second counterfactual branches."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time


PYTHON_SOURCES = (
    "run_d151a_conditional_second_counterfactual.py",
    "run_d144a_two_intervention_mc_pilot.py",
    "rl_q6_proposal_env.py",
    "rl_macro_env.py",
)


def log(event: str, **payload: object) -> None:
    print(
        "[d151-yt-map] "
        + json.dumps({"event": event, **payload}, sort_keys=True),
        file=sys.stderr,
        flush=True,
    )


def input_specs():
    for line in sys.stdin:
        if line.strip():
            yield json.loads(line)


def safe_extract(archive_path: Path, target: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        root = target.resolve()
        for member in archive.getmembers():
            destination = (target / member.name).resolve()
            if destination != root and root not in destination.parents:
                raise RuntimeError(f"unsafe D151 runtime member: {member.name!r}")
        archive.extractall(target)


def prepare_layout(base: Path) -> Path:
    layout = base / "layout"
    if layout.exists():
        shutil.rmtree(layout)
    (layout / "cgauto").mkdir(parents=True)
    (layout / "cgauto" / "__init__.py").write_text("")
    for source in PYTHON_SOURCES:
        shutil.copy2(source, layout / "cgauto" / source)
    library = layout / "rust" / "target" / "release" / "libtroll_farm.so"
    library.parent.mkdir(parents=True)
    shutil.copy2("libtroll_farm.so", library)
    experts = (
        layout
        / "data"
        / "analysis"
        / "live-agent-6553250"
        / "d105a-q6-expert-population.tsv"
    )
    experts.parent.mkdir(parents=True)
    shutil.copy2("d105a-q6-expert-population.tsv", experts)
    shutil.copy2("d151_plan.tsv", layout / "d151_plan.tsv")
    dependencies = layout / "dependencies"
    dependencies.mkdir()
    safe_extract(Path("d151_numpy_runtime.tar.gz"), dependencies)
    return layout


def emit_tsv(path: Path, spec: dict) -> int:
    count = 0
    with path.open(encoding="utf-8", newline="") as source:
        for row_index, raw in enumerate(source):
            line = raw[:-1] if raw.endswith("\n") else raw
            if line.endswith("\r"):
                line = line[:-1]
            print(
                json.dumps(
                    {
                        "record_type": "branches",
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
    layout = prepare_layout(work)
    output = layout / "branches.tsv"
    threads = int(spec.get("threads", os.environ.get("TF_D151_THREADS", "16")))
    env = os.environ.copy()
    env.update(
        {
            "RAYON_NUM_THREADS": str(threads),
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "PYTHONPATH": str(layout / "dependencies")
            + os.pathsep
            + env.get("PYTHONPATH", ""),
        }
    )
    command = [
        "python3",
        "-m",
        "cgauto.run_d151a_conditional_second_counterfactual",
        str(int(spec["start_seed"])),
        str(int(spec["maps"])),
        "d151_plan.tsv",
        "branches.tsv",
    ]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=layout,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.perf_counter() - started
    log(
        "runner_complete",
        shard_id=shard,
        return_code=completed.returncode,
        elapsed_seconds=elapsed,
        stdout=completed.stdout[-4000:],
        stderr=completed.stderr[-4000:],
    )
    if completed.returncode != 0:
        raise RuntimeError(f"D151 runner failed for {shard}: {completed.stderr[-4000:]}")
    line_count = emit_tsv(output, spec)
    summary = json.loads(completed.stdout.strip().splitlines()[-1])
    print(
        json.dumps(
            {
                "record_type": "metadata",
                "shard_id": shard,
                "start_seed": int(spec["start_seed"]),
                "row_index": 0,
                "line": json.dumps(
                    {
                        "replica": str(spec["replica"]),
                        "elapsed_seconds": elapsed,
                        "line_count": line_count,
                        "threads": threads,
                        "runner": summary,
                        "runner_stderr": completed.stderr.strip(),
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
    base = Path("d151_mapper_work").resolve()
    base.mkdir(exist_ok=True)
    specs = list(input_specs())
    log("mapper_start", specs=len(specs))
    for spec in specs:
        run_spec(spec, base)
    log("mapper_complete", specs=len(specs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
