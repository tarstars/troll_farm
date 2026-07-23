#!/usr/bin/env python3
"""Build D151's compact exact conditional-second branch plan."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from cgauto import build_d149a_joint_two_stage_dataset as d149
from cgauto import run_d148a_priority_joint_teacher as d148_runner
from cgauto import run_d151a_conditional_second_counterfactual as runner
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PLAN = BASE / "d151a-conditional-second-branch-plan-9844136-9844199.tsv"


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def build_rows() -> list[dict]:
    download = json.loads(yt_d148.DOWNLOAD_RECORD.read_text())
    manifests, fields = d149.d148.read_table(
        Path(download["outputs"]["manifest"]["path"])
    )
    if fields != list(d148_runner.MANIFEST_FIELDS):
        raise RuntimeError("D151 manifest schema drift")
    manifest_by_task = {task_key(row): row for row in manifests}
    targets = d149.load_targets()
    groups = {}
    for key, rows in d149.iter_candidate_groups():
        if rows[0]["stage"] == "second":
            groups[key[:3]] = rows
    if len(groups) != 909 or set(groups) != set(manifest_by_task):
        raise RuntimeError("D151 second-state task set drift")

    result = []
    for task in sorted(groups):
        candidates = sorted(groups[task], key=lambda row: int(row["candidate_slot"]))
        manifest = manifest_by_task[task]
        state = [candidates[0][field] for field in d148_runner.STATE_FIELDS]
        actions = [
            (
                int(row["candidate_slot"]),
                [row[field] for field in d148_runner.ACTION_FIELDS],
            )
            for row in candidates
        ]
        slots = tuple(slot for slot, _ in actions)
        if slots != tuple(range(0, max(slots) + 1)):
            # Representative slots may be sparse; only sorted uniqueness is required.
            if slots != tuple(sorted(set(slots))) or slots[0] != 0:
                raise RuntimeError("D151 candidate legal-slot ordering drift")
        result.append(
            {
                "scenario": int(manifest["scenario"]),
                "map_seed": task[0],
                "seat": task[1],
                "opponent": task[2],
                "source_replica": int(manifest["source_replica"]),
                "first_boundary": int(manifest["first_boundary"]),
                "first_slot": int(manifest["first_slot"]),
                "second_boundary": int(manifest["second_boundary"]),
                "selected_second_slot": int(manifest["second_slot"]),
                "target_active": int(targets[task]["target_active"]),
                "legal_second_slots": ",".join(str(slot) for slot in slots),
                "second_feature_sha256": runner.conditional_feature_hash(
                    state, actions
                ),
            }
        )
    if len(result) != 909:
        raise RuntimeError("D151 branch plan row count drift")
    return result


def write_plan(path: Path = PLAN) -> dict:
    if path.exists():
        raise FileExistsError(path)
    rows = build_rows()
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=runner.PLAN_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    branches = sum(len(runner.parse_slots(row["legal_second_slots"])) for row in rows)
    active_branches = sum(
        len(runner.parse_slots(row["legal_second_slots"]))
        for row in rows
        if int(row["target_active"])
    )
    return {
        "path": str(path),
        "rows": len(rows),
        "branches": branches,
        "active_branches": active_branches,
        "maximum_branches": max(
            len(runner.parse_slots(row["legal_second_slots"])) for row in rows
        ),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> int:
    print(json.dumps(write_plan(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
