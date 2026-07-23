#!/usr/bin/env python3
"""Launch, reconstruct, and analyze D139's second independent q6 corpus."""

from __future__ import annotations

import argparse
from collections import defaultdict
import gc
import json
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto import analyze_d133b_q6_support_semantics as d133b
from cgauto import yt_d133_q6_teacher_corpus as d133


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d139a-yt-q6-second-independent-corpus-protocol-2026-07-22.md"
LOCK = BASE / "d139a-yt-q6-second-independent-corpus-lock.json"
LAUNCH_RECORD = BASE / "d139a-yt-q6-second-independent-corpus-launch.json"
DOWNLOAD_RECORD = BASE / "d139a-yt-q6-second-independent-corpus-download.json"
OUTPUT = BASE / "d139a-yt-q6-second-independent-corpus-result.json"
LOCAL_OUTPUT = BASE / "yt" / "d139a-q6-second-independent-corpus"

YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d139a_q6_second_corpus_9844064_9844127_20260722"
START_SEED = 9_844_064
MAPS = 64
BLOCKS = 4

_ORIGINAL_BACKEND = {
    name: getattr(d133, name)
    for name in (
        "PROTOCOL",
        "LOCK",
        "LAUNCH_RECORD",
        "DOWNLOAD_RECORD",
        "OUTPUT",
        "LOCAL_OUTPUT",
        "YT_ROOT",
        "BUILD_NAME",
        "START_SEED",
        "MAPS",
        "BLOCKS",
        "EXPECTED_TASKS",
        "build_paths",
    )
}


def configure_backend() -> None:
    d133.PROTOCOL = PROTOCOL
    d133.LOCK = LOCK
    d133.LAUNCH_RECORD = LAUNCH_RECORD
    d133.DOWNLOAD_RECORD = DOWNLOAD_RECORD
    d133.OUTPUT = OUTPUT
    d133.LOCAL_OUTPUT = LOCAL_OUTPUT
    d133.YT_ROOT = YT_ROOT
    d133.BUILD_NAME = BUILD_NAME
    d133.START_SEED = START_SEED
    d133.MAPS = MAPS
    d133.BLOCKS = BLOCKS
    d133.EXPECTED_TASKS = MAPS * 2 * len(d112.OPPONENTS)
    original_build_paths = _ORIGINAL_BACKEND["build_paths"]
    d133.build_paths = lambda root=YT_ROOT, build_name=BUILD_NAME: original_build_paths(
        root, build_name
    )


def restore_backend() -> None:
    for name, value in _ORIGINAL_BACKEND.items():
        setattr(d133, name, value)


def sha256(path: Path) -> str:
    return d133.sha256(path)


def verify_lock() -> dict:
    configure_backend()
    return d133.verify_lock()


def _rewrite_record(path: Path, record: dict, schema: str) -> dict:
    record["schema"] = schema
    record["protocol"] = str(PROTOCOL.relative_to(ROOT))
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def launch(*, asynchronous: bool = True) -> dict:
    configure_backend()
    record = d133.launch(asynchronous=asynchronous)
    return _rewrite_record(
        LAUNCH_RECORD,
        record,
        "troll-farm-d139a-yt-q6-second-independent-corpus-launch-v1",
    )


def status() -> dict:
    configure_backend()
    return d133.status()


def download() -> dict:
    configure_backend()
    record = d133.download()
    return _rewrite_record(
        DOWNLOAD_RECORD,
        record,
        "troll-farm-d139a-yt-q6-second-independent-corpus-download-v1",
    )


def repaired_block(block: int, artifacts: dict, elapsed: float) -> dict:
    start = START_SEED + block * d133.MAPS_PER_BLOCK
    arms_path = Path(artifacts["arms"]["path"])
    baselines_path = Path(artifacts["baselines"]["path"])
    arms, fields = d133._read_table(arms_path)
    baselines, _ = d133._read_table(baselines_path)
    d113.START_SEED = start
    d113.MAPS = d133.MAPS_PER_BLOCK
    inherited, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms, baselines, fields, elapsed, {"pass": True}
    )
    mechanics = d133b.exact_mechanics_without_support_gate(inherited)
    if mechanics["pass"]:
        teacher, labels = d113.teacher_analysis(
            arms, baseline_by_task, arms_by_root
        )
        labels = [{"block_id": block + 4, **row} for row in labels]
        labels_path = LOCAL_OUTPUT / f"block-{block + 4:02d}-labels.tsv"
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
            "not_interpreted": "exact nonavailability mechanics failure",
        }
        label_summary = {"path": None, "rows": 0, "bytes": 0, "sha256": None}
    result = {
        "block_id": block + 4,
        "local_block_id": block,
        "start_seed": start,
        "maps": d133.MAPS_PER_BLOCK,
        "active_seconds_sum": elapsed,
        "mechanics": mechanics,
        "teacher": teacher,
        "labels": label_summary,
        "artifacts": artifacts,
    }
    del arms, baselines, baseline_by_task, arms_by_root
    gc.collect()
    return result


