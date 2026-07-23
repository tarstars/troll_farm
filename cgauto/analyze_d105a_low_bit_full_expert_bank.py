#!/usr/bin/env python3
"""Select and value-audit D105a's outcome-blind low-bit full expert bank."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.analyze_d104a_d98_expert_proposal_coverage import (
    D97_ARMS,
    D97_BASELINES,
    D97_MANIFEST,
    D98_POPULATION,
    EXPECTED_PROPOSALS,
    EXPECTED_ROOTS,
    OPPONENTS,
    PROPOSALS_A as EXACT_PROPOSALS,
    analyze as analyze_d104a,
    proposal_key,
    proposal_support,
    read_experts,
    read_table,
    root_manifest_rows,
    sha256,
    validate_proposals,
)
from cgauto.analyze_d104b_compact_expert_library import analyze_value
from cgauto.analyze_d97a_joint_concrete_jobs import manifest_support
from cgauto.make_d105a_quantized_expert_population import build_population


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d105a-low-bit-full-expert-bank-protocol-2026-07-22.md"
QUANTIZER = ROOT / "cgauto" / "make_d105a_quantized_expert_population.py"
RUNNER = ROOT / "rust" / "src" / "bin" / "d104_d98_expert_proposal_coverage.rs"
D104A_RESULT = BASE / "d104a-d98-expert-proposal-coverage-result.json"
BITS = (4, 6, 8)
POPULATIONS = {
    bits: BASE / f"d105a-q{bits}-expert-population.tsv" for bits in BITS
}
PROPOSALS_A = {
    bits: BASE / f"d105a-q{bits}-proposals-a-jobs1.tsv" for bits in BITS
}
PROPOSALS_B = {
    bits: BASE / f"d105a-q{bits}-proposals-b-jobs20.tsv" for bits in BITS
}
LOCK = BASE / "d105a-low-bit-full-expert-bank-lock.json"
OUTPUT = BASE / "d105a-low-bit-full-expert-bank-result.json"

PRELOCK_EXPECTED_HASHES = {
    PROTOCOL: "bb2a6e75316b753938e9ad785651a00fb1613b5bb33bff5b2d763590de5b1102",
    QUANTIZER: "c9efaea2f22c6225ac2731b80e55952e2f6b85a4c533029a1fd6a62dc0a4599b",
    RUNNER: "c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393",
    D98_POPULATION: "3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e",
    EXACT_PROPOSALS: "54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9",
    D97_MANIFEST: "ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e",
}
POSTLOCK_EXPECTED_HASHES = {
    D104A_RESULT: "c27e5ac38aabbb91ce02f175dd130d7edc01b6d9294f2817186ca26dd951f8bc",
    D97_ARMS: "c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33",
    D97_BASELINES: "8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6",
}


def relative_hashes(paths: dict[Path, str]) -> tuple[dict[str, str], bool]:
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in paths}
    passed = all(
        hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in paths.items()
    )
    return hashes, passed


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def noncontrol_sets(rows: list[dict[str, str]]) -> dict[int, set[str]]:
    result: dict[int, set[str]] = {}
    for row in rows:
        root_id = int(row["root_id"])
        result.setdefault(root_id, set())
        if int(row["paired_boundary"]) == 1 and row["arm_kind"] != "control":
            result[root_id].add(row["arm_id"])
    return result


def regenerate_populations() -> tuple[dict[int, dict], bool]:
    audits = {}
    with tempfile.TemporaryDirectory(prefix="d105a-regenerate-") as directory:
        temporary = Path(directory)
        for bits in BITS:
            target = temporary / f"q{bits}.tsv"
            audit = build_population(D98_POPULATION, target, bits)
            audit["byte_identical"] = target.read_bytes() == POPULATIONS[bits].read_bytes()
            audit["population_sha256"] = sha256(POPULATIONS[bits])
            audits[bits] = audit
    return audits, all(audit["byte_identical"] for audit in audits.values())


def fidelity_candidate(
    bits: int,
    exact_rows: list[dict[str, str]],
    exact_sets: dict[int, set[str]],
    roots: dict[int, dict[str, str]],
    manifest_by_arm: dict[str, dict[str, str]],
    population_audit: dict,
) -> tuple[dict, list[dict[str, str]]]:
    rows, _ = read_table(PROPOSALS_A[bits])
    experts = read_experts(POPULATIONS[bits])
    proposal_audit, by_root = validate_proposals(
        rows, rows, roots, manifest_by_arm, experts, repeat_identical=True
    )
    exact_by_key = {proposal_key(row): row for row in exact_rows}
    candidate_by_key = {proposal_key(row): row for row in rows}
    shared_keys = set(exact_by_key) & set(candidate_by_key)
    exact_matches = sum(
        exact_by_key[key]["arm_id"] == candidate_by_key[key]["arm_id"]
        for key in shared_keys
    )
    candidate_sets = noncontrol_sets(rows)
    recalls = []
    jaccards = []
    for root_id in sorted(exact_sets):
        exact = exact_sets[root_id]
        candidate = candidate_sets[root_id]
        recalls.append(len(exact & candidate) / len(exact))
        union = exact | candidate
        jaccards.append(len(exact & candidate) / len(union))
    similarity = {
        "exact_arm_matches": exact_matches,
        "exact_arm_match_rate": exact_matches / EXPECTED_PROPOSALS,
        "mean_exact_noncontrol_union_recall": mean(recalls),
        "minimum_exact_noncontrol_union_recall": min(recalls),
        "mean_noncontrol_union_jaccard": mean(jaccards),
    }
    support = proposal_support(by_root, manifest_by_arm)
    gates = {
        "exact_grid_and_supported_pair_boundaries": not proposal_audit["failure_counts"]
        and proposal_audit["rows_a"] == EXPECTED_PROPOSALS
        and proposal_audit["roots"] == EXPECTED_ROOTS
        and proposal_audit["supported_rate"] == 1.0
        and proposal_audit["exact_arm_matches"] == EXPECTED_PROPOSALS,
        "exact_arm_agreement_at_least_80pct": similarity["exact_arm_match_rate"] >= 0.80,
        "mean_exact_union_recall_at_least_85pct": similarity[
            "mean_exact_noncontrol_union_recall"
        ]
        >= 0.85,
        "minimum_exact_union_recall_at_least_50pct": similarity[
            "minimum_exact_noncontrol_union_recall"
        ]
        >= 0.50,
        "mean_union_jaccard_at_least_75pct": similarity[
            "mean_noncontrol_union_jaccard"
        ]
        >= 0.75,
        "mean_unique_noncontrol_at_least_14": support[
            "mean_unique_supported_noncontrol_proposals_per_root"
        ]
        >= 14,
        "minimum_unique_noncontrol_at_least_6": support[
            "minimum_unique_supported_noncontrol_proposals"
        ]
        >= 6,
        "joint_proposal_at_every_root": support["root_rate_with_supported_joint"] == 1.0,
        "at_least_48_active_experts": support[
            "experts_noncontrol_in_at_least_25pct_roots"
        ]
        >= 48,
        "proposal_breadth": set(support["proposal_job_kinds"])
        == {"fell", "harvest", "mine", "renew"}
        and {"natural", "own", "opponent"}.issubset(
            support["proposal_provenance_classes"]
        )
        and support["proposal_seats"] == [0, 1]
        and set(support["proposal_opponent_families"]) == set(OPPONENTS)
        and support["proposal_reversed_role_order_present"],
        "base85_payload_at_most_13000": population_audit["base85_payload_bytes"]
        <= 13_000,
    }
    return (
        {
            "bits": bits,
            "pass": all(gates.values()),
            "gates": gates,
            "similarity": similarity,
            "support": support,
            "proposal_audit": proposal_audit,
            "population_audit": population_audit,
            "population_sha256": sha256(POPULATIONS[bits]),
            "proposal_sha256": sha256(PROPOSALS_A[bits]),
        },
        rows,
    )


def select_width() -> tuple[dict, list[dict[str, str]] | None]:
    prelock_hashes, immutable_pass = relative_hashes(PRELOCK_EXPECTED_HASHES)
    if not immutable_pass:
        raise RuntimeError("D105a prelock immutable hash mismatch")
    population_audits, populations_repeat = regenerate_populations()
    if not populations_repeat:
        raise RuntimeError("D105a population regeneration mismatch")
    exact_rows, _ = read_table(EXACT_PROPOSALS)
    manifest, _ = read_table(D97_MANIFEST)
    roots = root_manifest_rows(manifest)
    _, manifest_by_arm = manifest_support(manifest)
    exact_sets = noncontrol_sets(exact_rows)

    diagnostics = []
    selected_rows = None
    for bits in BITS:
        candidate, rows = fidelity_candidate(
            bits,
            exact_rows,
            exact_sets,
            roots,
            manifest_by_arm,
            population_audits[bits],
        )
        diagnostics.append(candidate)
        if candidate["pass"]:
            selected_rows = rows
            break
    selected = diagnostics[-1] if diagnostics[-1]["pass"] else None
    selection = {
        "schema": "troll-farm-d105a-outcome-blind-low-bit-lock-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "prelock_source_hashes": prelock_hashes,
        "population_regeneration_pass": populations_repeat,
        "evaluated_bits": [candidate["bits"] for candidate in diagnostics],
        "selected_bits": None if selected is None else selected["bits"],
        "selection_pass": selected is not None,
        "selected_population_sha256": None
        if selected is None
        else selected["population_sha256"],
        "selected_proposal_sha256": None
        if selected is None
        else selected["proposal_sha256"],
        "selected_fidelity": selected,
        "candidate_diagnostics": diagnostics,
        "higher_width_fidelity_inspected": False,
        "outcomes_read_during_selection": False,
    }
    return selection, selected_rows


def write_or_verify_lock(selection: dict) -> str:
    encoded = json.dumps(selection, indent=2, sort_keys=True) + "\n"
    if LOCK.exists():
        if LOCK.read_text() != encoded:
            raise RuntimeError("D105a existing outcome-blind lock differs")
    else:
        LOCK.write_text(encoded)
    return sha256(LOCK)


def full_analysis(selection: dict, selected_rows: list[dict[str, str]], lock_preexisting: bool) -> dict:
    bits = selection["selected_bits"]
    if bits is None:
        raise RuntimeError("D105a full analysis without selected precision")
    if not lock_preexisting:
        raise RuntimeError("D105a terminal analysis requires a preexisting outcome-blind lock")
    repeat_path = PROPOSALS_B[bits]
    if not repeat_path.exists():
        raise RuntimeError(f"D105a selected repeat is missing: {repeat_path}")
    repeat_rows, _ = read_table(repeat_path)
    repeat_identical = PROPOSALS_A[bits].read_bytes() == repeat_path.read_bytes()

    manifest, _ = read_table(D97_MANIFEST)
    roots = root_manifest_rows(manifest)
    _, manifest_by_arm = manifest_support(manifest)
    selected_audit, selected_by_root = validate_proposals(
        selected_rows,
        repeat_rows,
        roots,
        manifest_by_arm,
        read_experts(POPULATIONS[bits]),
        repeat_identical,
    )

    # Terminal/outcome access begins here, after the preexisting lock was verified.
    postlock_hashes, postlock_hashes_pass = relative_hashes(POSTLOCK_EXPECTED_HASHES)
    exact_rows, _ = read_table(EXACT_PROPOSALS)
    full_report = analyze_d104a(exact_rows, exact_rows, repeat_identical=True)
    oracle, details, d97_audit = analyze_value(
        selected_rows, full_report, manifest
    )
    value_gates = {
        "mean_margin_gain_at_least_28": oracle["mean_margin_delta_vs_d40_all_tasks"]
        >= 28,
        "retain_at_least_90pct_d104a_union_gain": oracle[
            "retained_fraction_of_d104a_union_gain"
        ]
        >= 0.90,
        "capture_at_least_78pct_d97_joint_oracle": oracle[
            "capture_of_d97_joint_oracle"
        ]
        >= 0.78,
        "strictly_improve_at_least_82pct_roots": oracle[
            "strict_root_improvement_rate"
        ]
        >= 0.82,
        "every_family_gain_at_least_15": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 15,
        "own_nonnegative_opponent_nonpositive": oracle[
            "mean_own_score_delta_vs_d40_all_tasks"
        ]
        >= 0
        and oracle["mean_opponent_score_delta_vs_d40_all_tasks"] <= 0,
        "crop_exact_and_worker_three_preserved": oracle[
            "proposal_oracle_crop_rate"
        ]
        == 1.0
        and oracle["proposal_oracle_worker_three_rate"]
        >= oracle["baseline_worker_three_rate"] - 0.05,
        "gain_at_least_2_beyond_full_best_single": oracle[
            "mean_incremental_margin_vs_full_best_single_rooted"
        ]
        >= 2,
        "joint_selected_in_at_least_50pct_roots": oracle["joint_selected_root_rate"]
        >= 0.50,
        "joint_beats_single_in_at_least_35pct_roots": oracle[
            "joint_strictly_beats_full_best_single_rate"
        ]
        >= 0.35,
        "selected_proposal_breadth": len(oracle["selected_job_kinds"]) >= 3
        and len(oracle["selected_provenance_classes"]) >= 2
        and oracle["selected_seats"] == [0, 1]
        and set(oracle["selected_opponent_families"]) == set(OPPONENTS)
        and oracle["selected_reversed_role_order_present"],
    }
    lock = json.loads(LOCK.read_text())
    integrity_gates = {
        "prelock_immutable_hashes_match": all(
            selection["prelock_source_hashes"][str(path.relative_to(ROOT))] == expected
            for path, expected in PRELOCK_EXPECTED_HASHES.items()
        ),
        "postlock_immutable_hashes_match": postlock_hashes_pass,
        "population_regeneration_identical": selection["population_regeneration_pass"],
        "lock_preexisting_and_outcome_blind": lock_preexisting
        and lock == selection
        and lock["outcomes_read_during_selection"] is False,
        "selected_hashes_match_lock": sha256(POPULATIONS[bits])
        == selection["selected_population_sha256"]
        and sha256(PROPOSALS_A[bits]) == selection["selected_proposal_sha256"],
        "selected_repeat_byte_identical": repeat_identical,
        "selected_proposal_integrity": not selected_audit["failure_counts"]
        and selected_audit["exact_arm_matches"] == EXPECTED_PROPOSALS,
        "selected_support_reproduced": proposal_support(
            selected_by_root, manifest_by_arm
        )
        == selection["selected_fidelity"]["support"],
        "d104a_integrity_reproduced": full_report["integrity_pass"],
        "d97_terminal_integrity_reproduced": not d97_audit[
            "integrity_failure_counts"
        ]
        and d97_audit["mirror_failures"] == 0
        and d97_audit["control_parity_failures"] == 0,
    }
    integrity_pass = all(integrity_gates.values())
    value_pass = integrity_pass and all(value_gates.values())
    passed = integrity_pass and selection["selection_pass"] and value_pass
    decision = (
        "open_d105b_fresh_map_recurrent_proposal_controller_preflight"
        if passed
        else "close_low_bit_full_expert_bank_after_value_failure"
    )
    return {
        "protocol": "D105a low-bit full-expert bank",
        "integrity_pass": integrity_pass,
        "selection_pass": selection["selection_pass"],
        "value_opened": True,
        "value_pass": value_pass,
        "pass": passed,
        "decision": decision,
        "selected_bits": bits,
        "selection_lock_sha256": sha256(LOCK),
        "selection": selection,
        "integrity_gates": integrity_gates,
        "value_gates": value_gates,
        "selected_proposal_audit": selected_audit,
        "quantized_oracle": oracle,
        "oracle_details": details,
        "postlock_source_hashes": postlock_hashes,
        "provenance": {
            "protocol_sha256": sha256(PROTOCOL),
            "lock_sha256": sha256(LOCK),
            "analyzer_sha256": sha256(Path(__file__)),
            "selected_population_sha256": sha256(POPULATIONS[bits]),
            "selected_proposals_a_sha256": sha256(PROPOSALS_A[bits]),
            "selected_proposals_b_sha256": sha256(PROPOSALS_B[bits]),
        },
        "scope": (
            "outcome-blind full-bank quantization selection and consumed D97 value audit only; "
            "no learner, new terminal simulation, candidate, platform action, or resident mutation"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-only", action="store_true")
    args = parser.parse_args()
    lock_preexisting = LOCK.exists()
    selection, selected_rows = select_width()
    lock_sha256 = write_or_verify_lock(selection)
    if args.lock_only or not selection["selection_pass"]:
        summary = {
            "selection_pass": selection["selection_pass"],
            "selected_bits": selection["selected_bits"],
            "evaluated_bits": selection["evaluated_bits"],
            "lock_sha256": lock_sha256,
            "candidate_summaries": [
                {
                    "bits": candidate["bits"],
                    "pass": candidate["pass"],
                    "failed_gates": [
                        name for name, passed in candidate["gates"].items() if not passed
                    ],
                    "similarity": candidate["similarity"],
                    "mean_unique_noncontrol": candidate["support"][
                        "mean_unique_supported_noncontrol_proposals_per_root"
                    ],
                }
                for candidate in selection["candidate_diagnostics"]
            ],
            "outcomes_read": False,
        }
        if not selection["selection_pass"]:
            OUTPUT.write_text(
                json.dumps(
                    {
                        "protocol": "D105a low-bit full-expert bank",
                        "selection_pass": False,
                        "value_opened": False,
                        "pass": False,
                        "decision": "close_low_bit_full_expert_bank_after_fidelity_failure",
                        "selection": selection,
                        "selection_lock_sha256": lock_sha256,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
        print(json.dumps(summary, sort_keys=True))
        return 0

    if selected_rows is None:
        raise RuntimeError("D105a selected rows unexpectedly absent")
    report = full_analysis(selection, selected_rows, lock_preexisting)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "pass": report["pass"],
                "decision": report["decision"],
                "selected_bits": report["selected_bits"],
                "fidelity": selection["selected_fidelity"]["similarity"],
                "support": selection["selected_fidelity"]["support"],
                "quantized_oracle": report["quantized_oracle"],
                "failed_value_gates": [
                    name for name, passed in report["value_gates"].items() if not passed
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
