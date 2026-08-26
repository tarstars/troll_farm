#!/usr/bin/env python3
"""The m061 turn table — one row per turn per arm, wire joined to referee state. Read-only."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import read_m061 as R  # noqa: E402

HEAD = ("turn  unit  kept-goal-carried/best-available  r  k   cell  carry  command"
        "        | kp kq kl kr rd rf ro xc ka | own")


def table(seat, arm):
    if arm == "candidate":
        tr, wire, _ = R.load(seat)
    else:
        tr = R.parse_transcript(open(f"{HERE}/m061-s{seat}-{arm}_transcript.txt").read())
        wire = R.parse_commands(open(f"{HERE}/m061-s{seat}-{arm}_commands.txt").read())
    lines = [f"# m061 seat {seat} — {arm} arm", "",
             "# `kept-goal-carried` is the wire's `chosen`: the target of the candidate the",
             "# EMITTED command matched (NONE = the command matched no candidate, or matched",
             "# the always-present WAIT candidate, whose target is None — the two are the same",
             "# token on this wire). `best-available` is `want`: the highest-scoring candidate",
             "# the unit had this turn. r: P primary . L improving detour . R regressive detour",
             "# . W forced WAIT . N the emitted command was not a MOVE. k: 2 restricted and",
             "# carrying the kept goal . 1 holds a valid kept goal the command does not carry",
             "# . 0 no valid kept goal.", "", HEAD, ""]
    for t in range(1, len(wire) + 1):
        row, st = wire[t - 1], tr["turns"][t - 1]
        m = row["meta"]
        own = sum(st["inventories"][0][i] for i in (0, 1, 2, 3)) + 4 * st["inventories"][0][5]
        for i, uid in enumerate(sorted(row["units"])):
            chosen, want, br, _, k = row["units"][uid]
            u = st["units"].get(uid)
            cmd = next((c for c in row["commands"]
                        if c.split()[1:2] and c.split()[1].isdigit()
                        and int(c.split()[1]) == uid), "WAIT")
            tail = (f" | {m['kp']} {m['kq']} {m['kl']} {m['kr']} {m['rd']} {m['rf']} {m['ro']} "
                    f"{m['xc']} {m['ka']:3d} | {own:3d}" if i == 0 else "")
            lines.append(f"{t:4d}  u{uid}   {chosen:>12s}/{want:<12s} {br}  {k}  "
                         f"{str(u['cell']) if u else '-':7s} {sum(u['carry']) if u else '-'}  "
                         f"{cmd:14s}{tail}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    for seat in (0, 1):
        for arm in ("candidate", "ruleoff"):
            p = f"{HERE}/turntable-m061-s{seat}-{arm}.txt"
            open(p, "w").write(table(seat, arm))
            print(p)
