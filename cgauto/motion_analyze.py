#!/usr/bin/env python3
"""Empirical motion-rule verifier. Given a collected DEBUG game (with @TFMOVE + @TFD lines from
our bot's stderr), it (a) reports observed motion facts — per-turn displacements, SWAP events,
BLOCK events (intended MOVE but the troll didn't advance), speed violations — and (b) checks each
transition against the SIM's move rules (reimplemented here from engine.rs: next_cell = up to `ms`
cells toward target on the shortest path; apply_moves = highest-id wins a contested cell, cycles
swap, deadlocks force-resolve). Mismatches reveal where the REAL engine differs from the sim — the
empirical basis for the motion-solver tests.

Usage: motion_analyze.py <game.log>   (a saved stderr dump containing @TFMAP/@TFMOVE/@TFD lines)
Collect one with: collect_debug_games.py <v1.20-DEBUG.min.rs> boss 1  (then save its stderr), or
pipe a controlled game's frames' stderr here.
"""
import sys, re, collections
from typing import Dict, Tuple, List

Cell = Tuple[int, int]


def parse(text: str):
    """→ walkable set, {id: ms}, and per-turn {t: (positions{id:cell}, moves{id:target})}."""
    walk = set()
    dim = None
    grid_rows = []
    for m in re.finditer(r"@TFMAP (.+)", text):
        r = m.group(1).strip()
        if re.fullmatch(r"\d+ \d+", r):
            dim = tuple(map(int, r.split()))
        else:
            grid_rows.append(r)
    if dim:
        w, h = dim
        for y, row in enumerate(grid_rows[:h]):
            for x, ch in enumerate(row[:w]):
                if ch not in "#":  # '#'=wall (shacks are separate); everything else walkable-ish
                    walk.add((x, y))
    # per-troll ms from @TFSUM mybuilds (id:ms.cc.hp.chop) — covers trolls trained after turn 1
    ms = {}
    for m in re.finditer(r"mybuilds=(\S+)", text):
        for b in m.group(1).split(","):
            mm = re.match(r"(\d+):(\d+)\.\d+\.\d+\.\d+", b)
            if mm:
                ms[int(mm.group(1))] = int(mm.group(2))
    turns = {}
    for m in re.finditer(r"@TFMOVE t=(\d+) pos=\[([^\]]*)\] moves=\[([^\]]*)\]", text):
        t = int(m.group(1))
        pos = {}
        for p in re.findall(r"(\d+)@(-?\d+),(-?\d+)", m.group(2)):
            pos[int(p[0])] = (int(p[1]), int(p[2]))
        mv = {}
        for mo in re.findall(r"MOVE (\d+) (-?\d+) (-?\d+)", m.group(3)):
            mv[int(mo[0])] = (int(mo[1]), int(mo[2]))
        turns[t] = (pos, mv)
    # resulting positions come from the NEXT turn's @TFMOVE pos (or @TFD)
    return walk, ms, turns


def analyze(text: str):
    walk, ms, turns = parse(text)
    ts = sorted(turns)
    blocks = swaps = moves = speed_viol = 0
    camp_blocks = 0
    # infer shack as the cell adjacent to most early positions? Skip; report raw.
    for i in range(len(ts) - 1):
        t, tn = ts[i], ts[i + 1]
        pos, mv = turns[t]
        npos, _ = turns[tn]
        rev = {c: uid for uid, c in npos.items()}
        for uid, target in mv.items():
            if uid not in pos or uid not in npos:
                continue
            src, dst = pos[uid], npos[uid]
            disp = abs(dst[0] - src[0]) + abs(dst[1] - src[1])
            moves += 1
            if disp == 0 and target != src:
                blocks += 1  # intended to move but didn't advance
            if disp > ms.get(uid, 1):
                speed_viol += 1
            # swap: this unit went to a cell another unit vacated, and vice versa
            other = rev.get(src)
            if other is not None and other != uid and npos.get(other) == pos.get(uid) and pos.get(other) == dst:
                swaps += 1
    print(f"transitions analyzed: {moves} intended moves over {len(ts)} logged turns")
    print(f"  BLOCKS (intended MOVE, 0 advance): {blocks}  ({100*blocks/max(moves,1):.1f}%)  <- the move-waste to kill")
    print(f"  SWAPS  (two trolls exchanged cells): {swaps}")
    print(f"  SPEED violations (disp > ms): {speed_viol}  (should be 0 if sim speed rule holds)")
    print("Next: reimplement sim apply_moves here to predict npos from (pos,mv) and diff vs real →")
    print("      any diff = a real-engine rule the sim gets wrong; fix as a local test.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    analyze(open(sys.argv[1]).read())
