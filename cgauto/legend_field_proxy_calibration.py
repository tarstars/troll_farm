#!/usr/bin/env python3
"""Select and confirm the frozen LegendFieldProxy v1 rich-opponent grammar."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.field_continuation_coverage import read_local_rows, score_model_game
from cgauto.field_economy_catalog_calibration import (
    TARGET_ARCHETYPES,
    cohort_flags,
    model_target_rank,
    partition,
    rank_key,
    residual_summary,
    support_summary,
)


CATALOG = (
    "legend_hp2_f1_fell1",
    "legend_hp2_f1_fell100",
    "legend_hp2_f2_fell1",
    "legend_hp2_f2_fell100",
    "legend_balanced_f1_fell1",
    "legend_balanced_f1_fell100",
    "legend_balanced_f2_fell1",
    "legend_balanced_f2_fell100",
)
V2_CATALOG = (
    "legend_v2_hp2_cheap_farm",
    "legend_v2_hp2_cheap_late_chop",
    "legend_v2_hp2_strong_farm",
    "legend_v2_hp2_strong_late_chop",
    "legend_v2_balanced_cheap_farm",
    "legend_v2_balanced_cheap_late_chop",
    "legend_v2_balanced_strong_farm",
    "legend_v2_balanced_strong_late_chop",
)
RICH_ARCHETYPE = TARGET_ARCHETYPES[0]


def analyze(
    observed: dict,
    baseline: dict,
    local_rows: list[dict],
    catalog: tuple[str, ...] = CATALOG,
    version: str = "v1",
) -> dict:
    catalog = tuple(catalog)
    if len(catalog) != 8 or len(set(catalog)) != 8:
        raise ValueError("proxy catalog must contain exactly eight unique models")
    records = observed.get("records") or []
    if len(records) != 160:
        raise ValueError(f"expected 160 observed games, got {len(records)}")
    by_game = {int(record["game_id"]): record for record in records}
    baseline_by_game = {
        int(row["game_id"]): row for row in baseline.get("game_rows") or []
    }
    if len(by_game) != 160 or set(by_game) != set(baseline_by_game):
        raise ValueError("baseline/observed cohort mismatch")
    identities = {(int(row["game_id"]), row["model"]) for row in local_rows}
    expected = {(game_id, model) for game_id in by_game for model in catalog}
    if len(local_rows) != 1280 or len(identities) != len(local_rows) or identities != expected:
        raise ValueError("proxy audit does not contain the exact unique 160 x 8 grid")

    flags_by_game = {
        game_id: cohort_flags(record, baseline_by_game[game_id])
        for game_id, record in by_game.items()
    }
    rows_by_model_game = {}
    local_by_model_game = {}
    for local in local_rows:
        game_id = int(local["game_id"])
        scored = {
            "game_id": game_id,
            "model": local["model"],
            **flags_by_game[game_id],
            **score_model_game(by_game[game_id], local),
        }
        if scored["missing_checkpoint"]:
            raise ValueError(f"proxy trajectory misses a checkpoint: {game_id}")
        rows_by_model_game[(local["model"], game_id)] = scored
        local_by_model_game[(local["model"], game_id)] = local

    split_ids = {
        name: sorted(game_id for game_id in by_game if partition(game_id) == name)
        for name in ("discovery", "confirmation")
    }
    split_counts = {
        name: {
            "games": len(game_ids),
            "catastrophic": sum(flags_by_game[game_id]["catastrophic"] for game_id in game_ids),
            "worker_rich": sum(flags_by_game[game_id]["worker_rich"] for game_id in game_ids),
            "rich_immediate": sum(
                flags_by_game[game_id]["target_archetype"] == RICH_ARCHETYPE
                for game_id in game_ids
            ),
        }
        for name, game_ids in split_ids.items()
    }

    discovery_rich = {
        game_id
        for game_id in split_ids["discovery"]
        if flags_by_game[game_id]["target_archetype"] == RICH_ARCHETYPE
    }
    if not discovery_rich:
        raise ValueError("no rich-immediate discovery games")
    discovery_rankings = sorted(
        (
            model_target_rank(model, discovery_rich, rows_by_model_game)
            for model in catalog
        ),
        key=rank_key,
    )
    selected = discovery_rankings[0]["model"]
    selected_rows_by_game = defaultdict(list)
    for game_id in by_game:
        selected_rows_by_game[game_id].append(rows_by_model_game[(selected, game_id)])

    confirmation_ids = split_ids["confirmation"]
    cohort_ids = {
        "overall": confirmation_ids,
        "catastrophic": [
            game_id for game_id in confirmation_ids if flags_by_game[game_id]["catastrophic"]
        ],
        "worker_rich": [
            game_id for game_id in confirmation_ids if flags_by_game[game_id]["worker_rich"]
        ],
        "rich_immediate": [
            game_id
            for game_id in confirmation_ids
            if flags_by_game[game_id]["target_archetype"] == RICH_ARCHETYPE
        ],
    }
    confirmation = {
        name: support_summary(game_ids, baseline_by_game, selected_rows_by_game)
        for name, game_ids in cohort_ids.items()
    }
    rich_ids = cohort_ids["rich_immediate"]
    rich_rows = [rows_by_model_game[(selected, game_id)] for game_id in rich_ids]
    rich_local = [local_by_model_game[(selected, game_id)] for game_id in rich_ids]
    rich_macro = sum(row["macro_covers"] for row in rich_rows)
    rich_full = sum(row["fully_covers"] for row in rich_rows)
    confirmation["rich_immediate"]["selected_macro"] = rich_macro
    confirmation["rich_immediate"]["selected_macro_rate"] = (
        rich_macro / len(rich_ids) if rich_ids else None
    )
    confirmation["rich_immediate"]["selected_full"] = rich_full
    confirmation["rich_immediate"]["selected_final_worker_distribution"] = dict(
        sorted(
            Counter(
                int(local_by_model_game[(selected, game_id)]["final_workers"])
                for game_id in rich_ids
            ).items()
        )
    )
    confirmation["rich_immediate"]["selected_residuals"] = residual_summary(
        [by_game[game_id] for game_id in rich_ids], rich_local
    )

    # The protocol's secondary stop rule allows a failed universal proxy to be
    # retained only when one catalog member covers a coherent named family.
    # Keep the all-rich, split-specific evidence in the durable result instead
    # of requiring an ad-hoc post-hoc query.
    all_rich_ids = {
        game_id
        for game_id in by_game
        if flags_by_game[game_id]["target_archetype"] == RICH_ARCHETYPE
    }
    rich_catalog_summary = {
        model: {
            split: model_target_rank(
                model,
                {
                    game_id
                    for game_id in all_rich_ids
                    if partition(game_id) == split
                },
                rows_by_model_game,
            )
            for split in ("discovery", "confirmation")
        }
        for model in catalog
    }
    rich_game_nearest = []
    for game_id in sorted(all_rich_ids):
        nearest = min(
            (rows_by_model_game[(model, game_id)] for model in catalog),
            key=lambda row: (row["normalized_macro_distance"], row["model"]),
        )
        rich_game_nearest.append(
            {
                "game_id": game_id,
                "partition": partition(game_id),
                "opponent": by_game[game_id]["opponent"],
                "model": nearest["model"],
                "macro_covers": nearest["macro_covers"],
                "fully_covers": nearest["fully_covers"],
                "normalized_macro_distance": nearest["normalized_macro_distance"],
            }
        )

    overall = confirmation["overall"]
    catastrophic = confirmation["catastrophic"]
    worker_rich = confirmation["worker_rich"]
    gates = {
        "integrity": len(rows_by_model_game) == 1280,
        "rich_macro_coverage": bool(rich_ids) and rich_macro / len(rich_ids) >= 0.20,
        "rich_full_coverage": rich_full >= 1,
        "overall_macro_uplift": overall["delta"]["macro_rate"] is not None
        and overall["delta"]["macro_rate"] >= 0.05,
        "worker_rich_macro_uplift": worker_rich["games"] > 0
        and worker_rich["delta"]["macro_rate"] is not None
        and worker_rich["delta"]["macro_rate"] >= 0.10,
        "catastrophic_macro_uplift": catastrophic["games"] > 0
        and catastrophic["delta"]["macro_rate"] is not None
        and catastrophic["delta"]["macro_rate"] >= 0.10,
    }
    passed = all(gates.values())

    model_summary = {}
    for model in catalog:
        rows = [rows_by_model_game[(model, game_id)] for game_id in confirmation_ids]
        model_summary[model] = {
            "macro_covers": sum(row["macro_covers"] for row in rows),
            "fully_covers": sum(row["fully_covers"] for row in rows),
            "exact_opening": sum(row["exact_opening"] for row in rows),
            "mean_normalized_macro_distance": statistics.mean(
                row["normalized_macro_distance"] for row in rows
            ),
        }
    return {
        "schema": 1,
        "scope": "consumed exact-map rich-opponent proxy calibration; not candidate evidence",
        "games": len(by_game),
        "model_cells": len(rows_by_model_game),
        "catalog": catalog,
        "split_counts": split_counts,
        "discovery_rankings": discovery_rankings,
        "selected_model": selected,
        "confirmation": confirmation,
        "rich_catalog_summary": rich_catalog_summary,
        "rich_game_nearest": rich_game_nearest,
        "model_summary": model_summary,
        "gates": gates,
        "passed": passed,
        "decision": (
            f"LegendFieldProxy {version} passes held-out representation gates"
            if passed
            else f"LegendFieldProxy {version} fails; use residuals for the next model hypothesis"
        ),
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
    parser.add_argument("--catalog", choices=("v1", "v2"), default="v1")
    args = parser.parse_args()
    catalog = CATALOG if args.catalog == "v1" else V2_CATALOG
    payload = analyze(
        json.loads(args.observed.read_text()),
        json.loads(args.baseline.read_text()),
        read_local_rows(args.local),
        catalog,
        args.catalog,
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "model_cells": payload["model_cells"],
        "split_counts": payload["split_counts"],
        "discovery_rankings": payload["discovery_rankings"],
        "selected_model": payload["selected_model"],
        "confirmation": payload["confirmation"],
        "gates": payload["gates"],
        "passed": payload["passed"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
