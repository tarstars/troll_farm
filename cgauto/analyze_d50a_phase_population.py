#!/usr/bin/env python3
"""Validate and score the frozen D50a phase-recombined opponent population."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.field_continuation_coverage import (
    INTEGER_FIELDS,
    archetype_key,
    read_local_rows,
    score_model_game,
)
from cgauto.field_economy_catalog_calibration import partition


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = (
    ANALYSIS / "d50a-phase-recombined-opponent-population-protocol-2026-07-21.md"
)
AMENDMENT = ANALYSIS / "d50a-current-substrate-baseline-amendment-2026-07-21.md"
MANIFEST = ANALYSIS / "d50a-current-substrate-manifest.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
RUN_A = ANALYSIS / "d50a-phase-population-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d50a-phase-population-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d50a-phase-population-coverage-result.json"

LEGACY_FILES = (
    ANALYSIS / "d50a-current-baseline-phase21-local.tsv",
    ANALYSIS / "d50a-current-economy-phase21-local.tsv",
    ANALYSIS / "d50a-current-structural-phase21-local.tsv",
    ANALYSIS / "d50a-current-legend-v1-phase21-local.tsv",
    ANALYSIS / "d50a-current-legend-v2-phase21-local.tsv",
)

LEGACY_GRID_SIZES = (1_280, 4_960, 1_760, 1_280, 1_280)
LEGACY_MODEL_COUNTS = (8, 31, 11, 8, 8)

EXPECTED_SHA256 = {
    PROTOCOL: "d04d2b1621d1ea933bbc07b7f3fc5b33b33d0d0be6282d82cc77178d5b583608",
    AMENDMENT: "dd117c80446f4e613b3f1daa35897445ded1b13dcd48ed6b913bbbfcbb0aa536",
    MANIFEST: "0fa8c83d345e300983a4d59c92be0ba73d342d324fcdb4c0dc7d338af1e2e9a3",
    RUNNER: "03f640c48b268c4d49d36503dce2cdf7c32ffbfe0775df6d5421641c27ed1b8e",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    LEGACY_FILES[0]: "73d441becb6628a9fddd1bf57c1f9e406c9a36489a45141d3c2a924860d557c7",
    LEGACY_FILES[1]: "6fcbdc1057c1b81de47c58037ea309d5d7ca2e54b6d19248594e2ade1732d8c4",
    LEGACY_FILES[2]: "29e85cb293cd527512260e6a083252f126f25557cbd491162abfd600d6fa5a2a",
    LEGACY_FILES[3]: "c18ba0a3a056eb89ce3f9df06c23cc7d3dcf1949cf88e620ed67bb66b58e6a93",
    LEGACY_FILES[4]: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
    RUN_A: "8c5c40c11cd7a3d28510be9b57e5f850b72c85ef154513a4fc57fd8b752a8598",
    RUN_B: "8c5c40c11cd7a3d28510be9b57e5f850b72c85ef154513a4fc57fd8b752a8598",
}

COMPONENTS = (
    "v2_hp2_farm",
    "v2_hp2_late",
    "v2_bal_farm",
    "norx_compact",
    "farm3",
    "farm4",
    "lean",
    "norx_funded",
)

ANCHOR_HISTORY = {
    "v2_hp2_farm": (LEGACY_FILES[4], "legend_v2_hp2_cheap_farm"),
    "v2_hp2_late": (LEGACY_FILES[4], "legend_v2_hp2_cheap_late_chop"),
    "v2_bal_farm": (LEGACY_FILES[4], "legend_v2_balanced_cheap_farm"),
    "norx_compact": (LEGACY_FILES[2], "norx_compact"),
    "farm3": (LEGACY_FILES[1], "farm3_hold0_cap20"),
    "farm4": (LEGACY_FILES[1], "farm4_s30_hold120_cap24"),
    "lean": (LEGACY_FILES[1], "lean_m1c2h0k2"),
    "norx_funded": (LEGACY_FILES[2], "norx_funded_silver"),
}

RICH = "rich3plus:farm_wood:train_now"


def expected_models() -> tuple[str, ...]:
    labels = [f"d50_anchor_{component}" for component in COMPONENTS]
    labels.extend(
        f"d50_t{cut}_{early}_to_{late}"
        for early in COMPONENTS
        for late in COMPONENTS
        if early != late
        for cut in (100, 150)
    )
    return tuple(labels)


MODELS = expected_models()
SWITCH_METADATA = {
    f"d50_t{cut}_{early}_to_{late}": {
        "early": early,
        "late": late,
        "cut": cut,
    }
    for early in COMPONENTS
    for late in COMPONENTS
    if early != late
    for cut in (100, 150)
}


def terminal_signature(row: dict) -> tuple[int, ...]:
    return tuple(int(row[field]) for field in INTEGER_FIELDS if field != "game_id")


def without_model(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "model"}


def validate_phase_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(int(row["game_id"]), row["model"]) for row in rows}
    if len(rows) != 19_200 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D50a phase-population grid is not exact 160 x 120")


def activation_gates(
    *,
    repeat_exact: bool,
    grid_exact: bool,
    anchors_exact: bool,
    openings_exact: bool,
    changed_cells: int,
    active_policies: int,
) -> dict[str, bool]:
    return {
        "complete_byte_exact_repeat": repeat_exact and grid_exact,
        "all_eight_anchors_exact": anchors_exact,
        "all_switch_openings_exact": openings_exact,
        "at_least_40_percent_switch_cells_active": changed_cells >= 7_168,
        "at_least_80_switch_policies_active_on_10_percent_maps": active_policies >= 80,
    }


def support_gates(summary: dict, no_legacy_loss: bool) -> dict[str, bool]:
    confirmation = summary["confirmation"]
    return {
        "overall_macro_at_least_56_of_80": confirmation["overall"]["augmented"][
            "macro"
        ]
        >= 56,
        "overall_full_at_least_36_of_80": confirmation["overall"]["augmented"][
            "full"
        ]
        >= 36,
        "catastrophic_macro_at_least_7_of_19": confirmation["catastrophic"][
            "augmented"
        ]["macro"]
        >= 7,
        "worker_rich_macro_at_least_12_of_28": confirmation["worker_rich"][
            "augmented"
        ]["macro"]
        >= 12,
        "rich_macro_at_least_4_of_9": confirmation["rich_immediate"]["augmented"][
            "macro"
        ]
        >= 4,
        "rich_full_at_least_1_of_9": confirmation["rich_immediate"]["augmented"][
            "full"
        ]
        >= 1,
        "overall_macro_increment_at_least_5": confirmation["overall"]["increment"][
            "macro"
        ]
        >= 5,
        "overall_full_increment_at_least_3": confirmation["overall"]["increment"][
            "full"
        ]
        >= 3,
        "catastrophic_macro_increment_at_least_3": confirmation["catastrophic"][
            "increment"
        ]["macro"]
        >= 3,
        "worker_rich_macro_increment_at_least_4": confirmation["worker_rich"][
            "increment"
        ]["macro"]
        >= 4,
        "rich_macro_increment_at_least_2": confirmation["rich_immediate"][
            "increment"
        ]["macro"]
        >= 2,
        "rich_full_increment_at_least_1": confirmation["rich_immediate"][
            "increment"
        ]["full"]
        >= 1,
        "no_previously_covered_confirmation_game_lost": no_legacy_loss,
    }


def cohort_ids(records: dict[int, dict], split: str) -> dict[str, list[int]]:
    ids = sorted(game_id for game_id in records if partition(game_id) == split)
    return {
        "overall": ids,
        "catastrophic": [
            game_id for game_id in ids if bool(records[game_id]["catastrophic"])
        ],
        "worker_rich": [
            game_id for game_id in ids if bool(records[game_id]["worker_rich"])
        ],
        "rich_immediate": [
            game_id for game_id in ids if archetype_key(records[game_id]) == RICH
        ],
    }


def coverage_counts(
    ids: list[int],
    legacy: dict[int, list[dict]],
    phase: dict[int, list[dict]],
) -> dict:
    def count(rows: dict[int, list[dict]], field: str) -> int:
        return sum(any(row[field] for row in rows[game_id]) for game_id in ids)

    legacy_counts = {
        "macro": count(legacy, "macro_covers"),
        "full": count(legacy, "fully_covers"),
    }
    phase_counts = {
        "macro": count(phase, "macro_covers"),
        "full": count(phase, "fully_covers"),
    }
    augmented_counts = {
        field: sum(
            any(row[field] for row in legacy[game_id])
            or any(row[field] for row in phase[game_id])
            for game_id in ids
        )
        for field in ("macro_covers", "fully_covers")
    }
    augmented = {
        "macro": augmented_counts["macro_covers"],
        "full": augmented_counts["fully_covers"],
    }
    return {
        "games": len(ids),
        "legacy": legacy_counts,
        "phase": phase_counts,
        "augmented": augmented,
        "increment": {
            field: augmented[field] - legacy_counts[field] for field in ("macro", "full")
        },
    }


def nearest_summary(
    ids: list[int],
    legacy: dict[int, list[dict]],
    phase: dict[int, list[dict]],
) -> dict:
    old = [
        min(row["normalized_macro_distance"] for row in legacy[game_id])
        for game_id in ids
    ]
    new = [
        min(
            *(row["normalized_macro_distance"] for row in legacy[game_id]),
            *(row["normalized_macro_distance"] for row in phase[game_id]),
        )
        for game_id in ids
    ]
    return {
        "legacy_mean": statistics.mean(old),
        "augmented_mean": statistics.mean(new),
        "mean_delta": statistics.mean(new) - statistics.mean(old),
        "improved_games": sum(after < before for before, after in zip(old, new)),
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D50a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D50a phase-population repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D50a result")

    observed = json.loads(OBSERVED.read_text())
    records = {int(record["game_id"]): record for record in observed.get("records") or []}
    if len(records) != 160:
        raise ValueError("D50a observed cohort is not 160 unique games")

    rows_a = read_local_rows(RUN_A)
    rows_b = read_local_rows(RUN_B)
    validate_phase_grid(rows_a, set(records))
    validate_phase_grid(rows_b, set(records))
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    by_phase = {(row["game_id"], row["model"]): row for row in rows_a}

    legacy_rows_by_file = {path: read_local_rows(path) for path in LEGACY_FILES}
    for path, expected_rows, expected_models_count in zip(
        LEGACY_FILES, LEGACY_GRID_SIZES, LEGACY_MODEL_COUNTS
    ):
        rows = legacy_rows_by_file[path]
        identities = {(row["game_id"], row["model"]) for row in rows}
        models = {row["model"] for row in rows}
        if (
            len(rows) != expected_rows
            or len(identities) != expected_rows
            or {row["game_id"] for row in rows} != set(records)
            or len(models) != expected_models_count
        ):
            raise ValueError(f"D50a regenerated legacy grid mismatch: {path}")
    historical = {
        (path, row["game_id"], row["model"]): row
        for path, rows in legacy_rows_by_file.items()
        for row in rows
    }
    anchor_mismatches = []
    for component, (path, historical_label) in ANCHOR_HISTORY.items():
        anchor_label = f"d50_anchor_{component}"
        for game_id in records:
            phase_row = by_phase[(game_id, anchor_label)]
            old_row = historical[(path, game_id, historical_label)]
            if without_model(phase_row) != without_model(old_row):
                anchor_mismatches.append((game_id, anchor_label, historical_label))

    opening_mismatches = []
    changed_cells = 0
    changed_by_policy = defaultdict(int)
    for label, metadata in SWITCH_METADATA.items():
        anchor = f"d50_anchor_{metadata['early']}"
        for game_id in records:
            row = by_phase[(game_id, label)]
            early = by_phase[(game_id, anchor)]
            if row["first_commands"] != early["first_commands"]:
                opening_mismatches.append((game_id, label))
            if terminal_signature(row) != terminal_signature(early):
                changed_cells += 1
                changed_by_policy[label] += 1
    active_policies = sum(changed_by_policy[label] >= 16 for label in SWITCH_METADATA)
    activation = {
        "switch_cells": len(SWITCH_METADATA) * len(records),
        "changed_from_early_anchor_cells": changed_cells,
        "changed_from_early_anchor_rate": changed_cells
        / (len(SWITCH_METADATA) * len(records)),
        "switch_policies": len(SWITCH_METADATA),
        "policies_active_on_at_least_16_maps": active_policies,
        "anchor_mismatches": len(anchor_mismatches),
        "opening_mismatches": len(opening_mismatches),
    }
    mechanical_gates = activation_gates(
        repeat_exact=repeat_exact,
        grid_exact=True,
        anchors_exact=not anchor_mismatches,
        openings_exact=not opening_mismatches,
        changed_cells=changed_cells,
        active_policies=active_policies,
    )

    legacy_scored: dict[int, list[dict]] = defaultdict(list)
    for rows in legacy_rows_by_file.values():
        for row in rows:
            legacy_scored[row["game_id"]].append(
                {"model": row["model"], **score_model_game(records[row["game_id"]], row)}
            )
    phase_scored: dict[int, list[dict]] = defaultdict(list)
    for row in rows_a:
        phase_scored[row["game_id"]].append(
            {"model": row["model"], **score_model_game(records[row["game_id"]], row)}
        )

    support = {}
    nearest = {}
    split_cohorts = {}
    for split in ("discovery", "confirmation"):
        split_cohorts[split] = cohort_ids(records, split)
        support[split] = {
            cohort: coverage_counts(ids, legacy_scored, phase_scored)
            for cohort, ids in split_cohorts[split].items()
        }
        nearest[split] = {
            cohort: nearest_summary(ids, legacy_scored, phase_scored)
            for cohort, ids in split_cohorts[split].items()
        }
    confirmation_ids = split_cohorts["confirmation"]["overall"]
    no_legacy_loss = all(
        not any(row["macro_covers"] for row in legacy_scored[game_id])
        or any(row["macro_covers"] for row in [*legacy_scored[game_id], *phase_scored[game_id]])
        for game_id in confirmation_ids
    ) and all(
        not any(row["fully_covers"] for row in legacy_scored[game_id])
        or any(row["fully_covers"] for row in [*legacy_scored[game_id], *phase_scored[game_id]])
        for game_id in confirmation_ids
    )
    value_gates = support_gates(support, no_legacy_loss)

    new_confirmation = []
    for game_id in confirmation_ids:
        legacy_macro = any(row["macro_covers"] for row in legacy_scored[game_id])
        phase_coverers = sorted(
            row["model"] for row in phase_scored[game_id] if row["macro_covers"]
        )
        if not legacy_macro and phase_coverers:
            record = records[game_id]
            new_confirmation.append(
                {
                    "game_id": game_id,
                    "opponent": record["opponent"],
                    "catastrophic": bool(record["catastrophic"]),
                    "worker_rich": bool(record["worker_rich"]),
                    "rich_immediate": archetype_key(record) == RICH,
                    "covering_phase_policies": phase_coverers,
                }
            )

    multiplicity = {}
    for split, cohorts in split_cohorts.items():
        counts = [
            sum(row["macro_covers"] for row in phase_scored[game_id])
            for game_id in cohorts["overall"]
        ]
        multiplicity[split] = {
            "mean_phase_macro_coverers": statistics.mean(counts),
            "median_phase_macro_coverers": statistics.median(counts),
            "max_phase_macro_coverers": max(counts),
            "games_with_phase_macro_support": sum(value > 0 for value in counts),
        }

    per_opponent = {}
    for opponent in sorted({records[game_id]["opponent"] for game_id in confirmation_ids}):
        ids = [
            game_id
            for game_id in confirmation_ids
            if records[game_id]["opponent"] == opponent
        ]
        per_opponent[opponent] = coverage_counts(ids, legacy_scored, phase_scored)

    gates = {**mechanical_gates, **value_gates}
    report = {
        "schema": 1,
        "scope": (
            "consumed-map opponent-population coverage only; no candidate, fresh-map, "
            "TestSession, submission, or Arena evidence"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "amendment": str(AMENDMENT),
        "amendment_sha256": sha256(AMENDMENT),
        "manifest_sha256": sha256(MANIFEST),
        "inputs": {
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "legacy_sha256": {path.name: sha256(path) for path in LEGACY_FILES},
            "run_a_sha256": sha256(RUN_A),
            "run_b_sha256": sha256(RUN_B),
            "runner_sha256": sha256(RUNNER),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "grid": {
            "games": len(records),
            "models": len(MODELS),
            "cells_per_run": len(rows_a),
            "repeat_byte_identical": repeat_exact,
        },
        "activation": activation,
        "support": support,
        "nearest_distance": nearest,
        "phase_covering_multiplicity": multiplicity,
        "new_confirmation_macro_support": new_confirmation,
        "confirmation_per_opponent": per_opponent,
        "gates": gates,
        "pass": all(gates.values()),
        "decision": (
            "retain frozen phase population for a separately gated fresh-map robust search"
            if all(gates.values())
            else "close fixed phase recombination and require state/history-conditioned opponent generation"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
