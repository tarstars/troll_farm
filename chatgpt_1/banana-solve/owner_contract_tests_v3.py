#!/usr/bin/env python3
"""Final owner-contract adapter with a real second-worker transition.

The repository's historical mini-referee intentionally ignores TRAIN.  That is
fine for its old banana traces, but makes a funding-prefix acceptance test
impossible: the state forever contains one own unit.  This wrapper gives only
the one-worker funding fixture a rich, legal starting inventory and applies the
first emitted TRAIN using the real bill formula.  ``banana_command_turns`` then
checks only commands strictly before that landed TRAIN.

All lifecycle, unsafe-founding, delayed-threat, and carrier fixtures remain the
candidate-driven v2 tests unchanged.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "banana_owner_contract_v2", HERE / "owner_contract_tests_v2.py"
)
v2 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v2
spec.loader.exec_module(v2)
base = v2.base


class EventList(list):
    train_turn: int | None = None


class TrainingRecordingReferee(base.RecordingReferee):
    def __init__(self, inventory, plants, units):
        super().__init__(inventory, plants, units)
        self.funding_fixture = sum(
            1 for unit in self.units.values() if unit["player"] == 0
        ) == 1
        self.events = EventList()
        if self.funding_fixture:
            # Enough for any legal second-worker tuple selected by the parent;
            # BANANA remains available so pre/post-TRAIN banana behavior is
            # observable rather than vacuously disabled.
            self.inv = [50, 50, 50, max(self.inv[3], 2), 50, self.inv[5]]

    def apply(self, command_line: str) -> None:
        train = None
        for raw in command_line.split(";"):
            parts = raw.strip().split()
            if len(parts) == 5 and parts[0].upper() == "TRAIN":
                try:
                    train = tuple(int(value) for value in parts[1:5])
                except ValueError:
                    train = None
                break
        super().apply(command_line)
        if not self.funding_fixture or train is None or self.events.train_turn is not None:
            return
        ms, capacity, harvest, chop = train
        own = [unit for unit in self.units.values() if unit["player"] == 0]
        n = len(own)
        costs = [n + ms * ms, n + capacity * capacity,
                 n + harvest * harvest, 0, n + chop * chop, 0]
        if any(self.inv[index] < costs[index] for index in (0, 1, 2, 4)):
            return
        if any(unit["cell"] == base.mbt.TENT for unit in own):
            return
        for index in (0, 1, 2, 4):
            self.inv[index] -= costs[index]
        new_id = max(self.units) + 1
        self.units[new_id] = base.mbt.unit_row(
            new_id,
            0,
            base.mbt.TENT,
            speed=ms,
            cap=capacity,
            harvest=harvest,
            chop=chop,
        )
        self.events.train_turn = self.turn_number - 1


original_banana_turns = base.banana_command_turns


def banana_command_turns(events):
    turns = original_banana_turns(events)
    train_turn = getattr(events, "train_turn", None)
    if train_turn is None:
        return turns
    return [turn for turn in turns if turn < train_turn]


base.RecordingReferee = TrainingRecordingReferee
base.banana_command_turns = banana_command_turns

if __name__ == "__main__":
    raise SystemExit(base.main())
