#!/usr/bin/env python3
r"""OSC-032/033 G-3 — the per-turn route table.

Task `20260821-osc032-033-no-goal-instrument`, gate G-3. The instrument and its
six gates were reviewed and ACCEPTED_FOR_G3 by codex_1 on 2026-08-21
(`codex_1/reviews/osc032-033-no-goal-instrument-g1-revision-review-2026-08-21.md`).
This file adds NO tap and NO gate. It is a reporter over the accepted probe:
where `no_goal_census.py` writes the per-fixture histogram, this writes the row
the charter's G-3 asks for by name — one row per unit per turn, every turn of
both full games, with the route the generator actually returned through.

**Measurement only.** No fix, no candidate, no judgment, no class-wide claim.
Bug-versus-correct-caution is the OWNER's ruling afterwards.

Why a separate file rather than more output from the census: the census is the
G-1/G-2 artifact codex_1 reviewed, and a later gate must not edit an accepted
instrument to produce its own deliverable. Same reason the champion subject was
added opt-in rather than by rewriting task 20260820's manifest.

Run:  python3 claude_1/nogoal/route_table.py
"""
from __future__ import annotations

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
import route_census as RC       # noqa: E402
import no_goal_census as NG     # noqa: E402

OUT = HERE / "route-table-2026-08-21.json"


def rows_for(sid, rerr, window):
    """Every (unit, turn) the tap saw, with its one route. Gated, not trusted."""
    finals, mains, routes = {}, {}, {}
    for line in rerr.splitlines():
        m = RC.RE_FINAL.match(line)
        if m:
            finals[(int(m.group(1)), int(m.group(2)))] = {
                "n": int(m.group(3)), "endgame": m.group(4) == "true",
                "early": m.group(5) == "true", "committed": m.group(6) == "true",
                "train_now": m.group(7) == "true"}
            continue
        m = RC.RE_MAIN.match(line)
        if m:
            mains[(int(m.group(1)), int(m.group(2)))] = {
                "carried": int(m.group(3)), "free_cap": int(m.group(4)),
                "safe_regen": m.group(5) == "true", "idle_regen": m.group(6) == "true"}
            continue
        m = RC.RE_ROUTE.match(line)
        if m:
            routes.setdefault((int(m.group(1)), int(m.group(2))), []).append(
                (f"{m.group(3)}:{m.group(4)}", m.group(5).strip()))
    lo, hi = window
    out = []
    for (uid, turn), fin in sorted(finals.items()):
        tags = routes.get((uid, turn), [])
        if len(tags) != 1:
            raise RC.GateError(
                f"{sid} unit {uid} turn {turn}: {len(tags)} route rows, expected exactly 1. "
                f"The accepted instrument gates full-game coverage at 200/200; a table built "
                f"from anything else would report a route the run did not measure.")
        row = {"unit": uid, "turn": turn, "route": tags[0][0],
               "n": fin["n"], "idle": fin["n"] == 1,
               "in_window": lo <= turn <= hi,
               "branch": ("committed" if fin["committed"] else
                          "endgame" if fin["endgame"] else
                          "early" if fin["early"] else "main")}
        if tags[0][1]:
            row["detail"] = tags[0][1]
        if (uid, turn) in mains:
            row["preds"] = mains[(uid, turn)]
        out.append(row)
    return out


def runs(rows):
    """Contiguous same-route spans — the per-turn table without 200 identical lines."""
    out = []
    for r in rows:
        if out and out[-1]["route"] == r["route"] and out[-1]["idle"] == r["idle"] \
                and out[-1]["unit"] == r["unit"] and out[-1]["turn_end"] == r["turn"] - 1:
            out[-1]["turn_end"] = r["turn"]
            out[-1]["turns"] += 1
        else:
            out.append({"unit": r["unit"], "turn_start": r["turn"], "turn_end": r["turn"],
                        "turns": 1, "route": r["route"], "idle": r["idle"],
                        "in_window": r["in_window"]})
    return out


def main():
    units = {r["situation"]: r["unit"]
             for r in json.loads(NG.CAUSE_TABLE.read_text())["table"]}
    rman = json.loads(NG.ROUTE_MANIFEST.read_text())[NG.ROUTE_ARM]
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(NG.FIXTURES)}
    fixtures = []
    with tempfile.TemporaryDirectory(prefix="nogoal-table-") as wd:
        wd = Path(wd)
        (wd / "p").mkdir()
        (wd / "r").mkdir()
        print(f"compiling champion {rman['source_sha256'][:12]} + the accepted route tap ...")
        plain = H.compile_candidate(REPO / rman["source"], wd / "p")
        rprobe = H.compile_candidate(REPO / rman["probe"], wd / "r")
        for sid in NG.FIXTURES:
            sit, uid = sits[sid], units[sid]
            window = (sit["window"]["turn_start"], sit["window"]["turn_end"])
            rerr = C.check_parity(sit, cfg, plain, rprobe)   # gate: the tap only prints
            rows = rows_for(sid, rerr, window)
            spans = runs(rows)
            fixtures.append({"id": sid, "audited_unit": uid, "window": list(window),
                             "turns_named": len(rows), "units_seen": len({r["unit"] for r in rows}),
                             "runs": spans, "turns": rows})
            print(f"  {sid}  unit {uid}  window {list(window)}  "
                  f"{len(rows)} turns named, {len(spans)} contiguous route spans")
            for s in spans:
                mark = "IN " if s["in_window"] else "out"
                print(f"      {mark} turns {s['turn_start']:>3}-{s['turn_end']:<3} "
                      f"x{s['turns']:<3} {'idle ' if s['idle'] else 'work '} {s['route']}")
    OUT.write_text(json.dumps(
        {"task": "20260821-osc032-033-no-goal-instrument",
         "gate": "G-3 — the per-turn route table",
         "instrument": "the G-1/G-2 package ACCEPTED_FOR_G3 by codex_1 2026-08-21; this file "
                       "adds no tap and no gate, it reports the accepted probe per turn",
         "base": {"name": NG.ROUTE_ARM, "source": rman["source"],
                  "source_sha256": rman["source_sha256"],
                  "note": "champion of record, Door-1 pure deletion, KEPT by the owner "
                          "2026-08-21; diagnostic copy only, no candidate, no Arena"},
         "probe": {"generator": rman["probe"], "generator_sha256": rman["probe_sha256"]},
         "scope": "measurement only; no fix, no candidate, no judgment, no class-wide claim; "
                  "bug-versus-correct-caution is the owner's ruling",
         "not_claimed": "which conjunct of the view.turn>=100 replant block is false is NOT "
                        "measured here and is not attributed; codex_1 ruled the seven-conjunct "
                        "probe not required (2026-08-21)",
         "fixtures": fixtures}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
