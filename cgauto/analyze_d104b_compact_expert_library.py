#!/usr/bin/env python3
"""Build and evaluate D104b's outcome-blind compact D98 proposal library."""

from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.analyze_d104a_d98_expert_proposal_coverage import (
    D97_ARMS,
    D97_BASELINES,
    D97_MANIFEST,
    D98_POPULATION,
    EXPECTED_EXPERTS,
    EXPECTED_PROPOSALS,
    EXPECTED_ROOTS,
    OPPONENTS,
    PROPOSALS_A,
    PROPOSALS_B,
    analyze as analyze_d104a,
    proposal_oracle,
    proposal_support,
    read_experts,
    read_table,
    root_manifest_rows,
    sha256,
)
from cgauto.analyze_d97a_joint_concrete_jobs import (
    manifest_support,
    validate_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d104b-outcome-blind-compact-expert-library-protocol-2026-07-22.md"
D104A_RESULT = BASE / "d104a-d98-expert-proposal-coverage-result.json"
LOCK = BASE / "d104b-compact-expert-library-lock.json"
OUTPUT = BASE / "d104b-compact-expert-library-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "7c81d8731e937ad8888d552c93eaa986b05799382db47cc9b97fae6fce805126",
    PROPOSALS_A: "54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9",
    PROPOSALS_B: "54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9",
    D104A_RESULT: "c27e5ac38aabbb91ce02f175dd130d7edc01b6d9294f2817186ca26dd951f8bc",
    D98_POPULATION: "3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e",
    D97_MANIFEST: "ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e",
    D97_ARMS: "c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33",
    D97_BASELINES: "8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6",
}
MAX_EXPERTS = 12
MAX_PAYLOAD_BYTES = 30_000


def population_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    result = {row["policy"]: row for row in rows if row["kind"] == "four"}
    if sorted(result) != [f"four_{index:02}" for index in range(EXPECTED_EXPERTS)]:
        raise RuntimeError("D104b expert population mismatch")
    return result


def coefficient_payload_bytes(
    selected: list[str], population: dict[str, dict[str, str]]
) -> int:
    payload = "".join(
        "\t".join(population[label][f"param_{index:03}"] for index in range(153)) + "\n"
        for label in selected
    )
    return len(payload.encode())


def proposal_rows_by_root(rows: list[dict[str, str]]) -> dict[int, list[dict[str, str]]]:
    result = defaultdict(list)
    for row in rows:
        result[int(row["root_id"])].append(row)
    return dict(result)


def support_pass(support: dict, payload_bytes: int) -> bool:
    return (
        support["mean_unique_supported_noncontrol_proposals_per_root"] >= 6
        and support["minimum_unique_supported_noncontrol_proposals"] >= 3
        and support["root_rate_with_supported_joint"] >= 0.90
        and set(support["proposal_job_kinds"]) == {"fell", "harvest", "mine", "renew"}
        and {"natural", "own", "opponent"}.issubset(
            support["proposal_provenance_classes"]
        )
        and support["proposal_seats"] == [0, 1]
        and set(support["proposal_opponent_families"]) == set(OPPONENTS)
        and support["proposal_reversed_role_order_present"]
        and payload_bytes <= MAX_PAYLOAD_BYTES
    )


