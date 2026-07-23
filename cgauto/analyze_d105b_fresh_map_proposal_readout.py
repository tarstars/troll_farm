#!/usr/bin/env python3
"""Audit D105b's outcome-blind fresh-map proposal support branch."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.make_d105b_proposal_union_manifest import (  # noqa: E402
    build_union,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d105b-fresh-map-proposal-readout-protocol-2026-07-22.md"
AMENDMENT = BASE / "d105b-d104-cardinality-measurement-amendment-2026-07-22.md"
UNION_BUILDER = ROOT / "cgauto" / "make_d105b_proposal_union_manifest.py"
ADAPTER = ROOT / "cgauto" / "d105b_d104_cardinality_adapter.py"
MANIFEST_RUNNER = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_manifest.rs"
PROPOSAL_RUNNER = ROOT / "rust" / "src" / "bin" / "d104_d98_expert_proposal_coverage.rs"
CONTINUATION_RUNNER = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_continuations.rs"
POPULATION = BASE / "d105a-q4-expert-population.tsv"
FULL_MANIFEST = BASE / "d105b-full-d97-manifest-9826000-9826015.tsv"
PADDED_MANIFEST = BASE / "d105b-d104-padded-manifest-9826000-9826015.tsv"
ADAPTER_METADATA = BASE / "d105b-d104-cardinality-adapter.json"
RAW_PROPOSALS = BASE / "d105b-q4-proposals-raw-padded-9826000-9826015.tsv"
PROPOSALS = BASE / "d105b-q4-proposals-9826000-9826015.tsv"
UNION_MANIFEST = BASE / "d105b-q4-union-manifest-9826000-9826015.tsv"
LOCK = BASE / "d105b-proposal-union-lock.json"
OUTPUT = BASE / "d105b-fresh-map-proposal-readout-result.json"
TERMINAL_OUTPUTS = (
    BASE / "d105b-q4-union-arms-a-9826000-9826015.tsv",
    BASE / "d105b-q4-union-arms-b-9826000-9826015.tsv",
    BASE / "d105b-q4-baselines-a-9826000-9826015.tsv",
    BASE / "d105b-q4-baselines-b-9826000-9826015.tsv",
)

EXPECTED_HASHES = {
    PROTOCOL: "42b5dd0f689b8d8d7e110d7babf6bcf4ea41b21811c3a28017cbbd8c3720962a",
    AMENDMENT: "2a9ef21225c0eee4bee3fb51ce5c0bd400b6430761f7a43214239732113efac1",
    UNION_BUILDER: "e2872dcaadd8826210ee2e902daf7dec4e5522f2910fcf4117fb7699e9bf8a96",
    ADAPTER: "6f5c8e062e7449ed30f5701c1a9b73609fe250a4f3102ccce5ac8427f3866546",
    MANIFEST_RUNNER: "f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23",
    PROPOSAL_RUNNER: "c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393",
    CONTINUATION_RUNNER: "e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4",
    POPULATION: "d32a0c0b6de7856e86ef55090e07807dc52bb676db626e5e2e7d69dd72d50b90",
    FULL_MANIFEST: "389d5a3111e5232dbbea85f051b46babad9d370072599c37fe44b0e6aa0cb81b",
    PADDED_MANIFEST: "050256b9bac0f58d05c8a0ca5e347ec80615fafe02a977c48ce5e087edd96acd",
    ADAPTER_METADATA: "65f9f8edb053b7a6b61499d7e959e6b4ee28c1aeca35f94112ffcda8d013a17b",
    RAW_PROPOSALS: "b5ae93d3fe444ab062a1a9a9ec547a4b5653d0d4fba58e6c615fff694969dade",
    PROPOSALS: "e93a427677ef2fb18b25246bd5b5e9e4e0ad35d47785b9d747880f219e1345f0",
    UNION_MANIFEST: "d7087fb6ec219ee9ad7afa229dda69368d1ddb72eba52bab07ec708237e5b5d2",
    LOCK: "7644971cb739b8c38365aa63a69c2964801d75df9b2d4210d3f74b3f1c83f1fa",
}


def main() -> int:
    source_hashes = {
        str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES
    }
    hashes_pass = all(
        source_hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED_HASHES.items()
    )
    if not hashes_pass:
        raise RuntimeError("D105b immutable hash mismatch")
    rows, fields, regenerated = build_union(
        FULL_MANIFEST, PROPOSALS, POPULATION, PROTOCOL
    )
    lock = json.loads(LOCK.read_text())
    regenerated["union_manifest_sha256"] = sha256(UNION_MANIFEST)
    lock_reproduced = regenerated == lock
    if not lock_reproduced:
        raise RuntimeError("D105b outcome-blind union lock does not reproduce")

    import csv

    with PROPOSALS.open(newline="") as source:
        proposals = list(csv.DictReader(source, delimiter="\t"))
    expert_counts = Counter(
        row["expert"] for row in proposals if row["arm_kind"] != "control"
    )
    root_count = lock["support"]["roots"]
    active_floor = (root_count + 3) // 4
    ordered_activity = sorted(
        (
            {
                "expert": f"four_{index:02}",
                "noncontrol_roots": expert_counts[f"four_{index:02}"],
                "rate": expert_counts[f"four_{index:02}"] / root_count,
            }
            for index in range(64)
        ),
        key=lambda row: (-row["noncontrol_roots"], row["expert"]),
    )
    support = lock["support"]
    support_gates = {
        "at_least_220_roots": support["roots"] >= 220,
        "mean_unique_noncontrol_at_least_14": support[
            "mean_unique_noncontrol_proposals_per_root"
        ]
        >= 14,
        "minimum_unique_noncontrol_at_least_6": support[
            "minimum_unique_noncontrol_proposals_per_root"
        ]
        >= 6,
        "joint_at_every_root": support["roots_with_joint"] == support["roots"],
        "at_least_48_experts_active_on_25pct_roots": support[
            "experts_noncontrol_in_at_least_25pct_roots"
        ]
        >= 48,
        "semantic_breadth": set(support["job_kinds"])
        == {"fell", "harvest", "mine", "renew"}
        and {"natural", "own", "opponent"}.issubset(
            support["provenance_classes"]
        )
        and support["seats"] == [0, 1]
        and len(support["opponents"]) == 8
        and support["reversed_role_order_present"],
    }
    terminal_outputs_absent = all(not path.exists() for path in TERMINAL_OUTPUTS)
    integrity_gates = {
        "immutable_hashes_match": hashes_pass,
        "lock_reproduced": lock_reproduced,
        "filtered_rows_reproduce": len(rows) == support["selected_arms"]
        and fields
        and sha256(UNION_MANIFEST) == lock["union_manifest_sha256"],
        "adapter_exact_233_to_240": json.loads(ADAPTER_METADATA.read_text())[
            "source_roots"
        ]
        == 233
        and json.loads(ADAPTER_METADATA.read_text())["target_roots"] == 240,
        "stripped_grid_exact": len(proposals) == 233 * 64,
        "terminal_outputs_absent": terminal_outputs_absent,
        "outcomes_unread": lock["outcomes_read"] is False,
    }
    integrity_pass = all(integrity_gates.values())
    support_pass = integrity_pass and all(support_gates.values())
    report = {
        "protocol": "D105b fresh-map proposal readout",
        "integrity_pass": integrity_pass,
        "support_pass": support_pass,
        "terminal_value_opened": False,
        "readout_fit_opened": False,
        "pass": False,
        "decision": "close_d105b_q4_fresh_map_readout_before_outcomes",
        "integrity_gates": integrity_gates,
        "support_gates": support_gates,
        "failed_support_gates": [
            name for name, passed in support_gates.items() if not passed
        ],
        "support": support,
        "active_root_floor": active_floor,
        "expert_activity": ordered_activity,
        "activity_boundary": {
            "experts_at_or_above_floor": sum(
                row["noncontrol_roots"] >= active_floor for row in ordered_activity
            ),
            "expert_48": ordered_activity[47],
            "expert_49": ordered_activity[48],
        },
        "source_hashes": source_hashes,
        "provenance": {
            "protocol_sha256": sha256(PROTOCOL),
            "amendment_sha256": sha256(AMENDMENT),
            "lock_sha256": sha256(LOCK),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "scope": (
            "fresh-map outcome-blind q4 proposal support only; no terminal continuation, value, "
            "fit, candidate, or platform action"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "integrity_pass": integrity_pass,
                "support_pass": support_pass,
                "decision": report["decision"],
                "failed_support_gates": report["failed_support_gates"],
                "support": support,
                "activity_boundary": report["activity_boundary"],
                "terminal_value_opened": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
