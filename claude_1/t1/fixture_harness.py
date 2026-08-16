#!/usr/bin/env python3
"""T-1 stage 1 — the 34-fixture replay harness.

Task `20260816-t1-transport-level`, claimed at `f2d352d8`. **This is the instrument every later
T-1 claim is judged by**, so it is built before any fix code exists and it is required to be RED
on the unmodified resident for all 34 situations.

## Why the replay is a re-run, not a playback

The frozen situations record **only our own side's command line** — the opponent's commands are
not in the library at all. So a situation cannot be "played back": there is nothing to drive the
opponent with. What the library *does* record is enough to **regenerate the game that produced
it**: `map_id`, `map_class`, `opponent_profile`, `seed`, `generation_attempt`, `seat` and the
panel config digest.

Verified before this harness was written, not assumed: rebuilding all 34 maps from provenance
through `fuzz_panel.build_skeleton` reproduces each situation's `static_map_rows`
**byte-identically, 34 of 34**. That is what makes the re-run legitimate.

## The trap this harness is most likely to fall into

A harness that mis-wires the replay reports 34 failures too — identical output, wrong reason —
and would then report "fixed" for reasons unrelated to the fix. **Red for all 34 is therefore not
evidence on its own.** `--self-test` carries the control that matters: the same grader, on the
same real trace, must return FIXED for a window where the unit is *not* stuck. A grader that
cannot say FIXED cannot be trusted when it later says FIXED.

## Grading rule — frozen upstream, not softened here

From `local_claude_1/t1-prediction-registry-2026-08-16.md`:

> FIXED only if the D-1/P4 detector is silent over the window **AND** progress is restored.
> Detector-quiet-but-stalled counts as NOT FIXED.

That second clause is the 08-09 20/20 lesson and it is the failure mode T-1 is most likely to
produce, since yielding a square can convert an oscillation into a polite standstill.

## Stage 1b — the P4 clause, CLOSED

Stage 1 shipped with this gap named rather than hidden: the harness ran `detect_d1` only, so for
the four `P4_STALL` situations the "detector silent" clause was **vacuously True** and they were
graded on the progress clause alone.

Now wired, using **the panel's own `fuzz_panel.eval_p4`** rather than a second definition of
"stalled" written here — a second definition would let the word mean one thing to the gate and
another to this harness. `tr_p` is accepted by that function for signature parity and never
consulted (`fuzz_panel:1831-1838`), so passing the candidate trace twice is faithful.
`post_ct_state(ref)` supplies the world after the final command set resolves, which the post-C_T
rule needs to judge turn T at all.

Which clause applies is decided by the situation's own `kind`: **D-1 for a `D1_EPISODE`, P4 for a
`P4_STALL`.** `check_p4_fidelity()` requires every frozen stall to reproduce as a P4 violation
overlapping its window — the control that stops the new clause from being wired and still inert,
which is exactly how the D-1 clause shipped the first time.

**All 34 situations now carry a live detector clause**, verified firing on the resident.

Run:
    python3 claude_1/t1/fixture_harness.py --self-test
    python3 claude_1/t1/fixture_harness.py --candidate <path.rs> [--only OSC-006,OSC-007]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PIPE = REPO / "claude_1" / "pipeline"
BR2 = REPO / "claude_1" / "banana-restoration-r2"
LIB = BR2 / "oscillation-library-98628e98" / "library"

sys.path.insert(0, str(PIPE))
sys.path.insert(0, str(BR2))

import fuzz_panel as fp          # noqa: E402
import trace_detectors as td     # noqa: E402
import regression_tests as rt     # noqa: E402  (binary runner, same one fuzz_panel uses)

RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
CONFIG = PIPE / "fuzz-panel-floor-config.json"


class HarnessError(Exception):
    """Anything that would make a result mean something other than it says."""


def load_situations(only=None):
    sys.path.insert(0, str(BR2))
    import oscillation_library as ol
    sits = ol.load_library(str(LIB))
    if only:
        want = set(only)
        sits = [s for s in sits if s["id"] in want]
        missing = want - {s["id"] for s in sits}
        if missing:
            raise HarnessError(f"unknown situation id(s): {sorted(missing)}")
    return sits


def spec_for(sit, cfg):
    """Rebuild the exact game spec that produced this situation, from its provenance."""
    p = sit["provenance"]
    idx = int(p["map_id"][1:])
    _, specs = fp.build_skeleton(idx, p["map_class"], p["opponent_profile"], cfg)
    for spec in specs:
        if spec["seat"] == p["seat"]:
            # A reconstruction that does not reproduce the frozen board is not this game.
            if spec["rows"] != sit["static_map_rows"]:
                raise HarnessError(
                    f"{sit['id']}: rebuilt map does not match the frozen static_map_rows; "
                    f"the replay would be of a DIFFERENT game and any verdict would be void.")
            if spec["attempt"] != p["generation_attempt"] or spec["seed"] != p["seed"]:
                raise HarnessError(
                    f"{sit['id']}: rebuilt seed/attempt "
                    f"({spec['seed']}/{spec['attempt']}) != provenance "
                    f"({p['seed']}/{p['generation_attempt']}).")
            return spec
    raise HarnessError(f"{sit['id']}: no spec for seat {p['seat']}")


# --------------------------------------------------------------------------------------
# grading


def unit_positions(tr, uid, lo, hi):
    return [(t, tr.pos(uid, t)) for t in range(lo, min(hi, tr.T) + 1)]


def had_progress(tr, uid, lo, hi):
    """A progress event on any transition inside the window, by the detector's own definition.

    Deliberately reuses D-1's notion (carry change / inventory change on a DROP-PICK turn /
    plant appearing or disappearing under the unit) rather than inventing a second one — a
    second definition would let 'progress' mean one thing to the detector and another here.
    """
    for t in range(lo, min(hi, tr.T)):
        u0, u1 = tr.unit(uid, t), tr.unit(uid, t + 1)
        if u0 is None or u1 is None:
            continue
        if u0.carry != u1.carry:
            return True
        cmd = tr.cmd_of(uid, t)
        if cmd is not None and cmd.verb in ("DROP", "PICK"):
            if tr.state(t).inventories[0] != tr.state(t + 1).inventories[0]:
                return True
        p0 = tr.state(t).plant_at(u0.cell)
        p1 = tr.state(t + 1).plant_at(u0.cell)
        if (p0 is None) != (p1 is None):
            return True
    return False


def left_the_cycle(tr, uid, lo, hi, cycle_cells):
    """Did the unit reach any cell outside the frozen paced set inside the window?"""
    cyc = {tuple(c) for c in cycle_cells}
    for _, cell in unit_positions(tr, uid, lo, hi):
        if cell is not None and tuple(cell) not in cyc:
            return True
    return False


def check_p4_fidelity(sit, p4_violations):
    """A frozen P4_STALL must reproduce as a P4 liveness violation overlapping its window.

    Stage 1b's own control. Without it the P4 clause could be wired and still inert -- the
    exact failure the D-1 clause already shipped with once in this file.
    """
    if sit["kind"] != "P4_STALL":
        return None
    w = sit["window"]
    over = [v for v in p4_violations
            if not (v["window_end"] < w["turn_start"] or v["window_start"] > w["turn_end"])]
    if not over:
        raise HarnessError(
            f"{sit['id']}: the re-run does NOT reproduce a P4 liveness violation overlapping "
            f"turns {w['turn_start']}-{w['turn_end']}. Found: {p4_violations}. The P4 clause "
            f"would be inert and a FIXED verdict on a stall would be meaningless.")
    return over[0]


def check_replay_fidelity(sit, d1_episodes):
    """The re-run must REPRODUCE the frozen episode, or the replay is not of this situation.

    This is the control the first draft lacked. It fails loudly when the detector clause goes
    quiet for plumbing reasons rather than because the bot changed -- which is precisely how an
    inert grader would otherwise report a clean sweep of FIXEDs.
    """
    if sit["kind"] != "D1_EPISODE":
        return None
    w = sit["window"]
    # finding 2 — ACCEPTED. This matched only unit + turn bounds and then called the
    # episode "exact". Two different oscillations can share a unit and a window; the cells
    # and k are what make it THIS episode.
    match = [e for e in d1_episodes
             if e["unit"] == w["unit"] and e["turn_start"] == w["turn_start"]
             and e["turn_end"] == w["turn_end"]
             and [list(c) for c in e["cells"]] == [list(c) for c in w["cells"]]
             and e["k"] == w["k"]]
    if not match:
        near = [e for e in d1_episodes if e["unit"] == w["unit"]]
        raise HarnessError(
            f"{sit['id']}: the re-run does NOT reproduce the frozen D-1 episode "
            f"(unit {w['unit']}, turns {w['turn_start']}-{w['turn_end']}). Found for that "
            f"unit: {near}. Either the replay is of a different game or the grader is blind; "
            f"a FIXED verdict from here would be meaningless.")
    return match[0]


def grade(sit, tr, d1_episodes, p4_violations=()):
    """FIXED = detector silent over the window AND progress restored. Never one alone.

    "Detector" means D-1 for a D1_EPISODE situation and P4 liveness for a P4_STALL. Before
    stage 1b the P4 half did not exist, so the four stall situations were graded by the
    progress clause alone with a vacuously-silent detector clause beside it.
    """
    w = sit["window"]
    uid, lo, hi = w["unit"], w["turn_start"], w["turn_end"]

    # Keys are `turn_start` / `turn_end` -- read from a real episode, not guessed.
    # The first draft filtered on `t_start`/`t_end`, which do not exist, so `.get(...)`
    # returned the defaults, EVERY episode was excluded and `silent` was always True.
    # The detector clause was inert: the exact "mechanism that cannot fail" class this
    # harness exists to prevent, in the harness itself. `check_replay_fidelity()` below
    # is the control that now makes that impossible to ship quietly.
    overlapping = [e for e in d1_episodes
                   if e["unit"] == uid
                   and not (e["turn_end"] < lo or e["turn_start"] > hi)]
    p4_over = [v for v in p4_violations
               if not (v["window_end"] < lo or v["window_start"] > hi)]

    # The clause that applies is the one this situation was frozen under.
    if sit["kind"] == "P4_STALL":
        silent = not p4_over
    else:
        silent = not overlapping

    progressed = had_progress(tr, uid, lo, hi)
    escaped = left_the_cycle(tr, uid, lo, hi, w["cells"])
    # `codex_1` blocker 2026-08-16, finding 1 — ACCEPTED. This was
    #     restored = progressed or escaped
    # which counted "visited any third cell" as restored progress. D-1 detects a TWO-cell
    # A-B-A alternation, so a three-cell no-progress loop evades the detector clause AND
    # satisfied the progress clause: a false FIXED with neither check objecting.
    # The frozen rule is "reaches its target OR produces progress events". Target is NOT
    # evaluable -- the library records no goals (its own README says so) -- so the only
    # honest reading is progress events alone. `escaped` is retained as a REPORTED
    # diagnostic and no longer participates in the verdict.
    restored = progressed

    return {
        "id": sit["id"], "kind": sit["kind"], "unit": uid,
        "window": [lo, hi], "cells": w["cells"],
        "detector_silent": silent,
        "detector_clause": "P4" if sit["kind"] == "P4_STALL" else "D-1",
        "d1_episodes_in_window": len(overlapping),
        "p4_violations_in_window": len(p4_over),
        "progress_events": progressed,
        "left_cycle": escaped,
        "progress_restored": restored,
        # both clauses, never one: quiet-but-stalled is NOT fixed
        "verdict": "FIXED" if (silent and restored) else "NOT_FIXED",
        "why": ("detector silent and progress restored" if (silent and restored)
                else "detector still fires" if not silent
                else "detector quiet but the unit never progressed or left its cycle"),
    }


# --------------------------------------------------------------------------------------


def run_situation(sit, binary, cfg):
    spec = spec_for(sit, cfg)
    ref = fp.make_referee(spec)
    transcript, commands = rt.run_binary_custom(Path(binary), ref, int(cfg["turns"]))
    tr = td.build_trace(transcript, commands)
    d1 = td.detect_d1(tr)
    # STAGE 1b: P4 liveness, using the PANEL'S OWN eval_p4 rather than a second definition
    # of "stalled" written here. `tr_p` is accepted for signature parity and never consulted
    # (fuzz_panel:1831-1838), so passing the candidate trace twice is faithful, not a fudge.
    # `post_ct_state(ref)` supplies the world AFTER the final command set resolves, which is
    # what the post-C_T rule needs to judge turn T at all.
    p4 = fp.eval_p4(tr, tr, int(cfg["liveness_window"]), fp.post_ct_state(ref))
    return tr, d1.get("episodes", []), p4, spec


def compile_candidate(src: Path, workdir: Path) -> Path:
    import semantic_harness as sh
    out = workdir / "cand.bin"
    sh.compile_text(src.read_text(), out, crate="t1_fixture_candidate")
    return out


def run_all(candidate: Path, only=None, verbose=True, baseline=False):
    cfg = json.loads(CONFIG.read_text())
    sits = load_situations(only)
    results = []
    with tempfile.TemporaryDirectory(prefix="t1-fixtures-") as wd:
        binary = compile_candidate(candidate, Path(wd))
        for sit in sits:
            tr, eps, p4, _ = run_situation(sit, binary, cfg)
            if baseline:
                check_p4_fidelity(sit, p4)
                # On the UNMODIFIED resident every D1 situation must reproduce. Under a
                # candidate it must not be required -- curing the episode is the point.
                check_replay_fidelity(sit, eps)
            r = grade(sit, tr, eps, p4)
            results.append(r)
            if verbose:
                mark = "FIXED    " if r["verdict"] == "FIXED" else "NOT FIXED"
                print(f"  {mark} {r['id']}  {r['kind']:<12} "
                      f"turns {r['window'][0]}-{r['window'][1]}  "
                      f"{r['detector_clause']:<4} silent={r['detector_silent']} "
                      f"progress={r['progress_restored']}")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", default=str(RESIDENT))
    ap.add_argument("--only")
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    only = args.only.split(",") if args.only else None
    cand = Path(args.candidate)
    baseline = cand.resolve() == RESIDENT.resolve()
    print(f"candidate: {cand}")
    if baseline:
        print("baseline run: replay fidelity is ENFORCED (every frozen D-1 episode "
              "must reproduce)")
    results = run_all(cand, only, baseline=baseline)
    fixed = [r for r in results if r["verdict"] == "FIXED"]
    print(f"\n{len(fixed)} FIXED / {len(results)} situations")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"candidate": str(cand), "results": results}, indent=1, sort_keys=True) + "\n")
        print(f"wrote {args.json}")
    return 0


def _self_test():
    """The control that matters: the grader must be able to say FIXED on real data."""
    cfg = json.loads(CONFIG.read_text())
    sits = load_situations(["OSC-006"])
    sit = sits[0]
    cases = []

    with tempfile.TemporaryDirectory(prefix="t1-selftest-") as wd:
        binary = compile_candidate(RESIDENT, Path(wd))
        tr, eps, p4, spec = run_situation(sit, binary, cfg)

        r = grade(sit, tr, eps, p4)
        cases.append(("resident is NOT FIXED on its own frozen window",
                      r["verdict"] == "NOT_FIXED", r["why"]))

        # The control the first draft lacked. It must report the detector FIRING -- if this
        # says silent, the clause is inert and every later FIXED is worthless.
        cases.append(("detector clause actually FIRES on the resident (not inert)",
                      r["detector_silent"] is False and r["d1_episodes_in_window"] >= 1,
                      f"episodes in window = {r['d1_episodes_in_window']}"))

        ep = check_replay_fidelity(sit, eps)
        cases.append(("re-run REPRODUCES the frozen episode exactly",
                      ep is not None and ep["cells"] == sit["window"]["cells"],
                      f"unit {ep['unit']} turns {ep['turn_start']}-{ep['turn_end']} "
                      f"k={ep['k']}" if ep else "no match"))

        stall = load_situations(["OSC-033"])[0]
        tr_s, eps_s, p4_s, _ = run_situation(stall, binary, cfg)
        rs = grade(stall, tr_s, eps_s, p4_s)
        cases.append(("P4 clause FIRES on a frozen stall (stage 1b, was inert)",
                      rs["detector_clause"] == "P4" and rs["detector_silent"] is False
                      and rs["p4_violations_in_window"] >= 1,
                      f"P4 violations in window = {rs['p4_violations_in_window']}"))
        cases.append(("frozen stall still grades NOT FIXED on the resident",
                      rs["verdict"] == "NOT_FIXED", rs["why"]))
        # finding 1 control: a detector-quiet THIRD-CELL loop with no progress must NOT pass
        class _StubUnit:
            def __init__(self, cell): self.cell, self.carry = cell, (0, 0, 0, 0, 0, 0)
        class _StubState:
            inventories = [(0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)]
            def plant_at(self, cell): return None
        class _FakeTr:
            """A three-cell loop with NO progress of any kind: carry constant, inventories
            constant, no plant appears or disappears, no DROP/PICK. Everything is stubbed so
            nothing leaks in from the real trace -- the first draft of this control delegated
            to the real one and reported progress=True, which measured nothing."""
            T = 100
            def pos(self, uid, t): return (t % 3, 0)
            def unit(self, uid, t): return _StubUnit((t % 3, 0))
            def cmd_of(self, uid, t): return None
            def state(self, t): return _StubState()
        fake = _FakeTr()
        third = {**sit, "window": {**sit["window"], "turn_start": 1, "turn_end": 30}}
        rf = grade(third, fake, [], [])
        cases.append(("detector-quiet 3-cell loop with no progress is NOT FIXED",
                      rf["verdict"] == "NOT_FIXED",
                      f"left_cycle={rf['left_cycle']} progress={rf['progress_events']}"))

        # finding 2 controls: cells-only and k-only mismatches must both abort
        real_ep = [e for e in eps if e["unit"] == sit["window"]["unit"]][0]
        bad_cells = {**sit, "window": {**sit["window"], "cells": [[9, 9], [8, 8]]}}
        try:
            check_replay_fidelity(bad_cells, eps)
            cases.append(("fidelity aborts on a CELLS-only mismatch", False, "NO ERROR"))
        except HarnessError:
            cases.append(("fidelity aborts on a CELLS-only mismatch", True, "aborted"))
        bad_k = {**sit, "window": {**sit["window"], "k": real_ep["k"] + 7}}
        try:
            check_replay_fidelity(bad_k, eps)
            cases.append(("fidelity aborts on a K-only mismatch", False, "NO ERROR"))
        except HarnessError:
            cases.append(("fidelity aborts on a K-only mismatch", True, "aborted"))

        try:
            check_p4_fidelity({**stall, "window": {**stall["window"],
                                                   "turn_start": 1, "turn_end": 2}}, [])
            cases.append(("P4 fidelity aborts when no stall reproduces", False,
                          "NO ERROR RAISED"))
        except HarnessError as e:
            cases.append(("P4 fidelity aborts when no stall reproduces",
                          "does NOT reproduce" in str(e), str(e)[:55]))

        try:
            check_replay_fidelity({**sit, "window": {**sit["window"], "turn_start": 999,
                                                     "turn_end": 1001}}, eps)
            cases.append(("fidelity check aborts when the episode does not reproduce",
                          False, "NO ERROR RAISED"))
        except HarnessError as e:
            cases.append(("fidelity check aborts when the episode does not reproduce",
                          "does NOT reproduce" in str(e), str(e)[:58]))

        # THE control: same grader, same real trace, a window where the unit is not stuck.
        # Without this the harness could be a constant `NOT_FIXED` and look identical.
        w = sit["window"]
        late = dict(sit)
        late["window"] = dict(w)
        late["window"]["turn_start"] = max(1, w["turn_end"] + 5)
        late["window"]["turn_end"] = min(tr.T, w["turn_end"] + 40)
        r2 = grade(late, tr, eps, p4)
        cases.append(("grader CAN return FIXED on a non-stuck window of the same trace",
                      r2["verdict"] == "FIXED", r2["why"]))

        # a window the unit never leaves its cycle in, with the detector muted by hand,
        # must still be NOT FIXED -- the quiet-but-stalled clause
        r3 = grade(sit, tr, [], p4)
        cases.append(("detector silenced by hand is still NOT FIXED without progress",
                      r3["verdict"] == "NOT_FIXED", r3["why"]))

        # a reconstruction mismatch must abort rather than grade a different game
        bad = json.loads(json.dumps(sit))
        bad["static_map_rows"] = ["#" * len(sit["static_map_rows"][0])] * len(
            sit["static_map_rows"])
        try:
            spec_for(bad, cfg)
            cases.append(("wrong map aborts instead of grading another game", False,
                          "NO ERROR RAISED"))
        except HarnessError as e:
            cases.append(("wrong map aborts instead of grading another game",
                          "DIFFERENT game" in str(e), str(e)[:70]))

    allok = True
    for label, ok, detail in cases:
        print(f"  {'OK  ' if ok else 'BAD '} {label:60} {detail[:60]}")
        allok = allok and ok
    print(f"\nself-test: {len(cases)} cases —",
          "PASS" if allok else "FAIL — the harness cannot be trusted")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
