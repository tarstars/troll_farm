#!/usr/bin/env python3
"""The cheap third troll on paper: per-game net points for each design, from the replay facts (`games-*.json`,
`replay_read.py`) and the trip model (`detour-*.json`, `detour_cost.py`). Nothing is played.

Per game (319 games in which the champion trained its second troll):
  E        = the last turn with a tree to chop: the turn the last tree fell when the map ends empty, else the game's end
  r1(phase)= the starter's wood banked per troll-turn, pooled over the 320 games by phase (the 1/1/0/1 proxy:
             same speed, carry and chop under the same policy); r2 = the second troll's rate by its talents, pooled
  A1  strong troll first (as today), then the cheap bill: the starter harvests the fruit, the trained troll mines the
      iron, in parallel from the TRAIN turn; the third troll exists at T3 = train_turn + max(fruit, iron) turns
  A2  cheap troll first, at turn 1 (2/2/1/2 at n = 1: every Legend draw covers it), the champion's actual second
      troll at n = 2 afterwards: the starter harvests, the cheap troll mines; the strong troll is delayed by
      (cheap-first wall - the model's turns for today's opening), model against model so the calibration bias cancels
  B   A1 only in the games where the bill's wall is within N turns (N = 30, 60); nothing spent elsewhere
Costs: wood forgone by each collector (its turns x its rate x 4) and the bill's fruit (8 items: 3 plums, 3 lemons,
2 apples; bananas are free) - LOW: 1 point each, the score they were; HIGH: plus the seed value, 3 points more for
every fruit the champion would have planted and felled as a size-1 tree (plum/lemon 0.81 of the post-TRAIN bank,
apple 0.49, measured).
Earnings: U (ceiling) = r1 x the third troll's turns to E, uncontested; C (floor) = the share shift on the forest
felled after T3 - our felling share f becomes f k / (f k + 1 - f) with k = 1 + r1/(r1 + r2); point estimate
min(U, C + 4 x wood-units standing at the end).
"""
from __future__ import annotations
import json, random, statistics as S, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
PH = (("p1_100", 1, 100), ("p101_200", 101, 200), ("p201_250", 201, 250), ("p251_300", 251, 300))
FRUIT_ITEMS = 8
SEED_HIGH = 3 * (3 * 0.81 + 3 * 0.81 + 2 * 0.49)


def load():
    G, D = {}, {}
    for b in ("41202036", "41230202"):
        for g in json.load(open(HERE / f"games-{b}.json"))["games"]:
            G[g["gameId"]] = g
        for d in json.load(open(HERE / f"detour-{b}.json"))["games"]:
            D[d["gameId"]] = d
    return G, D


def rates(G):
    agg = collections.defaultdict(lambda: [collections.Counter(), collections.Counter(), 0, 0])
    for g in G.values():
        for u in g["units"]:
            if u["side"] != "ours":
                continue
            a = agg[u["talents"]]
            for ph, w in u["wood_by_phase"].items():
                a[0][ph] += w
            for ph, n in u["turns_by_phase"].items():
                a[1][ph] += n
            a[2] += u["wood"]
            a[3] += u["turns"]
    r1 = {ph: agg["1/1/1/1"][0][ph] / agg["1/1/1/1"][1][ph] for ph, _, _ in PH}
    r2 = {t: a[2] / a[3] for t, a in agg.items() if t != "1/1/1/1" and a[3] >= 1000}
    r2_all = sum(a[2] for t, a in agg.items() if t != "1/1/1/1") / sum(a[3] for t, a in agg.items() if t != "1/1/1/1")
    return r1, r2, r2_all


def wood_turns(r1, t_from, t_to):
    """Wood a starter-rate troll banks over turns (t_from, t_to], by phase."""
    w = 0.0
    for ph, lo, hi in PH:
        n = max(0, min(hi, t_to) - max(lo, t_from + 1) + 1)
        w += n * r1[ph]
    return w


def game_econ(g, d, r1, r2, r2_all):
    E = (g["last_tree_fall"] or g["n_turns"]) if g["standing_size_units_end"] == 0 else g["n_turns"]
    sec = g["second_troll"]
    rr2 = r2.get(sec, r2_all)
    k = 1 + r1["p101_200"] / (r1["p101_200"] + rr2)
    out = {"gameId": g["gameId"], "E": E, "train_turn": g["train_turn"], "second": sec, "r2": rr2, "k": k,
           "standing_end": g["standing_size_units_end"]}

    def earnings(t3, extra_turns_lost=0):
        turns = max(0, E - t3 - extra_turns_lost)
        U = 4 * wood_turns(r1, t3 + extra_turns_lost, E)
        after = [(t, side, sz) for t, side, sz in g["fell_events"] if t > t3]
        W = sum(sz for _, _, sz in after)
        mine = sum(sz for _, side, sz in after if side == "ours") + 0.5 * sum(sz for _, side, sz in after if side == "both")
        f = mine / W if W else 0.0
        f2 = f * k / (f * k + 1 - f) if W else 0.0
        C = 4 * W * (f2 - f)
        point = min(U, C + 4 * g["standing_size_units_end"])
        return dict(turns=turns, U=U, C=C, point=point, W_after=W, f=f)

    b = d["bills"]["1/1/0/1"]
    tf, ti = b["split_starter_fruit"], b["split_trained_iron"]
    if tf is None or ti is None:
        out["A1"] = None
    else:
        wall = max(tf, ti)
        t3 = g["train_turn"] + wall
        forgone = 4 * (wood_turns(r1, g["train_turn"], g["train_turn"] + tf) + ti * rr2)
        e = earnings(t3)
        out["A1"] = dict(tf=tf, ti=ti, wall=wall, t3=t3, forgone=forgone, fruit_low=FRUIT_ITEMS, fruit_high=FRUIT_ITEMS + SEED_HIGH,
                         **e, net_low=e["point"] - forgone - FRUIT_ITEMS, net_high=e["point"] - forgone - FRUIT_ITEMS - SEED_HIGH,
                         net_ceiling=e["U"] - forgone - FRUIT_ITEMS, net_floor=e["C"] - forgone - FRUIT_ITEMS - SEED_HIGH)
    cf = d["cheap_first"]
    cur = d["calib"].get("model_turns") or 0
    if cf["wall"] is None:
        out["A2"] = None
    else:
        delay = max(0, cf["wall"] - cur)
        # the strong troll is delayed; the cheap troll mines for cf['cheap_iron'] turns then chops from turn 2
        forgone = 4 * (delay * rr2 + wood_turns(r1, 1, 1 + max(0, cf["starter_fruit"] - cur)))
        e = earnings(1, cf["cheap_iron"] or 0)
        out["A2"] = dict(delay=delay, wall=cf["wall"], cur=cur, forgone=forgone, **e,
                         net_low=e["point"] - forgone - FRUIT_ITEMS, net_high=e["point"] - forgone - FRUIT_ITEMS - SEED_HIGH,
                         net_ceiling=e["U"] - forgone - FRUIT_ITEMS, net_floor=e["C"] - forgone - FRUIT_ITEMS - SEED_HIGH)
    return out


