#!/usr/bin/env python3
"""plan_end.py -- three open questions about Bubaptik's training plan, from the raw replays:
 A. the speed-1 fallback for troll 3: what differs in those games (plum trees, plum income)?
 B. is the harvest->chop switch tied to the LAST train or to every train?
 C. what ends the plan: was the next troll ever affordable in games that stopped at 2, 3, 4?
 D. plant and pick types before/after the last train.
Reads the same files as train_trigger.py; writes plan_end.json next to this file.
"""
import json, os, re, sys, statistics
from collections import Counter, defaultdict

DATA = "/home/tarstars/prj/troll_farm/data"
HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = int(sys.argv[1]) if len(sys.argv) > 1 else 6568138
TYPE36 = {0: "PLUM", 1: "LEMON", 2: "APPLE", 3: "BANANA"}
RE_HARV = re.compile(r"troll (\d+) harvested (\d+) (PLUM|LEMON|APPLE|BANANA)")
RE_PLANT = re.compile(r"troll (\d+) planted a (\w+)")


def b36(c):
    return int(c, 36)


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) >= 2 else [xs[0]] * 3
    return {"n": len(xs), "mean": round(statistics.fmean(xs), 2), "median": statistics.median(xs),
            "p25": q[0], "p75": q[2], "min": xs[0], "max": xs[-1]}


def cost(n, tal):
    ms, cc, hp, ch = tal
    return [n + ms * ms, n + cc * cc, n + hp * hp, 0, n + ch * ch]


def affordable(inv, c):
    return all(inv[i] >= c[i] for i in (0, 1, 2, 4))


def parse_cmds(so):
    return [chunk.split() for chunk in so.replace("\n", ";").split(";") if chunk.split()]


def load_raw(path):
    d = json.load(open(path))
    frames = d["frames"]
    j0 = json.loads(frames[0]["view"].split("\n", 1)[1])
    grid = j0["global"]["inputmodule"].split("\n")
    w, h = (int(v) for v in grid[0].split())
    init_inv = [[int(v) for v in ln.split()] for ln in j0["frame"]["inputmodule"].split("\n")]
    plants0 = []
    for ent in j0["frame"]["diff"].split(";"):
        p = ent.split()
        if len(p) == 3 and p[1] == "P" and len(p[2]) == 7:
            v = p[2]
            plants0.append({"x": b36(v[0]), "y": b36(v[1]), "type": TYPE36.get(b36(v[2]), "?"), "stage": b36(v[3])})
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
            new_trolls = []
            for ent in (j.get("diff") or "").split(";"):
                p = ent.split()
                if len(p) >= 3 and p[1] == "W" and len(p[2]) == 8:
                    new_trolls.append(b36(p[2][3]))   # owner
            turns.append({"cmds": {p: parse_cmds("\n".join(pending[p])) for p in (0, 1)},
                          "inv": inv, "summary": f.get("summary") or "", "new_trolls": new_trolls})
            pending = {0: [], 1: []}
    return w, h, init_inv, plants0, turns


games = []
with open(os.path.join(DATA, "processed", "games.jsonl")) as fh:
    for line in fh:
        if "Bubaptik" not in line:
            continue
        g = json.loads(line)
        for pl in g["players"]:
            if pl["name"] == "Bubaptik" and pl["agentId"] == AGENT:
                games.append((g, pl["index"]))