def analyze() -> dict:
    configure_backend()
    lock = verify_lock()
    download_record = json.loads(DOWNLOAD_RECORD.read_text())
    if download_record["operation"]["state"] != "completed":
        raise RuntimeError("D139 download is not from a completed operation")
    for artifacts in download_record["outputs"].values():
        for summary in artifacts.values():
            path = Path(summary["path"])
            if sha256(path) != summary["sha256"]:
                raise RuntimeError(f"D139 downloaded artifact changed: {path}")

    metadata = download_record["mapper_metadata"]
    metadata_by_block: dict[int, list[dict]] = defaultdict(list)
    shard_rates = {}
    for item in metadata:
        metadata_by_block[int(item["block_id"])].append(item)
        arms = int(item["arm_lines"]) - 1
        elapsed = float(item["elapsed_seconds"])
        shard_rates[str(item["shard_id"])] = arms / elapsed

    blocks = []
    for block in range(BLOCKS):
        elapsed = sum(
            float(item["elapsed_seconds"])
            for item in metadata_by_block[block]
        )
        blocks.append(
            repaired_block(
                block, download_record["outputs"][str(block)], elapsed
            )
        )

    total_baselines = sum(
        block["mechanics"]["details"]["baselines"] for block in blocks
    )
    total_roots = sum(
        block["mechanics"]["details"]["roots"] for block in blocks
    )
    total_arms = sum(
        block["mechanics"]["details"]["arms"] for block in blocks
    )
    supported = sum(
        block["mechanics"]["details"]["supported_tasks"] for block in blocks
    )
    infrastructure_gates = {
        "operation_completed": download_record["operation"]["state"] == "completed",
        "exactly_16_mapper_metadata_rows": len(metadata)
        == BLOCKS * d133.SHARDS_PER_BLOCK,
        "exact_prescribed_shards": {item["shard_id"] for item in metadata}
        == {spec["shard_id"] for spec in d133.build_specs()},
        "every_shard_at_most_900_active_seconds": all(
            float(item["elapsed_seconds"]) <= d133.MAX_SHARD_ACTIVE_SECONDS
            for item in metadata
        ),
        "every_shard_at_least_12_arms_per_second": all(
            rate >= d133.MIN_SHARD_ARMS_PER_SECOND
            for rate in shard_rates.values()
        ),
        "every_shard_used_16_threads": all(
            int(item["threads"]) == d133.THREADS for item in metadata
        ),
    }
    mechanics_gates = {
        "all_four_blocks_pass_exact_nonavailability_mechanics": all(
            block["mechanics"]["pass"] for block in blocks
        ),
        "exactly_1024_baselines": total_baselines == d133.EXPECTED_TASKS,
        "at_least_80000_arms": total_arms >= d133.MIN_ARMS,
        "at_least_4800_roots": total_roots >= d133.MIN_ROOTS,
        "each_block_has_256_baselines": all(
            block["mechanics"]["details"]["baselines"]
            == d133.EXPECTED_BASELINES_PER_BLOCK
            for block in blocks
        ),
    }
    mechanics_pass = all(mechanics_gates.values())
    teacher = (
        d133.combine_teachers([block["teacher"] for block in blocks])
        if mechanics_pass
        else {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D139 exact mechanics failure",
        }
    )
    full_pass = (
        all(infrastructure_gates.values())
        and mechanics_pass
        and teacher["signal_pass"]
        and teacher["safety_pass"]
    )
    result = {
        "schema": "troll-farm-d139a-yt-q6-second-independent-corpus-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": download_record["operation"],
        "panel": {
            "start_seed": START_SEED,
            "maps": MAPS,
            "blocks": BLOCKS,
            "global_block_ids": [4, 5, 6, 7],
            "tasks": d133.EXPECTED_TASKS,
        },
        "infrastructure": {
            "gates": infrastructure_gates,
            "pass": all(infrastructure_gates.values()),
            "shard_arms_per_second": shard_rates,
            "metadata": metadata,
        },
        "mechanics": {
            "gates": mechanics_gates,
            "pass": mechanics_pass,
            "details": {
                "baselines": total_baselines,
                "supported_tasks": supported,
                "task_support_rate": supported / d133.EXPECTED_TASKS,
                "roots": total_roots,
                "arms": total_arms,
                "support_by_block": [
                    block["mechanics"]["details"]["supported_tasks"]
                    for block in blocks
                ],
            },
        },
        "teacher": teacher,
        "blocks": blocks,
        "full_pass": full_pass,
        "decision": (
            "open_frozen_eight_block_learner_selection"
            if full_pass
            else "repair_d139_infrastructure_or_exact_mechanics_only"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("launch", "status", "download", "analyze"))
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
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
