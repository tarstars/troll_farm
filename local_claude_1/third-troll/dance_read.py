#!/usr/bin/env python3
"""The dance in three heroes' ladder games (owner 2026-08-28: "There is a dance when two trolls
are trying to collect lemons. One troll tries to collect resource, starts go to tree. Then the
second troll aims to the tree, first freezes. They spend a lot of turns this way.").

Reads a collected package (.jsonl.gz) and, from the v6 diagnostics line our bot prints every turn
(`u<id>=<chosen target>/<wanted target>/r=<move-conflict code>/...`), counts per game:
  contest turns   both own trolls WANT the same tree and at least one of them was given no
                  command at all that turn (a bare WAIT) -- the freeze the owner saw;
  own waits       troll-turns on which an own troll wanted a tree and received no command;
  longest run     the longest streak of consecutive contest turns.
Also lists the worst games and, for one game id (--game), prints the turns.

    python3 local_claude_1/third-troll/dance_read.py <package.jsonl.gz> <agent id> [--game ID]
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter

TOKEN = re.compile(r"u(\d+)=([A-Z]+(?:\([^)]*\))?)/([A-Z]+(?:\([^)]*\))?)/r=(\w)")


def read_game(g, agent_id):
    seat = [a["index"] for a in g["agents"] if a["agentId"] == agent_id][0]
    turns = []
    for fr in g["frames"][1:]:
        if fr.get("agentId") != seat:
            continue
        out = fr.get("stdout") or ""
        units = {}
        for m in TOKEN.finditer(out):
            units[int(m.group(1))] = (m.group(2), m.group(3), m.group(4))
        cmds = [c for c in out.replace("\n", ";").split(";") if c and not c.startswith("MSG")]
        turns.append((units, cmds))
    contest, waits, run, best = 0, 0, 0, 0
    for units, cmds in turns:
        acting = set()
        for cmd in cmds:
            f = cmd.split()
            if len(f) >= 2 and f[0] != "TRAIN":
                try:
                    acting.add(int(f[1]))
                except ValueError:
                    pass
        wants = [(uid, w) for uid, (c, w, r) in units.items() if w.startswith("TREE")]
        same = len(wants) >= 2 and len({w for _, w in wants}) < len(wants)
        frozen_ids = [uid for uid, (c, w, r) in units.items()
                      if w.startswith("TREE") and uid not in acting]
        frozen = bool(frozen_ids)
        waits += len(frozen_ids)
        if same and frozen:
            contest += 1
            run += 1
            best = max(best, run)
        else:
            run = 0
    opp = 1 - seat
    return {"gameId": g["gameId"], "turns": len(turns), "contest": contest, "waits": waits,
            "longest": best, "win": g["scores"][seat] > g["scores"][opp],
            "own": g["scores"][seat], "opp": g["scores"][opp],
            "opp_name": (g["agents"][opp].get("codingamer") or {}).get("pseudo"), "_turns": turns}


def main() -> int:
    path, agent_id = sys.argv[1], int(sys.argv[2])
    want = int(sys.argv[sys.argv.index("--game") + 1]) if "--game" in sys.argv else None
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            g = json.loads(line)
            r = read_game(g, agent_id)
            if want and r["gameId"] == want:
                for t, (units, cmds) in enumerate(r["_turns"], 1):
                    print(f"t{t:>3}  {' ; '.join(cmds):<58} " + "  ".join(
                        f"u{u}={c}/{w}/r={rc}" for u, (c, w, rc) in sorted(units.items())))
            del r["_turns"]
            rows.append(r)
    n = len(rows)
    with_dance = [r for r in rows if r["contest"] >= 10]
    print(f"games {n}; contest turns per game: mean {sum(r['contest'] for r in rows)/n:.1f}, "
          f"median {sorted(r['contest'] for r in rows)[n//2]}, max {max(r['contest'] for r in rows)}; "
          f"games with >= 10 contest turns: {len(with_dance)} "
          f"(wins {sum(r['win'] for r in with_dance)}); own waits while wanting a tree per game: "
          f"mean {sum(r['waits'] for r in rows)/n:.1f}")
    for r in sorted(rows, key=lambda r: -r["contest"])[:12]:
        print(f"  game {r['gameId']} vs {r['opp_name']!s:<20} contest {r['contest']:>3} longest run "
              f"{r['longest']:>3} waits {r['waits']:>3}  {'win' if r['win'] else 'loss'} {r['own']}-{r['opp']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