A = []                       # troll-3 purchases with context
B = defaultdict(lambda: defaultdict(Counter))   # rank -> window -> verbs
Bn = defaultdict(Counter)
C = []                       # plan end
D = defaultdict(Counter)     # before/after last train -> plant type
Dp = defaultdict(Counter)    # before/after last train -> pick type
last_train_turns = []
train_attempt_last = []
for g, seat in games:
    path = os.path.join(DATA, "raw", "games", f"{g['gameId']}.json")
    if not os.path.exists(path):
        continue
    w, h, init_inv, plants0, turns = load_raw(path)
    n_turns = len(turns)

    def inv_before(t):
        return init_inv[seat] if t == 1 else (turns[t - 2]["inv"] or [0] * 6)[seat]

    own_half = (lambda x: x < w / 2) if seat == 0 else (lambda x: x >= w / 2)
    plum_trees_own_half = sum(1 for p in plants0 if p["type"] == "PLUM" and own_half(p["x"]))
    plum_trees_total = sum(1 for p in plants0 if p["type"] == "PLUM")
    lemon_trees_own_half = sum(1 for p in plants0 if p["type"] == "LEMON" and own_half(p["x"]))
    # successful trains of this seat: from new_trolls (owner == seat) after turn 1
    my_trains = []           # (turn, talents)
    all_attempts = []
    n_trolls = 1
    opp_trolls = 1
    plum_harv = 0
    plum_plants = 0
    lemon_harv = 0
    cum = []                 # per turn (plum_harv, plum_plants, opp_trolls) before the turn
    for i, tr in enumerate(turns):
        t = i + 1
        cum.append((plum_harv, plum_plants, lemon_harv, opp_trolls))
        for p in tr["cmds"][seat]:
            if p[0].upper() == "TRAIN" and len(p) >= 5:
                all_attempts.append(t)
        n_new = sum(1 for o in tr["new_trolls"] if o == seat)
        if n_new:
            for p in tr["cmds"][seat]:
                if p[0].upper() == "TRAIN" and len(p) >= 5:
                    my_trains.append((t, tuple(int(v) for v in p[1:5]), n_trolls))
                    n_trolls += 1
                    break
        opp_trolls += sum(1 for o in tr["new_trolls"] if o != seat)
        for ln in tr["summary"].split("\n"):
            if not ln.startswith(f"${seat}"):
                continue
            m = RE_HARV.search(ln)
            if m:
                if m.group(3) == "PLUM":
                    plum_harv += int(m.group(2))
                if m.group(3) == "LEMON":
                    lemon_harv += int(m.group(2))
            m = RE_PLANT.search(ln)
            if m and m.group(2).upper() == "PLUM":
                plum_plants += 1
    # A
    for (t, tal, n) in my_trains:
        if n == 2:      # troll 3
            ph, pp, lh, ot = cum[t - 1]
            plum_max_before = max(inv_before(u)[0] for u in range(1, t + 1))
            A.append({"gameId": g["gameId"], "turn": t, "talents": list(tal), "plum_trees_own_half_start": plum_trees_own_half,
                      "plum_trees_total_start": plum_trees_total, "lemon_trees_own_half_start": lemon_trees_own_half,
                      "plums_harvested_before": ph, "plums_planted_before": pp, "lemons_harvested_before": lh,
                      "opp_trolls_at_train": ot, "plum_stock_max_before": plum_max_before,
                      "stock_before": inv_before(t), "map_w": w, "map_h": h, "n_trains_total": len(my_trains)})
    # B: windows around each train, by rank and whether it is the last one
    for k, (t, tal, n) in enumerate(my_trains):
        is_last = (k == len(my_trains) - 1)
        label = f"rank{n + 1}_{'last' if is_last else 'not_last'}"
        for i, tr in enumerate(turns):
            rel = (i + 1) - t
            if -20 <= rel < 20:
                wname = "before(-20..-1)" if rel < 0 else "after(0..19)"
                for p in tr["cmds"][seat]:
                    B[label][wname][p[0].upper()] += 1
                Bn[label][wname] += 1
    # C: plan end
    n_end = 1 + len(my_trains)
    c_fast = cost(n_end, (4, 3, 0, 2))
    c_cheap = cost(n_end, (1, 3, 0, 2))
    first_fast = next((t for t in range(1, n_turns + 1) if affordable(inv_before(t), c_fast)), None)
    first_cheap = next((t for t in range(1, n_turns + 1) if affordable(inv_before(t), c_cheap)), None)
    last_t = my_trains[-1][0] if my_trains else None
    C.append({"gameId": g["gameId"], "trolls_end": n_end, "last_train_turn": last_t, "n_turns": n_turns,
              "next_fast_first_affordable": first_fast, "next_cheap_first_affordable": first_cheap,
              "last_train_attempt": max(all_attempts) if all_attempts else None,
              "attempts_after_last_success": sum(1 for a in all_attempts if last_t and a > last_t)})
    if last_t:
        last_train_turns.append(last_t)
    if all_attempts:
        train_attempt_last.append(max(all_attempts))
    # D
    if last_t:
        for i, tr in enumerate(turns):
            wname = "before_last_train" if (i + 1) < last_t else "after_last_train"
            for p in tr["cmds"][seat]:
                if p[0].upper() == "PLANT" and len(p) >= 3:
                    kind = p[-1].upper()
                    kind = TYPE36.get(int(kind), kind) if kind.isdigit() else kind
                    D[wname][kind] += 1
                if p[0].upper() == "PICK" and len(p) >= 3:
                    kind = p[-1].upper()
                    kind = TYPE36.get(int(kind), kind) if kind.isdigit() else kind
                    Dp[wname][kind] += 1

