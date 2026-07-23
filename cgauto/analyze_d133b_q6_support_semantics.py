#!/usr/bin/env python3
"""Repair only D133's q6 task-support semantics and interpret all four blocks."""

from __future__ import annotations

import csv
import gc
import json
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto import yt_d133_q6_teacher_corpus as d133


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d133b-q6-support-semantics-repair-protocol-2026-07-22.md"
LOCK = BASE / "d133b-q6-support-semantics-repair-lock.json"
D133_RESULT = BASE / "d133a-yt-q6-independent-block-corpus-result.json"
OUTPUT = BASE / "d133b-q6-support-semantics-repair-result.json"
D134_TARGET_ACTIVITY = 0.84

PRIOR_BASELINES = (
    BASE / "d114a-q6-train-baselines-9843300-9843315.tsv",
    BASE / "d116a-q6-validation-repair1-baselines-9843650-9843665.tsv",
    BASE / "d119a-q6-validation-baselines-9843670-9843685.tsv",
    BASE / "d119a-q6-held-baselines-9843700-9843715.tsv",
    BASE / "d119a-q6-held-repair1-baselines-9843716-9843731.tsv",
    BASE / "d119a-q6-held-repair2-baselines-9843732-9843747.tsv",
    BASE / "d119a-q6-held-repair3-baselines-9843748-9843763.tsv",
    BASE / "d119a-q6-held-repair4-baselines-9843764-9843779.tsv",
    BASE / "d126a-q6-validation-baselines-9843780-9843795.tsv",
)


def verify_lock() -> dict:
    return _verify_manifest(LOCK)


def _verify_manifest(path: Path) -> dict:
    payload = json.loads(path.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        target = ROOT / relative
        actual = d133.sha256(target) if target.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D133b lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d133.sha256(path),
        "mismatches": mismatches,
        "pass": True,
    }


def support_summary(path: Path) -> dict:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    supported = sum(int(row["boundary_count"]) > 0 for row in rows)
    seeds = sorted({int(row["map_seed"]) for row in rows})
    try:
        display_path = str(path.relative_to(ROOT))
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "sha256": d133.sha256(path),
        "start_seed": seeds[0],
        "end_seed": seeds[-1],
        "maps": len(seeds),
        "tasks": len(rows),
        "supported_tasks": supported,
        "support_rate": supported / len(rows),
    }


def exact_mechanics_without_support_gate(mechanics: dict) -> dict:
    gates = {
        name: passed
        for name, passed in mechanics["gates"].items()
        if name != "supported_tasks_at_least_90pct"
    }
    return {
        "gates": gates,
        "descriptive_support_gate": mechanics["gates"][
            "supported_tasks_at_least_90pct"
        ],
        "details": mechanics["details"],
        "pass": all(gates.values()),
    }


def calibration_minimum(tasks: int) -> int:
    return round(D134_TARGET_ACTIVITY * tasks) + 1


def repaired_block(descriptor: dict) -> dict:
    block = int(descriptor["block_id"])
    start = int(descriptor["start_seed"])
    arms_path = Path(descriptor["artifacts"]["arms"]["path"])
    baselines_path = Path(descriptor["artifacts"]["baselines"]["path"])
    arms, fields = d133._read_table(arms_path)
    baselines, _ = d133._read_table(baselines_path)
    d113.START_SEED = start
    d113.MAPS = int(descriptor["maps"])
    inherited, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms,
        baselines,
        fields,
        float(descriptor["active_seconds_sum"]),
        {"pass": True},
    )
    mechanics = exact_mechanics_without_support_gate(inherited)
    if mechanics["pass"]:
        teacher, labels = d113.teacher_analysis(
            arms, baseline_by_task, arms_by_root
        )
        labels = [{"block_id": block, **row} for row in labels]
        labels_path = d133.LOCAL_OUTPUT / f"block-{block:02d}-labels.tsv"
        d112.write_labels(labels_path, labels)
        label_summary = {
            "path": str(labels_path),
            "rows": len(labels),
            "bytes": labels_path.stat().st_size,
            "sha256": d133.sha256(labels_path),
        }
    else:
        teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "exact mechanics failure remains after support repair",
        }
        label_summary = {"path": None, "rows": 0, "bytes": 0, "sha256": None}
    result = {
        "block_id": block,
        "start_seed": start,
        "maps": int(descriptor["maps"]),
        "mechanics": mechanics,
        "teacher": teacher,
        "labels": label_summary,
        "artifacts": descriptor["artifacts"],
    }
    del arms, baselines, baseline_by_task, arms_by_root
    gc.collect()
    return result


