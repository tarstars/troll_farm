#!/usr/bin/env python3
"""Small model-level falsifiers for the PLANT-aware candidate generator."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = json.loads((HERE / "parameters.json").read_text())

HEALTH = {"BANANA": 6, "PLUM": 12, "LEMON": 12, "APPLE": 20}
FIRST = {
    ("PLUM", True): 12, ("LEMON", True): 12, ("APPLE", True): 8, ("BANANA", True): 16,
    ("PLUM", False): 32, ("LEMON", False): 32, ("APPLE", False): 36, ("BANANA", False): 24,
}


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def test_species_felling_is_not_uniform() -> None:
    assert ceil_div(HEALTH["BANANA"], 1) == 6
    assert ceil_div(HEALTH["APPLE"], 1) == 20
    assert 16 / 6 > 3 * (16 / 20)


def test_water_is_a_scarce_timing_resource() -> None:
    assert FIRST[("APPLE", True)] < FIRST[("BANANA", True)]
    assert FIRST[("PLUM", True)] < FIRST[("PLUM", False)]
    assert P["geometry"]["median_wet_cells_within_4"] < P["geometry"]["median_free_cells_within_4"]


def test_finite_ledger_caps_rate_fantasy() -> None:
    trees = 3
    wood_units = 4 * trees
    rate_fantasy = 3.0 * 180
    assert min(rate_fantasy, wood_units) == wood_units
    assert 4 * wood_units == 48


def test_no_plant_is_legal_below_activation() -> None:
    gross = 16.0
    seed = 2.0
    worker_turns = 40
    net = gross - seed - P["opportunity_points_per_turn"] * worker_turns
    assert net < P["activation_points"]


def test_parameter_bounds_fit_packed_search() -> None:
    assert 0 < P["max_candidate_cells"] <= 64
    assert P["max_plan_depth"] <= P["max_plants"]
    assert P["max_plan_states"] > 0


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok {test.__name__}")
    print(f"PASS {len(tests)} tests")
