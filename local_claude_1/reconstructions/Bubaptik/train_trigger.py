#!/usr/bin/env python3
"""train_trigger.py -- what the behaviour profile does not measure: Bubaptik's TRAIN decisions
against its shack stock, the switch from harvesting to chopping around the last TRAIN, the
inventory/score curves, and the version history across all of its agent ids.

Reads (read-only): /home/tarstars/prj/troll_farm/data/processed/games.jsonl and the raw replays
/home/tarstars/prj/troll_farm/data/raw/games/<gameId>.json (same parsing as profiles/profile_bot.py).
Writes: train_trigger.json next to this file.  Usage: python3 train_trigger.py [agent_id]
"""
import json, os, sys, statistics
from collections import Counter, defaultdict

DATA = "/home/tarstars/prj/troll_farm/data"
HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = int(sys.argv[1]) if len(sys.argv) > 1 else 6568138
ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) >= 2 else [xs[0]] * 3
    return {"n": len(xs), "mean": round(statistics.fmean(xs), 2), "median": statistics.median(xs),
            "p25": q[0], "p75": q[2], "min": xs[0], "max": xs[-1]}


def cost(n_trolls, tal):
    ms, cc, hp, ch = tal
    return [n_trolls + ms * ms, n_trolls + cc * cc, n_trolls + hp * hp, 0, n_trolls + ch * ch]


def affordable(inv, c):
    return all(inv[i] >= c[i] for i in (0, 1, 2, 4))


def parse_cmds(so):
    out = []
    for chunk in so.replace("\n", ";").split(";"):
        p = chunk.split()
        if p:
            out.append(p)
    return out


def load_raw(path):
    d = json.load(open(path))
    frames = d["frames"]
    j0 = json.loads(frames[0]["view"].split("\n", 1)[1])
    init_inv = [[int(v) for v in ln.split()] for ln in j0["frame"]["inputmodule"].split("\n")]
    turns = []
    pending = {0: [], 1: []}
    for f in frames[1:]:
        a, so = f.get("agentId"), f.get("stdout")
        if so is not None and a in (0, 1):
            pending[a].append(so)
        if f.get("keyframe"):
            view = f.get("view") or ""
            j = json.loads(view.split("\n", 1)[1]) if "{" in view else {}
            lines = (j.get("inputmodule") or "").split("\n")
            inv = [[int(v) for v in ln.split()] for ln in lines] if len(lines) == 2 else None
            turns.append({"cmds": {p: parse_cmds("\n".join(pending[p])) for p in (0, 1)},
                          "inv": inv, "summary": f.get("summary") or ""})
            pending = {0: [], 1: []}
    return init_inv, turns


# ------------------------------------------------------------------ 1. version history (games.jsonl)
games = []
by_id = defaultdict(lambda: {"games": 0, "wins": 0, "score": [], "opp": [], "arena": [], "trains": [],
                             "trolls_end": [], "gids": []})
with open(os.path.join(DATA, "processed", "games.jsonl")) as fh:
    for line in fh:
        if "Bubaptik" not in line:
            continue
        g = json.loads(line)
        for pl in g["players"]:
            if pl["name"] != "Bubaptik":
                continue
            aid, seat = pl["agentId"], pl["index"]
            rec = by_id[aid]
            rec["games"] += 1
            rec["gids"].append(g["gameId"])
            rec["wins"] += 1 if g["ranks"][seat] == 0 else 0
            rec["score"].append(g["scores"][seat])
            rec["opp"].append(g["scores"][1 - seat])
            rec["arena"].append(pl.get("arenaScore"))
            pp = g["per_player"][str(seat)]
            rec["trains"].append(pp.get("trains", []))
            rec["trolls_end"].append(1 + len(pp.get("trains", [])))
            if aid == AGENT:
                games.append((g, seat))

