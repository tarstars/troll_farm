#!/usr/bin/env python3
"""Track E, the recoverability of our idle troll-turns (251-300): for each idle troll-turn, was there a
reachable, unguarded living tree that the idle troll could have FELLED before the end (travel/speed +
ceil(health/chop) <= turns left, chop > 0, free capacity) or HARVESTED and banked before the end (the
champion's own idle-harvest trip test: travel + 1 + home + 1 <= turns left, harvest > 0, empty hands)?
Then the bound: trees that were feasible at some idle turn AND still stood at the game end (nobody took
them) -> wood units x 4 and fruit, per game. Also the idle turns by 10-turn bucket.
"""
import json, sys, collections, statistics as S, math
from pathlib import Path
sys.path.insert(0, '.'); sys.path.insert(0, 'local_claude_1/reconstructions/fits')
import reconstruct as R
R.RAW = Path('/data/scratch/claude1-champ-41202036')
OUR = 6667789
UNIT_VERBS = {"MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE"}
def cmd_units(cmds):
    out = {}
    for c in cmds:
        t = c.split()
        if len(t) >= 2 and t[0].upper() in UNIT_VERBS and t[1].lstrip('-').isdigit():
            out[int(t[1])] = t[0].upper()
    return out
def bfs(rows, starts):
    w, h = len(rows[0]), len(rows); seen = {s: 0 for s in starts}; q = list(starts)
    for x, y in q:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and rows[n[1]][n[0]] not in "~#+":
                seen[n] = seen[(x, y)] + 1; q.append(n)
    return seen
buckets = collections.Counter(); feas = collections.Counter(); per_game = []
for p in sorted(R.RAW.glob('*.json')):
    r = R.Reconstructor(int(p.stem)); states = r.run(True)
    ours = next(a['index'] for a in r.replay['agents'] if a['agentId'] == OUR)
    if r.n_turns < 251:
        continue
    rows = r.map['rows']; shack = None
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == str(ours):
                shack = (x, y)
    home = bfs(rows, [c for c in ((shack[0]+1, shack[1]), (shack[0]-1, shack[1]), (shack[0], shack[1]+1), (shack[0], shack[1]-1)) if 0 <= c[1] < len(rows) and 0 <= c[0] < len(rows[0]) and rows[c[1]][c[0]] not in "~#+"])
    feasible_trees = {}   # cell -> ('chop'|'harvest', size, fruits) first seen feasible at an idle turn
    idle_n = 0; idle_feas = 0
    for t in range(251, r.n_turns + 1):
        st = states[t - 1]; cu = cmd_units(r.commands(t)[ours]); left = 300 - t + 1
        mine = [u for u in st['units'] if u['player'] == ours]
        opp_cells = {(u['x'], u['y']) for u in st['units'] if u['player'] != ours}
        for u in mine:
            if u['id'] in cu:
                continue
            idle_n += 1; buckets[(t - 251) // 10] += 1
            d = bfs(rows, [(u['x'], u['y'])]); free = u['cc'] - sum(u['carry']); ok = None
            for pl in st['plants']:
                cell = (pl['x'], pl['y'])
                if pl['health'] <= 0 or cell not in d or cell in opp_cells:
                    continue
                travel = math.ceil(d[cell] / max(u['ms'], 1))
                if u['chop'] > 0 and free > 0 and travel + math.ceil(pl['health'] / u['chop']) <= left:
                    ok = ok or 'chop'; feasible_trees.setdefault(cell, ('chop', pl['size'], pl['fruits']))
                if u['hp'] > 0 and sum(u['carry']) == 0 and pl['fruits'] > 0 and cell in home and travel + 1 + math.ceil(home[cell] / max(u['ms'], 1)) + 1 <= left:
                    ok = ok or 'harvest'; feasible_trees.setdefault(cell, ('harvest', pl['size'], pl['fruits']))
            feas[ok or 'none'] += 1; idle_feas += 1 if ok else 0
    final = r.snapshot(r.n_turns + 1)
    standing = {(pl['x'], pl['y']): pl for pl in final['plants'] if pl['health'] > 0}
    untaken = [(c, v, standing[c]) for c, v in feasible_trees.items() if c in standing]
    wood_pts = sum(4 * pl['size'] for c, v, pl in untaken if v[0] == 'chop')
    fruit = sum(pl['fruits'] for c, v, pl in untaken)
    per_game.append({'gameId': int(p.stem), 'idle': idle_n, 'idle_feasible': idle_feas, 'untaken_feasible_trees': len(untaken),
                     'untaken_wood_points_bound': wood_pts, 'untaken_fruit_bound': fruit})
tot = sum(feas.values())
print('idle troll-turns', tot, 'feasibility:', {k: f"{v} ({v/tot:.1%})" for k, v in feas.most_common()})
print('idle by 10-turn bucket from 251:', [buckets[i] for i in range(5)])
print('per game: untaken feasible trees mean %.2f; wood-points bound mean %.1f median %.0f; fruit bound mean %.1f median %.0f; games with any: %d/%d'
      % (S.mean(g['untaken_feasible_trees'] for g in per_game), S.mean(g['untaken_wood_points_bound'] for g in per_game),
         S.median(g['untaken_wood_points_bound'] for g in per_game), S.mean(g['untaken_fruit_bound'] for g in per_game),
         S.median(g['untaken_fruit_bound'] for g in per_game), sum(1 for g in per_game if g['untaken_feasible_trees']), len(per_game)))
json.dump({'feasibility': dict(feas), 'buckets': [buckets[i] for i in range(5)], 'per_game': per_game}, open('claude_1/endgame-gap/idle-feasible.json', 'w'), indent=1, sort_keys=True)
