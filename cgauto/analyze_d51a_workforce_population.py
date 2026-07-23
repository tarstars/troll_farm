#!/usr/bin/env python3
"""Validate and score the frozen D51a workforce-history opponent population."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d50a_phase_population import (
    ANCHOR_HISTORY,
    COMPONENTS,
    LEGACY_FILES,
    LEGACY_GRID_SIZES,
    LEGACY_MODEL_COUNTS,
    cohort_ids,
    coverage_counts,
    nearest_summary,
    terminal_signature,
)
from cgauto.field_continuation_coverage import read_local_rows, score_model_game


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d51a-workforce-history-opponent-population-protocol-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
RUN_A = ANALYSIS / "d51a-workforce-population-a-phase21-local.tsv"
RUN_B = ANALYSIS / "d51a-workforce-population-b-phase21-local.tsv"
OUTPUT = ANALYSIS / "d51a-workforce-population-activation-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "99e87ea222d3762f368979274190d38ffe44c7e48ba52ef7dbfe201de8857224",
    RUNNER: "74dc0cca758f2e97902662a62656555ce790ec6b4aceaa225c37ae4b056bc3e4",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    LEGACY_FILES[0]: "73d441becb6628a9fddd1bf57c1f9e406c9a36489a45141d3c2a924860d557c7",
    LEGACY_FILES[1]: "6fcbdc1057c1b81de47c58037ea309d5d7ca2e54b6d19248594e2ade1732d8c4",
    LEGACY_FILES[2]: "29e85cb293cd527512260e6a083252f126f25557cbd491162abfd600d6fa5a2a",
    LEGACY_FILES[3]: "c18ba0a3a056eb89ce3f9df06c23cc7d3dcf1949cf88e620ed67bb66b58e6a93",
    LEGACY_FILES[4]: "2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b",
}

EARLY_COMPONENTS = ("v2_hp2_farm", "v2_hp2_late", "v2_bal_farm")
LATE_COMPONENTS = ("farm3", "farm4", "lean", "norx_funded", "v2_hp2_late")
TRIGGERS = ("w3_now", "w3_plus25", "w3_plus50", "w3_score60")


def expected_models() -> tuple[str, ...]:
    labels = [f"d51_anchor_{component}" for component in COMPONENTS]
    labels.extend(
        f"d51_{trigger}_{early}_to_{late}"
        for early in EARLY_COMPONENTS
        for late in LATE_COMPONENTS
        if early != late
        for trigger in TRIGGERS
    )
    return tuple(labels)


MODELS = expected_models()
SWITCH_METADATA = {
    f"d51_{trigger}_{early}_to_{late}": {
        "trigger": trigger,
        "early": early,
        "late": late,
    }
    for early in EARLY_COMPONENTS
    for late in LATE_COMPONENTS
    if early != late
    for trigger in TRIGGERS
}


def read_d51(path: Path) -> list[dict]:
    rows = read_local_rows(path)
    for row in rows:
        for field in ("third_worker_turn", "switch_turn", "switch_score"):
            row[field] = int(row[field])
    return rows


def validate_grid(rows: list[dict], game_ids: set[int]) -> None:
    expected = {(game_id, model) for game_id in game_ids for model in MODELS}
    identities = {(row["game_id"], row["model"]) for row in rows}
    if len(rows) != 10_240 or len(identities) != len(rows) or identities != expected:
        raise ValueError("D51a grid is not exact 160 x 64")


def trigger_is_valid(metadata: dict, row: dict) -> bool:
    third = int(row["third_worker_turn"])
    switch = int(row["switch_turn"])
    score = int(row["switch_score"])
    if switch == 0:
        return score == 0
    if third <= 0 or switch < third or switch > int(row["terminal_turn"]):
        return False
    trigger = metadata["trigger"]
    if trigger == "w3_now":
        return switch == third
    if trigger == "w3_plus25":
        return switch - third == 25
    if trigger == "w3_plus50":
        return switch - third == 50
    if trigger == "w3_score60":
        return score >= 60
    raise ValueError(f"unknown D51 trigger: {trigger}")


def mechanical_gates(
    *,
    repeat_exact: bool,
    anchors_exact: bool,
    openings_exact: bool,
    trigger_failures: int,
    triggered_policies: int,
    changed_cells: int,
) -> dict[str, bool]:
    return {
        "complete_byte_exact_repeat": repeat_exact,
        "all_eight_anchors_exact": anchors_exact,
        "all_switch_openings_exact": openings_exact,
        "all_recorded_switches_satisfy_trigger": trigger_failures == 0,
        "at_least_45_policies_trigger_on_16_maps": triggered_policies >= 45,
        "at_least_35_percent_switch_cells_active": changed_cells >= 3_136,
    }


def support_gates(support: dict, no_loss: bool) -> dict[str, bool]:
    confirmation = support["confirmation"]
    discovery = support["discovery"]
    return {
        "confirmation_overall_macro_at_least_56": confirmation["overall"][
            "augmented"
        ]["macro"]
        >= 56,
        "confirmation_overall_full_at_least_36": confirmation["overall"][
            "augmented"
        ]["full"]
        >= 36,
        "confirmation_overall_macro_increment_at_least_5": confirmation["overall"][
            "increment"
        ]["macro"]
        >= 5,
        "confirmation_overall_full_increment_at_least_3": confirmation["overall"][
            "increment"
        ]["full"]
        >= 3,
        "confirmation_catastrophic_macro_at_least_7": confirmation["catastrophic"][
            "augmented"
        ]["macro"]
        >= 7,
        "confirmation_catastrophic_increment_at_least_3": confirmation[
            "catastrophic"
        ]["increment"]["macro"]
        >= 3,
        "confirmation_worker_rich_macro_at_least_12": confirmation["worker_rich"][
            "augmented"
        ]["macro"]
        >= 12,
        "confirmation_worker_rich_increment_at_least_4": confirmation[
            "worker_rich"
        ]["increment"]["macro"]
        >= 4,
        "confirmation_rich_macro_at_least_4": confirmation["rich_immediate"][
            "augmented"
        ]["macro"]
        >= 4,
        "confirmation_rich_full_at_least_1": confirmation["rich_immediate"][
            "augmented"
        ]["full"]
        >= 1,
        "confirmation_rich_macro_increment_at_least_2": confirmation[
            "rich_immediate"
        ]["increment"]["macro"]
        >= 2,
        "confirmation_rich_full_increment_at_least_1": confirmation[
            "rich_immediate"
        ]["increment"]["full"]
        >= 1,
        "discovery_overall_macro_increment_at_least_5": discovery["overall"][
            "increment"
        ]["macro"]
        >= 5,
        "discovery_worker_rich_increment_at_least_3": discovery["worker_rich"][
            "increment"
        ]["macro"]
        >= 3,
        "discovery_catastrophic_increment_at_least_1": discovery["catastrophic"][
            "increment"
        ]["macro"]
        >= 1,
        "discovery_rich_macro_increment_at_least_1": discovery["rich_immediate"][
            "increment"
        ]["macro"]
        >= 1,
        "discovery_rich_full_increment_at_least_1": discovery["rich_immediate"][
            "increment"
        ]["full"]
        >= 1,
        "no_legacy_support_lost": no_loss,
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D51a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D51a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D51a result")

    observed = json.loads(OBSERVED.read_text())
    records = {int(record["game_id"]): record for record in observed.get("records") or []}
    if len(records) != 160:
        raise ValueError("D51a observed cohort is not 160 unique games")
    rows_a = read_d51(RUN_A)
    rows_b = read_d51(RUN_B)
    validate_grid(rows_a, set(records))
    validate_grid(rows_b, set(records))
    repeat_exact = RUN_A.read_bytes() == RUN_B.read_bytes()
    by_model_game = {(row["game_id"], row["model"]): row for row in rows_a}

    legacy_rows_by_file = {path: read_local_rows(path) for path in LEGACY_FILES}
    for path, expected_rows, expected_models_count in zip(
        LEGACY_FILES, LEGACY_GRID_SIZES, LEGACY_MODEL_COUNTS
    ):
        rows = legacy_rows_by_file[path]
        identities = {(row["game_id"], row["model"]) for row in rows}
        if (
            len(rows) != expected_rows
            or len(identities) != expected_rows
            or {row["game_id"] for row in rows} != set(records)
            or len({row["model"] for row in rows}) != expected_models_count
        ):
            raise ValueError(f"D51a legacy grid mismatch: {path}")
    historical = {
        (path, row["game_id"], row["model"]): row
        for path, rows in legacy_rows_by_file.items()
        for row in rows
    }

    anchor_mismatches = []
    for component, (path, old_label) in ANCHOR_HISTORY.items():
        label = f"d51_anchor_{component}"
        for game_id in records:
            row = by_model_game[(game_id, label)]
            old = historical[(path, game_id, old_label)]
            if any(
                key != "model" and row[key] != value for key, value in old.items()
            ) or any(
                int(row[field]) != 0
                for field in ("third_worker_turn", "switch_turn", "switch_score")
            ):
                anchor_mismatches.append((game_id, label))

    opening_mismatches = []
    trigger_failures = []
    changed_cells = 0
    triggers_by_policy = defaultdict(int)
    switch_turns_by_trigger: dict[str, list[int]] = defaultdict(list)
    switch_turns_by_pair: dict[str, list[int]] = defaultdict(list)
    for label, metadata in SWITCH_METADATA.items():
        anchor = f"d51_anchor_{metadata['early']}"
        pair = f"{metadata['early']}->{metadata['late']}"
        for game_id in records:
            row = by_model_game[(game_id, label)]
            early = by_model_game[(game_id, anchor)]
            if row["first_commands"] != early["first_commands"]:
                opening_mismatches.append((game_id, label))
            if not trigger_is_valid(metadata, row):
                trigger_failures.append((game_id, label))
            if int(row["switch_turn"]) > 0:
                triggers_by_policy[label] += 1
                switch_turns_by_trigger[metadata["trigger"]].append(row["switch_turn"])
                switch_turns_by_pair[pair].append(row["switch_turn"])
            if terminal_signature(row) != terminal_signature(early):
                changed_cells += 1
    triggered_policies = sum(value >= 16 for value in triggers_by_policy.values())
    mechanics = mechanical_gates(
        repeat_exact=repeat_exact,
        anchors_exact=not anchor_mismatches,
        openings_exact=not opening_mismatches,
        trigger_failures=len(trigger_failures),
        triggered_policies=triggered_policies,
        changed_cells=changed_cells,
    )

    activation = {
        "switch_cells": len(SWITCH_METADATA) * len(records),
        "triggered_cells": sum(triggers_by_policy.values()),
        "triggered_rate": sum(triggers_by_policy.values())
        / (len(SWITCH_METADATA) * len(records)),
        "triggered_policies_on_at_least_16_maps": triggered_policies,
        "changed_cells": changed_cells,
        "changed_rate": changed_cells / (len(SWITCH_METADATA) * len(records)),
        "anchor_mismatches": len(anchor_mismatches),
        "opening_mismatches": len(opening_mismatches),
        "trigger_integrity_failures": len(trigger_failures),
    }
    if not all(mechanics.values()):
        report = {
            "schema": 1,
            "scope": (
                "activation/integrity only; outcome, support, distance, cohort, opponent, "
                "and coverage fields ignored"
            ),
            "protocol": str(PROTOCOL),
            "protocol_sha256": sha256(PROTOCOL),
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
            "audit": {
                "outcome_fields_ignored": True,
                "quarantined_accidental_output": str(
                    ANALYSIS / "d51a-workforce-population-coverage-result.json"
                ),
                "quarantined_accidental_output_sha256": (
                    "e3b545deaae72df7ff89668039cb53325bafc03700845ae873655d5f81187a7d"
                ),
            },
            "activation": activation,
            "gates": mechanics,
            "pass": False,
            "decision": (
                "close D51 before support evaluation; field-supported early controllers "
                "do not reach the workforce trigger broadly enough"
            ),
        }
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return

    legacy_scored: dict[int, list[dict]] = defaultdict(list)
    for rows in legacy_rows_by_file.values():
        for row in rows:
            legacy_scored[row["game_id"]].append(
                {"model": row["model"], **score_model_game(records[row["game_id"]], row)}
            )
    switch_scored: dict[int, list[dict]] = defaultdict(list)
    for row in rows_a:
        switch_scored[row["game_id"]].append(
            {"model": row["model"], **score_model_game(records[row["game_id"]], row)}
        )

    support = {}
    nearest = {}
    split_ids = {}
    for split in ("discovery", "confirmation"):
        split_ids[split] = cohort_ids(records, split)
        support[split] = {
            cohort: coverage_counts(ids, legacy_scored, switch_scored)
            for cohort, ids in split_ids[split].items()
        }
        nearest[split] = {
            cohort: nearest_summary(ids, legacy_scored, switch_scored)
            for cohort, ids in split_ids[split].items()
        }
    no_loss = all(
        (
            not any(row[field] for row in legacy_scored[game_id])
            or any(
                row[field]
                for row in [*legacy_scored[game_id], *switch_scored[game_id]]
            )
        )
        for split in split_ids.values()
        for game_id in split["overall"]
        for field in ("macro_covers", "fully_covers")
    )
    value_gates = support_gates(support, no_loss)

    new_critical = []
    for split, cohorts in split_ids.items():
        for game_id in cohorts["overall"]:
            if any(row["macro_covers"] for row in legacy_scored[game_id]):
                continue
            coverers = sorted(
                row["model"] for row in switch_scored[game_id] if row["macro_covers"]
            )
            if coverers and (
                records[game_id]["catastrophic"]
                or records[game_id]["worker_rich"]
                or game_id in cohorts["rich_immediate"]
            ):
                new_critical.append(
                    {
                        "split": split,
                        "game_id": game_id,
                        "opponent": records[game_id]["opponent"],
                        "catastrophic": bool(records[game_id]["catastrophic"]),
                        "worker_rich": bool(records[game_id]["worker_rich"]),
                        "rich_immediate": game_id in cohorts["rich_immediate"],
                        "covering_policies": coverers,
                    }
                )

    confirmation_ids = split_ids["confirmation"]["overall"]
    support_by_trigger = {}
    for trigger in TRIGGERS:
        labels = {
            label
            for label, metadata in SWITCH_METADATA.items()
            if metadata["trigger"] == trigger
        }
        support_by_trigger[trigger] = {
            "policies": len(labels),
            "triggered_cells": sum(triggers_by_policy[label] for label in labels),
            "mean_switch_turn": statistics.mean(switch_turns_by_trigger[trigger])
            if switch_turns_by_trigger[trigger]
            else None,
            "confirmation_macro_games": sum(
                any(
                    row["model"] in labels and row["macro_covers"]
                    for row in switch_scored[game_id]
                )
                for game_id in confirmation_ids
            ),
        }
    support_by_pair = {}
    for pair in sorted(switch_turns_by_pair):
        early, late = pair.split("->")
        labels = {
            label
            for label, metadata in SWITCH_METADATA.items()
            if metadata["early"] == early and metadata["late"] == late
        }
        support_by_pair[pair] = {
            "policies": len(labels),
            "triggered_cells": sum(triggers_by_policy[label] for label in labels),
            "mean_switch_turn": statistics.mean(switch_turns_by_pair[pair]),
            "confirmation_macro_games": sum(
                any(
                    row["model"] in labels and row["macro_covers"]
                    for row in switch_scored[game_id]
                )
                for game_id in confirmation_ids
            ),
        }

    gates = {**mechanics, **value_gates}
    report = {
        "schema": 1,
        "scope": (
            "consumed-map opponent-model calibration only; neither split is fresh after D50; "
            "no candidate or platform evidence"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
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
        "support_by_trigger": support_by_trigger,
        "support_by_pair": support_by_pair,
        "new_critical_macro_support": new_critical,
        "gates": gates,
        "pass": all(gates.values()),
        "decision": (
            "freeze D51 mechanism pending a separate interaction-corpus transfer audit"
            if all(gates.values())
            else "close whole-controller switching and advance to procedural factorized job allocation"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
