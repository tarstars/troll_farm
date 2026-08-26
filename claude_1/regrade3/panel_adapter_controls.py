#!/usr/bin/env python3
r"""Card `20260822-alpha-progress-regrade`, G-1 — the controls for the panel adapter.

G-1 is instrument-first: the adapter is reviewed BEFORE any result from it is a finding. This
file is the evidence, and it is built to be capable of failing.

## C1 — the predicate is the accepted one, unmodified

`panel_progress_adapter` IMPORTS `claude_1/t1/fixture_harness.py` and calls `grade` on it. There
is no copy, so there is nothing to drift. C1 pins it anyway: the sha256 of the harness file and
of `inspect.getsource` for each of the four functions the measurement rides on. If the accepted
harness is edited, this control fails here instead of quietly changing what "progress" means
under a published number.

## C2 — the predicate refuses to grade without an identity verdict

`grade(..., identity=None)` must raise. A caller that forgets the gate must not be able to
obtain a verdict.

## C3 — WINDOW_ABSENT is reachable and is its OWN outcome

Two constructed cases on real panel traces: a window past the candidate run's last turn, and a
window whose unit is absent from the candidate run. Both must come back `WINDOW_ABSENT`, never
`QUIET_BUT_STALLED` (which is what folding identity into "silent" would produce, and it is the
trap that produced eight false "FIXED on the champion" grades).

## C4 — the detector clause is LIVE, on all 240 games

Every base event of every game, graded against the BASE arm. All must come back `STILL_FIRING`.
This is the control against the inert-clause failure the harness itself once shipped, where a
mis-keyed filter made `silent` unconditionally True. It uses the 210 unchanged games ONCE, as a
control; it does not re-grade them.

## C5 — BOTH WAYS, on the card's own named cases, and the fixture identity gate that refuses them

The card names P1+P2's fixtures as the two-way control: OSC-004/013/017 quiet-but-stalled,
OSC-034 healed with progress.

**Observed today, not recalled:** run through `fixture_harness` unchanged, the cure arm
`claude_1/picker2/candidate-cureC-p1p2.rs` returns `NOT_REPRODUCIBLE_ON_BASE` on all four. The
fixture identity gate compares the frozen window's command lines, and a cure exists to change
them. That is the wall this adapter's panel identity replaces, and C5 measures it rather than
citing it.

C5 then does what the card actually asks: it puts those same four fixtures through **the
adapter's** identity question -- `window_askable`, "does this run contain the window" -- and then
through the accepted predicate and the adapter's bucketer. The ruled outcome must reappear:
three `QUIET_BUT_STALLED`, one `HEALED_WITH_PROGRESS`. A bucketer that cannot produce both is
not evidence when it later produces one.

Run:  python3 claude_1/regrade3/panel_adapter_controls.py
"""
from __future__ import annotations

import hashlib
import inspect
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
import panel_progress_adapter as A     # noqa: E402
import fixture_harness as fh           # noqa: E402  (path set by the adapter)

HARNESS = REPO / "claude_1/t1/fixture_harness.py"
HARNESS_SHA256 = "6fd8f2b3284fbe19e3009b670a957e754d6cebb69747c1f07e72629b0bc470cf"
PINNED = {
    "grade": "eeaa55a35da4cabe806d887f973ec28c7988e6cfff60ffdd3e88acc885fa996b",
    "had_progress": "c184f0c62cf5bc3f1e11b64e04eb911c6ca1d0e47979ed361316a1bdf760430f",
    "left_the_cycle": "49de1289cf12a6a02a2274d2f404a8bd71294ca2a12704c46a00318c8b4832a4",
    "unit_positions": "da1af87f74aac82b57914a5ac5bda05b6db7939f56efea32953e052dbbd2c90e",
}
CURE_ARM = REPO / "claude_1/picker2/candidate-cureC-p1p2.rs"
CONTROL_FIXTURES = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
RULED = {"OSC-004": "QUIET_BUT_STALLED", "OSC-013": "QUIET_BUT_STALLED",
         "OSC-017": "QUIET_BUT_STALLED", "OSC-034": "HEALED_WITH_PROGRESS"}
OUT = HERE / "panel-adapter-controls-2026-08-22.json"


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha256_src(fn):
    return hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()


def c1_predicate_pinned():
    got = {n: sha256_src(getattr(fh, n)) for n in PINNED}
    return {"control": "C1 predicate imported from the accepted harness, unmodified",
            "harness": str(HARNESS.relative_to(REPO)),
            "harness_sha256": sha256_file(HARNESS),
            "harness_sha256_matches_pin": sha256_file(HARNESS) == HARNESS_SHA256,
            "function_source_sha256": got,
            "function_source_matches_pin": {n: got[n] == PINNED[n] for n in PINNED},
            "grade_is_the_imported_object": A.fh.grade is fh.grade,
            "adapter_defines_no_grade": not hasattr(A, "grade")}


