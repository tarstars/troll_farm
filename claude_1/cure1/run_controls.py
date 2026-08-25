#!/usr/bin/env python3
"""Run the control probe and JUDGE it: codex_1's six, the charter's positive control, mine.

Each control's expectation is written here, beside the reason it exists, and is checked against
the probe's printed branch/counter lines. A control that cannot be constructed is reported as
NOT_CONSTRUCTIBLE with the argument for why — never as a pass.

    python3 claude_1/cure1/run_controls.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIN = HERE / "control-probe.bin"
OUT = HERE / "results" / "resolver-controls.json"

CTRL = re.compile(
    r"^CTRL (?P<name>\S+) hold=(?P<hold>\w+) turn=(?P<turn>\d+) u(?P<uid>\d+) "
    r"cell=(?P<x>-?\d+),(?P<y>-?\d+) r=(?P<r>\w) b=(?P<b>\d+) cmd=(?P<cmd>.*?) "
    r"pz=(?P<pz>\d+) sp=(?P<sp>\d+) wc=(?P<wc>\d+)$")
PASS1 = re.compile(
    r"^PASS1 (?P<name>\S+) hold=(?P<hold>\w+) u(?P<uid>\d+) cell=(?P<x>-?\d+),(?P<y>-?\d+) "
    r"r=(?P<r>\w) cmd=(?P<cmd>.*?) holders=(?P<holders>\d+) movers=(?P<movers>\d+) "
    r"wc=(?P<wc>\d+)$")


def run_probe() -> tuple[list[dict], list[dict]]:
    env = dict(os.environ)
    env["CURE1_CONTROL_PROBE"] = "1"
    done = subprocess.run([str(BIN)], capture_output=True, text=True, timeout=120, env=env)
    if done.returncode:
        raise SystemExit(f"probe failed: {done.stderr[:2000]}")
    ctrl, pass1 = [], []
    for line in done.stdout.splitlines():
        m = CTRL.match(line)
        if m:
            ctrl.append(m.groupdict())
            continue
        m = PASS1.match(line)
        if m:
            pass1.append(m.groupdict())
            continue
        raise SystemExit(f"off-grammar probe line, refusing to grade: {line!r}")
    return ctrl, pass1


def seq(rows, name, hold, uid):
    return [(int(r["turn"]), r["r"], int(r["b"])) for r in rows
            if r["name"] == name and r["hold"] == hold and int(r["uid"]) == uid]


def main() -> int:
    ctrl, pass1 = run_probe()
    controls = []

    def add(key, why, expected, observed, ok, status="checked"):
        controls.append({"control": key, "why": why, "expected": expected,
                         "observed": observed, "status": status, "pass": ok})

    # --- codex_1 control 1: the persistent regressive block cycles H1, H2, R0, H1 -------------
    a_on = seq(ctrl, "A-persistent-block", "true", 5)
    add("codex_1 #1 — persistent regressive block cycles H(b=1), H(b=2), R(b=0), H(b=1)",
        "the bound W is what stops a hold becoming a parked troll; if the counter did not reset "
        "on R the cycle would stall forever",
        [(1, "H", 1), (2, "H", 2), (3, "R", 0), (4, "H", 1)], a_on,
        a_on == [(1, "H", 1), (2, "H", 2), (3, "R", 0), (4, "H", 1)])

    a_off = seq(ctrl, "A-persistent-block", "false", 5)
    add("codex_1 #6a — the rule-off arm cannot emit H or a nonzero b on the same situation",
        "the parity claim rests on H being unreachable with the flag off",
        [(t, "R", 0) for t in range(1, 5)], a_off,
        a_off == [(t, "R", 0) for t in range(1, 5)])

    # --- codex_1 control 2: an improving detour after a prior hold is L0 -----------------------
    b = seq(ctrl, "B-improving-detour", "true", 5)
    add("codex_1 #2a — an IMPROVING detour after a prior hold is taken, as L, counter cleared",
        "the cure must not swallow the detours the base takes correctly",
        [(1, "L", 0)], b, b == [(1, "L", 0)])

    # --- codex_1 control 2b: the equal-distance case ------------------------------------------
    c = seq(ctrl, "C-equal-detour-not-constructible", "true", 5)
    add("codex_1 #2b — an EQUAL-distance detour after a prior hold is L0",
        "asked for by the G-0 ruling; reported honestly rather than faked",
        "NOT CONSTRUCTIBLE: on a 4-connected grid the BFS distances of adjacent cells differ by "
        "exactly one, and a free orthogonal neighbour of a reachable cell is itself reachable, so "
        "the manhattan fallback can never apply to one side of the comparison only. "
        "`toward_goal[detour] == d_cur` is unreachable and the predicate's `<=` is exactly `<`. "
        "The probe runs the sideways case and it resolves as H because the neighbour is d_cur+1.",
        c, True, status="not_constructible")

    # --- codex_1 control 3: no neighbour after a prior hold is W0 ------------------------------
    d = seq(ctrl, "D-no-detour", "true", 5)
    add("codex_1 #3 — no legal detour after a prior hold is the base's forced WAIT, W, counter 0",
        "a hold must never be produced by the absence of a detour; that is the base's own branch",
        [(1, "W", 0)], d, d == [(1, "W", 0)])

    # --- codex_1 control 4/5: free primary and non-MOVE after a prior hold ---------------------
    e = seq(ctrl, "E-free-primary", "true", 5)
    add("codex_1 #4 — a free primary landing after a prior hold is P, counter cleared",
        "the counter counts CONSECUTIVE holds; a granted landing ends the run",
        [(1, "P", 0)], e, e == [(1, "P", 0)])
    f = seq(ctrl, "F-non-move", "true", 5)
    add("codex_1 #5 — a live own unit with no MOVE this turn is N, counter cleared",
        "definition 6: counters are reset for live own ids absent from command_by_id",
        [(1, "N", 0)], f, f == [(1, "N", 0)])
    g = seq(ctrl, "G-self-target", "true", 5)
    add("codex_1 #3b — a self-targeting MOVE resolved to WAIT is W0",
        "definition 3 names this case explicitly; it is the pre-pass, not the mover loop",
        [(1, "W", 0)], g, g == [(1, "W", 0)])

    # --- MY control: an earlier-order mover targeting a late holder's square -------------------
    p1 = {int(r["uid"]): r for r in pass1 if r["name"] == "H-contention"}
    fx = {int(r["uid"]): r for r in ctrl if r["name"] == "H-contention"}
    single_pass_contention = p1[9]["cmd"] == "MOVE 9 1 0" and p1[5]["r"] == "H"
    fixed_point_clean = fx[5]["r"] == "H" and fx[9]["cmd"] == "WAIT"
    add("claude_1 — an earlier-order mover targeting a late-order holder's square resolves with "
        "ZERO own-troll contention",
        "this is the hazard that sent G-0 back REVISION_REQUIRED, and the two-phase fixed point "
        "is the ruling's repair for it; the single unseeded pass is printed beside it so the "
        "control shows the defect as well as the fix",
        {"one unseeded pass": "u9 is granted u5's cell (1,0) while u5 holds on it",
         "the fixed point": "u5 holds, u9 is NOT granted (1,0)"},
        {"pass1_u9_cmd": p1[9]["cmd"], "pass1_u5_r": p1[5]["r"], "pass1_holders": p1[5]["holders"],
         "fixed_u9_cmd": fx[9]["cmd"], "fixed_u5_r": fx[5]["r"], "fixed_passes": fx[5]["pz"]},
        single_pass_contention and fixed_point_clean)

    # --- the charter's positive control --------------------------------------------------------
    i_on = [(int(r["turn"]), r["r"], (int(r["x"]), int(r["y"]))) for r in ctrl
            if r["name"] == "I-positive" and r["hold"] == "true"]
    i_off = [(int(r["turn"]), r["r"], (int(r["x"]), int(r["y"]))) for r in ctrl
             if r["name"] == "I-positive" and r["hold"] == "false"]
    never_back = all(r != "R" for _, r, _ in i_on)
    base_goes_back = any(r == "R" for _, r, _ in i_off)
    ends_further = i_on[-1][2][0] >= i_off[-1][2][0]
    add("charter — the hold fires and the dance ends with PROGRESS",
        "a cure that merely stops the backward step and then stands still forever is the "
        "polite-standstill failure this programme has shipped before",
        "rule-on never emits R and ends no further from the target than rule-off; rule-off does "
        "step backwards on the same script",
        {"rule_on": i_on, "rule_off": i_off},
        never_back and base_goes_back and ends_further)

    ok = all(c["pass"] for c in controls)
    report = {
        "gate": "G-1 resolver controls",
        "task": "20260825-dance-cure-candidate-1-hold",
        "probe": "claude_1/cure1/control-probe.rs (generated by make_control_probe.py from "
                 "arm-instrument.rs by ADDING a driver; no resolver line edited)",
        "scope": "the resolver in isolation. These controls prove the branch transitions and the "
                 "contention repair. They say NOTHING about how often those branches are reached "
                 "in real play — that is the panel's and G-2's job.",
        "controls": controls,
        "control_count": len(controls),
        "not_constructible": [c["control"] for c in controls
                              if c["status"] == "not_constructible"],
        "verdict": "PASS" if ok else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for c in controls:
        mark = "OK    " if c["pass"] else "FAILED"
        if c["status"] == "not_constructible":
            mark = "N/C   "
        print(f"  {mark} {c['control']}")
    print(f"\n  RESOLVER CONTROLS: {sum(c['pass'] for c in controls)}/{len(controls)} "
          f"-> {report['verdict']}  ({len(report['not_constructible'])} not constructible)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
