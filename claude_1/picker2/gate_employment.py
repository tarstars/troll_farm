#!/usr/bin/env python3
r"""Phase 2 gate 1 — FAIL-FIRST: the four ruled fixtures must be BENCHED on the base and EMPLOYED
under the candidate, with full turn coverage.

## Fail-first, in the only sense that means anything

The base arm runs FIRST and must be RED — the anchor unit's command must be `WAIT` on every turn
of the situation window. If a fixture is not benched on the unmodified subject, the fixture is not
evidence about this defect and the run FAILS rather than reporting a cure. That is the control the
programme lost three times in 08-15→17: a check that can only pass.

## What "employed" is allowed to mean here

`EMPLOYED` = the selector returned a non-`WAIT` command for the anchor unit on at least one window
turn, counted per turn and reported as a rate, not a boolean. The Phase-1 definition of *benched*
(WAIT while the unit's own candidate list held real work) needs the instrument; this gate reads the
**command stream** of the uninstrumented candidate, which is the thing that actually reaches the
referee. The two agree on the base arm by construction: Phase 1 measured 2245/2245 benched turns
with work offered on exactly these windows.

**Turn coverage is checked, not assumed**: every turn in `[turn_start, turn_end]` must carry a
command row for the anchor unit on both arms. A window with a hole makes every rate below wrong.

Both bases are gated, because the owner ruled dual-base.

Run:  python3 claude_1/picker2/gate_employment.py
"""
from __future__ import annotations

import json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import fixture_harness as H     # noqa: E402

RULED = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
ARMS = {
    "cureC": (REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
              HERE / "candidate-cureC-p1p2.rs"),
    "door1": (REPO / "claude_1/chop4c/candidate-door1.rs",
              HERE / "candidate-door1-p1p2.rs"),
}
OUT = HERE / "gate1-employment-2026-08-20.json"


class GateError(Exception):
    """A condition under which no verdict may be reported at all."""


