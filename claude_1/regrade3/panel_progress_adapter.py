#!/usr/bin/env python3
r"""Card `20260822-alpha-progress-regrade` — the ADAPTER, and only the adapter.

## What this file is

Cure alpha's headline on the matched 240-game panel is **D-1 27 -> 9 (healed 18, new 0)** and
**P4 16 -> 0 (healed 16, new 0)**. Those are counts of episodes that stopped firing. They do not
say a troll started working. This file adapts a **panel episode** into the shape the ALREADY
ACCEPTED two-clause predicate consumes, so that the second clause can be asked of alpha.

**The predicate is not defined here and is not modified here.** It is imported from
`claude_1/t1/fixture_harness.py` and called:

    fixture_harness.grade(sit, tr, d1_episodes, p4_violations, identity=...)

Importing is a stronger guarantee than lifting bytes: there is no copy that can drift.
`panel_adapter_controls.py` pins the source of `grade`, `had_progress`, `left_the_cycle` and
`unit_positions` by sha256 anyway, so that an edit to the accepted harness is caught here rather
than silently changing what "progress" means underneath this measurement.

## THE ONE PLACE THIS ADAPTER IS NOT A FAITHFUL RE-USE, STATED FIRST

`grade()` demands an `identity` verdict under the key
`reproduces_the_recorded_episode`, and refuses to grade without one. In the FIXTURE setting that
key means: *this re-run replays the recorded episode* -- proven by the frozen window's command
lines and the frozen board at the window's first turn (`fixture_harness.episode_identity`).

**That question is not askable of a panel candidate arm, and asking it would answer the wrong
thing.** The cure's whole purpose is to make the candidate emit DIFFERENT commands from the base;
`check_window_commands` would therefore reject every changed game by construction, and a
re-grade that rejects exactly the twenty games it exists to measure has measured nothing. This is
the same wall recorded on `20260821-swap-r1-cure`: the identity gate was measured incapable of
returning FIXED on a cure arm, 7 for 7.

So the panel identity question is a DIFFERENT question, and it is the one the card names:

> **WINDOW_ABSENT** -- the base episode's window does not exist in the candidate run, so the
> question cannot be asked of it.

`window_askable()` below answers exactly that: does the candidate run reach the window's last
turn, and is the unit present in it. It is passed to `grade()` in the parameter that gates it,
which keeps `WINDOW_ABSENT` a THIRD outcome that can never be folded into either other bucket --
the identity trap that produced eight false "FIXED on the champion" grades.

**This substitution is the G-1 review object.** It is named here rather than left for a reviewer
to discover, because it is the only place the instrument departs from the accepted one.

## Where each input comes from, and why P4's base column is the floor panel's

Same provenance as the accepted `claude_1/swap1/g2_grade.py`, whose verdict this re-grade does
not restate and does not contradict:

- base D-1 episodes: `detect_d1` on the candidate panel row's PARENT transcript;
- candidate D-1 episodes: `detect_d1` on that row's CANDIDATE transcript;
- base P4 violations: the FLOOR panel row's own candidate arm, where P4 is computed in the full
  accepted mode with `post_state` supplied -- never the reduced `post_state=None` mode;
- candidate P4 violations: the candidate panel row's own P4 violations.

Gate M (`g2_grade.gate_m`) is what makes the fourth line legitimate, and this adapter re-runs it
rather than assuming yesterday's pass.

## P4 has no unit, and the predicate's progress clause does

A panel P4 violation reads `candidate makes no own-inventory/own-cargo progress over turns
42-200`. It is a statement about the **side**, not about a unit; its detail carries no unit id.
`grade()`'s progress clause is unit-scoped (`had_progress(tr, uid, lo, hi)`).

The adapter therefore grades a P4 event **once per own unit** and composes at the event level:
the detector clause is unit-independent, so the event is HEALED_WITH_PROGRESS iff the detector is
silent AND at least one own unit progressed. That composition is P4's own notion of progress --
own-side progress -- and it is done in the ADAPTER; no per-unit verdict is altered and the
predicate is untouched. Every per-unit row is kept in the output so a reviewer can recompute the
composition instead of trusting it.

For a P4 event the "cycle cells" the frozen fixtures carry do not exist. The adapter supplies the
cells the unit actually occupied during the window IN THE BASE RUN, which is the faithful
analogue. `left_cycle` is a REPORTED DIAGNOSTIC ONLY -- codex_1's accepted finding 1 of
2026-08-16 removed it from the verdict -- so this choice cannot move a bucket.

## Buckets

    WINDOW_ABSENT         grade() -> NOT_REPRODUCIBLE_ON_BASE; the question was not askable
    STILL_FIRING          detector still fires over the window; the event did not heal at all
    HEALED_WITH_PROGRESS  detector silent AND progress restored
    QUIET_BUT_STALLED     detector silent, no progress. This is the P1+P2 outcome and it comes
                          off the headline.

STILL_FIRING is not one of the card's three buckets because the card's three partition the
*healed* events. It exists because this adapter grades EVERY base event rather than trusting a
count subtraction to say which ones healed, and the non-healed remainder has to land somewhere
visible. It is also the detector clause's own control: a base event graded against the BASE arm
must come back STILL_FIRING, or the clause is inert.

Import-only module. `panel_regrade.py` runs it; `panel_adapter_controls.py` proves it.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/swap1"):
    sys.path.insert(0, str(REPO / _p))

import trace_detectors as td      # noqa: E402
import fixture_harness as fh      # noqa: E402  -- THE PREDICATE. imported, never redefined.
import g2_grade as g2             # noqa: E402  -- gate M and the panel loader, re-used

CANDIDATE_PACKET = Path("/tmp/claude-1000/swap-g2/games/games.jsonl.gz")
FLOOR_PACKET = Path("/tmp/claude-1000/swap-g2-floor/games/games.jsonl.gz")


class AdapterError(Exception):
    """Anything that would make a bucket mean something other than it says."""


# ---------------------------------------------------------------------------------------
# inputs


def load_panels(cand_gz: Path, floor_gz: Path):
    """Both packets, with GATE M RE-RUN. A non-matched pair is refused, not reported."""
    cand_rows = g2.load(Path(cand_gz))
    floor_rows = g2.load(Path(floor_gz))
    matched, problems = g2.gate_m(cand_rows, floor_rows)
    if not matched:
        raise AdapterError("GATE M FAILED — the panels are not matched; refusing to grade. "
                           + "; ".join(problems[:5]))
    return cand_rows, floor_rows


def traces(cand_row):
    a = cand_row["artifacts"]
    return (td.build_trace(a["parent_transcript"], a["parent_commands"]),
            td.build_trace(a["candidate_transcript"], a["candidate_commands"]))


def d1_episodes(tr):
    return td.detect_d1(tr)["episodes"]


def p4_details(row):
    return [v["detail"] for v in row["violations"] if v["property"] == "P4"]


# ---------------------------------------------------------------------------------------
# the adapter proper: a panel event -> the shape the accepted predicate consumes


def sit_from_d1(map_id, seat, ep):
    """A base-arm D-1 episode as a `sit`. Every field is the detector's own output."""
    return {
        "id": f"{map_id}/s{seat}/D-1@{ep['turn_start']}-{ep['turn_end']}/u{ep['unit']}",
        "kind": "D1_EPISODE",
        "shape": "D-1",
        "window": {"unit": ep["unit"], "turn_start": int(ep["turn_start"]),
                   "turn_end": int(ep["turn_end"]),
                   "cells": [list(c) for c in ep["cells"]], "k": ep["k"]},
    }


