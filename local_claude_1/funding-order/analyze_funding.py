#!/usr/bin/env python3
"""Turn-by-turn read of the third-troll funding phase, orchard 6 (submission 41209711,
agent 6671418, 160 ladder games).

State is rebuilt EXACTLY the way local_claude_1/reconstructions/fits/reconstruct.py does it
(validated there against the referee: "40,458 recorded turns replay ... parity 9,502/0"):
replay both seats' commands through the referee mirror sim/engine.py (this predicts the
passive ticks the platform's diff does NOT re-send every turn -- confirmed empirically here:
a tree's cooldown/stage token is only re-sent on the turns it is *touched*, so a diff-only
read silently freezes fruit growth between touches and undercounts "fruits before harvest").
The platform's own keyframe diff then overlays the engine's prediction with the ground truth
(positions, carries, plant health/stage/cooldown resets, inventories) turn by turn.

Usage: python3 analyze_funding.py <games.jsonl.gz> <our_agent_id> [max_games]
"""
import gzip, json, sys, os, statistics
from collections import defaultdict, Counter, deque

ROOT = "/home/tarstars/prj/troll_farm-local_claude_1"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "local_claude_1/reconstructions/fits"))
import reconstruct as rc  # parse_frame0, build_game, split_cmds, view_payload, Reconstructor
from sim.engine import step  # noqa: E402

TYPES = ("PLUM", "LEMON", "APPLE", "BANANA")
ITEM_NAMES = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))
BILL_ITEMS = ["PLUM", "LEMON", "APPLE", "IRON"]
FUNDING_WINDOW = 130  # turns 1..130: covers every 3rd-troll TRAIN turn observed (max 122 over 160 games)


def bfs(walkable, sources):
    dist = {}
    dq = deque()
    for s in sources:
        if s not in dist:
            dist[s] = 0
            dq.append(s)
    while dq:
        c = dq.popleft()
        d = dist[c]
        for dx, dy in ORTH:
            n = (c[0] + dx, c[1] + dy)
            if n in walkable and n not in dist:
                dist[n] = d + 1
                dq.append(n)
    return dist


def training_cost(n, ms, cc, hp, chop):
    return {"PLUM": n + ms * ms, "LEMON": n + cc * cc, "APPLE": n + hp * hp, "IRON": n + chop * chop}


def make_reconstructor(game_dict):
    """Build a reconstruct.Reconstructor directly from an in-memory game dict (same schema as
    reconstruct.py's RAW/{id}.json), instead of reading a file -- this is the ONLY change from
    reconstruct.py's own __init__."""
    r = rc.Reconstructor.__new__(rc.Reconstructor)
    r.game_id = game_dict["gameId"]
    r.replay = game_dict
    r.frames = game_dict["frames"]
    w, h, rows, units, plants, inv = rc.parse_frame0(r.frames[0])
    r.map = dict(w=w, h=h, rows=rows)
    r.game = rc.build_game(w, h, rows, units, plants, inv)
    r.unit_by_eid, r.plant_by_eid = {}, {}
    by_id = {u.id: u for u in r.game.units}
    for eid, u in units.items():
        r.unit_by_eid[eid] = by_id[u["id"]]
    by_pos = {p.pos: p for p in r.game.plants}
    for eid, p in plants.items():
        r.plant_by_eid[eid] = by_pos[(p["x"], p["y"])]
    r.mismatch = Counter()
    r.examples = {}
    r.agents = {a["index"]: a for a in r.replay["agents"]}
    r.n_turns = (len(r.frames) - 1) // 2
    return r


def map_geometry(r, seat):
    rows, w, h = r.map["rows"], r.map["w"], r.map["h"]
    walkable, iron, water = set(), set(), set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            c = (x, y)
            if ch == "0":
                shacks[0] = c
            elif ch == "1":
                shacks[1] = c
            elif ch == ".":
                walkable.add(c)
            elif ch == "+":
                iron.add(c)
            elif ch == "~":
                water.add(c)
    shack = shacks[seat]
    doors = [d for d in [(shack[0] + dx, shack[1] + dy) for dx, dy in ORTH] if d in walkable]
    return dict(walkable=walkable, iron=iron, water=water, shacks=shacks,
                dist_from_shack=bfs(walkable, doors) if doors else {})


