#!/usr/bin/env python3
"""Repair D148's inherited root-density semantics, then expose frozen transfer."""

from __future__ import annotations

from collections import defaultdict
import csv
import gc
import io
import json
import math
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto import analyze_d148a_priority_joint_teacher as d148
from cgauto import yt_d133_q6_teacher_corpus as d133
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = (
    BASE / "d148b-priority-joint-support-semantics-protocol-2026-07-22.md"
)
LOCK = BASE / "d148b-priority-joint-support-semantics-lock.json"
D148_RESULT = BASE / "d148a-priority-joint-teacher-corpus-result.json"
OUTPUT = BASE / "d148b-priority-joint-support-semantics-result.json"

ROOTS_PER_MAP = 600 / 16
FULL_ROOT_MINIMUM = 4_800
FULL_ARM_MINIMUM = 80_000


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = yt_d148.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D148b lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": yt_d148.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def exact_mechanics_with_scaled_root_gate(mechanics: dict, maps: int) -> dict:
    """Remove only support-rate and unscaled-root gates, retaining root density."""

    removed = {"supported_tasks_at_least_90pct", "at_least_600_roots"}
    gates = {
        name: passed
        for name, passed in mechanics["gates"].items()
        if name not in removed
    }
    roots = int(mechanics["details"]["roots"])
    minimum = math.ceil(ROOTS_PER_MAP * maps)
    gates["at_least_37_5_roots_per_map"] = roots >= minimum
    return {
        "gates": gates,
        "descriptive_support_gate": mechanics["gates"][
            "supported_tasks_at_least_90pct"
        ],
        "descriptive_unscaled_root_gate": mechanics["gates"][
            "at_least_600_roots"
        ],
        "root_density": {
            "maps": maps,
            "roots": roots,
            "roots_per_map": roots / maps,
            "required_roots_per_map": ROOTS_PER_MAP,
            "required_roots": minimum,
        },
        "details": mechanics["details"],
        "pass": all(gates.values()),
    }


