#!/usr/bin/env python3
"""Run the banana-farm latch rule -- the ROLLING one, exactly as specified -- over the
replay seats, and report how often it would have fired.

Round 1 of the design review (codex_1, defect 1) rejected calibrating a windowed rule
from whole-game ratios: whole-game quartiles do not establish the false-trigger rate of
a rule that looks at the last w turns. This script runs the rule itself.

Input: the per-(game,seat) records written by ring_pressure.py, which carry the turn of
every referee-accepted enemy chop on that seat's ring (`enemy_chop_turns`) and of every
own harvest/chop on it (`my_ring_work_turns`).

Frozen window semantics, identical here and in the build:
  * the window at turn T is the INCLUSIVE turn range [T-w+1, T]; before turn w it is
    [1, T], so the rule is evaluated from turn 1 on a short window and only the N-gate
    keeps it quiet;
  * events are counted per event, not per turn: two accepted chops in one turn are two;
  * one enemy hit is one accepted damage event by one enemy troll on one of our ring
    cells. In-game the bot cannot see damage events, only health, so the build counts,
    per (turn, ring cell), ONE hit when that cell's plant lost health and an enemy troll
    stands on the cell -- regardless of how much health it lost. A troll chops at most
    once a turn, so this equals the replay counter unless two enemy trolls share a cell,
    in which case the build undercounts by one and latches LATER. Conservative on the
    only side that matters.
  * the test is evaluated once per turn, after the referee's events for that turn.

Usage:
  python3 claude_1/farm/latch_sim.py --in claude_1/farm/ring-pressure-2026-08-26.json \
      --out claude_1/farm/latch-sim-2026-08-26.json
"""
import argparse, bisect, collections, json, statistics, sys

LEADERS = ("goq", "yaichi", "Stounate")
TASS = "tass"


def first_trigger(work_turns, foe_turns, w, n, ratio, last_turn, floor=0, persist=1,
                  full_window=False):
    """First turn at which the condition has held `persist` turns running.

    Condition at turn t, on the inclusive window [t-w+1, t]:
        fw >= floor  and  fe + fw >= n  and  fe > ratio * fw
    With full_window, turns before w are not evaluated at all.
    Returns (turn, fe, fw) at the firing turn, or (None, None, None).
    """
    work = sorted(work_turns)
    foe = sorted(foe_turns)
    run = 0
    for t in range(w if full_window else 1, last_turn + 1):
        lo = max(1, t - w + 1)
        fw = bisect.bisect_right(work, t) - bisect.bisect_left(work, lo)
        fe = bisect.bisect_right(foe, t) - bisect.bisect_left(foe, lo)
        run = run + 1 if (fw >= floor and fe + fw >= n and fe > ratio * fw) else 0
        if run >= persist:
            return t, fe, fw
    return None, None, None


def group_of(name):
    if name in LEADERS:
        return "leaders"
    if name == TASS:
        return "tass-6536563"
    return "field"


def q(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    i = min(len(xs) - 1, int(round(p * (len(xs) - 1))))
    return xs[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="claude_1/farm/ring-pressure-2026-08-26.json")
    ap.add_argument("--out", default="-")
    ap.add_argument("--w", type=int, default=60)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--ratio", type=float, default=2.0)
    ap.add_argument("--floor", type=int, default=6, help="minimum own ring work in the window (F)")
    ap.add_argument("--persist", type=int, default=15, help="consecutive qualifying turns (M)")
    a = ap.parse_args()
    rows = json.load(open(a.inp))["per_game_seat"]

    grid = []
    for w in (40, 60, 80, 100):
        for n in (6, 8, 12):
            for ratio in (1.0, 1.5, 2.0, 3.0):
                grid.append((w, n, ratio))

    results = {}
    for (w, n, ratio) in grid:
        by = collections.defaultdict(lambda: {"seats": 0, "fired": 0, "turns": []})
        for r in rows:
            g = group_of(r["name"])
            t, fe, fw = first_trigger(r["my_ring_work_turns"], r["enemy_chop_turns"],
                                      w, n, ratio, r["turns"])
            for key in (g, "ALL"):
                b = by[key]
                b["seats"] += 1
                if t is not None:
                    b["fired"] += 1
                    b["turns"].append(t)
        key = f"w={w},N={n},ratio={ratio}"
        results[key] = {
            g: {"seats": b["seats"], "fired": b["fired"],
                "rate": round(b["fired"] / b["seats"], 4) if b["seats"] else None,
                "first_turn_median": statistics.median(b["turns"]) if b["turns"] else None,
                "first_turn_q1": q(b["turns"], 0.25), "first_turn_q3": q(b["turns"], 0.75)}
            for g, b in sorted(by.items())}

    # the round-2 operating point of the packet's sec.4.2, per seat, so the shape can be read
    w, n, ratio, floor, persist = a.w, a.n, a.ratio, a.floor, a.persist
    per_seat = []
    for r in rows:
        t, fe, fw = first_trigger(r["my_ring_work_turns"], r["enemy_chop_turns"], w, n, ratio,
                                  r["turns"], floor=floor, persist=persist, full_window=True)
        # a "ring-economy" seat has at least one w-turn window with own ring work >= floor: the
        # closest proxy this corpus holds for a bot running a ring economy, as the farm will.
        econ = False
        work, foe = sorted(r["my_ring_work_turns"]), sorted(r["enemy_chop_turns"])
        for tt in range(w, r["turns"] + 1):
            lo = tt - w + 1
            if bisect.bisect_right(work, tt) - bisect.bisect_left(work, lo) >= floor:
                econ = True
                break
        per_seat.append({"gameId": r["gameId"], "seat": r["seat"], "name": r["name"],
                         "group": group_of(r["name"]), "turns": r["turns"],
                         "ring_economy": econ,
                         "fired_turn": t, "fe_at_fire": fe, "fw_at_fire": fw,
                         "game_fe": r["enemy_chop_on_my_ring"],
                         "game_fw": r["harvest_ring"] + r["chop_ring"]})
    ec = [p for p in per_seat if p["ring_economy"]]
    fired = [p["fired_turn"] for p in ec if p["fired_turn"]]
    lead = [p for p in ec if p["group"] == "leaders"]
    out = {"window_semantics": "inclusive [T-w+1,T]; per-event counts; turns < w not evaluated; "
                               "condition must hold `persist` consecutive turns; "
                               "evaluated once per turn after referee events",
           "round1_rule_grid": results,
           "operating_point": {"w": w, "N": n, "ratio": ratio, "F": floor, "M": persist},
           "operating_point_summary": {
               "all_seats": len(per_seat),
               "all_fired": sum(1 for p in per_seat if p["fired_turn"]),
               "ring_economy_seats": len(ec),
               "ring_economy_fired": len(fired),
               "ring_economy_rate": round(len(fired) / len(ec), 4) if ec else None,
               "leader_econ_seats": len(lead),
               "leader_econ_fired": sum(1 for p in lead if p["fired_turn"]),
               "first_trigger_min": min(fired) if fired else None,
               "first_trigger_q1": q(fired, 0.25),
               "first_trigger_median": statistics.median(fired) if fired else None,
               "first_trigger_q3": q(fired, 0.75)},
           "per_seat_at_operating_point": per_seat}
    json.dump(out, sys.stdout if a.out == "-" else open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