def analyze(path, agent_id, max_games=None):
    raw_games = []
    with gzip.open(path, "rt") as fh:
        for i, line in enumerate(fh):
            if max_games and i >= max_games:
                break
            raw_games.append(json.loads(line))

    per_game = []
    skipped = []
    for g in raw_games:
      try:
        seat = [a["index"] for a in g["agents"] if a["agentId"] == agent_id][0]
        opp_seat = 1 - seat
        r = make_reconstructor(g)
        geo = map_geometry(r, seat)
        has_iron = len(geo["iron"]) > 0

        rec = dict(game_id=g["gameId"], iron_map=has_iron, own_score=g["scores"][seat],
                   opp_score=g["scores"][opp_seat], win=g["scores"][seat] > g["scores"][opp_seat],
                   n_turns=r.n_turns, second=None, third=None, opening12=[], plants=[], harvests=[],
                   drops=[], mines=[], trains_issued=[], picks=[], bill_series=[],
                   action_counts=defaultdict(Counter), stuck_moves=0, one_item_drops=0,
                   multi_item_drops=0, total_drop_items=0, pick_train_same_turn=0,
                   idle_wait_on_empty_tree=0, idle_wait_elsewhere=0, planted_cells=set())

        role_of = {}
        starting_id = min(u.id for u in r.game.units if u.player == seat)
        role_of[starting_id] = "A"
        own_trolls_before = 1

        for t in range(1, r.n_turns + 1):
            c0, c1 = r.commands(t)
            our_cmds, opp_cmds = (c0, c1) if seat == 0 else (c1, c0)
            pre_units = {u.id: dict(x=u.x, y=u.y, carry=list(u.carry), player=u.player) for u in r.game.units}
            pre_plants = {p.pos: dict(type=p.type, size=p.size, fruits=p.fruits, health=p.health) for p in r.game.plants}
            pre_inv = [list(x) for x in r.game.inventories]
            own_trolls_now = sum(1 for u in pre_units.values() if u["player"] == seat)

            train_cmd, per_unit_cmd, picks_this_turn = None, {}, []
            for cmd in our_cmds:
                f = cmd.split()
                if not f or f[0] == "MSG":
                    continue
                if f[0] == "TRAIN":
                    train_cmd = f
                    continue
                uid = int(f[1]) if len(f) > 1 and f[1].lstrip("-").isdigit() else None
                if uid is not None:
                    per_unit_cmd[uid] = f
                if f[0] == "PICK":
                    picks_this_turn.append(f)
            if train_cmd and picks_this_turn:
                rec["pick_train_same_turn"] += 1

            for uid, u in pre_units.items():
                if u["player"] != seat:
                    continue
                f = per_unit_cmd.get(uid)
                role = role_of.get(uid, "?")
                cell = (u["x"], u["y"])
                action = "WAIT" if f is None else f[0]
                in_window = t <= FUNDING_WINDOW
                if in_window:
                    rec["action_counts"][role][action] += 1
                if action == "WAIT" and in_window:
                    tree = pre_plants.get(cell)
                    if tree and tree["health"] > 0 and tree["fruits"] == 0:
                        rec["idle_wait_on_empty_tree"] += 1
                    else:
                        rec["idle_wait_elsewhere"] += 1
                if action == "PLANT" and len(f) == 3:
                    kind = f[2]
                    is_orchard = kind in ("LEMON", "PLUM") and own_trolls_now < 3
                    rec["plants"].append(dict(turn=t, troll=role, cell=cell, kind=kind,
                                               dist=geo["dist_from_shack"].get(cell), orchard=is_orchard))
                    if is_orchard:
                        rec["planted_cells"].add(cell)
                if action == "HARVEST" and in_window:
                    tree = pre_plants.get(cell)
                    if tree:
                        rec["harvests"].append(dict(turn=t, troll=role, cell=cell, kind=tree["type"],
                                                     fruits_before=tree["fruits"], full_before=tree["fruits"] >= 3,
                                                     dist=geo["dist_from_shack"].get(cell),
                                                     orchard=cell in rec["planted_cells"]))
                if action == "DROP" and in_window:
                    load = sum(u["carry"])
                    rec["drops"].append(dict(turn=t, troll=role, cell=cell, load=load))
                    rec["total_drop_items"] += load
                    if load == 1:
                        rec["one_item_drops"] += 1
                    elif load > 1:
                        rec["multi_item_drops"] += 1
                if action == "MINE" and in_window:
                    rec["mines"].append(dict(turn=t, troll=role, cell=cell))
                if action == "PICK" and len(f) == 3 and in_window:
                    rec["picks"].append(dict(turn=t, troll=role, kind=f[2]))

            if t <= 12:
                rec["opening12"].append(dict(
                    turn=t, inv=list(pre_inv[seat]),
                    cmds={role_of.get(uid, "?"): " ".join(per_unit_cmd[uid]) if uid in per_unit_cmd else "WAIT"
                          for uid, u in pre_units.items() if u["player"] == seat}))

            if own_trolls_now < 3 and (t % 2 == 1 or t <= 20):
                bill = training_cost(2, 2, 3, 0, 3)
                rec["bill_series"].append(dict(turn=t, inv={k: pre_inv[seat][ITEM_NAMES.index(k)] for k in BILL_ITEMS}, bill=bill))

            # advance the engine, then overlay the platform's own diff (reconstruct.py's method)
            r._pre_units = {u.id: (u.x, u.y, list(u.carry)) for u in r.game.units}
            r._pre_plants = [(p.pos, p.size, p.fruits, p.health) for p in r.game.plants]
            step(r.game, c0, c1)
            j = rc.view_payload(r.frames[2 * t].get("view"))
            inv_after = [[int(v) for v in ln.split()] for ln in j["inputmodule"].split("\n")]
            r.apply_diff(t, j.get("diff", ""), inv_after)

            post_units = {u.id: u for u in r.game.units}
            for uid, f in per_unit_cmd.items():
                if f[0] == "MOVE" and len(f) == 4 and t <= FUNDING_WINDOW:
                    tx, ty = int(f[2]), int(f[3])
                    pre_cell = (pre_units[uid]["x"], pre_units[uid]["y"])
                    if (tx, ty) == pre_cell:
                        continue
                    post = post_units.get(uid)
                    if post and (post.x, post.y) == pre_cell:
                        rec["stuck_moves"] += 1

            if train_cmd:
                new_ids = [uid for uid in post_units if uid not in pre_units and post_units[uid].player == seat]
                success = len(new_ids) > 0
                rec["trains_issued"].append(dict(turn=t, cmd=" ".join(train_cmd), success=success,
                                                  own_trolls_before=own_trolls_now))
                if success:
                    nid = new_ids[0]
                    role = "B" if own_trolls_before == 1 else "C"
                    role_of[nid] = role
                    own_trolls_before = max(own_trolls_before, own_trolls_now + 1)
                    if role == "B":
                        rec["second"] = dict(turn=t, talents=train_cmd[1:5])
                    elif role == "C":
                        rec["third"] = dict(turn=t, talents=train_cmd[1:5])

        per_game.append(rec)
      except Exception as e:
        skipped.append((g.get("gameId"), f"{type(e).__name__}: {e}"))
    if skipped:
        print(f"  [skipped {len(skipped)}/{len(raw_games)} games -- malformed/edge-case replay: "
              f"{skipped[:5]}{' ...' if len(skipped) > 5 else ''}]", file=sys.stderr)
    return per_game