versions = []
for aid, rec in sorted(by_id.items()):
    tal_by_rank = defaultdict(Counter)
    turn_by_rank = defaultdict(list)
    for tr in rec["trains"]:
        for k, (t, tal) in enumerate(tr):
            tal_by_rank[k + 2][tuple(tal)] += 1
            turn_by_rank[k + 2].append(t)
    versions.append({
        "agent_id": aid, "games": rec["games"], "win_rate": round(rec["wins"] / rec["games"], 3),
        "mean_score": round(statistics.fmean(rec["score"]), 1), "mean_opp_score": round(statistics.fmean(rec["opp"]), 1),
        "arena_score_mean": round(statistics.fmean([a for a in rec["arena"] if a is not None]), 2) if any(a is not None for a in rec["arena"]) else None,
        "arena_score_max": max([a for a in rec["arena"] if a is not None], default=None),
        "trolls_at_end_mean": round(statistics.fmean(rec["trolls_end"]), 2),
        "speed4_share_of_games": round(sum(1 for tr in rec["trains"] if any(tal[0] == 4 for _, tal in tr)) / rec["games"], 3),
        "troll2_top": [(" ".join(map(str, k)), n) for k, n in tal_by_rank[2].most_common(3)],
        "troll3_top": [(" ".join(map(str, k)), n) for k, n in tal_by_rank[3].most_common(3)],
        "troll4_top": [(" ".join(map(str, k)), n) for k, n in tal_by_rank[4].most_common(3)],
        "troll2_turn_median": statistics.median(turn_by_rank[2]) if turn_by_rank[2] else None,
        "troll3_turn_median": statistics.median(turn_by_rank[3]) if turn_by_rank[3] else None,
        "troll4_turn_median": statistics.median(turn_by_rank[4]) if turn_by_rank[4] else None,
    })

# ------------------------------------------------------------------ 2. raw replays of AGENT
turn2 = []            # first TRAIN when it is on turn 2 (or the first TRAIN at all)
trains = []           # every TRAIN
curves = defaultdict(list)   # turn -> list of (own inv, opp inv)
switch = defaultdict(Counter)  # window relative to last TRAIN -> verb counts
switch_n = Counter()
inv_order_ok = 0
inv_order_bad = 0
missing_raw = 0
for g, seat in games:
    path = os.path.join(DATA, "raw", "games", f"{g['gameId']}.json")
    if not os.path.exists(path):
        missing_raw += 1
        continue
    init_inv, turns = load_raw(path)
    n_turns = len(turns)
    # inventory BEFORE turn t (1-based): init for t=1, else turns[t-2].inv
    def inv_before(t):
        return init_inv[seat] if t == 1 else (turns[t - 2]["inv"] or [0] * 6)[seat]
    n_trolls = 1
    my_trains = []
    for i, tr in enumerate(turns):
        t = i + 1
        for p in tr["cmds"][seat]:
            if p[0].upper() == "TRAIN" and len(p) >= 5:
                tal = tuple(int(v) for v in p[1:5])
                ok = f"${seat}: trained a troll" in tr["summary"] or ("trained" in tr["summary"] and f"${seat}" in tr["summary"])
                my_trains.append((t, tal, ok))
    # verify the referee's train events instead of the summary text: count W entries per seat is
    # heavier; use the failure text: "[failed]" with "afford" or "blocked" for this seat
    for k, (t, tal, ok) in enumerate(my_trains):
        c = cost(n_trolls, tal)
        before = inv_before(t)
        after = (turns[t - 1]["inv"] or [0] * 6)[seat]
        failed = any(("[failed]" in ln and f"${seat}" in ln and ("afford" in ln or "blocked" in ln))
                     for ln in turns[t - 1]["summary"].split("\n"))
        if failed:
            continue
        # sanity: own line should drop by the cost in plum/lemon/apple/iron (up to same-turn pick/drop)
        drop_ok = all(before[i] - after[i] >= c[i] - 3 for i in (0, 1, 2, 4))
        inv_order_ok += drop_ok
        inv_order_bad += (not drop_ok)
        # how long affordable before t: walk back while affordable
        first_aff = t
        while first_aff > 1 and affordable(inv_before(first_aff - 1), c):
            first_aff -= 1
        # best affordable talent per resource at t (independent per resource)
        def best(level0_ok, stock):
            k = 0 if level0_ok else 1
            while n_trolls + (k + 1) ** 2 <= stock:
                k += 1
            return k
        best_tal = (best(False, before[0]), best(False, before[1]), best(True, before[2]), best(True, before[4]))
        rec = {"gameId": g["gameId"], "seat": seat, "rank": k + 2, "turn": t, "talents": list(tal),
               "n_trolls_before": n_trolls, "cost_plum_lemon_apple_iron": [c[0], c[1], c[2], c[4]],
               "stock_before": before, "affordable_at_t": affordable(before, c),
               "first_affordable_turn": first_aff, "delay_turns": t - first_aff,
               "best_affordable_per_resource": list(best_tal),
               "n_turns": n_turns}
        trains.append(rec)
        if k == 0:
            rec2 = dict(rec)
            rec2["start_stock"] = init_inv[seat]
            turn2.append(rec2)
        n_trolls += 1
    # curves
    for t in (1, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300):
        if t <= n_turns and turns[t - 1]["inv"]:
            curves[t].append((turns[t - 1]["inv"][seat], turns[t - 1]["inv"][1 - seat]))
    # verb mix relative to the last successful TRAIN
    if trains and trains[-1]["gameId"] == g["gameId"]:
        last_t = trains[-1]["turn"]
        for i, tr in enumerate(turns):
            t = i + 1
            rel = t - last_t
            if -40 <= rel < 80:
                w = ("-40..-21" if rel < -20 else "-20..-1" if rel < 0 else "0..19" if rel < 20 else
                     "20..39" if rel < 40 else "40..59" if rel < 60 else "60..79")
                for p in tr["cmds"][seat]:
                    switch[w][p[0].upper()] += 1
                switch_n[w] += 1