def c2_identity_is_mandatory():
    sit = {"id": "C2", "kind": "D1_EPISODE", "shape": "D-1",
           "window": {"unit": 0, "turn_start": 1, "turn_end": 2, "cells": [], "k": 2}}
    try:
        fh.grade(sit, None, [], (), None)
        return {"control": "C2 grade() refuses without an identity verdict", "refused": False}
    except fh.HarnessError as exc:
        return {"control": "C2 grade() refuses without an identity verdict", "refused": True,
                "error": str(exc)[:160]}


def c3_window_absent(cand_rows, floor_rows):
    key = sorted(cand_rows)[0]
    tr_base, tr_cand = A.traces(cand_rows[key])
    cand_d1, cand_p4 = A.d1_episodes(tr_cand), A.p4_details(cand_rows[key])
    cases = []
    past = {"id": "C3-past-horizon", "kind": "D1_EPISODE", "shape": "D-1",
            "window": {"unit": tr_cand.own_ids[0], "turn_start": tr_cand.T + 5,
                       "turn_end": tr_cand.T + 20, "cells": [], "k": 2}}
    absent_uid = max(tr_cand.own_ids) + 999
    absent = {"id": "C3-absent-unit", "kind": "D1_EPISODE", "shape": "D-1",
              "window": {"unit": absent_uid, "turn_start": 1,
                         "turn_end": min(10, tr_cand.T), "cells": [], "k": 2}}
    for sit in (past, absent):
        g = A.grade_sit(sit, tr_cand, cand_d1, cand_p4)
        cases.append({"case": sit["id"], "bucket": g["bucket"], "verdict": g["verdict"],
                      "reasons": g["identity_reasons"]})
    return {"control": "C3 WINDOW_ABSENT reachable and never folded",
            "game": {"map_id": key[0], "seat": key[1]}, "cases": cases,
            "both_window_absent": all(c["bucket"] == "WINDOW_ABSENT" for c in cases)}


def c4_detector_clause_live(cand_rows, floor_rows):
    buckets, offenders = {}, []
    n = 0
    for key in sorted(cand_rows):
        for e in A.grade_game(key[0], key[1], cand_rows[key], floor_rows[key], arm="base"):
            n += 1
            buckets[e["bucket"]] = buckets.get(e["bucket"], 0) + 1
            if e["bucket"] != "STILL_FIRING":
                offenders.append({"event_id": e["event_id"], "bucket": e["bucket"]})
    return {"control": "C4 detector clause live: every base event, graded against the BASE arm, "
                       "must still fire",
            "games": len(cand_rows), "base_events": n, "buckets": buckets,
            "offenders": offenders[:20],
            "all_still_firing": not offenders}


def c5_both_ways():
    """The card's named fixtures, twice: through the fixture gate, then through the adapter's."""
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(CONTROL_FIXTURES)
    fixture_gate, adapter_gate = [], []
    with tempfile.TemporaryDirectory(prefix="regrade3-c5-") as wd:
        binary = fh.compile_candidate(CURE_ARM, Path(wd))
        for sit in sits:
            tr, eps, p4, _, command_lines = fh.run_situation_ex(sit, binary, cfg)
            ident = fh.episode_identity(sit["id"], sit, tr, command_lines)
            r = fh.grade(sit, tr, eps, p4, ident)
            fixture_gate.append({"id": sit["id"], "verdict": r["verdict"],
                                 "reasons": r.get("identity_reasons", [])[:1]})
            psit = dict(sit)
            psit["shape"] = "P4" if sit["kind"] == "P4_STALL" else "D-1"
            g = A.grade_sit(psit, tr, eps, p4)
            adapter_gate.append({"id": sit["id"], "bucket": g["bucket"],
                                 "detector_silent": g.get("detector_silent"),
                                 "progress_restored": g.get("progress_restored"),
                                 "ruled": RULED[sit["id"]],
                                 "agrees": g["bucket"] == RULED[sit["id"]]})
    got = {r["bucket"] for r in adapter_gate}
    return {"control": "C5 both ways on the card's named fixtures",
            "cure_arm": str(CURE_ARM.relative_to(REPO)),
            "through_the_FIXTURE_identity_gate": fixture_gate,
            "fixture_gate_refuses_the_cure_arm":
                all(r["verdict"] == "NOT_REPRODUCIBLE_ON_BASE" for r in fixture_gate),
            "through_the_ADAPTER_identity_question": adapter_gate,
            "reproduces_the_ruled_buckets": all(r["agrees"] for r in adapter_gate),
            "fired_both_ways": {"HEALED_WITH_PROGRESS", "QUIET_BUT_STALLED"} <= got}


def main():
    cand_rows, floor_rows = A.load_panels(A.CANDIDATE_PACKET, A.FLOOR_PACKET)
    out = {"card": "20260822-alpha-progress-regrade", "gate": "G-1",
           "controls": [c1_predicate_pinned(), c2_identity_is_mandatory(),
                        c3_window_absent(cand_rows, floor_rows),
                        c4_detector_clause_live(cand_rows, floor_rows),
                        c5_both_ways()]}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    for c in out["controls"]:
        print(json.dumps({k: v for k, v in c.items()
                          if k in ("control",) or isinstance(v, (bool, int))}, indent=None))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
