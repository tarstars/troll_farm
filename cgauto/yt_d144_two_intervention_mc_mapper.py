#!/usr/bin/env python3
"""YT mapper for D144's repeated MC panel and exact one-use comparator."""

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
    "run_d144a_two_intervention_mc_pilot.py",
    "rl_q6_proposal_env.py",
    "rl_macro_env.py",
)


def log(event: str, **payload: object) -> None:
    print(
        "[d144-yt-map] "
        + json.dumps({"event": event, **payload}, sort_keys=True),
        file=sys.stderr,
        flush=True,
    )


def input_specs():
    for line in sys.stdin:
        if line.strip():
            yield json.loads(line)


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
    shutil.copy2(
        "d112_q6_dense_counterfactual_teacher",
        layout / "d112_q6_dense_counterfactual_teacher",
    )
    (layout / "d112_q6_dense_counterfactual_teacher").chmod(0o755)
    dependencies = layout / "dependencies"
    dependencies.mkdir()
    with tarfile.open("d144_numpy_runtime.tar.gz", "r:gz") as archive:
        root = dependencies.resolve()
        for member in archive.getmembers():
            target = (dependencies / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe D144 runtime member: {member.name!r}")
        archive.extractall(dependencies)
    return layout


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
    layout = prepare_layout(work)
    kind = str(spec["kind"])
    threads = int(spec.get("threads", os.environ.get("TF_D144_THREADS", "16")))
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
    if kind == "mc":
        output = layout / "episodes.tsv"
        command = [
            "python3",
            "-m",
            "cgauto.run_d144a_two_intervention_mc_pilot",
            str(int(spec["start_seed"])),
            str(int(spec["maps"])),
            str(int(spec["replicas"])),
            str(int(spec["single_replicas"])),
            str(output.relative_to(layout)),
        ]
        outputs = ((output, "mc"),)
    elif kind == "exact":
        arms = layout / "arms.tsv"
        baselines = layout / "baselines.tsv"
        command = [
            "./d112_q6_dense_counterfactual_teacher",
            "./data/analysis/live-agent-6553250/d105a-q6-expert-population.tsv",
            str(int(spec["start_seed"])),
            str(int(spec["maps"])),
            str(arms.relative_to(layout)),
            str(baselines.relative_to(layout)),
            str(threads),
        ]
        outputs = ((arms, "arms"), (baselines, "baselines"))
    else:
        raise RuntimeError(f"unknown D144 mapper kind: {kind}")

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
        kind=kind,
        return_code=completed.returncode,
        elapsed_seconds=elapsed,
        stdout=completed.stdout[-2000:],
        stderr=completed.stderr[-2000:],
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"D144 {kind} runner failed for {shard}: {completed.stderr[-2000:]}"
        )
    line_counts = {
        record_type: emit_tsv(path, record_type, spec)
        for path, record_type in outputs
    }
    print(
        json.dumps(
            {
                "record_type": "metadata",
                "shard_id": shard,
                "start_seed": int(spec["start_seed"]),
                "row_index": 0,
                "line": json.dumps(
                    {
                        "kind": kind,
                        "elapsed_seconds": elapsed,
                        "line_counts": line_counts,
                        "threads": threads,
                        "runner_stdout": completed.stdout.strip(),
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
    base = Path("d144_mapper_work").resolve()
    base.mkdir(exist_ok=True)
    specs = list(input_specs())
    log("mapper_start", specs=len(specs))
    for spec in specs:
        run_spec(spec, base)
    log("mapper_complete", specs=len(specs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
