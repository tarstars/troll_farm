#!/usr/bin/env python3
"""Decode-level controls for G-P v3: prove each check can FAIL before believing it passed.

A gate that reports 34/34 without ever having been shown to fail is the failure mode this project
keeps paying for. Every control below corrupts exactly one thing the gate claims to catch and
asserts the complaint arrives.

The three controls that are new in v3 — version refusal, malformed-input failure, and the
three-state round-trip distinction — are the ones codex_1's ruling `20260823T113503Z` named as
load-bearing, because the collapse of `available=<concrete>` into `available=NONE` is precisely
what cost the last round.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_gp3_parity as gp   # noqa: E402


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
    "MSG yamo-waypoint-rust NARRATE v3 t=1 u0=NONE/NONE;MOVE 0 3 4",
    "MSG NARRATE v3 t=2 u0=TREE(3,4)/TREE(3,4) u2=NONE/SHACK;MOVE 0 3 4;HARVEST 2",
]
ROSTERS = [[0], [0, 2]]


def run(name, lines, rosters, expect_error_substr):
    errs = gp.check_telemetry("CTRL", FakeTrace(rosters), lines)
    return {"control": name, "expected": expect_error_substr,
            "fired": any(expect_error_substr in e for e in errs), "errors": errs[:3]}


def refuses(payload, substr):
    try:
        gp.decode(payload)
    except gp.GateError as exc:
        return substr in str(exc)
    return False


def main():
    base_errs = gp.check_telemetry("CTRL", FakeTrace(ROSTERS), GOOD)
    controls = [
        {"control": "unmutated v3 telemetry is accepted", "expected": "no errors",
         "fired": not base_errs, "errors": base_errs},
        run("turn misalignment", [GOOD[0], GOOD[1].replace("t=2", "t=3")], ROSTERS,
            "turn misalignment"),
        run("a unit dropped from the roster",
            [GOOD[0], GOOD[1].replace(" u2=NONE/SHACK", "")], ROSTERS, "roster"),
        run("ids out of order",
            [GOOD[0], "MSG NARRATE v3 t=2 u2=NONE/SHACK u0=TREE(3,4)/TREE(3,4);MOVE 0 3 4"],
            ROSTERS, "not ascending"),
        run("a second MSG token", [GOOD[0], GOOD[1] + ";MSG extra"], ROSTERS, "2 MSG tokens"),
        run("MSG not first",
            [GOOD[0], "MOVE 0 3 4;MSG NARRATE v3 t=2 u0=TREE(3,4)/TREE(3,4) u2=NONE/SHACK"],
            ROSTERS, "not first"),
        run("off-grammar chosen target",
            [GOOD[0], GOOD[1].replace("u2=NONE/SHACK", "u2=HOME/SHACK")], ROSTERS,
            "off-grammar chosen"),
        run("off-grammar available target",
            [GOOD[0], GOOD[1].replace("u2=NONE/SHACK", "u2=NONE/HOME")], ROSTERS,
            "off-grammar available"),
        run("banner on a later turn",
            [GOOD[0], "MSG yamo-waypoint-rust NARRATE v3 t=2 u0=TREE(3,4)/TREE(3,4) "
                      "u2=NONE/SHACK;MOVE 0 3 4"], ROSTERS, "banner present"),
        run("a duplicated unit",
            [GOOD[0], "MSG NARRATE v3 t=2 u0=NONE/NONE u0=SHACK/SHACK u2=NONE/SHACK;MOVE 0 3 4"],
            ROSTERS, "appears twice"),
        run("lone-unit tie parity broken",
            ["MSG yamo-waypoint-rust NARRATE v3 t=1 u0=NONE/TREE(3,4);MOVE 0 3 4"], [[0]],
            "tie parity broken"),
        run("payload over the 2,000-character budget",
            ["MSG yamo-waypoint-rust NARRATE v3 t=1 u0=NONE/NONE " + "x" * 2000 + ";MOVE 0 3 4"],
            [[0]], "exceeds 2000"),
    ]

    # --- version refusal: the v3 decoder must refuse anything that is not v3, never guess ---
    for label, payload in [
            ("v2 (the previous live grammar)", "MSG NARRATE v2 t=2 u0=NONE"),
            ("v4 (a future grammar)", "MSG NARRATE v4 t=2 u0=NONE/NONE"),
            ("no version token at all", "MSG NARRATE t=2 u0=NONE/NONE")]:
        controls.append({
            "control": f"version refusal — {label}", "expected": "unsupported NARRATE version",
            "fired": refuses(payload, "unsupported NARRATE version"), "errors": [payload]})

    # --- malformed input: each of these must FAIL, not decode to something plausible ---
    for label, payload, substr in [
            ("v2-shaped unit token, no separator",
             "MSG NARRATE v3 t=1 u0=NONE", "off-grammar unit token"),
            ("empty available side", "MSG NARRATE v3 t=1 u0=NONE/", "off-grammar unit token"),
            ("empty chosen side", "MSG NARRATE v3 t=1 u0=/NONE", "off-grammar unit token"),
            ("two separators", "MSG NARRATE v3 t=1 u0=NONE/NONE/NONE", "off-grammar unit token"),
            ("no t= field", "MSG NARRATE v3 u0=NONE/NONE", "no t= field"),
            ("not an MSG token", "NARRATE v3 t=1 u0=NONE/NONE", "not an MSG token"),
            ("ABSENT in the chosen position",
             "MSG NARRATE v3 t=1 u0=ABSENT/NONE", "off-grammar chosen")]:
        controls.append({"control": f"malformed input — {label}", "expected": substr,
                         "fired": refuses(payload, substr), "errors": [payload]})

    # --- the three-state round-trip distinction: the whole reason v3 exists ---
    three = {
        "discarded real want": "MSG NARRATE v3 t=1 u0=NONE/TREE(3,4)",
        "explicit WAIT was locally best": "MSG NARRATE v3 t=1 u0=NONE/NONE",
        "no candidate vector at all": "MSG NARRATE v3 t=1 u0=NONE/ABSENT",
    }
    decoded = {k: gp.decode(v)[1][0] for k, v in three.items()}
    wires = list(three.values())
    controls.append({
        "control": "three-state round trip — the three states are pairwise distinct on the wire "
                   "AND after decoding",
        "expected": "3 distinct wire forms, 3 distinct decoded values, all with chosen=NONE",
        "fired": (len(set(wires)) == 3 and len(set(decoded.values())) == 3
                  and all(v[0] == "NONE" for v in decoded.values())),
        "errors": [f"{k}: {v}" for k, v in decoded.items()]})
    controls.append({
        "control": "ABSENT is not readable as NONE and NONE is not readable as ABSENT",
        "expected": "decoded available differs",
        "fired": decoded["no candidate vector at all"][1] == "ABSENT"
                 and decoded["explicit WAIT was locally best"][1] == "NONE",
        "errors": [str(decoded["no candidate vector at all"]),
                   str(decoded["explicit WAIT was locally best"])]})

    # --- the charter's cross-version rule: a v2 decoder must REFUSE v3, never mis-read it ---
    sys.path.insert(0, str(HERE.parent / "narrate1"))
    import run_gp_parity as v2   # noqa: E402
    v2_refusals = []
    for payload in ["MSG NARRATE v3 t=1 u0=NONE/TREE(3,4)", "MSG NARRATE v3 t=1 u0=NONE/NONE",
                    "MSG NARRATE v3 t=1 u0=NONE/ABSENT"]:
        try:
            v2.decode(payload)
            v2_refusals.append(f"DECODED (must not): {payload}")
        except v2.GateError as exc:
            v2_refusals.append(str(exc)[:90])
    controls.append({
        "control": "the live v2 decoder REFUSES a v3 payload rather than mis-reading it",
        "expected": "version is not v2, on all three states",
        "fired": all(r.startswith("version is not v2") for r in v2_refusals),
        "errors": v2_refusals})

    # --- the parity comparison itself must stay live, unchanged from v2 ---
    line = GOOD[1]
    controls.append({
        "control": "strip_msg removes the complete token, and only it",
        "expected": "stripped == the gameplay tokens; unstripped still carries MSG",
        "fired": (gp.strip_msg(line) == "MOVE 0 3 4;HARVEST 2"
                  and "MSG" in line and len(gp.msg_fragments(line)) == 1),
        "errors": [gp.strip_msg(line)]})
    controls.append({
        "control": "a gameplay token containing the letters MSG is NOT stripped",
        "expected": "kept", "fired": gp.strip_msg("MOVE 0 3 4;MSGX 1") == "MOVE 0 3 4;MSGX 1",
        "errors": [gp.strip_msg("MOVE 0 3 4;MSGX 1")]})

    ok = all(c["fired"] for c in controls)
    out = {"gate": "G-P (NARRATE v3)", "controls": controls, "control_count": len(controls),
           "all_fired": ok}
    dest = HERE / "results" / "gp3-controls-2026-08-23.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for c in controls:
        print(f"  {'OK    ' if c['fired'] else 'FAILED'} {c['control']}")
    print(f"\n  G-P v3 CONTROLS: {sum(c['fired'] for c in controls)}/{len(controls)} fired -> "
          f"{'ALL FIRED' if ok else 'A CONTROL DID NOT FIRE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
