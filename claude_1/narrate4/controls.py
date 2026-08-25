#!/usr/bin/env python3
"""Decode-level controls for NARRATE **v4** — prove every check can FAIL before believing a pass.

A gate that reports 240/240 without ever having been shown to fail is the failure mode this
programme keeps paying for. Every control below corrupts exactly ONE thing the v4 decoder claims
to catch, and asserts the complaint arrives.

The v4-specific ones are the branch code, the `b=` counter and its consecutive-H arithmetic, the
three per-turn measurements, the pass bound, the rule-off clauses, and mutual refusal with v3 —
in BOTH directions, which is the charter's explicit requirement and is checked here against the
LIVE v3 decoder (`claude_1/narrate3/run_gp3_parity.py`), not against a copy of it.

    python3 claude_1/narrate4/controls.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "narrate3"))

import narrate4 as n4          # noqa: E402
import run_gp3_parity as v3    # noqa: E402


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
    "MSG yamo-waypoint-rust NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0;WAIT",
    "MSG NARRATE v4 t=2 u0=TREE(3,4)/TREE(3,4)/r=H/b=1 u2=NONE/SHACK/r=P/b=0 pz=2 sp=0 wc=0;"
    "WAIT;MOVE 2 1 1",
]
ROSTERS = [[0], [0, 2]]


def run(name, lines, rosters, expect, rule_off=False):
    errs = n4.check_telemetry("CTRL", FakeTrace(rosters), lines, rule_off=rule_off)
    return {"control": name, "expected": expect,
            "fired": any(expect in e for e in errs), "errors": errs[:3]}


def refuses(payload, substr):
    try:
        n4.decode(payload)
    except n4.GateError as exc:
        return substr in str(exc)
    return False


def main() -> int:
    base_errs = n4.check_telemetry("CTRL", FakeTrace(ROSTERS), GOOD)
    controls = [
        {"control": "unmutated v4 telemetry is accepted", "expected": "no errors",
         "fired": not base_errs, "errors": base_errs},

        # --- inherited v3 checks, re-run rather than assumed to survive the grammar change ---
        run("turn misalignment", [GOOD[0], GOOD[1].replace("t=2", "t=3")], ROSTERS,
            "turn misalignment"),
        run("a unit dropped from the roster",
            [GOOD[0], GOOD[1].replace(" u2=NONE/SHACK/r=P/b=0", "")], ROSTERS, "roster"),
        run("ids out of order",
            [GOOD[0], "MSG NARRATE v4 t=2 u2=NONE/SHACK/r=P/b=0 "
                      "u0=TREE(3,4)/TREE(3,4)/r=H/b=1 pz=2 sp=0 wc=0;WAIT"],
            ROSTERS, "not ascending"),
        run("a second MSG token", [GOOD[0], GOOD[1] + ";MSG extra"], ROSTERS, "2 MSG tokens"),
        run("MSG not first",
            [GOOD[0], "WAIT;MSG NARRATE v4 t=2 u0=TREE(3,4)/TREE(3,4)/r=H/b=1 "
                      "u2=NONE/SHACK/r=P/b=0 pz=2 sp=0 wc=0"], ROSTERS, "not first"),
        run("banner on a later turn",
            [GOOD[0], "MSG yamo-waypoint-rust NARRATE v4 t=2 u0=TREE(3,4)/TREE(3,4)/r=H/b=1 "
                      "u2=NONE/SHACK/r=P/b=0 pz=2 sp=0 wc=0;WAIT"], ROSTERS, "banner present"),
        run("a duplicated unit",
            [GOOD[0], "MSG NARRATE v4 t=2 u0=NONE/NONE/r=P/b=0 u0=SHACK/SHACK/r=P/b=0 "
                      "u2=NONE/SHACK/r=P/b=0 pz=2 sp=0 wc=0;WAIT"], ROSTERS, "appears twice"),
        run("lone-unit tie parity broken",
            ["MSG yamo-waypoint-rust NARRATE v4 t=1 u0=NONE/TREE(3,4)/r=P/b=0 pz=1 sp=0 wc=0"],
            [[0]], "tie parity broken"),
        run("payload over the 2,000-character budget",
            ["MSG yamo-waypoint-rust NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 " + "x" * 2000
             + " pz=1 sp=0 wc=0"], [[0]], "exceeds 2000"),

        # --- v4-specific: the branch code and the counter ---
        run("b= rises by more than one on a hold",
            [GOOD[0], GOOD[1].replace("r=H/b=1", "r=H/b=2")], ROSTERS, "held with b=2"),
        run("b= nonzero on a branch that is not H",
            [GOOD[0], GOOD[1].replace("u2=NONE/SHACK/r=P/b=0", "u2=NONE/SHACK/r=P/b=3")],
            ROSTERS, "branch P with b=3"),
        run("the fixed point exceeds its movers+1 bound",
            [GOOD[0], GOOD[1].replace("pz=2", "pz=9")], ROSTERS, "exceeds movers+1"),
        run("pz=0 — a turn that ran no pass at all",
            [GOOD[0], GOOD[1].replace("pz=2", "pz=0")], ROSTERS, "at least one pass"),

        # --- v4-specific: the rule-off clauses ---
        run("rule-off arm emits a hold", [GOOD[0], GOOD[1]], ROSTERS, "rule-off emitted r=H",
            rule_off=True),
        run("rule-off arm runs two passes", [GOOD[0], GOOD[1]], ROSTERS,
            "rule-off ran pz=2 passes", rule_off=True),
        run("rule-off arm reports a stale protection",
            [GOOD[0].replace("sp=0", "sp=1")], [[0]], "rule-off reports sp=1", rule_off=True),
    ]

    # --- malformed input: each must FAIL, not decode into something plausible ---
    for label, payload, substr in [
            ("a v3-shaped unit token (no r=/b= fields)",
             "MSG NARRATE v4 t=1 u0=NONE/NONE pz=1 sp=0 wc=0", "off-grammar unit token"),
            ("branch code that is not one of PLHRWN",
             "MSG NARRATE v4 t=1 u0=NONE/NONE/r=X/b=0 pz=1 sp=0 wc=0", "off-grammar branch code"),
            ("empty branch code",
             "MSG NARRATE v4 t=1 u0=NONE/NONE/r=/b=0 pz=1 sp=0 wc=0", "off-grammar branch code"),
            ("non-numeric b=",
             "MSG NARRATE v4 t=1 u0=NONE/NONE/r=H/b=x pz=1 sp=0 wc=0", "off-grammar b= value"),
            ("missing pz=", "MSG NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 sp=0 wc=0",
             "missing per-turn field"),
            ("missing sp=", "MSG NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 wc=0",
             "missing per-turn field"),
            ("missing wc=", "MSG NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 sp=0",
             "missing per-turn field"),
            ("a duplicated per-turn field",
             "MSG NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 pz=2 sp=0 wc=0", "appears twice"),
            ("a unit token after the per-turn fields",
             "MSG NARRATE v4 t=1 pz=1 sp=0 wc=0 u0=NONE/NONE/r=N/b=0",
             "after a per-turn field"),
            ("ABSENT in the chosen position",
             "MSG NARRATE v4 t=1 u0=ABSENT/NONE/r=N/b=0 pz=1 sp=0 wc=0", "off-grammar chosen"),
            ("off-grammar available target",
             "MSG NARRATE v4 t=1 u0=NONE/HOME/r=N/b=0 pz=1 sp=0 wc=0", "off-grammar available"),
            ("no t= field", "MSG NARRATE v4 u0=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0", "no t= field"),
            ("not an MSG token", "NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0",
             "not an MSG token")]:
        controls.append({"control": f"malformed input — {label}", "expected": substr,
                         "fired": refuses(payload, substr), "errors": [payload]})

    # --- version refusal, BOTH directions, against the live v3 decoder ---
    for label, payload in [("v3 (the previous live grammar)",
                            "MSG NARRATE v3 t=1 u0=NONE/NONE"),
                           ("v2", "MSG NARRATE v2 t=1 u0=NONE"),
                           ("v5 (a future grammar)",
                            "MSG NARRATE v5 t=1 u0=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0"),
                           ("no version token at all", "MSG NARRATE t=1 u0=NONE/NONE/r=N/b=0")]:
        controls.append({
            "control": f"the v4 decoder REFUSES {label}", "expected": "unsupported NARRATE version",
            "fired": refuses(payload, "unsupported NARRATE version"), "errors": [payload]})

    v3_refusals = []
    for payload in [GOOD[0].split(";")[0], GOOD[1].split(";")[0],
                    "MSG NARRATE v4 t=1 u0=NONE/ABSENT/r=W/b=0 pz=1 sp=0 wc=0"]:
        try:
            v3.decode(payload)
            v3_refusals.append(f"DECODED (must not): {payload}")
        except v3.GateError as exc:
            v3_refusals.append(str(exc)[:90])
    controls.append({
        "control": "the LIVE v3 decoder REFUSES a v4 payload rather than mis-reading it",
        "expected": "unsupported NARRATE version, on all three shapes",
        "fired": all("unsupported NARRATE version" in r for r in v3_refusals),
        "errors": v3_refusals})

    # --- the three-state round trip, inherited from v3 and still load-bearing in v4 ---
    three = {
        "discarded real want": "MSG NARRATE v4 t=1 u0=NONE/TREE(3,4)/r=N/b=0 pz=1 sp=0 wc=0",
        "explicit WAIT was locally best": "MSG NARRATE v4 t=1 u0=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0",
        "no candidate vector at all": "MSG NARRATE v4 t=1 u0=NONE/ABSENT/r=N/b=0 pz=1 sp=0 wc=0",
    }
    decoded = {k: n4.decode(v)[1][0] for k, v in three.items()}
    controls.append({
        "control": "three-state round trip — ABSENT, NONE and a concrete target stay pairwise "
                   "distinct through the v4 grammar",
        "expected": "3 distinct wire forms, 3 distinct decoded values, all with chosen=NONE",
        "fired": (len(set(three.values())) == 3 and len({v[:2] for v in decoded.values()}) == 3
                  and all(v[0] == "NONE" for v in decoded.values())),
        "errors": [f"{k}: {v}" for k, v in decoded.items()]})

    # --- the parity comparison itself must stay live ---
    line = GOOD[1]
    controls.append({
        "control": "strip_msg removes the complete token, and only it",
        "expected": "stripped == the gameplay tokens; unstripped still carries MSG",
        "fired": (n4.strip_msg(line) == "WAIT;MOVE 2 1 1" and "MSG" in line
                  and len(n4.msg_fragments(line)) == 1),
        "errors": [n4.strip_msg(line)]})
    controls.append({
        "control": "a gameplay token containing the letters MSG is NOT stripped",
        "expected": "kept", "fired": n4.strip_msg("MOVE 0 3 4;MSGX 1") == "MOVE 0 3 4;MSGX 1",
        "errors": [n4.strip_msg("MOVE 0 3 4;MSGX 1")]})

    ok = all(c["fired"] for c in controls)
    out = {"gate": "NARRATE v4 decode controls",
           "task": "20260825-dance-cure-candidate-1-hold",
           "controls": controls, "control_count": len(controls), "all_fired": ok}
    dest = HERE / "results" / "v4-decode-controls.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for c in controls:
        print(f"  {'OK    ' if c['fired'] else 'FAILED'} {c['control']}")
    print(f"\n  v4 DECODE CONTROLS: {sum(c['fired'] for c in controls)}/{len(controls)} fired -> "
          f"{'ALL FIRED' if ok else 'A CONTROL DID NOT FIRE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
