from __future__ import annotations

import pytest

from cgauto.d11_recipe_catalog_analysis import RECIPES, analyze, validate


def fixture_rows() -> list[dict]:
    rows = []
    for seat in range(2):
        for recipe, spec in RECIPES.items():
            margin = 20 if recipe == 2 else recipe
            rows.append(
                {
                    "seed": 0,
                    "seat": seat,
                    "opponent": "fixture",
                    "recipe": recipe,
                    "ms": spec[0],
                    "cc": spec[1],
                    "hp": spec[2],
                    "chop": spec[3],
                    "margin": margin,
                    "wood_edge": margin // 4,
                    "workers": 2,
                    "train_commands": 1,
                    "plant_commands": 1,
                    "harvest_commands": 2,
                    "chop_commands": 3,
                    "drop_commands": 4,
                    "move_commands": 5,
                }
            )
    return rows


def test_complete_catalog_selects_best_fixed_recipe(tmp_path):
    source = tmp_path / "catalog.tsv"
    source.write_text("fixture\n")
    result = analyze(fixture_rows(), source)

    assert result["design"]["complete"] is True
    assert result["best_fixed_recipe"] == 2
    assert result["map_oracle"]["selection_counts"] == {2: 1}
    assert result["per_recipe"]["2"]["training_completion"]["rate"] == 1


def test_catalog_rejects_missing_recipe_row():
    rows = fixture_rows()
    rows.pop()

    with pytest.raises(ValueError, match="incomplete/non-unique"):
        validate(rows)