def cells_occupied(tr, uid, lo, hi):
    """The cells this unit actually stood on in the window, in the run given."""
    seen = []
    for t in range(lo, min(hi, tr.T) + 1):
        c = tr.pos(uid, t)
        if c is not None and list(c) not in seen:
            seen.append(list(c))
    return seen


def sits_from_p4(map_id, seat, detail, tr_base):
    """A base-arm P4 violation as ONE `sit` PER OWN UNIT — see the module docstring.

    P4's detail names a window and no unit. The per-unit rows are composed at the event level by
    `bucket_p4_event`; nothing here decides a verdict.
    """
    lo, hi = int(detail["window_start"]), int(detail["window_end"])
    out = []
    for uid in tr_base.own_ids:
        cells = cells_occupied(tr_base, uid, lo, hi)
        out.append({
            "id": f"{map_id}/s{seat}/P4@{lo}-{hi}/u{uid}",
            "kind": "P4_STALL",
            "shape": "P4",
            "window": {"unit": uid, "turn_start": lo, "turn_end": hi, "cells": cells, "k": None},
        })
    return out


def window_askable(tr, sit):
    """PANEL identity: does the candidate run CONTAIN the base episode's window?

    Returned under `grade()`'s own key so that a window the candidate run does not contain is
    `NOT_REPRODUCIBLE_ON_BASE` — its own outcome, never FIXED and never NOT_FIXED. Read the
    module docstring: in the panel setting this key does NOT mean "replays the recorded episode",
    and that substitution is the thing G-1 is being asked to rule on.
    """
    w = sit["window"]
    uid, lo, hi = w["unit"], w["turn_start"], w["turn_end"]
    reasons = []
    if tr.T < hi:
        reasons.append(f"the candidate run ends at turn {tr.T}, before the base window's last "
                       f"turn {hi}; the window is not contained in this run")
    present = [t for t in range(lo, min(hi, tr.T) + 1) if tr.unit(uid, t) is not None]
    if not present:
        reasons.append(f"unit {uid} is absent from the candidate run on every turn of "
                       f"{lo}-{min(hi, tr.T)}")
    return {"reproduces_the_recorded_episode": not reasons, "reasons": reasons,
            "panel_identity": {"candidate_horizon": tr.T, "window": [lo, hi],
                               "unit_present_turns": len(present)},
            "window_commands": None, "entry_state": None}


