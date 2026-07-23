#!/usr/bin/env python3
"""Audit robust first-turn option selection across continuation models."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import statistics


ORIGINAL_MODELS = ("gold_elite", "sched_bot", "mybot", "silver_boss")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def robust_summary(values) -> dict:
    values = list(values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "worst_decile_mean": None,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "minimum": None,
            "maximum": None,
        }
    ordered = sorted(values)
    worst_n = max(1, math.ceil(0.10 * len(ordered)))
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "worst_decile_mean": statistics.mean(ordered[:worst_n]),
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def read_grid(path: Path) -> tuple[dict, tuple[str, ...], tuple[str, ...]]:
    deltas = defaultdict(lambda: defaultdict(dict))
    active = defaultdict(dict)
    trains = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = (int(row["seed"]), int(row["seat"]))
            option = row["option"]
            model = row["model"]
            if model in deltas[key][option]:
                raise ValueError(f"duplicate grid row {key + (option, model)}")
            control = int(row["control_margin"])
            option_margin = int(row["option_margin"])
            delta = int(row["delta"])
            if option_margin - control != delta:
                raise ValueError(f"bad delta arithmetic for {key + (option, model)}")
            deltas[key][option][model] = delta
            state = bool(int(row["active"]))
            if option in active[key] and active[key][option] != state:
                raise ValueError(f"model-dependent activation for {key + (option,)}")
            active[key][option] = state
            train_key = (key, option)
            if train_key in trains and trains[train_key] != row["first_train"]:
                raise ValueError(f"model-dependent first train for {key + (option,)}")
            trains[train_key] = row["first_train"]

    cells = {}
    model_names = tuple(sorted({model for options in deltas.values() for row in options.values() for model in row}))
    option_names = tuple(sorted({option for options in deltas.values() for option in options}))
    expected = set(model_names)
    for key, options in deltas.items():
        if set(options) != set(option_names):
            raise ValueError(f"option coverage mismatch for {key}")
        for option, values in options.items():
            if set(values) != expected:
                raise ValueError(f"model coverage mismatch for {key + (option,)}")
        cells[key] = {
            option: {
                "deltas": dict(values),
                "active": active[key][option],
                "first_train": trains[(key, option)],
            }
            for option, values in options.items()
        }
    return cells, model_names, option_names


def train_cost(command: str) -> int:
    fields = command.split()
    if len(fields) != 5 or fields[0] != "TRAIN":
        return 0
    return sum(int(value) ** 2 for value in fields[1:])


def choose(
    options: dict,
    models: tuple[str, ...],
    *,
    allowed_nonpositive: int = 0,
    floor: float = 0.0,
    minimum_mean: float = 0.0,
) -> dict | None:
    candidates = []
    for name, row in options.items():
        if name == "control" or not row["active"]:
            continue
        values = [row["deltas"][model] for model in models]
        if sum(value <= 0 for value in values) > allowed_nonpositive:
            continue
        if min(values) < floor or statistics.mean(values) <= minimum_mean:
            continue
        candidates.append(
            (
                min(values),
                statistics.mean(values),
                -train_cost(row["first_train"]),
                name,
                row,
            )
        )
    if not candidates:
        return None
    worst, mean, _negative_cost, name, row = max(candidates)
    return {
        "option": name,
        "first_train": row["first_train"],
        "selection_worst_delta": worst,
        "selection_mean_delta": mean,
        "deltas": row["deltas"],
    }


def evaluate(
    cells: dict,
    models: tuple[str, ...],
    *,
    allowed_nonpositive: int = 0,
    floor: float = 0.0,
    minimum_mean: float = 0.0,
) -> dict:
    selections = {
        key: selected
        for key, options in cells.items()
        if (
            selected := choose(
                options,
                models,
                allowed_nonpositive=allowed_nonpositive,
                floor=floor,
                minimum_mean=minimum_mean,
            )
        )
        is not None
    }
    seeds = sorted({seed for seed, _seat in cells})
    by_model = {}
    for model in models:
        values = [
            statistics.mean(
                selections[(seed, seat)]["deltas"][model]
                if (seed, seat) in selections
                else 0
                for seat in (0, 1)
            )
            for seed in seeds
        ]
        by_model[model] = robust_summary(values)
    overall = [
        statistics.mean(
            selections[(seed, seat)]["deltas"][model]
            if (seed, seat) in selections
            else 0
            for seat in (0, 1)
            for model in models
        )
        for seed in seeds
    ]
    return {
        "rule": {
            "allowed_nonpositive": allowed_nonpositive,
            "floor": floor,
            "minimum_mean": minimum_mean,
            "choice": (
                "maximize worst model delta, then mean delta, then prefer lower first-train "
                "quadratic talent cost, then canonical option name"
            ),
        },
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


def leave_one_model_out(
    cells: dict,
    models: tuple[str, ...],
    *,
    allowed_nonpositive: int = 0,
    floor: float = 0.0,
    minimum_mean: float = 0.0,
) -> dict:
    seeds = sorted({seed for seed, _seat in cells})
    reports = []
    for held in models:
        visible = tuple(model for model in models if model != held)
        selections = {
            key: selected
            for key, options in cells.items()
            if (
                selected := choose(
                    options,
                    visible,
                    allowed_nonpositive=allowed_nonpositive,
                    floor=floor,
                    minimum_mean=minimum_mean,
                )
            )
            is not None
        }
        held_values = [
            statistics.mean(
                selections[(seed, seat)]["deltas"][held]
                if (seed, seat) in selections
                else 0
                for seat in (0, 1)
            )
            for seed in seeds
        ]
        reports.append(
            {
                "held_model": held,
                "visible_models": visible,
                "selected_cell_count": len(selections),
                "selected_seed_count": len({seed for seed, _seat in selections}),
                "held_model_seed_balanced": robust_summary(held_values),
            }
        )
    return {
        "held_models": reports,
        "total_selected_cells": sum(row["selected_cell_count"] for row in reports),
        "total_held_loss_seeds": sum(
            row["held_model_seed_balanced"]["losses"] for row in reports
        ),
        "worst_held_model_mean": min(
            (row["held_model_seed_balanced"]["mean"] for row in reports), default=0
        ),
        "worst_held_seed_delta": min(
            (row["held_model_seed_balanced"]["minimum"] for row in reports), default=0
        ),
    }


def selector_report(cells: dict, models: tuple[str, ...], rule: dict) -> dict:
    return {
        "models": models,
        "full_information": evaluate(cells, models, **rule),
        "leave_one_model_out": leave_one_model_out(cells, models, **rule),
    }


def study(path: Path) -> dict:
    cells, models, options = read_grid(path)
    missing_original = sorted(set(ORIGINAL_MODELS) - set(models))
    if missing_original:
        raise ValueError(f"grid lacks original continuation models {missing_original}")
    strict = {"allowed_nonpositive": 0, "floor": 0.0, "minimum_mean": 0.0}
    one_veto = {"allowed_nonpositive": 1, "floor": -10.0, "minimum_mean": 10.0}
    two_veto = {"allowed_nonpositive": 2, "floor": -30.0, "minimum_mean": 10.0}
    original = selector_report(cells, ORIGINAL_MODELS, strict)
    expanded = selector_report(cells, models, strict)
    relaxations = {
        "one_veto": selector_report(cells, models, one_veto),
        "two_veto": selector_report(cells, models, two_veto),
    }
    passes_discovery = (
        expanded["full_information"]["selected_seed_count"] >= 2
        and expanded["leave_one_model_out"]["total_selected_cells"] > 0
        and expanded["leave_one_model_out"]["worst_held_model_mean"] >= 0
        and expanded["leave_one_model_out"]["worst_held_seed_delta"] >= -10
    )
    return {
        "schema": 1,
        "scope": (
            "consumed discovery seeds; exact terminal control/option deltas for both seats; "
            "27 fixed harvest-0 first workers, dynamic max-bank anchor, exact resident "
            "abstention; not prospective or arena evidence"
        ),
        "source": str(path),
        "cells": len(cells),
        "seeds": len({seed for seed, _seat in cells}),
        "models": models,
        "options": options,
        "active_cell_counts": {
            option: sum(row[option]["active"] for row in cells.values())
            for option in options
        },
        "strict_original_four": original,
        "strict_expanded": expanded,
        "relaxation_diagnostics": relaxations,
        "discovery_gate": {
            "requirements": [
                "strict expanded rule selects at least two seeds",
                "leave-one-model-out selection is non-inert",
                "worst held-model mean is nonnegative",
                "worst held seed is at least -10",
            ],
            "passed": passes_discovery,
        },
        "interpretation_limit": (
            "All option and rule inspection occurred on consumed discovery maps.  Failure "
            "prevents opening a holdout; success would only authorize a frozen validation run."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = study(args.input)
    atomic_write(args.output, json.dumps(result, indent=1) + "\n")
    compact = {
        "original_four": {
            "selected": result["strict_original_four"]["full_information"]["selected_cell_count"],
            "worst_loo_mean": result["strict_original_four"]["leave_one_model_out"]["worst_held_model_mean"],
            "loo_loss_seeds": result["strict_original_four"]["leave_one_model_out"]["total_held_loss_seeds"],
        },
        "expanded": {
            "selected": result["strict_expanded"]["full_information"]["selected_cell_count"],
            "loo_selected": result["strict_expanded"]["leave_one_model_out"]["total_selected_cells"],
        },
        "relaxations": {
            name: {
                "selected": row["full_information"]["selected_cell_count"],
                "worst_loo_mean": row["leave_one_model_out"]["worst_held_model_mean"],
                "loo_loss_seeds": row["leave_one_model_out"]["total_held_loss_seeds"],
                "worst_held_seed": row["leave_one_model_out"]["worst_held_seed_delta"],
            }
            for name, row in result["relaxation_diagnostics"].items()
        },
        "discovery_gate": result["discovery_gate"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
