#!/usr/bin/env python3
"""Lock the outcome-blind D105b q4 proposal union inside a fresh D97 manifest."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def arm_key_digest(arm_ids: list[str]) -> str:
    payload = "".join(f"{arm_id}\n" for arm_id in sorted(arm_ids)).encode()
    return hashlib.sha256(payload).hexdigest()


def build_union(
    manifest_path: Path,
    proposals_path: Path,
    population_path: Path,
    protocol_path: Path,
) -> tuple[list[dict[str, str]], list[str], dict]:
    manifest, fields = read_table(manifest_path)
    proposals, proposal_fields = read_table(proposals_path)
    if not manifest or not proposals:
        raise RuntimeError("D105b manifest/proposal input is empty")
    required_proposal_fields = {
        "root_id",
        "map_seed",
        "seat",
        "opponent",
        "expert_index",
        "expert",
        "arm_kind",
        "arm_id",
        "paired_boundary",
    }
    if not required_proposal_fields.issubset(proposal_fields):
        raise RuntimeError("D105b proposal schema mismatch")

    manifest_by_arm = {row["arm_id"]: row for row in manifest}
    if len(manifest_by_arm) != len(manifest):
        raise RuntimeError("D105b full manifest has duplicate arm IDs")
    manifest_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        manifest_by_root[row["root_id"]].append(row)
    roots = sorted(manifest_by_root, key=int)
    expected_keys = {
        (root_id, expert_index) for root_id in roots for expert_index in range(64)
    }
    actual_keys = {
        (row["root_id"], int(row["expert_index"])) for row in proposals
    }
    if len(proposals) != len(expected_keys) or actual_keys != expected_keys:
        raise RuntimeError("D105b proposal expert/root grid mismatch")

    selected_ids = set()
    proposal_ids_by_root: dict[str, set[str]] = defaultdict(set)
    expert_noncontrol_roots = Counter()
    for row in proposals:
        root_id = row["root_id"]
        if row["expert"] != f"four_{int(row['expert_index']):02}":
            raise RuntimeError("D105b expert label mismatch")
        if int(row["paired_boundary"]) != 1 or row["arm_id"] not in manifest_by_arm:
            raise RuntimeError("D105b unsupported proposal")
        arm = manifest_by_arm[row["arm_id"]]
        for field in ("root_id", "map_seed", "seat", "opponent", "arm_kind", "arm_id"):
            if row[field] != arm[field]:
                raise RuntimeError(f"D105b proposal/manifest mismatch: {field}")
        selected_ids.add(row["arm_id"])
        if row["arm_kind"] != "control":
            proposal_ids_by_root[root_id].add(row["arm_id"])
            expert_noncontrol_roots[row["expert"]] += 1

    controls = {}
    for root_id, rows in manifest_by_root.items():
        root_controls = [row for row in rows if row["arm_kind"] == "control"]
        if len(root_controls) != 1:
            raise RuntimeError("D105b root does not have exactly one control")
        controls[root_id] = root_controls[0]["arm_id"]
        selected_ids.add(root_controls[0]["arm_id"])

    filtered = [row for row in manifest if row["arm_id"] in selected_ids]
    if {row["arm_id"] for row in filtered} != selected_ids:
        raise RuntimeError("D105b filtered manifest identity mismatch")
    selected_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in filtered:
        selected_by_root[row["root_id"]].append(row)
    unique_counts = [len(proposal_ids_by_root[root_id]) for root_id in roots]
    kinds = Counter(row["arm_kind"] for row in filtered)
    jobs = {
        row[f"{position}_job_kind"]
        for row in filtered
        for position in ("first", "second")
        if row[f"{position}_class"] != "keep"
    }
    owners = {
        row[f"{position}_owner"]
        for row in filtered
        for position in ("first", "second")
        if row[f"{position}_owner"] != "none"
    }
    seats = sorted({int(row["seat"]) for row in filtered})
    opponents = sorted({row["opponent"] for row in filtered})
    pairs = {
        (row["first_class"], row["second_class"])
        for row in filtered
        if row["arm_kind"] != "control"
    }
    reversed_order = any(
        left != right and (right, left) in pairs for left, right in pairs
    )
    support = {
        "roots": len(roots),
        "full_manifest_arms": len(manifest),
        "selected_arms": len(filtered),
        "arm_kind_counts": dict(sorted(kinds.items())),
        "mean_unique_noncontrol_proposals_per_root": sum(unique_counts) / len(unique_counts),
        "minimum_unique_noncontrol_proposals_per_root": min(unique_counts),
        "maximum_unique_noncontrol_proposals_per_root": max(unique_counts),
        "roots_with_joint": sum(
            any(row["arm_kind"] == "joint" for row in selected_by_root[root_id])
            for root_id in roots
        ),
        "experts_noncontrol_in_at_least_25pct_roots": sum(
            expert_noncontrol_roots[f"four_{index:02}"] >= 0.25 * len(roots)
            for index in range(64)
        ),
        "job_kinds": sorted(jobs),
        "provenance_classes": sorted(owners),
        "seats": seats,
        "opponents": opponents,
        "reversed_role_order_present": reversed_order,
    }
    lock = {
        "schema": "troll-farm-d105b-outcome-blind-proposal-union-lock-v1",
        "protocol_sha256": sha256(protocol_path),
        "full_manifest_sha256": sha256(manifest_path),
        "proposal_sha256": sha256(proposals_path),
        "population_sha256": sha256(population_path),
        "selected_arm_ids_sha256": arm_key_digest(list(selected_ids)),
        "selected_control_arm_ids_sha256": arm_key_digest(list(controls.values())),
        "support": support,
        "outcomes_read": False,
    }
    return filtered, fields, lock


def write_or_verify_table(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    encoded = buffer.getvalue()
    if path.exists():
        if path.read_text() != encoded:
            raise RuntimeError("D105b existing union manifest differs")
    else:
        path.write_text(encoded)


def write_or_verify_lock(path: Path, lock: dict, union_path: Path) -> None:
    payload = dict(lock)
    payload["union_manifest_sha256"] = sha256(union_path)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != encoded:
            raise RuntimeError("D105b existing outcome-blind lock differs")
    else:
        path.write_text(encoded)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--proposals", type=Path, required=True)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    args = parser.parse_args()
    rows, fields, lock = build_union(
        args.manifest, args.proposals, args.population, args.protocol
    )
    write_or_verify_table(args.output, rows, fields)
    write_or_verify_lock(args.lock, lock, args.output)
    print(json.dumps({**lock["support"], "lock": sha256(args.lock)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
