#!/usr/bin/env python3
r"""Negative control for the G-2 gates — each one is fed a stream it MUST reject.

Task `20260821-osc032-033-cause-attribution`. Work owner claude_1 · reviewer codex_1.
**Measurement only**; no fix, no candidate, no hypothesis verdict.

codex_1's standing requirement, twice applied at G-1 and adopted here without being asked:
*a gate that has only ever passed has not been shown to be a gate.* `g2_controls.py` passes on
this corpus. That is worth nothing until each of its checks is shown to BITE. So this file runs
OSC-032 once, captures the real command streams and the real stderr, then hands the very same
check functions deliberately corrupted copies and requires a `G2Error` for each.

The corruptions are the failure modes that would let a wrong cause be attributed:

- parity: one changed command byte; an empty pair of streams (equality that says nothing)
- coverage: a deleted call on a window turn (a gap); a duplicated call group (double-counting);
  a call claiming more plants than it emitted rows for, and fewer; a plant row emitted under a
  guard-return group; the same plant cell named twice in one call
- both ways: every ACCEPTED row stripped (a constant-"rejected" tap); the ACCEPTED rows stripped
  from one `main:CHOPS` turn (an acceptance the tap missed); two different routes in one turn
- card cross-check: one `main:CHOPS` route row dropped, so the measured count drifts from the
  count the card names

Two clean cases are also run and MUST be accepted, so the control cannot pass by rejecting
everything.

The cell-duplicate and plants-count cases are exercised on turns 41-52, which is OUTSIDE the
audited window, because the audited window of both fixtures contains no plants at all. That is a
control over the check, not a claim about the window, and it is the only honest way to exercise a
per-plant gate on a board with no plants.

Run:  python3 claude_1/cause1/g2_negative_control.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker2", "claude_1/cause1"):
    sys.path.insert(0, str(REPO / p))
import clause_tap as CT         # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import g2_controls as G2        # noqa: E402
import regression_tests as rt   # noqa: E402

SID = "OSC-032"
SUBJECT = "door1-clause"
MANIFEST = HERE / "route-probe-manifest-clause-2026-08-21.json"
CAUSE_TABLE = REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json"
OUT = HERE / "g2-negative-control-2026-08-21.json"
PLANTED_WINDOW = (41, 52)   # turns that really do carry plants, for the per-plant cases


def drop_first(lines, pred):
    out, dropped = [], False
    for ln in lines:
        if not dropped and pred(ln):
            dropped = True
            continue
        out.append(ln)
    if not dropped:
        raise RuntimeError("the corruption found no line to drop — the control is not exercising "
                           "what it claims to exercise")
    return out


def edit_first(lines, pred, fn):
    out, done = [], False
    for ln in lines:
        if not done and pred(ln):
            out.append(fn(ln))
            done = True
            continue
        out.append(ln)
    if not done:
        raise RuntimeError("the corruption found no line to edit")
    return out


def dup_group(lines, turn):
    """Duplicate a whole PS4CHOPFN group (its FN row and everything up to the next FN row)."""
    out, buf, capturing, done = [], [], False, False
    head = f"PS4CHOPFN unit=0 turn={turn} "
    for ln in lines:
        if not done and ln.startswith(head):
            capturing, buf = True, [ln]
            out.append(ln)
            continue
        if capturing and ln.startswith("PS4CHOPFN "):
            out.extend(buf)
            capturing, done = False, True
        out.append(ln)
    if capturing:
        out.extend(buf)
        done = True
    if not done:
        raise RuntimeError(f"no PS4CHOPFN group on turn {turn} to duplicate")
    return out


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(CAUSE_TABLE.read_text())["table"]}
    man = json.loads(MANIFEST.read_text())[SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    sit = {s["id"]: s for s in H.load_situations([SID])}[SID]
    uid = units[SID]
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    turns = int(cfg["turns"])

    with tempfile.TemporaryDirectory(prefix="g2neg-") as wd:
        wd = Path(wd)
        for d in ("p", "c"):
            (wd / d).mkdir()
        print(f"compiling champion {man['source_sha256'][:12]} + the clause tap ...")
        plain = H.compile_candidate(REPO / man["source"], wd / "p")
        probe = H.compile_candidate(REPO / man["probe"], wd / "c")
        spec = H.spec_for(sit, cfg)
        _, plain_cmds = rt.run_binary_custom(Path(plain), fp.make_referee(spec), turns)
        _, probe_cmds, err = C.run_diagnostic(probe, fp.make_referee(spec), turns)

    lines = err.splitlines()
    cases = []

    def record(name, must_reject, fn, what):
        try:
            fn()
        except (G2.G2Error, CT.ClauseGateError, RuntimeError, KeyError, ValueError) as exc:
            rejected, why = True, f"{type(exc).__name__}: {exc}"
        else:
            rejected, why = False, ""
        cases.append({"case": name, "gate": what, "must_be_rejected": must_reject,
                      "rejected": rejected, "rejection": why[:400]})
        flag = "ok " if rejected == must_reject else "!! "
        print(f"  {flag}{name:<34} must_reject={must_reject} rejected={rejected}")

    # ---------------- parity ----------------------------------------------------------------
    record("parity/clean", False, lambda: G2.check_parity_streams(SID, plain_cmds, probe_cmds),
           "parity")
    record("parity/one-changed-command", True,
           lambda: G2.check_parity_streams(SID, plain_cmds, probe_cmds.replace("WAIT", "MOVE", 1)),
           "parity")
    record("parity/both-streams-empty", True,
           lambda: G2.check_parity_streams(SID, "", ""), "parity")

    # ---------------- coverage --------------------------------------------------------------
    def cov(ls, a=lo, b=hi, which="chop", key="chop"):
        return G2.coverage_one_tap(SID, which, CT.parse("\n".join(ls))[key], uid, a, b)

    record("coverage/clean", False, lambda: cov(lines), "coverage")
    record("coverage/deleted-window-call", True,
           lambda: cov(drop_first(lines, lambda l: l.startswith(f"PS4CHOPFN unit=0 turn={lo} "))),
           "coverage")
    record("coverage/duplicated-call-group", True,
           lambda: cov(dup_group(lines, lo)), "coverage")
    record("coverage/claims-more-plants-than-rows", True,
           lambda: cov(edit_first(
               lines, lambda l: l.startswith(f"PS4CHOPFN unit=0 turn={lo} ") and "plants=0" in l,
               lambda l: l.replace("plants=0", "plants=1"))), "coverage")
    record("coverage/planted-turns-clean", False,
           lambda: cov(lines, *PLANTED_WINDOW), "coverage")
    record("coverage/claims-fewer-plants-than-rows", True,
           lambda: cov(edit_first(
               lines,
               lambda l: l.startswith(f"PS4CHOPFN unit=0 turn={PLANTED_WINDOW[0]} ")
               and "plants=" in l,
               lambda l: l.replace("plants=1", "plants=0").replace("plants=2", "plants=1")),
               *PLANTED_WINDOW), "coverage")
    record("coverage/same-cell-named-twice", True,
           lambda: cov(dup_plant_row(lines, PLANTED_WINDOW[0]), *PLANTED_WINDOW), "coverage")
    record("coverage/plant-row-under-guard-return", True,
           lambda: cov(guarded_with_a_plant_row(lines, lo)), "coverage")

    # ---------------- both ways -------------------------------------------------------------
    def bw(ls):
        parsed = CT.parse("\n".join(ls))
        chops = G2.route_turns("\n".join(ls), uid, "main:CHOPS")
        G2.check_both_ways(SID, chops, G2.accepted_turns(parsed, uid))
        return chops

    record("both-ways/clean", False, lambda: bw(lines), "both ways")
    record("both-ways/no-ACCEPTED-anywhere", True,
           lambda: bw([l for l in lines if "clause=ACCEPTED" not in l]), "both ways")
    record("both-ways/acceptance-missed-on-a-CHOPS-turn", True,
           lambda: bw(strip_accept_on_turn(lines, PLANTED_WINDOW[0])), "both ways")
    record("both-ways/two-routes-in-one-turn", True,
           lambda: bw(second_route_row(lines, PLANTED_WINDOW[0])), "both ways")

    # ---------------- card cross-check ------------------------------------------------------
    record("card-cross/clean", False,
           lambda: G2.check_card_cross(SID, G2.route_turns(err, uid, "main:CHOPS")), "card")
    record("card-cross/one-CHOPS-turn-dropped", True,
           lambda: G2.check_card_cross(SID, G2.route_turns(
               "\n".join(drop_first(
                   lines,
                   lambda l: l.startswith(f"PS3ROUTE unit=0 turn={PLANTED_WINDOW[0]} ")
                   and "route=CHOPS" in l)), uid, "main:CHOPS")), "card")

    bad = [c for c in cases if c["rejected"] != c["must_be_rejected"]]
    art = {
        "task": "20260821-osc032-033-cause-attribution",
        "gate": "negative control over the G-2 gates",
        "scope": "measurement only; no fix, no candidate, no hypothesis verdict",
        "fixture": SID, "unit": uid, "window": [lo, hi],
        "planted_control_window": list(PLANTED_WINDOW),
        "planted_window_note":
            "the audited window contains no plants at all, so the per-plant coverage cases are "
            "exercised on turns 41-52, which do. This controls the CHECK; it claims nothing "
            "about the window.",
        "cases": cases,
        "n_cases": len(cases),
        "n_corruptions": sum(1 for c in cases if c["must_be_rejected"]),
        "n_clean": sum(1 for c in cases if not c["must_be_rejected"]),
        "all_behaved": not bad,
    }
    OUT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    if bad:
        print(f"NEGATIVE CONTROL FAILED: {len(bad)} case(s) misbehaved, first {bad[0]['case']!r}",
              file=sys.stderr)
        raise SystemExit(1)
    print(f"{art['n_corruptions']} corruptions rejected, {art['n_clean']} clean streams accepted, "
          f"{len(cases)}/{len(cases)}")


def dup_plant_row(lines, turn):
    """Name the SAME cell twice inside one call, COUNT-PRESERVING.

    Duplicating a row would also change the row count, and the count check would fire first — the
    cell-identity gate would never be exercised and the case would pass for the wrong reason. So
    the second plant row's cell is rewritten to the first's instead: `plants=` still matches, and
    only the duplicate-cell gate can catch it. This is codex_1's same-count/wrong-cell class.
    """
    head = f"PS4CHOP unit=0 turn={turn} "
    idx = [i for i, ln in enumerate(lines) if ln.startswith(head)]
    if len(idx) < 2:
        raise RuntimeError(f"turn {turn} has {len(idx)} plant row(s); a count-preserving "
                           f"duplicate-cell corruption needs at least 2")
    first_cell = lines[idx[0]].split(" plant=")[1].split(" ")[0]
    out = list(lines)
    second = out[idx[1]]
    second_cell = second.split(" plant=")[1].split(" ")[0]
    if first_cell == second_cell:
        raise RuntimeError(f"turn {turn}: the two plant rows already share a cell")
    out[idx[1]] = second.replace(f" plant={second_cell} ", f" plant={first_cell} ", 1)
    return out


def guarded_with_a_plant_row(lines, turn):
    """Turn an ENTERED call into a guard return while leaving a plant row attached to it."""
    out, done = [], False
    head = f"PS4CHOPFN unit=0 turn={turn} "
    for ln in lines:
        if not done and ln.startswith(head):
            out.append(ln.replace("clause=ENTERED", "clause=FN_NO_CHOP_POWER"))
            out.append(f"PS4CHOP unit=0 turn={turn} plant=3,3 kind=APPLE "
                       f"clause=WOOD_NONPOSITIVE wood=0")
            done = True
            continue
        out.append(ln)
    if not done:
        raise RuntimeError(f"no PS4CHOPFN row on turn {turn}")
    return out


def strip_accept_on_turn(lines, turn):
    head = f"PS4CHOP unit=0 turn={turn} "
    out = [l for l in lines if not (l.startswith(head) and "clause=ACCEPTED" in l)]
    if len(out) == len(lines):
        raise RuntimeError(f"no ACCEPTED plant row on turn {turn} to strip")
    return out


def second_route_row(lines, turn):
    out, done = [], False
    head = f"PS3ROUTE unit=0 turn={turn} "
    for ln in lines:
        out.append(ln)
        if not done and ln.startswith(head):
            out.append(f"PS3ROUTE unit=0 turn={turn} fn=main route=FULL_BANK")
            done = True
    if not done:
        raise RuntimeError(f"no PS3ROUTE row on turn {turn}")
    return out


if __name__ == "__main__":
    main()