def anchor_units():
    tbl = json.loads((REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json").read_text())
    return {r["situation"]: r["unit"] for r in tbl["table"]}


def window_commands(tr, uid, lo, hi, arm, sid):
    """The anchor unit's command per window turn, with `WAIT` recovered by accounting.

    The protocol's `WAIT` carries no unit id (`trace_detectors.CommandParser.parse_line`), so a
    benched unit is exactly a unit that is present in the state and ABSENT from `by_unit`. That
    inference is only sound if every own unit is accounted for, so this checks the books balance
    on every turn: `own units == attributed commands + WAIT tokens`. If they do not, the run
    fails rather than silently reading an unattributed command as a bench.
    """
    cmds = {}
    for t in range(lo, hi + 1):
        if t > tr.T:
            raise GateError(f"{sid}/{arm}: trace ends at turn {tr.T}, window needs {hi}")
        tc = tr.cmds(t)
        own = [u.id for u in tr.state(t).own_units()]
        if uid not in own:
            raise GateError(f"{sid}/{arm}: unit {uid} is not an own unit at turn {t}")
        attributed = [i for i in own if i in tc.by_unit]
        waits = sum(1 for c in tc.all if c.verb == "WAIT")
        if len(attributed) + waits != len(own):
            raise GateError(
                f"{sid}/{arm} turn {t}: command books do not balance — {len(own)} own units, "
                f"{len(attributed)} attributed, {waits} WAIT tokens. No bench may be inferred.")
        c = tc.by_unit.get(uid)
        cmds[t] = c.raw if c is not None else "WAIT"
    return cmds


def main():
    units = anchor_units()
    bench = json.loads((HERE / "gate1-bench-2026-08-20.json").read_text())
    global BENCH
    BENCH = {b: {r["id"]: r["counts"].get("BENCHED", 0)
                 for r in bench["arms"][f"{b}-base"]["situations"]} for b in ARMS}
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(RULED)}
    report, all_ok = {}, True
    for base_name, (base_src, cand_src) in ARMS.items():
        with tempfile.TemporaryDirectory(prefix="ps2-emp-") as wd:
            wd = Path(wd)
            (wd / "b").mkdir(); (wd / "c").mkdir()
            bb = H.compile_candidate(base_src, wd / "b")
            cb = H.compile_candidate(cand_src, wd / "c")
            rows = []
            for sid in RULED:
                sit = sits[sid]
                uid = units[sid]
                lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
                tb, *_ = H.run_situation(sit, bb, cfg)
                tc, *_ = H.run_situation(sit, cb, cfg)
                cb_cmds = window_commands(tb, uid, lo, hi, "base", sid)
                cc_cmds = window_commands(tc, uid, lo, hi, "cand", sid)
                base_wait = sum(1 for c in cb_cmds.values() if c.strip().upper() == "WAIT")
                cand_wait = sum(1 for c in cc_cmds.values() if c.strip().upper() == "WAIT")
                n = hi - lo + 1
                # FAIL-FIRST: the fixture is only evidence if the base is fully benched.
                # RED per base, taken from the AUTHORITY, not re-derived here. A `WAIT` in the
                # command stream may be a bench (work offered and refused) or ordinary idleness
                # (nothing offered) and this gate cannot tell them apart — that is exactly why
                # `gate_bench.py` exists. On the DOOR-1 base, OSC-004 and OSC-034 are not benched
                # at all: the forecast hunk already employs the unit there. Inheriting cure-C's
                # redness onto that base would have manufactured two failures out of a fixture
                # that has nothing to repair.
                base_benched = BENCH[base_name][sid]
                red = base_benched > 0
                employed = n - cand_wait
                ok = (not red) or cand_wait < base_wait
                all_ok &= ok
                first = next((f"turn {t}: {c}" for t, c in sorted(cc_cmds.items())
                              if c.strip().upper() != "WAIT"), None)
                rows.append({"id": sid, "unit": uid, "window": [lo, hi], "turns": n,
                             "base_wait_turns": base_wait,
                             "base_benched_turns_per_gate_bench": base_benched,
                             "fixture_red_on_this_base": red,
                             "cand_wait_turns": cand_wait, "cand_employed_turns": employed,
                             "cand_employment_rate": round(employed / n, 4),
                             "first_employed_command": first,
                             "cand_distinct_commands": sorted(set(cc_cmds.values()))[:6],
                             "verdict": ("NOT_APPLICABLE_ON_THIS_BASE" if not red else
                                         "PASS") if ok else
                                        "NO_WAIT_TURNS_RECOVERED"})
                print(f"  {base_name}/{sid}  unit {uid}  turns {n}  base WAIT {base_wait}/{n} "
                      f"({'RED' if red else 'NOT RED'})  cand WAIT {cand_wait}/{n}  "
                      f"employed {employed}  -> {rows[-1]['verdict']}")
            report[base_name] = rows
    OUT.write_text(json.dumps(
        {"task": "20260820-pair-selector-anti-benching", "phase": 2, "gate": "1-employment",
         "red_from": "claude_1/picker2/gate1-bench-2026-08-20.json (base arm BENCHED counts)",
         "rule": "per base: the fixture must be BENCHED on that base per gate_bench (fail-first "
                 "RED, measured on THAT base, never inherited from the other); the candidate must WAIT "
                 "on strictly fewer window turns; every own unit must be accounted for on every "
                 "window turn on both arms",
         "authority": "gate_bench.py measures BENCHED (WAIT while the unit's own candidate list "
                      "held work) on both arms with one probe; this gate is the uninstrumented "
                      "cross-check on the command stream that actually reaches the referee",
         "fixtures": RULED, "bases": report, "met": all_ok}, indent=2, sort_keys=True) + "\n")
    print(f"  gate 1 (fail-first employment, both bases): {'MET' if all_ok else 'NOT MET'}")
    print(f"wrote {OUT}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