# ------------------------------------------------------------------ 3. summaries
def summarize_turn2(rows):
    out = {"n": len(rows)}
    out["turn_hist"] = dict(Counter(r["turn"] for r in rows).most_common(8))
    on2 = [r for r in rows if r["turn"] == 2]
    out["n_on_turn_2"] = len(on2)
    # per-talent: actual vs best affordable per resource (independent maximisation)
    names = ["speed(plum)", "carry(lemon)", "harvest(apple)", "chop(iron)"]
    per = {}
    for i, nm in enumerate(names):
        cmp_ = Counter()
        for r in on2:
            a, b = r["talents"][i], r["best_affordable_per_resource"][i]
            cmp_["equal" if a == b else ("below_max" if a < b else "ABOVE_MAX(?)")] += 1
        per[nm] = dict(cmp_)
        # joint table actual x best
        per[nm + "_table_actual_by_best"] = {f"best={b}": dict(Counter(r["talents"][i] for r in on2 if r["best_affordable_per_resource"][i] == b))
                                            for b in sorted({r["best_affordable_per_resource"][i] for r in on2})}
    out["per_talent_vs_best_affordable"] = per
    out["all_four_equal_best"] = sum(1 for r in on2 if list(r["talents"]) == r["best_affordable_per_resource"])
    out["cost_share_of_start_stock"] = stats([sum(r["cost_plum_lemon_apple_iron"]) / max(1, sum(r["start_stock"][:3]) + r["start_stock"][4]) for r in on2])
    late = [r for r in rows if r["turn"] > 2]
    out["late_first_trains"] = [{"turn": r["turn"], "talents": r["talents"], "start_stock": r["start_stock"], "stock_before": r["stock_before"],
                                 "best_affordable_at_start": None, "delay_turns": r["delay_turns"]} for r in late]
    # start stock of the late ones: what was the best affordable on turn 2 with the start stock?
    for r, row in zip(late, out["late_first_trains"]):
        s = r["start_stock"]
        def best(level0_ok, stock):
            k = 0 if level0_ok else 1
            while 1 + (k + 1) ** 2 <= stock:
                k += 1
            return k
        row["best_affordable_at_start"] = [best(False, s[0]), best(False, s[1]), best(True, s[2]), best(True, s[4])]
    return out