def select_compact_library(
    rows: list[dict[str, str]],
    manifest_by_arm: dict[str, dict[str, str]],
    population: dict[str, dict[str, str]],
    expert_hashes: dict[str, dict],
) -> dict:
    by_expert = defaultdict(list)
    root_ids = sorted({int(row["root_id"]) for row in rows})
    if len(root_ids) != EXPECTED_ROOTS or len(rows) != EXPECTED_PROPOSALS:
        raise RuntimeError("D104b proposal grid mismatch before selection")
    for row in rows:
        if int(row["paired_boundary"]) != 1 or row["arm_id"] not in manifest_by_arm:
            raise RuntimeError("D104b unsupported proposal before selection")
        if int(row["expert_hash"]) != expert_hashes[row["expert"]]["hash"]:
            raise RuntimeError("D104b expert hash mismatch before selection")
        by_expert[row["expert"]].append(row)
    if any(len(expert_rows) != EXPECTED_ROOTS for expert_rows in by_expert.values()):
        raise RuntimeError("D104b expert/root grid mismatch")

    current = {root_id: set() for root_id in root_ids}
    joint_roots = set()
    selected = []
    trajectory = []
    compact_rows = []
    chosen_support = None
    for _ in range(MAX_EXPERTS):
        candidates = []
        for index in range(EXPECTED_EXPERTS):
            label = f"four_{index:02}"
            if label in selected:
                continue
            breadth = 0
            new_joint = set()
            new_tokens = 0
            for row in by_expert[label]:
                if row["arm_kind"] == "control":
                    continue
                root_id = int(row["root_id"])
                arm_id = row["arm_id"]
                if arm_id in current[root_id]:
                    continue
                new_tokens += 1
                breadth += len(current[root_id]) < 3
                if row["arm_kind"] == "joint" and root_id not in joint_roots:
                    new_joint.add(root_id)
            candidates.append(((breadth, len(new_joint), new_tokens, -index), label))
        score, chosen = max(candidates)
        selected.append(chosen)
        compact_rows.extend(by_expert[chosen])
        for row in by_expert[chosen]:
            if row["arm_kind"] == "control":
                continue
            root_id = int(row["root_id"])
            current[root_id].add(row["arm_id"])
            if row["arm_kind"] == "joint":
                joint_roots.add(root_id)
        compact_by_root = proposal_rows_by_root(compact_rows)
        support = proposal_support(compact_by_root, manifest_by_arm)
        payload_bytes = coefficient_payload_bytes(selected, population)
        passed = support_pass(support, payload_bytes)
        trajectory.append(
            {
                "step": len(selected),
                "selected_expert": chosen,
                "greedy_score": {
                    "roots_below_three_gaining_token": score[0],
                    "roots_newly_gaining_joint": score[1],
                    "new_noncontrol_tokens": score[2],
                },
                "mean_unique_noncontrol": support[
                    "mean_unique_supported_noncontrol_proposals_per_root"
                ],
                "minimum_unique_noncontrol": support[
                    "minimum_unique_supported_noncontrol_proposals"
                ],
                "joint_root_rate": support["root_rate_with_supported_joint"],
                "coefficient_payload_bytes": payload_bytes,
                "selection_gates_pass": passed,
            }
        )
        if passed:
            chosen_support = support
            break

    payload_bytes = coefficient_payload_bytes(selected, population)
    return {
        "selected_experts": selected,
        "selected_expert_hashes": {
            label: expert_hashes[label]["hash"] for label in selected
        },
        "selected_count": len(selected),
        "coefficient_payload_bytes": payload_bytes,
        "selection_pass": chosen_support is not None,
        "support": chosen_support
        if chosen_support is not None
        else proposal_support(proposal_rows_by_root(compact_rows), manifest_by_arm),
        "trajectory": trajectory,
        "compact_rows": compact_rows,
    }


def lock_payload(selection: dict) -> dict:
    return {
        "schema": "troll-farm-d104b-outcome-blind-compact-expert-library-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "proposal_sha256": sha256(PROPOSALS_A),
        "population_sha256": sha256(D98_POPULATION),
        "manifest_sha256": sha256(D97_MANIFEST),
        "selected_experts": selection["selected_experts"],
        "selected_expert_hashes": selection["selected_expert_hashes"],
        "selected_count": selection["selected_count"],
        "coefficient_payload_bytes": selection["coefficient_payload_bytes"],
        "selection_pass": selection["selection_pass"],
        "support": selection["support"],
        "trajectory": selection["trajectory"],
        "outcomes_read_during_selection": False,
    }


def write_or_verify_lock(payload: dict) -> str:
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if LOCK.exists():
        if LOCK.read_text() != encoded:
            raise RuntimeError("D104b existing outcome-blind lock differs")
    else:
        LOCK.write_text(encoded)
    return sha256(LOCK)


def analyze_value(
    compact_rows: list[dict[str, str]],
    full_report: dict,
    manifest: list[dict[str, str]],
) -> tuple[dict, dict, dict]:
    _, manifest_by_arm = manifest_support(manifest)
    roots = root_manifest_rows(manifest)
    arms, arm_fields = read_table(D97_ARMS)
    baselines, baseline_fields = read_table(D97_BASELINES)
    d97_audit, arm_by_id, baseline_by_task = validate_outputs(
        manifest_by_arm, arms, arm_fields, baselines, baseline_fields
    )
    compact_by_root = proposal_rows_by_root(compact_rows)
    oracle, details = proposal_oracle(
        compact_by_root, roots, manifest_by_arm, arm_by_id, baseline_by_task
    )
    oracle["retained_fraction_of_d104a_union_gain"] = (
        oracle["mean_margin_delta_vs_d40_all_tasks"]
        / full_report["proposal_oracle"]["mean_margin_delta_vs_d40_all_tasks"]
    )
    oracle["capture_of_d97_joint_oracle"] = (
        oracle["mean_margin_delta_vs_d40_all_tasks"]
        / full_report["d97_oracle"]["paired_mean_margin_delta_vs_d40_all_tasks"]
    )
    return oracle, details, d97_audit


