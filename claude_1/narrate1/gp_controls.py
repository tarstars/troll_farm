#!/usr/bin/env python3
"""Controls for the G-P gate: prove each check can FAIL before believing it passed.

A gate that reports 34/34 without ever having been shown to fail is the failure mode this project
keeps paying for. Every control below corrupts exactly one thing the gate claims to catch, on a
real recorded line, and asserts the complaint arrives.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_gp_parity as gp   # noqa: E402


class FakeState:
    def __init__(self, ids):
        self._ids = ids

    def own_units(self):
        return [type("U", (), {"id": i})() for i in self._ids]


class FakeTrace:
    def __init__(self, rosters):
        self.T = len(rosters)
        self._rosters = rosters

    def state(self, t):
        return FakeState(self._rosters[t - 1])


GOOD = [
    "MSG yamo-waypoint-rust NARRATE v2 t=1 u0=NONE;MOVE 0 3 4",
    "MSG NARRATE v2 t=2 u0=TREE(3,4) u2=SHACK;MOVE 0 3 4;HARVEST 2",
]
ROSTERS = [[0], [0, 2]]


def run(name, lines, rosters, expect_error_substr):
    errs = gp.check_telemetry("CTRL", FakeTrace(rosters), lines)
    fired = any(expect_error_substr in e for e in errs)
    return {"control": name, "expected": expect_error_substr, "fired": fired,
            "errors": errs[:3]}


def main():
    controls = [
        # the baseline must be CLEAN, or every "fired" below proves nothing
        {"control": "unmutated telemetry is accepted", "expected": "no errors",
         "fired": not gp.check_telemetry("CTRL", FakeTrace(ROSTERS), GOOD),
         "errors": gp.check_telemetry("CTRL", FakeTrace(ROSTERS), GOOD)},
        run("turn misalignment", [GOOD[0], GOOD[1].replace("t=2", "t=3")], ROSTERS,
            "turn misalignment"),
        run("a unit dropped from the roster",
            [GOOD[0], GOOD[1].replace(" u2=SHACK", "")], ROSTERS, "roster"),
        run("ids out of order",
            [GOOD[0], "MSG NARRATE v2 t=2 u2=SHACK u0=TREE(3,4);MOVE 0 3 4"], ROSTERS,
            "not ascending"),
        run("a second MSG token",
            [GOOD[0], GOOD[1] + ";MSG extra"], ROSTERS, "2 MSG tokens"),
        run("MSG not first",
            [GOOD[0], "MOVE 0 3 4;MSG NARRATE v2 t=2 u0=TREE(3,4) u2=SHACK"], ROSTERS,
            "not first"),
        run("off-grammar target", [GOOD[0], GOOD[1].replace("SHACK", "HOME")], ROSTERS,
            "off-grammar"),
        run("banner on a later turn",
            [GOOD[0], "MSG yamo-waypoint-rust NARRATE v2 t=2 u0=TREE(3,4) u2=SHACK;MOVE 0 3 4"],
            ROSTERS, "banner present"),
        run("a duplicated unit",
            [GOOD[0], "MSG NARRATE v2 t=2 u0=TREE(3,4) u0=SHACK u2=SHACK;MOVE 0 3 4"], ROSTERS,
            "appears twice"),
    ]
    # the parity comparison itself must be live: WITHOUT stripping, the arms differ
    line = GOOD[1]
    controls.append({
        "control": "strip_msg removes the complete token, and only it",
        "expected": "stripped == the gameplay tokens; unstripped still carries MSG",
        "fired": (gp.strip_msg(line) == "MOVE 0 3 4;HARVEST 2"
                  and "MSG" in line and len(gp.msg_fragments(line)) == 1),
        "errors": [gp.strip_msg(line)],
    })
    # a MSG-shaped payload must not be confused with a gameplay token that merely contains "MSG"
    controls.append({
        "control": "a gameplay token containing the letters MSG is NOT stripped",
        "expected": "kept",
        "fired": gp.strip_msg("MOVE 0 3 4;MSGX 1") == "MOVE 0 3 4;MSGX 1",
        "errors": [gp.strip_msg("MOVE 0 3 4;MSGX 1")],
    })

    ok = all(c["fired"] for c in controls)
    out = {"gate": "G-P", "controls": controls, "all_fired": ok}
    dest = HERE / "results" / "gp-controls-2026-08-23.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for c in controls:
        print(f"  {'OK    ' if c['fired'] else 'FAILED'} {c['control']}")
    print(f"\n  G-P CONTROLS: {'ALL FIRED' if ok else 'A CONTROL DID NOT FIRE'} -> {dest}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
