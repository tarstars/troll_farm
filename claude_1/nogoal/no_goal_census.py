#!/usr/bin/env python3
r"""OSC-032/033 — the generator names its own silence, on the champion base.

Task `20260821-osc032-033-no-goal-instrument`. The owner's question, in plain
words: in these two recorded cases a troll stood still for 110 and 143 turns
while the instrument measured that work was available on every one of those
turns, and nobody assigned it a job. **Why was no goal ever assigned?**

**Measurement only.** Nothing here proposes a change, names a bug, or judges
whether the route it finds is wrong. Bug-versus-correct-caution is the OWNER's
ruling afterwards and the deliverable must not pre-empt it.

## Reuse, not reinvention

The charter is explicit that Phase 3 of `20260820-pair-selector-anti-benching`
already built this instrument and that a new one is justified only where the
existing one provably cannot answer. It can answer, and nothing needed
rewriting: all five of `make_route_probe.py`'s anchors match the champion
source `547fa706...` EXACTLY ONCE, unmodified. So this file supplies the
subject list and the controls, and imports the parser, the census and every
gate from the Phase-3 modules:

  * `route_census.parse` / `.census` — the generator rows and the per-fixture
    histogram, including its coverage, one-route-per-turn and cross-probe gates;
  * `gate_bench.parse` / `.check_coverage` — the selector tap and its coverage;
  * `coverage.check_parity` — both probes' command streams against the
    uninstrumented champion.

## The both-ways control, per fixture (revised after G-1)

Phase 3's fixtures had employed turns INSIDE the audited window, so its
`employed_routes` bucket was its own both-ways control. These two windows are
all-`WAIT` by construction — that is what makes them the cases nobody can
explain — so an in-window employed bucket is expected to be empty, and an empty
bucket must not be read as "the tap fired both ways". The control therefore has
to come from the employed turns each fixture has OUTSIDE its window.

The first version of this file could not take it that way and weakened the gate
instead, from "each fixture names a non-idle route" to "at least one fixture in
the run does". codex_1 refused that at G-1 (2026-08-21) and was right to: which
control flow a fixture takes is the very thing being classified, so OSC-032
proving non-constancy cannot stand in for OSC-033, identical binary or not.

The real defect was in the reused probe, not in the charter. `commands()`
chooses its generator from FIVE branches and Phase 3's five anchors tapped only
`main_candidates` and `endgame_candidates`. Turns 1-34 of BOTH games run the
`early` branch, and all 34 in each produced a `PS3FINAL` with no `PS3ROUTE` —
including every one of OSC-033's 20 employed turns. Every unrouted turn in
either fixture was `early=true` and no other flag combination appeared, so the
gap had exactly one cause. `make_route_probe.py` now carries two more anchors,
`early_candidates/entry` and `early_candidates/tail`, applied to the champion
subject only; the five Phase-3 anchors are untouched and still match exactly
once each.

With the early branch named, coverage is exact over the WHOLE game rather than
only in-window, so both gates below are now real: every fixture supplies its own
both-ways control, and an employed-but-unnamed turn fails the run instead of
being counted and excused.

Run:  python3 claude_1/nogoal/no_goal_census.py
"""
from __future__ import annotations

import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker2"):
    sys.path.insert(0, str(REPO / p))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import gate_bench as GB         # noqa: E402
import route_census as RC       # noqa: E402

FIXTURES = ["OSC-032", "OSC-033"]
ROUTE_ARM = "door1-champion"    # the champion + the generator tap
SEL_ARM = "door1-base"          # the champion + the Phase-2 selector tap
ROUTE_MANIFEST = HERE / "route-probe-manifest-2026-08-21.json"
SEL_MANIFEST = REPO / "claude_1/picker2/probe-manifest-2026-08-20.json"
CAUSE_TABLE = REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json"
OUT = HERE / "no-goal-census-2026-08-21.json"


def unit_outside_window(sid, rt, uid, window):
    """What the AUDITED unit did on the rest of its game — and, since G-1, a GATE.

    The unrouted counters stay in the artifact because quietly dropping the
    turns an instrument cannot read is how a partial measurement comes to look
    complete. They are no longer expected to be non-zero: with the `early`
    anchors added, the seven anchors name every return path of every generator
    `commands()` can call, so any unrouted turn means a route this instrument
    still cannot see. `main` gates them at zero. In-window coverage remains
    exact and gated separately by `route_census.census`.
    """
    lo, hi = window
    idle, employed = collections.Counter(), collections.Counter()
    unrouted_idle = unrouted_employed = 0
    for turn, rec in sorted(rt.items()):
        if lo <= turn <= hi or rec["final"] is None:
            continue
        is_idle = rec["final"]["n"] == 1
        if len(rec["routes"]) > 1:
            raise RC.GateError(
                f"{sid} turn {turn}: {len(rec['routes'])} route rows for unit {uid} outside the "
                f"window — a unit takes ONE return path per turn, so more than one row means the "
                f"tap is double-counting and no route may be reported.")
        if not rec["routes"]:
            if is_idle:
                unrouted_idle += 1
            else:
                unrouted_employed += 1
            continue
        r = rec["routes"][0]
        (idle if is_idle else employed)[f"{r['fn']}:{r['route']}"] += 1
    return {"outside_window_idle_routes": dict(idle),
            "outside_window_employed_routes": dict(employed),
            "outside_window_unrouted_idle_turns": unrouted_idle,
            "outside_window_unrouted_employed_turns": unrouted_employed,
            "audited_unit_employed_anywhere_in_game": bool(employed or unrouted_employed)}


