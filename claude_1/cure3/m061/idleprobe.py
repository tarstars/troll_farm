#!/usr/bin/env python3
"""The stricter release rule: two cells for N turns **and no work in those N turns**.

Companion to `fixprobe.py`, same archive, same episode definition, same read-only stance —
nothing here re-runs the bot. `fixprobe.py`'s `dance<N>` fires on position alone, so it also
fires on a chopper standing at its tree; `idle<N>` additionally requires that the holder issued
no CHOP / HARVEST / DROP / PLANT / PICK anywhere in the window, which is what makes it safe to
recommend. Produces `idleprobe.json` (the artifact cited as item 4's "2-cell-dance-and-no-work"
evidence):

    python3 idleprobe.py <games.jsonl.gz> idleprobe.json
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
from fixprobe import WORK, unit_command  # noqa: E402

WINDOWS = (8, 12, 20)


def idle_fire(cells, commands, uid, start, end, window):
    """First turn t whose last `window` turns sit on <=2 cells and contain no work command."""
    for t in range(start + window - 1, end + 1):
        span = range(t - window + 1, t + 1)
        seen = {cells[x] for x in span if x in cells}
        if len(seen) > 2:
            continue
        worked = any(unit_command(commands[x - 1], uid).split()[0].upper() in WORK for x in span)
        if not worked:
            return t
    return None


def analyse(archive):
    out = []
    for line in gzip.open(archive, "rt"):
        d = json.loads(line)
        eps, _rows = EP.episodes_for_game(d["artifacts"]["candidate_commands"])
        tr = parse_transcript(d["artifacts"]["candidate_transcript"])
        cmds = [[f.strip() for f in ln.split(";") if not narrate6.MSG_TOKEN.match(f)]
                for ln in d["artifacts"]["candidate_commands"].strip("\n").split("\n")]
        for e in eps:
            uid = e["unit"]
            cells = {t: tr["turns"][t - 1]["units"][uid]["cell"]
                     for t in range(e["start"], e["end"] + 1)
                     if uid in tr["turns"][t - 1]["units"]}
            fires, tails = {}, {}
            for w in WINDOWS:
                ft = idle_fire(cells, cmds, uid, e["start"], e["end"], w)
                fires[f"idle{w}"] = ft
                if ft is None or ft >= e["end"]:
                    tails[f"idle{w}"] = None
                    continue
                work = {}
                for t in range(ft + 1, e["end"] + 1):
                    c = unit_command(cmds[t - 1], uid).split()[0].upper()
                    if c in WORK:
                        work[c] = work.get(c, 0) + 1
                tails[f"idle{w}"] = {"cut_turn": ft, "turns_removed": e["end"] - ft, "work": work}
            out.append({"map_id": d["map_id"], "seat": d["seat"], "unit": uid,
                        "start": e["start"], "end": e["end"], "length": e["length"],
                        "end_cause": e["end_cause"],
                        "delta": d["candidate"]["score"] - d["parent"]["score"],
                        "fires": fires, "tails": tails})
    return out


if __name__ == "__main__":
    res = analyse(sys.argv[1])
    json.dump(res, open(sys.argv[2], "w"), indent=1, sort_keys=True)
    print(f"{len(res)} episodes -> {sys.argv[2]}")
