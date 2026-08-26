#!/usr/bin/env python3
"""What each candidate release rule would have cut, across the whole Candidate 3 panel.

Read-only, and deliberately NOT a simulation: nothing here re-runs the bot. For each kept-goal
EPISODE (see `episodes.py`) it reports the turn a rule would have fired and what the holder did
on the turns the rule would have removed — the CHOP / HARVEST / DROP / PLANT / PICK it emitted
after the cut, and whether the episode went on to end in `rd` (the goal completed). A rule that
cuts a tail full of CHOPs which ends in `rd` is taking work away; a rule that cuts a tail of
MOVE/WAIT which ends at `game_end` is taking waste away. Everything downstream of the cut turn
would in truth be different — that is exactly why this file reports evidence, not a score.

Rules probed
  cap<N>      release a kept goal on its Nth turn.
  dance<N>    release when the holder has occupied at most two distinct cells on the last N
              turns of the episode. This is the D-1 shape, applied to the goal-holder.
  bps<X>      release when the wire's `xd` (basis points given up by keeping, `give_up_bps`)
              exceeds X on that turn. `xd` is a per-TURN field, not per-unit, so this rule is
              only attributed on turns where exactly one unit holds a kept goal.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "narrate6"))
import narrate6  # noqa: E402
import episodes as EP  # noqa: E402
from read_m061 import parse_transcript  # noqa: E402

WORK = ("CHOP", "HARVEST", "DROP", "PLANT", "PICK")


def unit_command(commands, uid):
    for c in commands:
        f = c.split()
        if len(f) >= 2 and f[1].isdigit() and int(f[1]) == uid:
            return c
    return "WAIT"


def dance_fire(cells, start, end, window):
    """First turn t in [start+window-1, end] where cells[start..t] last `window` are <=2 distinct."""
    for t in range(start + window - 1, end + 1):
        seen = {cells[x] for x in range(t - window + 1, t + 1) if x in cells}
        if len(seen) <= 2:
            return t
    return None


def analyse(archive):
    out = []
    for line in gzip.open(archive, "rt"):
        d = json.loads(line)
        eps, rows = EP.episodes_for_game(d["artifacts"]["candidate_commands"])
        tr = parse_transcript(d["artifacts"]["candidate_transcript"])
        cmds = [[f.strip() for f in ln.split(";") if not narrate6.MSG_TOKEN.match(f)]
                for ln in d["artifacts"]["candidate_commands"].strip("\n").split("\n")]
        for e in eps:
            uid = e["unit"]
            cells = {t: tr["turns"][t - 1]["units"][uid]["cell"]
                     for t in range(e["start"], e["end"] + 1)
                     if uid in tr["turns"][t - 1]["units"]}
            fires = {}
            for n in (20, 30, 40, 60):
                fires[f"cap{n}"] = e["start"] + n - 1 if e["length"] >= n else None
            for w in (8, 12, 20):
                fires[f"dance{w}"] = dance_fire(cells, e["start"], e["end"], w)
            xd = {}
            for t in range(e["start"], e["end"] + 1):
                meta = rows[t - 1][1]
                if meta["kp"] == 1:
                    xd[t] = meta["xd"]
            for x in (0, 100, 1000):
                hit = [t for t in sorted(xd) if xd[t] > x]
                fires[f"bps{x}"] = hit[0] if hit else None
            tails = {}
            for name, ft in fires.items():
                if ft is None or ft >= e["end"]:
                    tails[name] = None
                    continue
                work = {}
                for t in range(ft + 1, e["end"] + 1):
                    c = unit_command(cmds[t - 1], uid).split()[0].upper()
                    if c in WORK:
                        work[c] = work.get(c, 0) + 1
                tails[name] = {"cut_turn": ft, "turns_removed": e["end"] - ft, "work": work}
            out.append({"map_id": d["map_id"], "seat": d["seat"], "unit": uid,
                        "start": e["start"], "end": e["end"], "length": e["length"],
                        "end_cause": e["end_cause"],
                        "own_candidate": d["candidate"]["score"],
                        "own_parent": d["parent"]["score"],
                        "fires": fires, "tails": tails})
    return out


if __name__ == "__main__":
    res = analyse(sys.argv[1])
    json.dump({"archive": sys.argv[1], "episodes": res}, open(sys.argv[2], "w"),
              indent=1, sort_keys=True)
    print(f"{len(res)} episodes -> {sys.argv[2]}")
