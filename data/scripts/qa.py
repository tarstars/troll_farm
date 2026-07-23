#!/usr/bin/env python3
"""Dataset QA: end-to-end consistency checks over the processed dataset.

The strongest check: the final score recomputed from the trajectory's last
inventories (fruits + 4*wood) must equal the official scores[] from the replay.
This exercises the whole pipeline: frame->turn alignment, inventory line order,
and the score formula. Also validates map/tree decoding invariants.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent
PROC = DATA / "processed"

MAXW = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}

def score_status(official_scores, final_inventories):
    """Classify exact scores, expected crash penalties, and real decode drift."""

    derived = [sum(inv[:4]) + 4 * inv[5] for inv in final_inventories]
    unexpected = [
        p
        for p, (official, decoded) in enumerate(zip(official_scores, derived))
        if official >= 0 and official != decoded
    ]
    if unexpected:
        return "unexpected", derived
    if any(score < 0 for score in official_scores):
        return "penalty", derived
    return "exact", derived


def main():
    n = score_ok = score_penalty = score_off = 0
    tree_bad = []
    sym = 0
    early_mismatch = []
    for line in open(PROC / "games.jsonl"):
        g = json.loads(line)
        n += 1
        # 1. score consistency (only meaningful when we have official scores)
        final_inventories = [g["per_player"][str(p)]["final_inv"] for p in (0, 1)]
        status, derived = score_status(g["scores"], final_inventories)
        if status == "exact":
            score_ok += 1
        elif status == "penalty":
            score_penalty += 1
            early_mismatch.append((g["gameId"], g["n_turns"], g["scores"], derived))
        else:
            score_off += 1
            early_mismatch.append((g["gameId"], g["n_turns"], g["scores"], derived))
        # 2. tree decode invariants
        for t in g["map"]["trees0"]:
            if not (0 <= t["x"] < g["map"]["w"] and 0 <= t["y"] < g["map"]["h"]):
                tree_bad.append((g["gameId"], "pos", t))
            if t["stage"] < 1 or t["stage"] > 7:
                tree_bad.append((g["gameId"], "stage", t))
            if t["cd_eff"] > MAXW[t["type"]] or t["cur_cd"] > t["cd_eff"]:
                tree_bad.append((g["gameId"], "cd", t))
            if t["type"] not in MAXW:
                tree_bad.append((g["gameId"], "type", t))
        # 3. tree point-symmetry (referee mapgen mirrors trees)
        pos = {(t["x"], t["y"]) for t in g["map"]["trees0"]}
        w, h = g["map"]["w"], g["map"]["h"]
        if all((w - 1 - x, h - 1 - y) in pos for x, y in pos):
            sym += 1
    print(f"games checked:            {n}")
    print(f"score exact match:        {score_ok} ({100*score_ok/n:.1f}%)")
    print(f"score penalty-only:       {score_penalty}")
    print(f"score unexpected mismatch:{score_off:>8}")
    for gid, nt, official, derived in early_mismatch[:8]:
        print(f"   {gid}: n_turns={nt} official={official} derived={derived}")
    print(f"tree invariant violations: {len(tree_bad)} {tree_bad[:3]}")
    print(f"tree layout point-symmetric: {sym}/{n}")
    return 1 if score_off or tree_bad or sym != n else 0

if __name__ == "__main__":
    sys.exit(main())