def root_coverage_gates(blocks: list[dict]) -> tuple[dict, dict]:
    roots = [int(block["mechanics"]["details"]["roots"]) for block in blocks]
    arms = [int(block["mechanics"]["details"]["arms"]) for block in blocks]
    pair_roots = {
        str(index): roots[2 * index] + roots[2 * index + 1]
        for index in range(len(roots) // 2)
    }
    summary = {
        "roots_by_eight_map_shard": roots,
        "roots_by_sixteen_map_block": pair_roots,
        "total_roots": sum(roots),
        "total_arms": sum(arms),
    }
    gates = {
        "all_eight_shards_present": len(blocks) == yt_d148.SHARDS,
        "every_eight_map_shard_at_least_300_roots": all(value >= 300 for value in roots),
        "every_sixteen_map_block_at_least_600_roots": (
            len(pair_roots) == 4 and all(value >= 600 for value in pair_roots.values())
        ),
        "full_corpus_at_least_4800_roots": sum(roots) >= FULL_ROOT_MINIMUM,
        "full_corpus_at_least_80000_arms": sum(arms) >= FULL_ARM_MINIMUM,
    }
    return summary, gates


def analyze_exact_repaired(
    arms_path: Path,
    baselines_path: Path,
    metadata_by_shard: dict[str, dict],
) -> tuple[dict, dict, dict]:
    baselines, _ = d148.read_table(baselines_path)
    baseline_by_task = {d148.task(row): row for row in baselines}
    duplicate_baselines = len(baseline_by_task) != len(baselines)
    blocks = []
    best_one_by_task = {}
    seen_blocks = []

    for block, arms, fields in d148.iter_arm_blocks(arms_path):
        seen_blocks.append(block)
        start = yt_d148.START_SEED + block * yt_d148.MAPS_PER_SHARD
        block_baselines = [
            row
            for row in baselines
            if start <= int(row["map_seed"]) < start + yt_d148.MAPS_PER_SHARD
        ]
        d113.START_SEED = start
        d113.MAPS = yt_d148.MAPS_PER_SHARD
        elapsed = float(metadata_by_shard[f"exact-{block:02d}"]["elapsed_seconds"])
        inherited, block_controls, arms_by_root = d113.zero_aware_mechanics(
            arms, block_baselines, fields, elapsed, {"pass": True}
        )
        mechanics = exact_mechanics_with_scaled_root_gate(
            inherited, yt_d148.MAPS_PER_SHARD
        )
        if mechanics["pass"]:
            teacher, labels = d113.teacher_analysis(
                arms, block_controls, arms_by_root
            )
            label_rows = len(labels)
        else:
            teacher = {
                "signal_pass": False,
                "safety_pass": False,
                "not_interpreted": "non-root exact mechanics failure remains",
            }
            label_rows = 0

        arms_by_task = defaultdict(list)
        for row in arms:
            arms_by_task[d148.task(row)].append(row)
        for key, control in block_controls.items():
            candidates = arms_by_task.get(key, [])
            best = (
                max(candidates, key=lambda row: d112.tie_key(row, control))
                if candidates
                else control
            )
            if d148.margin(best) <= d148.margin(control):
                best = control
            best_one_by_task[key] = {
                **{
                    field: str(best[field])
                    for field in d148.TRANSFER_TERMINAL_FIELDS
                },
                "boundary_index": str(best.get("boundary_index", -1)),
                "slot": str(best.get("slot", 0)),
            }

        blocks.append(
            {
                "block": block,
                "start_seed": start,
                "maps": yt_d148.MAPS_PER_SHARD,
                "mechanics": mechanics,
                "teacher": teacher,
                "interpreted_label_rows": label_rows,
            }
        )
        del arms, arms_by_root, arms_by_task, block_controls
        if mechanics["pass"]:
            del labels
        gc.collect()

    coverage, coverage_gates = root_coverage_gates(blocks)
    mechanics_gates = {
        "exact_prescribed_block_order": seen_blocks == list(range(yt_d148.SHARDS)),
        "exactly_1024_unique_baselines": (
            len(baselines) == 1024
            and len(baseline_by_task) == 1024
            and not duplicate_baselines
        ),
        "best_one_for_all_1024_tasks": len(best_one_by_task) == 1024,
        "all_inherited_nonroot_and_scaled_root_gates_pass": all(
            block["mechanics"]["pass"] for block in blocks
        ),
        **coverage_gates,
    }
    mechanics_pass = all(mechanics_gates.values())
    teacher = (
        d133.combine_teachers([block["teacher"] for block in blocks])
        if mechanics_pass
        else {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D148b repaired exact mechanics failure",
        }
    )
    summary = {
        "blocks": blocks,
        "baselines": len(baselines),
        "best_one_tasks": len(best_one_by_task),
        "coverage": coverage,
        "mechanics_gates": mechanics_gates,
        "mechanics_pass": mechanics_pass,
        "teacher": teacher,
        "pass": mechanics_pass and teacher["signal_pass"] and teacher["safety_pass"],
    }
    return summary, baseline_by_task, best_one_by_task


def write_or_verify_targets(rows: list[dict]) -> dict:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=d148.TARGET_FIELDS,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    expected = buffer.getvalue().encode()
    path = d148.TARGETS
    if path.exists():
        if path.read_bytes() != expected:
            raise RuntimeError(f"existing D148 targets disagree with D148b: {path}")
        disposition = "verified_existing"
    else:
        with path.open("xb") as target:
            target.write(expected)
        disposition = "created"
    return {
        "path": str(path),
        "rows": len(rows),
        "active_rows": sum(int(row["target_active"]) for row in rows),
        "bytes": path.stat().st_size,
        "sha256": yt_d148.sha256(path),
        "disposition": disposition,
    }


def main() -> int:
    lock = verify_lock()
    original = json.loads(D148_RESULT.read_text())
    if original["decision"] != "repair_d148_infrastructure_or_mechanics_only":
        raise RuntimeError("D148a is not at its frozen mechanics-repair boundary")
    download = json.loads(yt_d148.DOWNLOAD_RECORD.read_text())
    outputs = download["outputs"]
    metadata_by_shard = {
        item["shard_id"]: item for item in download["mapper_metadata"]
    }

    exact, baseline_by_task, best_one = analyze_exact_repaired(
        Path(outputs["arms"]["path"]),
        Path(outputs["baselines"]["path"]),
        metadata_by_shard,
    )
    population_rows, population_fields = d148.read_table(
        Path(outputs["population"]["path"])
    )
    population, controls, best_pair = d148.validate_population(
        population_rows, population_fields, baseline_by_task
    )
    manifest_rows, manifest_fields = d148.read_table(Path(outputs["manifest"]["path"]))
    replay_rows, replay_fields = d148.read_table(Path(outputs["replays"]["path"]))
    selected, manifest_by_task = d148.validate_manifest_and_replays(
        manifest_rows, manifest_fields, replay_rows, replay_fields, best_pair
    )
    candidates = d148.analyze_candidates(
        Path(outputs["candidates"]["path"]), manifest_by_task
    )
    reproduction_gates = {
        "d148a_infrastructure_passed": original["infrastructure"]["pass"],
        "population_reproduced_exactly": population == original["population"],
        "selected_replays_reproduced_exactly": selected
        == original["selected_replays"],
        "candidate_validation_reproduced_exactly": candidates
        == original["candidates"],
    }
    mechanics_pass = (
        lock["pass"]
        and exact["pass"]
        and population["pass"]
        and selected["pass"]
        and candidates["pass"]
        and all(reproduction_gates.values())
    )
    if mechanics_pass:
        transfer, target_rows = d148.transfer_analysis(controls, best_one, best_pair)
        targets = write_or_verify_targets(target_rows)
    else:
        transfer = {"pass": False, "not_interpreted": "D148b mechanics failure"}
        targets = {
            "path": None,
            "rows": 0,
            "active_rows": 0,
            "bytes": 0,
            "sha256": None,
            "disposition": "not_written",
        }
    full_pass = mechanics_pass and transfer["pass"]
    result = {
        "schema": "troll-farm-d148b-priority-joint-support-semantics-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d148a": {
            "path": str(D148_RESULT.relative_to(ROOT)),
            "sha256": yt_d148.sha256(D148_RESULT),
            "decision": original["decision"],
        },
        "operation": download["operation"],
        "repair": {
            "removed_absolute_gate": "at_least_600_roots",
            "removed_descriptive_support_gate": "supported_tasks_at_least_90pct",
            "replacement_root_density": ROOTS_PER_MAP,
            "reproduction_gates": reproduction_gates,
        },
        "exact_one_use": exact,
        "population": population,
        "selected_replays": selected,
        "candidates": candidates,
        "mechanics_pass": mechanics_pass,
        "transfer": transfer,
        "targets": targets,
        "full_pass": full_pass,
        "decision": (
            "open_d149_grouped_joint_two_stage_policy_fit"
            if full_pass
            else "close_nontransferring_d148_population"
            if mechanics_pass
            else "close_d148_after_frozen_support_semantics_repair"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
