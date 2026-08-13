#!/usr/bin/env python3
"""Append sigma runs 1, 3 and 4 to the registry inputs manifest.

Run 2 is deliberately NOT appended: its checkpoint carries a stale arena-room row
(agent 6604529's 22.46/140 served for deployment 41125448), so the builder would either
fault it (post-fix) or silently record another deployment's score (pre-fix).  Which field
is authoritative when the room is stale is a measurement-semantics decision for the
coordinator, not something this script should assume.
"""
from __future__ import annotations

import hashlib
import json
import sys

MANIFEST = "data/analysis/arena-submission-history-inputs.json"
BASE = "data/analysis/arena-noise-band-2026-08"


def sha256(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


RUNS = [
    # (run, submission_id, agent_id, checkpoint file)
    (1, 41125196, 6610399, f"{BASE}/run1-checkpoint-terminal.json"),
    # Run 2 enters through the *initial*-labelled artifact per the coordinator's ruling
    # 20260813T060000Z.  Despite the role string it is a complete terminal observation --
    # 160/160, pending 0, identity_clean true, arena and filtered_ladder both agent 6610636
    # at 23.73 -- captured 19:22:19Z, two minutes BEFORE the room went stale.  The
    # role string is a filename hint; maturity is keyed on content, never on the label.
    (2, 41125448, 6610636, f"{BASE}/run2-checkpoint-initial.json"),
    (3, 41128302, 6612307, f"{BASE}/run3-checkpoint-terminal.json"),
    (4, 41129543, 6614096, f"{BASE}/run4-checkpoint-terminal.json"),
]


def main() -> int:
    with open(MANIFEST, encoding="utf-8") as handle:
        manifest = json.load(handle)

    subs = {s["submission_id"]: s for s in manifest["submissions"]}
    obs_ids = {c["observation_id"] for c in manifest["checkpoint_inputs"]}

    # 41090606 was displaced by 41113243 -- evidence at
    # coordination/tasks/20260812-readable-no-orchard-rerun-arena.md:147 ("displaced: agent
    # 6594200 / submission 41090606"), supplied by the coordinator's ruling 20260813T060000Z.
    # This retires the pre-existing test_exactly_one_submission_is_active failure.
    subs[41090606]["disposition"] = "displaced_superseded"
    subs[41090606]["replaced_by_submission_id"] = 41113243
    subs[41090606]["disposition_rationale"] = (
        "Displaced by 41113243 / agent 6604529 at the readable-no-orchard rerun submission."
    )
    provenance = subs[41090606].setdefault("provenance", [])
    rerun_task = "coordination/tasks/20260812-readable-no-orchard-rerun-arena.md"
    if rerun_task not in provenance:
        provenance.append(rerun_task)

    # Run 3 is superseded by run 4; only run 4 remains deployed.
    subs[41128302]["agent_id"] = 6612307
    subs[41128302]["disposition"] = "displaced_superseded"
    subs[41128302]["replaced_by_submission_id"] = 41129543
    subs[41128302]["disposition_rationale"] = (
        "Sigma campaign run 3 of 4; terminal 160/160 read at 24.90, then displaced by run 4."
    )

    if 41129543 not in subs:
        manifest["submissions"].append(
            {
                "submission_id": 41129543,
                "agent_id": 6614096,
                "source_id": "e7a-readable-no-orchard-code-cost",
                "source_attribution_confidence": "hash_verified_on_platform",
                "era_id": "legend-147",
                "deployment_purpose": "same_source_capacity_control",
                "comparison_basis": "same_source_repeat",
                "authority": "owner_directed_override",
                "task_id": "20260810-arena-noise-band-measurement",
                "protocol_id": None,
                "deployed_at": "2026-08-13T05:24:00Z",
                "parent_submission_id": 41128302,
                "replaced_by_submission_id": None,
                "disposition": "active",
                "disposition_rationale": (
                    "Sigma campaign run 4 of 4, the last authorized Arena mutation."
                ),
                "provenance": ["coordination/tasks/20260810-arena-noise-band-measurement.md"],
                "notes": (
                    "Submit accepted=true ambiguous=false http=200, single mutation call, "
                    "source sha256 98628e98... verified before the call."
                ),
            }
        )

    for run, sub, agent, path in RUNS:
        oid = f"obs-{sub}-terminal160"
        if oid in obs_ids:
            continue
        manifest["checkpoint_inputs"].append(
            {
                "observation_id": oid,
                "path": path,
                "sha256": sha256(path),
                "expect_agent_id": agent,
                "expect_submission_id": sub,
                "observation_scope": "submission_scoped",
                "observed_at_override": None,
                "observed_at_override_evidence": None,
                "is_terminal_audit": True,
            }
        )
        print(f"appended sigma run {run}: {oid} ({path})")

    # Deliberately NOT re-sorted.  One legitimate record (`unknown-pre-reset-resident-6557204`)
    # carries submission_id null, so a naive sort raises; and reordering existing entries would
    # produce a large diff that buries the four lines actually being added.  The builder emits
    # observations in its own deterministic order regardless.

    with open(MANIFEST, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1, sort_keys=False)
        handle.write("\n")
    print("manifest written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
