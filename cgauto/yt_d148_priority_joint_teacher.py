#!/usr/bin/env python3
"""Launch and reconstruct D148's fresh-map priority joint teacher corpus."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d148a-priority-joint-teacher-corpus-protocol-2026-07-22.md"
LOCK = BASE / "d148a-priority-joint-teacher-corpus-lock.json"
LAUNCH_RECORD = BASE / "d148a-priority-joint-teacher-corpus-launch.json"
DOWNLOAD_RECORD = BASE / "d148a-priority-joint-teacher-corpus-download.json"
LOCAL_OUTPUT = BASE / "yt" / "d148a-priority-joint-teacher-corpus"

MATH_SRC = Path("/home/tarstars/prj/math_through_eml/src")
MAPPER = ROOT / "cgauto" / "yt_d148_priority_joint_teacher_mapper.py"
DRIVER = ROOT / "cgauto" / "run_d148a_priority_joint_teacher.py"
COLLECTOR = ROOT / "cgauto" / "collect_d147a_selected_trajectory_features.py"
D144_DRIVER = ROOT / "cgauto" / "run_d144a_two_intervention_mc_pilot.py"
Q6_WRAPPER = ROOT / "cgauto" / "rl_q6_proposal_env.py"
MACRO_WRAPPER = ROOT / "cgauto" / "rl_macro_env.py"
LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
BINARY = ROOT / "rust" / "target" / "release" / "d112_q6_dense_counterfactual_teacher"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
NUMPY_RUNTIME = BASE / "yt" / "d144a-numpy-2.2.6-py310-runtime.tar.gz"

YT_PROXY = "watt.yt.yandex.net"
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d148a_priority_joint_teacher_9844136_9844199_20260722"
LAYER_PATHS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)

START_SEED = 9_844_136
MAPS = 64
MAPS_PER_SHARD = 8
SHARDS = MAPS // MAPS_PER_SHARD
SEARCH_BUDGET = 64
THREADS = 16
JOINT_MAX_ACTIVE_SECONDS = 2_700.0
EXACT_MAX_ACTIVE_SECONDS = 1_200.0
VALIDATION_START_SEED = 9_844_200
VALIDATION_MAPS = 16

JOINT_RECORD_TYPES = ("population", "manifest", "candidates", "replays")
EXACT_RECORD_TYPES = ("arms", "baselines")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_paths(root: str = YT_ROOT, build_name: str = BUILD_NAME) -> dict[str, str]:
    build = f"{root.rstrip('/')}/dataset_builds/{build_name}"
    return {
        "build": build,
        "specs": f"{build}/specs",
        "records": f"{build}/records",
    }


def build_specs() -> list[dict[str, object]]:
    joint = [
        {
            "shard_id": f"joint-{index:02d}",
            "kind": "joint",
            "start_seed": START_SEED + index * MAPS_PER_SHARD,
            "maps": MAPS_PER_SHARD,
            "search_budget": SEARCH_BUDGET,
            "threads": THREADS,
        }
        for index in range(SHARDS)
    ]
    exact = [
        {
            "shard_id": f"exact-{index:02d}",
            "kind": "exact",
            "start_seed": START_SEED + index * MAPS_PER_SHARD,
            "maps": MAPS_PER_SHARD,
            "threads": THREADS,
        }
        for index in range(SHARDS)
    ]
    return joint + exact


def _load_yt():
    if str(MATH_SRC) not in sys.path:
        sys.path.insert(0, str(MATH_SRC))
    import yt.wrapper as yt
    from math_through_eml.yt_utils import default_token_path, get_yt_client
    from yt.wrapper.file_commands import LocalFile

    client = get_yt_client(
        YT_PROXY,
        token=os.environ.get("YT_TOKEN"),
        token_path=os.environ.get("YT_TOKEN_PATH") or default_token_path(),
        max_upload_thread_count=1,
    )
    return yt, LocalFile, client


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    for absolute, expected in payload["external_sha256"].items():
        path = Path(absolute)
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[absolute] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D148 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def _write_specs_as_chunks(yt, client, path: str, specs: list[dict]) -> None:
    append = False
    for spec in specs:
        client.write_table(
            yt.TablePath(path, append=append),
            [spec],
            format=yt.JsonFormat(),
            force_create=not append,
        )
        append = True


def launch(*, asynchronous: bool = True) -> dict:
    lock = verify_lock()
    yt, LocalFile, client = _load_yt()
    paths = build_paths()
    specs = build_specs()
    if client.exists(paths["build"]):
        raise RuntimeError(f"D148 YT build already exists: {paths['build']}")
    client.create("map_node", paths["build"], recursive=True)
    _write_specs_as_chunks(yt, client, paths["specs"], specs)
    operation_spec = {
        "max_failed_job_count": 1,
        "title": "Troll Farm D148 priority joint q6 teacher corpus",
        "pool": "delivery-ml",
        "mapper": {
            "cpu_limit": THREADS,
            "environment": {
                "TF_D148_THREADS": str(THREADS),
                "RAYON_NUM_THREADS": str(THREADS),
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            },
            "layer_paths": list(LAYER_PATHS),
        },
    }
    payload = (
        MAPPER,
        DRIVER,
        COLLECTOR,
        D144_DRIVER,
        Q6_WRAPPER,
        MACRO_WRAPPER,
        LIBRARY,
        BINARY,
        EXPERTS,
        NUMPY_RUNTIME,
    )
    local_files = [
        LocalFile(str(path), file_name=path.name)
        for path in payload[:-1]
    ] + [
        LocalFile(str(NUMPY_RUNTIME), file_name="d148_numpy_runtime.tar.gz")
    ]
    operation = client.run_map(
        f"python3 {MAPPER.name}",
        paths["specs"],
        paths["records"],
        local_files=local_files,
        input_format=yt.JsonFormat(),
        output_format=yt.JsonFormat(),
        job_count=len(specs),
        memory_limit=12 * 1024**3,
        spec=operation_spec,
        sync=not asynchronous,
    )
    record = {
        "schema": "troll-farm-d148a-priority-joint-teacher-launch-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "launched_utc": utc_now(),
        "operation_id": str(operation.id),
        "paths": paths,
        "specs": specs,
        "job_count": len(specs),
        "fresh_training_panel": [START_SEED, START_SEED + MAPS - 1],
        "reserved_validation_panel": [
            VALIDATION_START_SEED,
            VALIDATION_START_SEED + VALIDATION_MAPS - 1,
        ],
        "layer_paths": LAYER_PATHS,
        "payload": {str(path): sha256(path) for path in payload},
    }
    LAUNCH_RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return record


def _operation():
    yt, _, client = _load_yt()
    launch_record = json.loads(LAUNCH_RECORD.read_text())
    return (
        yt,
        client,
        yt.Operation(launch_record["operation_id"], client=client),
        launch_record,
    )


def status() -> dict:
    _, client, operation, launch_record = _operation()
    records = launch_record["paths"]["records"]
    result = {
        "operation_id": launch_record["operation_id"],
        "state": str(operation.get_state()),
        "progress": operation.get_progress(),
        "records_exists": client.exists(records),
        "row_count": int(client.get(f"{records}/@row_count"))
        if client.exists(records)
        else None,
    }
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return result


def _artifact(path: Path, rows: int) -> dict:
    return {
        "path": str(path),
        "rows": rows,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def reconstruct_stream(
    rows: Iterable[dict], output_dir: Path, specs: list[dict]
) -> tuple[dict, list[dict], int]:
    expected = {str(spec["shard_id"]): spec for spec in specs}
    if len(expected) != len(specs):
        raise RuntimeError("duplicate D148 shard ids")
    output_dir.mkdir(parents=True, exist_ok=False)
    parts = output_dir / "parts"
    parts.mkdir()
    handles = {}
    next_index: dict[tuple[str, str], int] = defaultdict(int)
    metadata_by_shard = {}
    table_rows = 0
    try:
        for row in rows:
            table_rows += 1
            shard = str(row["shard_id"])
            record_type = str(row["record_type"])
            if shard not in expected:
                raise RuntimeError(f"unexpected D148 shard: {shard}")
            spec = expected[shard]
            if int(row["start_seed"]) != int(spec["start_seed"]):
                raise RuntimeError(f"D148 start seed drift for {shard}")
            if record_type == "metadata":
                if shard in metadata_by_shard or int(row["row_index"]) != 0:
                    raise RuntimeError(f"duplicate or malformed D148 metadata: {shard}")
                payload = json.loads(str(row["line"]))
                payload.update(
                    {
                        "shard_id": shard,
                        "start_seed": int(spec["start_seed"]),
                        "maps": int(spec["maps"]),
                    }
                )
                metadata_by_shard[shard] = payload
                continue
            allowed = JOINT_RECORD_TYPES if spec["kind"] == "joint" else EXACT_RECORD_TYPES
            if record_type not in allowed:
                raise RuntimeError(f"unexpected D148 record type for {shard}: {record_type}")
            key = (shard, record_type)
            index = int(row["row_index"])
            if index != next_index[key]:
                raise RuntimeError(
                    f"noncontiguous D148 rows for {key}: expected {next_index[key]}, got {index}"
                )
            if key not in handles:
                shard_dir = parts / shard
                shard_dir.mkdir(exist_ok=True)
                handles[key] = (shard_dir / f"{record_type}.tsv").open(
                    "w", encoding="utf-8", newline=""
                )
            handles[key].write(str(row["line"]) + "\n")
            next_index[key] += 1
    finally:
        for handle in handles.values():
            handle.close()

    if set(metadata_by_shard) != set(expected):
        raise RuntimeError("D148 metadata set incomplete")
    for shard, spec in expected.items():
        metadata = metadata_by_shard[shard]
        if metadata["kind"] != spec["kind"] or int(metadata["threads"]) != int(
            spec["threads"]
        ):
            raise RuntimeError(f"D148 metadata/spec drift for {shard}")
        record_types = JOINT_RECORD_TYPES if spec["kind"] == "joint" else EXACT_RECORD_TYPES
        for record_type in record_types:
            key = (shard, record_type)
            if next_index[key] < 1:
                raise RuntimeError(f"D148 {shard} lacks {record_type}")
            if int(metadata["line_counts"][record_type]) != next_index[key]:
                raise RuntimeError(f"D148 line-count drift for {key}")

    outputs = {}
    end_seed = START_SEED + MAPS - 1
    kind_specs = {
        "joint": sorted(
            (spec for spec in specs if spec["kind"] == "joint"),
            key=lambda item: int(item["start_seed"]),
        ),
        "exact": sorted(
            (spec for spec in specs if spec["kind"] == "exact"),
            key=lambda item: int(item["start_seed"]),
        ),
    }
    for record_type in JOINT_RECORD_TYPES + EXACT_RECORD_TYPES:
        kind = "joint" if record_type in JOINT_RECORD_TYPES else "exact"
        target = output_dir / f"d148a-{record_type}-{START_SEED}-{end_seed}.tsv"
        header = None
        data_rows = 0
        with target.open("x", encoding="utf-8", newline="") as sink:
            for spec in kind_specs[kind]:
                shard = str(spec["shard_id"])
                source = parts / shard / f"{record_type}.tsv"
                with source.open(encoding="utf-8", newline="") as part:
                    shard_header = part.readline()
                    if not shard_header:
                        raise RuntimeError(f"empty D148 {record_type} shard: {shard}")
                    if header is None:
                        header = shard_header
                        sink.write(header)
                    elif header != shard_header:
                        raise RuntimeError(f"inconsistent D148 {record_type} header")
                    shutil.copyfileobj(part, sink, length=1024 * 1024)
                data_rows += next_index[(shard, record_type)] - 1
        outputs[record_type] = _artifact(target, data_rows)
    metadata = [metadata_by_shard[key] for key in sorted(metadata_by_shard)]
    shutil.rmtree(parts)
    return outputs, metadata, table_rows


def download() -> dict:
    lock = verify_lock()
    yt, client, operation, launch_record = _operation()
    state = str(operation.get_state())
    if state != "completed":
        raise RuntimeError(f"D148 operation is not complete: {state}")
    outputs, metadata, table_rows = reconstruct_stream(
        client.read_table(launch_record["paths"]["records"], format=yt.JsonFormat()),
        LOCAL_OUTPUT,
        launch_record["specs"],
    )
    result = {
        "schema": "troll-farm-d148a-priority-joint-teacher-download-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "downloaded_utc": utc_now(),
        "operation": {
            "operation_id": launch_record["operation_id"],
            "state": state,
            "paths": launch_record["paths"],
            "table_rows": table_rows,
        },
        "outputs": outputs,
        "mapper_metadata": metadata,
    }
    DOWNLOAD_RECORD.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("launch", "status", "download"))
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    if args.command == "launch":
        launch(asynchronous=not args.sync)
    elif args.command == "status":
        status()
    else:
        download()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
