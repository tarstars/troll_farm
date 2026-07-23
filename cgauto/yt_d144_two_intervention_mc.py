#!/usr/bin/env python3
"""Launch, reconstruct, and analyze D144's two-intervention MC pilot."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Iterable

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto.run_d144a_two_intervention_mc_pilot import (
    FIELDS as MC_FIELDS,
    TASKS_PER_MAP,
    episode_spec,
    expected_task,
    update_selection_hash,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d144a-two-intervention-mc-pilot-protocol-2026-07-22.md"
LOCK = BASE / "d144a-two-intervention-mc-pilot-repair1-lock.json"
LAUNCH_RECORD = BASE / "d144a-two-intervention-mc-pilot-repair1-launch.json"
DOWNLOAD_RECORD = BASE / "d144a-two-intervention-mc-pilot-repair1-download.json"
OUTPUT = BASE / "d144a-two-intervention-mc-pilot-result.json"
LOCAL_OUTPUT = BASE / "yt" / "d144a-two-intervention-mc-pilot"

MATH_SRC = Path("/home/tarstars/prj/math_through_eml/src")
MAPPER = ROOT / "cgauto" / "yt_d144_two_intervention_mc_mapper.py"
DRIVER = ROOT / "cgauto" / "run_d144a_two_intervention_mc_pilot.py"
Q6_WRAPPER = ROOT / "cgauto" / "rl_q6_proposal_env.py"
MACRO_WRAPPER = ROOT / "cgauto" / "rl_macro_env.py"
LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
BINARY = ROOT / "rust" / "target" / "release" / "d112_q6_dense_counterfactual_teacher"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
NUMPY_RUNTIME = BASE / "yt" / "d144a-numpy-2.2.6-py310-runtime.tar.gz"

YT_PROXY = "watt.yt.yandex.net"
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
BUILD_NAME = "d144a_two_intervention_mc_9844128_9844135_repair1_20260722"
LAYER_PATHS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)

START_SEED = 9_844_128
MAPS = 8
TASKS = MAPS * TASKS_PER_MAP
REPLICAS = 128
SINGLE_REPLICAS = 16
DOUBLE_REPLICAS = REPLICAS - SINGLE_REPLICAS - 1
THREADS = 16
MC_MAX_ACTIVE_SECONDS = 2_700.0
MC_MIN_EPISODES_PER_SECOND = 5.0
EXACT_MAX_ACTIVE_SECONDS = 900.0
EXACT_MIN_ARMS_PER_SECOND = 12.0
EXPECTED_EPISODES = TASKS * REPLICAS

LIBRARY_SHA256 = "90284b35574e78740bdd1b1f81ea6ba5fdf03265a5ef029f1667a676748835cf"
BINARY_SHA256 = "5bed211a33393f041221dcda81bdd2bf5d11522ad1aa3978fe4d3b79492f6d02"
EXPERT_SHA256 = "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8"
NUMPY_RUNTIME_SHA256 = "7ef9f486b6824ef3f46c7f88bec9f033575c86f0f3f2ba37dc6943f46f8678d8"


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
    return [
        {
            "shard_id": label,
            "kind": "mc",
            "start_seed": START_SEED,
            "maps": MAPS,
            "replicas": REPLICAS,
            "single_replicas": SINGLE_REPLICAS,
            "threads": THREADS,
        }
        for label in ("mc-a", "mc-b")
    ] + [
        {
            "shard_id": f"exact-{index:02d}",
            "kind": "exact",
            "start_seed": START_SEED + index * 4,
            "maps": 4,
            "threads": THREADS,
        }
        for index in range(2)
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
        raise RuntimeError(f"D144 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def _verify_payload() -> None:
    actual = {
        "library": sha256(LIBRARY),
        "binary": sha256(BINARY),
        "experts": sha256(EXPERTS),
        "numpy_runtime": sha256(NUMPY_RUNTIME),
    }
    expected = {
        "library": LIBRARY_SHA256,
        "binary": BINARY_SHA256,
        "experts": EXPERT_SHA256,
        "numpy_runtime": NUMPY_RUNTIME_SHA256,
    }
    if actual != expected:
        raise RuntimeError(f"D144 payload hashes changed: {actual!r}")


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
    _verify_payload()
    yt, LocalFile, client = _load_yt()
    paths = build_paths()
    specs = build_specs()
    if client.exists(paths["build"]):
        raise RuntimeError(f"D144 YT build already exists: {paths['build']}")
    client.create("map_node", paths["build"], recursive=True)
    _write_specs_as_chunks(yt, client, paths["specs"], specs)
    operation_spec = {
        "max_failed_job_count": 1,
        "title": "Troll Farm D144 two-intervention MC pilot",
        "pool": "delivery-ml",
        "mapper": {
            "cpu_limit": THREADS,
            "environment": {
                "TF_D144_THREADS": str(THREADS),
                "RAYON_NUM_THREADS": str(THREADS),
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            },
            "layer_paths": list(LAYER_PATHS),
        },
    }
    local_files = [
        LocalFile(str(MAPPER), file_name=MAPPER.name),
        LocalFile(str(DRIVER), file_name=DRIVER.name),
        LocalFile(str(Q6_WRAPPER), file_name=Q6_WRAPPER.name),
        LocalFile(str(MACRO_WRAPPER), file_name=MACRO_WRAPPER.name),
        LocalFile(str(LIBRARY), file_name=LIBRARY.name),
        LocalFile(str(BINARY), file_name=BINARY.name),
        LocalFile(str(EXPERTS), file_name=EXPERTS.name),
        LocalFile(str(NUMPY_RUNTIME), file_name="d144_numpy_runtime.tar.gz"),
    ]
    operation = client.run_map(
        f"python3 {MAPPER.name}",
        paths["specs"],
        paths["records"],
        local_files=local_files,
        input_format=yt.JsonFormat(),
        output_format=yt.JsonFormat(),
        job_count=len(specs),
        memory_limit=8 * 1024**3,
        spec=operation_spec,
        sync=not asynchronous,
    )
    record = {
        "schema": "troll-farm-d144a-two-intervention-mc-launch-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "launched_utc": utc_now(),
        "operation_id": str(operation.id),
        "paths": paths,
        "specs": specs,
        "job_count": len(specs),
        "layer_paths": LAYER_PATHS,
        "payload": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                MAPPER,
                DRIVER,
                Q6_WRAPPER,
                MACRO_WRAPPER,
                LIBRARY,
                BINARY,
                EXPERTS,
                NUMPY_RUNTIME,
            )
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
        raise RuntimeError("duplicate D144 shard ids")
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
                raise RuntimeError(f"unexpected D144 shard: {shard}")
            spec = expected[shard]
            if int(row["start_seed"]) != int(spec["start_seed"]):
                raise RuntimeError(f"D144 start seed drift for {shard}")
            if record_type == "metadata":
                if shard in metadata_by_shard or int(row["row_index"]) != 0:
                    raise RuntimeError(f"duplicate or malformed D144 metadata: {shard}")
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
            allowed = {"mc"} if spec["kind"] == "mc" else {"arms", "baselines"}
            if record_type not in allowed:
                raise RuntimeError(f"unexpected D144 record type for {shard}: {record_type}")
            key = (shard, record_type)
            row_index = int(row["row_index"])
            if row_index != next_index[key]:
                raise RuntimeError(
                    f"noncontiguous D144 rows for {key}: "
                    f"expected {next_index[key]}, got {row_index}"
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
        raise RuntimeError(
            f"missing D144 metadata: {sorted(set(expected) - set(metadata_by_shard))}"
        )
    for shard, spec in expected.items():
        metadata = metadata_by_shard[shard]
        if metadata["kind"] != spec["kind"] or int(metadata["threads"]) != int(
            spec["threads"]
        ):
            raise RuntimeError(f"D144 metadata/spec drift for {shard}")
        record_types = ("mc",) if spec["kind"] == "mc" else ("arms", "baselines")
        for record_type in record_types:
            key = (shard, record_type)
            if next_index[key] < 1:
                raise RuntimeError(f"D144 {shard} lacks {record_type}")
            if int(metadata["line_counts"][record_type]) != next_index[key]:
                raise RuntimeError(f"D144 line-count drift for {key}")

    outputs = {}
    end_seed = START_SEED + MAPS - 1
    for label in ("mc-a", "mc-b"):
        source = parts / label / "mc.tsv"
        target = output_dir / f"d144a-{label}-{START_SEED}-{end_seed}.tsv"
        shutil.copyfile(source, target)
        outputs[label] = _artifact(target, next_index[(label, "mc")] - 1)
    exact_specs = sorted(
        (spec for spec in specs if spec["kind"] == "exact"),
        key=lambda spec: int(spec["start_seed"]),
    )
    for record_type in ("arms", "baselines"):
        target = output_dir / f"d144a-exact-{record_type}-{START_SEED}-{end_seed}.tsv"
        header = None
        data_rows = 0
        with target.open("x", encoding="utf-8", newline="") as sink:
            for spec in exact_specs:
                shard = str(spec["shard_id"])
                source = parts / shard / f"{record_type}.tsv"
                with source.open(encoding="utf-8", newline="") as part:
                    shard_header = part.readline()
                    if not shard_header:
                        raise RuntimeError(f"empty D144 {record_type} shard: {shard}")
                    if header is None:
                        header = shard_header
                        sink.write(header)
                    elif header != shard_header:
                        raise RuntimeError(f"inconsistent D144 {record_type} header")
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
        raise RuntimeError(f"D144 operation is not complete: {state}")
    outputs, metadata, table_rows = reconstruct_stream(
        client.read_table(launch_record["paths"]["records"], format=yt.JsonFormat()),
        LOCAL_OUTPUT,
        launch_record["specs"],
    )
    result = {
        "schema": "troll-farm-d144a-two-intervention-mc-download-v1",
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


def _read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def _task(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def _margin(row: dict[str, str]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def _mc_mechanics(
    rows: list[dict[str, str]],
    fields: list[str],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
    arms: list[dict[str, str]],
) -> dict:
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAPS)
        for seat in range(2)
        for opponent in d112.OPPONENTS
    }
    task_indices = Counter(int(row["task_index"]) for row in rows)
    mode_counts = Counter(row["mode"] for row in rows)
    task_mode_counts = Counter((_task(row), row["mode"]) for row in rows)
    failures = {
        field: sum(int(row[field]) for row in rows)
        for field in d112.FAILURE_FIELDS
    }
    semantic_errors = []
    for row in rows:
        index = int(row["task_index"])
        spec = episode_spec(index, TASKS, SINGLE_REPLICAS)
        expected = expected_task(START_SEED, spec["scenario"])
        interventions = int(row["intervention_batches"])
        valid = (
            int(row["scenario"]) == spec["scenario"]
            and int(row["replica"]) == spec["replica"]
            and row["mode"] == spec["mode"]
            and int(row["scheduled_first_boundary"]) == spec["first"]
            and int(row["scheduled_second_boundary"]) == spec["second"]
            and _task(row) == expected
            and int(row["margin"]) == _margin(row)
            and int(row["baseline_margin"])
            == int(row["baseline_own_score"]) - int(row["baseline_opponent_score"])
            and int(row["margin_delta"])
            == int(row["margin"]) - int(row["baseline_margin"])
            and 0 <= interventions <= (0 if spec["mode"] == "control" else 1 if spec["mode"] == "single" else 2)
        )
        if interventions >= 1:
            valid = valid and (
                int(row["first_selected_boundary"]) == spec["first"]
                and int(row["first_selected_slot"]) > 0
            )
        else:
            valid = valid and int(row["first_selected_boundary"]) == -1
        if interventions == 2:
            valid = valid and (
                int(row["second_selected_boundary"]) == spec["second"]
                and int(row["second_selected_slot"]) > 0
            )
        else:
            valid = valid and int(row["second_selected_boundary"]) == -1
        expected_hash = 0
        if interventions >= 1:
            expected_hash = update_selection_hash(
                expected_hash,
                int(row["first_selected_boundary"]),
                int(row["first_selected_slot"]),
            )
        if interventions == 2:
            expected_hash = update_selection_hash(
                expected_hash,
                int(row["second_selected_boundary"]),
                int(row["second_selected_slot"]),
            )
        valid = valid and int(row["selection_hash"]) == expected_hash
        if not valid:
            semantic_errors.append(index)

    controls = [row for row in rows if row["mode"] == "control"]
    control_by_task = {_task(row): row for row in controls}
    control_errors = []
    comparable_fields = (
        "own_score",
        "opponent_score",
        "margin",
        "own_workers",
        "successful_trains",
        "own_created_crops",
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
        "action_hash",
        "state_hash",
    )
    for task, baseline in baseline_by_task.items():
        row = control_by_task.get(task)
        if row is None or any(str(row[field]) != str(baseline[field]) for field in comparable_fields):
            control_errors.append(task)
        elif int(row["margin_delta"]) != 0:
            control_errors.append(task)

    arm_by_key = {
        (_task(row), int(row["boundary_index"]), int(row["slot"])): row
        for row in arms
    }
    single_errors = []
    single_selected = 0
    single_fields = comparable_fields + (
        "intervention_batches",
        "joint_batches",
        "noncontrol_assignments",
    )
    for row in rows:
        if row["mode"] != "single" or int(row["intervention_batches"]) != 1:
            continue
        single_selected += 1
        arm = arm_by_key.get(
            (
                _task(row),
                int(row["first_selected_boundary"]),
                int(row["first_selected_slot"]),
            )
        )
        if arm is None or any(str(row[field]) != str(arm[field]) for field in single_fields):
            single_errors.append(int(row["task_index"]))

    double_rows = [row for row in rows if row["mode"] == "double"]
    two_rows = [row for row in double_rows if int(row["intervention_batches"]) == 2]
    tasks_with_two = {_task(row) for row in two_rows}
    gates = {
        "exact_mc_schema": fields == list(MC_FIELDS),
        "complete_unique_episode_grid": (
            len(rows) == EXPECTED_EPISODES
            and set(task_indices) == set(range(EXPECTED_EPISODES))
            and all(value == 1 for value in task_indices.values())
        ),
        "exact_mode_counts": mode_counts
        == {
            "control": TASKS,
            "single": TASKS * SINGLE_REPLICAS,
            "double": TASKS * DOUBLE_REPLICAS,
        },
        "exact_per_task_mode_counts": (
            set(control_by_task) == expected_tasks
            and all(task_mode_counts[(task, "control")] == 1 for task in expected_tasks)
            and all(
                task_mode_counts[(task, "single")] == SINGLE_REPLICAS
                for task in expected_tasks
            )
            and all(
                task_mode_counts[(task, "double")] == DOUBLE_REPLICAS
                for task in expected_tasks
            )
        ),
        "schedule_mapping_hash_and_caps_exact": not semantic_errors,
        "zero_mechanical_failures": all(value == 0 for value in failures.values()),
        "control_exactly_matches_dense_baseline": not control_errors,
        "selected_single_episodes_match_dense_arms": single_selected > 0 and not single_errors,
        "at_least_40pct_double_episodes_reach_two_interventions": (
            len(two_rows) / len(double_rows) >= 0.40
        ),
        "at_least_95pct_tasks_have_sampled_two_interventions": (
            len(tasks_with_two) / TASKS >= 0.95
        ),
    }
    return {
        "gates": gates,
        "pass": all(gates.values()),
        "details": {
            "episodes": len(rows),
            "mode_counts": dict(mode_counts),
            "intervention_counts": dict(
                Counter(int(row["intervention_batches"]) for row in rows)
            ),
            "double_episodes": len(double_rows),
            "two_intervention_episodes": len(two_rows),
            "two_intervention_rate_within_double": len(two_rows) / len(double_rows),
            "tasks_with_two_interventions": len(tasks_with_two),
            "task_two_intervention_coverage": len(tasks_with_two) / TASKS,
            "selected_single_episodes": single_selected,
            "mechanical_failures": failures,
            "error_samples": {
                "semantic": semantic_errors[:10],
                "control": [str(item) for item in control_errors[:10]],
                "single": single_errors[:10],
            },
        },
    }


def _outcome_key(row: dict[str, str], control: dict[str, str], tie: int) -> tuple:
    return (
        _margin(row) - _margin(control),
        int(row["own_score"]) - int(control["own_score"]),
        -(int(row["opponent_score"]) - int(control["opponent_score"])),
        -tie,
    )


def _incremental_oracle(
    mc_rows: list[dict[str, str]],
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    arms_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    doubles_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        arms_by_task[_task(row)].append(row)
    for row in mc_rows:
        if row["mode"] == "double" and int(row["intervention_batches"]) == 2:
            doubles_by_task[_task(row)].append(row)

    enriched = []
    for task in sorted(baseline_by_task):
        control = baseline_by_task[task]
        one_rows = arms_by_task.get(task, [])
        best_one = (
            max(one_rows, key=lambda row: d112.tie_key(row, control))
            if one_rows
            else control
        )
        if _margin(best_one) <= _margin(control):
            best_one = control
        double_rows = doubles_by_task.get(task, [])
        best_double = (
            max(
                double_rows,
                key=lambda row: _outcome_key(row, control, int(row["replica"])),
            )
            if double_rows
            else control
        )
        selected = best_double if _margin(best_double) > _margin(best_one) else best_one
        one_gain = _margin(best_one) - _margin(control)
        combined_gain = _margin(selected) - _margin(control)
        increment = combined_gain - one_gain
        enriched.append(
            {
                "task": task,
                "opponent": task[2],
                "one_gain": one_gain,
                "combined_gain": combined_gain,
                "increment": increment,
                "strict": increment > 0,
                "selected_double": selected is best_double and best_double is not control,
                "own_increment": int(selected["own_score"]) - int(best_one["own_score"]),
                "opponent_increment": int(selected["opponent_score"])
                - int(best_one["opponent_score"]),
                "one_crop": int(best_one["own_created_crops"]) > 0,
                "combined_crop": int(selected["own_created_crops"]) > 0,
                "one_worker_three": int(best_one["own_workers"]) >= 3,
                "combined_worker_three": int(selected["own_workers"]) >= 3,
                "double_samples": len(double_rows),
            }
        )
    mean = d112.mean
    family_increment = {
        opponent: mean(
            item["increment"] for item in enriched if item["opponent"] == opponent
        )
        for opponent in d112.OPPONENTS
    }
    summary = {
        "tasks": len(enriched),
        "mean_one_use_oracle_gain": mean(item["one_gain"] for item in enriched),
        "mean_combined_oracle_gain": mean(item["combined_gain"] for item in enriched),
        "mean_increment_beyond_one_use": mean(item["increment"] for item in enriched),
        "strict_increment_rate": mean(item["strict"] for item in enriched),
        "strict_increment_tasks": sum(item["strict"] for item in enriched),
        "selected_double_rate": mean(item["selected_double"] for item in enriched),
        "mean_own_score_increment": mean(item["own_increment"] for item in enriched),
        "mean_opponent_score_increment": mean(
            item["opponent_increment"] for item in enriched
        ),
        "family_mean_increment": family_increment,
        "positive_families": sum(value > 0 for value in family_increment.values()),
        "worst_family_increment": min(family_increment.values()),
        "one_use_crop_rate": mean(item["one_crop"] for item in enriched),
        "combined_crop_rate": mean(item["combined_crop"] for item in enriched),
        "new_crop_failures": sum(
            item["one_crop"] and not item["combined_crop"] for item in enriched
        ),
        "one_use_worker_three_rate": mean(
            item["one_worker_three"] for item in enriched
        ),
        "combined_worker_three_rate": mean(
            item["combined_worker_three"] for item in enriched
        ),
        "minimum_two_intervention_samples_per_task": min(
            item["double_samples"] for item in enriched
        ),
        "mean_two_intervention_samples_per_task": mean(
            item["double_samples"] for item in enriched
        ),
    }
    signal_gates = {
        "increment_mean_at_least_3": summary["mean_increment_beyond_one_use"] >= 3.0,
        "strict_increment_at_least_20pct": summary["strict_increment_rate"] >= 0.20,
        "at_least_six_positive_families": summary["positive_families"] >= 6,
        "worst_family_increment_nonnegative": summary["worst_family_increment"] >= 0.0,
    }
    safety_gates = {
        "no_new_crop_failures_vs_one_use": summary["new_crop_failures"] == 0,
        "combined_worker_three_within_5pp": (
            summary["combined_worker_three_rate"]
            >= summary["one_use_worker_three_rate"] - 0.05
        ),
    }
    return {
        "summary": summary,
        "signal_gates": signal_gates,
        "signal_pass": all(signal_gates.values()),
        "safety_gates": safety_gates,
        "safety_pass": all(safety_gates.values()),
    }


def analyze() -> dict:
    lock = verify_lock()
    download_record = json.loads(DOWNLOAD_RECORD.read_text())
    if download_record["operation"]["state"] != "completed":
        raise RuntimeError("D144 download is not from a completed operation")
    for summary in download_record["outputs"].values():
        path = Path(summary["path"])
        if sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D144 downloaded artifact changed: {path}")
    artifacts = download_record["outputs"]
    mc_a, mc_fields = _read_table(Path(artifacts["mc-a"]["path"]))
    arms, arm_fields = _read_table(Path(artifacts["arms"]["path"]))
    baselines, _ = _read_table(Path(artifacts["baselines"]["path"]))
    metadata = download_record["mapper_metadata"]
    metadata_by_shard = {item["shard_id"]: item for item in metadata}

    mc_rates = {
        label: (int(metadata_by_shard[label]["line_counts"]["mc"]) - 1)
        / float(metadata_by_shard[label]["elapsed_seconds"])
        for label in ("mc-a", "mc-b")
    }
    exact_rates = {
        label: (int(item["line_counts"]["arms"]) - 1)
        / float(item["elapsed_seconds"])
        for label, item in metadata_by_shard.items()
        if item["kind"] == "exact"
    }
    infrastructure_gates = {
        "operation_completed": download_record["operation"]["state"] == "completed",
        "exactly_four_mapper_metadata_rows": len(metadata) == 4,
        "exact_prescribed_shards": set(metadata_by_shard)
        == {str(spec["shard_id"]) for spec in build_specs()},
        "all_jobs_used_16_threads": all(int(item["threads"]) == THREADS for item in metadata),
        "mc_jobs_at_most_2700_active_seconds": all(
            float(metadata_by_shard[label]["elapsed_seconds"]) <= MC_MAX_ACTIVE_SECONDS
            for label in ("mc-a", "mc-b")
        ),
        "mc_jobs_at_least_5_episodes_per_second": min(mc_rates.values())
        >= MC_MIN_EPISODES_PER_SECOND,
        "exact_jobs_at_most_900_active_seconds": all(
            float(item["elapsed_seconds"]) <= EXACT_MAX_ACTIVE_SECONDS
            for item in metadata
            if item["kind"] == "exact"
        ),
        "exact_jobs_at_least_12_arms_per_second": min(exact_rates.values())
        >= EXACT_MIN_ARMS_PER_SECOND,
    }

    d113.START_SEED = START_SEED
    d113.MAPS = MAPS
    exact_elapsed = sum(
        float(item["elapsed_seconds"])
        for item in metadata
        if item["kind"] == "exact"
    )
    exact_mechanics, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms,
        baselines,
        arm_fields,
        exact_elapsed,
        {"pass": True},
    )
    exact_teacher = (
        d113.teacher_analysis(arms, baseline_by_task, arms_by_root)[0]
        if exact_mechanics["pass"]
        else {"signal_pass": False, "safety_pass": False}
    )
    mc_mechanics = _mc_mechanics(mc_a, mc_fields, baseline_by_task, arms)
    repeated = sha256(Path(artifacts["mc-a"]["path"])) == sha256(
        Path(artifacts["mc-b"]["path"])
    )
    mechanics_gates = {
        "mc_a_b_byte_exact": repeated,
        "exact_one_use_mechanics_pass": exact_mechanics["pass"],
        "mc_mechanics_pass": mc_mechanics["pass"],
        "exactly_128_baselines": len(baselines) == TASKS,
    }
    oracle = (
        _incremental_oracle(mc_a, arms, baseline_by_task)
        if all(mechanics_gates.values())
        else {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D144 infrastructure/mechanics failure",
        }
    )
    infrastructure_pass = all(infrastructure_gates.values())
    mechanics_pass = all(mechanics_gates.values())
    full_pass = (
        infrastructure_pass
        and mechanics_pass
        and oracle["signal_pass"]
        and oracle["safety_pass"]
    )
    result = {
        "schema": "troll-farm-d144a-two-intervention-mc-pilot-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": download_record["operation"],
        "panel": {
            "start_seed": START_SEED,
            "maps": MAPS,
            "tasks": TASKS,
            "replicas": REPLICAS,
            "single_replicas": SINGLE_REPLICAS,
            "double_replicas": DOUBLE_REPLICAS,
            "mc_episodes_per_repeat": EXPECTED_EPISODES,
        },
        "infrastructure": {
            "gates": infrastructure_gates,
            "pass": infrastructure_pass,
            "mc_episodes_per_second": mc_rates,
            "exact_arms_per_second": exact_rates,
            "metadata": metadata,
        },
        "mechanics": {
            "gates": mechanics_gates,
            "pass": mechanics_pass,
            "mc": mc_mechanics,
            "exact_one_use": exact_mechanics,
        },
        "exact_one_use_teacher": exact_teacher,
        "incremental_oracle": oracle,
        "artifacts": artifacts,
        "full_pass": full_pass,
        "decision": (
            "open_two_intervention_trajectory_teacher_and_policy_fit"
            if full_pass
            else "repair_d144_infrastructure_or_mechanics_only"
            if not (infrastructure_pass and mechanics_pass)
            else "close_this_two_intervention_mc_population"
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
