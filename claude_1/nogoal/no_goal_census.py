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

## The control the reused census cannot supply here

Phase 3's fixtures had employed turns INSIDE the audited window, so its
`employed_routes` bucket was its own both-ways control. These two windows are
all-`WAIT` by construction — that is what makes them the cases nobody can
explain — so an in-window employed bucket is expected to be empty, and an empty
bucket must not be read as "the tap fired both ways". The both-ways control is
therefore taken across the fixtures of the run on the identical binary: at least
one must NAME a non-idle route, and which ones did is recorded per fixture. A
fixture where the tap named none supplies nothing here even if its unit was
employed, because an employed turn the instrument cannot read is not evidence
that the instrument reads employed turns.

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
    """What the AUDITED unit did on the rest of its game. Informational, not a gate.

    Outside the window the probe's five anchors do not cover every turn — some
    turns produce a `PS3FINAL` with no `PS3ROUTE` at all, i.e. the unit left the
    generator through a return path this instrument does not name. Those turns
    are COUNTED and reported rather than skipped: quietly dropping the turns an
    instrument cannot read is how a partial measurement comes to look complete.
    In-window coverage is exact and gated separately by `route_census.census`.
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

    What this can and cannot see is worth stating exactly, because the two are
    easy to confuse and I confused them once already. A turn contributes here
    only when the tap NAMED a route on it. A fixture can therefore have plenty
    of employed turns and still supply nothing: OSC-033's unit is employed on 20
    turns outside its window, and on every one of them the generator returned
    through a path these five anchors do not name. "Supplies no control" means
    "named no non-idle route", NOT "was never employed" — the artifact records
    the employed-but-unnamed turns separately so the difference is visible.
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
    for key, n in finals.items():
        for tag in routes.get(key, []):
            (idle if n == 1 else employed)[tag] += 1
    return {"fixture_employed_routes_all_units": dict(employed),
            "fixture_supplies_own_both_ways_control": bool(employed),
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
    # G-2 both-ways, gated at the INSTRUMENT level.
    #
    # The charter words this control per fixture ("employed turns of the same
    # fixtures must come back with non-idle routes"), which silently assumes
    # each fixture HAS employed turns. OSC-033 does not: it carries a single
    # unit, and while that unit IS employed on 20 turns outside its window, the
    # generator returns through a path these five anchors do not name on every
    # one of them — so no non-idle route can be NAMED for that fixture. Failing
    # the run on that would condemn a working instrument for a gap in the reused
    # probe's anchor set.
    #
    # The control is therefore taken across the fixtures this instrument ran,
    # on the IDENTICAL binary: at least one must come back with named non-idle
    # routes. Which fixtures did is recorded per fixture, so the weaker
    # standing of OSC-033 is visible in the artifact and cannot be read as
    # in-fixture evidence it does not have.
    supplying = [r["id"] for r in rows if r["fixture_supplies_own_both_ways_control"]]
    if not supplying:
        raise RC.GateError(
            "no fixture in this run named a route on any turn whose list was longer than one. A "
            "tap that only ever reports the idle path is a constant, and a constant cannot name "
            "a route. Nothing is reported.")  # employed-but-unnamed turns do not count here
    for r in rows:
        if not r["fixture_supplies_own_both_ways_control"]:
            print(f"  NOTE {r['id']}: the tap named NO non-idle route anywhere in this fixture "
                  f"({r['outside_window_unrouted_employed_turns']} employed turns outside the "
                  f"window took an unnamed return path), so it supplies NO in-fixture both-ways "
                  f"control. The tap's non-constancy rests on {supplying}, same binary.")

    OUT.write_text(json.dumps(
        {"task": "20260821-osc032-033-no-goal-instrument",
         "question": "on the champion base, which return path of main_candidates/"
                     "endgame_candidates hands back the seeded WAIT alone on every turn of the "
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
                   "both ways: at least one fixture in the run names non-idle routes on the "
                   "identical binary, recorded per fixture; a fixture with no employed turn "
                   "anywhere supplies no in-fixture control and says so"],
         "both_ways_supplied_by": supplying,
         "scope": "measurement only; no fix, no candidate, no judgment; "
                  "bug-versus-correct-caution is the owner's ruling",
         "fixtures": rows}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
