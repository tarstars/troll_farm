#!/usr/bin/env python3
"""Build D75b's horizon-repaired outcome-blind sequence manifest."""

from __future__ import annotations

import collections
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
import cgauto.make_d75a_option_sequence_manifest as base  # noqa: E402
from cgauto.rl_batch_option_env import OPPONENTS  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d75b-two-batch-option-sequence-repair-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d75b-option-sequence-manifest.tsv"
SUMMARY = ANALYSIS / "d75b-option-sequence-manifest-summary.json"
MAX_ELIGIBLE_TURN_EXCLUSIVE = 299


def repaired_bank() -> tuple[list[dict], dict]:
    bank, census = base.collect_bank()
    repaired = [row for row in bank if row["turn"] < MAX_ELIGIBLE_TURN_EXCLUSIVE]
    return repaired, {
        **census,
        "base_eligible_states": len(bank),
        "eligible_states": len(repaired),
        "repair_horizon_exclusions": len(bank) - len(repaired),
        "maximum_eligible_turn_exclusive": MAX_ELIGIBLE_TURN_EXCLUSIVE,
    }


def main() -> int:
    if MANIFEST.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite D75b manifest artifacts")
    bank_a, census_a = repaired_bank()
    bank_b, census_b = repaired_bank()
    selected_a = base.select_rows(bank_a)
    selected_b = base.select_rows(bank_b)
    payload_a = base.serialize(selected_a)
    payload_b = base.serialize(selected_b)
    repeat_exact = payload_a == payload_b and census_a == census_b
    if not repeat_exact:
        raise RuntimeError("D75b outcome-blind manifest generation is not deterministic")
    with MANIFEST.open("xb") as target:
        target.write(payload_a)

    partitions = collections.Counter(row["partition"] for row in selected_a)
    strata = collections.Counter(
        (row["partition"], row["opponent"], row["seat"], row["phase"])
        for row in selected_a
    )
    expected_strata = {
        (partition, opponent, seat, phase_name)
        for partition in ("discovery", "validation")
        for opponent in OPPONENTS
        for seat in (0, 1)
        for phase_name in ("early", "middle", "late")
    }
    gates = {
        "repeat_byte_exact": repeat_exact,
        "exactly_576_unique_states": (
            len(selected_a) == 576
            and len({base.identity(row) for row in selected_a}) == len(selected_a)
        ),
        "exactly_288_each_partition": partitions
        == collections.Counter({"discovery": 288, "validation": 288}),
        "all_partition_opponent_seat_phase_strata": set(strata) == expected_strata,
        "six_rows_each_stratum": all(strata[key] == base.PER_STRATUM for key in expected_strata),
        "all_features_finite_source_free_and_before_repaired_horizon": all(
            row["turn"] < MAX_ELIGIBLE_TURN_EXCLUSIVE
            and np.isfinite(row["features"]).all()
            and np.all(row["features"][56:64] == 0.0)
            and row["features"][69] == 0.0
            and row["features"][70] == 1.0
            and row["features"][71] == 0.0
            for row in selected_a
        ),
    }
    report = {
        "schema": "troll-farm-d75b-option-sequence-manifest-v1",
        "protocol": sha256_file(PROTOCOL),
        "generator": sha256_file(Path(__file__)),
        "base_generator": sha256_file(Path(base.__file__)),
        "repair": {
            "d75a_result": "17b9ff7353bd3ed1ea439c8daf9aab5c6e0e3acb89279870af132cd6f203a4e2",
            "only_change": "maximum eligible turn exclusive changed from 300 to 299",
        },
        "seed_base": base.SEED_BASE,
        "maps": base.MAPS,
        "quota_per_stratum": base.PER_STRATUM,
        "census": census_a,
        "samples": len(selected_a),
        "partition_counts": dict(sorted(partitions.items())),
        "stratum_counts": {
            "|".join(map(str, key)): value for key, value in sorted(strata.items())
        },
        "manifest": sha256_file(MANIFEST),
        "gates": gates,
        "pass": all(gates.values()),
        "selection_outcome_blind": True,
    }
    atomic_write_new(SUMMARY, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
