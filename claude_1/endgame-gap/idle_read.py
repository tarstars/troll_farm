#!/usr/bin/env python3
"""Track E, deliverable 2/4: why our trolls stand in turns 251-300 and what a rule could recover, from the
exact reconstruction of the champion's 160 collected games (commands are what the bot emitted; a troll with
no unit command that turn is 'idle').

Per idle troll-turn: the nearest living tree (distance, size, health, fruit, an opponent standing on it),
whether the partner troll is chopping at that moment, and the class:
  partner_chopping        the partner is on a tree chopping; the idle troll could join it (co-chop)
  opp_guarded_only        every living tree within reach carries an opponent troll
  no_tree_left            no living tree reachable
  fruit_only              reachable trees carry fruit but the troll has harvest 0 or a full load
  tree_reachable_free     a living tree reachable, unguarded, partner not on it (the bot refused it)
Felled-by-us trees in 251-300 by size, with the partner idle that turn (the co-chop duplication bound:
two own choppers on the death turn take size+1 wood from a size-1 or size-3 tree, engine.rs 604-627).
Standing fruit and tree sizes at game end (what nobody took).
"""
import json, sys, collections, statistics as S
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


def reach(rows, start):
    w, h = len(rows[0]), len(rows); seen = {start: 0}; q = [start]
    for x, y in q:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and rows[n[1]][n[0]] not in "~#+":
                seen[n] = seen[(x, y)] + 1; q.append(n)
    return seen


cls = collections.Counter(); felled = collections.Counter(); felled_partner_idle = collections.Counter()
per_game = []; examples = collections.defaultdict(list)
for p in sorted(R.RAW.glob('*.json')):
    r = R.Reconstructor(int(p.stem)); states = r.run(True)
    ours = next(a['index'] for a in r.replay['agents'] if a['agentId'] == OUR)
    if r.n_turns < 251:
        continue
    rows = r.map['rows']; c = collections.Counter(); f = collections.Counter(); fpi = collections.Counter()
    for t in range(251, r.n_turns + 1):
        st = states[t - 1]; nxt = states[t] if t < r.n_turns else r.snapshot(t + 1)
        cu = cmd_units(r.commands(t)[ours])
        mine = [u for u in st['units'] if u['player'] == ours]
        opp_cells = {(u['x'], u['y']) for u in st['units'] if u['player'] != ours}
        chopping_cells = {(u['x'], u['y']) for u in mine if cu.get(u['id']) == 'CHOP'}
        idle = [u for u in mine if u['id'] not in cu]
        # trees felled this turn by us: living in st, gone in nxt, one of ours chopping on it
        after = {(pl['x'], pl['y']) for pl in nxt['plants']}
        for pl in st['plants']:
            cell = (pl['x'], pl['y'])
            if pl['health'] > 0 and cell not in after and cell in chopping_cells:
                f[pl['size']] += 1
                if idle:
                    fpi[pl['size']] += 1
        for u in idle:
            d = reach(rows, (u['x'], u['y'])); free = u['cc'] - sum(u['carry'])
            trees = [(d[(pl['x'], pl['y'])], pl) for pl in st['plants'] if pl['health'] > 0 and (pl['x'], pl['y']) in d]
            if chopping_cells:
                key = 'partner_chopping'
            elif not trees:
                key = 'no_tree_left'
            elif all((pl['x'], pl['y']) in opp_cells for _, pl in trees):
                key = 'opp_guarded_only'
            elif u['chop'] > 0 and free > 0:
                key = 'tree_reachable_free'
            elif any(pl['fruits'] > 0 for _, pl in trees):
                key = 'fruit_only'
            else:
                key = 'tree_reachable_free'
            c[key] += 1
            if len(examples[key]) < 3 and (not examples[key] or examples[key][-1][0] != int(p.stem)):
                near = min(trees, key=lambda x: x[0])[1] if trees else None
                examples[key].append((int(p.stem), t, [u['x'], u['y']], u['id'], [u['ms'], u['cc'], u['hp'], u['chop']],
                                      (near['type'], near['size'], near['health'], near['fruits'], min(trees, key=lambda x: x[0])[0]) if near else None))
    final = r.snapshot(r.n_turns + 1)
    cls.update(c); felled.update(f); felled_partner_idle.update(fpi)
    per_game.append({'gameId': int(p.stem), 'n_turns': r.n_turns, 'idle': dict(c), 'felled_by_size': dict(f), 'felled_partner_idle': dict(fpi),
                     'fruit_standing_end': sum(pl['fruits'] for pl in final['plants'] if pl['health'] > 0),
                     'tree_sizes_standing_end': sum(pl['size'] for pl in final['plants'] if pl['health'] > 0),
                     'trees_end': sum(1 for pl in final['plants'] if pl['health'] > 0)})
tot = sum(cls.values())
print('idle troll-turns (ours, 251-300, games reaching 251):', tot, 'over', len(per_game), 'games')
for k, v in cls.most_common():
    print(f'  {k:22s} {v:6d} {v/tot:6.1%}   e.g. {examples[k][:3]}')
print('trees felled by us in 251-300 by size:', dict(sorted(felled.items())), '; of which with our other troll idle that turn:', dict(sorted(felled_partner_idle.items())))
dup = felled_partner_idle.get(1, 0) + felled_partner_idle.get(3, 0)
print(f'co-chop duplication bound: {dup} odd-size fellings with an idle partner = +{dup} wood = +{4*dup} points over {len(per_game)} games = {4*dup/len(per_game):.1f} points a game')
print('standing at end: fruit mean %.1f median %.0f; tree-size units mean %.1f median %.0f; trees mean %.1f; games with none: %d'
      % (S.mean(g['fruit_standing_end'] for g in per_game), S.median(g['fruit_standing_end'] for g in per_game),
         S.mean(g['tree_sizes_standing_end'] for g in per_game), S.median(g['tree_sizes_standing_end'] for g in per_game),
         S.mean(g['trees_end'] for g in per_game), sum(1 for g in per_game if g['trees_end'] == 0)))
json.dump({'idle_classes': dict(cls), 'felled_by_size': dict(felled), 'felled_partner_idle': dict(felled_partner_idle),
           'examples': {k: v for k, v in examples.items()}, 'per_game': per_game},
          open('claude_1/endgame-gap/idle-read.json', 'w'), indent=1, sort_keys=True)
