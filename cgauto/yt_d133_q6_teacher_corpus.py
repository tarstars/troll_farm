#!/usr/bin/env python3
"""Launch, reconstruct, and analyze D133's independent-block q6 teacher corpus."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
from typing import Iterable

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
MATH_SRC = Path("/home/tarstars/prj/math_through_eml/src")
MATH_YT_UTILS = MATH_SRC / "math_through_eml" / "yt_utils.py"
PROTOCOL = BASE / "d133a-yt-q6-independent-block-corpus-protocol-2026-07-22.md"
MAPPER = ROOT / "cgauto" / "yt_d132_q6_teacher_mapper.py"
BINARY = ROOT / "rust" / "target" / "release" / "d112_q6_dense_counterfactual_teacher"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
LOCK = BASE / "d133a-yt-q6-independent-block-corpus-lock.json"
LAUNCH_RECORD = BASE / "d133a-yt-q6-independent-block-corpus-launch.json"
DOWNLOAD_RECORD = BASE / "d133a-yt-q6-independent-block-corpus-download.json"
OUTPUT = BASE / "d133a-yt-q6-independent-block-corpus-result.json"
LOCAL_OUTPUT = BASE / "yt" / "d133a-q6-independent-block-corpus"

YT_PROXY = "watt.yt.yandex.net"
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d133a_q6_teacher_corpus_9844000_9844063_20260722"
LAYER_PATHS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)
START_SEED = 9_844_000
MAPS = 64
BLOCKS = 4
MAPS_PER_BLOCK = 16
SHARDS_PER_BLOCK = 4
MAPS_PER_SHARD = 4
THREADS = 16
EXPECTED_TASKS = MAPS * 2 * len(d112.OPPONENTS)
EXPECTED_BASELINES_PER_BLOCK = MAPS_PER_BLOCK * 2 * len(d112.OPPONENTS)
MIN_ARMS = 80_000
MIN_ROOTS = 4_800
MAX_SHARD_ACTIVE_SECONDS = 900.0
MIN_SHARD_ARMS_PER_SECOND = 12.0
BINARY_SHA256 = "5bed211a33393f041221dcda81bdd2bf5d11522ad1aa3978fe4d3b79492f6d02"
EXPERT_SHA256 = "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8"


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
    specs = []
    for block in range(BLOCKS):
        for shard in range(SHARDS_PER_BLOCK):
            start = (
                START_SEED
                + block * MAPS_PER_BLOCK
                + shard * MAPS_PER_SHARD
            )
            specs.append(
                {
                    "shard_id": f"block-{block:02d}-shard-{shard:02d}",
                    "block_id": block,
                    "start_seed": start,
                    "maps": MAPS_PER_SHARD,
                    "threads": THREADS,
                }
            )
    return specs


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
        raise RuntimeError(f"D133 payload hashes changed: {actual!r}")


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
        raise RuntimeError(f"D133 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def _write_specs_as_chunks(yt, client, path: str, specs: list[dict]) -> None:
    append = False
    for spec in specs:
        target = yt.TablePath(path, append=append)
        client.write_table(
            target,
            [spec],
            format=yt.JsonFormat(),
            force_create=not append,
        )
        append = True


def launch(*, asynchronous: bool = True) -> dict:
    lock = verify_lock()
    _verify_payload()
    yt, LocalFile, client = _load_yt()
    paths = build_paths()
    specs = build_specs()
    if client.exists(paths["build"]):
        raise RuntimeError(f"D133 YT build already exists: {paths['build']}")
    client.create("map_node", paths["build"], recursive=True)
    _write_specs_as_chunks(yt, client, paths["specs"], specs)
    operation_spec = {
        "max_failed_job_count": 1,
        "title": "Troll Farm D133 independent-block exact q6 teacher corpus",
        "pool": "delivery-ml",
        "mapper": {
            "cpu_limit": THREADS,
            "environment": {"TF_D132_THREADS": str(THREADS)},
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
        job_count=len(specs),
        memory_limit=8 * 1024**3,
        spec=operation_spec,
        sync=not asynchronous,
    )
    record = {
        "schema": "troll-farm-d133a-yt-q6-teacher-corpus-launch-v1",
        "lock": lock,
        "launched_utc": utc_now(),
        "operation_id": str(operation.id),
        "paths": paths,
        "specs": specs,
        "spec_write_batch_size": 1,
        "job_count": len(specs),
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
    return yt, client, operation, launch_record


def status() -> dict:
    _, client, operation, launch_record = _operation()
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


def _block_file(output_dir: Path, block: int, record_type: str) -> Path:
    start = START_SEED + block * MAPS_PER_BLOCK
    end = start + MAPS_PER_BLOCK - 1
    return output_dir / f"block-{block:02d}-{record_type}-{start}-{end}.tsv"


def reconstruct_stream(
    rows: Iterable[dict], output_dir: Path, specs: list[dict]
) -> tuple[dict, list[dict], int]:
    """Route a YT row stream to shards, then merge only within fixed blocks."""

    expected = {str(spec["shard_id"]): spec for spec in specs}
    if len(expected) != len(specs):
        raise RuntimeError("duplicate D133 shard ids in specs")
    parts = output_dir / "parts"
    if parts.exists():
        raise RuntimeError(f"D133 partial output already exists: {parts}")
    parts.mkdir(parents=True)
    handles = {}
    next_index: dict[tuple[str, str], int] = defaultdict(int)
    metadata_by_shard = {}
    table_rows = 0
    try:
        for row in rows:
            table_rows += 1
            record_type = str(row["record_type"])
            shard = str(row["shard_id"])
            if shard not in expected:
                raise RuntimeError(f"unexpected D133 shard: {shard}")
            spec = expected[shard]
            start_seed = int(row["start_seed"])
            if start_seed != int(spec["start_seed"]):
                raise RuntimeError(
                    f"wrong D133 start seed for {shard}: {start_seed}"
                )
            if record_type == "metadata":
                if shard in metadata_by_shard:
                    raise RuntimeError(f"duplicate D133 metadata for {shard}")
                if int(row["row_index"]) != 0:
                    raise RuntimeError(f"invalid D133 metadata row index for {shard}")
                payload = json.loads(str(row["line"]))
                payload.update(
                    {
                        "shard_id": shard,
                        "block_id": int(spec["block_id"]),
                        "start_seed": start_seed,
                        "maps": int(spec["maps"]),
                    }
                )
                metadata_by_shard[shard] = payload
                continue
            if record_type not in ("arms", "baselines"):
                raise RuntimeError(f"unexpected D133 record type: {record_type}")
            key = (shard, record_type)
            row_index = int(row["row_index"])
            if row_index != next_index[key]:
                raise RuntimeError(
                    f"noncontiguous D133 rows for {key}: "
                    f"expected {next_index[key]}, got {row_index}"
                )
            if key not in handles:
                shard_dir = parts / shard
                shard_dir.mkdir(parents=True, exist_ok=True)
                handles[key] = (shard_dir / f"{record_type}.tsv").open(
                    "w", encoding="utf-8", newline=""
                )
            handles[key].write(str(row["line"]) + "\n")
            next_index[key] += 1
    finally:
        for handle in handles.values():
            handle.close()

    if set(metadata_by_shard) != set(expected):
        missing = sorted(set(expected) - set(metadata_by_shard))
        raise RuntimeError(f"missing D133 mapper metadata: {missing}")
    for shard, spec in expected.items():
        metadata = metadata_by_shard[shard]
        for record_type, metadata_key in (
            ("arms", "arm_lines"),
            ("baselines", "baseline_lines"),
        ):
            key = (shard, record_type)
            if next_index[key] < 1:
                raise RuntimeError(f"D133 {shard} lacks {record_type}")
            if int(metadata[metadata_key]) != next_index[key]:
                raise RuntimeError(
                    f"D133 {metadata_key} mismatch for {shard}: "
                    f"{metadata[metadata_key]} != {next_index[key]}"
                )
        if int(metadata["threads"]) != int(spec["threads"]):
            raise RuntimeError(f"wrong D133 thread count for {shard}")

    outputs = {}
    for block in range(BLOCKS):
        block_specs = sorted(
            (spec for spec in specs if int(spec["block_id"]) == block),
            key=lambda spec: int(spec["start_seed"]),
        )
        if len(block_specs) != SHARDS_PER_BLOCK:
            raise RuntimeError(f"D133 block {block} has wrong shard count")
        outputs[str(block)] = {}
        for record_type in ("arms", "baselines"):
            target = _block_file(output_dir, block, record_type)
            header = None
            data_rows = 0
            with target.open("w", encoding="utf-8", newline="") as sink:
                for spec in block_specs:
                    shard = str(spec["shard_id"])
                    part = parts / shard / f"{record_type}.tsv"
                    with part.open(encoding="utf-8", newline="") as source:
                        shard_header = source.readline()
                        if not shard_header:
                            raise RuntimeError(
                                f"empty D133 {record_type} shard: {shard}"
                            )
                        if header is None:
                            header = shard_header
                            sink.write(header)
                        elif shard_header != header:
                            raise RuntimeError(
                                f"inconsistent D133 {record_type} headers"
                            )
                        shutil.copyfileobj(source, sink, length=1024 * 1024)
                    data_rows += next_index[(shard, record_type)] - 1
            outputs[str(block)][record_type] = {
                "path": str(target),
                "rows": data_rows,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
    metadata = [metadata_by_shard[key] for key in sorted(metadata_by_shard)]
    shutil.rmtree(parts)
    return outputs, metadata, table_rows


def download() -> dict:
    lock = verify_lock()
    yt, client, operation, launch_record = _operation()
    state = str(operation.get_state())
    if state != "completed":
        raise RuntimeError(f"D133 operation is not complete: {state}")
    paths = launch_record["paths"]
    outputs, metadata, table_rows = reconstruct_stream(
        client.read_table(paths["records"], format=yt.JsonFormat()),
        LOCAL_OUTPUT,
        launch_record["specs"],
    )
    result = {
        "schema": "troll-farm-d133a-yt-q6-teacher-corpus-download-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "downloaded_utc": utc_now(),
        "operation": {
            "operation_id": launch_record["operation_id"],
            "state": state,
            "paths": paths,
            "table_rows": table_rows,
        },
        "outputs": outputs,
        "mapper_metadata": metadata,
    }
    DOWNLOAD_RECORD.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def _read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def _analyze_block(block: int, artifacts: dict, elapsed: float) -> dict:
    start = START_SEED + block * MAPS_PER_BLOCK
    arms_path = Path(artifacts["arms"]["path"])
    baselines_path = Path(artifacts["baselines"]["path"])
    arms, fields = _read_table(arms_path)
    baselines, _ = _read_table(baselines_path)
    d113.START_SEED = start
    d113.MAPS = MAPS_PER_BLOCK
    mechanics, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms,
        baselines,
        fields,
        elapsed,
        {"pass": True},
    )
    if mechanics["pass"]:
        teacher, labels = d113.teacher_analysis(
            arms, baseline_by_task, arms_by_root
        )
        labels = [{"block_id": block, **row} for row in labels]
        labels_path = LOCAL_OUTPUT / f"block-{block:02d}-labels.tsv"
        d112.write_labels(labels_path, labels)
        label_summary = {
            "path": str(labels_path),
            "rows": len(labels),
            "bytes": labels_path.stat().st_size,
            "sha256": sha256(labels_path),
        }
    else:
        teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "block mechanics failure",
        }
        label_summary = {"path": None, "rows": 0, "bytes": 0, "sha256": None}
    result = {
        "block_id": block,
        "start_seed": start,
        "maps": MAPS_PER_BLOCK,
        "active_seconds_sum": elapsed,
        "mechanics": mechanics,
        "teacher": teacher,
        "labels": label_summary,
        "artifacts": {
            "arms": artifacts["arms"],
            "baselines": artifacts["baselines"],
        },
    }
    del arms, baselines, baseline_by_task, arms_by_root
    gc.collect()
    return result


def _weighted(blocks: list[dict], section: str, field: str, weight: str) -> float:
    numerator = sum(
        block[section][field] * block[section][weight] for block in blocks
    )
    denominator = sum(block[section][weight] for block in blocks)
    return numerator / denominator if denominator else 0.0


def combine_teachers(block_teachers: list[dict]) -> dict:
    """Aggregate D113 teacher sufficient statistics without pooling arm rows."""

    views = [
        {"oracle": teacher["oracle"], "dp": teacher["backward_dp"]}
        for teacher in block_teachers
    ]
    tasks = sum(view["oracle"]["tasks"] for view in views)
    supported = sum(view["oracle"]["supported_tasks"] for view in views)
    strict_count = sum(
        view["oracle"]["strict_improvement_rate"] * view["oracle"]["tasks"]
        for view in views
    )

    def oracle_mean(field: str) -> float:
        return sum(
            view["oracle"][field] * view["oracle"]["tasks"] for view in views
        ) / tasks

    family_means = {
        opponent: sum(
            view["oracle"]["family_mean_margin_gain"][opponent]
            for view in views
        )
        / len(views)
        for opponent in d112.OPPONENTS
    }
    selected_boundary_numerator = sum(
        view["oracle"]["mean_selected_boundary"]
        * view["oracle"]["strict_improvement_rate"]
        * view["oracle"]["tasks"]
        for view in views
    )
    kind_counts = Counter()
    for view in views:
        kind_counts.update(
            {int(key): value for key, value in view["oracle"]["selected_kind_counts"].items()}
        )
    oracle = {
        "tasks": tasks,
        "supported_tasks": supported,
        "mean_margin_gain": oracle_mean("mean_margin_gain"),
        "strict_improvement_rate": strict_count / tasks,
        "mean_own_score_gain": oracle_mean("mean_own_score_gain"),
        "mean_opponent_score_delta": oracle_mean("mean_opponent_score_delta"),
        "family_mean_margin_gain": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family": min(family_means.values()),
        "intervention_rate": strict_count / tasks,
        "mean_selected_boundary": (
            selected_boundary_numerator / strict_count if strict_count else 0.0
        ),
        "selected_kind_counts": dict(sorted(kind_counts.items())),
        "first_boundary_oracle_mean_gain": oracle_mean(
            "first_boundary_oracle_mean_gain"
        ),
        "crop_rate": oracle_mean("crop_rate"),
        "worker_three_rate": oracle_mean("worker_three_rate"),
        "control_worker_three_rate": oracle_mean("control_worker_three_rate"),
    }
    oracle["later_boundary_increment"] = (
        oracle["mean_margin_gain"] - oracle["first_boundary_oracle_mean_gain"]
    )

    roots = sum(view["dp"]["roots"] for view in views)
    arms = sum(view["dp"]["arms"] for view in views)
    act = sum(view["dp"]["act_now_roots"] for view in views)
    positive = sum(view["dp"]["positive_arm_advantages"] for view in views)
    negative = sum(view["dp"]["negative_arm_advantages"] for view in views)
    zero = sum(view["dp"]["zero_arm_advantages"] for view in views)
    target_mean = sum(
        view["dp"]["target_mean"] * view["dp"]["arms"] for view in views
    ) / arms
    target_second_moment = sum(
        (
            view["dp"]["target_standard_deviation"] ** 2
            + view["dp"]["target_mean"] ** 2
        )
        * view["dp"]["arms"]
        for view in views
    ) / arms
    target_variance = max(0.0, target_second_moment - target_mean**2)
    dp = {
        "roots": roots,
        "arms": arms,
        "act_now_roots": act,
        "wait_roots": roots - act,
        "act_now_root_rate": act / roots,
        "positive_arm_advantages": positive,
        "negative_arm_advantages": negative,
        "zero_arm_advantages": zero,
        "positive_arm_advantage_rate": positive / arms,
        "negative_arm_advantage_rate": negative / arms,
        "target_mean": target_mean,
        "target_standard_deviation": math.sqrt(target_variance),
        "target_minimum": min(view["dp"]["target_minimum"] for view in views),
        "target_maximum": max(view["dp"]["target_maximum"] for view in views),
        "best_now_mean": sum(
            view["dp"]["best_now_mean"] * view["dp"]["roots"]
            for view in views
        )
        / roots,
    }
    signal_gates = {
        "oracle_mean_at_least_20": oracle["mean_margin_gain"] >= 20.0,
        "oracle_strict_at_least_75pct": oracle["strict_improvement_rate"] >= 0.75,
        "at_least_seven_positive_families": oracle["positive_families"] >= 7,
        "worst_family_at_least_8": oracle["worst_family"] >= 8.0,
        "own_nonnegative_or_opponent_nonpositive": (
            oracle["mean_own_score_gain"] >= 0.0
            or oracle["mean_opponent_score_delta"] <= 0.0
        ),
        "act_now_roots_5_to_90pct": 0.05 <= dp["act_now_root_rate"] <= 0.90,
        "positive_arm_targets_1_to_50pct": (
            0.01 <= dp["positive_arm_advantage_rate"] <= 0.50
        ),
        "negative_arm_targets_at_least_40pct": (
            dp["negative_arm_advantage_rate"] >= 0.40
        ),
        "target_stddev_at_least_5": dp["target_standard_deviation"] >= 5.0,
    }
    safety_gates = {
        "oracle_crop_100pct": oracle["crop_rate"] == 1.0,
        "oracle_worker_three_within_5pp": (
            oracle["worker_three_rate"]
            >= oracle["control_worker_three_rate"] - 0.05
        ),
    }
    return {
        "oracle": oracle,
        "backward_dp": dp,
        "signal_gates": signal_gates,
        "signal_pass": all(signal_gates.values()),
        "safety_gates": safety_gates,
        "safety_pass": all(safety_gates.values()),
    }


def analyze() -> dict:
    lock = verify_lock()
    download_record = json.loads(DOWNLOAD_RECORD.read_text())
    if download_record["operation"]["state"] != "completed":
        raise RuntimeError("D133 download record is not from a completed operation")
    for artifacts in download_record["outputs"].values():
        for summary in artifacts.values():
            path = Path(summary["path"])
            if sha256(path) != summary["sha256"]:
                raise RuntimeError(f"D133 downloaded artifact changed: {path}")

    metadata = download_record["mapper_metadata"]
    metadata_by_block: dict[int, list[dict]] = defaultdict(list)
    shard_rates = {}
    for item in metadata:
        metadata_by_block[int(item["block_id"])].append(item)
        arm_rows = int(item["arm_lines"]) - 1
        elapsed = float(item["elapsed_seconds"])
        shard_rates[str(item["shard_id"])] = arm_rows / elapsed

    blocks = []
    for block in range(BLOCKS):
        elapsed = sum(
            float(item["elapsed_seconds"]) for item in metadata_by_block[block]
        )
        blocks.append(
            _analyze_block(
                block,
                download_record["outputs"][str(block)],
                elapsed,
            )
        )

    block_mechanics = [block["mechanics"] for block in blocks]
    total_baselines = sum(
        block["mechanics"]["details"]["baselines"] for block in blocks
    )
    total_roots = sum(block["mechanics"]["details"]["roots"] for block in blocks)
    total_arms = sum(block["mechanics"]["details"]["arms"] for block in blocks)
    supported_tasks = sum(
        block["mechanics"]["details"]["supported_tasks"] for block in blocks
    )
    infrastructure_gates = {
        "operation_completed": download_record["operation"]["state"] == "completed",
        "exactly_16_mapper_metadata_rows": len(metadata) == BLOCKS * SHARDS_PER_BLOCK,
        "exact_prescribed_shards": {item["shard_id"] for item in metadata}
        == {spec["shard_id"] for spec in build_specs()},
        "every_shard_at_most_900_active_seconds": all(
            float(item["elapsed_seconds"]) <= MAX_SHARD_ACTIVE_SECONDS
            for item in metadata
        ),
        "every_shard_at_least_12_arms_per_second": all(
            value >= MIN_SHARD_ARMS_PER_SECOND for value in shard_rates.values()
        ),
        "every_shard_used_16_threads": all(
            int(item["threads"]) == THREADS for item in metadata
        ),
    }
    mechanics_gates = {
        "all_four_blocks_pass_inherited_mechanics": (
            len(blocks) == BLOCKS and all(item["pass"] for item in block_mechanics)
        ),
        "exactly_1024_baselines": total_baselines == EXPECTED_TASKS,
        "at_least_80000_arms": total_arms >= MIN_ARMS,
        "at_least_4800_roots": total_roots >= MIN_ROOTS,
        "global_support_at_least_90pct": supported_tasks / EXPECTED_TASKS >= 0.90,
        "each_block_has_256_baselines": all(
            block["mechanics"]["details"]["baselines"]
            == EXPECTED_BASELINES_PER_BLOCK
            for block in blocks
        ),
        "each_block_support_at_least_90pct": all(
            block["mechanics"]["details"]["task_support_rate"] >= 0.90
            for block in blocks
        ),
    }
    if all(mechanics_gates.values()):
        aggregate_teacher = combine_teachers([block["teacher"] for block in blocks])
    else:
        aggregate_teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D133 infrastructure/mechanics failure",
        }
    full_pass = (
        all(infrastructure_gates.values())
        and all(mechanics_gates.values())
        and aggregate_teacher["signal_pass"]
        and aggregate_teacher["safety_pass"]
    )
    result = {
        "schema": "troll-farm-d133a-yt-q6-independent-block-corpus-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": download_record["operation"],
        "panel": {
            "start_seed": START_SEED,
            "maps": MAPS,
            "blocks": BLOCKS,
            "tasks": EXPECTED_TASKS,
        },
        "infrastructure": {
            "gates": infrastructure_gates,
            "pass": all(infrastructure_gates.values()),
            "shard_arms_per_second": shard_rates,
            "metadata": metadata,
        },
        "mechanics": {
            "gates": mechanics_gates,
            "pass": all(mechanics_gates.values()),
            "details": {
                "baselines": total_baselines,
                "supported_tasks": supported_tasks,
                "task_support_rate": supported_tasks / EXPECTED_TASKS,
                "roots": total_roots,
                "arms": total_arms,
            },
        },
        "teacher": aggregate_teacher,
        "blocks": blocks,
        "full_pass": full_pass,
        "decision": (
            "open_d134_leave_one_block_out_training"
            if full_pass
            else "repair_d133_infrastructure_or_mechanics_only"
            if not (
                all(infrastructure_gates.values()) and all(mechanics_gates.values())
            )
            else "close_d133_corpus_for_q6_learner_selection"
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
    sub.add_parser("analyze")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "launch":
        launch(asynchronous=not args.sync)
    elif args.command == "status":
        status()
    elif args.command == "download":
        download()
    else:
        analyze()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