def main() -> int:
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES}
    hashes_match = all(
        hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED_HASHES.items()
    )
    if not hashes_match:
        raise RuntimeError("D104b immutable hash mismatch")
    if PROPOSALS_A.read_bytes() != PROPOSALS_B.read_bytes():
        raise RuntimeError("D104b D104a proposal repeats differ")

    # Outcome-blind phase: do not read D97 arms/baselines or parse D104a's result here.
    proposals, _ = read_table(PROPOSALS_A)
    manifest, _ = read_table(D97_MANIFEST)
    _, manifest_by_arm = manifest_support(manifest)
    population = population_rows(D98_POPULATION)
    expert_hashes = read_experts(D98_POPULATION)
    selection = select_compact_library(
        proposals, manifest_by_arm, population, expert_hashes
    )
    repeated_selection = select_compact_library(
        proposals, manifest_by_arm, population, expert_hashes
    )
    first_lock = lock_payload(selection)
    if first_lock != lock_payload(repeated_selection):
        raise RuntimeError("D104b compact selection is not deterministic")
    lock_sha256 = write_or_verify_lock(first_lock)

    if not selection["selection_pass"]:
        report = {
            "protocol": "D104b outcome-blind compact expert library",
            "integrity_pass": True,
            "selection_pass": False,
            "value_opened": False,
            "pass": False,
            "decision": "close_exact_embedded_d98_experts_as_deployable_library",
            "source_hashes": hashes,
            "lock_sha256": lock_sha256,
            "selection": {key: value for key, value in selection.items() if key != "compact_rows"},
        }
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0

    # Value phase begins only after the exact subset lock exists.
    full_rows, _ = read_table(PROPOSALS_A)
    full_report = analyze_d104a(full_rows, full_rows, repeat_identical=True)
    oracle, details, d97_audit = analyze_value(
        selection["compact_rows"], full_report, manifest
    )
    value_gates = {
        "mean_margin_gain_at_least_25": oracle["mean_margin_delta_vs_d40_all_tasks"] >= 25,
        "retain_at_least_80pct_d104a_union_gain": oracle[
            "retained_fraction_of_d104a_union_gain"
        ]
        >= 0.80,
        "capture_at_least_65pct_d97_joint_oracle": oracle[
            "capture_of_d97_joint_oracle"
        ]
        >= 0.65,
        "strictly_improve_at_least_75pct_roots": oracle[
            "strict_root_improvement_rate"
        ]
        >= 0.75,
        "every_family_gain_at_least_10": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 10,
        "own_nonnegative_opponent_nonpositive": oracle[
            "mean_own_score_delta_vs_d40_all_tasks"
        ]
        >= 0
        and oracle["mean_opponent_score_delta_vs_d40_all_tasks"] <= 0,
        "crop_exact_and_worker_three_preserved": oracle["proposal_oracle_crop_rate"] == 1.0
        and oracle["proposal_oracle_worker_three_rate"]
        >= oracle["baseline_worker_three_rate"] - 0.05,
        "gain_at_least_2_beyond_full_best_single": oracle[
            "mean_incremental_margin_vs_full_best_single_rooted"
        ]
        >= 2,
        "joint_selected_in_at_least_35pct_roots": oracle["joint_selected_root_rate"]
        >= 0.35,
        "joint_beats_single_in_at_least_15pct_roots": oracle[
            "joint_strictly_beats_full_best_single_rate"
        ]
        >= 0.15,
        "selected_proposal_breadth": len(oracle["selected_job_kinds"]) >= 3
        and len(oracle["selected_provenance_classes"]) >= 2
        and oracle["selected_seats"] == [0, 1]
        and set(oracle["selected_opponent_families"]) == set(OPPONENTS)
        and oracle["selected_reversed_role_order_present"],
    }
    integrity_gates = {
        "immutable_hashes_match": hashes_match,
        "exact_proposal_grid": len(proposals) == EXPECTED_PROPOSALS,
        "selection_repeat_identical": first_lock == lock_payload(repeated_selection),
        "lock_written_before_value": LOCK.exists() and lock_sha256 == sha256(LOCK),
        "d104a_integrity_reproduced": full_report["integrity_pass"],
        "compact_rows_are_validated_d104a_subset": len(selection["compact_rows"])
        == selection["selected_count"] * EXPECTED_ROOTS,
        "d97_terminal_integrity_reproduced": not d97_audit["integrity_failure_counts"]
        and d97_audit["mirror_failures"] == 0
        and d97_audit["control_parity_failures"] == 0,
    }
    integrity_pass = all(integrity_gates.values())
    value_pass = integrity_pass and all(value_gates.values())
    passed = integrity_pass and selection["selection_pass"] and value_pass
    decision = (
        "open_d104c_recurrent_opponent_aware_proposal_controller_preflight"
        if passed
        else "close_coverage_only_compact_expert_library"
    )
    report = {
        "protocol": "D104b outcome-blind compact expert library",
        "integrity_pass": integrity_pass,
        "selection_pass": selection["selection_pass"],
        "value_opened": True,
        "value_pass": value_pass,
        "pass": passed,
        "decision": decision,
        "integrity_gates": integrity_gates,
        "value_gates": value_gates,
        "source_hashes": hashes,
        "lock_sha256": lock_sha256,
        "selection": {key: value for key, value in selection.items() if key != "compact_rows"},
        "compact_oracle": oracle,
        "oracle_details": details,
        "provenance": {
            "protocol_sha256": sha256(PROTOCOL),
            "lock_sha256": lock_sha256,
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "scope": (
            "outcome-blind proposal-library compression and consumed D97 value audit only; no "
            "learner, new terminal simulation, candidate, platform action, or resident mutation"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "pass": passed,
                "decision": decision,
                "selected_experts": selection["selected_experts"],
                "selected_count": selection["selected_count"],
                "coefficient_payload_bytes": selection["coefficient_payload_bytes"],
                "selection_support": selection["support"],
                "compact_oracle": oracle,
                "failed_value_gates": [
                    name for name, value in value_gates.items() if not value
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