def boot(xs, n=2000, seed=1):
    rnd = random.Random(seed)
    m = S.mean(xs)
    bs = sorted(S.mean(rnd.choices(xs, k=len(xs))) for _ in range(n))
    return round(m, 2), round(bs[int(0.025 * n)], 2), round(bs[int(0.975 * n)], 2)


def main():
    G, D = load()
    r1, r2, r2_all = rates(G)
    games = [game_econ(G[i], D[i], r1, r2, r2_all) for i in sorted(G) if G[i]["train_turn"] and D[i].get("train_turn")]
    rep = {"r1_by_phase": r1, "r2_by_talents": r2, "r2_all": r2_all, "seed_high": SEED_HIGH, "games": games, "summary": {}}
    print("starter rate by phase", {k: round(v, 4) for k, v in r1.items()}, "second troll pooled", round(r2_all, 4))
    for design in ("A1", "A2"):
        rows = [x[design] for x in games if x[design]]
        s = {"n": len(rows)}
        for key in ("wall", "t3", "delay", "turns", "forgone", "U", "C", "point", "W_after", "f", "net_low", "net_high", "net_ceiling", "net_floor"):
            vals = [r[key] for r in rows if key in r]
            if vals:
                s[key] = dict(zip(("mean", "ci_lo", "ci_hi"), boot(vals))) | {"median": round(S.median(vals), 1)}
        s["share_net_low_positive"] = round(sum(1 for r in rows if r["net_low"] > 0) / len(rows), 3)
        s["share_net_high_positive"] = round(sum(1 for r in rows if r["net_high"] > 0) / len(rows), 3)
        rep["summary"][design] = s
        print(design, json.dumps(s, indent=None)[:1500])
    for N in (30, 60):
        rows = [x["A1"] for x in games if x["A1"]]
        fire = [r for r in rows if r["wall"] <= N]
        s = {"N": N, "fires": len(fire), "n": len(rows)}
        for key in ("net_low", "net_high", "net_ceiling", "net_floor"):
            vals = [r[key] if r["wall"] <= N else 0.0 for r in rows]
            s[key] = dict(zip(("mean", "ci_lo", "ci_hi"), boot(vals)))
            s[key + "_when_fires"] = round(S.mean(r[key] for r in fire), 2) if fire else None
        rep["summary"][f"B{N}"] = s
        print(f"B{N}", json.dumps(s))
    # by game length
    for design in ("A1", "A2"):
        for lo, hi in ((0, 199), (200, 299), (300, 300)):
            rows = [x[design] for x in games if x[design] and lo <= x["E"] <= hi]
            if rows:
                print(design, f"E in {lo}-{hi}", len(rows), "net_low mean", round(S.mean(r["net_low"] for r in rows), 1), "net_high", round(S.mean(r["net_high"] for r in rows), 1), "point earn", round(S.mean(r["point"] for r in rows), 1), "forgone", round(S.mean(r["forgone"] for r in rows), 1))
    # the win indicator: games whose margin the design's net would cross, under each fruit reading
    for design in ("A1", "A2", "B30"):
        fl = {}
        for reading in ("net_low", "net_high"):
            gain = loss = 0
            for x in games:
                r = x["A1" if design == "B30" else design]
                if not r or (design == "B30" and r["wall"] > 30):
                    continue
                g = G[x["gameId"]]
                margin = g["final_scores"][g["our_seat"]] - g["final_scores"][1 - g["our_seat"]]
                if margin < 0 and r[reading] > -margin:
                    gain += 1
                if margin > 0 and -r[reading] > margin:
                    loss += 1
            fl[reading] = dict(losses_flipped_to_wins=gain, wins_flipped_to_losses=loss, net_wins=gain - loss)
        rep["summary"][design]["win_flips"] = fl
        print(design, "win flips", fl)
    json.dump(rep, open(HERE / "paper-2026-09-03.json", "w"), indent=1, sort_keys=True)
    print("wrote paper-2026-09-03.json")


if __name__ == "__main__":
    main()