def pct(n, d):
    return f"{100.0*n/d:.1f}%" if d else "n/a"


def main():
    path, agent_id = sys.argv[1], int(sys.argv[2])
    max_games = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rows = analyze(path, agent_id, max_games)
    iron_rows = [r for r in rows if r["iron_map"]]
    free_rows = [r for r in rows if not r["iron_map"]]
    print(f"games analyzed: {len(rows)}  iron maps: {len(iron_rows)}  iron-free maps: {len(free_rows)}")

    def med(lst):
        return statistics.median(lst) if lst else None

    for label, sub in (("ALL", rows), ("IRON maps", iron_rows), ("IRON-FREE maps", free_rows)):
        if not sub:
            print(f"\n=== {label} (n=0) ===")
            continue
        third_turns = [r["third"]["turn"] for r in sub if r["third"]]
        second_turns = [r["second"]["turn"] for r in sub if r["second"]]
        print(f"\n=== {label} (n={len(sub)}) ===")
        print(f"  trained 2nd troll: {len(second_turns)}/{len(sub)}  median turn {med(second_turns)}")
        print(f"  trained 3rd troll: {len(third_turns)}/{len(sub)}  median turn {med(third_turns)}  "
              f"min {min(third_turns) if third_turns else None} max {max(third_turns) if third_turns else None}")
        if second_turns:
            talents = Counter(tuple(r["second"]["talents"]) for r in sub if r["second"])
            print(f"  2nd troll talents: {talents.most_common(6)}")
        if third_turns:
            talents = Counter(tuple(r["third"]["talents"]) for r in sub if r["third"])
            print(f"  3rd troll talents: {talents.most_common(6)}")
        fails = sum(1 for r in sub for tr in r["trains_issued"] if not tr["success"])
        total_train_cmds = sum(len(r["trains_issued"]) for r in sub)
        pts = sum(r["pick_train_same_turn"] for r in sub)
        print(f"  TRAIN commands issued: {total_train_cmds}  failed (no new unit that turn): {fails}")
        print(f"  turns with PICK and TRAIN both issued by us: {pts}")
        stuck = sum(r["stuck_moves"] for r in sub)
        moves = sum(r["action_counts"][role].get("MOVE", 0) for r in sub for role in r["action_counts"])
        print(f"  MOVE commands (<= turn {FUNDING_WINDOW}): {moves}  stuck (0 displacement): {stuck} ({pct(stuck, moves)})")
        one = sum(r["one_item_drops"] for r in sub); multi = sum(r["multi_item_drops"] for r in sub)
        print(f"  DROP events: {one+multi}  one-item: {one} ({pct(one, one+multi)})  multi-item: {multi}")
        iwe = sum(r["idle_wait_on_empty_tree"] for r in sub); iwo = sum(r["idle_wait_elsewhere"] for r in sub)
        print(f"  WAIT turns: on-a-barren-tree {iwe}  elsewhere {iwo}")
        agg = defaultdict(Counter)
        for r in sub:
            for role, c in r["action_counts"].items():
                agg[role].update(c)
        for role in sorted(agg):
            tot = sum(agg[role].values())
            print(f"  role {role} action mix (n={tot}): {dict(agg[role].most_common())}")
        all_plants = [p for r in sub for p in r["plants"]]
        plants = [p for p in all_plants if p["orchard"]]
        other_plants = [p for p in all_plants if not p["orchard"]]
        print(f"  ORCHARD PLANT events (LEMON/PLUM while <3 own trolls): {len(plants)} over {len(sub)} games "
              f"({len(plants)/len(sub):.2f}/game)  kinds: {Counter(p['kind'] for p in plants)}  "
              f"dist-to-shack: {Counter(p['dist'] for p in plants).most_common(6)}  "
              f"turns: median {med([p['turn'] for p in plants])} min {min([p['turn'] for p in plants], default=None)} max {max([p['turn'] for p in plants], default=None)}")
        print(f"  (other, non-orchard plants elsewhere in the game -- a different mechanic, out of scope: {len(other_plants)}, "
              f"kinds {Counter(p['kind'] for p in other_plants)}, turn range "
              f"{min([p['turn'] for p in other_plants], default=None)}-{max([p['turn'] for p in other_plants], default=None)})")
        harvests = [h for r in sub for h in r["harvests"]]
        orch = [h for h in harvests if h["orchard"]]
        wild = [h for h in harvests if not h["orchard"]]
        print(f"  HARVEST events: {len(harvests)}  orchard: {len(orch)} ({pct(len(orch), len(harvests))})  wild: {len(wild)}")
        zero = [h for h in harvests if h["fruits_before"] == 0]
        print(f"  HARVEST with 0 fruit on the tree (a no-op / idle-park): {len(zero)} ({pct(len(zero), len(harvests))})")
        real = [h for h in harvests if h["fruits_before"] > 0]
        full = [h for h in real if h["full_before"]]
        print(f"  of the {len(real)} harvests that actually gained fruit: from a FULL(3) tree {len(full)} ({pct(len(full), len(real))})")
        print(f"  fruits-on-tree-before-harvest histogram (all HARVEST cmds): {sorted(Counter(h['fruits_before'] for h in harvests).items())}")
        print(f"  orchard-harvest fruits-before histogram: {sorted(Counter(h['fruits_before'] for h in orch).items())}")
        wilddist = Counter(h["dist"] for h in wild if h["fruits_before"] > 0)
        print(f"  wild REAL-harvest (fruit>0) distance-from-shack histogram: {sorted(wilddist.items())}")
        mines = [m for r in sub for m in r["mines"]]
        print(f"  MINE events: {len(mines)} ({len(mines)/len(sub):.2f}/game)")
        # bill: binding constraint + turns complete before train
        binding = Counter()
        wait_after_complete = []
        for r in sub:
            if not r["third"] or not r["bill_series"]:
                continue
            tt = r["third"]["turn"]
            complete_turn = None
            for b in r["bill_series"]:
                if all(b["inv"][k] >= b["bill"][k] for k in BILL_ITEMS):
                    complete_turn = b["turn"]
                    break
            if complete_turn:
                wait_after_complete.append(tt - complete_turn)
            last = r["bill_series"][-1]
            worst = max(BILL_ITEMS, key=lambda k: max(0, last["bill"][k] - last["inv"][k]))
            binding[worst] += 1
        print(f"  binding (last-to-complete) bill item across games with a 3rd troll: {binding.most_common()}")
        if wait_after_complete:
            print(f"  turns bill was complete before TRAIN fired: median {med(wait_after_complete)}  "
                  f"min {min(wait_after_complete)} max {max(wait_after_complete)}  "
                  f"(n={len(wait_after_complete)}, sampled every-other-turn so +/-1)")

    import os
    outdir = os.path.dirname(os.path.abspath(__file__))
    slim = []
    for r in rows:
        s = dict(r)
        s["action_counts"] = {k: dict(v) for k, v in r["action_counts"].items()}
        s["planted_cells"] = list(r["planted_cells"])
        slim.append(s)
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(slim, fh, default=str)
    print(f"\nwrote {os.path.join(outdir, 'summary.json')}")


if __name__ == "__main__":
    main()
