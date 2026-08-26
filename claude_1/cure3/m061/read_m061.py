#!/usr/bin/env python3
"""Track D-3 reader — join the v6 wire to the referee transcript, game by game.

Read-only. Inputs are the files pinned in `inputs-manifest.json`, copied out of the
Candidate 3 instrument archive so this task does not depend on `/tmp` surviving.

Three things this file does and nothing else:

  * `parse_transcript`  — the referee's per-turn state exactly as the bot read it
    (`readable/door1-champion.rs:360-435`): two 6-slot inventories, the plant list
    (kind x y size health fruits cooldown), the unit list (id player x y speed carry_cap
    harvest_power chop_power carry[6]). This is where position and carry come from; they
    are NOT on the v6 wire.
  * `parse_commands`    — the emitted command list per turn, and the `MSG ... NARRATE v6`
    payload decoded by `claude_1/narrate6/narrate6.py` (the same decoder the G-1 packet used).
  * `goal_runs`         — maximal runs of consecutive turns on which one unit holds the same
    kept-goal target with `k>0`. The wire's `ka` is the per-turn maximum age over units; a run
    is the per-unit object the charter asks about.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "narrate6"))
import narrate6  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_transcript(text):
    lines = [ln.rstrip("\n") for ln in text.split("\n")]
    i = 0
    width, height = (int(v) for v in lines[i].split())
    i += 1
    rows = lines[i:i + height]
    i += height
    turns = []
    while i < len(lines):
        if not lines[i].strip():
            break
        inv = []
        for _ in range(2):
            inv.append([int(v) for v in lines[i].split()])
            i += 1
        n_plants = int(lines[i]); i += 1
        plants = []
        for _ in range(n_plants):
            f = lines[i].split(); i += 1
            plants.append({"kind": f[0], "cell": (int(f[1]), int(f[2])), "size": int(f[3]),
                           "health": int(f[4]), "fruits": int(f[5]), "cooldown": int(f[6])})
        n_units = int(lines[i]); i += 1
        units = {}
        for _ in range(n_units):
            v = [int(x) for x in lines[i].split()]; i += 1
            units[v[0]] = {"id": v[0], "player": v[1], "cell": (v[2], v[3]),
                           "speed": v[4], "carry_cap": v[5], "harvest": v[6], "chop": v[7],
                           "carry": v[8:14]}
        turns.append({"inventories": inv, "plants": plants, "units": units})
    return {"width": width, "height": height, "rows": rows, "turns": turns}


def parse_commands(text):
    out = []
    for index, line in enumerate(text.strip("\n").split("\n"), 1):
        frags = line.split(";")
        msgs = narrate6.msg_fragments(line)
        cmds = [f.strip() for f in frags if not narrate6.MSG_TOKEN.match(f)]
        turn, units, order, banner, meta = narrate6.decode(msgs[0].strip())
        assert turn == index, (turn, index)
        out.append({"turn": turn, "units": units, "order": order, "meta": meta, "commands": cmds})
    return out


def goal_runs(wire):
    """[(unit, target, first_turn, last_turn, length)] — same target held with k>0, unbroken."""
    live = {}
    runs = []
    for row in wire:
        seen = set()
        for uid, (chosen, _avail, _branch, _b, keep) in row["units"].items():
            if keep == "0" or chosen == "NONE":
                continue
            seen.add(uid)
            cur = live.get(uid)
            if cur and cur[0] == chosen:
                cur[2] = row["turn"]
            else:
                if cur:
                    runs.append((uid, cur[0], cur[1], cur[2]))
                live[uid] = [chosen, row["turn"], row["turn"]]
        for uid in list(live):
            if uid not in seen:
                runs.append((uid, *live.pop(uid)[0:3]))
    for uid, cur in live.items():
        runs.append((uid, cur[0], cur[1], cur[2]))
    return sorted([(u, t, a, b, b - a + 1) for u, t, a, b in runs], key=lambda r: -r[4])


def load(seat, arm="candidate"):
    tr = parse_transcript(open(f"{HERE}/m061-s{seat}-{arm}_transcript.txt").read())
    cm = open(f"{HERE}/m061-s{seat}-{arm}_commands.txt").read()
    wire = parse_commands(cm) if arm == "candidate" else None
    raw = [ln for ln in cm.strip("\n").split("\n")]
    return tr, wire, raw


if __name__ == "__main__":
    for seat in (0, 1):
        tr, wire, _ = load(seat)
        print(f"=== m061 seat {seat}: {len(tr['turns'])} transcript turns, {len(wire)} wire turns")
        print("    ka max", max(r["meta"]["ka"] for r in wire))
        for run in goal_runs(wire)[:6]:
            print("    run u%d %-14s t%d..t%d  len %d" % run)
