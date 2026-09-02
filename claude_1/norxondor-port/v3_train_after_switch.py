#!/usr/bin/env python3
"""The read's third mechanism check on the replays: with PRODUCE_ROSTER_CAP = 3 the port must never issue a
third TRAIN (the starting troll plus two bought ones make three), and after the second TRAIN no TRAIN may follow (the switch fires the turn after the third troll
exists, and Deforest suppresses TRAIN). Reads an `h2h.py --replays` file; prints the TRAIN count per game, the
median turn of each TRAIN, and any violation."""
import json, statistics, sys
path = sys.argv[1]
counts = {}
turns_by_rank = {}
violations = []
games = 0
for line in open(path):
    g = json.loads(line); games += 1
    seat = f"seat{g['policy_seat']}"
    trains = [t['turn'] for t in g['turns'] if any(c.startswith('TRAIN') for c in t[seat].split(';'))]
    counts[len(trains)] = counts.get(len(trains), 0) + 1
    for i, tt in enumerate(trains):
        turns_by_rank.setdefault(i + 1, []).append(tt)
    if len(trains) > 2:
        violations.append((g['map_hash'], g['policy_seat'], trains))
print(f"games {games}; TRAIN count per game {dict(sorted(counts.items()))}")
for k, v in sorted(turns_by_rank.items()):
    print(f"TRAIN #{k}: n={len(v)} median turn {statistics.median(v)}")
print(f"games with a third TRAIN (a fourth troll): {len(violations)}")
for v in violations[:10]: print("  ", v)
