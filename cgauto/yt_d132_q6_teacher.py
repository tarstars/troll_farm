#!/usr/bin/env python3
"""Launch, monitor, and verify the D132 YT exact-teacher parity pilot."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
MATH_ROOT = Path("/home/tarstars/prj/math_through_eml")
MATH_SRC = MATH_ROOT / "src"
MATH_YT_UTILS = MATH_SRC / "math_through_eml" / "yt_utils.py"
PROTOCOL = BASE / "d132a-yt-q6-teacher-parity-protocol-2026-07-22.md"
MAPPER = ROOT / "cgauto" / "yt_d132_q6_teacher_mapper.py"
BINARY = ROOT / "rust" / "target" / "release" / "d112_q6_dense_counterfactual_teacher"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
REFERENCE_ARMS = BASE / "d126a-q6-validation-arms-9843780-9843795.tsv"
REFERENCE_BASELINES = BASE / "d126a-q6-validation-baselines-9843780-9843795.tsv"
LOCK = BASE / "d132a-yt-q6-teacher-parity-repair2-lock.json"
LAUNCH_RECORD = BASE / "d132a-yt-q6-teacher-parity-repair2-launch.json"
OUTPUT = BASE / "d132a-yt-q6-teacher-parity-result.json"
LOCAL_OUTPUT = BASE / "yt" / "d132a-q6-teacher-parity"

YT_PROXY = "watt.yt.yandex.net"
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d132a_q6_teacher_parity_seed9843780_repair1_20260722"
LAYER_PATHS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)
PILOT_SEED = 9_843_780
EXPECTED_ARM_ROWS = 2_232
EXPECTED_BASELINE_ROWS = 16
MAX_ACTIVE_SECONDS = 240.0
BINARY_SHA256 = "5bed211a33393f041221dcda81bdd2bf5d11522ad1aa3978fe4d3b79492f6d02"
EXPERT_SHA256 = "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            "shard_id": "pilot-00000",
            "start_seed": PILOT_SEED,
            "maps": 1,
            "threads": 16,
        }
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


def _verify_payload() -> None:
    actual = {"binary": sha256(BINARY), "experts": sha256(EXPERTS)}
    expected = {"binary": BINARY_SHA256, "experts": EXPERT_SHA256}
    if actual != expected:
        raise RuntimeError(f"D132 payload hashes changed: {actual!r}")


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
        raise RuntimeError(f"D132 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def launch(*, asynchronous: bool = True) -> dict:
    lock = verify_lock()
    _verify_payload()
    yt, LocalFile, client = _load_yt()
    paths = build_paths()
    if client.exists(paths["build"]):
        raise RuntimeError(f"D132 YT build already exists: {paths['build']}")
    client.create("map_node", paths["build"], recursive=True)
    client.write_table(
        paths["specs"], build_specs(), format=yt.JsonFormat(), force_create=True
    )
    spec = {
        "max_failed_job_count": 1,
        "title": "Troll Farm D132 exact q6 teacher parity",
        "pool": "delivery-ml",
        "mapper": {
            "cpu_limit": 16,
            "environment": {"TF_D132_THREADS": "16"},
            "layer_paths": list(LAYER_PATHS),
        },
    }
    operation = client.run_map(
        "python3 yt_d132_q6_teacher_mapper.py",
        paths["specs"],
        paths["records"],
        local_files=[
            LocalFile(str(MAPPER), file_name="yt_d132_q6_teacher_mapper.py"),
            LocalFile(str(BINARY), file_name="d112_q6_dense_counterfactual_teacher"),
            LocalFile(str(EXPERTS), file_name="d105a-q6-expert-population.tsv"),
        ],
        input_format=yt.JsonFormat(),
        output_format=yt.JsonFormat(),
        job_count=1,
        memory_limit=8 * 1024**3,
        spec=spec,
        sync=not asynchronous,
    )
    record = {
        "schema": "troll-farm-d132a-yt-q6-teacher-launch-v1",
        "lock": lock,
        "launched_utc": utc_now(),
        "operation_id": str(operation.id),
        "paths": paths,
        "specs": build_specs(),
        "layer_paths": LAYER_PATHS,
        "payload": {
            str(BINARY.relative_to(ROOT)): sha256(BINARY),
            str(EXPERTS.relative_to(ROOT)): sha256(EXPERTS),
            str(MAPPER.relative_to(ROOT)): sha256(MAPPER),
        },
    }
    LAUNCH_RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return record


def _operation():
    yt, _, client = _load_yt()
    launch_record = json.loads(LAUNCH_RECORD.read_text())
    operation = yt.Operation(launch_record["operation_id"], client=client)
    return client, operation, launch_record


def status() -> dict:
    client, operation, launch_record = _operation()
    paths = launch_record["paths"]
    result = {
        "operation_id": launch_record["operation_id"],
        "state": str(operation.get_state()),
        "progress": operation.get_progress(),
        "records_exists": client.exists(paths["records"]),
        "row_count": (
            int(client.get(f"{paths['records']}/@row_count"))
            if client.exists(paths["records"])
            else None
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return result


def reconstruct_rows(rows: list[dict], output_dir: Path) -> tuple[dict, list[dict]]:
    grouped: dict[str, dict[tuple[int, str], list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    metadata = []
    for row in rows:
        record_type = str(row["record_type"])
        if record_type == "metadata":
            metadata.append(json.loads(row["line"]))
            continue
        grouped[record_type][
            (int(row["start_seed"]), str(row["shard_id"]))
        ].append(row)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for record_type in ("arms", "baselines"):
        shards = grouped[record_type]
        header = None
        data_lines = []
        for shard_key in sorted(shards):
            shard_rows = sorted(shards[shard_key], key=lambda row: int(row["row_index"]))
            if [int(row["row_index"]) for row in shard_rows] != list(
                range(len(shard_rows))
            ):
                raise RuntimeError(f"noncontiguous D132 rows for {record_type} {shard_key}")
            shard_header = str(shard_rows[0]["line"])
            if header is None:
                header = shard_header
            elif header != shard_header:
                raise RuntimeError(f"inconsistent D132 {record_type} headers")
            data_lines.extend(str(row["line"]) for row in shard_rows[1:])
        if header is None:
            raise RuntimeError(f"D132 output lacks {record_type}")
        path = output_dir / f"{record_type}.tsv"
        path.write_text("\n".join([header, *data_lines]) + "\n", encoding="utf-8")
        outputs[record_type] = {
            "path": str(path),
            "rows": len(data_lines),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return outputs, metadata


def write_reference_subset(source: Path, seed: int, target: Path) -> dict:
    with source.open(encoding="utf-8", newline="") as stream:
        header = next(stream).rstrip("\r\n")
        selected = [
            line.rstrip("\r\n")
            for line in stream
            if line.split("\t", 1)[0] == str(seed)
        ]
    target.write_text("\n".join([header, *selected]) + "\n", encoding="utf-8")
    return {
        "path": str(target),
        "rows": len(selected),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
    }


def download_and_verify() -> dict:
    lock = verify_lock()
    yt, _, client = _load_yt()
    launch_record = json.loads(LAUNCH_RECORD.read_text())
    paths = launch_record["paths"]
    operation = yt.Operation(launch_record["operation_id"], client=client)
    state = str(operation.get_state())
    if state != "completed":
        raise RuntimeError(f"D132 operation is not complete: {state}")
    rows = list(client.read_table(paths["records"], format=yt.JsonFormat()))
    generated_dir = LOCAL_OUTPUT / "generated"
    reference_dir = LOCAL_OUTPUT / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)
    generated, metadata = reconstruct_rows(rows, generated_dir)
    reference = {
        "arms": write_reference_subset(
            REFERENCE_ARMS, PILOT_SEED, reference_dir / "arms.tsv"
        ),
        "baselines": write_reference_subset(
            REFERENCE_BASELINES, PILOT_SEED, reference_dir / "baselines.tsv"
        ),
    }
    if len(metadata) != 1:
        raise RuntimeError(f"D132 expected one metadata row, got {len(metadata)}")
    active_seconds = float(metadata[0]["elapsed_seconds"])
    gates = {
        "operation_completed": state == "completed",
        "exactly_2232_arm_rows": generated["arms"]["rows"]
        == EXPECTED_ARM_ROWS,
        "exactly_16_baseline_rows": generated["baselines"]["rows"]
        == EXPECTED_BASELINE_ROWS,
        "arm_bytes_exact": (generated_dir / "arms.tsv").read_bytes()
        == (reference_dir / "arms.tsv").read_bytes(),
        "baseline_bytes_exact": (generated_dir / "baselines.tsv").read_bytes()
        == (reference_dir / "baselines.tsv").read_bytes(),
        "active_collection_at_most_240_seconds": active_seconds
        <= MAX_ACTIVE_SECONDS,
    }
    result = {
        "schema": "troll-farm-d132a-yt-q6-teacher-parity-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": {
            "operation_id": launch_record["operation_id"],
            "state": state,
            "paths": paths,
            "table_rows": len(rows),
        },
        "mapper_metadata": metadata[0],
        "generated": generated,
        "reference": reference,
        "gates": gates,
        "pass": all(gates.values()),
        "decision": (
            "authorize_frozen_multi_shard_teacher_corpus"
            if all(gates.values())
            else "close_yt_for_q6_teacher_collection"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    launch_parser = sub.add_parser("launch")
    launch_parser.add_argument("--sync", action="store_true")
    sub.add_parser("status")
    sub.add_parser("download")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "launch":
        launch(asynchronous=not args.sync)
    elif args.command == "status":
        status()
    else:
        download_and_verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
