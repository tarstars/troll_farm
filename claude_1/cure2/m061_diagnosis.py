#!/usr/bin/env python3
"""`m061`, both seats, turn by turn off the wire — the coordinator's 17:30 ruling 2.

The instrument arm loses 75 points across `m061:0` and `m061:1` with one and two exchanges and, on
`m061:1`, NO dance under rule-off: the rule fires where there was nothing to cure and the game goes
badly. This driver reads both games from the wire on both arms and prints the record a diagnosis
needs: the first divergence from the rule-off arm, and then, for every turn in a window around it,
each own unit's cell, chosen goal, wanted goal, branch letter and issued command on BOTH arms,
with the plants that matter and the banked inventory.

It diagnoses. It proposes nothing and changes nothing.

Gates:
  G-B  row identity -- each arm must reproduce the score recorded in `panel-swap-census.json`
                       (candidate 39/43, parent 75/82); otherwise the regenerated spec is a
                       different game and every turn number below is about another world.

    python3 claude_1/cure2/m061_diagnosis.py [m061:0 m061:1]
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

import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import trace_detectors as td          # noqa: E402
import narrate5 as n5                 # noqa: E402

PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
INSTR = HERE / "arm-instrument.rs"
RULEOFF = HERE / "arm-ruleoff.rs"
OUT = HERE / "results" / "m061-diagnosis.json"
WINDOW_BEFORE, WINDOW_AFTER = 3, 25


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


def gameplay(commands):
    return [n5.strip_msg(l) for l in commands.rstrip("\n").split("\n")]


def snapshot(trace, rows, turn):
    st = trace.state(turn)
    units, meta = rows.get(turn, ({}, {}))
    out = {"turn": turn, "units": {}, "inventory0": list(st.inventories[0]),
           "sw": meta.get("sw"), "so": meta.get("so"), "sn": meta.get("sn")}
    for u in sorted(st.own_units(), key=lambda u: u.id):
        w = units.get(u.id)
        out["units"][str(u.id)] = {
            "cell": list(u.cell), "carry": list(u.carry),
            "chosen": w[0] if w else None, "want": w[1] if w else None,
            "branch": w[2] if w else None,
            "command": (trace.cmd_of(u.id, turn).raw if trace.cmd_of(u.id, turn) else None),
        }
    out["plants"] = [{"cell": list(p.cell), "kind": str(p.kind), "size": p.size,
                      "health": p.health, "fruits": p.fruits} for p in st.plants]
    return out


def main() -> int:
    keys = sys.argv[1:] or ["m061:0", "m061:1"]
    census = {r["game"]: r for r in json.loads(CENSUS.read_text())["rows"]}
    cfg = fp.load_config(PANEL_CFG)
    result = {"task": "20260825-dance-cure-candidate-2-swap",
              "ruling": "coordination/messages/local_claude_1/20260825T173045Z-"
                        "20260825-dance-cure-candidate-2-swap-policy.md item 2",
              "games": {}}
    with tempfile.TemporaryDirectory(prefix="cure2-m061-") as wd:
        wd = Path(wd)
        instr, ruleoff, parent = wd / "instr.bin", wd / "ruleoff.bin", wd / "parent.bin"
        sh.compile_text(INSTR.read_text(), instr, crate="cure2_m061_instrument")
        sh.compile_text(RULEOFF.read_text(), ruleoff, crate="cure2_m061_ruleoff")
        parent_src = (PANEL_CFG.parent / cfg["parent"]["source"]).resolve()
        sh.compile_text(parent_src.read_text(), parent, crate="cure2_m061_parent")
        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, instr, parent)}
        for key in keys:
            job = jobs[key]
            spec = job["spec"]
            turns = job["turns"]
            traces, rows_by_arm, scores, raw_lines = {}, {}, {}, {}
            for arm, binary in (("instrument", instr), ("ruleoff", ruleoff)):
                transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec), turns)
                traces[arm] = td.build_trace(transcript, commands)
                raw_lines[arm] = commands.rstrip("\n").split("\n")
                rows_by_arm[arm] = wire(commands)
                row = fp.run_pair(dict(job, candidate=str(binary)))
                scores[arm] = {"candidate_score": row["candidate"]["score"],
                               "parent_score": row["parent"]["score"],
                               "violations": row["violations"], "flags": row["flags"],
                               # The tail question: why does the champion's shack-side
                               # plant/chop/replant cycle start on the rule-off arm and never on
                               # the instrument arm? TRAIN suppresses the regeneration PICK
                               # (`persistent_regeneration && train_now` retains PICK out), so the
                               # train ledger is recorded rather than guessed at.
                               "train_events": row["train_events"],
                               "successful_train_turns": row.get("successful_train_turns"),
                               "command_error_total": row["command_error_total"]}
                if arm == "instrument":
                    cmds_instr = commands
                else:
                    cmds_ruleoff = commands
            recorded = census[key]
            if scores["instrument"]["candidate_score"] != recorded["candidate_score"]:
                raise GateError(f"{key}: instrument scores "
                                f"{scores['instrument']['candidate_score']} against recorded "
                                f"{recorded['candidate_score']}")
            if scores["ruleoff"]["candidate_score"] != recorded["parent_score"]:
                raise GateError(f"{key}: rule-off scores "
                                f"{scores['ruleoff']['candidate_score']} against recorded "
                                f"parent {recorded['parent_score']}")
            a, b = gameplay(cmds_instr), gameplay(cmds_ruleoff)
            first_div = next((i + 1 for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
            swap_turns = [t for t, (_u, m) in rows_by_arm["instrument"].items() if m["sw"]]
            lo = max(1, min([first_div or 1] + swap_turns) - WINDOW_BEFORE)
            hi = min(traces["instrument"].T, max([first_div or 1] + swap_turns) + WINDOW_AFTER)
            result["games"][key] = {
                "spec": {k: spec[k] for k in ("map_id", "seat", "class", "profile", "seed",
                                              "attempt", "orchard_eligible")},
                "scores": scores, "recorded_row": recorded,
                "first_divergence_turn": first_div,
                "exchange_turns": swap_turns,
                "window": [lo, hi],
                "instrument": [snapshot(traces["instrument"], rows_by_arm["instrument"], t)
                               for t in range(lo, hi + 1)],
                "ruleoff": [snapshot(traces["ruleoff"], rows_by_arm["ruleoff"], t)
                            for t in range(lo, hi + 1)],
                "raw_command_lines": {arm: {str(t): n5.strip_msg(raw_lines[arm][t - 1])
                                            for t in range(lo, hi + 1)}
                                      for arm in ("instrument", "ruleoff")},
                "raw_command_lines_tail": {arm: {str(t): n5.strip_msg(raw_lines[arm][t - 1])
                                                 for t in range(max(1, len(raw_lines[arm]) - 4),
                                                                len(raw_lines[arm]) + 1)}
                                           for arm in ("instrument", "ruleoff")},
                "full_game": {arm: [
                    {"t": t,
                     "u": {str(u.id): [list(u.cell),
                                       (rows_by_arm[arm].get(t, ({}, {}))[0].get(u.id) or
                                        [None, None, None, None])[0],
                                       (rows_by_arm[arm].get(t, ({}, {}))[0].get(u.id) or
                                        [None, None, None, None])[2]]
                           for u in sorted(traces[arm].state(t).own_units(), key=lambda u: u.id)},
                     "inv": list(traces[arm].state(t).inventories[0]),
                     "plants": [[list(pl.cell), pl.health, pl.fruits]
                                for pl in traces[arm].state(t).plants],
                     "sw": rows_by_arm[arm].get(t, ({}, {}))[1].get("sw")}
                    for t in range(1, traces[arm].T + 1)] for arm in ("instrument", "ruleoff")},
                "final_inventory": {
                    "instrument": list(traces["instrument"].state(
                        traces["instrument"].T).inventories[0]),
                    "ruleoff": list(traces["ruleoff"].state(
                        traces["ruleoff"].T).inventories[0])},
            }
            print(f"  {key}: instrument {scores['instrument']['candidate_score']} vs rule-off "
                  f"{scores['ruleoff']['candidate_score']}, first divergence t{first_div}, "
                  f"exchanges at {swap_turns}", flush=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
