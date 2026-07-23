#!/usr/bin/env python3
"""Calibrate the frozen complete-economy catalog against consumed field trajectories."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.field_continuation_coverage import (
    ACTUAL_FIELDS,
    FEATURES,
    actual_checkpoint,
    archetype_key,
    rate,
    read_local_rows,
    score_model_game,
)


CATALOG = (
    "lean_m1c2h0k2",
    "lean_m2c2h0k2",
    "lean_m2c3h0k2",
    "lean_m2c2h0k3",
    "dual3_s20_h0_cap12",
    "dual3_s20_h0_cap20",
    "dual3_s20_h1_cap12",
    "dual3_s20_h1_cap20",
    "dual3_s60_h0_cap12",
    "dual3_s60_h0_cap20",
    "dual3_s60_h1_cap12",
    "dual3_s60_h1_cap20",
    "farm3_hold0_cap12",
    "farm3_hold0_cap20",
    "farm3_hold60_cap12",
    "farm3_hold60_cap20",
    "farm3_hold100_cap12",
    "farm3_hold100_cap20",
    "farm4_s30_hold0_cap18",
    "farm4_s30_hold0_cap24",
    "farm4_s30_hold80_cap18",
    "farm4_s30_hold80_cap24",
    "farm4_s30_hold120_cap18",
    "farm4_s30_hold120_cap24",
    "farm4_s60_hold0_cap18",
    "farm4_s60_hold0_cap24",
    "farm4_s60_hold80_cap18",
    "farm4_s60_hold80_cap24",
    "farm4_s60_hold120_cap18",
    "farm4_s60_hold120_cap24",
    "adaptive_density",
)
STRUCTURAL_CATALOG = (
    "boss4",
    "boss5",
    "boss_real",
    "norx_native_full",
    "norx_native_three",
    "norx_compact",
    "norx_silver",
    "norx_funded_silver",
    "norx_cooperative_silver",
    "norx_soft_cooperative_silver",
    "norx_three_worker_silver",
)
TARGET_ARCHETYPES = (
    "rich3plus:farm_wood:train_now",
    "compact2:farm_wood:deferred",
    "compact2:wood_only:deferred",
)


def partition(game_id: int) -> str:
    digest = hashlib.sha256(
        f"field-economy-calibration-v1:{game_id}".encode()
    ).digest()
    return "discovery" if digest[0] & 1 == 0 else "confirmation"


def cohort_flags(record: dict, baseline: dict) -> dict:
    key = archetype_key(record)
    return {
        "catastrophic": bool(record["catastrophic"]),
        "worker_rich": bool(record["worker_rich"]),
        "target_archetype": (
            key if not baseline["fully_supported"] and key in TARGET_ARCHETYPES else None
        ),
    }


def model_target_rank(
    model: str,
    game_ids: set[int],
    rows_by_model_game: dict[tuple[str, int], dict],
) -> dict:
    rows = [rows_by_model_game[(model, game_id)] for game_id in game_ids]
    return {
        "model": model,
        "games": len(rows),
        "macro_covers": sum(row["macro_covers"] for row in rows),
        "fully_covers": sum(row["fully_covers"] for row in rows),
        "macro_coverage_rate": rate(sum(row["macro_covers"] for row in rows), len(rows)),
        "full_coverage_rate": rate(sum(row["fully_covers"] for row in rows), len(rows)),
        "mean_normalized_macro_distance": statistics.mean(
            row["normalized_macro_distance"] for row in rows
        ),
    }


def rank_key(row: dict) -> tuple:
    return (
        -row["macro_covers"],
        -row["fully_covers"],
        row["mean_normalized_macro_distance"],
        row["model"],
    )


def support_summary(
    game_ids: list[int],
    baseline_by_game: dict[int, dict],
    selected_rows_by_game: dict[int, list[dict]],
) -> dict:
    baseline_macro = sum(baseline_by_game[game_id]["macro_supported"] for game_id in game_ids)
    baseline_full = sum(baseline_by_game[game_id]["fully_supported"] for game_id in game_ids)
    baseline_exact = sum(
        baseline_by_game[game_id]["exact_opening_supported"] for game_id in game_ids
    )
    catalog_macro = sum(
        any(row["macro_covers"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    catalog_full = sum(
        any(row["fully_covers"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    catalog_exact = sum(
        any(row["exact_opening"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    expanded_macro = sum(
        baseline_by_game[game_id]["macro_supported"]
        or any(row["macro_covers"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    expanded_full = sum(
        baseline_by_game[game_id]["fully_supported"]
        or any(row["fully_covers"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    expanded_exact = sum(
        baseline_by_game[game_id]["exact_opening_supported"]
        or any(row["exact_opening"] for row in selected_rows_by_game[game_id])
        for game_id in game_ids
    )
    denominator = len(game_ids)
    return {
        "games": denominator,
        "baseline": {
            "macro": baseline_macro,
            "full": baseline_full,
            "exact_opening": baseline_exact,
            "macro_rate": rate(baseline_macro, denominator),
            "full_rate": rate(baseline_full, denominator),
            "exact_opening_rate": rate(baseline_exact, denominator),
        },
        "selected_catalog": {
            "macro": catalog_macro,
            "full": catalog_full,
            "exact_opening": catalog_exact,
            "macro_rate": rate(catalog_macro, denominator),
            "full_rate": rate(catalog_full, denominator),
            "exact_opening_rate": rate(catalog_exact, denominator),
        },
        "expanded": {
            "macro": expanded_macro,
            "full": expanded_full,
            "exact_opening": expanded_exact,
            "macro_rate": rate(expanded_macro, denominator),
            "full_rate": rate(expanded_full, denominator),
            "exact_opening_rate": rate(expanded_exact, denominator),
        },
        "delta": {
            "macro": expanded_macro - baseline_macro,
            "full": expanded_full - baseline_full,
            "exact_opening": expanded_exact - baseline_exact,
            "macro_rate": rate(expanded_macro - baseline_macro, denominator),
            "full_rate": rate(expanded_full - baseline_full, denominator),
            "exact_opening_rate": rate(expanded_exact - baseline_exact, denominator),
        },
    }


def residual_summary(records: list[dict], local_rows: list[dict]) -> dict:
    if not records:
        return {"games": 0, "checkpoints": {}, "terminal": None}
    by_game = {int(record["game_id"]): record for record in records}
    local_by_game = {int(row["game_id"]): row for row in local_rows}
    checkpoints = {}
    for checkpoint in ("50", "100", "final"):
        prefix = f"t{checkpoint}" if checkpoint != "final" else "final"
        checkpoints[checkpoint] = {}
        for feature in FEATURES:
            signed = []
            for game_id, record in by_game.items():
                actual = actual_checkpoint(record, checkpoint)
                predicted = int(local_by_game[game_id][f"{prefix}_{feature}"])
                signed.append(predicted - int(actual[ACTUAL_FIELDS[feature]]))
            checkpoints[checkpoint][feature] = {
                "mean_signed": statistics.mean(signed),
                "mean_absolute": statistics.mean(abs(value) for value in signed),
            }
    terminal = [
        int(local_by_game[game_id]["terminal_turn"]) - int(record["actual"]["turns"])
        for game_id, record in by_game.items()
    ]
    return {
        "games": len(records),
        "checkpoints": checkpoints,
        "terminal": {
            "mean_signed": statistics.mean(terminal),
            "mean_absolute": statistics.mean(abs(value) for value in terminal),
        },
    }


def analyze(
    observed: dict,
    baseline: dict,
    local_rows: list[dict],
    catalog: tuple[str, ...] = CATALOG,
) -> dict:
    catalog = tuple(catalog)
    if not catalog or len(set(catalog)) != len(catalog):
        raise ValueError("model catalog must be nonempty and unique")
    records = observed.get("records") or []
    if len(records) != 160:
        raise ValueError(f"expected 160 observed games, got {len(records)}")
    by_game = {int(record["game_id"]): record for record in records}
    baseline_rows = baseline.get("game_rows") or []
    baseline_by_game = {int(row["game_id"]): row for row in baseline_rows}
    if set(by_game) != set(baseline_by_game) or len(baseline_by_game) != 160:
        raise ValueError("baseline audit does not match the exact 160-game cohort")

    identities = {(int(row["game_id"]), row["model"]) for row in local_rows}
    expected = {(game_id, model) for game_id in by_game for model in catalog}
    if (
        len(local_rows) != 160 * len(catalog)
        or len(identities) != len(local_rows)
        or identities != expected
    ):
        raise ValueError(
            f"catalog audit does not contain the exact unique 160 x {len(catalog)} grid"
        )

    flags_by_game = {
        game_id: cohort_flags(record, baseline_by_game[game_id])
        for game_id, record in by_game.items()
    }
    scored_rows = []
    rows_by_model_game = {}
    for local in local_rows:
        game_id = int(local["game_id"])
        scored = {
            "game_id": game_id,
            "model": local["model"],
            "partition": partition(game_id),
            **flags_by_game[game_id],
            **score_model_game(by_game[game_id], local),
        }
        if scored["missing_checkpoint"]:
            raise ValueError(f"catalog trajectory misses a checkpoint: {game_id}")
        scored_rows.append(scored)
        rows_by_model_game[(scored["model"], game_id)] = scored

    split_ids = {
        name: sorted(game_id for game_id in by_game if partition(game_id) == name)
        for name in ("discovery", "confirmation")
    }
    split_counts = {}
    for name, game_ids in split_ids.items():
        split_counts[name] = {
            "games": len(game_ids),
            "catastrophic": sum(flags_by_game[game_id]["catastrophic"] for game_id in game_ids),
            "worker_rich": sum(flags_by_game[game_id]["worker_rich"] for game_id in game_ids),
            "target_archetypes": {
                archetype: sum(
                    flags_by_game[game_id]["target_archetype"] == archetype
                    for game_id in game_ids
                )
                for archetype in TARGET_ARCHETYPES
            },
        }

    selections = {}
    rankings = {}
    discovery_ids = set(split_ids["discovery"])
    for archetype in TARGET_ARCHETYPES:
        target_ids = {
            game_id
            for game_id in discovery_ids
            if flags_by_game[game_id]["target_archetype"] == archetype
        }
        if not target_ids:
            raise ValueError(f"no discovery games for target archetype {archetype}")
        ranked = sorted(
            (model_target_rank(model, target_ids, rows_by_model_game) for model in catalog),
            key=rank_key,
        )
        rankings[archetype] = ranked
        selections[archetype] = ranked[0]
    selected_models = sorted({selection["model"] for selection in selections.values()})

    selected_rows_by_game: dict[int, list[dict]] = defaultdict(list)
    for model in selected_models:
        for game_id in by_game:
            selected_rows_by_game[game_id].append(rows_by_model_game[(model, game_id)])

    confirmation_ids = split_ids["confirmation"]
    cohorts = {
        "overall": confirmation_ids,
        "catastrophic": [
            game_id for game_id in confirmation_ids if flags_by_game[game_id]["catastrophic"]
        ],
        "worker_rich": [
            game_id for game_id in confirmation_ids if flags_by_game[game_id]["worker_rich"]
        ],
    }
    confirmation = {
        name: support_summary(game_ids, baseline_by_game, selected_rows_by_game)
        for name, game_ids in cohorts.items()
    }

    target_confirmation = {}
    archetype_checks = {}
    for archetype in TARGET_ARCHETYPES:
        game_ids = [
            game_id
            for game_id in confirmation_ids
            if flags_by_game[game_id]["target_archetype"] == archetype
        ]
        representative = selections[archetype]["model"]
        representative_rows = [
            rows_by_model_game[(representative, game_id)] for game_id in game_ids
        ]
        summary = support_summary(game_ids, baseline_by_game, selected_rows_by_game)
        representative_macro = sum(row["macro_covers"] for row in representative_rows)
        summary["representative"] = representative
        summary["representative_macro"] = representative_macro
        summary["representative_macro_rate"] = rate(representative_macro, len(game_ids))
        representative_local = [
            local
            for local in local_rows
            if local["model"] == representative and int(local["game_id"]) in game_ids
        ]
        summary["representative_residuals"] = residual_summary(
            [by_game[game_id] for game_id in game_ids], representative_local
        )
        target_confirmation[archetype] = summary
        archetype_checks[archetype] = (
            True
            if len(game_ids) < 4
            else summary["representative_macro_rate"] is not None
            and summary["representative_macro_rate"] >= 0.20
        )

    overall = confirmation["overall"]
    catastrophic = confirmation["catastrophic"]
    worker_rich = confirmation["worker_rich"]
    gates = {
        "integrity": len(scored_rows) == 160 * len(catalog),
        "overall_macro_uplift": overall["delta"]["macro_rate"] is not None
        and overall["delta"]["macro_rate"] >= 0.10,
        "overall_full_uplift": overall["delta"]["full_rate"] is not None
        and overall["delta"]["full_rate"] >= 0.05,
        "catastrophic_macro_uplift": catastrophic["games"] > 0
        and catastrophic["delta"]["macro_rate"] is not None
        and catastrophic["delta"]["macro_rate"] >= 0.15,
        "worker_rich_macro_uplift": worker_rich["games"] > 0
        and worker_rich["delta"]["macro_rate"] is not None
        and worker_rich["delta"]["macro_rate"] >= 0.15,
        "target_archetype_confirmation": all(archetype_checks.values()),
    }
    macro_gate_names = (
        "integrity",
        "overall_macro_uplift",
        "catastrophic_macro_uplift",
        "worker_rich_macro_uplift",
        "target_archetype_confirmation",
    )
    macro_viable = all(gates[name] for name in macro_gate_names)
    catalog_useful = all(gates.values())

    model_summary = {}
    for model in catalog:
        rows = [
            rows_by_model_game[(model, game_id)] for game_id in confirmation_ids
        ]
        model_summary[model] = {
            "confirmation_games": len(rows),
            "macro_covers": sum(row["macro_covers"] for row in rows),
            "fully_covers": sum(row["fully_covers"] for row in rows),
            "exact_opening": sum(row["exact_opening"] for row in rows),
            "mean_normalized_macro_distance": statistics.mean(
                row["normalized_macro_distance"] for row in rows
            ),
        }

    if catalog_useful:
        decision = "frozen catalog supplies useful field-proxy representatives"
    elif macro_viable:
        decision = "macro representation is useful but opening/full support requires a frozen graft"
    elif catalog == CATALOG:
        decision = "close parameter-only GoldElite calibration; build a structurally new field proxy"
    else:
        decision = "close reuse of existing structural controllers; build a purpose-specific Legend proxy"
    return {
        "schema": 1,
        "scope": "consumed exact-map opponent-model calibration; not candidate evidence",
        "games": len(by_game),
        "model_cells": len(scored_rows),
        "catalog": catalog,
        "target_archetypes": TARGET_ARCHETYPES,
        "split_counts": split_counts,
        "selections": selections,
        "selected_models": selected_models,
        "discovery_rankings": rankings,
        "confirmation": confirmation,
        "target_confirmation": target_confirmation,
        "archetype_checks": archetype_checks,
        "gates": gates,
        "macro_viable": macro_viable,
        "catalog_useful": catalog_useful,
        "model_summary": model_summary,
        "decision": decision,
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--catalog",
        choices=("economy", "structural"),
        default="economy",
    )
    args = parser.parse_args()
    catalog = CATALOG if args.catalog == "economy" else STRUCTURAL_CATALOG
    payload = analyze(
        json.loads(args.observed.read_text()),
        json.loads(args.baseline.read_text()),
        read_local_rows(args.local),
        catalog,
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "model_cells": payload["model_cells"],
        "split_counts": payload["split_counts"],
        "selections": payload["selections"],
        "selected_models": payload["selected_models"],
        "confirmation": payload["confirmation"],
        "target_confirmation": payload["target_confirmation"],
        "gates": payload["gates"],
        "macro_viable": payload["macro_viable"],
        "catalog_useful": payload["catalog_useful"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
