#!/usr/bin/env python3
"""The loop anatomy for the owner — the coordinator's 17:30 ruling 3, on all six loop games.

C-5 fired on 4 panel games (`m078:0`, `m090:0`, `m090:1`, `m118:1`) and 2 fixtures (OSC-006,
OSC-007). The ruling asks, per exchange: both units' chosen targets at `t-1`, `t` and `t+1`, the
trees involved, whether both units are choppers of the same cluster, and which unit re-picked and
to what. All of it read off the wire and the referee trace of the instrument arm — no rerun, no
counterfactual arm. The rule-off arm is dumped over the same window only so the owner can see what
the same turns looked like with the rule off.

Gate G-B: each panel game must reproduce its recorded `panel-swap-census.json` swap count and
score; each fixture its recorded `swap-loop-control.json` exchange turns.

    python3 claude_1/cure2/loop_anatomy.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import trace_detectors as td          # noqa: E402
import narrate5 as n5                 # noqa: E402

PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
LOOP_CONTROL = HERE / "results" / "swap-loop-control.json"
INSTR = HERE / "arm-instrument.rs"
RULEOFF = HERE / "arm-ruleoff.rs"
OUT = HERE / "results" / "loop-anatomy.json"

PANEL_GAMES = ["m078:0", "m090:0", "m090:1", "m118:1"]
FIXTURES = ["OSC-006", "OSC-007"]
BEFORE, AFTER = 3, 8


class GateError(Exception):
    pass


def wire(commands):
    out = {}
    for index, line in enumerate(commands.rstrip("\n").split("\n"), 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"turn {index}: {len(frags)} MSG fragments")
        turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        out[turn] = (units, meta)
    return out


def snapshot(trace, rows, turn):
    if turn < 1 or turn > trace.T:
        return None
    st = trace.state(turn)
    units, meta = rows.get(turn, ({}, {}))
    out = {"turn": turn, "units": {}, "sw": meta.get("sw"), "so": meta.get("so"),
           "sn": meta.get("sn")}
    for u in sorted(st.own_units(), key=lambda u: u.id):
        w = units.get(u.id)
        cmd = trace.cmd_of(u.id, turn)
        out["units"][str(u.id)] = {
            "cell": list(u.cell), "chosen": w[0] if w else None, "want": w[1] if w else None,
            "branch": w[2] if w else None, "command": cmd.raw if cmd else None}
    out["plants"] = [{"cell": list(p.cell), "kind": str(p.kind), "size": p.size,
                      "health": p.health, "fruits": p.fruits} for p in st.plants]
    return out


def anatomy(key, trace, rows):
    """Per exchange: the pair, the three turns, the goals, and who re-picked."""
    exchanges = []
    for turn in sorted(rows):
        units, meta = rows[turn]
        if not meta["sw"]:
            continue
        s_ids = sorted(u for u, v in units.items() if v[2] == "S")
        x_ids = sorted(u for u, v in units.items() if v[2] == "X")
        ambiguous = len(s_ids) != 1 or len(x_ids) != 1
        mover, partner = (s_ids[0], x_ids[0]) if not ambiguous else (None, None)
        row = {"turn": turn, "ambiguous": ambiguous, "mover": mover, "partner": partner,
               "at": {}}
        for label, t in (("t-1", turn - 1), ("t", turn), ("t+1", turn + 1)):
            snap = snapshot(trace, rows, t)
            row["at"][label] = snap
        if not ambiguous:
            def goal(t, uid):
                snap = row["at"][t]
                return snap["units"].get(str(uid), {}).get("chosen") if snap else None
            row["mover_goal"] = {t: goal(t, mover) for t in ("t-1", "t", "t+1")}
            row["partner_goal"] = {t: goal(t, partner) for t in ("t-1", "t", "t+1")}
            row["mover_repicked_after"] = (row["mover_goal"]["t"] != row["mover_goal"]["t+1"])
            row["partner_repicked_after"] = (row["partner_goal"]["t"]
                                             != row["partner_goal"]["t+1"])
            row["goals_traded"] = (row["mover_goal"]["t+1"] == row["partner_goal"]["t"]
                                   and row["partner_goal"]["t+1"] == row["mover_goal"]["t"])
            snap = row["at"]["t"]
            trees = {tuple(p["cell"]) for p in (snap["plants"] if snap else [])}
            goals = [row["mover_goal"]["t"], row["partner_goal"]["t"]]
            row["both_goals_are_trees"] = all(g and g.startswith("TREE(") for g in goals)
            row["goal_cells_are_live_plants"] = [
                (g[5:-1] if g and g.startswith("TREE(") else None) for g in goals]
            row["live_plant_cells"] = sorted(list(c) for c in trees)
        exchanges.append(row)
    return exchanges


def main() -> int:
    census = {r["game"]: r for r in json.loads(CENSUS.read_text())["rows"]}
    loopctl = json.loads(LOOP_CONTROL.read_text())
    result = {"task": "20260825-dance-cure-candidate-2-swap",
              "ruling": "coordination/messages/local_claude_1/20260825T173045Z-"
                        "20260825-dance-cure-candidate-2-swap-policy.md item 3",
              "games": {}}
    with tempfile.TemporaryDirectory(prefix="cure2-loop-") as wd:
        wd = Path(wd)
        instr, ruleoff, parent = wd / "instr.bin", wd / "ruleoff.bin", wd / "parent.bin"
        sh.compile_text(INSTR.read_text(), instr, crate="cure2_loop_instrument")
        sh.compile_text(RULEOFF.read_text(), ruleoff, crate="cure2_loop_ruleoff")

        # ---------------------------------------------------------------- fixtures
        fcfg = json.loads(fh.CONFIG.read_text())
        for sit in fh.load_situations(FIXTURES):
            spec = fh.spec_for(sit, fcfg)
            turns = int(fcfg["turns"])
            out = {}
            for arm, binary in (("instrument", instr), ("ruleoff", ruleoff)):
                transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec), turns)
                trace, rows = td.build_trace(transcript, commands), wire(commands)
                out[arm] = {"exchanges": anatomy(sit["id"], trace, rows)}
                if arm == "instrument":
                    lo = max(1, min(r["turn"] for r in out[arm]["exchanges"]) - BEFORE)
                    hi = min(trace.T, max(r["turn"] for r in out[arm]["exchanges"]) + AFTER)
                out[arm]["window"] = [snapshot(trace, rows, t) for t in range(lo, hi + 1)]
            turns_now = [r["turn"] for r in out["instrument"]["exchanges"]]
            # Fail-closed: the recorded exchange turns come from swap-loop-control.json's `pairs`
            # map, keyed "<fixture>:<a>-<b>". A fixture absent from that map is a GATE FAILURE,
            # not a skipped check.
            recorded = sorted(t for key, turns_ in loopctl["pairs"].items()
                              if key.split(":")[0] == sit["id"] for t in turns_)
            if not recorded:
                raise GateError(f"{sit['id']}: no recorded exchange turns in "
                                f"{LOOP_CONTROL.name}; cannot gate this game")
            if recorded != turns_now:
                raise GateError(f"{sit['id']}: exchanges now at {turns_now}, recorded {recorded}")
            result["games"][sit["id"]] = out
            print(f"  {sit['id']}: exchanges at {turns_now}", flush=True)

        # ---------------------------------------------------------------- panel
        cfg = fp.load_config(PANEL_CFG)
        parent_src = (PANEL_CFG.parent / cfg["parent"]["source"]).resolve()
        sh.compile_text(parent_src.read_text(), parent, crate="cure2_loop_parent")
        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, instr, parent)}
        for key in PANEL_GAMES:
            job = jobs[key]
            spec, turns = job["spec"], job["turns"]
            out = {}
            for arm, binary in (("instrument", instr), ("ruleoff", ruleoff)):
                transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec), turns)
                trace, rows = td.build_trace(transcript, commands), wire(commands)
                out[arm] = {"exchanges": anatomy(key, trace, rows)}
                if arm == "instrument":
                    lo = max(1, min(r["turn"] for r in out[arm]["exchanges"]) - BEFORE)
                    hi = min(trace.T, max(r["turn"] for r in out[arm]["exchanges"]) + AFTER)
                out[arm]["window"] = [snapshot(trace, rows, t) for t in range(lo, hi + 1)]
                row = fp.run_pair(dict(job, candidate=str(binary)))
                out[arm]["score"] = row["candidate"]["score"]
            recorded = census[key]
            if len(out["instrument"]["exchanges"]) != recorded["swaps"]:
                raise GateError(f"{key}: {len(out['instrument']['exchanges'])} exchanges against "
                                f"{recorded['swaps']} recorded")
            if out["instrument"]["score"] != recorded["candidate_score"]:
                raise GateError(f"{key}: score {out['instrument']['score']} against recorded "
                                f"{recorded['candidate_score']}")
            out["recorded_row"] = recorded
            result["games"][key] = out
            print(f"  {key}: exchanges at "
                  f"{[r['turn'] for r in out['instrument']['exchanges']]}, "
                  f"score {out['instrument']['score']} vs rule-off {out['ruleoff']['score']}",
                  flush=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