def main() -> int:
    lock = verify_lock()
    original = json.loads(D133_RESULT.read_text())
    if original["decision"] != "repair_d133_infrastructure_or_mechanics_only":
        raise RuntimeError("D133a is not at its frozen repair boundary")
    prior = [support_summary(path) for path in PRIOR_BASELINES]
    prior_supported = sum(item["supported_tasks"] for item in prior)
    prior_tasks = sum(item["tasks"] for item in prior)
    audit = {
        "panels": prior,
        "panel_count": len(prior),
        "tasks": prior_tasks,
        "supported_tasks": prior_supported,
        "pooled_support_rate": prior_supported / prior_tasks,
        "minimum_panel_support_rate": min(item["support_rate"] for item in prior),
        "maximum_panel_support_rate": max(item["support_rate"] for item in prior),
        "panels_below_90pct": sum(item["support_rate"] < 0.90 for item in prior),
    }

    blocks = [repaired_block(item) for item in original["blocks"]]
    exact_pass = all(block["mechanics"]["pass"] for block in blocks)
    supported = [
        block["mechanics"]["details"]["supported_tasks"] for block in blocks
    ]
    three_block_support = {
        str(held): sum(value for index, value in enumerate(supported) if index != held)
        for held in range(len(blocks))
    }
    three_block_minimum = calibration_minimum(3 * 256)
    full_minimum = calibration_minimum(4 * 256)
    gates = {
        "d133_infrastructure_passed": original["infrastructure"]["pass"],
        "all_four_blocks_pass_exact_nonavailability_mechanics": exact_pass,
        "exactly_1024_baselines": sum(
            block["mechanics"]["details"]["baselines"] for block in blocks
        )
        == 1024,
        "at_least_80000_arms": sum(
            block["mechanics"]["details"]["arms"] for block in blocks
        )
        >= 80_000,
        "at_least_4800_roots": sum(
            block["mechanics"]["details"]["roots"] for block in blocks
        )
        >= 4_800,
        "every_three_block_fit_supports_84pct_calibration": min(
            three_block_support.values()
        )
        >= three_block_minimum,
        "all_block_fit_supports_84pct_calibration": sum(supported) >= full_minimum,
    }
    if all(gates.values()):
        teacher = d133.combine_teachers([block["teacher"] for block in blocks])
    else:
        teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D133b repaired mechanics/calibration failure",
        }
    full_pass = all(gates.values()) and teacher["signal_pass"] and teacher["safety_pass"]
    result = {
        "schema": "troll-farm-d133b-q6-support-semantics-repair-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "original_d133": {
            "path": str(D133_RESULT.relative_to(ROOT)),
            "sha256": d133.sha256(D133_RESULT),
            "decision": original["decision"],
        },
        "historical_support_audit": audit,
        "repair": {
            "removed_gate": "supported_tasks_at_least_90pct",
            "target_activity": D134_TARGET_ACTIVITY,
            "supported_tasks_by_block": supported,
            "three_block_supported_tasks": three_block_support,
            "three_block_required_supported_tasks": three_block_minimum,
            "all_block_supported_tasks": sum(supported),
            "all_block_required_supported_tasks": full_minimum,
            "gates": gates,
            "pass": all(gates.values()),
        },
        "blocks": blocks,
        "teacher": teacher,
        "full_pass": full_pass,
        "decision": (
            "open_frozen_d134_leave_one_block_out_selection"
            if full_pass
            else "close_d133_corpus_after_support_semantics_repair"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
