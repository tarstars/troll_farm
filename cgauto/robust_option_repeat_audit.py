#!/usr/bin/env python3
"""Compare repeated robust-option grids and expose continuation instability."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics

try:
    from cgauto.robust_first_option_study import ORIGINAL_MODELS, choose
except ModuleNotFoundError:  # Support direct execution from the cgauto directory.
    from robust_first_option_study import ORIGINAL_MODELS, choose


RowKey = tuple[int, int, str, str]
VALUE_FIELDS = ("control_margin", "option_margin", "delta")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def read_rows(path: Path) -> dict[RowKey, dict]:
    rows = {}
    with path.open(newline="") as stream:
        for source in csv.DictReader(stream, delimiter="\t"):
            key = (
                int(source["seed"]),
                int(source["seat"]),
                source["model"],
                source["option"],
            )
            if key in rows:
                raise ValueError(f"duplicate grid row {key}")
            row = {
                "active": bool(int(source["active"])),
                "first_train": source["first_train"],
                "control_margin": int(source["control_margin"]),
                "option_margin": int(source["option_margin"]),
                "delta": int(source["delta"]),
            }
            if row["option_margin"] - row["control_margin"] != row["delta"]:
                raise ValueError(f"bad delta arithmetic for {key}")
            rows[key] = row
    if not rows:
        raise ValueError(f"empty grid {path}")
    return rows


def mean_abs(values: list[int]) -> float:
    return statistics.mean(abs(value) for value in values) if values else 0.0


def comparison_summary(pairs: list[tuple[dict, dict]]) -> dict:
    field_differences = {
        field: [repeat[field] - reference[field] for reference, repeat in pairs]
        for field in VALUE_FIELDS
    }
    exact_terminal = [
        all(reference[field] == repeat[field] for field in VALUE_FIELDS)
        for reference, repeat in pairs
    ]
    action_exact = [
        reference["active"] == repeat["active"]
        and reference["first_train"] == repeat["first_train"]
        for reference, repeat in pairs
    ]
    delta_classes = [
        (
            (reference["delta"] > 0) - (reference["delta"] < 0),
            (repeat["delta"] > 0) - (repeat["delta"] < 0),
        )
        for reference, repeat in pairs
    ]
    rows = len(pairs)
    terminal_exact_count = sum(exact_terminal)
    action_exact_count = sum(action_exact)
    return {
        "rows": rows,
        "action_exact_count": action_exact_count,
        "action_exact_rate": action_exact_count / rows if rows else None,
        "terminal_exact_count": terminal_exact_count,
        "terminal_exact_rate": terminal_exact_count / rows if rows else None,
        "terminal_changed_count": rows - terminal_exact_count,
        "by_field": {
            field: {
                "exact_count": sum(difference == 0 for difference in differences),
                "changed_count": sum(difference != 0 for difference in differences),
                "mean_abs_difference": mean_abs(differences),
                "max_abs_difference": max((abs(value) for value in differences), default=0),
            }
            for field, differences in field_differences.items()
        },
        "delta_class_changed_count": sum(before != after for before, after in delta_classes),
        "delta_strict_sign_flip_count": sum(before * after < 0 for before, after in delta_classes),
        "delta_positive_to_nonpositive_count": sum(
            before > 0 and after <= 0 for before, after in delta_classes
        ),
        "delta_nonpositive_to_positive_count": sum(
            before <= 0 and after > 0 for before, after in delta_classes
        ),
    }


def cells_from_rows(rows: dict[RowKey, dict]) -> tuple[dict, tuple[str, ...]]:
    cells = defaultdict(dict)
    models = sorted({model for _seed, _seat, model, _option in rows})
    for (seed, seat, model, option), row in rows.items():
        option_row = cells[(seed, seat)].setdefault(
            option,
            {
                "deltas": {},
                "active": row["active"],
                "first_train": row["first_train"],
            },
        )
        if option_row["active"] != row["active"]:
            raise ValueError(f"model-dependent activation for {(seed, seat, option)}")
        if option_row["first_train"] != row["first_train"]:
            raise ValueError(f"model-dependent first train for {(seed, seat, option)}")
        option_row["deltas"][model] = row["delta"]
    expected_models = set(models)
    options = None
    for key, option_rows in cells.items():
        names = set(option_rows)
        if options is None:
            options = names
        elif names != options:
            raise ValueError(f"option coverage mismatch for {key}")
        for option, row in option_rows.items():
            if set(row["deltas"]) != expected_models:
                raise ValueError(f"model coverage mismatch for {key + (option,)}")
    return dict(cells), tuple(models)


def selections(cells: dict, models: tuple[str, ...], rule: dict) -> dict:
    return {
        key: choose(options, models, **rule)
        for key, options in cells.items()
    }


def selector_comparison(
    reference_cells: dict,
    repeat_cells: dict,
    models: tuple[str, ...],
    rule: dict,
) -> dict:
    reference = selections(reference_cells, models, rule)
    repeat = selections(repeat_cells, models, rule)
    if set(reference) != set(repeat):
        raise ValueError("selector cell scopes differ")
    decisions = []
    for seed, seat in sorted(reference):
        before = reference[(seed, seat)]
        after = repeat[(seed, seat)]
        before_option = before["option"] if before else None
        after_option = after["option"] if after else None
        if before_option != after_option:
            decisions.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "reference": before_option,
                    "repeat": after_option,
                }
            )
    reference_selected = {key for key, row in reference.items() if row is not None}
    repeat_selected = {key for key, row in repeat.items() if row is not None}
    union = reference_selected | repeat_selected
    return {
        "models": models,
        "rule": rule,
        "cells": len(reference),
        "reference_selected_cells": len(reference_selected),
        "repeat_selected_cells": len(repeat_selected),
        "shared_selected_cells": len(reference_selected & repeat_selected),
        "selected_cell_jaccard": len(reference_selected & repeat_selected) / len(union) if union else 1.0,
        "decision_changed_count": len(decisions),
        "decision_exact_rate": 1 - len(decisions) / len(reference) if reference else None,
        "changed_decisions": decisions,
    }


def audit(reference_path: Path, repeat_path: Path) -> dict:
    reference_all = read_rows(reference_path)
    repeat = read_rows(repeat_path)
    unexpected = sorted(set(repeat) - set(reference_all))
    if unexpected:
        raise ValueError(f"repeat has {len(unexpected)} rows absent from reference")
    reference = {key: reference_all[key] for key in repeat}

    pairs_by_model = defaultdict(list)
    pairs_by_option = defaultdict(list)
    all_pairs = []
    for key in sorted(repeat):
        pair = (reference[key], repeat[key])
        all_pairs.append(pair)
        pairs_by_model[key[2]].append(pair)
        pairs_by_option[key[3]].append(pair)

    reference_cells, reference_models = cells_from_rows(reference)
    repeat_cells, repeat_models = cells_from_rows(repeat)
    if reference_models != repeat_models:
        raise ValueError("model scopes differ")
    strict = {"allowed_nonpositive": 0, "floor": 0.0, "minimum_mean": 0.0}
    two_veto = {"allowed_nonpositive": 2, "floor": -30.0, "minimum_mean": 10.0}
    selector_rules = {
        "strict_expanded": (reference_models, strict),
        "two_veto_expanded": (reference_models, two_veto),
    }
    if set(ORIGINAL_MODELS).issubset(reference_models):
        selector_rules["strict_original_four"] = (ORIGINAL_MODELS, strict)

    per_model = {
        model: comparison_summary(pairs)
        for model, pairs in sorted(pairs_by_model.items())
    }
    deterministic_models = [
        model
        for model, row in per_model.items()
        if row["terminal_exact_count"] == row["rows"]
    ]
    process_sensitive_models = [
        model
        for model, row in per_model.items()
        if row["terminal_exact_count"] != row["rows"]
    ]
    return {
        "schema": 1,
        "scope": (
            "identical-map, identical-option repeat audit on the overlap of the two grids; "
            "elapsed time is intentionally excluded"
        ),
        "reference": str(reference_path),
        "repeat": str(repeat_path),
        "reference_rows_total": len(reference_all),
        "overlap_rows": len(repeat),
        "overlap_cells": len(reference_cells),
        "models": reference_models,
        "overall": comparison_summary(all_pairs),
        "by_model": per_model,
        "by_option": {
            option: comparison_summary(pairs)
            for option, pairs in sorted(pairs_by_option.items())
        },
        "classification": {
            "terminal_exact_models": deterministic_models,
            "process_sensitive_models": process_sensitive_models,
            "criterion": "all control, option, and delta margins are exact on every overlap row",
        },
        "selector_repeatability": {
            name: selector_comparison(
                reference_cells,
                repeat_cells,
                models,
                rule,
            )
            for name, (models, rule) in selector_rules.items()
        },
        "interpretation": (
            "Stable activation and first-train commands prove that the option library itself "
            "is reproducible. Changed terminal margins make a one-process continuation score "
            "an unsafe deterministic label; process-sensitive models require replicated "
            "scenario sampling or exclusion before a selector can be frozen."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--repeat", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.reference, args.repeat)
    atomic_write(args.output, json.dumps(result, indent=1) + "\n")
    compact = {
        "overlap_rows": result["overlap_rows"],
        "terminal_exact_models": result["classification"]["terminal_exact_models"],
        "process_sensitive_models": result["classification"]["process_sensitive_models"],
        "by_model": {
            model: {
                "terminal_exact": row["terminal_exact_count"],
                "rows": row["rows"],
                "delta_class_changes": row["delta_class_changed_count"],
            }
            for model, row in result["by_model"].items()
        },
        "selector_changes": {
            name: row["decision_changed_count"]
            for name, row in result["selector_repeatability"].items()
        },
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