def fixture_both_ways(sid, rerr):
    """G-2's both-ways control: the tap is not a constant, measured per FIXTURE.

    Counted across ALL units, which is what the charter says ("employed turns
    of the same fixtures must come back with non-idle routes") rather than
    across the audited unit alone.

    A turn contributes here only when the tap NAMED a route on it, so the two
    ways a fixture can fail this control are kept apart and both reported:
    `fixture_employed_turns_unnamed` counts turns whose list was longer than one
    and which produced no route row at all. Before G-1 that counter stood at 20
    for OSC-033 — an employed turn the instrument cannot read is not evidence
    that the instrument reads employed turns, and `main` now fails on it rather
    than recording it as an excused omission.
    """
    finals, routes = {}, {}
    for line in rerr.splitlines():
        m = RC.RE_FINAL.match(line)
        if m:
            finals[(int(m.group(1)), int(m.group(2)))] = int(m.group(3))
            continue
        m = RC.RE_ROUTE.match(line)
        if m:
            routes.setdefault((int(m.group(1)), int(m.group(2))), []).append(
                f"{m.group(3)}:{m.group(4)}")
    employed, idle = collections.Counter(), collections.Counter()
    unnamed_employed = unnamed_idle = 0
    multi = []
    for key, n in finals.items():
        tags = routes.get(key, [])
        if len(tags) > 1:
            multi.append((key, tags))
        if not tags:
            if n == 1:
                unnamed_idle += 1
            else:
                unnamed_employed += 1
        for tag in tags:
            (idle if n == 1 else employed)[tag] += 1
    if multi:
        unit, turn = multi[0][0]
        raise RC.GateError(
            f"{sid} unit {unit} turn {turn}: {len(multi[0][1])} route rows ({multi[0][1]}) for a "
            f"single turn, and {len(multi)} such turns in the fixture. A unit takes ONE return "
            f"path per turn, so more than one row means the tap double-counts and no route may "
            f"be reported.")
    return {"fixture_employed_routes_all_units": dict(employed),
            "fixture_supplies_own_both_ways_control": bool(employed),
            "fixture_employed_turns_unnamed": unnamed_employed,
            "fixture_idle_turns_unnamed": unnamed_idle,
            "fixture_idle_routes_all_units": dict(idle),
            "fixture_units_seen": len({u for u, _ in finals})}


