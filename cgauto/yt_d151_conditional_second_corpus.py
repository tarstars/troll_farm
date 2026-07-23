#!/usr/bin/env python3
"""Launch and reconstruct D151's replicated conditional-second corpus."""

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
PROTOCOL = BASE / "d151a-conditional-second-counterfactual-corpus-protocol-2026-07-23.md"
LOCK = BASE / "d151a-conditional-second-counterfactual-corpus-lock.json"
PLAN = BASE / "d151a-conditional-second-branch-plan-9844136-9844199.tsv"
LAUNCH_RECORD = BASE / "d151a-conditional-second-counterfactual-corpus-launch.json"
DOWNLOAD_RECORD = BASE / "d151a-conditional-second-counterfactual-corpus-download.json"
LOCAL_OUTPUT = BASE / "yt" / "d151a-conditional-second-counterfactual-corpus"

MATH_SRC = Path("/home/tarstars/prj/math_through_eml/src")
MAPPER = ROOT / "cgauto" / "yt_d151_conditional_second_mapper.py"
DRIVER = ROOT / "cgauto" / "run_d151a_conditional_second_counterfactual.py"
D144_DRIVER = ROOT / "cgauto" / "run_d144a_two_intervention_mc_pilot.py"
Q6_WRAPPER = ROOT / "cgauto" / "rl_q6_proposal_env.py"
MACRO_WRAPPER = ROOT / "cgauto" / "rl_macro_env.py"
LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
NUMPY_RUNTIME = BASE / "yt" / "d144a-numpy-2.2.6-py310-runtime.tar.gz"

YT_PROXY = "watt.yt.yandex.net"
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d151a_conditional_second_9844136_9844199_20260723"
LAYER_PATHS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)

START_SEED = 9_844_136
MAPS = 64
MAPS_PER_SHARD = 8
SHARDS = MAPS // MAPS_PER_SHARD
THREADS = 16
MAX_ACTIVE_SECONDS = 1_200.0
EXPECTED_ROWS = 16_228


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