def summarize_rank(rows, rank):
    rs = [r for r in rows if r["rank"] == rank]
    out = {"n": len(rs), "turn": stats([r["turn"] for r in rs]),
           "delay_turns_since_first_affordable": stats([r["delay_turns"] for r in rs]),
           "delay_hist": dict(sorted(Counter(min(r["delay_turns"], 10) for r in rs).items())),
           "affordable_at_t": sum(1 for r in rs if r["affordable_at_t"]),
           "stock_before_mean": [round(statistics.fmean(r["stock_before"][i] for r in rs), 1) for i in range(6)] if rs else None,
           "talents_top": [(" ".join(map(str, k)), n) for k, n in Counter(tuple(r["talents"]) for r in rs).most_common(6)],
           }
    # per talent: actual vs best affordable per resource at the train turn
    names = ["speed(plum)", "carry(lemon)", "harvest(apple)", "chop(iron)"]
    per = {}
    for i, nm in enumerate(names):
        per[nm] = {f"best={b}": dict(Counter(r["talents"][i] for r in rs if r["best_affordable_per_resource"][i] == b))
                   for b in sorted({r["best_affordable_per_resource"][i] for r in rs})}
    out["actual_talent_by_best_affordable"] = per
    # speed-1 late trolls: turn and plum stock
    s1 = [r for r in rs if r["talents"][0] == 1]
    out["speed1_trolls"] = {"n": len(s1), "turn": stats([r["turn"] for r in s1]),
                            "plum_stock_before": stats([r["stock_before"][0] for r in s1])}
    s4 = [r for r in rs if r["talents"][0] == 4]
    out["speed4_trolls"] = {"n": len(s4), "turn": stats([r["turn"] for r in s4]),
                            "plum_stock_before": stats([r["stock_before"][0] for r in s4]),
                            "lemon_stock_before": stats([r["stock_before"][1] for r in s4]),
                            "iron_stock_before": stats([r["stock_before"][4] for r in s4]),
                            "apple_stock_before": stats([r["stock_before"][2] for r in s4])}
    # chop 3 vs iron stock; harvest 1 vs apple stock
    out["chop_level_by_iron_stock"] = {}
    for r in rs:
        key = f"iron>={r['n_trolls_before'] + 9}" if r["stock_before"][4] >= r["n_trolls_before"] + 9 else "iron<chop3cost"
        out["chop_level_by_iron_stock"].setdefault(key, Counter())[r["talents"][3]] += 1
    out["chop_level_by_iron_stock"] = {k: dict(v) for k, v in out["chop_level_by_iron_stock"].items()}
    out["harvest_level_by_apple_stock"] = {}
    for r in rs:
        key = f"apple>={r['n_trolls_before'] + 1}" if r["stock_before"][2] >= r["n_trolls_before"] + 1 else "apple<harvest1cost"
        out["harvest_level_by_apple_stock"].setdefault(key, Counter())[r["talents"][2]] += 1
    out["harvest_level_by_apple_stock"] = {k: dict(v) for k, v in out["harvest_level_by_apple_stock"].items()}
    return out


result = {
    "agent": AGENT, "games": len(games), "missing_raw": missing_raw,
    "inventory_line_order_check": {"train_cost_seen_on_own_line": inv_order_ok, "not_seen": inv_order_bad},
    "versions": versions,
    "turn2_train": summarize_turn2(turn2),
    "troll3": summarize_rank(trains, 3),
    "troll4": summarize_rank(trains, 4),
    "troll5": summarize_rank(trains, 5),
    "curves": {str(t): {"own_mean": [round(statistics.fmean(v[0][i] for v in vs), 1) for i in range(6)],
                        "opp_mean": [round(statistics.fmean(v[1][i] for v in vs), 1) for i in range(6)],
                        "own_score_mean": round(statistics.fmean(sum(v[0][:4]) + 4 * v[0][5] for v in vs), 1),
                        "opp_score_mean": round(statistics.fmean(sum(v[1][:4]) + 4 * v[1][5] for v in vs), 1),
                        "n": len(vs)} for t, vs in sorted(curves.items())},
    "verb_mix_relative_to_last_train": {w: {"turns": switch_n[w], **{v: round(c / switch_n[w], 2) for v, c in switch[w].most_common()}}
                                        for w in ("-40..-21", "-20..-1", "0..19", "20..39", "40..59", "60..79") if switch_n[w]},
    "all_trains": trains,
}
json.dump(result, open(os.path.join(HERE, "train_trigger.json"), "w"), indent=1)
r = dict(result)
r.pop("all_trains")
print(json.dumps(r, indent=1))