def bucket_of(graded):
    """The card's buckets, from a verdict the predicate produced. No re-derivation."""
    if graded["verdict"] == "NOT_REPRODUCIBLE_ON_BASE":
        return "WINDOW_ABSENT"
    if not graded["detector_silent"]:
        return "STILL_FIRING"
    return "HEALED_WITH_PROGRESS" if graded["progress_restored"] else "QUIET_BUT_STALLED"


def grade_sit(sit, tr_cand, cand_d1, cand_p4):
    """One call into the ACCEPTED predicate, with the panel identity verdict supplied."""
    ident = window_askable(tr_cand, sit)
    graded = fh.grade(sit, tr_cand, cand_d1, cand_p4, identity=ident)
    graded["panel_identity"] = ident["panel_identity"]
    graded["identity_reasons"] = graded.get("identity_reasons", ident["reasons"])
    graded["bucket"] = bucket_of(graded)
    graded["shape"] = sit["shape"]
    return graded


def bucket_p4_event(unit_rows):
    """Compose the per-unit rows of ONE P4 event into ONE event bucket.

    The detector clause is unit-independent (a P4 violation is a property of the side), so only
    the progress clause is composed, and it is composed the way P4 itself states it: own-side
    progress. Documented in the module docstring; the per-unit rows are all retained.
    """
    if not unit_rows:
        raise AdapterError("a P4 event produced no per-unit rows; the game has no own units, "
                           "which cannot be graded and must not be silently bucketed")
    askable = [r for r in unit_rows if r["bucket"] != "WINDOW_ABSENT"]
    if not askable:
        return "WINDOW_ABSENT"
    if any(r["bucket"] == "STILL_FIRING" for r in askable):
        return "STILL_FIRING"
    return ("HEALED_WITH_PROGRESS" if any(r["progress_restored"] for r in askable)
            else "QUIET_BUT_STALLED")


def grade_game(map_id, seat, cand_row, floor_row, arm="candidate"):
    """Every base event of this game, graded against `arm`. Returns event rows.

    `arm="base"` grades the base events against the BASE arm — the detector clause's control,
    where every event must come back STILL_FIRING.
    """
    tr_base, tr_cand = traces(cand_row)
    tr = tr_base if arm == "base" else tr_cand
    if arm == "base":
        cand_d1, cand_p4 = d1_episodes(tr_base), p4_details(floor_row)
    else:
        cand_d1, cand_p4 = d1_episodes(tr_cand), p4_details(cand_row)

    events = []
    for ep in d1_episodes(tr_base):
        sit = sit_from_d1(map_id, seat, ep)
        g = grade_sit(sit, tr, cand_d1, cand_p4)
        events.append({"map_id": map_id, "seat": seat, "shape": "D-1", "event_id": sit["id"],
                       "window": [sit["window"]["turn_start"], sit["window"]["turn_end"]],
                       "unit": sit["window"]["unit"], "cells": sit["window"]["cells"],
                       "bucket": g["bucket"], "unit_rows": [g]})
    for detail in p4_details(floor_row):
        sits = sits_from_p4(map_id, seat, detail, tr_base)
        rows = [grade_sit(s, tr, cand_d1, cand_p4) for s in sits]
        lo, hi = int(detail["window_start"]), int(detail["window_end"])
        events.append({"map_id": map_id, "seat": seat, "shape": "P4",
                       "event_id": f"{map_id}/s{seat}/P4@{lo}-{hi}",
                       "window": [lo, hi], "unit": None, "cells": None,
                       "bucket": bucket_p4_event(rows), "unit_rows": rows,
                       "p4_why": detail.get("why")})
    return events
