#!/usr/bin/env python3
"""Track E: the top four from the fits' per-turn tables (`local_claude_1/reconstructions/fits/tables/
<player>_turns.jsonl.gz`, one row per player-turn of every 300-turn game, exact inventories and roster
from the referee diff). Gives per player: score at turns 250 and 300 for both seats (score = fruit in
the shack + 4 x wood), the last-fifty-turn gain split by who led at 250, the exact roster per phase and
the share of turns with fewer unit commands than trolls (from the `verbs` list, one entry per command).
"""
import gzip, json, collections, sys
PHASES = (("p1_100", 1, 100), ("p101_200", 101, 200), ("p201_250", 201, 250), ("p251_300", 251, 300))
def phase_of(t):
    for n, lo, hi in PHASES:
        if lo <= t <= hi:
            return n
def score(inv): return inv[0]+inv[1]+inv[2]+inv[3]+4*inv[5]
out = {}
for player in ("delineate", "norxondor", "MSz", "Bubaptik"):
    rows = collections.defaultdict(dict)
    agg = collections.defaultdict(collections.Counter)
    with gzip.open(f"local_claude_1/reconstructions/fits/tables/{player}_turns.jsonl.gz", "rt") as fh:
        for l in fh:
            r = json.loads(l)
            key = (r["g"], r["seat"])
            if r["t"] in (250, 300):
                rows[key][r["t"]] = r
            ph = phase_of(r["t"])
            a = agg[ph]
            a["turns"] += 1; a["roster"] += r["n"]; a["roster_opp"] += r["n_opp"]
            a["cmds"] += len(r["verbs"]); a["MOVE"] += r["verbs"].count("MOVE")
            a["fewer_cmds_than_trolls"] += 1 if len([v for v in r["verbs"] if v not in ("TRAIN","MSG","WAIT")]) < r["n"] else 0
            a["trees"] += r["trees"]; a["trees_fruit"] += r["trees_fruit"]
    games = []
    for key, d in rows.items():
        if 250 in d and 300 in d:
            a, b = d[250], d[300]
            # row t=300 holds the pre-turn-300 inventory; the final is after turn 300 -- one turn short, noted
            games.append({"g": key[0], "seat": key[1], "own_250": score(a["inv"]), "opp_250": score(a["inv_opp"]),
                          "own_300": score(b["inv"]), "opp_300": score(b["inv_opp"]), "n_250": a["n"], "n_opp_250": a["n_opp"]})
    led = [g for g in games if g["own_250"] > g["opp_250"]]; trailed = [g for g in games if g["own_250"] <= g["opp_250"]]
    res = {"games": len(games), "phases": {}}
    for ph, a in agg.items():
        t = a["turns"]
        res["phases"][ph] = {"turns": t, "roster_per_turn": round(a["roster"]/t, 3), "opp_roster_per_turn": round(a["roster_opp"]/t, 3),
                             "cmds_per_turn": round(a["cmds"]/t, 3), "MOVE_per_turn": round(a["MOVE"]/t, 3),
                             "MOVE_per_troll_turn": round(a["MOVE"]/max(a["roster"],1), 4),
                             "fewer_cmds_than_trolls_share": round(a["fewer_cmds_than_trolls"]/t, 4),
                             "trees_per_turn": round(a["trees"]/t, 2), "trees_with_fruit_per_turn": round(a["trees_fruit"]/t, 2)}
    for name, grp in (("led", led), ("trailed", trailed), ("all", games)):
        if grp:
            res[name] = {"n": len(grp), "own_gain_250_300": round(sum(g["own_300"]-g["own_250"] for g in grp)/len(grp), 1),
                         "opp_gain_250_300": round(sum(g["opp_300"]-g["opp_250"] for g in grp)/len(grp), 1),
                         "own_250_mean": round(sum(g["own_250"] for g in grp)/len(grp), 1),
                         "final_wins": sum(1 for g in grp if g["own_300"] > g["opp_300"])}
    out[player] = res
    print(player, json.dumps({k: v for k, v in res.items() if k != "phases"}))
    for ph, _, _ in PHASES:
        print("   ", ph, json.dumps(res["phases"][ph]))
json.dump(out, open("claude_1/endgame-gap/top4-tables.json", "w"), indent=1, sort_keys=True)
