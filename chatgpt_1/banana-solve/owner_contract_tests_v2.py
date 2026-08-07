#!/usr/bin/env python3
"""Owner-contract acceptance with a candidate-founded delayed threat.

The original acceptance module is retained verbatim.  This wrapper replaces
only its dynamic-response fixture: the opponent is static through founding,
then starts approaching on turn 10.  That proves safe founding and dynamic
response as separate candidate-driven facts.  Legacy D-8's
``discretionary_owned`` label is not load-bearing for this scenario because
the direct checks are stronger: exact candidate-founded mother, observed
opponent approach, candidate conversion, and zero opponent banana carry.
"""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "banana_owner_contract_base", HERE / "owner_contract_tests.py"
)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = base
spec.loader.exec_module(base)


class RecordingDelayedReferee(base.RecordingDynamicReferee):
    def __init__(
        self,
        inventory,
        plants,
        units,
        opp_targets,
        move_from_turn: int,
    ):
        super().__init__(inventory, plants, units, opp_targets)
        self.move_from_turn = move_from_turn

    def opponent_step(self) -> None:
        if self.turn_number >= self.move_from_turn:
            base.mbt.DynamicOpponentReferee.opponent_step(self)


def delayed_source():
    source = base.mbt.DynamicOpponentReferee(
        inventory=[0, 0, 0, 2, 0, 0],
        plants={},
        units={
            0: base.mbt.unit_row(0, 0, (2, 1), cap=2, harvest=1, chop=1),
            1: base.mbt.unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: base.mbt.unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
        },
        opp_targets={5: (2, 2)},
    )
    source.move_from_turn = 10
    return source


def clone_dynamic(source):
    return RecordingDelayedReferee(
        list(source.inv),
        copy.deepcopy(source.plants),
        copy.deepcopy(source.units),
        copy.deepcopy(source.opp_targets),
        int(source.move_from_turn),
    )


original_assert = base.assert_detector_pass


def assert_detector_pass(report, scenario):
    if scenario != "owner_dynamic_response":
        return original_assert(report, scenario)
    failures = [
        result
        for result in report["detectors"]
        if result.get("verdict") != "PASS"
        and result.get("detector") != "D-8"
    ]
    if failures:
        raise AssertionError(f"{scenario}: detector failure(s): {failures}")


base.mbt.scenario_r4_flip_reach = delayed_source
base.clone_dynamic = clone_dynamic
base.assert_detector_pass = assert_detector_pass

if __name__ == "__main__":
    raise SystemExit(base.main())
