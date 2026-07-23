#!/usr/bin/env python3
"""Lock D106a's q6 precision from fresh proposal support without outcomes."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d106a-q6-fresh-map-proposal-readout-protocol-2026-07-22.md"
MANIFEST = BASE / "d106a-full-d97-manifest-9827000-9827015.tsv"
POPULATIONS = {
    4: BASE / "d105a-q4-expert-population.tsv",
    6: BASE / "d105a-q6-expert-population.tsv",
}
PROPOSALS = {
    bits: BASE / f"d106a-q{bits}-proposals-9827000-9827015.tsv"
    for bits in (4, 6)
}
UNIONS = {
    bits: BASE / f"d106a-q{bits}-union-manifest-9827000-9827015.tsv"
    for bits in (4, 6)
}
UNION_LOCKS = {
    bits: BASE / f"d106a-q{bits}-proposal-union-lock.json" for bits in (4, 6)
}
LOCK = BASE / "d106a-q6-precision-selection-lock.json"
PROTOCOL_SHA256 = "809b2204e67214001e61d10d8e8edd3124b68e7256110daede489f6430b0418d"
POPULATION_HASHES = {
    4: "d32a0c0b6de7856e86ef55090e07807dc52bb676db626e5e2e7d69dd72d50b90",
    6: "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def noncontrol_sets(path: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in read_rows(path):
        result.setdefault(row["root_id"], set())
        if row["arm_kind"] != "control":
            result[row["root_id"]].add(row["arm_id"])
    return result


def build_lock() -> dict:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("D106a protocol hash mismatch")
    for bits in (4, 6):
        if sha256(POPULATIONS[bits]) != POPULATION_HASHES[bits]:
            raise RuntimeError(f"D106a q{bits} population hash mismatch")
    union_locks = {bits: json.loads(UNION_LOCKS[bits].read_text()) for bits in (4, 6)}
    for bits, lock in union_locks.items():
        if lock["protocol_sha256"] != PROTOCOL_SHA256:
            raise RuntimeError(f"D106a q{bits} union protocol mismatch")
        if lock["population_sha256"] != POPULATION_HASHES[bits]:
            raise RuntimeError(f"D106a q{bits} union population mismatch")
        if lock["outcomes_read"] is not False:
            raise RuntimeError(f"D106a q{bits} union is not outcome-blind")
        if lock["union_manifest_sha256"] != sha256(UNIONS[bits]):
            raise RuntimeError(f"D106a q{bits} union hash mismatch")

    sets = {bits: noncontrol_sets(UNIONS[bits]) for bits in (4, 6)}
    if set(sets[4]) != set(sets[6]):
        raise RuntimeError("D106a q4/q6 root mismatch")
    recalls = []
    jaccards = []
    for root_id in sorted(sets[4], key=int):
        q4 = sets[4][root_id]
        q6 = sets[6][root_id]
        recalls.append(len(q4 & q6) / len(q4))
        jaccards.append(len(q4 & q6) / len(q4 | q6))
    similarity = {
        "mean_q4_union_recall": sum(recalls) / len(recalls),
        "minimum_q4_union_recall": min(recalls),
        "mean_q4_q6_union_jaccard": sum(jaccards) / len(jaccards),
    }
    q4_support = union_locks[4]["support"]
    q6_support = union_locks[6]["support"]
    q4_active = q4_support["experts_noncontrol_in_at_least_25pct_roots"]
    q6_active = q6_support["experts_noncontrol_in_at_least_25pct_roots"]
    gates = {
        "exact_64_expert_root_grids": len(read_rows(PROPOSALS[4]))
        == q4_support["roots"] * 64
        and len(read_rows(PROPOSALS[6])) == q6_support["roots"] * 64,
        "q6_mean_unique_at_least_14": q6_support[
            "mean_unique_noncontrol_proposals_per_root"
        ]
        >= 14,
        "q6_minimum_unique_at_least_6": q6_support[
            "minimum_unique_noncontrol_proposals_per_root"
        ]
        >= 6,
        "q6_joint_at_every_root": q6_support["roots_with_joint"] == q6_support["roots"],
        "q6_at_least_48_active_experts": q6_active >= 48,
        "q6_improves_active_experts_over_q4": q6_active >= q4_active + 1,
        "q6_semantic_breadth": set(q6_support["job_kinds"])
        == {"fell", "harvest", "mine", "renew"}
        and {"natural", "own", "opponent"}.issubset(
            q6_support["provenance_classes"]
        )
        and q6_support["seats"] == [0, 1]
        and len(q6_support["opponents"]) == 8
        and q6_support["reversed_role_order_present"],
        "q6_mean_q4_recall_at_least_85pct": similarity["mean_q4_union_recall"]
        >= 0.85,
        "q6_minimum_q4_recall_at_least_50pct": similarity[
            "minimum_q4_union_recall"
        ]
        >= 0.50,
        "q6_mean_q4_jaccard_at_least_75pct": similarity[
            "mean_q4_q6_union_jaccard"
        ]
        >= 0.75,
        "q6_base85_payload_at_most_10000": 9_180 <= 10_000,
    }
    selected = all(gates.values())
    return {
        "schema": "troll-farm-d106a-q6-outcome-blind-precision-lock-v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "manifest_sha256": sha256(MANIFEST),
        "population_sha256": {
            f"q{bits}": sha256(POPULATIONS[bits]) for bits in (4, 6)
        },
        "proposal_sha256": {
            f"q{bits}": sha256(PROPOSALS[bits]) for bits in (4, 6)
        },
        "union_manifest_sha256": {
            f"q{bits}": sha256(UNIONS[bits]) for bits in (4, 6)
        },
        "union_lock_sha256": {
            f"q{bits}": sha256(UNION_LOCKS[bits]) for bits in (4, 6)
        },
        "q4_support": q4_support,
        "q6_support": q6_support,
        "q6_vs_q4_similarity": similarity,
        "selection_gates": gates,
        "selection_pass": selected,
        "selected_bits": 6 if selected else None,
        "q6_base85_payload_bytes": 9_180,
        "consumed_d105a_q6_proposals_inspected": False,
        "outcomes_read": False,
    }


def main() -> int:
    lock = build_lock()
    encoded = json.dumps(lock, indent=2, sort_keys=True) + "\n"
    if LOCK.exists():
        if LOCK.read_text() != encoded:
            raise RuntimeError("D106a existing precision lock differs")
    else:
        LOCK.write_text(encoded)
    print(
        json.dumps(
            {
                "selection_pass": lock["selection_pass"],
                "selected_bits": lock["selected_bits"],
                "failed_gates": [
                    name for name, passed in lock["selection_gates"].items() if not passed
                ],
                "q4_active_experts": lock["q4_support"][
                    "experts_noncontrol_in_at_least_25pct_roots"
                ],
                "q6_active_experts": lock["q6_support"][
                    "experts_noncontrol_in_at_least_25pct_roots"
                ],
                "similarity": lock["q6_vs_q4_similarity"],
                "lock_sha256": sha256(LOCK),
                "outcomes_read": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