# ---- summaries
def grp(rows, key):
    return {k: stats([r[key] for r in rows]) for k in ["x"]}["x"]

s1 = [r for r in A if r["talents"][0] == 1]
s4 = [r for r in A if r["talents"][0] == 4]
other = [r for r in A if r["talents"][0] not in (1, 4)]
def ctx(rows):
    return {"n": len(rows),
            "turn": stats([r["turn"] for r in rows]),
            "plum_trees_own_half_start": stats([r["plum_trees_own_half_start"] for r in rows]),
            "plum_trees_total_start": stats([r["plum_trees_total_start"] for r in rows]),
            "plums_harvested_before": stats([r["plums_harvested_before"] for r in rows]),
            "plums_planted_before": stats([r["plums_planted_before"] for r in rows]),
            "lemons_harvested_before": stats([r["lemons_harvested_before"] for r in rows]),
            "plum_stock_max_before": stats([r["plum_stock_max_before"] for r in rows]),
            "opp_trolls_at_train": dict(Counter(r["opp_trolls_at_train"] for r in rows)),
            "map_h": dict(Counter(r["map_h"] for r in rows)),
            "n_trains_total": dict(Counter(r["n_trains_total"] for r in rows)),
            "share_with_zero_plum_trees_on_own_half": round(sum(1 for r in rows if r["plum_trees_own_half_start"] == 0) / len(rows), 3) if rows else None}
out = {
    "agent": AGENT, "games": len(games),
    "A_troll3_speed1": ctx(s1), "A_troll3_speed4": ctx(s4), "A_troll3_other": ctx(other),
    "A_speed1_rows": s1,
    "B_verbs_per_turn_around_each_train": {lab: {wn: {"turns": Bn[lab][wn], **{v: round(c / Bn[lab][wn], 2) for v, c in B[lab][wn].most_common()}}
                                                for wn in B[lab]} for lab in sorted(B)},
    "C_plan_end": {
        "trolls_at_end": dict(Counter(r["trolls_end"] for r in C)),
        "last_train_turn": stats(last_train_turns),
        "last_train_attempt_turn": stats(train_attempt_last),
        "attempts_after_last_success": dict(Counter(r["attempts_after_last_success"] for r in C)),
        "by_trolls_end": {},
    },
    "D_plant_types": {k: dict(v) for k, v in D.items()},
    "D_pick_types": {k: dict(v) for k, v in Dp.items()},
}
for n_end in sorted({r["trolls_end"] for r in C}):
    rs = [r for r in C if r["trolls_end"] == n_end]
    out["C_plan_end"]["by_trolls_end"][str(n_end)] = {
        "games": len(rs),
        "next_fast_troll_ever_affordable": sum(1 for r in rs if r["next_fast_first_affordable"] is not None),
        "next_fast_first_affordable_turn": stats([r["next_fast_first_affordable"] for r in rs]),
        "next_cheap_troll_ever_affordable": sum(1 for r in rs if r["next_cheap_first_affordable"] is not None),
        "next_cheap_first_affordable_turn": stats([r["next_cheap_first_affordable"] for r in rs]),
        "next_cheap_first_affordable_hist_25": dict(sorted(Counter((r["next_cheap_first_affordable"] // 25) * 25 for r in rs if r["next_cheap_first_affordable"]).items())),
        "last_train_turn": stats([r["last_train_turn"] for r in rs]),
    }
json.dump(out, open(os.path.join(HERE, "plan_end.json"), "w"), indent=1)
o = dict(out)
o.pop("A_speed1_rows")
print(json.dumps(o, indent=1))
print("SPEED1 ROWS (turn, talents, plum trees own half/total, plums harvested, planted, plum max stock, opp trolls, stock):")
for r in s1:
    print(r["turn"], r["talents"], r["plum_trees_own_half_start"], r["plum_trees_total_start"], r["plums_harvested_before"], r["plums_planted_before"], r["plum_stock_max_before"], r["opp_trolls_at_train"], r["stock_before"], r["n_trains_total"])