def build_specs() -> list[dict]:
    return [
        {
            "shard_id": f"{replica}-{index:02d}",
            "replica": replica,
            "start_seed": START_SEED + index * MAPS_PER_SHARD,
            "maps": MAPS_PER_SHARD,
            "threads": THREADS,
        }
        for replica in ("a", "b")
        for index in range(SHARDS)
    ]


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
        raise RuntimeError(f"D151 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def _write_specs(yt, client, path: str, specs: list[dict]) -> None:
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
        raise RuntimeError(f"D151 YT build already exists: {paths['build']}")
    client.create("map_node", paths["build"], recursive=True)
    _write_specs(yt, client, paths["specs"], specs)
    operation_spec = {
        "max_failed_job_count": 1,
        "title": "Troll Farm D151 conditional-second counterfactual corpus A/B",
        "pool": "delivery-ml",
        "mapper": {
            "cpu_limit": THREADS,
            "environment": {
                "TF_D151_THREADS": str(THREADS),
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
        D144_DRIVER,
        Q6_WRAPPER,
        MACRO_WRAPPER,
        LIBRARY,
        EXPERTS,
        PLAN,
        NUMPY_RUNTIME,
    )
    local_files = [
        LocalFile(str(path), file_name=path.name) for path in payload[:-2]
    ] + [
        LocalFile(str(PLAN), file_name="d151_plan.tsv"),
        LocalFile(str(NUMPY_RUNTIME), file_name="d151_numpy_runtime.tar.gz"),
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
        "schema": "troll-farm-d151a-conditional-second-launch-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "launched_utc": utc_now(),
        "operation_id": str(operation.id),
        "paths": paths,
        "specs": specs,
        "job_count": len(specs),
        "layer_paths": LAYER_PATHS,
        "payload": {str(path): sha256(path) for path in payload},
    }
    LAUNCH_RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return record


def _operation():
    yt, _, client = _load_yt()
    launch_record = json.loads(LAUNCH_RECORD.read_text())
    return yt, client, yt.Operation(launch_record["operation_id"], client=client), launch_record


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
        raise RuntimeError("duplicate D151 shard ids")
    output_dir.mkdir(parents=True, exist_ok=False)
    parts = output_dir / "parts"
    parts.mkdir()
    handles = {}
    next_index = defaultdict(int)
    metadata = {}
    table_rows = 0
    try:
        for row in rows:
            table_rows += 1
            shard = str(row["shard_id"])
            if shard not in expected or int(row["start_seed"]) != int(
                expected[shard]["start_seed"]
            ):
                raise RuntimeError(f"unexpected D151 shard/start: {shard}")
            record_type = str(row["record_type"])
            if record_type == "metadata":
                if shard in metadata or int(row["row_index"]) != 0:
                    raise RuntimeError(f"duplicate D151 metadata: {shard}")
                value = json.loads(str(row["line"]))
                value.update(
                    {
                        "shard_id": shard,
                        "start_seed": int(expected[shard]["start_seed"]),
                        "maps": int(expected[shard]["maps"]),
                    }
                )
                metadata[shard] = value
                continue
            if record_type != "branches":
                raise RuntimeError(f"unexpected D151 record type: {record_type}")
            index = int(row["row_index"])
            if index != next_index[shard]:
                raise RuntimeError(f"noncontiguous D151 rows for {shard}")
            if shard not in handles:
                target_dir = parts / shard
                target_dir.mkdir()
                handles[shard] = (target_dir / "branches.tsv").open(
                    "w", encoding="utf-8", newline=""
                )
            handles[shard].write(str(row["line"]) + "\n")
            next_index[shard] += 1
    finally:
        for handle in handles.values():
            handle.close()
    if set(metadata) != set(expected):
        raise RuntimeError("D151 metadata set incomplete")
    for shard, spec in expected.items():
        item = metadata[shard]
        if (
            item["replica"] != spec["replica"]
            or int(item["threads"]) != int(spec["threads"])
            or int(item["line_count"]) != next_index[shard]
            or next_index[shard] < 2
        ):
            raise RuntimeError(f"D151 metadata/spec drift for {shard}")

    outputs = {}
    end_seed = START_SEED + MAPS - 1
    for replica in ("a", "b"):
        target = output_dir / f"d151a-branches-{replica}-{START_SEED}-{end_seed}.tsv"
        header = None
        data_rows = 0
        with target.open("x", encoding="utf-8", newline="") as sink:
            for spec in sorted(
                (item for item in specs if item["replica"] == replica),
                key=lambda item: int(item["start_seed"]),
            ):
                shard = str(spec["shard_id"])
                with (parts / shard / "branches.tsv").open(
                    encoding="utf-8", newline=""
                ) as source:
                    shard_header = source.readline()
                    if not shard_header:
                        raise RuntimeError(f"empty D151 shard: {shard}")
                    if header is None:
                        header = shard_header
                        sink.write(header)
                    elif shard_header != header:
                        raise RuntimeError("inconsistent D151 branch header")
                    shutil.copyfileobj(source, sink, length=1024 * 1024)
                data_rows += next_index[shard] - 1
        outputs[replica] = _artifact(target, data_rows)
    shutil.rmtree(parts)
    return outputs, [metadata[key] for key in sorted(metadata)], table_rows


def download() -> dict:
    lock = verify_lock()
    yt, client, operation, launch_record = _operation()
    state = str(operation.get_state())
    if state != "completed":
        raise RuntimeError(f"D151 operation is not complete: {state}")
    outputs, metadata, table_rows = reconstruct_stream(
        client.read_table(launch_record["paths"]["records"], format=yt.JsonFormat()),
        LOCAL_OUTPUT,
        launch_record["specs"],
    )
    result = {
        "schema": "troll-farm-d151a-conditional-second-download-v1",
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
        "byte_identical": Path(outputs["a"]["path"]).read_bytes()
        == Path(outputs["b"]["path"]).read_bytes(),
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
