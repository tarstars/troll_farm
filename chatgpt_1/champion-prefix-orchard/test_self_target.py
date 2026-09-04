#!/usr/bin/env python3
from __future__ import annotations

import oracle


class Ref:
    def __init__(self, include_other: bool):
        self.plants = {}
        self.units = {
            0: {"player": 0, "cell": (3, 3)},
        }
        if include_other:
            self.units[2] = {"player": 0, "cell": (3, 3)}


def controller() -> oracle.OrchardController:
    policy = oracle.Policy(
        name="test", enabled=True, species="BANANA", start_turn=1,
        plant_count=1, max_door_distance=2, latest_plant_turn=20,
        fell_size=4,
    )
    value = oracle.OrchardController(policy)
    value.planter_id = 0
    value.candidate_cells = [(3, 3)]
    return value


def main() -> None:
    own = controller()
    assert own._next_empty_cell(Ref(False)) == (3, 3), (
        "the planter standing on its target must be allowed to PLANT there"
    )
    other = controller()
    assert other._next_empty_cell(Ref(True)) is None, (
        "a target occupied by another unit must still be rejected"
    )
    print("PASS planter self-occupancy regression")


if __name__ == "__main__":
    main()