def main():
    units = {r["situation"]: r["unit"]
             for r in json.loads(CAUSE_TABLE.read_text())["table"]}
    rman = json.loads(ROUTE_MANIFEST.read_text())[ROUTE_ARM]
    sman = json.loads(SEL_MANIFEST.read_text())[SEL_ARM]
    if rman["source_sha256"] != sman["source_sha256"]:
        raise RC.GateError(
            f"the two probes are not built from the same subject: route probe on "
            f"{rman['source_sha256'][:12]}, selector probe on {sman['source_sha256'][:12]}. "
            f"Cross-probe agreement between different sources would be meaningless.")
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(FIXTURES)}
    rows = []
    with tempfile.TemporaryDirectory(prefix="nogoal-") as wd:
        wd = Path(wd)
        for d in ("p", "r", "s"):
            (wd / d).mkdir()
        print(f"compiling champion {rman['source_sha256'][:12]} + two taps ...")
        plain = H.compile_candidate(REPO / rman["source"], wd / "p")
        rprobe = H.compile_candidate(REPO / rman["probe"], wd / "r")
        sprobe = H.compile_candidate(REPO / sman["probe"], wd / "s")
        for sid in FIXTURES:
            sit, uid = sits[sid], units[sid]
            rerr = C.check_parity(sit, cfg, plain, rprobe)   # gate: route probe only prints
            serr = C.check_parity(sit, cfg, plain, sprobe)   # gate: selector probe only prints
            rt = RC.parse(rerr, uid)
            sel_turns = GB.parse(serr)
            GB.check_coverage(sid, sit, sel_turns)
            row = RC.census(sid, sit, uid, rt, sel_turns)
            row.update(unit_outside_window(
                sid, rt, uid,
                (sit["window"]["turn_start"], sit["window"]["turn_end"])))
            row.update(fixture_both_ways(sid, rerr))
            rows.append(row)
            print(f"  {sid}  unit {uid}  window {row['window']}  "
                  f"idle {row['idle_turns']}/{row['turns']}")
            print(f"      idle_routes     {row['idle_routes']}")
            print(f"      employed(in)    {row['employed_routes']}")
            print(f"      employed(out)   {row['outside_window_employed_routes']}")
            print(f"      both-ways       {row['fixture_employed_routes_all_units']} "
                  f"over {row['fixture_units_seen']} units")
            for k, v in row["idle_predicates"].items():
                print(f"      preds     {k}  x{v}")
            for k, v in row["idle_route_detail"].items():
                print(f"      detail    {k}  x{v}")
            for k, v in row["idle_discarded_candidates"].items():
                print(f"      DISCARDED {k}  x{v}")
    # G-2 both-ways, gated PER FIXTURE, as the charter words it.
    #
    # The first delivery weakened this to an instrument-level gate (">=1 fixture
    # names a non-idle route") because OSC-033 could name none. codex_1 refused
    # that at G-1 and the refusal was correct: fixture-dependent control flow is
    # the thing being classified, so one fixture's non-constancy is not the
    # other's control even on the identical binary. The repair was to the probe,
    # not to the gate — see the module docstring.
    #
    # Three separate failures are checked, because "no control" has three causes
    # and lumping them would hide which one fired:
    #   (a) the fixture named no non-idle route at all -> the tap may be a constant;
    #   (b) the fixture HAS employed turns the tap could not name -> coverage hole;
    #   (c) the audited unit has unrouted turns of either kind -> same hole, per unit.
    failures = []
    for r in rows:
        if not r["fixture_supplies_own_both_ways_control"]:
            failures.append(
                f"{r['id']}: the tap named NO non-idle route anywhere in this fixture, so the "
                f"fixture supplies no both-ways control and the tap cannot be shown to be "
                f"anything but a constant on it.")
        if r["fixture_employed_turns_unnamed"]:
            failures.append(
                f"{r['id']}: {r['fixture_employed_turns_unnamed']} employed turns produced no "
                f"route row. An employed turn the instrument cannot read is not evidence that "
                f"the instrument reads employed turns; it may not satisfy the both-ways gate.")
        if r["fixture_idle_turns_unnamed"]:
            failures.append(
                f"{r['id']}: {r['fixture_idle_turns_unnamed']} idle turns produced no route row, "
                f"so the idle side of this fixture is not fully named either.")
        unrouted = (r["outside_window_unrouted_employed_turns"]
                    + r["outside_window_unrouted_idle_turns"])
        if unrouted:
            failures.append(
                f"{r['id']}: the audited unit has {unrouted} turns outside its window with no "
                f"route row, so full-game coverage for the audited unit is not exact.")
    if failures:
        raise RC.GateError(
            "the both-ways / coverage control failed and NOTHING is reported:\n  "
            + "\n  ".join(failures))
    supplying = [r["id"] for r in rows if r["fixture_supplies_own_both_ways_control"]]
    for r in rows:
        print(f"  both-ways {r['id']}: OWN control, "
              f"{sum(r['fixture_employed_routes_all_units'].values())} named employed turns, "
              f"0 unnamed")

    OUT.write_text(json.dumps(
        {"task": "20260821-osc032-033-no-goal-instrument",
         "question": "on the champion base, which return path of main_candidates/"
                     "endgame_candidates/early_candidates hands back the seeded WAIT alone on "
                     "every turn of the "
                     "OSC-032 and OSC-033 windows, and what did the generator see when it did?",
         "base": {"name": ROUTE_ARM, "source": rman["source"],
                  "source_sha256": rman["source_sha256"],
                  "note": "champion of record, Door-1 pure deletion, KEPT by the owner "
                          "2026-08-21; diagnostic copy only, no candidate, no Arena"},
         "probes": {"generator": rman["probe"], "generator_sha256": rman["probe_sha256"],
                    "selector": sman["probe"], "selector_sha256": sman["probe_sha256"]},
         "gates": ["parity vs the uninstrumented champion, for BOTH probes",
                   "exactly one PS3FINAL row per window turn for the audited unit",
                   "PS3FINAL n == the selector probe's PS2CAND row count, same unit and turn",
                   "exactly one route row per unit per turn",
                   "both ways, PER FIXTURE: every fixture names non-idle routes on its own "
                   "employed turns, and an employed-but-unnamed turn fails the run instead of "
                   "satisfying the gate",
                   "full-game route coverage: every PS3FINAL turn of every unit carries exactly "
                   "one PS3ROUTE, so no generator return path is unobservable"],
         "both_ways_supplied_by": supplying,
         "scope": "measurement only; no fix, no candidate, no judgment; "
                  "bug-versus-correct-caution is the owner's ruling",
         "fixtures": rows}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
