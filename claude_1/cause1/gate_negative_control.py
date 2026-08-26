#!/usr/bin/env python3
r"""NEGATIVE CONTROL for the two identity gates — task `20260821-osc032-033-cause-attribution`.

codex_1's G-1 review rejected the previous instrument because both joins were on CARDINALITY:
the accepted side compared the number of `ACCEPTED` rows with `chops=`, and the referee/bot
agreement compared plant COUNT plus powers. Both survive a wrong-cell attribution. The repair
replaced them with identity joins — but a gate that passes on the real corpus has not been shown
to be capable of failing, and an inert gate is exactly the failure mode this programme keeps
finding. So each gate is fed a stream that is corrupt in precisely the way the review named, and
the run FAILS unless every one of them is rejected.

Each case below is the mutation stated in the review, not a mutation chosen because it is easy to
catch: same count, wrong cell.

Run:  python3 claude_1/cause1/gate_negative_control.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/cause1",):
    sys.path.insert(0, str(REPO / p))
import cause_attribution as CA   # noqa: E402
import clause_tap as CT          # noqa: E402

OUT = HERE / "gate-negative-control-2026-08-21.json"

FN = ("PS4CHOPFN unit=0 turn=7 clause=ENTERED chop_power=2 free_cap=4 plants=2 "
      "unit_cell=3,3 state=5,5:PLUM:h4:s3:f1:cd0|6,6:LEMON:h2:s1:f0:cd2")
ROW_A = "PS4CHOP unit=0 turn=7 plant=5,5 kind=PLUM clause=ACCEPTED wood=3 trip=4"
ROW_B = "PS4CHOP unit=0 turn=7 plant=6,6 kind=LEMON clause=ACCEPTED wood=1 trip=6"
OUT_A = "PS4CHOPOUT unit=0 turn=7 i=0 target=5,5 command=MOVE_0_5_5"
OUT_B = "PS4CHOPOUT unit=0 turn=7 i=1 target=6,6 command=MOVE_0_6_6"
LIST2 = "PS4CHOPLIST unit=0 turn=7 returned=2"
GOOD = "\n".join([FN, ROW_A, ROW_B, OUT_A, OUT_B, LIST2])


class FakePlant:
    def __init__(self, cell, kind, health, size, fruits, cooldown):
        self.cell, self.kind = cell, kind
        self.health, self.size, self.fruits, self.cooldown = health, size, fruits, cooldown


class FakeUnit:
    def __init__(self, cell, chop_power=2, harvest_power=1):
        self.cell, self.chop_power, self.harvest_power = cell, chop_power, harvest_power


class FakeState:
    def __init__(self, plants):
        self.plants = plants


class FakeTrace:
    """The referee side, spelled by hand so the mutation is visible in this file."""

    def __init__(self, plants, unit_cell=(3, 3)):
        self._st, self._u = FakeState(plants), FakeUnit(unit_cell)

    def state(self, _turn):
        return self._st

    def unit(self, _uid, _turn):
        return self._u


TRACE_MATCHING = lambda: FakeTrace([FakePlant((5, 5), "PLUM", 4, 3, 1, 0),      # noqa: E731
                                    FakePlant((6, 6), "LEMON", 2, 1, 0, 2)])


def returned_list_cases():
    """Gate 5 — the accepted side. Every mutation keeps the COUNT the old join looked at."""
    swapped = "\n".join([FN, ROW_A, ROW_B,
                         "PS4CHOPOUT unit=0 turn=7 i=0 target=6,6 command=MOVE_0_6_6",
                         "PS4CHOPOUT unit=0 turn=7 i=1 target=5,5 command=MOVE_0_5_5", LIST2])
    wrong_cell = "\n".join([FN, ROW_A, ROW_B, OUT_A,
                            "PS4CHOPOUT unit=0 turn=7 i=1 target=9,9 command=MOVE_0_9_9", LIST2])
    moved_acceptance = "\n".join([
        FN, ROW_A,
        "PS4CHOP unit=0 turn=7 plant=6,6 kind=LEMON clause=PREDICT_TREE_NONE travel=1",
        OUT_A, OUT_B, LIST2])
    no_list = "\n".join([FN, ROW_A, ROW_B, OUT_A, OUT_B])
    guard_with_list = "\n".join([
        "PS4CHOPFN unit=0 turn=7 clause=FN_NO_CHOP_POWER chop_power=0 free_cap=4 plants=0 "
        "unit_cell=3,3 state=none",
        "PS4CHOPLIST unit=0 turn=7 returned=0"])
    length_lie = "\n".join([FN, ROW_A, ROW_B, OUT_A, OUT_B,
                            "PS4CHOPLIST unit=0 turn=7 returned=3"])
    out_of_order = "\n".join([FN, ROW_A, ROW_B,
                              "PS4CHOPOUT unit=0 turn=7 i=1 target=5,5 command=MOVE_0_5_5",
                              "PS4CHOPOUT unit=0 turn=7 i=0 target=6,6 command=MOVE_0_6_6", LIST2])
    return [
        ("same count, cells SWAPPED — the review's exact case", swapped, True),
        ("same count, one accepted cell replaced by a cell never accepted", wrong_cell, True),
        ("acceptance moved to the other plant, vector unchanged", moved_acceptance, True),
        ("an ENTERED call that emitted no list row", no_list, True),
        ("a guard-return call that emitted a list row", guard_with_list, True),
        ("a list row whose length does not match its elements", length_lie, True),
        ("returned-vector indices not in the vector's own order", out_of_order, True),
        ("the unmutated stream", GOOD, False),
    ]


def agreement_cases():
    """Gate: referee/bot agreement. Every mutation keeps plant COUNT and the powers equal."""
    moved = FakeTrace([FakePlant((5, 5), "PLUM", 4, 3, 1, 0),
                       FakePlant((7, 7), "LEMON", 2, 1, 0, 2)])
    restated = FakeTrace([FakePlant((5, 5), "PLUM", 1, 3, 1, 0),
                          FakePlant((6, 6), "LEMON", 2, 1, 0, 2)])
    rekinded = FakeTrace([FakePlant((5, 5), "APPLE", 4, 3, 1, 0),
                          FakePlant((6, 6), "LEMON", 2, 1, 0, 2)])
    elsewhere = FakeTrace([FakePlant((5, 5), "PLUM", 4, 3, 1, 0),
                           FakePlant((6, 6), "LEMON", 2, 1, 0, 2)], unit_cell=(4, 4))
    empty_fn = ("PS4CHOPFN unit=0 turn=7 clause=ENTERED chop_power=2 free_cap=4 plants=0 "
                "unit_cell=3,3 state=none")
    return [
        ("same count, one plant in a DIFFERENT CELL", GOOD, moved, True),
        ("same cells, one plant in a different STATE (health)", GOOD, restated, True),
        ("same cells and state, one plant a different KIND", GOOD, rekinded, True),
        ("same board, the audited unit standing somewhere else", GOOD, elsewhere, True),
        ("every cross-checked call saw an EMPTY board (inert gate)",
         empty_fn, FakeTrace([]), True),
        ("the unmutated stream against the matching trace", GOOD, TRACE_MATCHING(), False),
    ]


def main():
    rows, failures = [], []

    for name, stream, must_fail in returned_list_cases():
        try:
            CT.check_returned_lists("NEGCTL", "chop", CT.parse(stream)["chop"])
            rejected, why = False, None
        except CT.ClauseGateError as exc:
            rejected, why = True, str(exc).split(".")[0]
        rows.append({"gate": "returned-vector identity (gate 5)", "case": name,
                     "must_be_rejected": must_fail, "rejected": rejected, "gate_said": why})
        if rejected != must_fail:
            failures.append(f"gate 5, {name!r}: rejected={rejected}, expected {must_fail}")

    for name, stream, trace, must_fail in agreement_cases():
        try:
            CA.check_trace_agrees_with_tap("NEGCTL", CT.parse(stream), trace, 0)
            rejected, why = False, None
        except CT.ClauseGateError as exc:
            rejected, why = True, str(exc).split(".")[0]
        rows.append({"gate": "referee/bot canonical identity agreement", "case": name,
                     "must_be_rejected": must_fail, "rejected": rejected, "gate_said": why})
        if rejected != must_fail:
            failures.append(f"agreement gate, {name!r}: rejected={rejected}, expected {must_fail}")

    for r in rows:
        print(f"  [{'REJECTED' if r['rejected'] else 'accepted'}] "
              f"{'(must reject)' if r['must_be_rejected'] else '(must accept)'}  {r['case']}")
    OUT.write_text(json.dumps({
        "task": "20260821-osc032-033-cause-attribution",
        "what": "each identity gate is fed the corruption codex_1's G-1 review named — same "
                "count, wrong cell — and must reject it; the unmutated stream must pass",
        "why": "a gate that has only ever passed has not been shown to be capable of failing",
        "cases": rows}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    if failures:
        raise CT.ClauseGateError(
            "the identity gates are NOT fail-closed as claimed:\n  " + "\n  ".join(failures))
    print(f"\nall {len(rows)} cases behaved as required "
          f"({sum(1 for r in rows if r['must_be_rejected'])} corruptions rejected, "
          f"{sum(1 for r in rows if not r['must_be_rejected'])} clean streams accepted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
