#!/usr/bin/env python3
"""Evaluate first-turn options across independent continuation realizations."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics

try:
    from cgauto.robust_first_option_study import robust_summary, train_cost
    from cgauto.robust_option_repeat_audit import read_rows
except ModuleNotFoundError:  # Support direct execution from the cgauto directory.
    from robust_first_option_study import robust_summary, train_cost
    from robust_option_repeat_audit import read_rows


# One-sided 90% Student-t critical values, indexed by degrees of freedom.
T90 = {
    1: 3.077684,
    2: 1.885618,
    3: 1.637744,
    4: 1.533206,
    5: 1.475884,
    6: 1.439756,
    7: 1.414924,
    8: 1.396815,
    9: 1.383029,
    10: 1.372184,
    11: 1.363430,
    12: 1.356217,
    13: 1.350171,
    14: 1.345030,
    15: 1.340606,
    16: 1.336757,
    17: 1.333379,
    18: 1.330391,
    19: 1.327728,
    20: 1.325341,
    21: 1.323188,
    22: 1.321237,
    23: 1.319460,
    24: 1.317836,
    25: 1.316345,
    26: 1.314972,
    27: 1.313703,
    28: 1.312527,
    29: 1.311434,
    30: 1.310415,
}


RULES = (
    "empirical_minimax",
    "model_mean_minimax",
    "model_lcb90_minimax",
    "pooled_lcb90_floor30_diagnostic",
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def lower_confidence_bound(values: list[int], confidence: float = 0.90) -> float:
    if confidence != 0.90:
        raise ValueError("only the predeclared one-sided 90% bound is supported")
    if not values:
        raise ValueError("confidence bound requires samples")
    mean = statistics.mean(values)
    if len(values) == 1 or all(value == values[0] for value in values):
        return float(mean)
    degrees = len(values) - 1
    # The df=30 value is slightly more conservative than the asymptotic normal
    # value, which is appropriate for this discovery diagnostic.
    critical = T90.get(degrees, T90[30])
    return mean - critical * statistics.stdev(values) / math.sqrt(len(values))


def sample_summary(values: list[int]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "lcb90": lower_confidence_bound(values),
        "minimum": min(values),
        "maximum": max(values),
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
    }


def load_replicates(paths: list[Path]) -> tuple[list[dict], tuple[str, ...], tuple[str, ...]]:
    if len(paths) < 2:
        raise ValueError("at least two independent grids are required")
    raw = [read_rows(path) for path in paths]
    common = set.intersection(*(set(rows) for rows in raw))
    if not common:
        raise ValueError("grids have no common rows")
    scoped = [{key: rows[key] for key in common} for rows in raw]
    if any(set(rows) != common for rows in scoped):
        raise ValueError("internal overlap error")

    models = tuple(sorted({key[2] for key in common}))
    options = tuple(sorted({key[3] for key in common}))
    cells = {(key[0], key[1]) for key in common}
    expected = len(cells) * len(models) * len(options)
    if len(common) != expected:
        raise ValueError("intersection is not a complete cell/model/option grid")

    for key in sorted(common):
        action = (scoped[0][key]["active"], scoped[0][key]["first_train"])
        if any((rows[key]["active"], rows[key]["first_train"]) != action for rows in scoped[1:]):
            raise ValueError(f"opening action changed across replicates for {key}")
    return scoped, models, options


def build_cells(
    replicates: list[dict],
    models: tuple[str, ...],
    options: tuple[str, ...],
    indices: tuple[int, ...],
) -> dict:
    cell_keys = sorted({(key[0], key[1]) for key in replicates[0]})
    cells = {}
    for seed, seat in cell_keys:
        option_rows = {}
        for option in options:
            first = replicates[0][(seed, seat, models[0], option)]
            option_rows[option] = {
                "active": first["active"],
                "first_train": first["first_train"],
                "samples": {
                    model: [
                        replicates[index][(seed, seat, model, option)]["delta"]
                        for index in indices
                    ]
                    for model in models
                },
            }
        cells[(seed, seat)] = option_rows
    return cells


def option_evidence(row: dict, models: tuple[str, ...]) -> dict:
    by_model = {model: sample_summary(row["samples"][model]) for model in models}
    pooled = [value for model in models for value in row["samples"][model]]
    return {
        "by_model": by_model,
        "pooled": sample_summary(pooled),
        "worst_sample": min(pooled),
        "worst_model_mean": min(summary["mean"] for summary in by_model.values()),
        "worst_model_lcb90": min(summary["lcb90"] for summary in by_model.values()),
    }


def choose(options: dict, models: tuple[str, ...], rule: str) -> dict | None:
    if rule not in RULES:
        raise ValueError(f"unknown selector rule {rule}")
    candidates = []
    for name, row in options.items():
        if name == "control" or not row["active"]:
            continue
        evidence = option_evidence(row, models)
        if rule == "empirical_minimax":
            score = evidence["worst_sample"]
            qualifies = score > 0
        elif rule == "model_mean_minimax":
            score = evidence["worst_model_mean"]
            qualifies = score > 0
        elif rule == "model_lcb90_minimax":
            score = evidence["worst_model_lcb90"]
            qualifies = score > 0
        else:
            score = evidence["pooled"]["lcb90"]
            qualifies = score > 0 and evidence["worst_sample"] >= -30
        if qualifies:
            candidates.append(
                (
                    score,
                    evidence["pooled"]["mean"],
                    -train_cost(row["first_train"]),
                    name,
                    row,
                    evidence,
                )
            )
    if not candidates:
        return None
    score, pooled_mean, _negative_cost, name, row, evidence = max(candidates)
    return {
        "option": name,
        "first_train": row["first_train"],
        "selection_score": score,
        "pooled_mean": pooled_mean,
        "evidence": evidence,
    }


def select_cells(cells: dict, models: tuple[str, ...], rule: str) -> dict:
    return {
        key: selected
        for key, options in cells.items()
        if (selected := choose(options, models, rule)) is not None
    }


def evaluate_selected(
    selections: dict,
    cells: dict,
    models: tuple[str, ...],
) -> dict:
    seeds = sorted({seed for seed, _seat in cells})
    by_model = {}
    for model in models:
        values = [
            statistics.mean(
                statistics.mean(cells[(seed, seat)][selections[(seed, seat)]["option"]]["samples"][model])
                if (seed, seat) in selections
                else 0
                for seat in (0, 1)
            )
            for seed in seeds
        ]
        by_model[model] = robust_summary(values)
    overall = [
        statistics.mean(
            statistics.mean(cells[(seed, seat)][selections[(seed, seat)]["option"]]["samples"][model])
            if (seed, seat) in selections
            else 0
            for seat in (0, 1)
            for model in models
        )
        for seed in seeds
    ]
    return {
        "selected_cell_count": len(selections),
        "selected_seed_count": len({seed for seed, _seat in selections}),
        "option_counts": dict(sorted(Counter(row["option"] for row in selections.values()).items())),
        "overall_seed_balanced": robust_summary(overall),
        "by_model": by_model,
        "worst_model_mean": min((row["mean"] for row in by_model.values()), default=0),
        "selected_cells": [
            {"seed": seed, "seat": seat, **selections[(seed, seat)]}
            for seed, seat in sorted(selections)
        ],
    }


def cross_repetition(
    replicates: list[dict],
    models: tuple[str, ...],
    options: tuple[str, ...],
    rule: str,
) -> dict:
    fold_rows = []
    held_values_by_model = defaultdict(list)
    held_values_overall = []
    for held in range(len(replicates)):
        train_indices = tuple(index for index in range(len(replicates)) if index != held)
        train_cells = build_cells(replicates, models, options, train_indices)
        held_cells = build_cells(replicates, models, options, (held,))
        selections = select_cells(train_cells, models, rule)
        seeds = sorted({seed for seed, _seat in train_cells})
        fold_overall = []
        for seed in seeds:
            model_values = []
            for model in models:
                value = statistics.mean(
                    held_cells[(seed, seat)][selections[(seed, seat)]["option"]]["samples"][model][0]
                    if (seed, seat) in selections
                    else 0
                    for seat in (0, 1)
                )
                held_values_by_model[model].append(value)
                model_values.append(value)
            fold_overall.append(statistics.mean(model_values))
        held_values_overall.extend(fold_overall)
        fold_rows.append(
            {
                "held_replicate": held,
                "selected_cell_count": len(selections),
                "selected_seed_count": len({seed for seed, _seat in selections}),
                "held_overall_seed_balanced": robust_summary(fold_overall),
            }
        )
    by_model = {
        model: robust_summary(values)
        for model, values in sorted(held_values_by_model.items())
    }
    return {
        "folds": fold_rows,
        "total_selected_cells": sum(row["selected_cell_count"] for row in fold_rows),
        "overall_held_seed_balanced": robust_summary(held_values_overall),
        "by_model": by_model,
        "worst_held_model_mean": min((row["mean"] for row in by_model.values()), default=0),
        "worst_held_seed_delta": min(
            (row["minimum"] for row in by_model.values() if row["minimum"] is not None),
            default=0,
        ),
        "total_held_loss_seeds": sum(row["losses"] for row in by_model.values()),
    }


def rule_report(
    replicates: list[dict],
    models: tuple[str, ...],
    options: tuple[str, ...],
    rule: str,
) -> dict:
    cells = build_cells(replicates, models, options, tuple(range(len(replicates))))
    selections = select_cells(cells, models, rule)
    return {
        "definition": {
            "empirical_minimax": "every observed model/replicate delta is positive",
            "model_mean_minimax": "every continuation model has positive replicate mean",
            "model_lcb90_minimax": "every continuation model has positive one-sided 90% LCB",
            "pooled_lcb90_floor30_diagnostic": (
                "pooled model/replicate 90% LCB is positive and no observation is below -30; "
                "diagnostic only because model pooling can hide opponent-specific losses"
            ),
        }[rule],
        "full_information": evaluate_selected(selections, cells, models),
        "leave_one_repetition_out": cross_repetition(replicates, models, options, rule),
    }


def study(paths: list[Path]) -> dict:
    replicates, models, options = load_replicates(paths)
    reports = {
        rule: rule_report(replicates, models, options, rule)
        for rule in RULES
    }
    robust = reports["model_lcb90_minimax"]
    passes = (
        robust["full_information"]["selected_seed_count"] >= 2
        and robust["leave_one_repetition_out"]["total_selected_cells"] > 0
        and robust["leave_one_repetition_out"]["worst_held_model_mean"] >= 0
        and robust["leave_one_repetition_out"]["worst_held_seed_delta"] >= -10
    )
    cells = len({(key[0], key[1]) for key in replicates[0]})
    return {
        "schema": 1,
        "scope": (
            "consumed discovery maps only; independent process-level realizations of the same "
            "complete first-turn option grid; exact resident abstention; not prospective or "
            "arena evidence"
        ),
        "sources": [str(path) for path in paths],
        "replicates": len(replicates),
        "cells": cells,
        "seeds": len({key[0] for key in replicates[0]}),
        "models": models,
        "options": options,
        "rules": reports,
        "discovery_gate": {
            "primary_rule": "model_lcb90_minimax",
            "requirements": [
                "primary rule selects at least two discovery seeds",
                "leave-one-repetition-out selection is non-inert",
                "worst held-model mean is nonnegative",
                "worst held seed is at least -10",
            ],
            "passed": passes,
        },
        "interpretation_limit": (
            "The repetitions estimate process-sensitive continuation noise but do not create "
            "new map evidence. Failure keeps the untouched holdout sealed. A pooled-model signal "
            "cannot override a failed opponent-robust rule."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = study(args.input)
    atomic_write(args.output, json.dumps(result, indent=1) + "\n")
    compact = {
        "replicates": result["replicates"],
        "cells": result["cells"],
        "rules": {
            name: {
                "selected": row["full_information"]["selected_cell_count"],
                "cross_repeat_selected": row["leave_one_repetition_out"]["total_selected_cells"],
                "worst_held_model_mean": row["leave_one_repetition_out"]["worst_held_model_mean"],
                "held_loss_seeds": row["leave_one_repetition_out"]["total_held_loss_seeds"],
            }
            for name, row in result["rules"].items()
        },
        "discovery_gate": result["discovery_gate"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
